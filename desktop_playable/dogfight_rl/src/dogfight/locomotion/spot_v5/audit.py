import json,torch,numpy as np,random
from ..spot_v4.rewards import gait_phase_eligible
from ..spot_v2.contacts import contact_state
from .config import TranslationGait,position_cost,smoothness_cost

def audit(runner,out):
 b=runner.env.unwrapped;r=b.scene['robot'];policy=runner.alg.policy
 rng=(torch.get_rng_state(),torch.cuda.get_rng_state_all(),np.random.get_state(),random.getstate())
 initial={k:v.clone() for k,v in policy.state_dict().items()};rows=[]
 # Same initial Gaussian mean and physical initialization for all four noise probes.
 for std in [.3,.4,.5,.6]:
  torch.manual_seed(42);np.random.seed(42);random.seed(42);b.reset(seed=42)
  policy.load_state_dict(initial)
  with torch.no_grad():policy.std.fill_(std)
  fall=0;heights=[];swing=[];torques=[];deltas=[];prev=None;targets=[]
  for step in range(100):
   term=b.command_manager.get_term('base_velocity');term.vel_command_b[:]=torch.tensor([.2,0.,0.],device=b.device);term.is_standing_env[:]=False;term.time_left[:]=1000.
   with torch.no_grad():action=policy.act(runner.env.get_observations());_,_,done,extra=runner.env.step(action)
   s=contact_state(b);fall+=int((done.bool()&~extra.get('time_outs',torch.zeros_like(done)).bool()).sum())
   heights.append(s.clearance.max(0).values.cpu().numpy());swing.append(float(((~s.contact)&(s.clearance>.015)).float().mean()));torques.append(float((r.data.applied_torque.abs()>=9.9).float().mean()))
   if prev is not None:deltas.append(float((action-prev).square().mean().sqrt()))
   prev=action.clone();targets.append(r.data.joint_pos_target.detach().cpu().numpy().copy())
  rows.append(dict(std=std,seconds=2,falls=fall,fall_events_per_env=fall/b.num_envs,true_swing_ratio=float(np.mean(swing)),max_clearance_per_leg=np.max(heights,axis=0).tolist(),torque_saturation=float(np.mean(torques)),raw_action_delta_rms=float(np.mean(deltas)),target_delta_rms=float(np.sqrt(np.mean(np.diff(np.stack(targets),axis=0)**2)))))
 policy.load_state_dict(initial);b.reset(seed=42)
 gate=TranslationGait(b.cfg.rewards.gait,b);gates={}
 for name,cmd in [('forward',(.2,0,0)),('backward',(-.2,0,0)),('left',(0,.2,0)),('right',(0,-.2,0)),('yaw',(0,0,.4)),('stop',(0,0,0))]:
  term=b.command_manager.get_term('base_velocity');term.vel_command_b[:]=torch.tensor(cmd,device=b.device)
  gate(b,**b.cfg.rewards.gait.params);gates[name]=float(b._gait_applicable.float().mean())
  cost=position_cost(b,translation_scale=.5);reference=position_cost(b,translation_scale=1.)
  if name in ['yaw','stop']:assert torch.equal(cost,reference)
 assert all(gates[x]==1 for x in ['forward','backward','left','right']) and gates['yaw']==0 and gates['stop']==0
 contact=torch.tensor([[1,1,1,1],[0,0,0,0],[1,0,0,1]],dtype=torch.bool)
 height=torch.tensor([[0.,0,0,0],[.03,.03,.03,.03],[0,.03,.03,0]])
 force=contact.float()*10
 assert gait_phase_eligible(contact,height,force).tolist()==[False,False,True]
 (out/'zero_update_audit.json').write_text(json.dumps(dict(noise_probes=rows,repaired_gait_applicability=gates,unit_checks='PASS',ppo_updates=0,noise_probe_limitation='Random untrained policy exploration only; not deterministic learned gait and not a std training comparison.'),indent=2))
 runner.env.samples.clear();runner.env.previous=None
 torch.set_rng_state(rng[0]);torch.cuda.set_rng_state_all(rng[1]);np.random.set_state(rng[2]);random.setstate(rng[3]);b.reset()
