import unittest
import torch
from csdog_motion.liftoff_handover import LiftOffMemory,fade

class LiftOffTests(unittest.TestCase):
    def setup_case(self):
        m=LiftOffMemory(1);stance=torch.tensor([[True,False,True,False]]);patch=stance.clone();phase=torch.tensor([.54]);duty=torch.tensor([.55]);p=torch.zeros(1,4,3);actual=p.clone();actual[0,0]=torch.tensor([.017,.009,.002])
        m.prepare(0,phase,stance,patch,p,actual,duty)
        return m,phase,stance,patch,p,actual,duty
    def test_first_swing_starts_from_measured_foot_and_other_legs_unchanged(self):
        m,phase,stance,patch,p,a,duty=self.setup_case();phase[:]=.56
        delta=m.prepare(1,phase,~stance,~patch&False,p,a,duty)
        self.assertTrue(torch.allclose((p+delta)[0,0],a[0,0],atol=1e-7));self.assertTrue(torch.equal(delta[0,1],p[0,1]));self.assertEqual(m.events,2)
    def test_contact_loss_during_stance_does_not_trigger_swing_offset(self):
        m,phase,stance,patch,p,a,duty=self.setup_case()
        delta=m.prepare(1,phase,stance,patch&False,p,a,duty);self.assertFalse(m.active.any());self.assertTrue(torch.equal(delta,p))
    def test_correction_fades_by_mid_swing_and_cannot_reappear_next_cycle(self):
        m,phase,stance,patch,p,a,duty=self.setup_case();phase[:]=.56;m.prepare(1,phase,~stance,patch&False,p,a,duty)
        self.assertTrue(torch.equal(m.forecast(phase,.12,.5,duty),p));self.assertTrue(torch.equal(m.forecast(phase,.6,.5,duty),p))
    def test_repeated_counter_and_subset_reset_do_not_mutate_state(self):
        m,phase,stance,patch,p,a,duty=self.setup_case();phase[:]=.56;first=m.prepare(1,phase,~stance,patch&False,p,a,duty);before=m.offset.clone();events=m.events
        again=m.prepare(1,phase,~stance,patch&False,p,a+1,duty);self.assertTrue(torch.equal(first,again));self.assertTrue(torch.equal(m.offset,before));self.assertEqual(m.events,events)
        m.reset(torch.tensor([0]));self.assertFalse(m.active.any());self.assertFalse(m.was_patch.any());self.assertEqual(float(m.offset.abs().sum()),0.)
    def test_large_unmeasured_jump_is_a_hard_failure(self):
        m,phase,stance,patch,p,a,duty=self.setup_case();phase[:]=.56;a[0,0,0]=.1
        with self.assertRaisesRegex(RuntimeError,'5cm bound'):m.prepare(1,phase,~stance,patch&False,p,a,duty)
    def test_envelope_has_zero_first_and_second_derivatives_at_endpoints(self):
        duty=torch.tensor([.55],dtype=torch.float64)
        for value in [.55,.775]:
            x=torch.tensor([[value]],dtype=torch.float64,requires_grad=True);y=fade(x,duty);v=torch.autograd.grad(y,x,create_graph=True)[0];acc=torch.autograd.grad(v,x)[0]
            self.assertLess(float(v.abs().max()),1e-10);self.assertLess(float(acc.abs().max()),1e-9)
