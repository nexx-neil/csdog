"""Independent priority for mandatory versus optional height requests."""
from isaaclab.utils import configclass
from csdog_motion.contact_lift_priority import TAG,contract,choose_goal
from .motion_contact_datum import MotionContactDatumEnv
from .motion_contact_lift_preview import MotionContactLiftEnvCfg,MotionContactLiftEnv
@configclass
class MotionContactPriorityEnvCfg(MotionContactLiftEnvCfg):
    def __post_init__(self):
        super().__post_init__();self.checkpoint_compatibility_tag=TAG;self.motion_contract=contract(self.motion_contract)
class MotionContactPriorityEnv(MotionContactLiftEnv):
    def _plan_height(self):
        c=self.height_coordinator;previous=c.goal.clone();before=self.height_preview_no_common_plan
        MotionContactDatumEnv._plan_height(self);basic=c.goal.clone();basic_bad=self.height_preview_no_common_plan-before
        c.goal.copy_(previous);self.height_preview_no_common_plan=before
        MotionContactLiftEnv._plan_height(self);full=c.goal.clone();full_bad=self.height_preview_no_common_plan-before
        selected,optional=choose_goal(basic,full,c.value,c.velocity);c.goal.copy_(selected)
        self.optional_preview_env_plans=getattr(self,'optional_preview_env_plans',0)+int(optional.sum())
        self.basic_preview_no_common_plans=getattr(self,'basic_preview_no_common_plans',0)+basic_bad
        self.optional_preview_no_common_plans=getattr(self,'optional_preview_no_common_plans',0)+full_bad
        self.peak_full_preview_goal_m=max(getattr(self,'peak_full_preview_goal_m',0.),float(full.abs().max()))
