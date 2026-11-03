"""500Hz geometric evaluation, independent of reward and equal across ablation arms."""
from pathlib import Path
import numpy as np
import torch
from .runtime import contacts,clock
from ...autoppo.storage import atomic_json

@torch.inference_mode()
def evaluate(runner,out,seeds=(103,307),seconds=10.,video=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    b=runner.env.unwrapped
    if video:b.render_mode='rgb_array'
    r=b.scene['robot'];s=contacts(b);rows=[];raws=[];frames=[]
    from ..curriculum_v6_3.stride import Stride
    from isaaclab.utils.math import quat_apply_inverse
    from tensordict import TensorDict
    commands={'forward':[.2,0,0],'stop':[0,0,0]}
    stage=b.cfg.v7.get('stage',0)
    if stage>=1:commands.update(backward=[-.2,0,0])
    if stage>=2:commands.update(yaw_positive=[0,0,.3],yaw_negative=[0,0,-.3])
    if stage>=3:commands.update(forward_left=[.2,0,.3],forward_right=[.2,0,-.3],backward_left=[-.2,0,.3],backward_right=[-.2,0,-.3])
    commands['transition_stop']=[0,0,0]
    state=Stride(b.num_envs,b.device);air=torch.zeros(b.num_envs,4,device=b.device,dtype=torch.long)
    max_air=torch.zeros_like(air);previous=torch.zeros_like(air,dtype=torch.bool);count=torch.zeros_like(air);cycles=torch.zeros_like(air)
    original_update=b.scene.update;recording=[False];phase_for_action=[None];tangents=[None]
    def update(dt):
        original_update(dt)
        if not recording[0]:return
        s.key=None;s.update();d=r.data;reset=b.episode_length_buf<=1
        rel=quat_apply_inverse(d.root_quat_w[:,None,:].expand(-1,4,-1),s.tip_position-d.root_pos_w[:,None,:])
        cmd=b.command_manager.get_command('base_velocity');turn=(cmd[:,0].abs()<.04)&(cmd[:,2].abs()>.04)
        tangent=torch.stack((-rel[:,:,1],rel[:,:,0]),-1)/rel[:,:,:2].norm(dim=-1,keepdim=True).clamp_min(.05)
        if tangents[0] is None:tangents[0]=tangent.clone()
        tangents[0]=torch.where(reset[:,None,None],tangent,tangents[0])
        placement=torch.where(turn[:,None],(rel[:,:,:2]*tangents[0]).sum(-1),rel[:,:,0])
        c=torch.where(turn,cmd[:,2],cmd[:,0]);v=torch.where(turn,d.root_ang_vel_b[:,2],d.root_lin_vel_b[:,0])
        old=state.stride_count.clone()
        state.update(dt,s.contact,s.clearance,s.raw_force,s.shin,placement,s.velocity[:,:,:2].norm(dim=-1),c,v,d.projected_gravity_b[:,:2].norm(dim=-1),s.force,reset)
        delta=(state.stride_count-old).clamp_min(0);cycles.add_(delta.long())
        strict=(~s.contact)&(s.clearance>.015)&(s.raw_force<1.)&~s.shin
        air.copy_(torch.where(strict,air+1,torch.zeros_like(air)));max_air.copy_(torch.maximum(max_air,air))
        count.add_(s.contact&~previous&(max_air>=30));max_air.masked_fill_(s.contact,0);previous.copy_(s.contact)
        raw=torch.cat((d.root_lin_vel_b[:,:2],d.root_ang_vel_b[:,2:3],phase_for_action[0][:,None],s.contact.float(),s.clearance,s.velocity[:,:,:2].norm(dim=-1),s.shin.float(),delta,count.float(),s.velocity.norm(dim=-1),d.projected_gravity_b[:,:2].norm(dim=-1)[:,None],d.joint_vel.square().mean(-1).sqrt()[:,None]),-1)
        raws.append(raw.cpu().numpy())
    b.scene.update=update
    try:
        for seed in seeds:
            for mode,target in commands.items():
                b.reset(seed=seed);s.key=None;clock(b).reset(slice(None));state.reset(torch.ones(b.num_envs,device=b.device,dtype=torch.bool));air.zero_();max_air.zero_();count.zero_();cycles.zero_();previous.zero_();raws.clear();tangents[0]=None
                falls=torch.zeros(b.num_envs,device=b.device);n=int(seconds/b.step_dt);recording[0]=True
                for t in range(n):
                    desired=[.2,0,0] if mode=='transition_stop' and t<n//2 else target
                    cmd=b.command_manager.get_term('base_velocity');cmd.vel_command_b[:]=torch.tensor(desired,device=b.device);cmd.is_standing_env[:]=sum(abs(x) for x in desired)<.04;cmd.time_left[:]=100.
                    obs=TensorDict(b.observation_manager.compute(),batch_size=[b.num_envs],device=b.device)
                    phase_for_action[0]=clock(b).phase.clone();state.begin_control()
                    action=runner.alg.policy.act_inference(obs);runner.env.step(action);falls+=b.reset_terminated.float()
                    if video and seed==seeds[0] and mode in ('forward','transition_stop') and t%2==0:
                        frame=b.render()
                        if frame is not None:frames.append(frame)
                recording[0]=False;a=np.stack(raws)
                np.savez_compressed(out/f'{mode}_seed{seed}.npz',data=a,dt=b.physics_dt,columns='vx vy yaw phase contact4 clearance4 slip4 shin4 cycle_delta4 cumulative_swing4 foot_speed3d4 tilt joint_velocity_rms')
                # Settling excluded. Transition stop measured after 0.5s grace.
                begin=int((seconds/2+.5 if mode=='transition_stop' else 1.)/b.physics_dt);a=a[begin:]
                contact=a[:,:,4:8]>.5;clear=a[:,:,8:12];slip=a[:,:,12:16];shin=a[:,:,16:20]>.5;support=contact&~shin
                stance=.5+.5*np.tanh(np.sin(a[:,:,3])/.2);plan=np.stack((1-stance,stance,stance,1-stance),-1);match=plan*contact+(1-plan)*(~contact)
                target=np.array(target);active=np.abs(target[[0,2]])>.04
                ratios=[]
                if active[0]:ratios.append(a[:,:,0].mean(0)/target[0])
                if active[1]:ratios.append(a[:,:,2].mean(0)/target[2])
                tracking=np.stack(ratios).mean(0) if ratios else np.zeros(b.num_envs)
                row=dict(seed=seed,mode=mode,target_velocity=target.tolist(),target_speed=float(target[0]),actual_speed=float(a[:,:,0].mean()),lateral_rms=float(np.sqrt((a[:,:,1]**2).mean())),yaw_abs=float(np.abs(a[:,:,2]).mean()),translation_rms=float(np.sqrt((a[:,:,:2]**2).sum(-1).mean())),tracking_ratio=float(tracking.mean()),tracking_quantiles=[float(min(np.quantile(v,.1) for v in ratios)),float(max(np.quantile(v,.9) for v in ratios))] if ratios else [0.,0.],contact_duty=contact.mean((0,1)).tolist(),phase_match=float(match.mean()),phase_match_q10=float(np.quantile(match.mean((0,2)),.1)),swing_count=count.sum(0).tolist(),min_swing_per_env=float(np.quantile(count.cpu().numpy(),.1,axis=0).min()),complete_cycles=cycles.sum(0).tolist(),cycle_q10=np.quantile(cycles.cpu().numpy(),.1,axis=0).tolist(),clearance_peak=np.quantile(clear,.95,axis=(0,1)).tolist(),support_slip=float((slip*support).sum()/max(1,support.sum())),shin_rate=float(shin.mean()),fall_fraction=float((falls>0).float().mean()))
                row.update(foot_speed=float(a[:,:,28:32].mean()),tilt_q95=float(np.quantile(a[:,:,32],.95)),joint_velocity_rms=float(a[:,:,33].mean()))
                moving=active.any()
                from .trace_metrics import qualify_row
                row['qualified']=qualify_row(row)
                rows.append(row)
    finally:b.scene.update=original_update;recording[0]=False
    moving=[x for x in rows if x['mode']=='forward'];stopped=[x for x in rows if x['mode'] in ('stop','transition_stop')]
    m={k:float(np.mean([x[k] for x in moving])) for k in ['actual_speed','phase_match','support_slip','shin_rate','fall_fraction','min_swing_per_env']}
    m.update(stop_speed=float(max(x['translation_rms'] for x in stopped)),stop_yaw=float(max(x['yaw_abs'] for x in stopped)),contact_duty=np.mean([x['contact_duty'] for x in moving],axis=0).tolist(),swing_count=np.sum([x['swing_count'] for x in moving],axis=0).tolist(),clearance_peak=np.mean([x['clearance_peak'] for x in moving],axis=0).tolist(),complete_cycles=np.sum([x['complete_cycles'] for x in moving],axis=0).tolist(),qualified=all(x['qualified'] for x in rows),course=stage,rows=rows,stop_foot_speed=max(x['foot_speed'] for x in stopped),stop_min_contact_duty=min(min(x['contact_duty']) for x in stopped),protocol='v7-geometry-500hz-v3')
    atomic_json(out/'evaluation.json',dict(protocol='v7-geometry-500hz-v3',rows=rows,metrics=m,seed_list=list(seeds),seconds=seconds,training_updates=runner.updates))
    from .trace_metrics import correct_evaluation
    m=correct_evaluation(out/'evaluation.json')
    if frames:
        import imageio.v2 as imageio
        imageio.mimsave(out/'physical_rollout.mp4',frames,fps=25)
    return m
