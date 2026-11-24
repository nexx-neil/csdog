"""Flat-only observed-yaw residual learning, retaining 75% old command exposure."""
import torch

TAG='csdog_observed_yaw_flat_residual_learning_obs76_v24'


def sample_commands(count,device='cpu'):
    cmd=torch.empty(count,3,device=device).uniform_(-1,1)*torch.tensor([.4,.3,.4],device=device)
    category=torch.rand(count,device=device)
    low=category<.25
    cmd[low]*=cmd.new_tensor([.375,1/3,.375])
    fast=category>=.75;ids=torch.where(fast)[0]
    axes=torch.randint(0,3,(len(ids),),device=device)
    magnitude=torch.empty(len(ids),device=device).uniform_(.65,1.)
    signs=torch.where(torch.rand(len(ids),device=device)<.5,-1.,1.)
    cmd[ids]=0;cmd[ids,axes]=cmd.new_tensor([.6,.4,.8])[axes]*magnitude*signs
    return cmd,category


def learning_contract(base):
    import copy
    value=copy.deepcopy(base);value.update(schema_version=24,compatibility_tag=TAG)
    value['learning_replay']={'low_probability':.25,'old_full_probability':.5,'fast_single_axis_probability':.25,
        'inside_episode_command_changes':True,'reward':'same flat residual terms and scales as v7; true current stance/reference and observed yaw controller states',
        'scope':'flat only; no posture/terrain/jump learning'}
    return value
