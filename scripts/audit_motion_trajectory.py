#!/usr/bin/env python3
"""Screen calibrated foot references on a predeclared command/profile grid."""
import argparse
from dataclasses import asdict
import hashlib
import itertools
import json
from pathlib import Path

import torch

from csdog_motion.calibration import ASSET, calibrated_data
from csdog_motion.contracts import JOINT_NAMES
from csdog_motion.trajectory import LegKinematics, TrajectoryConfig, foot_reference


def run(output, workspace=False, centered=False):
    if output.exists():
        raise FileExistsError(output)
    torch.set_num_threads(1)
    data=calibrated_data()
    q0=[data["standing_joint_angles"][name] for name in JOINT_NAMES]
    nominal=torch.tensor([data["nominal_sole_positions_body_m"][name] for name in ("lr","lf","rf","rr")],dtype=torch.float64)
    commands=sorted(set(itertools.product((-.4,0.,.4),(-.3,0.,.3),(-.4,0.,.4))) | {(0.,y,0.) for y in (-.2,-.1,.1,.2)})
    if centered:
        profiles=[(TrajectoryConfig(p,d,h),.5,height) for p,d,h,height in ((.5,.55,.015,-.03),(.5,.5,.02,-.02))]
    elif workspace:
        profiles=[(TrajectoryConfig(p,d,h),.6,height) for p,d,h,height in itertools.product((.5,.6),(.55,.6),(.015,.02),(-.01,-.02))]
    else:
        profiles=[(TrajectoryConfig(p,d,h),.35,0.) for p,d,h in ((.5,.6,.025),(.5,.6,.032),(.5,.5,.025),(.4,.6,.025),(.6,.6,.025),(.5,.6,.02))]
    phase=torch.arange(200,dtype=torch.float64)/200
    twist=torch.tensor(commands,dtype=torch.float64).repeat_interleave(len(phase),dim=0)
    phases=phase.repeat(len(commands))
    result={"scope":"constant-command periodic free-space reference screening; not dynamics, contact, collision or torque validation",
            "urdf_sha256":hashlib.sha256((ASSET/"robot_sim.urdf").read_bytes()).hexdigest(),
            "samples_per_cycle":len(phase),"commands":commands,
            "selection_scope":"centered reference candidate exploration; not independent holdout" if centered else ("workspace exploration, not independent holdout" if workspace else "original joint envelope screen"),
            "thresholds":{"max_ik_error_m":.001,"joint_target_velocity_rad_s":8.,"minimum_joint_residual_reserve_rad":.05},"profiles":[]}
    for cfg,bound,height in profiles:
        center=q0
        if centered:
            pose_model=LegKinematics(ASSET/"robot_sim.urdf",q0,offset_bound=.7,dtype=torch.float64)
            pose_target=nominal.clone();pose_target[:,2]-=height
            solution,pose_error=pose_model.solve(pose_target[None],iterations=30)
            if pose_error.max() > 1e-6:
                raise RuntimeError("Candidate nominal pose failed")
            center=solution[0].flatten().tolist()
        model=LegKinematics(ASSET/"robot_sim.urdf",center,offset_bound=bound,dtype=torch.float64)
        target,contacts=foot_reference(phases,twist,nominal,cfg,height_delta=torch.full_like(phases,height))
        q,error=model.solve(target,iterations=18)
        q=q.reshape(len(commands),len(phase),4,3)
        error=error.reshape(len(commands),len(phase),4)
        dt=cfg.period_s/len(phase)
        speed=(q.roll(-1,1)-q.roll(1,1))/(2*dt)
        margin=torch.minimum(q-model.lower,model.upper-q)
        checks={"ik":float(error.max())<=.001,"joint_target_velocity":float(speed.abs().max())<=8.,"residual_reserve":float(margin.min())>=.05}
        entry={"config":asdict(cfg),"joint_envelope_offset_rad":bound,"height_delta_m":height,
               "nominal_joint_positions_rad":list(center),
               "checks":checks,"geometry_screen":"PASS" if all(checks.values()) else "FAIL",
               "max_ik_error_m":float(error.max()),"peak_joint_target_velocity_rad_s":float(speed.abs().max()),
               "minimum_residual_reserve_rad":float(margin.min()),"cases":[]}
        for i,command in enumerate(commands):
            entry["cases"].append({"command":command,"max_ik_error_m":float(error[i].max()),
                                   "peak_joint_target_velocity_rad_s":float(speed[i].abs().max()),
                                   "minimum_residual_reserve_rad":float(margin[i].min()),
                                   "peak_offset_per_joint_rad":(q[i]-model.nominal_q).abs().amax(0).flatten().tolist()})
        result["profiles"].append(entry)
        print(entry["config"],"bound",bound,"height",height,entry["geometry_screen"],"error_mm",round(entry["max_ik_error_m"]*1000,3),"speed",round(entry["peak_joint_target_velocity_rad_s"],3),"reserve",round(entry["minimum_residual_reserve_rad"],3))
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+"\n")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--workspace",action="store_true")
    parser.add_argument("--centered",action="store_true")
    args=parser.parse_args()
    run(args.output,args.workspace,args.centered)
