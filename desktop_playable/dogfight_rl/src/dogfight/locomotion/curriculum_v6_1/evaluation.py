"""Common fixed-seed V6 protocol with optional 500Hz raw contact capture."""
from ..curriculum_v6.evaluation import summarize,CASES
from ..curriculum_v6 import evaluation as original
from ..curriculum_v6.supervisor import atomic_json
from .supervisor import SEEDS,SCORE_VERSION
import numpy as np
import torch

class SubstepRecorder:
    def __init__(self,b):
        from .contacts import physical_events
        self.b=b;self.state=physical_events(b).raw;self.rows=[];self.original=b.scene.update
        from .events import diagnostic_indices
        self.indices=diagnostic_indices(b.num_envs,CASES)
    def update(self,dt):
        self.original(dt)
        if len(self.rows)>=6100:return
        # Independent raw sampler; its timing buffers never enter rewards or acceptance.
        s=self.state;r=self.b.scene['robot'];ix=self.indices
        row=dict(command=self.b.command_manager.get_command('base_velocity')[ix],contact=s.contact[ix],force=s.force[ix],raw_force=s.raw_force[ix],shin=s.shin[ix],clearance=s.clearance[ix],foot_position=s.tip_position[ix],foot_velocity=s.tip_velocity[ix],patch_velocity=s.velocity[ix],velocity=r.data.root_lin_vel_b[ix],yaw=r.data.root_ang_vel_b[ix,2],tilt=r.data.projected_gravity_b[ix,:2],episode=self.b.episode_length_buf[ix])
        self.rows.append({k:v.detach().cpu().numpy().copy() for k,v in row.items()})
    def install(self):self.b.scene.update=self.update
    def close(self,path):
        self.b.scene.update=self.original
        if self.rows:np.savez_compressed(path,dt=.002,indices=self.indices,**{k:np.stack([r[k] for r in self.rows]) for k in self.rows[0]})

def evaluate(runner,out,full=True,tag=None,seeds_override=None,raw=False):
    recorder=SubstepRecorder(runner.env.unwrapped) if raw else None
    if recorder:recorder.install()
    saved_rollout=original.rollout;saved_summarize=original.summarize
    original.rollout=verified_rollout;original.summarize=verified_summarize
    try:
        result=original.evaluate(runner,out,full,tag,seeds_override or (SEEDS if full else None))
        result.update(score_version=SCORE_VERSION,contact_version=CONTACT_VERSION,protocol='v6.1-fixed-panel-1')
        atomic_json(out/f"evaluation_{result['id']}.json",result)
        return result
    finally:
        original.rollout=saved_rollout;original.summarize=saved_summarize
        if recorder:recorder.close(out/'physics_500hz.npz')

# Keep the V6 policy-rate trajectory and append independently measured physical events.
from ..spot_v4.evaluation import rollout as base_rollout
from .contacts import physical_events,CONTACT_VERSION

def verified_rollout(wrapped,policy,commands,seconds,seed,writer=None,title=''):
    verifier=physical_events(wrapped.unwrapped);records=[];step=wrapped.step
    def measured(actions):
        verifier.begin_control()
        result=step(actions)
        records.append({k:v.detach().cpu().numpy().copy() for k,v in verifier.snapshot().items()})
        return result
    wrapped.step=measured
    try:d=base_rollout(wrapped,policy,commands,seconds,seed,writer,title)
    finally:wrapped.step=step
    d.update({k:np.stack([r[k] for r in records]) for k in records[0]})
    return d

def verified_summarize(d,ix,name,t):
    result=summarize(d,ix,name,t)
    c=d['command'][:,ix];changes=np.any(np.diff(c,axis=0)!=0,axis=(1,2));age=np.zeros(len(c));age[0]=.02
    for k in range(1,len(c)):age[k]=.02 if changes[k-1] else age[k-1]+.02
    valid=d['valid'][:,ix]&(age[:,None]>.6);moving=np.linalg.norm(c,axis=-1)>.04
    for r in result:
        if not r['valid']:continue
        mask=valid&(~moving if r['is_stop'] else moving)
        ticks=d['physics_event_ticks'][:,ix]
        duration=ticks*.002
        # The entire segment must lie in the stable, alive phase; no gap merging.
        events=(ticks>=round(t['swing_duration']/.002))&(ticks<=300)&mask[:,:,None]&(age[:,None,None]>=.6+duration)
        r['policy_periodic_legs']=r['periodic_legs'];r['policy_gait_trial_fraction']=r['gait_trial_fraction']
        r['periodic_legs']=0;qualified=np.ones(len(ix),dtype=bool)
        contact_switches=d['physics_contact_switches'][:,ix]
        for j,leg in enumerate(['LF','RF','LR','RR']):
            switches=(contact_switches[:,:,j]*mask).sum(0)
            ok=(events[:,:,j].sum(0)>=2)&(switches>=4)
            qualified&=ok
            if ok.mean()>=t['trial_pass_fraction']:r['periodic_legs']+=1
            ratio=float((d['physics_strict_ticks'][:,ix,j]/10.)[mask].mean())
            r['feet'][leg]['policy_swing_ratio']=r[leg+'_swing_ratio']
            r[leg+'_swing_ratio']=ratio
            r['feet'][leg]['verified_swing_durations_s']=duration[:,:,j][events[:,:,j]].tolist()
            r['feet'][leg]['verified_contact_switches']=switches.tolist()
            r['feet'][leg]['verified_trial_fraction']=float(ok.mean())
        r['gait_trial_fraction']=float(qualified.mean())
        r['policy_support_slip_speed']=r['support_slip_speed']
        support=d['physics_support_n'][:,ix]*mask[:,:,None]
        r['support_slip_speed']=float((d['physics_slip_sum'][:,ix]*mask[:,:,None]).sum()/max(1,support.sum()))
        r['contact_version']=CONTACT_VERSION
    return result
