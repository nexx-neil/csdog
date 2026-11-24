import sys,unittest
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source/stackforce_simready_generated_robot_lab'))
from csdog_motion.skill_supervisor import SkillSupervisor,SkillMode,SkillFault


class SkillTests(unittest.TestCase):
    def setUp(self):
        self.s=SkillSupervisor(2);h=self.s.cfg.nominal_height_m
        self.sensor=dict(twist=torch.zeros(2,3),tilt_deg=torch.zeros(2),contacts=torch.ones(2,4,dtype=torch.bool),blend=torch.zeros(2),applied_height=torch.full((2,),h),actual_height=torch.full((2,),h))
    def tick(self,n=1):
        for _ in range(n):out=self.s.tick(.02,**self.sensor)
        return out
    def lower(self):
        self.s.request_crouch();self.tick(18)
        self.assertTrue((self.s.mode==SkillMode.LOWER).all())
        self.sensor['applied_height']-=.04;self.sensor['actual_height']-=.04
        self.tick();self.assertTrue((self.s.mode==SkillMode.HOLD).all())

    def test_crouch_requires_continuous_quiet_four_foot_stop(self):
        self.s.request_twist([.3,0,0]);self.assertTrue((self.tick()[:,0]==.3).all())
        self.s.request_crouch();self.sensor['twist'][:,0]=.1
        out=self.tick(30);self.assertTrue((self.s.mode==SkillMode.BRAKE).all());self.assertTrue((out[:,:3]==0).all());self.assertTrue((out[:,3]==self.s.cfg.nominal_height_m).all())
        self.sensor['twist'].zero_();self.sensor['contacts'][:,0]=False;self.tick(20)
        self.assertTrue((self.s.mode==SkillMode.BRAKE).all())
        self.sensor['contacts'][:]=True;self.sensor['blend'][:]=.1;self.tick(20)
        self.assertTrue((self.s.mode==SkillMode.BRAKE).all())
        self.sensor['blend'].zero_();self.tick(16);self.assertTrue((self.s.mode==SkillMode.LOWER).all())

    def test_move_from_crouch_waits_for_rise_and_settle(self):
        self.lower();self.s.request_twist([.3,0,0])
        out=self.tick();self.assertTrue((self.s.mode==SkillMode.RISE).all());self.assertTrue((out[:,:3]==0).all())
        self.tick(20);self.assertTrue((self.s.mode==SkillMode.RISE).all())
        self.sensor['applied_height'][:]=self.s.cfg.nominal_height_m;self.sensor['actual_height'][:]=self.s.cfg.nominal_height_m
        self.tick();self.assertTrue((self.s.mode==SkillMode.SETTLE).all())
        self.assertTrue((self.tick(10)[:,:3]==0).all());out=self.tick(8)
        self.assertTrue((self.s.mode==SkillMode.LOCOMOTION).all());self.assertTrue((out[:,0]==.3).all())

    def test_zero_twist_preserves_crouch_and_stand_is_explicit(self):
        self.lower();self.s.request_twist([0,0,0]);self.tick(10);self.assertTrue((self.s.mode==SkillMode.HOLD).all())
        self.s.request_stand();self.tick();self.assertTrue((self.s.mode==SkillMode.RISE).all())

    def test_fault_latches_and_freezes_height_until_reset(self):
        self.lower();self.sensor['contacts'][:,0]=False
        self.tick(5);self.assertTrue((self.s.mode!=SkillMode.FAULT).all())
        out=self.tick(7);self.assertTrue((self.s.mode==SkillMode.FAULT).all());self.assertTrue((self.s.fault==SkillFault.CONTACT_LOSS).all())
        self.assertTrue(torch.equal(out[:,3],self.sensor['applied_height']))
        self.sensor['contacts'][:]=True;self.s.request_stand();self.tick(20);self.assertTrue((self.s.mode==SkillMode.FAULT).all())
        self.s.reset();self.assertTrue((self.s.mode==SkillMode.LOCOMOTION).all())

    def test_cancel_mid_lower_is_guarded_rise_not_motion(self):
        self.s.request_crouch();self.tick(18);self.sensor['applied_height']-=.01;self.sensor['actual_height']-=.01
        self.s.request_twist([0,.2,0]);out=self.tick();self.assertTrue((self.s.mode==SkillMode.RISE).all());self.assertTrue((out[:,:3]==0).all())

    def test_timeout_and_nonfinite_fail_closed(self):
        self.s.request_crouch();self.sensor['twist'][:,0]=.1;self.tick(405)
        self.assertTrue((self.s.fault==SkillFault.TIMEOUT).all())
        self.s.reset();self.sensor['twist'][:,0]=float('nan');self.sensor['applied_height'][:]=float('nan');out=self.tick()
        self.assertTrue((self.s.fault==SkillFault.NONFINITE).all());self.assertTrue(torch.isfinite(out).all());self.assertTrue((out[:,:3]==0).all())

    def test_subset_reset_and_invalid_requests(self):
        self.s.request_crouch(ids=[0]);self.tick(18);self.assertEqual(int(self.s.mode[1]),SkillMode.LOCOMOTION)
        self.s.reset([0]);self.assertEqual(int(self.s.mode[0]),SkillMode.LOCOMOTION)
        for value in ([.5,.35,.6],[float('nan'),0,0]):
            with self.assertRaises(ValueError):self.s.request_twist(value)
        with self.assertRaises(ValueError):self.s.request_crouch(.05)
        with self.assertRaises(ValueError):self.s.tick(0.,**self.sensor)

    def test_inactive_environments_do_not_advance(self):
        self.s.request_crouch();self.s.tick(.02,active=torch.zeros(2,dtype=torch.bool),**self.sensor)
        self.assertTrue((self.s.mode_age==0).all());self.assertTrue((self.s.mode==SkillMode.LOCOMOTION).all())

if __name__=='__main__':unittest.main()

class SupportTransitionTests(unittest.TestCase):
    def test_default_allocation_is_bitwise_legacy_and_new_unloads_before_lift(self):
        from csdog_motion.support_feedback import support_weights
        phase=torch.arange(100)/100;blend=torch.linspace(0,1,100)
        local=torch.remainder(phase[:,None]+torch.tensor([0.,.5,0.,.5]),1.)
        progress=((local-.55)/.45).clamp(0,1)
        fade=(torch.minimum(progress,1-progress)/.1).clamp(0,1);fade=fade.square()*(3-2*fade)
        self.assertTrue(torch.equal(support_weights(phase,blend,.55),1-fade*blend[:,None]))
        from csdog_motion.support_transfer import TRANSITION
        old=support_weights(torch.tensor([.54,.58]),torch.ones(2),.55)
        new=support_weights(torch.tensor([.54,.58]),torch.ones(2),.55,TRANSITION)
        self.assertLess(float(new[0,0]),float(old[0,0]));self.assertEqual(float(new[1,0]),0.)
        allweights=support_weights(phase,torch.ones(100),.55,TRANSITION)
        self.assertTrue(((allweights>=0)&(allweights<=1)).all())
        self.assertGreater(float(allweights.sum(1).min()),1.99)
        self.assertTrue(torch.equal(support_weights(phase,torch.zeros(100),.55,TRANSITION),torch.ones(100,4)))


class BackwardTransferTests(unittest.TestCase):
    def test_nonbackward_and_low_commands_preserve_legacy_weights_exactly(self):
        from csdog_motion.support_feedback import support_weights,transfer_strength
        from csdog_motion.support_transfer import BACKWARD_TRANSITION
        commands=torch.tensor([[.5,0,0],[0,.3,0],[0,0,.4],[-.15,0,0],[-.4,0,0],[-.4,.3,0]])
        p=torch.full((6,),.54);b=torch.ones(6)
        old=support_weights(p,b,.55)
        new=support_weights(p,b,.55,BACKWARD_TRANSITION,commands)
        self.assertTrue(torch.equal(new[[0,1,2,3,5]],old[[0,1,2,3,5]]))
        strength=transfer_strength(commands,BACKWARD_TRANSITION)
        torch.testing.assert_close(strength,torch.tensor([0.,0.,0.,0.,1.,0.]))
        self.assertLess(float(new[4,0]),float(old[4,0]))

    def test_applied_height_alone_does_not_release_move_before_actual_rise(self):
        s=SkillSupervisor(1);h=s.cfg.nominal_height_m
        sensors=dict(twist=torch.zeros(1,3),tilt_deg=torch.zeros(1),contacts=torch.ones(1,4,dtype=torch.bool),blend=torch.zeros(1),applied_height=torch.tensor([h]),actual_height=torch.tensor([h-.008]))
        s.mode[:]=SkillMode.RISE;s.request_twist([.2,0,0])
        for _ in range(20):out=s.tick(.02,**sensors)
        self.assertEqual(int(s.mode[0]),SkillMode.RISE);self.assertEqual(float(out[0,0]),0.)
        sensors['actual_height'][:]=h-.004
        for _ in range(20):out=s.tick(.02,**sensors)
        self.assertEqual(int(s.mode[0]),SkillMode.LOCOMOTION)


class SupportRoundoffTests(unittest.TestCase):
    def test_dense_float32_support_curve_never_crosses_force_share_bounds(self):
        from csdog_motion.support_feedback import support_weights,transfer_strength
        from csdog_motion.support_transfer import BACKWARD_TRANSITION
        p=torch.linspace(0,1,100001);b=torch.ones_like(p)
        cmd=torch.zeros(len(p),3);cmd[:,0]=-.4
        w=support_weights(p,b,.55,BACKWARD_TRANSITION,cmd)
        self.assertTrue(((w>=0)&(w<=1)).all())
        cmd[:,0]=torch.linspace(-.35001,-.14999,len(p))
        strength=transfer_strength(cmd,BACKWARD_TRANSITION)
        self.assertTrue(((strength>=0)&(strength<=1)).all())
        cmd[:,0]=.4
        self.assertTrue(torch.equal(support_weights(p,b,.55,BACKWARD_TRANSITION,cmd),support_weights(p,b,.55)))
