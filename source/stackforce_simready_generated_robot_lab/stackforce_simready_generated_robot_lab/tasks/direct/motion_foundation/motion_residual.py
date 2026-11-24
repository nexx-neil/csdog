"""Fresh, contact-aware residual policy over the validated reference interface."""
import torch
from isaaclab.utils import configclass
from isaaclab.utils import math as math_utils

from csdog_motion.residual_learning import learning_profile, learning_contract, full_learning_contract, RESIDUAL_TAG, FULL_RESIDUAL_TAG, REWARD_SCALES, reward_terms
from .motion_reference import MotionReferenceEnv, MotionReferenceEnvCfg, configure_reference


@configclass
class MotionResidualEnvCfg(MotionReferenceEnvCfg):
    checkpoint_compatibility_tag=RESIDUAL_TAG
    observation_space=74
    motion_contract=learning_contract()
    # The generic legacy launcher remains blocked. Only the dedicated launcher
    # implements this task's initialization, safety gate and evaluation protocol.
    training_enabled=False
    residual_training_enabled=True
    training_block_reason="Use train_reference_residual.py with fresh initialization and the low-command development gate"
    reward_scales=dict(REWARD_SCALES)
    record_reward_terms=True
    command_ranges={"lin_vel_x":(-.15,.15),"lin_vel_y":(-.1,.1),"ang_vel_yaw":(-.15,.15)}

    def __post_init__(self):
        super().__post_init__()
        configure_reference(self,learning_profile())
        self.motion_contract=learning_contract()


class MotionResidualEnv(MotionReferenceEnv):
    def _get_observations(self):
        base=super()._get_observations()["policy"]
        robot=self._robot.data
        weight=self.cfg.reference_parameters["support_feedback"]["mass_kg"]*9.81
        forces=torch.linalg.vector_norm(self._contact_sensor.data.net_forces_w[:,self._foot_ids],dim=-1)/weight
        clearance=self._foot_clearance()
        return {"policy":torch.cat((base,forces.clamp(0,2),(clearance/.05).clamp(-1,2)),dim=1)}

    def _foot_clearance(self):
        return self._robot.data.body_pos_w[:,self._robot_foot_ids,2]-self._terrain.env_origins[:,2:3]-.018

    def _get_rewards(self):
        robot=self._robot.data
        foot_world=robot.body_pos_w[:,self._robot_foot_ids]
        quaternion=robot.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
        foot_body=math_utils.quat_apply_inverse(quaternion,(foot_world-robot.root_pos_w[:,None]).reshape(-1,3)).reshape(-1,4,3)
        reference_foot,_=self.reference_model.fk(self.reference_q.reshape(-1,4,3))
        forces=torch.linalg.vector_norm(self._contact_sensor.data.net_forces_w[:,self._foot_ids],dim=-1)
        weight=self.cfg.reference_parameters["support_feedback"]["mass_kg"]*9.81
        terms=reward_terms({
            "twist":torch.cat((robot.root_lin_vel_b[:,:2],robot.root_ang_vel_b[:,2:3]),dim=1),
            "command":self._commands,"stance":self.reference_stance,"blend":self.motion.blend,
            "foot_body":foot_body,"reference_foot":reference_foot,"contacts":forces>1.,
            "clearance":self._foot_clearance(),
            "desired_clearance":reference_foot[:,:,2]-self.reference_nominal[None,:,2],
            "force_over_weight":forces/weight,
            "height":robot.root_pos_w[:,2]-self._terrain.env_origins[:,2],"height_command":self.motion.applied[:,3],
            "gravity":robot.projected_gravity_b,"angular_xy":robot.root_ang_vel_b[:,:2],
            "vertical_velocity":robot.root_lin_vel_w[:,2],"foot_world_velocity":robot.body_lin_vel_w[:,self._robot_foot_ids],
            "torque":robot.applied_torque[:,self._actuated_joint_ids],"joint_acceleration":robot.joint_acc[:,self._actuated_joint_ids],
            "target":self._processed_actions,"previous_target":self.previous_joint_targets,
            "residual":self.last_residual_actions,"raw_action":self._raw_actions,
            "target_box_clip":self.target_box_limited,"terminated":self.reset_terminated,
        })
        reward=torch.zeros(self.num_envs,device=self.device)
        self.last_reward_terms={}
        for name,value in terms.items():
            scaled=value*self.cfg.reward_scales[name]*self.step_dt
            reward+=scaled
            self._episode_sums[name]+=scaled
            self.last_reward_terms[name]=scaled.detach()
        return reward


@configclass
class MotionResidualFullEnvCfg(MotionResidualEnvCfg):
    checkpoint_compatibility_tag=FULL_RESIDUAL_TAG
    motion_contract=full_learning_contract()
    command_ranges={"lin_vel_x":(-.4,.4),"lin_vel_y":(-.3,.3),"ang_vel_yaw":(-.4,.4)}

    def __post_init__(self):
        super().__post_init__()
        self.motion_contract=full_learning_contract()


class MotionResidualFullEnv(MotionResidualEnv):
    def _sample_commands(self,env_ids):
        super()._sample_commands(env_ids)
        if self.motion is not None:
            request=self.motion.request[env_ids].clone()
            replay=torch.rand(len(env_ids),device=self.device)<.4
            request[replay,:3]*=request.new_tensor([.375,1/3,.375])
            self.motion.set_request(request,env_ids)


from csdog_motion.speed_learning import SPEED_TAG, SPEED_LIMITS, speed_learning_contract, valid_speed_request


@configclass
class MotionResidualSpeedEnvCfg(MotionResidualFullEnvCfg):
    checkpoint_compatibility_tag=SPEED_TAG
    motion_contract=speed_learning_contract()

    def __post_init__(self):
        super().__post_init__()
        self.motion_contract=speed_learning_contract()
        self.motion_commands=dict(self.motion_commands,limits=SPEED_LIMITS)


class MotionResidualSpeedEnv(MotionResidualEnv):
    def set_motion_request(self,request,env_ids=None):
        twist=torch.as_tensor(request,device=self.device)[...,:3]
        if not valid_speed_request(twist).all():
            raise ValueError("Unvalidated combined high-speed command; use legacy mixed box or single-axis extension")
        super().set_motion_request(request,env_ids)

    def _sample_commands(self,env_ids):
        # Full legacy sampling is retained for40%; all rewards/control are unchanged.
        super()._sample_commands(env_ids)
        if self.motion is None:return
        request=self.motion.request[env_ids].clone()
        category=torch.rand(len(env_ids),device=self.device)
        low=category<.2
        request[low,:3]*=request.new_tensor([.375,1/3,.375])
        backward=(category>=.2)&(category<.4)
        request[backward,:3]=0
        request[backward,0]=-torch.empty(int(backward.sum()),device=self.device).uniform_(.15,.5)
        fast=(category>=.4)&(category<.6)
        ids=torch.where(fast)[0];axes=torch.randint(0,3,(len(ids),),device=self.device)
        request[ids,:3]=0
        magnitude=torch.empty(len(ids),device=self.device).uniform_(.6,1.)
        sign=torch.where(torch.rand(len(ids),device=self.device)<.5,-1.,1.)
        request[ids,axes]=request.new_tensor(SPEED_LIMITS)[axes]*magnitude*sign
        assert valid_speed_request(request[:,:3]).all()
        self.motion.set_request(request,env_ids)


from csdog_motion.speed_learning import STYLE_TAG,style_learning_contract,style_reward_scales


@configclass
class MotionResidualStyleEnvCfg(MotionResidualSpeedEnvCfg):
    checkpoint_compatibility_tag=STYLE_TAG
    reward_scales=style_reward_scales()
    motion_contract=style_learning_contract()

    def __post_init__(self):
        super().__post_init__()
        self.motion_contract=style_learning_contract()


class MotionResidualStyleEnv(MotionResidualSpeedEnv):
    pass
