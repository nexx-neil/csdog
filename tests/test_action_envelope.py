import sys
from pathlib import Path
import types
import unittest
import numpy as np
import torch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "source/stackforce_simready_generated_robot_lab"))
sys.path.insert(0, str(ROOT / "scripts"))
from csdog_motion.action_bounds import action_bounds, clip_actions, executed_actions, KNEE_CLIP, envelope_contract
from csdog_motion.contracts import contract
from audit_motion_mechanics import Leg, URDF


class EnvelopeTests(unittest.TestCase):
    def test_stand_has_zero_residual_and_blend_happens_after_clipping(self):
        raw = torch.ones(3, 12) * 2.
        applied = executed_actions(raw, torch.ones(12), torch.tensor([[0.], [.5], [1.]]))
        self.assertTrue(torch.equal(applied[0], torch.zeros(12)))
        self.assertTrue(torch.equal(applied[1], torch.ones(12) * .5))
        self.assertTrue(torch.equal(applied[2], torch.ones(12)))

    def test_scalar_behavior_preserved_and_only_knees_expand(self):
        cfg = types.SimpleNamespace(action_clip=1., action_space=12)
        actions = torch.linspace(-2, 2, 120).reshape(10, 12)
        self.assertTrue(torch.equal(clip_actions(actions, action_bounds(cfg, "cpu")), actions.clamp(-1, 1)))
        cfg.action_clip_per_joint = KNEE_CLIP
        applied = clip_actions(torch.ones(1, 12) * 2, action_bounds(cfg, "cpu"))
        self.assertTrue(torch.allclose(applied[0, 2::3], torch.ones(4) * 1.2))
        self.assertTrue(torch.all(applied[0, 0::3] == 1))
        self.assertTrue(torch.all(applied[0, 1::3] == 1))

    def test_new_contract_is_distinct_without_mutating_original(self):
        before = contract()
        new = envelope_contract()
        self.assertNotEqual(new["compatibility_tag"], before["compatibility_tag"])
        self.assertEqual(new["action"]["clip_per_joint"], list(KNEE_CLIP))
        self.assertEqual(contract(), before)

    def test_invalid_bounds_fail_closed(self):
        for values in ([1.] * 11, [float("nan")] * 12, [-1.] * 12):
            with self.assertRaises(ValueError):
                action_bounds(types.SimpleNamespace(action_space=12, action_clip_per_joint=values), "cpu")

    def test_fk_jacobian_matches_finite_difference(self):
        tree = ET.parse(URDF).getroot()
        for name in ("lr", "lf", "rf", "rr"):
            leg = Leg(tree, name)
            q = np.array([.13, -.12, .28])
            _, jacobian, _ = leg.evaluate(q)
            numeric = np.stack([(leg.evaluate(q + np.eye(3)[i] * 1e-6)[0] - leg.evaluate(q - np.eye(3)[i] * 1e-6)[0]) / 2e-6 for i in range(3)], axis=1)
            np.testing.assert_allclose(jacobian, numeric, atol=1e-8)
            target = leg.evaluate(q)[0]
            fitted, error = leg.solve(target, .35, np.zeros(3))
            self.assertLess(error, 1e-7)
            np.testing.assert_allclose(leg.evaluate(fitted)[0], target, atol=1e-7)


if __name__ == "__main__":
    unittest.main()
