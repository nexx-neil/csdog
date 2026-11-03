"""Independent settings applied only by new experiment entrypoints."""
from isaaclab.managers import RewardTermCfg as Term
import isaaclab_tasks.manager_based.locomotion.velocity.config.spot.mdp as spot
from . import rewards as r

def improve(cfg,settings):
 cfg.rewards.foot_slip.func=r.slip
 cfg.rewards.foot_slip.weight=settings.get('foot_slip_weight',-.6) if settings.get('enable_foot_slip_penalty',True) else 0.
 cfg.rewards.foot_air_time.func=r.air_time;cfg.rewards.foot_air_time.params={}
 cfg.rewards.foot_air_time.weight=settings.get('air_time_weight',.4) if settings.get('enable_air_time_reward',True) else 0.
 cfg.rewards.foot_clearance.func=r.clearance;cfg.rewards.foot_clearance.params={'target_height':settings.get('clearance_height',.03)}
 cfg.rewards.foot_clearance.weight=settings.get('foot_clearance_weight',.2) if settings.get('enable_foot_clearance_reward',True) else 0.
 cfg.rewards.stand_deviation.func=r.stand_still
 cfg.rewards.stand_deviation.weight=settings.get('stand_still_weight',-.4) if settings.get('enable_stand_still_penalty',True) else 0.
 cfg.rewards.action_rate_l2.weight=settings.get('action_rate_weight',-.02) if settings.get('enable_action_smoothness',True) else 0.
 cfg.rewards.spot_smoothness=Term(func=spot.action_smoothness_penalty,weight=settings.get('action_smoothness_weight',-.06) if settings.get('enable_action_smoothness',True) else 0.)
 cfg.rewards.raw_saturation=Term(func=r.saturation,weight=settings.get('raw_saturation_weight',-.3) if settings.get('enable_action_smoothness',True) else 0.)
 cfg.rewards.gait.func=r.DistalGaitReward
 cfg.rewards.gait.weight=settings.get('gait_weight',.35) if settings.get('enable_gait_reward',False) else 0.
 cfg.rewards.gait.params.update(std=.025,max_err=.2,velocity_threshold=.15)
 return cfg
