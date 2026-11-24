import copy
from pathlib import Path
import sys
import unittest
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"source/stackforce_simready_generated_robot_lab"))
from csdog_motion.residual_learning import learning_contract,full_learning_contract,learning_profile,low_command_cases,holdout_cases,reward_terms,REWARD_SCALES
from csdog_motion.evaluation import profile_at
from csdog_motion.reference_control import reference_contract


class ResidualTests(unittest.TestCase):
    def test_contract_is_distinct_and_exposes_contact_and_clearance(self):
        value=learning_contract()
        self.assertNotEqual(value["compatibility_tag"],reference_contract()["compatibility_tag"])
        self.assertEqual(value["observations"],74)
        self.assertEqual(value["observation_layout"]["foot_clearance_over_0_05m"],[70,74])
        self.assertIn("velocity_target",value["action"])
        self.assertEqual(value["action"]["residual_scale_rad"],.12)

    def test_full_transfer_changes_sampling_but_preserves_control_semantics(self):
        low=learning_contract();full=full_learning_contract()
        self.assertNotEqual(low["compatibility_tag"],full["compatibility_tag"])
        self.assertEqual(full["training_replay"]["low_command_probability"],.4)
        for value in (low,full):
            for key in ("schema_version","compatibility_tag","training_command_ranges","training_replay"):value.pop(key,None)
        self.assertEqual(low,full)

    def test_development_commands_are_explicitly_low_not_full_protocol(self):
        cases=low_command_cases()
        self.assertEqual(len(cases),18)
        for case in cases:
            for _,command in case["profile"]:
                self.assertLessEqual(abs(command[0]),.15+1e-9)
                self.assertLessEqual(abs(command[1]),.1+1e-9)
                self.assertLessEqual(abs(command[2]),.15+1e-9)
        self.assertEqual(next(c for c in cases if c["name"]=="left_low")["profile"][0][1],[0.,1/30,0.])

    def test_holdout_points_and_transition_times_differ_from_selection(self):
        selected={c["name"]:c for c in low_command_cases()}
        cases=holdout_cases()
        self.assertEqual(len(cases),18)
        self.assertEqual(len({c["name"] for c in cases}),18)
        for case in cases:
            if case["name"]!="stand":self.assertNotEqual(case["profile"],selected[case["name"]]["profile"])
            for end,_ in case["profile"]:
                command,_=profile_at(case["profile"],end-.001)
                self.assertTrue(all(abs(v)<=limit+1e-9 for v,limit in zip(command,[.15,.1,.15])))

    def state(self):
        z=lambda *shape:torch.zeros(*shape)
        return dict(twist=z(2,3),command=z(2,3),stance=torch.ones(2,4,dtype=torch.bool),blend=z(2),
            foot_body=z(2,4,3),reference_foot=z(2,4,3),contacts=torch.ones(2,4,dtype=torch.bool),
            clearance=z(2,4),desired_clearance=z(2,4),force_over_weight=z(2,4),height=z(2),height_command=z(2),
            gravity=torch.tensor([[0.,0.,-1.]]*2),angular_xy=z(2,2),vertical_velocity=z(2),
            foot_world_velocity=z(2,4,3),torque=z(2,12),joint_acceleration=z(2,12),target=z(2,12),
            previous_target=z(2,12),residual=z(2,12),raw_action=z(2,12),target_box_clip=torch.zeros(2,12,dtype=torch.bool),terminated=torch.zeros(2,dtype=torch.bool))

    def test_reward_penalizes_physical_target_change_even_at_zero_policy_output(self):
        state=self.state();before=reward_terms(state)
        state["target"][:]=.08
        after=reward_terms(state)
        self.assertTrue(torch.all(after["total_target_change"]>before["total_target_change"]))
        self.assertTrue(torch.all(after["residual_size"]==0))
        self.assertEqual(set(after),set(REWARD_SCALES))

    def test_swing_load_and_failed_axis_cannot_be_hidden_by_other_axes(self):
        state=self.state();perfect=reward_terms(state)
        state["twist"][:,1]=.2
        changed=reward_terms(state)
        self.assertTrue(torch.all(changed["track_y"]<perfect["track_y"]))
        torch.testing.assert_close(changed["track_x"],perfect["track_x"])
        state["blend"][:]=1;state["stance"][:]=False;state["force_over_weight"][:]=.25
        self.assertTrue(torch.all(reward_terms(state)["swing_load"]>0))


if __name__=="__main__":unittest.main()
