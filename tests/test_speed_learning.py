import copy
import itertools
from pathlib import Path
import sys
import unittest
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source/stackforce_simready_generated_robot_lab'))
from csdog_motion.speed_learning import valid_speed_request,speed_cases,speed_learning_contract
from csdog_motion.residual_learning import full_learning_contract,learning_profile
from csdog_motion.trajectory import LegKinematics,TrajectoryConfig,foot_reference
from csdog_motion.calibration import ASSET

class SpeedTests(unittest.TestCase):
    def test_domain_preserves_legacy_corners_but_rejects_unchecked_extensions(self):
        corners=torch.tensor(list(itertools.product((-.4,.4),(-.3,.3),(-.4,.4))))
        self.assertTrue(valid_speed_request(corners).all())
        self.assertTrue(valid_speed_request(torch.tensor([[.5,0.,0.],[0.,-.35,0.],[0.,0.,.6]])).all())
        self.assertFalse(valid_speed_request(torch.tensor([[.5,.35,.6],[.51,0.,0.],[float('nan'),0.,0.]])).any())
        for case in speed_cases():
            self.assertTrue(valid_speed_request(torch.tensor([row[1] for row in case['profile']])).all())

    def test_transfer_preserves_every_control_observation_field(self):
        old=full_learning_contract();new=speed_learning_contract()
        for contract in (old,new):
            for key in ('schema_version','compatibility_tag','training_command_ranges','training_replay','command_envelope'):contract.pop(key,None)
        self.assertEqual(old,new)

    def test_style_changes_only_declared_learning_terms(self):
        from csdog_motion.speed_learning import style_learning_contract,style_reward_scales
        from csdog_motion.residual_learning import REWARD_SCALES
        new=style_reward_scales()
        self.assertEqual({k for k in new if new[k]!=REWARD_SCALES[k]},{'foot_reference','contact_schedule','swing_load'})
        old=speed_learning_contract();new=style_learning_contract()
        for value in (old,new):
            for key in ('schema_version','compatibility_tag','learning_reward_scales'):value.pop(key,None)
        self.assertEqual(old,new)

    def test_adaptive_lift_keeps_phase_pairing_and_stand_and_reserves_combined_range(self):
        from csdog_motion.clean_gait import clean_foot_reference,extra_clearance
        d=learning_profile();nom=torch.tensor([d['nominal_sole_positions_body_m'][l] for l in ('lr','lf','rf','rr')],dtype=torch.float64)
        cfg=TrajectoryConfig(**d['trajectory']);p=torch.tensor([.775,.775],dtype=torch.float64)
        cmd=torch.tensor([[.5,0,0],[.4,.3,.4]],dtype=torch.float64)
        old,oldmask=foot_reference(p,cmd,nom,cfg)
        new,newmask=clean_foot_reference(p,cmd,nom,cfg)
        self.assertTrue(torch.equal(oldmask,newmask))
        self.assertAlmostEqual(float(new[0,0,2]-old[0,0,2]),.007)
        torch.testing.assert_close(new[1],old[1])
        stand,_=clean_foot_reference(p,cmd,nom,cfg,blend=torch.zeros_like(p))
        torch.testing.assert_close(stand,nom[None].expand(2,-1,-1))

    def test_adaptive_lift_has_zero_boundary_velocity_and_acceleration(self):
        from csdog_motion.clean_gait import clean_foot_reference
        cfg=TrajectoryConfig(.5,.55,.025);nom=torch.tensor([[-.24,.14,-.35],[.24,.14,-.35],[.24,-.14,-.35],[-.24,-.14,-.35]],dtype=torch.float64)
        for boundary in (.55,1.):
            p=torch.tensor([boundary-1e-5,boundary,boundary+1e-5],dtype=torch.float64)
            cmd=torch.tensor([[.5,0.,0.]]*3,dtype=torch.float64)
            foot,_=clean_foot_reference(p,cmd,nom,cfg)
            z=foot[:,0,2]
            self.assertLess(abs(float((z[2]-z[0])/(2e-5*cfg.period_s))),1e-5)
            self.assertLess(abs(float((z[2]-2*z[1]+z[0])/(1e-5*cfg.period_s)**2)),.01)

    def test_height_reference_really_changes_body_relative_foot_targets(self):
        d=learning_profile();nom=torch.tensor([d['nominal_sole_positions_body_m'][l] for l in ('lr','lf','rf','rr')],dtype=torch.float64)
        target,stance=foot_reference(torch.zeros(2,dtype=torch.float64),torch.zeros(2,3,dtype=torch.float64),nom,
            TrajectoryConfig(**d['trajectory']),blend=torch.zeros(2,dtype=torch.float64),height_delta=torch.tensor([0.,-.04],dtype=torch.float64))
        torch.testing.assert_close(target[1,:,2]-target[0,:,2],torch.full((4,),.04,dtype=torch.float64))
        model=LegKinematics(ASSET/'robot_sim.urdf',d['nominal_joint_positions_rad'],offset_bound=.5,dtype=torch.float64)
        q,error=model.solve(target,iterations=30)
        self.assertLess(float(error.max()),1e-6)
        self.assertGreater(float(torch.minimum(q-model.lower,model.upper-q).min()),.12)

if __name__=='__main__':unittest.main()
