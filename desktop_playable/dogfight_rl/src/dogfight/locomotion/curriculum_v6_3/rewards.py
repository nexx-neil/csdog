"""Rates passed to Isaac Lab; discrete credit divided by the actual control dt."""
import torch
from .stride import observe

def gait(env,index):
    s=observe(env).state
    values=[s.guide,s.touchdown_credit,s.stride_credit,s.stable_credit]
    return values[index].mean(-1)/env.step_dt

def support_slip(env):
    # Physical substep integral, not the final policy sample.
    s=observe(env).state
    return s.slip_cost.mean(-1)/env.step_dt

def stop_feedback(env):
    r=env.scene['robot'];cmd=env.command_manager.get_command('base_velocity')
    stop=cmd.norm(dim=-1)<.04
    return stop*(.15*torch.log1p(r.data.root_lin_vel_b[:,:2].norm(dim=-1)/.03)+.075*torch.log1p(r.data.root_ang_vel_b[:,2].abs()/.08))
