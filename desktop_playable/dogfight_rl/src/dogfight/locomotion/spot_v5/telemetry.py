"""Read-only mini-batch hooks around native RSL PPO. No probability/update changes."""
import torch,json,time
from ..spot_v4.runner import Runner as V4Runner,Wrapper as V4Wrapper,GracefulStop

class Wrapper(V4Wrapper):
 def step(self,actions):
  result=super().step(actions);e=self.unwrapped;c=e.command_manager.get_command('base_velocity');r=e.scene['robot']
  xy=c[:,:2].norm(dim=-1);yaw=c[:,2].abs();eps=1e-6
  masks=[(xy<eps)&(yaw<eps),(c[:,0]>eps)&(c[:,1].abs()<eps)&(yaw<eps),(c[:,0]<-eps)&(c[:,1].abs()<eps)&(yaw<eps),(c[:,1]>eps)&(c[:,0].abs()<eps)&(yaw<eps),(c[:,1]<-eps)&(c[:,0].abs()<eps)&(yaw<eps),(xy<eps)&(c[:,2]>eps),(xy<eps)&(c[:,2]<-eps),(c[:,0].abs()>eps)&(c[:,1].abs()>eps)&(yaw<eps)]
  for name,mask in zip(['stop','forward','backward','left','right','yaw_positive','yaw_negative','diagonal'],masks):self.samples[-1]['command_'+name]=float(mask.float().mean())
  self.samples[-1]['command_mixed']=float((~torch.stack(masks).any(0)).float().mean())
  limits=r.data.soft_joint_pos_limits
  self.samples[-1]['target_limit_fraction']=float(((r.data.joint_pos_target<limits[:,:,0])|(r.data.joint_pos_target>limits[:,:,1])).float().mean())
  self.samples[-1]['tilt']=float(r.data.projected_gravity_b[:,:2].norm(dim=-1).mean())
  return result

class Runner(V4Runner):
 def __init__(self,*a,ledger,**kw):
  self.ledger=ledger;self.batches=[];super().__init__(*a,**kw)
  alg=self.alg;storage=alg.storage;generator=storage.mini_batch_generator;logprob=alg.policy.get_actions_log_prob
  def batches(*args,**kwargs):
   for batch in generator(*args,**kwargs):
    self.pending=batch
    yield batch
   self.pending=None
  storage.mini_batch_generator=batches;self.pending=None
  def measured_logprob(actions):
   value=logprob(actions)
   if self.pending is not None:
    old_log=self.pending[5].squeeze();mu0=self.pending[6];s0=self.pending[7]
    with torch.no_grad():
     mu=alg.policy.action_mean;s=alg.policy.action_std
     kl=(torch.log(s/s0+1e-5)+(s0.square()+(mu0-mu).square())/(2*s.square())-.5).sum(-1)
     ratio=(value-old_log).exp()
     self.batches.append(dict(kl=float(kl.mean()),kl_max=float(kl.max()),mean_shift_kl=float(((mu0-mu).square()/(2*s.square())).sum(-1).mean()),variance_kl=float((torch.log(s/s0+1e-5)+s0.square()/(2*s.square())-.5).sum(-1).mean()),std_delta_rms=float((s-s0).square().mean().sqrt()),ratio_mean=float(ratio.mean()),ratio_min=float(ratio.min()),ratio_max=float(ratio.max()),clip_fraction=float(((ratio<.8)|(ratio>1.2)).float().mean()),lr_before_adaptation=alg.learning_rate))
   return value
  alg.policy.get_actions_log_prob=measured_logprob
  def pre(optimizer,args,kwargs):
   def norm(module):return float(torch.stack([p.grad.square().sum() for p in module.parameters() if p.grad is not None]).sum().sqrt())
   if self.batches:self.batches[-1].update(actor_gradient_norm_clipped=norm(alg.policy.actor),critic_gradient_norm_clipped=norm(alg.policy.critic),lr_used=alg.learning_rate)
  alg.optimizer.register_step_pre_hook(pre)
  # Backward hooks observe raw gradients before the native global clipping.
  self.raw_grad={}
  for name,p in alg.policy.named_parameters():
   p.register_hook(lambda g,n=name:self.raw_grad.__setitem__(n,float(g.detach().square().sum())) or None)
  def post(optimizer,args,kwargs):
   if self.batches:
    self.batches[-1].update(actor_gradient_norm_raw=sum(v for k,v in self.raw_grad.items() if k.startswith('actor.'))**.5,critic_gradient_norm_raw=sum(v for k,v in self.raw_grad.items() if k.startswith('critic.'))**.5)
  alg.optimizer.register_step_post_hook(post)
  original=alg.update
  def update():
   data=json.loads(self.ledger.read_text())
   if data['updates']>=1500 or data['seconds']>=3600:raise GracefulStop('Global budget exhausted')
   self.before={k:v.detach().clone() for k,v in alg.policy.named_parameters()}
   return original()
  alg.update=update
 def log(self,locs,*a,**kw):
  # Count completed updates BEFORE any logging that might fail.
  data=json.loads(self.ledger.read_text());data['updates']+=1;data['seconds']+=locs['collection_time']+locs['learn_time'];data['environment_steps']+=self.num_steps_per_env*self.env.num_envs
  self.ledger.write_text(json.dumps(data,indent=2))
  batch=self.batches
  with (self.output/'minibatches.jsonl').open('a') as f:
   for i,row in enumerate(batch):f.write(json.dumps(dict(update=self.total_updates+1,minibatch=i,**row))+'\n')
  extras={k:sum(x[k] for x in batch)/len(batch) for k in batch[0]} if batch else {}
  extras['kl_peak']=max((x['kl'] for x in batch),default=0.)
  for label in ['actor','critic']:
   extras[label+'_parameter_delta_l2']=float(torch.stack([(p-self.before[n]).square().sum() for n,p in self.alg.policy.named_parameters() if n.startswith(label+'.')]).sum().sqrt())
  locs['loss_dict']=dict(locs['loss_dict'],**extras)
  self.batches=[]
  samples=self.env.samples
  severe=(sum(x['falls'] for x in samples)>self.env.num_envs*.8 or sum(x['target_limit_fraction'] for x in samples)/len(samples)>.5 or sum(x['tilt'] for x in samples)/len(samples)>.8 or sum(x['action_delta_sq'] for x in samples)/len(samples)>4.)
  self.bad_count=getattr(self,'bad_count',0)+1 if severe else 0
  self.bad_ppo=getattr(self,'bad_ppo',0)+1 if extras.get('kl',0)>.3 or extras.get('clip_fraction',0)>.8 else 0
  if severe or self.bad_ppo:
   with (self.output/'alerts.jsonl').open('a') as f:f.write(json.dumps(dict(update=self.total_updates+1,severe_physics=severe,bad_ppo=self.bad_ppo))+'\n')
  if self.bad_count>=5:self.stop_requested='persistent_severe_physics'
  if self.bad_ppo>=5:self.stop_requested='persistent_excessive_policy_update'
  if (data['updates']>=1500 or data['seconds']>=3600) and self.session_updates+1<self.requested:self.stop_requested='global_budget'
  super().log(locs,*a,**kw)
