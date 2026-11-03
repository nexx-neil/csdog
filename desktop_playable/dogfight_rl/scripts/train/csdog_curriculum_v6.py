"""CSDog V6 native PPO: unlimited capability-gated curriculum or explicit smoke budget."""
from pathlib import Path
import argparse,copy,hashlib,json,os,random,shutil,signal,sys,time,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iterations',default='unlimited');p.add_argument('--auto-curriculum',action='store_true');p.add_argument('--auto-recovery',action='store_true')
    p.add_argument('--num-envs',type=int);p.add_argument('--headless',action='store_true');p.add_argument('--seed',type=int,default=42)
    p.add_argument('--experiment-name',required=True);p.add_argument('--resume',action='store_true');p.add_argument('--checkpoint',type=Path);p.add_argument('--device',default='cuda:0')
    p.add_argument('--config',type=Path,default=ROOT/'configs/locomotion/curriculum_v6/default.json');p.add_argument('--smoke-test',action='store_true');p.add_argument('--check-args',action='store_true')
    a=p.parse_args();limit=None
    if a.iterations!='unlimited':
        try:limit=int(a.iterations)
        except ValueError:p.error('--iterations accepts unlimited or a positive smoke update count')
        if limit<1 or not a.smoke_test:p.error('Finite updates are supported only with --smoke-test')
    if limit is None and (not a.auto_curriculum or not a.auto_recovery):p.error('Unlimited training requires --auto-curriculum --auto-recovery')
    if a.num_envs is None:
        import subprocess
        try:
            free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])
            a.num_envs=256 if free>=5000 else 128 if free>=3500 else 64 if free>=2500 else 32
        except Exception:a.num_envs=128
    if a.num_envs<16 or a.num_envs%16:p.error('--num-envs must be divisible by 16 (minimum 16)')
    import re
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',a.experiment_name):p.error('Use a simple unique experiment name')
    if a.resume!=bool(a.checkpoint):p.error('--resume requires a full V6 --checkpoint')
    out=ROOT/'runs/locomotion/csdog_curriculum_v6'/a.experiment_name
    if out.exists():p.error('Output exists; use a new experiment name, including for resume')
    options=json.loads(a.config.read_text())
    if a.check_args:print(json.dumps(dict(status='ARGUMENTS_VALID',iterations=limit or 'unlimited',output=str(out))));return
    out.mkdir(parents=True)
    import fcntl
    gpu_lock=(out.parent/'gpu.lock').open('a')
    fcntl.flock(gpu_lock,fcntl.LOCK_EX)  # Only one V6 simulator uses the GPU at a time.
    from dogfight.locomotion.curriculum_v6.supervisor import Supervisor,atomic_json,STAGES,BEST_NAMES
    supervisor=Supervisor(out,options);supervisor.publish()
    atomic_json(out/'launch.json',{k:str(v) if isinstance(v,Path) else v for k,v in vars(a).items()})
    (out/'pid').write_text(str(os.getpid()))
    files=list((ROOT/'src/dogfight/locomotion/curriculum_v6').glob('*.py'))+[Path(__file__),a.config]
    atomic_json(out/'source_sha256.json',{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files})
    protected=list((ROOT.parent/'model').rglob('*'))+list((ROOT/'assets/csdog_12dof').rglob('*'))
    protected=[f for f in protected if f.is_file()]
    hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in protected};atomic_json(out/'protected_before.json',hashes)
    import torch,numpy as np
    torch.set_num_threads(4);torch.manual_seed(a.seed);np.random.seed(a.seed);random.seed(a.seed)
    from isaaclab.app import AppLauncher
    app=AppLauncher(headless=a.headless,device=a.device).app
    env=None;runner=None;start=time.monotonic();success=False
    try:
        import gymnasium as gym
        from isaaclab.utils.io import dump_yaml
        from dogfight.locomotion.curriculum_v6.config import build
        from dogfight.locomotion.curriculum_v6.runner import Runner,Wrapper,GracefulStop
        from dogfight.locomotion.curriculum_v6.evaluation import evaluate
        from dogfight.locomotion.spot_v4.runtime import preflight
        if a.resume:
            resumed=torch.load(a.checkpoint,map_location='cpu',weights_only=False)
            resume_meta=(resumed.get('infos') or {}).get('curriculum_v6')
            if not resume_meta:raise ValueError('V6 full-state checkpoint required')
            if resume_meta['state'].get('num_envs',a.num_envs)!=a.num_envs:raise ValueError('Resume must retain num-envs for matched candidate sampling budgets')
            options=copy.deepcopy(resume_meta['options']);a.seed=resume_meta['state'].get('seed',a.seed)
        supervisor.state.update(seed=a.seed,num_envs=a.num_envs)
        cfg,agent=build(options,a.num_envs,a.seed,a.device);cfg.log_dir=str(out)
        env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg)
        atomic_json(out/'preflight.json',preflight(env))
        wrapped=Wrapper(env,clip_actions=None)
        # Preflight consumes RNG; seed the learner explicitly so random initialization is reproducible.
        torch.manual_seed(a.seed);np.random.seed(a.seed);random.seed(a.seed)
        runner=Runner(wrapped,agent.to_dict(),device=a.device,log_dir=str(out/'TensorBoard'),supervisor=supervisor)
        initial_hash=hashlib.sha256(b''.join(v.detach().cpu().numpy().tobytes() for v in runner.alg.policy.state_dict().values())).hexdigest()
        atomic_json(out/'initialization.json',dict(mode='full_v6_resume' if a.resume else 'random_from_scratch',seed=a.seed,initial_network_sha256=initial_hash,checkpoint=str(a.checkpoint) if a.resume else None))
        if a.resume:runner.restore(a.checkpoint);supervisor.event('FULL_LEARNER_RESUME',checkpoint=str(a.checkpoint),simulation_reset=True)
        runner.apply();dump_yaml(str(out/'env.yaml'),cfg);dump_yaml(str(out/'agent.yaml'),agent)
        def stopped(sig,frame):runner.stop_requested='USER_SIGNAL_'+str(sig)
        signal.signal(signal.SIGTERM,stopped);signal.signal(signal.SIGINT,stopped)
        # Validate signed command observation and exact PD target mapping without root-velocity writes.
        b=env.unwrapped;r=b.scene['robot'];term=b.command_manager.get_term('base_velocity')
        action=b.action_manager.get_term('joint_pos');mapping=action._joint_ids
        checks={}
        with torch.inference_mode():
            for name,command in [('forward',[.18,0,0]),('backward',[-.18,0,0]),('yaw_positive',[0,0,.3]),('yaw_negative',[0,0,-.3])]:
                term.vel_command_b[:]=torch.tensor(command,device=b.device);term.time_left[:]=100.
                obs=b.observation_manager.compute()
                if not torch.allclose(obs['policy'][:,9:12],term.vel_command_b):raise RuntimeError('COMMAND_OBSERVATION_SIGN_MISMATCH')
                checks[name]=True
            probe=torch.zeros(b.num_envs,12,device=b.device);probe[:,0]=.05
            b.step(probe)
            expected=r.data.default_joint_pos[:,mapping]+.2*probe
            if not torch.allclose(r.data.joint_pos_target[:,mapping],expected,atol=1e-5):raise RuntimeError('PD_TARGET_MAPPING_MISMATCH')
            b.reset()
        from isaaclab.utils.math import quat_apply_inverse
        if not torch.allclose(quat_apply_inverse(r.data.root_quat_w,r.data.root_lin_vel_w),r.data.root_lin_vel_b,atol=1e-5):raise RuntimeError('BODY_VELOCITY_FRAME_MISMATCH')
        checks.update(pd_target_mapping=True,body_velocity_frame=True,joints=12,root_velocity_override_used=False)
        from dogfight.locomotion.curriculum_v6.commands import DISTRIBUTIONS
        command_options=copy.deepcopy(term.cfg.v6);samples={}
        for stage,dist in enumerate(DISTRIBUTIONS):
            term.cfg.v6={'distribution':dist,'speed_range':[.12,.25]}
            collected=[]
            for _ in range(8):
                term._resample_command(torch.arange(b.num_envs,device=b.device));collected.append(term.vel_command_b.clone())
            commands=torch.cat(collected)
            if commands[:,1].abs().max()>0:raise RuntimeError('UNEXPECTED_LATERAL_COMMAND')
            if stage==0 and ((commands[:,0]<0).any() or (commands[:,2]!=0).any()):raise RuntimeError('FORWARD_STAGE_COMMAND_LEAK')
            samples[str(stage+1)]=dict(total=len(commands),forward=float((commands[:,0]>0).float().mean()),backward=float((commands[:,0]<0).float().mean()),yaw_positive=float((commands[:,2]>0).float().mean()),yaw_negative=float((commands[:,2]<0).float().mean()),stop=float((commands.norm(dim=-1)==0).float().mean()))
        term.cfg.v6=command_options
        checks['command_sampling']=samples
        checks['gpu_memory_free_mib']=torch.cuda.mem_get_info()[0]//(1024**2)
        atomic_json(out/'interface_checks.json',checks)
        if a.resume:runner.restore(a.checkpoint)  # Interface probes must not consume the restored learner RNG.
        runner.apply();runner.save(str(out/'initial.pt'))
        if not a.smoke_test:
            baseline=evaluate(runner,out,full=False,tag=f'baseline_{runner.total_updates:08d}')
            supervisor.state['last_evaluation']=baseline
            supervisor.event('BASELINE_EVALUATION',evaluation=baseline['id'],mode='resume' if a.resume else 'random_from_scratch')
            supervisor.publish(baseline)
        session_start=runner.total_updates;last_light=runner.total_updates;last_full=runner.total_updates
        while True:
            if runner.stop_requested:raise GracefulStop(runner.stop_requested)
            if (out/'STOP').exists():raise GracefulStop('USER_STOP_FILE')
            if shutil.disk_usage(out).free<5*1024**3:raise RuntimeError('DISK_FREE_BELOW_5_GIB')
            m=supervisor.options['monitor'];n=min(m['save_interval'],m['light_interval']-(runner.total_updates-last_light),m['full_interval']-(runner.total_updates-last_full))
            candidate=supervisor.state['candidate']
            if candidate:n=min(n,m['candidate_updates']-(runner.total_updates-candidate['start_update']))
            if limit is not None:n=min(n,limit-(runner.total_updates-session_start))
            runner.current_learning_iteration=runner.total_updates
            if n>0:runner.learn(n,init_at_random_ep_len=False)
            runner.current_learning_iteration=runner.total_updates
            if a.smoke_test:
                # Real full learner checkpoint round trip, including optimizer tensors and std.
                checkpoint=out/f'smoke_restore_{runner.total_updates:08d}.pt';runner.save(str(checkpoint))
                before=copy.deepcopy(runner.alg.policy.state_dict());optim=copy.deepcopy(runner.alg.optimizer.state_dict());lr=runner.alg.learning_rate
                with torch.no_grad():next(runner.alg.policy.actor.parameters()).add_(.001)
                runner.restore(checkpoint)
                def equal(x,y):
                    if torch.is_tensor(x):return torch.equal(x.cpu(),y.cpu())
                    if isinstance(x,dict):return x.keys()==y.keys() and all(equal(x[k],y[k]) for k in x)
                    if isinstance(x,(tuple,list)):return len(x)==len(y) and all(equal(v,w) for v,w in zip(x,y))
                    return x==y
                if not equal(before,runner.alg.policy.state_dict()) or not equal(optim,runner.alg.optimizer.state_dict()) or runner.alg.learning_rate!=lr:raise RuntimeError('CHECKPOINT_ROUNDTRIP_FAILED')
                atomic_json(out/'checkpoint_restore_test.json',dict(status='PASS',policy_exact=True,optimizer_exact=True,lr_exact=True,simulation_reset=True))
                summary=evaluate(runner,out,full=False);supervisor.publish(summary)
                if limit is not None and runner.total_updates-session_start>=limit:
                    supervisor.state['training_status']='SMOKE_PASSED';break
                continue
            full=runner.total_updates-last_full>=m['full_interval'] or bool(candidate and runner.total_updates-candidate['start_update']>=m['candidate_updates'])
            if full or runner.total_updates-last_light>=m['light_interval']:
                summary=evaluate(runner,out,full=full);last_light=runner.total_updates
                if full:
                    last_full=runner.total_updates;checkpoint=out/f'evaluated_{runner.total_updates:08d}.pt';runner.save(str(checkpoint))
                    supervisor.state['last_evaluation']=summary
                    previous_stage=supervisor.state['stage'];decision=supervisor.observe(summary,str(checkpoint),a.auto_recovery)
                    if decision.get('best'):
                        # Snapshot includes the just-computed assessment, and best aliases are atomically replaced.
                        runner.save(str(checkpoint));runner.save(str(out/'best_motion.pt'));runner.save(str(out/BEST_NAMES[previous_stage]))
                    action_name=decision['action']
                    if action_name in ['rollback','candidate_control','candidate_adjust']:
                        supervisor.event('ROLLBACK',checkpoint=decision['checkpoint'],reason=decision.get('reason',action_name),rejected_checkpoint=str(checkpoint))
                        restored=runner.restore(decision['checkpoint'],restore_supervisor=False)
                        if action_name=='rollback' and decision.get('reason')=='policy_regression':
                            from dogfight.locomotion.curriculum_v6.supervisor import score,assess
                            anchor_summary=evaluate(runner,out,full=True,tag=f'{runner.total_updates:08d}_anchor_review',seeds_override=summary['seeds'])
                            thresholds=supervisor.options['thresholds'];stage=supervisor.state['stage']
                            anchor_skills=assess(anchor_summary,stage,thresholds);new_skills=assess(summary,stage,thresholds)
                            better=(score(anchor_summary,stage,thresholds)>score(summary,stage,thresholds)+.02 or any(ok and not new_skills[k] for k,ok in anchor_skills.items()))
                            supervisor.event('COMMON_PANEL_ROLLBACK_REVIEW',accepted=better,anchor_evaluation=anchor_summary['id'],rejected_evaluation=summary['id'],seeds=summary['seeds'])
                            if not better:
                                runner.restore(checkpoint,restore_supervisor=False);supervisor.state['repairs']-=1
                                decision['failed_skills']=[]
                            else:
                                for key in ['weights','ppo','distribution','speed_range']:supervisor.state[key]=copy.deepcopy(restored['state'][key])
                        if action_name=='candidate_adjust':
                            factor=supervisor.adjust(decision['diagnosis'],summary)
                            if factor=='exploration_scale':
                                before=float(runner.alg.policy.std.mean())
                                with torch.no_grad():runner.alg.policy.std.mul_(1.25).clamp_(max=.65)
                                supervisor.event('EXPLORATION_CHANGE',before=before,after=float(runner.alg.policy.std.mean()))
                        if action_name=='rollback' and decision.get('failed_skills'):
                            from dogfight.locomotion.curriculum_v6.commands import DISTRIBUTIONS
                            dist=copy.deepcopy(supervisor.state['distribution'] or DISTRIBUTIONS[supervisor.state['stage']])
                            for name in decision['failed_skills']:
                                if name in dist:dist[name]*=1.5
                            z=sum(dist.values());supervisor.state['distribution']={k:v/z for k,v in dist.items()}
                            supervisor.event('REGRESSION_SAMPLING_CHANGE',distribution=supervisor.state['distribution'])
                    runner.apply()
                    if action_name=='advance':runner.save(str(out/f'stage_{supervisor.state["stage"]+1}_entry.pt'))
                    runner.save(str(out/'latest.pt'))
                    if action_name in ['success','blocked']:
                        success=action_name=='success';supervisor.publish(summary);break
                supervisor.publish(summary)
        runner.save(str(out/'final.pt'))
    except BaseException as exc:
        traceback.print_exc()
        user=type(exc).__name__=='GracefulStop' and str(exc).startswith('USER_')
        supervisor.state['training_status']='INTERRUPTED' if user else 'BLOCKED_NEEDS_REDESIGN'
        supervisor.state['diagnosis']=str(exc)
        supervisor.event('PROCESS_STOP',error=repr(exc),traceback=traceback.format_exc())
        if runner:
            try:runner.save(str(out/'interrupted.pt'))
            except Exception as save_error:supervisor.event('CHECKPOINT_SAVE_FAILED',error=str(save_error))
    finally:
        supervisor.state['wall_seconds']=time.monotonic()-start
        supervisor.publish();supervisor.report()
        changed=[f for f,h in hashes.items() if not Path(f).exists() or hashlib.sha256(Path(f).read_bytes()).hexdigest()!=h]
        atomic_json(out/'protection_verification.json',dict(files=len(hashes),changed=changed))
        if runner and runner.writer:runner.writer.close()
        if env is not None:env.close()
        app.close(wait_for_replicator=False,skip_cleanup=True)
        fcntl.flock(gpu_lock,fcntl.LOCK_UN)
    if success:
        import subprocess
        result=subprocess.run([sys.executable,str(ROOT/'scripts/evaluate/csdog_curriculum_v6.py'),'--checkpoint',str(out/'final.pt'),'--output-dir',str(out/'final_video'),'--headless','--video'],stdout=(out/'video.log').open('w'),stderr=subprocess.STDOUT)
        atomic_json(out/'video_result.json',dict(returncode=result.returncode))
    return 0 if supervisor.state['training_status'] in ['SUCCESS','SMOKE_PASSED','INTERRUPTED'] else 2
if __name__=='__main__':sys.exit(main())
