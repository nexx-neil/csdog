from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_urdf", REPO / "scripts/audit_urdf.py")
assert SPEC is not None and SPEC.loader is not None
AUDIT_URDF = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT_URDF)


class UrdfAuditTests(unittest.TestCase):
    def arguments(self, expectations: Path) -> argparse.Namespace:
        return argparse.Namespace(
            urdf=REPO / "source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/robot.urdf",
            expectations=expectations,
            repo=REPO,
            max_collision_triangles=1000,
        )

    def test_v2_structure_passes_but_physics_readiness_fails(self) -> None:
        expectations = REPO / "config/csdog_v2_urdf_expectations.json"
        report = AUDIT_URDF.audit(self.arguments(expectations))
        self.assertEqual(report["gate"]["structure_status"], "PASS")
        self.assertEqual(report["gate"]["physics_readiness_status"], "FAIL")
        self.assertEqual(report["summary"]["revolute_joint_count"], 12)
        self.assertAlmostEqual(report["summary"]["total_mass_kg"], 7.60426080, places=7)

    def test_joint_order_mismatch_is_a_structural_failure(self) -> None:
        manifest = json.loads(
            (REPO / "config/csdog_v2_urdf_expectations.json").read_text(encoding="utf-8")
        )
        manifest["actuated_joint_names"][0:2] = reversed(manifest["actuated_joint_names"][0:2])
        with tempfile.TemporaryDirectory() as directory:
            expectations = Path(directory) / "bad-order.json"
            expectations.write_text(json.dumps(manifest), encoding="utf-8")
            report = AUDIT_URDF.audit(self.arguments(expectations))
        self.assertEqual(report["gate"]["structure_status"], "FAIL")
        self.assertIn("JOINT_ORDER_MISMATCH", {item["code"] for item in report["issues"]})


if __name__ == "__main__":
    unittest.main()
