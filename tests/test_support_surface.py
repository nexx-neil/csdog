import unittest
import torch
from csdog_motion.support_surface import SupportSurface,contract


class SurfaceTests(unittest.TestCase):
    def test_repeated_reads_are_idempotent_and_reset_is_local(self):
        f=SupportSurface(2,'cpu');f.update(torch.tensor([1.,2.]),0)
        a=f.update(torch.tensor([2.,3.]),1).clone()
        for _ in range(4):self.assertTrue(torch.equal(f.update(torch.tensor([2.,3.]),1),a))
        f.reset(torch.tensor([0]));b=f.update(torch.tensor([8.,9.]),1)
        self.assertEqual(float(b[0]),8.);self.assertEqual(float(b[1]),float(a[1]))
        with self.assertRaises(ValueError):f.update(torch.tensor([float('inf'),0.]),2)

    def test_filter_is_invariant_to_world_height_translation(self):
        a=SupportSurface(2,'cpu');b=SupportSurface(2,'cpu')
        for t in range(10):
            z=torch.tensor([.01*t,-.02*t]);torch.testing.assert_close(a.update(z,t)+4,b.update(z+4,t),atol=1e-6,rtol=1e-5)
