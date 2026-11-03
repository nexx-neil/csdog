"""V6.1 deterministic panel augmented with full-stride measurements for all trials."""
from pathlib import Path
import numpy as np
import torch
from .stride import observe
from ..curriculum_v6_1 import evaluation as legacy
from ..curriculum_v6_1.supervisor import atomic_json
from .evaluation_version import VERSION

def evaluate(runner,out,full=True,tag='common',seeds=None,raw=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    b=runner.env.unwrapped;o=observe(b);saved_rollout=legacy.verified_rollout;saved_summary=legacy.verified_summarize
    def rollout(wrapped,policy,commands,seconds,seed,writer=None,title=''):
        records=[];physical=[];step=wrapped.step;scene=b.scene.update;active=False
        from ..curriculum_v6_1.events import diagnostic_indices
        ix=diagnostic_indices(b.num_envs,legacy.CASES)
        def physics(dt):
            scene(dt)
            if raw and active:
                s=o.physical.raw;r=b.scene['robot']
                fields=dict(contact=s.contact,clearance=s.clearance,force=s.force,raw_force=s.raw_force,shin=s.shin,foot_position=s.tip_position,foot_velocity=s.tip_velocity,patch_velocity=s.velocity,root_position=r.data.root_pos_w,root_quaternion=r.data.root_quat_w,root_velocity=r.data.root_lin_vel_b,root_angular_velocity=r.data.root_ang_vel_b,joint_position=r.data.joint_pos,joint_target=r.data.joint_pos_target,command=b.command_manager.get_command('base_velocity'),episode=b.episode_length_buf)
                physical.append({k:v[ix].detach().cpu().numpy().copy() for k,v in fields.items()})
        def measured(action):
            nonlocal active
            o.begin_control();active=True
            try:result=step(action)
            finally:active=False
            records.append({k:v.detach().cpu().numpy().copy() for k,v in o.snapshot().items()});return result
        wrapped.step=measured;b.scene.update=physics
        try:d=saved_rollout(wrapped,policy,commands,seconds,seed,writer,title)
        finally:wrapped.step=step;b.scene.update=scene
        d.update({k:np.stack([r[k] for r in records]) for k in records[0]})
        if physical:np.savez_compressed(out/f'physics_seed{seed}.npz',dt=b.physics_dt,indices=ix,**{k:np.stack([r[k] for r in physical]) for k in physical[0]})
        return d
    def summarize(d,ix,name,t):
        rows=saved_summary(d,ix,name,t)
        c=d['command'][:,ix];change=np.any(np.diff(c,axis=0)!=0,axis=(1,2));age=np.zeros(len(c));age[0]=.02
        for k in range(1,len(c)):age[k]=.02 if change[k-1] else age[k-1]+.02
        for r in rows:
            moving=np.linalg.norm(c,axis=-1)>.04
            # Whole sequence must start after settling; max .6s flight + .06 stance + .04 support.
            mask=d['valid'][:,ix]&(age[:,None]>1.3)&(~moving if r['is_stop'] else moving)
            for src,dst in [('stride_count','complete_stride_count'),('touchdown_count','valid_touchdown_count'),('stable_time','stable_stance_duration'),('lift_count','liftoff_count'),('swing_count','valid_swing_count')]:
                values=(d[src][:,ix]*mask[:,:,None]).sum(0)
                r[dst]=values.sum(0).tolist();r[dst+'_per_trial']=values.tolist()
            counts=np.asarray(r['complete_stride_count_per_trial'])
            r['complete_stride_ratio']=float((counts>=2).all(-1).mean())
            r['complete_stride_legs']=int(((counts>=2).mean(0)>=t['trial_pass_fraction']).sum())
            r['support_foot_slip']=r['support_slip_speed'];r['stop_linear_speed']=r['speed_xy'] if r['is_stop'] else None
            r['stop_yaw_rate']=r.get('yaw_abs') if r['is_stop'] else None
            r['forward_tracking_error']=float(np.abs(d['velocity'][:,ix,0]-c[:,:,0])[mask].mean()) if mask.any() else 1.
            r['stride_protocol']=VERSION
        return rows
    legacy.verified_rollout=rollout;legacy.verified_summarize=summarize
    try:
        result=legacy.evaluate(runner,out,full=full,tag=tag,seeds_override=seeds,raw=False)
        result['stride_protocol']=VERSION;result['protocol']=VERSION
        atomic_json(out/f'evaluation_{tag}.json',result);atomic_json(out/'summary.json',brief(result));return result
    finally:
        legacy.verified_rollout=saved_rollout;legacy.verified_summarize=saved_summary
        # The legacy evaluator deliberately wraps deterministic rollouts in
        # inference_mode. Convert recurrence buffers back before PPO resumes.
        o.state.normalize_storage()

def brief(panel):
    f=[r for r in panel['rows'] if r['test']=='forward'];s=[r for r in panel['rows'] if r['test']=='stop']
    avg=lambda rows,key:float(np.mean([r[key] for r in rows]))
    return dict(vx=avg(f,'velocity') if False else float(np.mean([r['velocity'][0] for r in f])),support_foot_slip=avg(f,'support_slip_speed'),complete_stride_ratio=avg(f,'complete_stride_ratio'),complete_stride_count=np.sum([r['complete_stride_count'] for r in f],axis=0).tolist(),valid_touchdown_count=np.sum([r['valid_touchdown_count'] for r in f],axis=0).tolist(),stable_stance_duration=np.sum([r['stable_stance_duration'] for r in f],axis=0).tolist(),legacy_gait_fraction=avg(f,'gait_trial_fraction'),stop_linear_speed=avg(s,'speed_xy'),stop_yaw_rate=avg(s,'yaw_abs'),fall_rate=max(r['fall_rate'] for r in f+s),action_delta_rms=avg(f,'action_delta_rms'))

def video(runner,path,title):
    import imageio.v2 as imageio
    from PIL import Image,ImageDraw
    from ..spot_v4.evaluation import rollout
    b=runner.env.unwrapped;o=observe(b);counts=torch.zeros((b.num_envs,4),device=b.device);step=runner.env.step
    def measured(a):
        o.begin_control();r=step(a);counts.add_(o.state.stride_count);return r
    class Overlay:
        def __init__(self,w):self.w=w
        def append_data(self,frame):
            im=Image.fromarray(frame);d=ImageDraw.Draw(im);d.rectangle((0,70,960,115),fill=(12,12,12))
            d.text((10,73),'clearance mm '+str([round(v*1000,1) for v in o.physical.raw.clearance[0].tolist()]),fill='white')
            d.text((10,94),'complete stride LF RF LR RR '+str(counts[0].int().tolist()),fill='white');self.w.append_data(np.asarray(im))
    commands=torch.zeros(b.num_envs,3,device=b.device);commands[:,0]=.25
    runner.env.step=measured
    try:
        with imageio.get_writer(path,fps=25) as w:
            with torch.inference_mode():rollout(runner.env,runner.get_inference_policy(),commands,12.,103,writer=Overlay(w),title=title)
    finally:runner.env.step=step
