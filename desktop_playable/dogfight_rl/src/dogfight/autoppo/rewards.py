"""Physical integrals converted to rates, for RewardManager's single dt scaling."""
from .stride import observe
from ..locomotion.curriculum_v6_3.rewards import stop_feedback

def gait(env,index):
    s=observe(env).state
    return [s.guide,s.touchdown_credit,s.stride_credit,s.stable_credit][index].mean(-1)/env.step_dt

def support_slip(env):
    return observe(env).state.slip_cost.mean(-1)/env.step_dt
