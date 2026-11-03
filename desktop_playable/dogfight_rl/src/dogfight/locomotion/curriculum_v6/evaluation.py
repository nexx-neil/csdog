"""Deterministic actor evaluation, signed per-skill metrics and strict physical swing tests."""
import json,random
import numpy as np
import torch
from ..spot_v4.evaluation import rollout,durations
from .supervisor import LEGS,atomic_json

CASES=[('stop',[(0,0)]),('forward',[(.18,0)]),('backward',[(-.18,0)]),('yaw_positive',[(0,.3)]),('yaw_negative',[(0,-.3)]),('forward_left',[(.18,.3)]),('forward_right',[(.18,-.3)]),('backward_left',[(-.18,.3)]),('backward_right',[(-.18,-.3)]),('forward_stop',[(.18,0),(0,0)]),('backward_stop',[(-.18,0),(0,0)]),('left_right',[(0,.3),(0,-.3)]),('forward_backward',[(.18,0),(-.18,0)]),('continuous',[(.18,.3),(0,0),(-.18,-.3),(0,.3),(0,-.3),(0,0)]),('forward',[(.25,0)]),('backward',[(-.25,0)])]

def summarize(d,ix,name,t):
    """Returns separate stop/motion phases so successful motion cannot hide failed stopping."""
    c=d['command'][:,ix];vel=d['velocity'][:,ix];yaw=d['yaw'][:,ix]
    changes=np.any(np.diff(c,axis=0)!=0,axis=(1,2));age=np.zeros(len(c));age[0]=.02
    for k in range(1,len(c)):age[k]=.02 if changes[k-1] else age[k-1]+.02
    valid=d['valid'][:,ix]&(age[:,None]>.6)
    moving=np.linalg.norm(c,axis=-1)>.04;result=[]
    for is_stop in [False,True]:
        mask=valid&(~moving if is_stop else moving)
        if not mask.any():continue
        def avg(x):return float(x[mask].mean())
        contact=d['contact'][:,ix];height=d['foot_height'][:,ix]
        strict=(~contact)&(height>t['swing_height'])&(d['raw_force'][:,ix]<1.)&(~d['shin'][:,ix])
        slip=np.linalg.norm(d['patch_velocity'][:,ix,:,:2],axis=-1);support=contact&mask[:,:,None]
        r=dict(test=name,is_stop=is_stop,valid=True,valid_samples=int(mask.sum()),fall_rate=float(d['fall'][:,ix].any(0).mean()),velocity=vel[mask].mean(0).tolist(),yaw=avg(yaw),yaw_abs=avg(abs(yaw)),speed_xy=avg(np.linalg.norm(vel[:,:,:2],axis=-1)),lateral_speed=avg(abs(vel[:,:,1])),tilt=avg(d['tilt'][:,ix]),support_slip_speed=float(slip[support].mean()) if support.any() else 1.,tracking_ratios=[],pure_yaw=bool((abs(c[:,:,0][mask])<.04).all() and not is_stop),feet={},periodic_legs=0)
        for j,value in [(0,vel[:,:,0]),(2,yaw)]:
            for sign in [1,-1]:
                active=mask&(c[:,:,j]*sign>.04)
                if active.any():r['tracking_ratios'].append(float((value[active]*sign/abs(c[:,:,j][active])).mean()))
        trial_qualified=np.ones(len(ix),dtype=bool)
        for j,leg in enumerate(LEGS):
            all_durations=[];qualified=[];switches=[]
            for k in range(len(ix)):
                # Preserve gaps as False: never concatenate air phases separated by reset or stop.
                signal=strict[:,k,j]&mask[:,k]
                ds=durations(signal);all_durations+=ds
                sw=int(((np.diff(contact[:,k,j].astype(int))!=0)&mask[1:,k]&mask[:-1,k]).sum());switches.append(sw)
                qualified.append(sum(v>=t['swing_duration'] for v in ds)>=2 and sw>=4)
            qualified=np.array(qualified);trial_qualified&=qualified
            if qualified.mean()>=t['trial_pass_fraction']:r['periodic_legs']+=1
            r[leg+'_swing_ratio']=avg(strict[:,:,j].astype(float))
            r['feet'][leg]=dict(swing_ratio=r[leg+'_swing_ratio'],max_height=float(height[:,:,j][mask].max()),swing_durations_s=all_durations,contact_switches=switches,swing_seconds_per_trial=float((strict[:,:,j]&mask).sum()*.02/len(ix)))
        r['gait_trial_fraction']=float(trial_qualified.mean())
        r['torque_saturation']=avg((abs(d['torque'][:,ix])>=9.9).mean(-1))
        r['action_delta_rms']=float(np.sqrt(np.mean(np.diff(d['raw_action'][:,ix],axis=0)**2)))
        r['displacement_body_x']=float(np.sum(vel[:,:,0]*mask)*.02/len(ix))
        result.append(r)
    if not result:
        result=[dict(test=name,is_stop=False,valid=False,valid_samples=0,fall_rate=1.,velocity=[0,0,0],yaw=0.,speed_xy=0.,lateral_speed=0.,tilt=1.,support_slip_speed=1.,tracking_ratios=[0.],pure_yaw=False,feet={},periodic_legs=0,gait_trial_fraction=0.,**{l+'_swing_ratio':0. for l in LEGS})]
    return result

def evaluate(runner,out,full=True,tag=None,seeds_override=None):
    b=runner.env.unwrapped;cfg=b.cfg
    rng=(torch.get_rng_state(),torch.cuda.get_rng_state_all(),np.random.get_state(),random.getstate())
    candidate=runner.supervisor.state['candidate']
    seeds=(seeds_override or (candidate.get('evaluation_seeds') if candidate else None) or [103,307,911,1301+1009*runner.supervisor.state['full_windows']]) if full else [103]
    seconds=12. if full else 6.;reps=b.num_envs//len(CASES)
    if reps<1:raise ValueError('Evaluation requires at least 16 environments')
    commands=torch.zeros(6,b.num_envs,3,device=b.device)
    for i,(_,sequence) in enumerate(CASES):
        for k in range(6):
            x,z=sequence[k%len(sequence)]
            commands[k,i*reps:(i+1)*reps,0]=x;commands[k,i*reps:(i+1)*reps,2]=z
    # Perturbations remain enabled; each seed yields genuinely different reset poses.
    rows=[];evaluation_id=tag or f"{runner.total_updates:08d}_{'full' if full else 'light'}"
    saved_episode=cfg.episode_length_s
    saved_noise=cfg.events.reset_joints.params['position_range']
    saved_pose=cfg.events.reset_base.params['pose_range'].copy()
    cfg.events.reset_joints.params['position_range']=(-.035,.035)
    cfg.events.reset_base.params['pose_range'].update(roll=(-.025,.025),pitch=(-.025,.025))
    runner.alg.policy.eval();policy=runner.get_inference_policy(device=b.device)
    try:
        for seed in seeds:
            with torch.inference_mode():d=rollout(runner.env,policy,commands,seconds,seed)
            np.savez_compressed(out/f'evaluation_{evaluation_id}_seed{seed}.npz',**d)
            for i,(name,_) in enumerate(CASES):
                for row in summarize(d,list(range(i*reps,(i+1)*reps)),name,runner.supervisor.options['thresholds']):
                    row.update(seed=seed,replicates=reps);rows.append(row)
        # Same joint state, two commands: actor response is diagnostic, never a success criterion.
        obs=runner.env.get_observations().clone()
        with torch.inference_mode():
            obs['policy'][:,9:12]=0.;a0=policy(obs).clone()
            obs['policy'][:,9]=.18;a1=policy(obs).clone()
        response=float((a1-a0).square().mean().sqrt())
        summary=dict(id=evaluation_id,full=full,updates=runner.total_updates,num_envs=b.num_envs,seeds=seeds,seconds=seconds,rows=rows,actor_command_response_rms=response,ppo=runner.last_ppo)
        atomic_json(out/f'evaluation_{evaluation_id}.json',summary)
        return summary
    finally:
        cfg.episode_length_s=saved_episode;cfg.events.reset_joints.params['position_range']=saved_noise;cfg.events.reset_base.params['pose_range']=saved_pose
        with torch.inference_mode():b.reset()
        runner.env.samples.clear();runner.env.previous=None
        torch.set_rng_state(rng[0]);torch.cuda.set_rng_state_all(rng[1]);np.random.set_state(rng[2]);random.setstate(rng[3])
        runner.alg.policy.train()
