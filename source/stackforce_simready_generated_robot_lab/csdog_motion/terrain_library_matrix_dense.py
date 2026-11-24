"""Preserve every original48 gate; append passive50Hz contact measurements."""
import json
from pathlib import Path
import numpy as np
import torch
from .terrain_library_matrix_evaluation import evaluate as original_evaluate


def evaluate(env,policy,checkpoint,output,steps=750,profile='foundation'):
    original_step=env.step;trace=[]
    def recorded_step(actions):
        result=original_step(actions)
        robot=env._robot.data
        contact=torch.linalg.vector_norm(env._contact_sensor.data.net_forces_w[:,env._foot_ids],dim=-1)>1.
        speed=torch.linalg.vector_norm(robot.body_lin_vel_w[:,env._robot_foot_ids,:2],dim=-1)
        proxy=(speed*contact).sum(1)/contact.sum(1).clamp_min(1)
        trace.append(proxy.detach().cpu().numpy().copy())
        return result
    env.step=recorded_step
    try:
        result=original_evaluate(env,policy,checkpoint,output,steps,profile)
    finally:
        env.step=original_step
    assert len(trace)==steps
    dense=np.asarray(trace);times=(np.arange(steps)+1)*env.step_dt
    for case,row in enumerate(result['cases']):
        ids=np.arange(case,env.num_envs,48)
        mask=(times>=3)&(times<9 if case//8>=4 else times<12)
        row['contact_slide_50hz_mps']=float(dense[mask][:,ids].mean())
        row['contact_slide_50hz_peak_mps']=float(dense[mask][:,ids].max())
    result['dense_contact_sampling_hz']=1/env.step_dt
    result['original_10hz_gates_retained']=True
    Path(output).write_text(json.dumps(result,indent=2)+'\n')
    return result
