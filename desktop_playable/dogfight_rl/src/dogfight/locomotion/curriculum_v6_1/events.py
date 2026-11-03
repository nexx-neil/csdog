"""Pure tensor continuous-flight counter; every failed raw substep breaks a segment."""
import torch

def advance_air_ticks(previous,strict):
    ended=torch.where(~strict,previous,0)
    current=torch.where(strict,previous+1,0)
    return current,ended

def diagnostic_indices(num_envs,cases):
    reps=num_envs//len(cases)
    selected=[next(i for i,(name,seq) in enumerate(cases) if name==task and seq==command)
              for task,command in [('stop',[(0,0)]),('forward',[(.18,0)]),('forward',[(.25,0)])]]
    return [i*reps+j for i in selected for j in range(min(4,reps))]
