#!/usr/bin/env python3
"""URDF whole-body COM, stance geometry and a separate COM-centered candidate."""
import argparse
import itertools
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from scipy.spatial.transform import Rotation
import torch

from csdog_motion.calibration import ASSET
from csdog_motion.contracts import JOINT_NAMES
from csdog_motion.reference_control import reference_data
from csdog_motion.trajectory import LegKinematics, TrajectoryConfig, foot_reference, LEGS


def body_com(urdf, angles):
    root=ET.parse(urdf).getroot()
    q=dict(zip(JOINT_NAMES,angles));poses={"base":(np.zeros(3),np.eye(3))}
    pending=list(root.findall("joint"))
    while pending:
        count=len(pending)
        for joint in pending[:]:
            parent=joint.find("parent").get("link")
            if parent not in poses:continue
            position,rotation=poses[parent];origin=joint.find("origin")
            position=position+rotation@np.fromstring(origin.get("xyz","0 0 0"),sep=" ")
            rotation=rotation@Rotation.from_euler("xyz",np.fromstring(origin.get("rpy","0 0 0"),sep=" ")).as_matrix()
            if joint.get("type") in ("revolute","continuous"):
                rotation=rotation@Rotation.from_rotvec(np.fromstring(joint.find("axis").get("xyz"),sep=" ")*q[joint.get("name")]).as_matrix()
            poses[joint.find("child").get("link")]=(position,rotation);pending.remove(joint)
        if len(pending)==count:raise ValueError("Disconnected URDF")
    masses=[];centers=[]
    for link in root.findall("link"):
        inertial=link.find("inertial")
        if inertial is None:continue
        mass=float(inertial.find("mass").get("value"));origin=inertial.find("origin")
        center=np.zeros(3) if origin is None else np.fromstring(origin.get("xyz","0 0 0"),sep=" ")
        p,r=poses[link.get("name")];masses.append(mass);centers.append(p+r@center)
    return float(sum(masses)),np.average(centers,weights=masses,axis=0)


def support_summary(urdf,profile):
    mass,com=body_com(urdf,profile["nominal_joint_positions_rad"])
    feet=np.array([profile["nominal_sole_positions_body_m"][leg] for leg in LEGS])
    distances=[]
    for a,b in ((0,2),(1,3)):
        direction=feet[b,:2]-feet[a,:2];offset=com[:2]-feet[a,:2]
        distance=abs(direction[0]*offset[1]-direction[1]*offset[0])/np.linalg.norm(direction)
        distances.append(float(distance))
    return {"total_mass_kg":mass,"com_body_m":com.tolist(),"foot_center_body_m":feet.mean(0).tolist(),
            "com_minus_foot_center_xy_m":(com[:2]-feet[:,:2].mean(0)).tolist(),
            "distance_from_com_to_each_diagonal_support_line_m":distances,
            "meaning":"nominal static COM geometry only; two contacts form a line, not an area support polygon or dynamic balance proof"}


def run(output):
    if output.exists():raise FileExistsError(output)
    torch.set_num_threads(1)
    original=reference_data();urdf=ASSET/"robot_sim.urdf"
    baseline=support_summary(urdf,original)
    candidate=json.loads(json.dumps(original))
    model=LegKinematics(urdf,original["nominal_joint_positions_rad"],offset_bound=.7,dtype=torch.float64)
    nominal=torch.tensor([original["nominal_sole_positions_body_m"][leg] for leg in LEGS],dtype=torch.float64)
    q=model.nominal_q[None].clone()
    for _ in range(5):
        _,com=body_com(urdf,q.flatten().tolist())
        correction=torch.tensor(com[:2])-nominal[:,:2].mean(0)
        nominal[:,:2]+=correction
        q,error=model.solve(nominal[None],initial=q,iterations=30)
        if error.max()>.000001:raise RuntimeError("COM-centered nominal pose unreachable")
    candidate["nominal_joint_positions_rad"]=q.flatten().tolist()
    candidate["nominal_sole_positions_body_m"]={leg:nominal[i].tolist() for i,leg in enumerate(LEGS)}
    candidate["scope"]="COM-centered reference diagnostic; static geometry selection only, not a locomotion result"
    centered=LegKinematics(urdf,q.flatten(),offset_bound=.5,dtype=torch.float64)
    commands=sorted(set(itertools.product((-.4,0.,.4),(-.3,0.,.3),(-.4,0.,.4)))|{(0.,y,0.) for y in (-.2,-.1,.1,.2)})
    phase=torch.arange(200,dtype=torch.float64)/200
    twist=torch.tensor(commands,dtype=torch.float64).repeat_interleave(len(phase),0)
    target,_=foot_reference(phase.repeat(len(commands)),twist,nominal,TrajectoryConfig(**candidate["trajectory"]))
    solved,error=centered.solve(target,iterations=25)
    solved=solved.reshape(len(commands),200,4,3)
    velocity=(solved.roll(-1,1)-solved.roll(1,1))/(candidate["trajectory"]["period_s"]/100)
    reserve=torch.minimum(solved-centered.lower,centered.upper-solved)
    screen={"max_ik_error_m":float(error.max()),"peak_joint_target_velocity_rad_s":float(velocity.abs().max()),"minimum_residual_reserve_rad":float(reserve.min())}
    passed=screen["max_ik_error_m"]<=.001 and screen["peak_joint_target_velocity_rad_s"]<=8. and screen["minimum_residual_reserve_rad"]>=.05
    candidate.update(screened_ik_max_error_m=screen["max_ik_error_m"],screened_peak_target_speed_rad_s=screen["peak_joint_target_velocity_rad_s"],screened_residual_reserve_rad=screen["minimum_residual_reserve_rad"])
    report={"baseline":baseline,"candidate":support_summary(urdf,candidate),"commands":commands,"geometry_screen":"PASS" if passed else "FAIL",**screen}
    output.mkdir(parents=True)
    (output/"support_audit.json").write_text(json.dumps(report,indent=2)+"\n")
    (output/"profile.json").write_text(json.dumps(candidate,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--output",type=Path,required=True)
    run(parser.parse_args().output)
