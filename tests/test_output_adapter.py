import unittest
import torch
from tensordict import TensorDict
from rsl_rl.algorithms import PPO
from rsl_rl.modules import ActorCritic
from csdog_motion.output_adapter import configure_output_adapter,preservation_check


class OutputAdapterTests(unittest.TestCase):
    def test_only_scan_inputs_and_output_head_change(self):
        obs=TensorDict({'policy':torch.randn(8,175)},batch_size=[8])
        p=ActorCritic(obs,{'policy':['policy'],'critic':['policy']},12,
            actor_hidden_dims=[16,16],critic_hidden_dims=[16],activation='elu')
        a=PPO(p,learning_rate=.001,schedule='fixed');teacher=configure_output_adapter(a)
        first=p.actor[0].weight.detach().clone();last=p.actor[-1].weight.detach().clone()
        for _ in range(3):
            a.optimizer.zero_grad();(p.act_inference(obs)-1).square().mean().backward();a.optimizer.step()
        self.assertTrue(preservation_check(p,teacher))
        self.assertTrue(torch.equal(p.actor[0].weight[:,:76],first[:,:76]))
        self.assertFalse(torch.equal(p.actor[-1].weight,last))
        self.assertTrue(all(x.grad is None for x in teacher.parameters()))
