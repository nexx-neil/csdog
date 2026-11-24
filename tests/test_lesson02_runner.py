"""Protect paired-experiment fairness and reject successful exits without evidence."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/lesson02_yaw_ab.py"
spec = importlib.util.spec_from_file_location("lesson02_yaw_ab", SCRIPT)
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


class Lesson02Tests(unittest.TestCase):
    def test_arms_share_parent_budget_seed_and_differ_only_in_width_and_log_name(self):
        _, a = lesson.command("control", "test")
        _, b = lesson.command("yaw_tight", "test")
        excluded = {a.index("--run_name") + 1, len(a) - 1}
        self.assertEqual([x for i, x in enumerate(a) if i not in excluded],
                         [x for i, x in enumerate(b) if i not in excluded])
        for invocation in (a, b):
            self.assertEqual(invocation[invocation.index("--resume_path") + 1], str(lesson.PARENT))
            self.assertEqual(invocation[invocation.index("--max_iterations") + 1], "10")
            self.assertEqual(invocation[invocation.index("--segment_iterations") + 1], "5")
            self.assertIn("--policy_only_resume", invocation)
        self.assertEqual(a[-1], "env.tracking_ang_vel_std=0.25")
        self.assertEqual(b[-1], "env.tracking_ang_vel_std=0.15")

    def test_failed_control_does_not_skip_independent_candidate_or_accept_empty_zero_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent = root / "parent.pt"
            reference = root / "reference.json"
            parent.write_bytes(b"fake parent, never loaded as policy")
            reference.write_text("{}")
            called = []

            def stub_command(arm, stamp):
                called.append(arm)
                # No simulator or policy imports: exercise process failure and missing evidence only.
                return f"stub_{arm}", [sys.executable, "-c", "raise SystemExit(1)" if arm == "control" else "pass"]

            with (patch.object(lesson, "ROOT", root), patch.object(lesson, "PARENT", parent),
                  patch.object(lesson, "REFERENCE", reference), patch.object(lesson, "LOG_ROOT", root / "runs"),
                  patch.object(lesson, "preflight", return_value={"checkpoint_sha256": lesson.sha256(parent)}),
                  patch.object(lesson, "command", side_effect=stub_command),
                  patch.object(sys, "argv", [str(SCRIPT)]), contextlib.redirect_stdout(io.StringIO())):
                status = lesson.main()
            self.assertEqual(status, 2)
            self.assertEqual(called, ["control", "yaw_tight"])
            manifest = next((root / "outputs/motion_foundation").glob("*/experiment.json"))
            value = json.loads(manifest.read_text())
            self.assertEqual(value["arms"]["control"]["returncode"], 1)
            self.assertEqual(value["arms"]["yaw_tight"]["returncode"], 0)
            self.assertTrue(all(x["status"] == "REJECTED_OR_RUNTIME_ERROR" for x in value["arms"].values()))


if __name__ == "__main__":
    unittest.main()
