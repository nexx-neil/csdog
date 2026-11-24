"""CPU-only primitive collision preflight for proposed whole-body poses.

This module does not change a simulator, checkpoint, collision filter or joint
limit. A geometric pass is not a balance/contact/dynamics validation. hppfcl is
loaded only when signed self-distance queries are explicitly requested.
"""
from dataclasses import dataclass
import itertools
import math
import xml.etree.ElementTree as ET

import numpy as np


def rpy_rotation(rpy):
    r, p, y = rpy
    cr, sr, cp, sp, cy, sy = (math.cos(r), math.sin(r), math.cos(p),
                             math.sin(p), math.cos(y), math.sin(y))
    return np.array([[cy*cp, cy*sp*sr-sy*cr, cy*sp*cr+sy*sr],
                     [sy*cp, sy*sp*sr+cy*cr, sy*sp*cr-cy*sr],
                     [-sp, cp*sr, cp*cr]])


def origin_transform(node):
    result = np.eye(4)
    if node is not None:
        result[:3, 3] = [float(v) for v in node.get("xyz", "0 0 0").split()]
        result[:3, :3] = rpy_rotation([float(v) for v in node.get("rpy", "0 0 0").split()])
    return result


def primitive_extents(kind, dimensions, rotation):
    """Exact world-axis half extents, including tilted finite cylinders."""
    if kind == "sphere":
        return np.full(3, dimensions[0])
    if kind == "box":
        return np.abs(rotation) @ (np.asarray(dimensions) / 2)
    if kind == "cylinder":
        radius, length = dimensions
        return (radius*np.linalg.norm(rotation[:, :2], axis=1)
                + length/2*np.abs(rotation[:, 2]))
    raise ValueError(f"Unsupported collision primitive: {kind}")


@dataclass(frozen=True)
class Primitive:
    link: str
    index: int
    local: np.ndarray
    kind: str
    dimensions: tuple


class PostureGeometry:
    def __init__(self, urdf, joint_names, soft_factor=.9):
        if not 0 < soft_factor <= 1:
            raise ValueError("soft_factor must be in (0, 1]")
        self.joint_names = tuple(joint_names)
        if len(set(self.joint_names)) != len(self.joint_names):
            raise ValueError("Duplicate joint names")
        xml = ET.parse(urdf).getroot()
        nodes = {j.get("name"): j for j in xml.findall("joint")}
        movable = {name for name, j in nodes.items() if j.get("type") != "fixed"}
        if movable != set(self.joint_names):
            raise ValueError("Joint order must cover every movable URDF joint")
        self.lower, self.upper = [], []
        for name in self.joint_names:
            node = nodes[name]
            if node.get("type") != "revolute":
                raise ValueError("Only fixed/revolute URDF trees are supported")
            limit = node.find("limit")
            lo, hi = float(limit.get("lower")), float(limit.get("upper"))
            if not math.isfinite(lo+hi) or lo >= hi:
                raise ValueError("Invalid joint limits")
            center = (lo+hi)/2
            self.lower.append(center+soft_factor*(lo-center))
            self.upper.append(center+soft_factor*(hi-center))
        self.lower, self.upper = np.array(self.lower), np.array(self.upper)
        self.adjacent = set()
        pending = list(nodes.values())
        children = {j.find("child").get("link") for j in pending}
        roots = {l.get("name") for l in xml.findall("link")}-children
        if len(roots) != 1:
            raise ValueError("Expected one URDF root")
        self.root = roots.pop()
        self.joints, resolved = [], {self.root}
        while pending:
            progress = False
            for j in pending.copy():
                parent, child = (j.find(n).get("link") for n in ("parent", "child"))
                if parent not in resolved:
                    continue
                idx = self.joint_names.index(j.get("name")) if j.get("type") == "revolute" else None
                k = np.zeros((3, 3))
                if idx is not None:
                    axis = np.array([float(v) for v in j.find("axis").get("xyz").split()])
                    if not np.isfinite(axis).all() or np.linalg.norm(axis) == 0:
                        raise ValueError("Invalid joint axis")
                    x, y, z = axis/np.linalg.norm(axis)
                    k = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
                self.joints.append((parent, child, origin_transform(j.find("origin")), idx, k, k@k))
                self.adjacent.add(frozenset((parent, child)))
                resolved.add(child)
                pending.remove(j)
                progress = True
            if not progress:
                raise ValueError("Unresolved URDF tree")
        self.primitives = []
        for link in xml.findall("link"):
            for index, collision in enumerate(link.findall("collision")):
                shape = list(collision.find("geometry"))[0]
                kind = shape.tag
                if kind == "sphere":
                    dimensions = (float(shape.get("radius")),)
                elif kind == "cylinder":
                    dimensions = (float(shape.get("radius")), float(shape.get("length")))
                elif kind == "box":
                    dimensions = tuple(float(v) for v in shape.get("size").split())
                else:
                    raise ValueError(f"Unsupported collision primitive: {kind}")
                if not all(math.isfinite(v) and v > 0 for v in dimensions):
                    raise ValueError("Invalid collision dimensions")
                self.primitives.append(Primitive(link.get("name"), index,
                    origin_transform(collision.find("origin")), kind, dimensions))
        self._fcl = self._shapes = None

    def world_frames(self, q, height, rpy=(0., 0., 0.)):
        q, rpy = np.asarray(q, dtype=float), np.asarray(rpy, dtype=float)
        if (q.shape != (len(self.joint_names),) or rpy.shape != (3,)
                or not np.isfinite(q).all() or not np.isfinite(rpy).all()
                or not math.isfinite(height) or height <= 0):
            raise ValueError("Expected finite joint vector, positive height and three root angles")
        base = np.eye(4)
        base[:3, :3], base[2, 3] = rpy_rotation(rpy), height
        frames = {self.root: base}
        for parent, child, origin, idx, k, k2 in self.joints:
            motion = np.eye(4)
            if idx is not None:
                motion[:3, :3] += math.sin(q[idx])*k+(1-math.cos(q[idx]))*k2
            frames[child] = frames[parent]@origin@motion
        return frames

    def primitive_bounds(self, q, height, rpy=(0., 0., 0.)):
        frames = self.world_frames(q, height, rpy)
        rows = []
        for p in self.primitives:
            t = frames[p.link]@p.local
            extent = primitive_extents(p.kind, p.dimensions, t[:3, :3])
            rows.append((t, t[:3, 3]-extent, t[:3, 3]+extent))
        return rows

    def _load_distances(self):
        if self._fcl is None:
            import hppfcl
            self._fcl = hppfcl
            self._shapes = [getattr(hppfcl, {"box": "Box", "sphere": "Sphere",
                            "cylinder": "Cylinder"}[p.kind])(*p.dimensions)
                            for p in self.primitives]

    def audit(self, q, height, rpy=(0., 0., 0.), distance_band=.01):
        if not math.isfinite(distance_band) or distance_band < 0:
            raise ValueError("Invalid distance band")
        bounds = self.primitive_bounds(q, height, rpy)
        self._load_distances()
        fcl = self._fcl
        request = fcl.DistanceRequest()
        request.gjk_tolerance = 1e-8
        floors = [{"link": p.link, "primitive": p.index, "kind": p.kind,
                   "clearance_m": float(b[1][2])} for p, b in zip(self.primitives, bounds)]
        pairs = []
        for i, j in itertools.combinations(range(len(self.primitives)), 2):
            a, b = self.primitives[i], self.primitives[j]
            if a.link == b.link or frozenset((a.link, b.link)) in self.adjacent:
                continue
            ta, la, ha = bounds[i]
            tb, lb, hb = bounds[j]
            if np.maximum(la-hb, lb-ha).max() > distance_band:
                continue
            distance = float(fcl.distance(self._shapes[i], fcl.Transform3f(ta[:3, :3], ta[:3, 3]),
                             self._shapes[j], fcl.Transform3f(tb[:3, :3], tb[:3, 3]),
                             request, fcl.DistanceResult()))
            if not math.isfinite(distance):
                raise RuntimeError("Nonfinite narrow-phase distance")
            if distance <= distance_band:
                pairs.append({"a": [a.link, a.index], "b": [b.link, b.index],
                              "signed_distance_m": distance})
        q = np.asarray(q)
        reserve = float(np.minimum(q-self.lower, self.upper-q).min())
        return {"height_m": float(height), "rpy_rad": list(rpy),
                "joint_positions_rad": q.tolist(), "soft_limit_reserve_rad": reserve,
                "floor": floors, "near_nonadjacent_pairs": pairs,
                "geometry_pass": (reserve >= 0 and all(r["clearance_m"] >= -.001 for r in floors)
                                  and all(r["signed_distance_m"] >= -.0001 for r in pairs)),
                "scope": "Exact primitive floor extents and hppfcl signed primitive distance; "
                         "same-link/direct parent-child pairs excluded; no other exclusions. "
                         "Provisional URDF soft limits only; no support, dynamics or hardware claim."}


def quintic_pose_segment(q0, height0, q1, height1, duration, sample_dt=.01):
    """Rest-to-rest geometric samples with analytic velocities; no execution."""
    q0, q1 = np.asarray(q0, dtype=float), np.asarray(q1, dtype=float)
    if (q0.ndim != 1 or q1.shape != q0.shape or not np.isfinite(q0).all()
            or not np.isfinite(q1).all() or not all(math.isfinite(x) and x > 0
            for x in (height0, height1, duration, sample_dt))):
        raise ValueError("Invalid geometric segment")
    t = np.linspace(0, duration, int(math.ceil(duration/sample_dt))+1)
    s = t/duration
    blend = s**3*(10+s*(-15+6*s))
    rate = 30*s**2*(1-s)**2/duration
    return {"time_s": t, "q": q0+blend[:, None]*(q1-q0),
            "q_velocity": rate[:, None]*(q1-q0),
            "height_m": height0+blend*(height1-height0),
            "height_velocity": rate*(height1-height0),
            "exact_peak_joint_velocity_rad_s": float(1.875*np.abs(q1-q0).max()/duration),
            "scope": "Sampled geometric path only; not continuous collision or balance proof"}
