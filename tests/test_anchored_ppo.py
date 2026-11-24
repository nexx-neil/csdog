import copy
import unittest
import torch
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
from rsl_rl.algorithms import PPO
from csdog_motion.anchored_ppo import configure_scan_adapter, preservation_check, anchored_update


def policy():
    return ActorCritic(TensorDict({'policy':torch.zeros(8,175)},batch_size=[8]),
        {'policy':['policy'],'critic':['policy']},12,actor_hidden_dims=[16],critic_hidden_dims=[16],activation='elu')


class AnchorTests(unittest.TestCase):
    def test_positive_teacher_loss_moves_student_toward_frozen_target(self):
        p=policy();a=PPO(p,learning_rate=.001,schedule='fixed',
            num_learning_epochs=1,num_mini_batches=1,value_loss_coef=0.,entropy_coef=0.)
        obs=TensorDict({'policy':torch.randn(8,175)},batch_size=[8])
        with torch.no_grad():
            actions=p.act(obs);values=p.evaluate(obs);logp=p.get_actions_log_prob(actions)
            mu=p.action_mean;sigma=p.action_std
        a.teacher=copy.deepcopy(p).requires_grad_(False)
        with torch.no_grad():a.teacher.actor[-1].bias.add_(.2)
        a.teacher_coefficient=1.;a.teacher_action_scale=.1
        batch=(obs,actions,values,torch.zeros(8,1),values,logp[:,None],mu,sigma,(None,None),None)
        class Storage:
            def mini_batch_generator(self,*args):yield batch
            def clear(self):pass
        a.storage=Storage()
        target=a.teacher.act_inference(obs).detach()
        before=(p.act_inference(obs)-target).square().mean().item()
        result=anchored_update(a)
        after=(p.act_inference(obs)-target).square().mean().item()
        self.assertGreater(result['teacher'],0.)
        self.assertLess(after,before)
        self.assertTrue(all(t.grad is None for t in a.teacher.parameters()))

    def test_scan_learning_preserves_legacy_actor_and_teacher(self):
        p=policy();a=PPO(p,learning_rate=.001,schedule='fixed');teacher=configure_scan_adapter(a)
        before=p.actor[0].weight.detach().clone()
        x=TensorDict({'policy':torch.randn(8,175)},batch_size=[8])
        for _ in range(3):
            a.optimizer.zero_grad();loss=(p.act_inference(x)-1).square().mean();loss.backward();a.optimizer.step()
        self.assertTrue(preservation_check(p,teacher))
        self.assertFalse(torch.equal(before[:,76:],p.actor[0].weight[:,76:]))
        self.assertTrue(all(t.grad is None for t in teacher.parameters()))
        with torch.no_grad():p.actor[0].weight[0,0]+=1
        with self.assertRaises(RuntimeError):preservation_check(p,teacher)

    def test_zero_teacher_loss_matches_upstream_ppo_step(self):
        torch.manual_seed(12);p=policy();q=copy.deepcopy(p)
        args=dict(learning_rate=.001,schedule='fixed',num_learning_epochs=1,num_mini_batches=1)
        a=PPO(p,**args);b=PPO(q,**args)
        obs=TensorDict({'policy':torch.randn(8,175)},batch_size=[8])
        with torch.no_grad():
            actions=p.act(obs);values=p.evaluate(obs);logp=p.get_actions_log_prob(actions);mu=p.action_mean;sigma=p.action_std
        batch=(obs,actions,values,torch.randn(8,1),torch.randn(8,1),logp[:,None],mu,sigma,(None,None),None)
        class Storage:
            def mini_batch_generator(self,*args):yield batch
            def clear(self):self.cleared=True
        a.storage=Storage();b.storage=Storage();b.teacher=copy.deepcopy(q).requires_grad_(False)
        b.teacher_coefficient=0.;b.teacher_action_scale=.1
        upstream=a.update();result=anchored_update(b)
        for k,v in p.state_dict().items():torch.testing.assert_close(v,q.state_dict()[k],rtol=0,atol=0)
        for k,v in upstream.items():self.assertEqual(v,result[k])
        self.assertTrue(b.storage.cleared)
