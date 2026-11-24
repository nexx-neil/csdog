#!/usr/bin/env python3
"""Isolated 30s mesh-collision/self-contact standing diagnostic, zero learning."""
import argparse
import json
from pathlib import Path
import traceback

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--provenance", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
if args.output.exists():
    parser.error("Refusing to overwrite a diagnostic")
args.output.mkdir(parents=True)
launcher = AppLauncher(args)

import torch
from pxr import Usd, UsdGeom, UsdPhysics
import stackforce_simready_generated_robot_lab.tasks  # noqa
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_reference import MotionReferenceEnv, MotionReferenceEnvCfg, configure_reference
from csdog_motion.reference_control import reference_data
from csdog_motion.residual_learning import learning_profile
from csdog_motion.training import file_hash


class ExplicitMeshStandingEnv(MotionReferenceEnv):
    def _setup_scene(self):
        super()._setup_scene()
        import omni.usd
        from csdog_motion.collision_cooking import normalize_mesh_colliders
        self.cooking_recipe = normalize_mesh_colliders(omni.usd.get_context().get_stage(), "/World/envs/env_0/Robot", "fine")


def main():
    provenance = json.loads(args.provenance.read_text())
    if file_hash(provenance["urdf"]) != provenance["diagnostic_urdf_sha256"]:
        raise ValueError("Diagnostic URDF hash mismatch")
    for path, sha in provenance["mesh_sha256"].items():
        if file_hash(path) != sha:
            raise ValueError("Source mesh hash mismatch")
    cfg = MotionReferenceEnvCfg()
    configure_reference(cfg, learning_profile())
    cfg.scene.num_envs = 1
    cfg.seed = 1709
    cfg.sim.device = args.device
    cfg.periodic_commands = False
    cfg.episode_length_s = 40.
    cfg.robot.spawn.asset_path = provenance["urdf"]
    cfg.robot.spawn.usd_dir = str((args.output/"converted_asset").resolve())
    cfg.robot.spawn.force_usd_conversion = True
    for key, value in provenance["required_import_settings"].items():
        if key == "enabled_self_collisions":
            cfg.robot.spawn.articulation_props.enabled_self_collisions = value
        else:
            setattr(cfg.robot.spawn, key, value)
    cfg.robot.init_state.pos = (0., 0., cfg.base_height_target+.01)
    cfg.checkpoint_compatibility_tag = "csdog_explicit_fine_collision_stand_diagnostic_v1"
    cfg.motion_contract = dict(cfg.motion_contract, compatibility_tag=cfg.checkpoint_compatibility_tag,
                               collision_diagnostic=provenance, training_enabled=False)
    env = ExplicitMeshStandingEnv(cfg=cfg)
    try:
        obs, _ = env.reset()
        frames = []
        failures = 0
        finite = True
        forces = []
        robot = env._robot
        actions = torch.zeros(1, 12, device=env.device)
        with torch.inference_mode():
            for step in range(1500):
                env.set_motion_request([0., 0., 0.])
                obs, _, term, trunc, _ = env.step(actions)
                failures += int(term.sum()+trunc.sum())
                finite &= bool(torch.isfinite(obs["policy"]).all())
                d = robot.data
                tilt = torch.acos((-d.projected_gravity_b[:, 2]).clamp(-1, 1))*180/torch.pi
                if not finite or failures or tilt.max() > 20:
                    break
                if step >= 250:
                    frames.append(torch.stack((d.root_pos_w[0, 2], tilt[0],
                        d.root_lin_vel_b[0].norm(), d.root_ang_vel_b[0].norm(),
                        d.applied_torque[:, env._actuated_joint_ids].abs().max())).cpu().tolist())
                    forces.append(env._contact_sensor.data.net_forces_w[0].cpu().tolist())
        data = torch.tensor(frames)
        result = {"complete": step == 1499, "physics_steps": step+1, "gradient_updates": 0,
            "scope": "One nominal clone, 30s zero-policy self-collision-enabled standing only; no gait or lie/rise validation",
            "urdf_sha256": file_hash(provenance["urdf"]), "self_collisions_enabled": True,
            "collider_type": cfg.robot.spawn.collider_type, "finite": finite,
            "unexpected_terminations": failures, "body_names": robot.body_names,
            "contact_body_names": env._contact_sensor.body_names,
            "contact_foot_ids": env._foot_ids,
            "statistics_interval_s": [5., (step+1)*.02],
            "height_mean_m": float(data[:, 0].mean()) if len(data) else None,
            "tilt_rms_deg": float(data[:, 1].square().mean().sqrt()) if len(data) else None,
            "max_speed_m_s": float(data[:, 2].max()) if len(data) else None,
            "max_angular_speed_rad_s": float(data[:, 3].max()) if len(data) else None,
            "peak_joint_torque_nm": float(data[:, 4].max()) if len(data) else None,
            "source_sha256": {str(Path(__file__).resolve()): file_hash(__file__)},
            "cooking_recipe": env.cooking_recipe,
            "stand_gate": "FAIL", "training_authorized": False, "posture_execution_authorized": False}
        if len(data):
            force = torch.tensor(forces)
            result["mean_body_net_contact_force_n"] = force.mean(0).tolist()
            feet = env._foot_ids
            duty = (force[:, feet].norm(dim=-1)>1.).all(dim=1).float().mean()
            result["all_four_foot_contact_fraction"] = float(duty)
            passed = (result["complete"] and finite and failures == 0 and float(duty) >= .99
                and result["tilt_rms_deg"] <= 3. and abs(result["height_mean_m"]-cfg.base_height_target) <= .02)
            result["stand_gate"] = "PASS" if passed else "FAIL"
        result["gate_thresholds"] = {"duration_s": 30., "terminations": 0, "tilt_rms_deg": 3.,
            "height_error_m": .02, "four_foot_contact_min": .99}
        (args.output/"summary.json").write_text(json.dumps(result, indent=2)+"\n")
        print("POSTURE COLLISION STAND", result["stand_gate"], {k: v for k, v in result.items() if k != "cooking_recipe"})
    finally:
        env.close()


try:
    main()
except BaseException:
    traceback.print_exc()
    raise
finally:
    launcher.app.close()
