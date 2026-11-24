import sys
from pathlib import Path
import unittest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source/stackforce_simready_generated_robot_lab"))
from csdog_motion.curriculum import lateral_balanced_bank, sample_lateral_balanced
from csdog_motion.evaluation import default_cases, protocol_hash


class CurriculumTests(unittest.TestCase):
    def test_distribution_preserves_rehearsal_and_samples_all_lateral_bands(self):
        torch.set_num_threads(1)
        bank = lateral_balanced_bank()
        self.assertAlmostEqual(sum(row[3] for row in bank), 1.0)
        generator = torch.Generator().manual_seed(42)
        commands, labels = sample_lateral_balanced(100000, generator=generator)
        self.assertTrue(torch.isfinite(commands).all())
        self.assertTrue(torch.all(commands.abs() <= torch.tensor([.4, .3, .4]) + 1e-6))
        for i, (name, low, high, weight) in enumerate(bank):
            selected = commands[labels == i]
            self.assertGreater(len(selected), 0, name)
            self.assertAlmostEqual(float((labels == i).float().mean()), weight, delta=.005, msg=name)
            self.assertTrue(torch.all(selected >= torch.tensor(low) - 1e-6), name)
            self.assertTrue(torch.all(selected <= torch.tensor(high) + 1e-6), name)
        for side in ("left", "right"):
            self.assertTrue(all(any(row[0] == f"{side}_{band}" for row in bank) for band in ("low", "mid", "high")))

    def test_expanded_protocol_protects_low_speed_without_changing_original_cases(self):
        old = default_cases()
        new = default_cases("lateral_grid")
        self.assertEqual(new[:14], old)
        self.assertEqual(len(new), 18)
        self.assertEqual(len({c["name"] for c in new}), 18)
        self.assertTrue(all(c["protected"] for c in new[14:]))
        self.assertNotEqual(protocol_hash(old, 1000, .02, 4), protocol_hash(new, 1000, .02, 4))
        with self.assertRaises(ValueError):
            default_cases("typo")


if __name__ == "__main__":
    unittest.main()
