#!/usr/bin/env python3
"""Explicit mesh cooking / static support diagnostic, initialized in a pre-screened pose.

No stand-to-lie trajectory, policy loading, optimization or locomotion release.
"""
import argparse
import json
from pathlib import Path
import traceback

from isaaclab.app import AppLauncher
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--provenance", type=Path, required=True)
parser.add_argument("--pose", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--record", action="store_true")
parser.add_argument("--repeats", type=int, default=1)
parser.add_argument("--seed", type=int, default=1709)
parser.add_argument("--cooking-quality", choices=("default", "fine"), default="default")
parser.add_argument("--fixture", choices=("full-platform", "belly-pedestal"), default="full-platform",
                    help="The small pedestal is a sensor/load positive control, never a flat-ground lie test")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
if not 1 <= args.repeats <= 8:
    parser.error("repeats must be 1..8")
if args.output.exists():
    parser.error("Refusing to overwrite a diagnostic")
args.output.mkdir(parents=True)
args.enable_cameras = bool(args.record)
launcher = AppLauncher(args)

import subprocess
import torch
import isaaclab.sim as sim_utils
from isaaclab.sensors import ContactSensor, ContactSensorCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_reference import MotionReferenceEnv, MotionReferenceEnvCfg, configure_reference
from csdog_motion.residual_learning import learning_profile
from csdog_motion.contracts import JOINT_NAMES
from csdog_motion.training import file_hash


class BellyHoldEnv(MotionReferenceEnv):
    def _setup_scene(self):
        super()._setup_scene()
        import omni.usd
        from csdog_motion.collision_cooking import normalize_mesh_colliders, extract_cooked_meshes
        stage = omni.usd.get_context().get_stage()
        self.cooking_recipe = normalize_mesh_colliders(stage, "/World/envs/env_0/Robot", args.cooking_quality)
        self.cooked_audit = extract_cooked_meshes(stage, "/World/envs/env_0/Robot", self.cfg.robot.spawn.asset_path, args.output/"cooked.json")
        (args.output/"cooking_recipe.json").write_text(json.dumps(self.cooking_recipe, indent=2)+"\n")
        # GPU force filtering is unsupported for an infinite plane. A separate
        # rigid platform provides a supported, measurable contact target.
        size = (.18, .16, .10) if args.fixture == "belly-pedestal" else (3., 3., .10)
        platform = sim_utils.CuboidCfg(size=size,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(kinematic_enabled=True, disable_gravity=True),
            mass_props=sim_utils.MassPropertiesCfg(mass=100.),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(.22, .25, .28)))
        platform.func("/World/BellyPlatform", platform, translation=(0., 0., 0.))
        self.belly_ground = ContactSensor(ContactSensorCfg(
            prim_path="/World/envs/env_.*/Robot/base", filter_prim_paths_expr=["/World/BellyPlatform"],
            update_period=0., history_length=1))
        self.scene.sensors["belly_ground"] = self.belly_ground
        self.hip_ground = []
        for leg in ("lr", "lf", "rf", "rr"):
            sensor = ContactSensor(ContactSensorCfg(prim_path=f"/World/envs/env_.*/Robot/link_{leg}_hip_pitch",
                filter_prim_paths_expr=["/World/BellyPlatform"], update_period=0., history_length=1))
            self.scene.sensors[f"hip_{leg}_ground"] = sensor
            self.hip_ground.append(sensor)

    def _reference(self):
        q = self._robot.data.default_joint_pos[:, self._actuated_joint_ids]
        return q, torch.zeros(self.num_envs, 4, device=self.device), torch.zeros(self.num_envs, 4, dtype=torch.bool, device=self.device)

    def _pre_physics_step(self, actions):
        # Start already in this pose: no instant jump from a standing target.
        self._raw_actions = actions.clone()
        self._actions.zero_()
        self._processed_actions = self._reference()[0].clone()

    def _apply_action(self):
        self._robot.set_joint_position_target(self._processed_actions, joint_ids=self._actuated_joint_ids)
        self._robot.set_joint_velocity_target(torch.zeros_like(self._processed_actions), joint_ids=self._actuated_joint_ids)

    def _get_dones(self):
        data = self._robot.data
        height = data.root_pos_w[:, 2]-.05  # platform top
        finite = torch.isfinite(data.root_pos_w).all(1) & torch.isfinite(data.joint_pos).all(1)
        q = data.joint_pos[:, self._actuated_joint_ids]
        limits = data.soft_joint_pos_limits[:, self._actuated_joint_ids]
        failed = (~finite | (height < .07) | (height > .15)
            | (data.projected_gravity_b[:, 2] > -torch.cos(height.new_tensor(20.*torch.pi/180)))
            | (data.root_lin_vel_w.norm(dim=1)>1.5)
            | (data.joint_vel[:, self._actuated_joint_ids].abs().amax(1)>10.05)
            | ((q<limits[..., 0]-.005) | (q>limits[..., 1]+.005)).any(1))
        return failed, self.episode_length_buf >= self.max_episode_length-1


def main():
    provenance, pose = json.loads(args.provenance.read_text()), json.loads(args.pose.read_text())
    source = pose["source_meshes"]
    if source["minimum_mesh_floor_clearance_m"] < -.0001 or any(p["surface_intersection"] for p in source["near_nonadjacent_mesh_pairs"]):
        raise ValueError("Source mesh static pose screen failed")
    if pose["original_primitives"]["joint_soft_limit_reserve_rad"] < .0199:
        raise ValueError("Insufficient provisional soft-limit reserve")
    if file_hash(provenance["urdf"]) != provenance["diagnostic_urdf_sha256"] or not provenance["toe_partitions"]:
        raise ValueError("Expected independently screened toe-partition diagnostic asset")
    for path, sha in provenance["mesh_sha256"].items():
        if file_hash(path) != sha:
            raise ValueError("Mesh provenance changed")
    cfg = MotionReferenceEnvCfg()
    configure_reference(cfg, learning_profile())
    cfg.scene.num_envs, cfg.seed, cfg.sim.device = 1, args.seed, args.device
    cfg.periodic_commands, cfg.episode_length_s = False, 12.
    cfg.robot.spawn.asset_path = provenance["urdf"]
    cfg.robot.spawn.usd_dir = str((args.output/"converted_asset").resolve())
    cfg.robot.spawn.force_usd_conversion = True
    cfg.robot.spawn.collider_type = "convex_decomposition"
    cfg.robot.spawn.self_collision = True
    cfg.robot.spawn.articulation_props.enabled_self_collisions = True
    cfg.robot.spawn.replace_cylinders_with_capsules = False
    cfg.robot.init_state.pos = (0., 0., pose["height"]+.004+.05)
    cfg.robot.init_state.joint_pos = dict(zip(JOINT_NAMES, pose["q"]))
    cfg.base_height_target = pose["height"]
    cfg.motion_commands = dict(cfg.motion_commands, nominal_height_m=pose["height"], height_min_m=pose["height"], height_max_m=pose["height"])
    cfg.checkpoint_compatibility_tag = "csdog_belly_explicit_mesh_"+args.cooking_quality+"_diagnostic_v1"
    cfg.motion_contract = dict(cfg.motion_contract, compatibility_tag=cfg.checkpoint_compatibility_tag,
        collision_diagnostic=provenance, static_pose_file_sha256=file_hash(args.pose),
        quasi_static_foot_support_disabled=True, training_enabled=False)
    cfg.viewer.eye, cfg.viewer.lookat, cfg.viewer.resolution = (.85, 1.0, .62), (-.10, 0., .1), (960, 720)
    env = BellyHoldEnv(cfg=cfg, render_mode="rgb_array" if args.record else None)
    encoder = None
    try:
        env.reset()
        if args.record:
            encoder = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "960x720", "-r", "25", "-i", "-", "-an", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(args.output/"preview.mp4")], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        rows, forces, hip_forces, failures, trials = [], [], [], 0, []
        weight = float(env._robot.root_physx_view.get_masses().sum())*9.81
        with torch.inference_mode():
            for trial in range(args.repeats):
                env.reset()
                first_row, previous_failures = len(rows), failures
                observation_finite = True
                for trial_step in range(500):
                    step = trial_step
                    env.set_motion_request([0., 0., 0.])
                    obs, _, term, trunc, _ = env.step(torch.zeros(1, 12, device=env.device))
                    failures += int(term.sum()+trunc.sum())
                    d = env._robot.data
                    tilt = float(torch.acos((-d.projected_gravity_b[0, 2]).clamp(-1, 1))*180/torch.pi)
                    belly = env.belly_ground.data.force_matrix_w[0, 0].sum(0)
                    rows.append([float(d.root_pos_w[0, 2]-.05), tilt, float(belly[2]),
                        float(d.applied_torque[:, env._actuated_joint_ids].abs().max()),
                        float((d.joint_pos[:, env._actuated_joint_ids]-env._reference()[0]).abs().max()),
                        float(d.root_lin_vel_w.norm()), float(d.joint_vel[:, env._actuated_joint_ids].abs().max())])
                    forces.append(env._contact_sensor.data.net_forces_w[0].cpu().tolist())
                    hip_forces.append([float(sensor.data.force_matrix_w[0, 0, :, 2].sum()) for sensor in env.hip_ground])
                    if encoder and step%2 == 0:
                        frame = env.render().copy()
                        from PIL import Image, ImageDraw, ImageFont
                        canvas = Image.fromarray(frame)
                        draw = ImageDraw.Draw(canvas)
                        font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 20)
                        draw.rectangle((0, 0, 960, 65), fill=(24, 29, 36))
                        draw.text((12, 5), f"平面低姿态保持：第{trial+1}/{args.repeats}次；直接初始化，无下降/起身", font=font, fill="white")
                        draw.text((12, 33), f"机腹对地载荷 {float(belly[2]):.2f} N | 髋部合计 {sum(hip_forces[-1]):.2f} N", font=font, fill="white")
                        import numpy as np
                        frame = np.asarray(canvas)
                        encoder.stdin.write(frame.tobytes())
                        if step == 300:
                            from PIL import Image
                            Image.fromarray(frame).save(args.output/"belly_hold.png")
                    observation_finite &= bool(torch.isfinite(obs["policy"]).all())
                    if failures or not observation_finite:
                        break
                trial_data = torch.tensor(rows[first_row:])
                steady = trial_data[100:]
                trial_hips = torch.tensor(hip_forces[first_row:])[100:]
                ok = (step == 499 and observation_finite and failures == previous_failures and len(steady)>0
                    and bool(torch.isfinite(trial_data).all()) and float(steady[:, 1].square().mean().sqrt())<=3.
                    and abs(float(steady[:, 0].mean())-.10)<=.01
                    and float((steady[:, 2]>.6*weight).float().mean())>=.99
                    and float(steady[:, 4].max())<=.08)
                item = {"trial": trial, "gate": "PASS" if ok else "FAIL", "steps": len(trial_data),
                    "unexpected_terminations": failures-previous_failures, "finite_observations": observation_finite}
                if len(steady):
                    item.update(height_mean_m=float(steady[:, 0].mean()), tilt_rms_deg=float(steady[:, 1].square().mean().sqrt()),
                        belly_ground_mean_force_n=float(steady[:, 2].mean()),
                        belly_contact_fraction=float((steady[:, 2]>.6*weight).float().mean()),
                        joint_error_max_rad=float(steady[:, 4].max()), mean_hip_ground_force_n=trial_hips.mean(0).tolist())
                trials.append(item)
                print("STATIC TRIAL", item, flush=True)
                if not ok:
                    break
        data = torch.tensor(rows)
        steady = torch.cat([data[t*500+100:(t+1)*500] for t in range(len(trials)) if len(data[t*500+100:(t+1)*500])]) if len(data)>100 else data[:0]
        def all_steady(sequence):
            value = torch.tensor(sequence)
            return torch.cat([value[t*500+100:(t+1)*500] for t in range(len(trials)) if len(value[t*500+100:(t+1)*500])]) if len(value)>100 else value[:0]
        weight = float(env._robot.root_physx_view.get_masses().sum())*9.81
        complete = len(trials) == args.repeats and all(t["steps"] == 500 for t in trials)
        passed = complete and failures == 0 and all(t["gate"] == "PASS" for t in trials)
        report = {"complete": complete, "static_belly_gate": "PASS" if passed else "FAIL", "simulation_seconds": len(rows)*.02,
            "scope": "Initialized in a low pose, free-root static support only. Does not perform stand-to-lie or rise. Small pedestal is a load/sensor positive control only.",
            "trials": trials, "requested_repeats": args.repeats, "seed": args.seed,
            "fixture": args.fixture, "cooking_recipe": env.cooking_recipe, "cooked_audit": env.cooked_audit,
            "gradient_updates": 0, "unexpected_terminations": failures, "robot_weight_n": weight,
            "contact_filter": {"sensor": "base", "target": "/World/BellyPlatform", "platform_top_z_m": .05},
            "self_collisions_enabled": True, "quasi_static_foot_mg_support_enabled": False,
            "statistics_interval_s": [2., 10.], "raw_columns": ["root_height_m", "tilt_deg", "base_ground_normal_force_n", "peak_joint_torque_nm", "joint_error_max_rad", "root_speed_m_s", "joint_speed_max_rad_s"],
            "hip_ground_force_order": ["lr", "lf", "rf", "rr"],
            "mean_hip_ground_force_n": all_steady(hip_forces).mean(0).tolist() if len(hip_forces)>100 else [],
            "final_joint_positions_rad": env._robot.data.joint_pos[:, env._actuated_joint_ids][0].cpu().tolist(),
            "final_root_quaternion_wxyz": env._robot.data.root_quat_w[0].cpu().tolist(),
            "final_root_position_world_m": env._robot.data.root_pos_w[0].cpu().tolist(),
            "cooking_module_sha256": file_hash(Path(__file__).resolve().parents[1]/"source/stackforce_simready_generated_robot_lab/csdog_motion/collision_cooking.py"),
            "raw": rows, "contact_body_names": env._contact_sensor.body_names,
            "mean_body_net_force_n": all_steady(forces).mean(0).tolist() if len(forces)>100 else [],
            "gate_thresholds": {"tilt_rms_deg": 3., "height_error_m": .01, "belly_weight_fraction_min": .6, "belly_contact_fraction_min": .99, "joint_error_max_rad": .08},
            "urdf_sha256": file_hash(provenance["urdf"]), "pose_sha256": file_hash(args.pose), "script_sha256": file_hash(__file__),
            "posture_transition_authorized": False, "training_authorized": False}
        if len(steady):
            report.update(height_mean_m=float(steady[:, 0].mean()), tilt_rms_deg=float(steady[:, 1].square().mean().sqrt()),
                belly_ground_mean_force_n=float(steady[:, 2].mean()), joint_error_max_rad=float(steady[:, 4].max()))
        (args.output/"summary.json").write_text(json.dumps(report, indent=2)+"\n")
        print("BELLY STATIC", report["static_belly_gate"], {k: v for k, v in report.items() if k not in ("raw", "mean_body_net_force_n", "cooking_recipe")})
    finally:
        if encoder:
            encoder.stdin.close()
            errors = encoder.stderr.read().decode()
            if encoder.wait() != 0:
                print("Encoder failed:", errors)
        env.close()


try:
    main()
except BaseException:
    traceback.print_exc()
    raise
finally:
    launcher.app.close()
