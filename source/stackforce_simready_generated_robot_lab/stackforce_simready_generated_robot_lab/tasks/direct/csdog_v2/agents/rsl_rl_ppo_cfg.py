from isaaclab.utils import configclass

from ...generated_robot.agents.rsl_rl_ppo_cfg import GeneratedRobotPPORunnerCfg


@configclass
class CSDogV2CalibrationPPORunnerCfg(GeneratedRobotPPORunnerCfg):
    """Runner metadata only; training.py rejects this calibration task."""

    experiment_name = "csdog_v2_calibration_do_not_train"
    max_iterations = 1
