from isaaclab.utils import configclass

from ...generated_robot.agents.rsl_rl_ppo_cfg import GeneratedRobotPPORunnerCfg


@configclass
class CSDogV2CalibrationPPORunnerCfg(GeneratedRobotPPORunnerCfg):
    """Runner metadata only; training.py rejects this calibration task."""

    experiment_name = "csdog_v2_calibration_do_not_train"
    max_iterations = 1


@configclass
class CSDogV2LocomotionPPORunnerCfg(GeneratedRobotPPORunnerCfg):
    """Independent v2 policy; no v1 checkpoint or optimizer state is reused."""

    experiment_name = "csdog_v2_locomotion"
    max_iterations = 1000
    save_interval = 50


@configclass
class CSDogV2PhaseGaitPPORunnerCfg(GeneratedRobotPPORunnerCfg):
    """Fresh policy with two gait-clock observations; old checkpoints are incompatible."""

    experiment_name = "csdog_v2_phase_gait"
    max_iterations = 1000
    save_interval = 50


@configclass
class CSDogV2TurnStylePPORunnerCfg(CSDogV2PhaseGaitPPORunnerCfg):
    """Short refinement task for compact, upright in-place turns."""

    experiment_name = "csdog_v2_turn_style"


@configclass
class CSDogV2TeleopPPORunnerCfg(CSDogV2TurnStylePPORunnerCfg):
    """Mixed-command refinement for QWEASD control."""

    experiment_name = "csdog_v2_teleop"
