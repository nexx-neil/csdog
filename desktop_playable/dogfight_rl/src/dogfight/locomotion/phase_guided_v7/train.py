"""Bounded V7 worker using the installed RSL-RL PPO and AutoPPO persistence."""
from pathlib import Path
import json,os,time,signal,random,uuid,fcntl
import numpy as np
from ...autoppo.storage import atomic_json

def worker(base,arm,target=250,resume=None,smoke=False,out=None,options_override=None):
    base=Path(base);out=Path(out) if out else base/arm;out.mkdir(parents=True,exist_ok=True)
    gpu_lock=(Path(__file__).resolve().parents[4]/'runs/locomotion/csdog_curriculum_v6/gpu.lock').open('a');fcntl.flock(gpu_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    from isaaclab.app import AppLauncher
    app=AppLauncher(headless=True,enable_cameras=True).app
    import torch,gymnasium as gym
    torch.set_num_threads(4);seed=42;torch.manual_seed(seed);np.random.seed(seed);random.seed(seed)
    from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
    from rsl_rl.runners import OnPolicyRunner
    from .runtime import build,contacts,clock
    from .kernel import DEFAULTS
    import dogfight.locomotion
    options=dict(DEFAULTS,phase=arm in ('C','D'),collision='sole' if arm in ('B','D') else 'original')
    if options_override:options.update(options_override)
    cfg,agent=build(options,64 if smoke else 128,seed)
    cfg.viewer.resolution=(640,480)
    env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg,render_mode='rgb_array')
    b=env.unwrapped;wrapped=RslRlVecEnvWrapper(env,clip_actions=None)
    result={'status':'FAILED'};stop=[False];start=time.time()
    class Runner(OnPolicyRunner):
        def __init__(self,*a,**kw):self.updates=0;super().__init__(*a,**kw)
        def log(self,locs,*args,**kwargs):
            self.updates+=1
            super().log(locs,*args,**kwargs)
            s=contacts(b);d=b.scene['robot'].data
            row=dict(reward_rate_schema=2,updates=self.updates,environment_steps=self.updates*self.num_steps_per_env*b.num_envs,actual_speed=float(d.root_lin_vel_b[:,0].mean()),clearance_peak=s.clearance.max(0).values.tolist(),contact_duty=s.contact.float().mean(0).tolist(),loss={k:float(v) for k,v in locs['loss_dict'].items()},wall_seconds=time.time()-start,reward_rates={name:float(b.reward_manager._step_reward[:,i].mean()) for i,name in enumerate(b.reward_manager.active_terms)})
            with (out/'metrics.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            atomic_json(out/'progress.json',row)

            if not all(torch.isfinite(v).all() for v in self.alg.policy.state_dict().values()):raise RuntimeError('NONFINITE_POLICY')
            if __import__('shutil').disk_usage(out).free<4*1024**3:raise OSError('DISK_FREE_BELOW_4_GIB')
            if stop[0] or (base/'STOP').exists():raise InterruptedError('USER_STOP')
        def save(self,path,infos=None):
            if Path(path).name.startswith('model_'):return
            dest=Path(path)
            if dest.exists():raise FileExistsError(dest)
            info=dict(v7=dict(options=options,updates=self.updates,phase=clock(b).state_dict(),simulation_restored=False,rng=dict(torch=torch.get_rng_state(),cuda=torch.cuda.get_rng_state_all(),numpy=np.random.get_state(),python=random.getstate())))
            tmp=dest.with_name('.'+dest.name+'.tmp');super().save(str(tmp),info);os.replace(tmp,dest)
            fd=os.open(dest,os.O_RDONLY)
            try:os.fsync(fd)
            finally:os.close(fd)
    runner=Runner(wrapped,agent.to_dict(),log_dir=str(out/'TensorBoard'),device='cuda:0')
    for sig in (signal.SIGTERM,signal.SIGINT):signal.signal(sig,lambda *args:stop.__setitem__(0,True))
    try:
        obs=wrapped.get_observations();expected=50 if options['phase'] else 48
        assert obs['policy'].shape[-1]==expected and obs['critic'].shape[-1]==expected
        assert b.scene['robot'].num_joints==12
        from ..robot_cfg import JOINTS
        assert list(b.action_manager.get_term('joint_pos')._joint_names)==JOINTS
        r=b.scene['robot'];assert torch.all(r.data.joint_effort_limits==10.) and torch.all(r.data.joint_vel_limits==3.)
        if options['phase']:assert torch.allclose(obs['policy'][:,-2:],clock(b).observation())
        atomic_json(out/'preflight.json',dict(status='PASS',actor_obs=expected,critic_obs=expected,joints=JOINTS,mass=float(r.root_physx_view.get_masses()[0].sum()),effort_limit=10.,velocity_limit=3.,per_env_clock=True))
        # Freeze network identity and control mapping in a run-local launch record.
        atomic_json(out/'launch.json',dict(options=options,num_envs=b.num_envs,seed=seed,observation_dim=expected,action_dim=12,dt=b.step_dt,physics_dt=b.physics_dt,source=resume,random_initialization=resume is None,ppo=agent.to_dict()))
        if resume:
            data=torch.load(resume,weights_only=False,map_location='cuda:0');meta=data['infos']['v7']
            assert all(meta['options'][k]==options[k] for k in ('phase','collision')),'Incompatible observation or collision lineage'
            # New search candidates may mutate one gait parameter. Same-trial
            # resumes retain the exact immutable candidate config from SQLite.
            runner.load(str(resume));runner.updates=meta['updates'];b.reset(seed=seed)
            rng=meta['rng'];torch.set_rng_state(rng['torch'].cpu());torch.cuda.set_rng_state_all([x.cpu() for x in rng['cuda']]);np.random.set_state(rng['numpy']);random.setstate(rng['python'])
        while runner.updates<target:
            runner.current_learning_iteration=runner.updates
            runner.learn(min(25,target-runner.updates),init_at_random_ep_len=False)
            cp=out/f'checkpoint_{runner.updates:06d}_{uuid.uuid4().hex[:6]}.pt';runner.save(str(cp));atomic_json(out/'latest.json',dict(path=str(cp),updates=runner.updates))
        from .evaluation import evaluate
        cp=out/f'final_{runner.updates:06d}_{uuid.uuid4().hex[:6]}.pt';runner.save(str(cp))
        m=evaluate(runner,out/f'evaluation_{runner.updates}',seeds=(103,) if smoke else (103,307),seconds=3. if smoke else 10.,video=True)
        if m['qualified'] and not smoke:
            confirm=evaluate(runner,out/f'confirmation_{runner.updates}',seeds=(2027,4099),seconds=12.,video=False)
            m['qualified']=bool(confirm['qualified']);m['independent_confirmation']=confirm
        from .plots import physical
        for p in (out/f'evaluation_{runner.updates}').glob('*.npz'):physical(p)
        result=dict(status='COMPLETE',checkpoint=str(cp),updates=runner.updates,environment_steps=runner.updates*runner.num_steps_per_env*b.num_envs,metrics=m)
    except BaseException as exc:
        import traceback;traceback.print_exc()
        cp=out/f'interrupted_{runner.updates:06d}_{uuid.uuid4().hex[:6]}.pt'
        try:runner.save(str(cp))
        except Exception:cp=None
        result=dict(status='STOPPED' if isinstance(exc,InterruptedError) else 'FAILED',error=repr(exc),updates=runner.updates,checkpoint=str(cp) if cp else None)
    finally:
        atomic_json(out/'result.json',result)
        if runner.writer:runner.writer.close()
        env.close();app.close(wait_for_replicator=False,skip_cleanup=True);gpu_lock.close()
    return 0 if result['status'] in ('COMPLETE','STOPPED') else 1
