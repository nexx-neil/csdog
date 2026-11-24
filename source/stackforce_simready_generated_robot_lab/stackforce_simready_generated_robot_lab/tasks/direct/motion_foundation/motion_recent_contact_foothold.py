"""Short real-contact archive; retain current-force support and all hard limits."""
import copy
from isaaclab.utils import configclass
from csdog_motion.recent_contact_foothold import TAG,contract,RecentContactMemory
from csdog_motion.post_filter_contacts import sensor_settings
from .motion_contact_tick_preview import MotionContactTickEnvCfg
from .motion_post_filter_contacts import MotionPostFilterEnv

@configclass
class MotionRecentContactEnvCfg(MotionContactTickEnvCfg):
    def __post_init__(self):
        super().__post_init__();self.checkpoint_compatibility_tag=TAG;self.motion_contract=contract(self.motion_contract)
        self.contact_sensor=copy.deepcopy(self.contact_sensor)
        settings=sensor_settings(self.sim.dt,self.contact_sensor.update_period,self.contact_sensor.history_length)
        self.contact_sensor.update_period=settings['update_period'];self.contact_sensor.history_length=settings['history_length']

class MotionRecentContactEnv(MotionPostFilterEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs);self.patch=RecentContactMemory(self.num_envs,self.device,self.patch.cfg,self.step_dt)
