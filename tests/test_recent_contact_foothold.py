import unittest
import torch
from csdog_motion.recent_contact_foothold import RecentContactMemory

class RecentContactTests(unittest.TestCase):
    def case(self):
        m=RecentContactMemory(1);s=torch.tensor([[False,True,False,False]]);p=torch.zeros(1,4,3);p[:,:,2]=.12;f=torch.zeros_like(p);f[0,1,2]=36.;r=torch.full((1,4),.12);xyz=p.clone();xyz[:,:,2]+=.018;env=torch.tensor([True]);err=torch.zeros(1,4)
        m.update(1,s,p,f,r,xyz,err.bool(),env,hard_invalid=err.bool())
        return m,s,p,f,r,xyz,env
    def bind(self,m,s,p,f,r,xyz,env,tick=2):
        missing=torch.full_like(p,float('nan'));zero=f*0;low=r-.029;now=xyz.clone();now[0,1,0]+=.006;now[0,1,1]+=.004
        e=torch.zeros_like(r);e[0,1]=.0115;margin=torch.ones_like(r)*.1;margin[0,1]=0
        m.update(tick,s,missing,zero,low,now,e>.00005,env,hard_invalid=e>.00005)
        return m.late_bind(tick,s,missing,zero,low,now,e,margin,env),zero
    def test_previous_loaded_point_can_bridge_current_zero_vertical_force(self):
        m,s,p,f,r,xyz,env=self.case();entered,forces=self.bind(m,s,p,f,r,xyz,env)
        self.assertTrue(entered[0,1]);self.assertTrue(torch.equal(m.xyz[0,1],xyz[0,1]));self.assertEqual(int(m.contact_tick[0,1]),1);self.assertEqual(float(forces.abs().sum()),0.);self.assertAlmostEqual(m.max_recent_age_s,.02,places=6)
    def test_no_measured_positive_load_cannot_create_archive(self):
        m,s,p,f,r,xyz,env=self.case();m.reset(torch.tensor([0]));entered,_=self.bind(m,s,p,f,r,xyz,env);self.assertFalse(entered.any())
    def test_expired_contact_cannot_reappear_as_support_reference(self):
        m,s,p,f,r,xyz,env=self.case();entered,_=self.bind(m,s,p,f,r,xyz,env,tick=5);self.assertFalse(entered.any())
    def test_scheduled_liftoff_never_activates_a_cached_stance(self):
        m,s,p,f,r,xyz,env=self.case();entered,_=self.bind(m,s&False,p,f,r,xyz,env);self.assertFalse(entered.any())
    def test_large_actual_foot_motion_disqualifies_old_contact(self):
        m,s,p,f,r,xyz,env=self.case();far=xyz.clone();far[0,1,0]+=.04;entered,_=self.bind(m,s,p,f,r,far,env);self.assertFalse(entered.any())
    def test_repeated_late_binding_does_not_change_memory_or_counters(self):
        m,s,p,f,r,xyz,env=self.case();self.bind(m,s,p,f,r,xyz,env);before=m.xyz.clone();count=m.recent_events
        entered=m.late_bind(2,s,p,f,r,xyz+1,torch.ones_like(r),r*0,env);self.assertFalse(entered.any());self.assertTrue(torch.equal(before,m.xyz));self.assertEqual(m.recent_events,count)
