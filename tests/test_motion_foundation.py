"""CPU regressions for the previously observed adapter and control failures."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest

import torch
from torch.nn import functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source/stackforce_simready_generated_robot_lab"))
from csdog_motion.commands import MotionCommandState, MotionCommandConfig, MotionMode, foot_velocity_body
from csdog_motion.contracts import migrate_observation_weights, FOUNDATION_TAG, JOINT_NAMES
from csdog_motion.evaluation import default_cases, profile_at, regression_gate
from csdog_motion.training import EpisodeCounterProxy, sync_learning_rate, bound_learning_rate, validate_checkpoint, install_checkpoint_records
from csdog_motion.staging import run_segments, require_validation_report

QUALITY_METRICS = {"body_tilt_rms_deg": 5.0, "body_height_std_m": 0.01,
                   "action_change_rms_per_step": 0.03, "contact_slide_speed_proxy_mps": 0.02}


class MotionTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)

    def test_low_speed_has_one_consistent_move_mode(self):
        motion = MotionCommandState(3)
        motion.set_request([[0.08, 0, 0], [0, 0.06, 0], [0, 0, 0.08]])
        for _ in range(20):
            motion.tick(0.02)
        self.assertTrue(torch.all(motion.mode == MotionMode.MOVE))
        self.assertTrue(torch.all(motion.extras()[:, 3] == 0))

    def test_acceleration_and_request_limits(self):
        motion = MotionCommandState(1)
        motion.set_request([10, -10, 10])
        motion.tick(0.02)
        self.assertTrue(torch.allclose(motion.request[0, :3], torch.tensor([0.4, -0.3, 0.4])))
        self.assertTrue(torch.allclose(motion.applied[0, :3], torch.tensor([0.016, -0.016, 0.032])))

    def test_stop_lands_before_freezing_phase(self):
        motion = MotionCommandState(1, config=MotionCommandConfig(clock_runs_in_stand=False))
        motion.set_request([0.3, 0, 0])
        for _ in range(30):
            motion.tick(0.02)
        motion.set_request([0, 0, 0])
        for _ in range(50):
            motion.tick(0.02, foot_contacts=torch.zeros(1, 4, dtype=torch.bool))
        self.assertEqual(motion.mode.item(), MotionMode.STOP)
        for _ in range(30):
            motion.tick(0.02, foot_contacts=torch.ones(1, 4, dtype=torch.bool))
        self.assertEqual(motion.mode.item(), MotionMode.STAND)
        phase = motion.phase.clone()
        motion.tick(0.02)
        self.assertTrue(torch.equal(motion.phase, phase))

    def test_migration_clock_continues_in_stand_without_forcing_swing_targets(self):
        motion = MotionCommandState(1)
        motion.tick(0.02)
        self.assertGreater(motion.phase.item(), 0)
        self.assertEqual(motion.mode.item(), MotionMode.STAND)
        contact, lift = motion.gait_targets()
        self.assertTrue(torch.all(contact == 1) and torch.all(lift == 0))

    def test_partial_reset_does_not_reset_other_dogs(self):
        motion = MotionCommandState(2)
        motion.set_request([0.3, 0, 0])
        motion.tick(0.1)
        preserved = motion.applied[1].clone()
        motion.reset(torch.tensor([0]))
        self.assertTrue(torch.equal(motion.applied[1], preserved))
        self.assertEqual(motion.mode[0].item(), MotionMode.STAND)

    def test_height_is_not_silently_enabled(self):
        motion = MotionCommandState(1)
        with self.assertRaises(ValueError):
            motion.set_request([0, 0, 0, 0.30])
        with self.assertRaises(ValueError):
            motion.set_request([float("nan"), 0, 0])

    def test_swing_endpoints_and_stand_support(self):
        motion = MotionCommandState(1)
        contact, lift = motion.gait_targets()
        self.assertTrue(torch.all(contact == 1))
        self.assertTrue(torch.all(lift == 0))
        motion.blend[:] = 1
        motion.phase[:] = 0.75
        _, lift = motion.gait_targets()
        self.assertAlmostEqual(lift[0, 0].item(), 0.032, places=6)

    def test_combined_stance_reference_contains_translation(self):
        feet = [[0.2, 0.1], [0.2, -0.1], [-0.2, 0.1], [-0.2, -0.1]]
        pure = foot_velocity_body(torch.tensor([[0., 0., 0.3]]), feet)
        mixed = foot_velocity_body(torch.tensor([[0., 0.2, 0.3]]), feet)
        self.assertTrue(torch.allclose(mixed - pure, torch.tensor([0., -0.2]).expand(1, 4, 2)))

    def test_episode_randomization_reaches_underlying_tensor_without_alias_break(self):
        class Wrapper(EpisodeCounterProxy):
            pass
        wrapper = Wrapper()
        counter = torch.zeros(16, dtype=torch.long)
        wrapper.env = types.SimpleNamespace(unwrapped=types.SimpleNamespace(episode_length_buf=counter))
        pointer = counter.data_ptr()
        wrapper.episode_length_buf = torch.arange(16)
        self.assertEqual(counter.data_ptr(), pointer)
        self.assertTrue(torch.equal(counter, torch.arange(16)))

    def test_migration_preserves_full_network_function(self):
        torch.manual_seed(4)
        weights = {}
        for kind, sizes in (("actor", [50, 16, 8, 12]), ("critic", [50, 16, 8, 1])):
            for i, (a, b) in enumerate(zip(sizes, sizes[1:])):
                weights[f"{kind}.{i * 2}.weight"] = torch.randn(b, a) * 0.1
                weights[f"{kind}.{i * 2}.bias"] = torch.randn(b) * 0.1
        new = migrate_observation_weights(weights)
        obs = torch.randn(100, 50)
        extended = torch.cat((obs, torch.randn(100, 4)), dim=1)
        def evaluate(state, value, kind):
            for i in (0, 2, 4):
                value = F.linear(value, state[f"{kind}.{i}.weight"], state[f"{kind}.{i}.bias"])
                if i != 4:
                    value = F.elu(value)
            return value
        for kind in ("actor", "critic"):
            self.assertTrue(torch.allclose(evaluate(weights, obs, kind), evaluate(new, extended, kind), atol=1e-6))

    def test_restored_optimizer_lr_is_synchronized_and_capped_at_step(self):
        parameter = torch.nn.Parameter(torch.tensor([1.0]))
        algorithm = types.SimpleNamespace(optimizer=torch.optim.Adam([parameter], lr=0.001), learning_rate=0.1)
        algorithm.optimizer.param_groups[0]["lr"] = 0.00011390625
        self.assertEqual(sync_learning_rate(algorithm), 0.00011390625)
        audit, handle = bound_learning_rate(algorithm, 1e-6, 1e-5)
        algorithm.optimizer.param_groups[0]["lr"] = 0.01
        parameter.square().sum().backward()
        algorithm.optimizer.step()
        self.assertEqual(algorithm.optimizer.param_groups[0]["lr"], 1e-5)
        self.assertEqual(algorithm.learning_rate, 1e-5)
        self.assertEqual(audit["optimizer_steps"], 1)
        handle.remove()

    def test_migrated_optimizer_is_rejected(self):
        cfg = types.SimpleNamespace(checkpoint_compatibility_tag=FOUNDATION_TAG, actuated_joint_names=JOINT_NAMES)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "init.pt"
            Path(str(path) + ".metadata.json").write_text(json.dumps({
                "checkpoint_compatibility_tag": FOUNDATION_TAG, "actuated_joint_names": JOINT_NAMES,
                "initialization_only": True,
            }))
            with self.assertRaises(ValueError):
                validate_checkpoint(path, cfg)
            self.assertTrue(validate_checkpoint(path, cfg, policy_only=True)["initialization_only"])

    def test_gate_rejects_failure_even_with_better_other_scores(self):
        value = {"complete": True, "protocol_sha256": "x", "physics_contract": {}, "cases": [
            {"name": "backward", "finite": True, "failures": 0, "steady_samples": 10,
             "steady_rmse": [0.05, 0.05, 0.05], "action_clip_fraction": 0.1, "target_limit_violations": 0, **QUALITY_METRICS}]}
        self.assertEqual(regression_gate(value, value)["status"], "PASS")
        candidate = copy.deepcopy(value)
        candidate["cases"][0]["failures"] = 1
        candidate["cases"][0]["steady_rmse"] = [0, 0, 0]
        self.assertEqual(regression_gate(candidate, value)["status"], "FAIL")
        candidate = copy.deepcopy(value)
        candidate["cases"] = []
        self.assertEqual(regression_gate(candidate, value)["status"], "FAIL")

    def test_gate_rejects_nonfinite_or_missing_reference_metrics(self):
        value = {"complete": True, "protocol_sha256": "x", "physics_contract": {}, "cases": [
            {"name": "forward", "finite": True, "failures": 0, "steady_samples": 10,
             "steady_rmse": [0.05, 0.05, 0.05], "action_clip_fraction": 0.1, "target_limit_violations": 0, **QUALITY_METRICS}]}
        broken = copy.deepcopy(value)
        broken["cases"][0]["action_clip_fraction"] = float("nan")
        self.assertEqual(regression_gate(broken, value)["status"], "FAIL")
        broken = copy.deepcopy(value)
        broken["cases"][0]["steady_rmse"][0] = float("nan")
        self.assertEqual(regression_gate(value, broken)["status"], "FAIL")

    def test_rejected_segment_never_reaches_next_update(self):
        updates, saves = [], []
        def validate(path, done):
            raise RuntimeError("rejected")
        with self.assertRaises(RuntimeError):
            run_segments(15, 5, lambda n, first: updates.append((n, first)),
                         lambda done: saves.append(done), validate)
        self.assertEqual(updates, [(5, True)])
        self.assertEqual(saves, [5])
        self.assertEqual(run_segments(0, 5, lambda *x: self.fail(), lambda *x: self.fail(), lambda *x: self.fail()), 0)

    def test_zero_exit_without_validation_report_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                require_validation_report(Path(directory) / "missing.json", "irrelevant.pt")

    def test_transition_failure_is_hard_rejection_without_steady_tracking_gate(self):
        reference = {"complete": True, "protocol_sha256": "x", "physics_contract": {}, "cases": [
            {"name": "start_stop", "protected": False, "finite": True, "failures": 0, "target_limit_violations": 0}]}
        candidate = copy.deepcopy(reference)
        candidate["cases"][0]["failures"] = 1
        self.assertEqual(regression_gate(candidate, reference)["status"], "FAIL")

    def test_every_checkpoint_records_real_updates_and_rng(self):
        parameter = torch.nn.Parameter(torch.ones(1))
        alg = types.SimpleNamespace(optimizer=torch.optim.Adam([parameter], lr=1e-5), learning_rate=1e-5,
                                    update=lambda: {"loss": 0.0})
        runner = types.SimpleNamespace(alg=alg)
        runner.save = lambda path, infos=None: torch.save({"model_state_dict": {}}, path)
        cfg = types.SimpleNamespace(checkpoint_compatibility_tag=FOUNDATION_TAG, actuated_joint_names=JOINT_NAMES,
                                    observation_space=54, action_space=12)
        count = install_checkpoint_records(runner, cfg, "test")
        runner.alg.update()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "periodic.pt"
            runner.save(path)
            metadata = json.loads(Path(str(path) + ".metadata.json").read_text())
            self.assertEqual(metadata["updates_in_this_run"], 1)
            self.assertEqual(count["updates_in_this_run"], 1)
            self.assertEqual(metadata["optimizer_lrs"], [1e-5])
            state = torch.load(str(path) + ".rng.pt", weights_only=True)
            self.assertFalse(state["environment_state_restored"])
            self.assertIn("torch_cpu", state)

    def test_profiles_include_real_in_episode_changes(self):
        profile = next(x["profile"] for x in default_cases() if x["name"] == "start_stop")
        self.assertEqual(profile_at(profile, 1)[0], [0, 0, 0])
        self.assertEqual(profile_at(profile, 3)[0], [0.3, 0, 0])
        self.assertEqual(profile_at(profile, 10)[0], [0, 0, 0])


if __name__ == "__main__":
    unittest.main()
