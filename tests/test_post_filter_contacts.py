import json
import unittest
from pathlib import Path
import torch
from csdog_motion.post_filter_contacts import PostFilterMemory,sensor_settings

class PostFilterTests(unittest.TestCase):
    def case(self):
        d=json.loads((Path(__file__).parent/'fixtures/post_filter433.json').read_text());m=PostFilterMemory(1)
        p=torch.tensor([d['points']]);valid=torch.tensor([d['point_valid']]);p[~valid]=float('nan')
        f=torch.tensor([d['forces']]);r=torch.tensor([d['actual_rays']]);xyz=torch.tensor([d['foot_positions']]);stance=torch.tensor([d['stance']]);active=torch.tensor([True])
        before=torch.tensor([d['before']['error']]);margin=torch.tensor([d['before']['margin']]);unsafe=(before>.00005)|(margin<.03)
        m.update(433,stance,p,f,r,xyz,unsafe,active,hard_invalid=before>.00005)
        return d,m,stance,p,f,r,xyz,active
    def test_recorded_loaded_foot_missed_early_is_bound_after_filters(self):
        d,m,s,p,f,r,xyz,a=self.case();self.assertFalse(m.active.any());self.assertGreater(float(f[0,0,2]),28.)
        entered=m.late_bind(433,s,p,f,r,xyz,torch.tensor([d['after']['error']]),torch.tensor([d['after']['margin']]),a)
        self.assertTrue(entered[0,0]);self.assertEqual(int(entered.sum()),1);self.assertTrue(torch.equal(m.xyz[0,0],xyz[0,0]));self.assertEqual(m.last_tick,433)
    def test_same_tick_late_binding_is_idempotent(self):
        d,m,s,p,f,r,xyz,a=self.case();e=torch.tensor([d['after']['error']]);margin=torch.tensor([d['after']['margin']]);m.late_bind(433,s,p,f,r,xyz,e,margin,a);before=m.xyz.clone();events=m.late_events
        entered=m.late_bind(433,s,p,f,r,xyz+1,e,margin,a);self.assertFalse(entered.any());self.assertTrue(torch.equal(before,m.xyz));self.assertEqual(m.late_events,events)
    def test_no_loaded_point_cannot_create_support(self):
        d,m,s,p,f,r,xyz,a=self.case();entered=m.late_bind(433,s,p,f*0,r,xyz,torch.tensor([d['after']['error']]),torch.tensor([d['after']['margin']]),a);self.assertFalse(entered.any())
    def test_stale_counter_is_rejected(self):
        d,m,s,p,f,r,xyz,a=self.case()
        with self.assertRaisesRegex(RuntimeError,'current-tick'):m.late_bind(434,s,p,f,r,xyz,torch.tensor([d['after']['error']]),torch.tensor([d['after']['margin']]),a)
    def test_every_physics_step_preserves_or_extends_history_coverage(self):
        settings=sensor_settings(.005);self.assertEqual(settings,{'update_period':0.,'history_length':12});self.assertGreaterEqual(settings['history_length']*.005,3*.02)
    def test_float32_period_drift_reproduces_after16s_but_zero_period_never_skips(self):
        def intervals(period):
            t=torch.zeros(1);last=t.clone();indices=[]
            for i in range(1,3701):
                t+=.005
                if bool((t-last+1e-6>=period).item()):last.copy_(t);indices.append(i)
            return [b-a for a,b in zip(indices,indices[1:])if b>3200]
        self.assertGreaterEqual(max(intervals(.02)),5);self.assertEqual(max(intervals(0.)),1)
    def test_invalid_sensor_timebase_is_rejected(self):
        for dt in (0.,-.01,float('nan')):
            with self.assertRaises(ValueError):sensor_settings(dt)
