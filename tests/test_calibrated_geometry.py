import json
from pathlib import Path
import sys
import types
import tempfile
import unittest
import xml.etree.ElementTree as ET
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "source/stackforce_simready_generated_robot_lab"))
from audit_motion_mechanics import Leg
from csdog_motion.calibration import ASSET, calibrated_data, calibrated_contract, posture_contract
from csdog_motion.contracts import contract, JOINT_NAMES
from csdog_motion.training import validate_checkpoint


class CalibratedGeometryTests(unittest.TestCase):
    def test_contacts_match_profile_and_mesh_paths_exist(self):
        tree = ET.parse(ASSET / "robot_sim.urdf").getroot()
        profile = json.loads((ROOT / "config/csdog_v2_hardware_profile.json").read_text())
        for name in ("lr", "lf", "rf", "rr"):
            np.testing.assert_allclose(Leg(tree, name).sole,
                profile["derived_collision"]["sole_centers_in_knee_link_m"][f"link_{name}_knee"], atol=1e-10)
        for mesh in tree.findall(".//mesh"):
            self.assertTrue((ASSET / mesh.get("filename")).is_file())

    def test_nominal_joints_recover_declared_feet_and_stay_within_soft_limits(self):
        data = calibrated_data()
        tree = ET.parse(ASSET / "robot_sim.urdf").getroot()
        for name in ("lr", "lf", "rf", "rr"):
            q = np.array([data["standing_joint_angles"][f"joint_{name}_{i}"] for i in (1, 2, 3)])
            np.testing.assert_allclose(Leg(tree, name).evaluate(q)[0], data["nominal_sole_positions_body_m"][name], atol=1e-6)
            for i, angle in enumerate(q, 1):
                limit = tree.find(f"joint[@name='joint_{name}_{i}']/limit")
                self.assertGreaterEqual(angle - .35, float(limit.get("lower")) * .9)
                self.assertLessEqual(angle + .35, float(limit.get("upper")) * .9)

    def test_calibration_has_distinct_contract_and_original_is_unchanged(self):
        before = contract()
        new = calibrated_contract()
        self.assertNotEqual(before["compatibility_tag"], new["compatibility_tag"])
        self.assertEqual(len(new["nominal_joint_positions_rad"]), 12)
        self.assertEqual(contract(), before)
        with tempfile.TemporaryDirectory() as folder:
            checkpoint = Path(folder) / "model.pt"
            Path(str(checkpoint) + ".metadata.json").write_text(json.dumps({
                "checkpoint_compatibility_tag": new["compatibility_tag"],
                "motion_contract": new, "actuated_joint_names": JOINT_NAMES}))
            # A v3 checkpoint must not silently run on the original geometry.
            cfg = types.SimpleNamespace(checkpoint_compatibility_tag=before["compatibility_tag"],
                                        motion_contract=before, actuated_joint_names=JOINT_NAMES)
            with self.assertRaises(ValueError):
                validate_checkpoint(checkpoint, cfg, policy_only=True)

    def test_posture_contract_cannot_be_confused_with_geometry_only(self):
        self.assertNotEqual(calibrated_contract()["compatibility_tag"], posture_contract()["compatibility_tag"])
        self.assertIn("posture_blend", posture_contract()["action"])


if __name__ == "__main__":
    unittest.main()
