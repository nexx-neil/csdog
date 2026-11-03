"""Use the frozen V6.1 environment and V6 PPO unchanged."""
import copy,sys
from pathlib import Path
from ..curriculum_v6_1.config import build as base_build
from isaaclab.managers import RewardTermCfg
from . import rewards
EXTRA={'swing_credit','touchdown_credit','stride_credit','support_quality','physical_slip','stop_feedback'}

def build(options,num_envs,seed,device):
    base=copy.deepcopy(options)
    for name in EXTRA:base['weights'].pop(name,None)
    base['variant']='control'
    cfg,agent=base_build(base,num_envs,seed,device)
    # Reuse the actual frozen V6.2 signal; do not create another source copy.
    old=Path(__file__).resolve().parents[4]/'runs/locomotion/csdog_ppo_v6_2_diagnostics/scripts'
    sys.path.insert(0,str(old))
    from early_swing_signal import early_swing
    cfg.rewards.gait_guide.func=early_swing
    for i,name in enumerate(['swing_credit','touchdown_credit','stride_credit','support_quality']):
        setattr(cfg.rewards,name,RewardTermCfg(func=rewards.gait,weight=options['weights'][name],params={'index':i}))
    cfg.rewards.physical_slip=RewardTermCfg(func=rewards.support_slip,weight=options['weights']['physical_slip'])
    cfg.rewards.stop_feedback=RewardTermCfg(func=rewards.stop_feedback,weight=options['weights']['stop_feedback'])
    agent.experiment_name='csdog_curriculum_ppo_v6_3'
    return cfg,agent

def options_from(source,arm):
    options=copy.deepcopy(source);options.update(schema=6.3,variant='control',initial_substage='1B',contact_validated=True)
    options['weights']['gait_guide']=1. if arm=='A' else 0.
    # Preserve the original completed-swing term in both arms. V6.3 adds the
    # stricter cycle terms; later pure-yaw stages still retain a generic event.
    options['weights']['swing']=.15
    for name in EXTRA:options['weights'][name]=0.
    if arm=='B':
        options['weights'].update(swing_credit=1.,touchdown_credit=1.,stride_credit=1.,support_quality=1.,physical_slip=-.6,stop_feedback=-1.)
    options['monitor'].update(save_interval=50,light_interval=250,full_interval=500,candidate_updates=300)
    return options
