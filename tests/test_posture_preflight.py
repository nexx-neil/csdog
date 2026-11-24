import math
from pathlib import Path
import sys
import unittest

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "source/stackforce_simready_generated_robot_lab"))
from csdog_motion.calibration import ASSET
from csdog_motion.contracts import JOINT_NAMES
from csdog_motion.posture_preflight import PostureGeometry, primitive_extents, rpy_rotation, quintic_pose_segment
from csdog_motion.residual_learning import learning_profile
from csdog_motion.trajectory import LegKinematics


class PosturePreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = learning_profile()
        cls.q = np.array(cls.profile["nominal_joint_positions_rad"])
        cls.height = cls.profile["nominal_height_m"]
        cls.model = PostureGeometry(ASSET/"robot_sim.urdf", JOINT_NAMES)

    def test_fk_matches_independent_batched_jacobian_implementation(self):
        kin = LegKinematics(ASSET/"robot_sim.urdf", self.q, offset_bound=2., dtype=torch.float64)
        rng = np.random.default_rng(909)
        for q in [self.q, *rng.uniform(self.model.lower, self.model.upper, (4, 12))]:
            feet, _ = kin.fk(torch.tensor(q).reshape(1, 4, 3))
            frames = self.model.world_frames(q, self.height)
            actual = [frames[f"link_{leg}_sole"][:3, 3] for leg in ("lr", "lf", "rf", "rr")]
            expected = feet[0].numpy()+[0, 0, self.height]
            np.testing.assert_allclose(actual, expected, atol=1e-12)

    def test_tilted_cylinder_extents_match_dense_surface_extrema(self):
        rotation = rpy_rotation([.37, -.61, .29])
        angles = np.linspace(0, 2*math.pi, 30001)
        points = np.concatenate([np.stack((.022*np.cos(angles), .022*np.sin(angles),
                    np.full_like(angles, z)), axis=1) for z in [-.06, .06]])
        actual = np.max(np.abs(points@rotation.T), axis=0)
        np.testing.assert_allclose(primitive_extents("cylinder", (.022, .12), rotation), actual, atol=1e-9)

    def test_narrow_phase_confirms_nominal_proxy_overlap_instead_of_aabb_alarm(self):
        result = self.model.audit(self.q, self.height)
        collisions = [r for r in result["near_nonadjacent_pairs"] if r["signed_distance_m"] < -.0001]
        self.assertFalse(result["geometry_pass"])
        self.assertEqual(len(collisions), 2)
        expected = {frozenset((f"link_l{end}_hip_pitch", f"link_r{end}_hip_pitch")) for end in ("f", "r")}
        self.assertEqual({frozenset((r["a"][0], r["b"][0])) for r in collisions}, expected)
        for row in collisions:
            self.assertAlmostEqual(row["signed_distance_m"], -.0085, delta=.00003)
        self.assertGreaterEqual(min(r["clearance_m"] for r in result["floor"]), -1e-12)

    def test_lowering_without_leg_reposition_is_rejected(self):
        result = self.model.audit(self.q, .10)
        self.assertFalse(result["geometry_pass"])
        self.assertLess(min(r["clearance_m"] for r in result["floor"]), -.25)

    def test_limits_come_from_each_joint_class_without_clamping_requested_pose(self):
        np.testing.assert_allclose(self.model.upper.reshape(4, 3), np.tile([.585, 1.26, 1.62], (4, 1)))
        q = self.q.copy()
        q[0] = .60
        result = self.model.audit(q, self.height)
        self.assertFalse(result["geometry_pass"])
        self.assertAlmostEqual(result["joint_positions_rad"][0], .60)
        self.assertAlmostEqual(result["soft_limit_reserve_rad"], -.015)

    def test_invalid_values_are_rejected_before_distance_queries(self):
        for q, height, rpy in [(self.q[:3], .3, (0, 0, 0)),
                               (np.full(12, np.nan), .3, (0, 0, 0)),
                               (self.q, 0, (0, 0, 0)), (self.q, .3, (0, math.inf, 0))]:
            with self.assertRaises(ValueError):
                self.model.audit(q, height, rpy)

    def test_quintic_endpoints_derivative_and_true_peak(self):
        segment = quintic_pose_segment(self.q, self.height, self.q+.2, self.height-.06, 1., .002)
        np.testing.assert_allclose(segment["q"][[0, -1]], [self.q, self.q+.2])
        np.testing.assert_allclose(segment["q_velocity"][[0, -1]], 0)
        np.testing.assert_allclose(np.gradient(segment["q"], segment["time_s"], axis=0)[2:-2],
                                   segment["q_velocity"][2:-2], atol=1e-5)
        self.assertAlmostEqual(segment["exact_peak_joint_velocity_rad_s"], .375)
        self.assertAlmostEqual(np.abs(segment["q_velocity"]).max(), .375)


if __name__ == "__main__":
    unittest.main()
