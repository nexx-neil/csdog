import unittest
import torch
from csdog_motion import trot_course as old
from csdog_motion.trot_extension import reference, valid_request, period, ExtensionCommands
from csdog_motion.trot_extension_policy import RoutedExtensionPolicy
from csdog_motion import trot_extension_flight as flight
from csdog_motion.trot_flight_policy import RoutedExtensionPolicy as FlightPolicy
from csdog_motion.commands import MotionCommandConfig
from csdog_motion.trajectory import TrajectoryConfig

class ConstantPolicy(torch.nn.Module):
    def __init__(self, value):
        super().__init__(); self.value = value
    def act_inference(self, obs):
        return torch.full((len(obs['policy']), 12), self.value)

class ExtensionTests(unittest.TestCase):
    def test_old_reference_and_phase_are_bitwise_retained(self):
        torch.manual_seed(3901)
        tw = torch.rand(320, 3) * torch.tensor([1.6, .8, 1.6]) - torch.tensor([.8, .4, .8])
        phase = torch.rand(320)
        nominal = torch.tensor([[-.24,.14,-.35],[.23,.14,-.35],[.23,-.14,-.35],[-.24,-.14,-.35]])
        args = (phase, tw, nominal, TrajectoryConfig(stance_fraction=.55))
        self.assertTrue(all(torch.equal(a,b) for a,b in zip(old.reference(*args), reference(*args))))
        cfg = MotionCommandConfig(limits=(1., .4, .8))
        a, b = old.TrotCommands(2, config=cfg), ExtensionCommands(2, config=cfg)
        for m in (a,b):
            m.set_request([.8,0,0]); m.applied[:,0]=.8; m.phase[:]=.2
        for _ in range(100):
            for m in (a,b): m.tick(.02)
        self.assertTrue(torch.equal(a.phase,b.phase))

    def test_clock_matches_extension_and_subset_does_not_advance_other_env(self):
        m = ExtensionCommands(2, config=MotionCommandConfig(limits=(1.,.4,.8)))
        m.set_request([1.,0,0]); m.applied[:,0]=1.; m.phase[:]=.2
        m.tick(.02, torch.tensor([0]), torch.ones(2,4,dtype=torch.bool))
        self.assertAlmostEqual(float(m.phase[0]), .25, places=6)
        self.assertAlmostEqual(float(m.phase[1]), .2, places=6)

    def test_only_finite_forward_single_axis_is_extended(self):
        values = torch.tensor([[1.,0,0],[1.001,0,0],[.9,.01,0],[-.9,0,0],[float('nan'),0,0],[.4,.3,.4]])
        self.assertEqual(valid_request(values).tolist(), [True,False,False,False,False,True])

    def test_router_preserves_old_outputs_and_has_smooth_endpoints(self):
        policy = RoutedExtensionPolicy(ConstantPolicy(3.),ConstantPolicy(1.))
        obs = torch.zeros(5,76); obs[:,9]=torch.tensor([.6,.8,.9,1.,1.1])
        result = policy.act_inference({'policy':obs})
        self.assertTrue(torch.equal(result[:2],torch.ones(2,12)))
        self.assertTrue(torch.allclose(result[2],torch.full((12,),2.),atol=2e-6))
        self.assertTrue(torch.equal(result[3:],torch.full((2,12),3.)))

class FlightTests(unittest.TestCase):
    def test_flight_branch_retains_old_reference_and_reduces_return_stroke(self):
        phase = torch.linspace(0, .99, 100)
        tw = torch.zeros(100,3); tw[:,0]=.8
        nominal = torch.tensor([[-.24,.14,-.35],[.23,.14,-.35],[.23,-.14,-.35],[-.24,-.14,-.35]])
        args = (phase,tw,nominal,TrajectoryConfig(stance_fraction=.55))
        self.assertTrue(all(torch.equal(a,b) for a,b in zip(old.reference(*args),flight.reference(*args))))
        tw[:,0]=1.
        self.assertTrue(torch.allclose(flight.duty(tw),torch.full((100,),.30)))
        self.assertTrue(torch.allclose(flight.period(tw),torch.full((100,),.40)))
        m = flight.ExtensionCommands(2,config=MotionCommandConfig(limits=(1.,.4,.8)))
        m.set_request([1.,0,0]);m.applied[:,0]=1.;m.phase[:]=.2
        m.tick(.02,torch.tensor([0]))
        self.assertAlmostEqual(float(m.phase[0]),.25,places=6)
        self.assertAlmostEqual(float(m.phase[1]),.2,places=6)
        self.assertEqual(flight.valid_request(torch.tensor([[1.,0,0],[1.,.01,0]])).tolist(),[True,False])

    def test_flight_router_preserves_previous_actor_exactly(self):
        policy=FlightPolicy(ConstantPolicy(3.),ConstantPolicy(1.))
        obs=torch.zeros(3,76);obs[:,9]=torch.tensor([.8,.9,1.])
        value=policy.act_inference({'policy':obs})
        self.assertTrue(torch.equal(value[0],torch.ones(12)))
        self.assertTrue(torch.allclose(value[1],torch.full((12,),2.),atol=2e-6))
        self.assertTrue(torch.equal(value[2],torch.full((12,),3.)))

if __name__ == '__main__': unittest.main()
