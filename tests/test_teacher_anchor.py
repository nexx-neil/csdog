import unittest
import torch
from tensordict import TensorDict
from rsl_rl.algorithms import PPO
from rsl_rl.modules import ActorCritic
from csdog_motion.teacher_anchor import configure_teacher_anchor,preservation_check


class TeacherAnchorTests(unittest.TestCase):
    def test_student_can_adapt_while_teacher_and_noise_stay_fixed(self):
        obs=TensorDict({'policy':torch.randn(8,175)},batch_size=[8])
        p=ActorCritic(obs,{'policy':['policy'],'critic':['policy']},12,
            actor_hidden_dims=[16],critic_hidden_dims=[16],activation='elu')
        a=PPO(p,learning_rate=.001,schedule='fixed');teacher=configure_teacher_anchor(a)
        before=p.actor[0].weight.detach().clone()
        for _ in range(3):
            a.optimizer.zero_grad();(p.act_inference(obs)-1).square().mean().backward();a.optimizer.step()
        self.assertTrue(preservation_check(p,teacher))
        self.assertFalse(torch.equal(p.actor[0].weight[:,:76],before[:,:76]))
        with torch.no_grad():teacher.actor[0].weight[0,0]+=1
        with self.assertRaises(RuntimeError):preservation_check(p,teacher)
