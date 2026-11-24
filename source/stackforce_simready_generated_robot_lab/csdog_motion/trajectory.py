"""Model-specific, C2 foot references and bounded batched URDF IK.

These are geometric references, not a balance controller. No task is changed
by importing this module. Foot coordinates denote sole-sphere centers.
"""
from dataclasses import dataclass
import math
import xml.etree.ElementTree as ET

import torch


LEGS = ("lr", "lf", "rf", "rr")


@dataclass(frozen=True)
class TrajectoryConfig:
    period_s: float = .5
    stance_fraction: float = .6
    clearance_m: float = .025

    def __post_init__(self):
        if not (math.isfinite(self.period_s) and self.period_s > 0
                and .5 <= self.stance_fraction < .9
                and math.isfinite(self.clearance_m) and 0 < self.clearance_m <= .08):
            raise ValueError("Invalid trajectory timing or clearance")


def body_flow(xy, twist, time):
    """Coordinates of stationary world points in a body with constant SE(2) twist.

    xy: [N,4,2], twist: [N,3], time: [N,4]. Stable at zero yaw rate.
    """
    theta = twist[:, 2:3] * time
    c, s = torch.cos(theta), torch.sin(theta)
    a = time * torch.sinc(theta / torch.pi)
    b = time * theta * .5 * torch.sinc(theta / (2 * torch.pi)).square()
    x, y = xy.unbind(-1)
    vx, vy = twist[:, 0:1], twist[:, 1:2]
    return torch.stack((c*x + s*y - a*vx - b*vy,
                        -s*x + c*y + b*vx - a*vy), dim=-1)


def _stance_derivatives(xy, twist):
    omega = twist[:, 2:3, None]
    tangent = torch.stack((-xy[..., 1], xy[..., 0]), dim=-1)
    velocity = -twist[:, None, :2] - omega * tangent
    acceleration = -omega * torch.stack((-velocity[..., 1], velocity[..., 0]), dim=-1)
    return velocity, acceleration


def foot_reference(phase, twist, nominal, config=None, blend=None, height_delta=None):
    """Return [N,4,3] centers and [N,4] scheduled contact masks.

    Stance integrates body twist exactly. Swing is a quintic Hermite return,
    matching position, velocity and acceleration at touchdown/liftoff. The
    vertical bump has zero first/second derivatives at both endpoints.
    Height changes are only a parameter interface, not validated capability.
    """
    cfg = config or TrajectoryConfig()
    nominal = torch.as_tensor(nominal, dtype=phase.dtype, device=phase.device)
    if nominal.shape != (4, 3) or twist.shape != (len(phase), 3):
        raise ValueError("Expected four nominal feet and one twist per phase")
    local = torch.remainder(phase[:, None] + phase.new_tensor([0., .5, 0., .5]), 1.)
    stance = local < cfg.stance_fraction
    base = nominal[None].expand(len(phase), -1, -1)
    stance_time = cfg.period_s * cfg.stance_fraction
    swing_time = cfg.period_s - stance_time
    elapsed = local * cfg.period_s - stance_time / 2
    stance_xy = body_flow(base[..., :2], twist, elapsed)
    # Also accept a per-environment stance duration for a bounded gait schedule.
    half = torch.ones_like(local) * (stance_time / 2)
    p0 = body_flow(base[..., :2], twist, half)
    p1 = body_flow(base[..., :2], twist, -half)
    v0, a0 = _stance_derivatives(p0, twist)
    v1, a1 = _stance_derivatives(p1, twist)
    swing_scale = swing_time[..., None] if torch.is_tensor(swing_time) else swing_time
    c0, c1, c2 = p0, swing_scale*v0, .5*swing_scale**2*a0
    d, e, f = p1-c0-c1-c2, swing_scale*v1-c1-2*c2, swing_scale**2*a1-2*c2
    c3, c4, c5 = 10*d-4*e+.5*f, -15*d+7*e-f, 6*d-3*e+.5*f
    progress = ((local - cfg.stance_fraction) / (1-cfg.stance_fraction)).clamp(0, 1)
    s = progress[..., None]
    swing_xy = c0 + s*(c1+s*(c2+s*(c3+s*(c4+s*c5))))
    xy = torch.where(stance[..., None], stance_xy, swing_xy)
    lift = cfg.clearance_m * 64 * progress.pow(3) * (1-progress).pow(3)
    target = torch.cat((xy, base[..., 2:3] + lift[..., None]), dim=-1)
    if blend is not None:
        target = base + blend[:, None, None] * (target - base)
    if height_delta is not None:
        target[..., 2] -= height_delta[:, None]
    return target, stance


def _rpy_matrix(value):
    r, p, y = value
    cr, sr, cp, sp, cy, sy = math.cos(r), math.sin(r), math.cos(p), math.sin(p), math.cos(y), math.sin(y)
    return [[cy*cp, cy*sp*sr-sy*cr, cy*sp*cr+sy*sr],
            [sy*cp, sy*sp*sr+cy*cr, sy*sp*cr-cy*sr], [-sp, cp*sr, cp*cr]]


class LegKinematics:
    """Four independent URDF chains with analytic Jacobians; no mirror assumption."""
    def __init__(self, urdf, nominal_q, offset_bound=.35, soft_factor=.9, device="cpu", dtype=torch.float32):
        root = ET.parse(urdf).getroot()
        origins, rotations, axes, soles, lo, hi = [], [], [], [], [], []
        masses, centers, sole_masses, sole_centers = [], [], [], []
        for leg in LEGS:
            joints = [root.find(f"joint[@name='joint_{leg}_{i}']") for i in (1, 2, 3)]
            origins.append([[float(x) for x in j.find("origin").get("xyz").split()] for j in joints])
            rotations.append([_rpy_matrix([float(x) for x in j.find("origin").get("rpy", "0 0 0").split()]) for j in joints])
            axes.append([[float(x) for x in j.find("axis").get("xyz").split()] for j in joints])
            soles.append([float(x) for x in root.find(f"joint[@name='joint_link_{leg}_sole_fixed']/origin").get("xyz").split()])
            leg_mass, leg_center = [], []
            for joint in joints:
                inertial=root.find(f"link[@name='{joint.find('child').get('link')}']/inertial")
                leg_mass.append(float(inertial.find("mass").get("value")))
                leg_center.append([float(x) for x in inertial.find("origin").get("xyz","0 0 0").split()])
            masses.append(leg_mass);centers.append(leg_center)
            fixed=root.find(f"joint[@name='joint_link_{leg}_sole_fixed']")
            inertial=root.find(f"link[@name='{fixed.find('child').get('link')}']/inertial")
            sole_masses.append(float(inertial.find("mass").get("value")))
            fixed_rotation=torch.tensor(_rpy_matrix([float(x) for x in fixed.find("origin").get("rpy","0 0 0").split()]),dtype=torch.float64)
            local=torch.tensor([float(x) for x in inertial.find("origin").get("xyz","0 0 0").split()],dtype=torch.float64)
            sole_centers.append((fixed_rotation@local).tolist())
            limits = [[float(j.find("limit").get(key)) for j in joints] for key in ("lower", "upper")]
            # Isaac soft limits shrink about the interval midpoint, including
            # asymmetric limits (the current asset happens to be symmetric).
            center = [(a+b)/2 for a, b in zip(*limits)]
            lo.append([c + soft_factor*(a-c) for c, a in zip(center, limits[0])])
            hi.append([c + soft_factor*(b-c) for c, b in zip(center, limits[1])])
        tensor = lambda x: torch.as_tensor(x, device=device, dtype=dtype)
        self.origins, self.rotations, self.axes, self.soles = map(tensor, (origins, rotations, axes, soles))
        self.link_masses,self.link_centers=map(tensor,(masses,centers))
        self.sole_masses,self.sole_centers=map(tensor,(sole_masses,sole_centers))
        self.axes = self.axes / torch.linalg.vector_norm(self.axes, dim=-1, keepdim=True)
        self.nominal_q = tensor(nominal_q).reshape(4, 3)
        self.lower = torch.maximum(tensor(lo), self.nominal_q-offset_bound)
        self.upper = torch.minimum(tensor(hi), self.nominal_q+offset_bound)
        self.eye = torch.eye(3, device=device, dtype=dtype)
        if not torch.all(self.lower < self.upper):
            raise ValueError("Empty joint envelope")
        axis = self.axes
        zeros = torch.zeros_like(axis[..., 0])
        x, y, z = axis.unbind(-1)
        self.skew = torch.stack((zeros,-z,y,z,zeros,-x,-y,x,zeros), dim=-1).reshape(4,3,3,3)

    def fk(self, q):
        if q.ndim != 3 or q.shape[1:] != (4, 3):
            raise ValueError("Joint arrays must be [N,4,3]")
        position = torch.zeros(q.shape[0], 4, 3, device=q.device, dtype=q.dtype)
        rotation = self.eye.expand(q.shape[0], 4, 3, 3)
        pivots, axes = [], []
        for i in range(3):
            position = position + (rotation @ self.origins[:, i, :, None]).squeeze(-1)
            rotation = rotation @ self.rotations[:, i]
            pivots.append(position)
            axes.append((rotation @ self.axes[:, i, :, None]).squeeze(-1))
            angle = q[:, :, i, None, None]
            k = self.skew[:, i]
            axis_rotation = self.eye + torch.sin(angle)*k + (1-torch.cos(angle))*(k@k)
            rotation = rotation @ axis_rotation
        foot = position + (rotation @ self.soles[..., None]).squeeze(-1)
        jacobian = torch.stack([torch.cross(a, foot-p, dim=-1) for a, p in zip(axes, pivots)], dim=-1)
        return foot, jacobian

    def solve(self, target, initial=None, iterations=12, damping=.002, step_bound=.15):
        q = self.nominal_q.expand(len(target), -1, -1).clone() if initial is None else initial.clone()
        q = torch.maximum(torch.minimum(q, self.upper), self.lower)
        for _ in range(iterations):
            position, jacobian = self.fk(q)
            error = target - position
            # Damped least squares in Cartesian coordinates, bounded each step.
            dual = torch.linalg.solve(jacobian @ jacobian.transpose(-1,-2) + damping**2*self.eye, error[..., None])
            delta = (jacobian.transpose(-1,-2) @ dual).squeeze(-1).clamp(-step_bound, step_bound)
            q = torch.maximum(torch.minimum(q + delta, self.upper), self.lower)
        position, _ = self.fk(q)
        return q, torch.linalg.vector_norm(target-position, dim=-1)

    def static_support_torque(self,q,foot_forces,gravity_body):
        """Joint torque balancing leg gravity and specified ground forces.

        Includes the three moving links and sole mass per leg. This is
        quasi-static feedforward, not full inverse dynamics.
        """
        position=torch.zeros_like(q);rotation=self.eye.expand(len(q),4,3,3)
        pivots=[];axes=[];gravity_external=torch.zeros_like(q)
        for i in range(3):
            position=position+(rotation@self.origins[:,i,:,None]).squeeze(-1)
            rotation=rotation@self.rotations[:,i]
            pivots.append(position);axes.append((rotation@self.axes[:,i,:,None]).squeeze(-1))
            angle=q[:,:,i,None,None];k=self.skew[:,i]
            rotation=rotation@(self.eye+torch.sin(angle)*k+(1-torch.cos(angle))*(k@k))
            center=position+(rotation@self.link_centers[:,i,:,None]).squeeze(-1)
            force=self.link_masses[:,i,None]*gravity_body[:,None,:]
            for j in range(i+1):
                jac=torch.cross(axes[j],center-pivots[j],dim=-1)
                gravity_external[:,:,j]+=(jac*force).sum(-1)
        sole_center=position+(rotation@(self.soles+self.sole_centers)[...,None]).squeeze(-1)
        sole_force=self.sole_masses[:,None]*gravity_body[:,None,:]
        for j in range(3):
            jac=torch.cross(axes[j],sole_center-pivots[j],dim=-1)
            gravity_external[:,:,j]+=(jac*sole_force).sum(-1)
        _,jacobian=self.fk(q)
        contact_external=(jacobian.transpose(-1,-2)@foot_forces[...,None]).squeeze(-1)
        return -gravity_external-contact_external
