"""Keep the V3 six official Spot kernels and weight; veto no-support hops and fake stance bonuses."""
from ..spot_aligned_v3.rewards import DistalGaitReward
from ..spot_v2.contacts import contact_state
from .rewards import gait_phase_eligible
class GroundedGaitReward(DistalGaitReward):
 def __call__(self,env,std,max_err,velocity_threshold,synced_feet_pair_names,asset_cfg,sensor_cfg):
  value=super().__call__(env,std,max_err,velocity_threshold,synced_feet_pair_names,asset_cfg,sensor_cfg)
  state=contact_state(env);eligible=gait_phase_eligible(state.contact,state.clearance,state.raw_force)
  env._v4_gait_phase_eligible=eligible
  return value*eligible
