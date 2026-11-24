import sys
from pathlib import Path
import unittest
import tempfile
import xml.etree.ElementTree as ET
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "source/stackforce_simready_generated_robot_lab"))
sys.path.insert(0, str(ROOT / "scripts"))
from csdog_motion.trajectory import LegKinematics, TrajectoryConfig, body_flow, foot_reference
from csdog_motion.calibration import ASSET, calibrated_data
from csdog_motion.contracts import JOINT_NAMES
from audit_motion_mechanics import Leg
from audit_reference_support import body_com
from csdog_motion.reference_control import reference_data, reference_contract, REFERENCE_TAG
from csdog_motion.calibration import posture_contract
from csdog_motion.support_feedback import support_forces


class TrajectoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)
        data = calibrated_data()
        cls.q0 = [data["standing_joint_angles"][name] for name in JOINT_NAMES]
        cls.model = LegKinematics(ASSET / "robot_sim.urdf", cls.q0, dtype=torch.float64)
        cls.nominal = torch.tensor([data["nominal_sole_positions_body_m"][name] for name in ("lr","lf","rf","rr")], dtype=torch.float64)

    def test_fk_and_jacobian_against_independent_scipy_chain(self):
        tree = ET.parse(ASSET / "robot_sim.urdf").getroot()
        q = self.model.nominal_q + torch.tensor(np.random.default_rng(91).uniform(-.25,.25,(20,4,3)))
        position, jac = self.model.fk(q)
        for i in range(len(q)):
            for j, name in enumerate(("lr","lf","rf","rr")):
                p, independent_jac, _ = Leg(tree,name).evaluate(q[i,j].numpy())
                np.testing.assert_allclose(position[i,j], p, atol=1e-12)
                np.testing.assert_allclose(jac[i,j], independent_jac, atol=1e-12)

    def test_ik_known_reachable_points_and_hard_bound(self):
        q = self.model.nominal_q + torch.tensor(np.random.default_rng(7).uniform(-.15,.15,(30,4,3)))
        target, _ = self.model.fk(q)
        solved, error = self.model.solve(target, iterations=18)
        self.assertLess(float(error.max()), 1e-6)
        impossible = target + 2
        bounded, _ = self.model.solve(impossible)
        self.assertTrue(torch.all(bounded >= self.model.lower))
        self.assertTrue(torch.all(bounded <= self.model.upper))

    def test_body_flow_composition_and_stationary_foot_velocity(self):
        twist = torch.tensor([[.3,-.2,.4],[.3,.2,0]], dtype=torch.float64)
        xy = self.nominal[None,:,:2].expand(2,-1,-1)
        t = torch.full((2,4), .13, dtype=torch.float64)
        torch.testing.assert_close(body_flow(body_flow(xy,twist,t),twist,t),body_flow(xy,twist,2*t))
        epsilon = 1e-6
        velocity = (body_flow(xy,twist,t+epsilon)-body_flow(xy,twist,t-epsilon))/(2*epsilon)
        current = body_flow(xy,twist,t)
        expected = -twist[:,None,:2] - twist[:,2:3,None]*torch.stack((-current[...,1],current[...,0]),dim=-1)
        torch.testing.assert_close(velocity,expected,atol=1e-10,rtol=1e-8)

    def test_periodic_c2_contact_boundaries(self):
        cfg = TrajectoryConfig()
        twist = torch.tensor([[.4,.3,.4]], dtype=torch.float64)
        def at(phase):
            return foot_reference(torch.tensor([phase],dtype=torch.float64),twist,self.nominal,cfg)[0]
        torch.testing.assert_close(at(0),at(1),atol=1e-12,rtol=0)
        eps=1e-4
        for boundary in (0.,.1,.5,.6):
            left_v=(at(boundary)-at(boundary-eps))/(eps*cfg.period_s)
            right_v=(at(boundary+eps)-at(boundary))/(eps*cfg.period_s)
            self.assertLess(float((left_v-right_v).abs().max()),.004)
            left_a=(at(boundary)-2*at(boundary-eps)+at(boundary-2*eps))/(eps*cfg.period_s)**2
            right_a=(at(boundary+2*eps)-2*at(boundary+eps)+at(boundary))/(eps*cfg.period_s)**2
            self.assertLess(float((left_a-right_a).abs().max()),.15)

    def test_stand_blend_and_support_schedule(self):
        phase=torch.arange(200,dtype=torch.float64)/200
        twist=torch.tensor([[.3,.1,.2]],dtype=torch.float64).expand(200,-1)
        target,contact=foot_reference(phase,twist,self.nominal,blend=torch.zeros(200,dtype=torch.float64))
        torch.testing.assert_close(target,self.nominal[None].expand(200,-1,-1))
        self.assertGreaterEqual(int(contact.sum(1).min()),2)
        self.assertTrue(torch.equal(contact[:,0],contact[:,2]))
        self.assertTrue(torch.equal(contact[:,1],contact[:,3]))
        self.assertAlmostEqual(float(contact.double().mean()),.6,places=2)

    def test_reference_contract_and_nominal_pose_are_distinct_and_consistent(self):
        data=reference_data();contract=reference_contract()
        self.assertEqual(contract["compatibility_tag"],REFERENCE_TAG)
        self.assertNotEqual(contract["compatibility_tag"],posture_contract()["compatibility_tag"])
        self.assertEqual(contract["observations"],66)
        self.assertEqual(contract["observation_layout"]["reference_joint_offset"],[54,66])
        model=LegKinematics(ASSET/"robot_sim.urdf",data["nominal_joint_positions_rad"],offset_bound=.5,dtype=torch.float64)
        feet,_=model.fk(model.nominal_q[None])
        target=torch.tensor([data["nominal_sole_positions_body_m"][leg] for leg in ("lr","lf","rf","rr")],dtype=torch.float64)
        torch.testing.assert_close(feet[0],target,atol=1e-6,rtol=0)

    def test_reference_contract_rejects_geometry_or_nominal_corruption(self):
        for key,value in (("geometry_sha256","unexpected"),("nominal_joint_positions_rad",[float("nan")]*12)):
            data=reference_data();data[key]=value
            with self.assertRaises(ValueError):reference_contract(data)

    def test_independent_random_command_phase_reachability(self):
        data=reference_data()
        model=LegKinematics(ASSET/"robot_sim.urdf",data["nominal_joint_positions_rad"],offset_bound=.5,dtype=torch.float64)
        rng=np.random.default_rng(713)
        twist=torch.tensor(rng.uniform([-0.4,-.3,-.4],[.4,.3,.4],(256,3)),dtype=torch.float64)
        phase=torch.tensor(rng.uniform(0,1,256),dtype=torch.float64)
        nominal=torch.tensor([data["nominal_sole_positions_body_m"][leg] for leg in ("lr","lf","rf","rr")],dtype=torch.float64)
        target,_=foot_reference(phase,twist,nominal,TrajectoryConfig(**data["trajectory"]))
        q,error=model.solve(target,iterations=20)
        self.assertLess(float(error.max()),.001)
        self.assertGreater(float(torch.minimum(q-model.lower,model.upper-q).min()),.05)

    def test_urdf_com_respects_link_mass_weighted_offset(self):
        path=ASSET/"robot_sim.urdf";data=reference_data()
        mass,com=body_com(path,data["nominal_joint_positions_rad"])
        tree=ET.parse(path);base=tree.find("link[@name='base']/inertial")
        base_mass=float(base.find("mass").get("value"))
        origin=base.find("origin");position=np.fromstring(origin.get("xyz"),sep=" ")
        position[0]+=.1;origin.set("xyz"," ".join(map(str,position)))
        with tempfile.TemporaryDirectory() as folder:
            changed=Path(folder)/"robot.urdf";tree.write(changed)
            new_mass,new_com=body_com(changed,data["nominal_joint_positions_rad"])
        self.assertAlmostEqual(new_mass,mass)
        np.testing.assert_allclose(new_com-com,[.1*base_mass/mass,0,0],atol=1e-12)

    def test_static_support_torque_matches_potential_gradient(self):
        model=self.model;q=model.nominal_q[None].clone()
        gravity=torch.tensor([[0.,0.,-9.81]],dtype=torch.float64)
        forces=torch.zeros(1,4,3,dtype=torch.float64)
        torque=model.static_support_torque(q,forces,gravity)
        # Whole-body gravitational potential from an independent SciPy FK.
        path=ASSET/"robot_sim.urdf"
        def energy(value):
            mass,com=body_com(path,value.flatten().tolist())
            return mass*com[2]*9.81
        epsilon=1e-6
        for leg in range(4):
            for joint in range(3):
                plus=q.clone();minus=q.clone();plus[0,leg,joint]+=epsilon;minus[0,leg,joint]-=epsilon
                gradient=(energy(plus)-energy(minus))/(2*epsilon)
                self.assertAlmostEqual(float(torque[0,leg,joint]),gradient,places=7)
        forces[:,:,2]=20
        _,jac=model.fk(q)
        loaded=model.static_support_torque(q,forces,gravity)
        torch.testing.assert_close(loaded-torque,-(jac.transpose(-1,-2)@forces[...,None]).squeeze(-1))

    def test_support_force_balance_nonnegative_and_friction_bound(self):
        foot=self.nominal[None].expand(2,-1,-1)
        com=torch.tensor([.041,0.,-.07],dtype=torch.float64)
        p={"mass_kg":7.6,"velocity_gain_s_inv":2.,"height_gain_s_inv2":80.,"height_damping_s_inv":15.,"attitude_gain_nm_rad":8.,"attitude_damping_nm_s_rad":.8}
        z=torch.zeros(2,3,dtype=torch.float64)
        forces=support_forces(foot,com,torch.tensor([[1.,1.,1.,1.],[1.,0.,1.,0.]],dtype=torch.float64),
            torch.tensor([[0.,0.,-9.81]]*2,dtype=torch.float64),z,z,z,torch.zeros(2,dtype=torch.float64),p)
        self.assertTrue(torch.all(forces[:,:,2]>=0))
        torch.testing.assert_close(forces[:,:,2].sum(1),torch.full((2,),7.6*9.81,dtype=torch.float64))
        self.assertTrue(torch.all(torch.linalg.vector_norm(forces[:,:,:2],dim=-1)<=.5*forces[:,:,2]+1e-9))

    def test_yaw_distribution_has_zero_net_xy_force_and_requested_moment(self):
        foot=self.nominal[None]
        com=torch.tensor([.041,0.,-.07],dtype=torch.float64)
        p={"mass_kg":7.6,"velocity_gain_s_inv":2.,"height_gain_s_inv2":80.,"height_damping_s_inv":15.,"attitude_gain_nm_rad":8.,"attitude_damping_nm_s_rad":.8,"yaw_gain_nm_s_rad":2.}
        z=torch.zeros(1,3,dtype=torch.float64);request=z.clone();request[:,2]=.4
        force=support_forces(foot,com,torch.ones(1,4,dtype=torch.float64),torch.tensor([[0.,0.,-9.81]],dtype=torch.float64),z,z,request,torch.zeros(1,dtype=torch.float64),p)
        torch.testing.assert_close(force[:,:,:2].sum(1),torch.zeros(1,2,dtype=torch.float64),atol=1e-12,rtol=0)
        torque=torch.cross(foot-com,force,dim=-1).sum(1)
        self.assertAlmostEqual(float(torque[0,2]),.8,places=10)


if __name__ == "__main__":
    unittest.main()
