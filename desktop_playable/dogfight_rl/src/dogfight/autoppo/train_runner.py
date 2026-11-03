"""One bounded native PPO worker. All simulation imports follow AppLauncher."""
from pathlib import Path
import copy,json,os,signal,time,traceback,fcntl,uuid,random
from .config import ROOT
from .storage import Store,atomic_json,canonical
from .resource_monitor import sample

def worker(base,trial_id,attempt_id,smoke=False):
    store=Store(base)
    trial=store.rows('SELECT * FROM trials WHERE id=?',(trial_id,))[0]
    config=json.loads(trial['config']);options=copy.deepcopy(config['options'])
    out=store.base/'trials'/trial_id/attempt_id;out.mkdir(parents=True,exist_ok=False)
    store.db.execute('UPDATE attempts SET pid=? WHERE id=?',(os.getpid(),attempt_id))
    atomic_json(out/'config.json',config)
    started=time.monotonic();app=None;env=None;runner=None;interrupted=False
    result=dict(status='FAILED',trial=trial_id,attempt=attempt_id)
    gpu_lock=(ROOT/'runs/locomotion/csdog_curriculum_v6/gpu.lock').open('a')
    try:
        fcntl.flock(gpu_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        import torch,numpy as np
        torch.set_num_threads(4);torch.manual_seed(config['seed']);np.random.seed(config['seed']);random.seed(config['seed'])
        from isaaclab.app import AppLauncher
        app=AppLauncher(headless=True,enable_cameras=True).app
        import gymnasium as gym
        from .runtime import build,Wrapper,Runner as NativeRunner
        from .evaluation import evaluate
        from .checkpoint_bank import inspect_checkpoint
        from .motion_evaluator import metrics,score,qualified,continuation_safe,safe
        from .checkpoint_bank import CheckpointBank
        from .recovery_manager import RecoveryManager
        from .stride import PROTOCOL
        from ..locomotion.curriculum_v6_1.supervisor import Supervisor
        from ..locomotion.curriculum_v6.runner import GracefulStop
        from ..locomotion.curriculum_v6.commands import DISTRIBUTIONS
        from ..locomotion.spot_v4.runtime import preflight
        from isaaclab.utils.io import dump_yaml
        start_progress=trial['progress'];source=trial['checkpoint'] or trial['source']
        if not source:raise ValueError('A verified compatible source is required for this branch')
        source_data,source_meta=inspect_checkpoint(source)
        cfg,agent=build(options,config['num_envs'],config['seed'],'cuda:0');cfg.viewer.resolution=(960,640)
        env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg,render_mode='rgb_array')
        atomic_json(out/'preflight.json',preflight(env))
        native_supervisor=Supervisor(out,copy.deepcopy(options))
        class MeasuredRunner(NativeRunner):
            def log(self,locs,*args,**kwargs):
                super().log(locs,*args,**kwargs)
                observed=self.total_updates-lineage_start
                store.db.execute('UPDATE attempts SET observed_updates=?,environment_steps=?,wall_seconds=? WHERE id=?',
                                 (observed,observed*self.num_steps_per_env*self.env.num_envs,time.monotonic()-started,attempt_id))
                if observed%25==0:
                    resource=sample(out)
                    atomic_json(out/'progress.json',dict(trial=trial_id,attempt=attempt_id,
                        progress=start_progress+observed,lineage_updates=self.total_updates,
                        environment_steps=observed*self.num_steps_per_env*self.env.num_envs,
                        steps_per_second=observed*self.num_steps_per_env*self.env.num_envs/max(.001,self.supervisor.state['training_seconds']-source_meta['state']['training_seconds']),
                        resources=resource))
                if (store.base/'STOP').exists():self.stop_requested='USER_STOP'
                if self.stop_requested:raise GracefulStop(self.stop_requested)
        runner=MeasuredRunner(Wrapper(env,clip_actions=None),agent.to_dict(),device='cuda:0',
                              log_dir=str(out/'TensorBoard'),supervisor=native_supervisor)
        lineage_start=source_meta['state']['total_updates']
        if trial['checkpoint'] or config['restore_mode']=='full':
            runner.restore(source)
            if trial['checkpoint'] and runner.total_updates!=source_meta['state']['total_updates']:raise ValueError('Resume counter mismatch')
            mode='full learner + optimizer + RNG; simulation reset'
        elif config['restore_mode']=='weights':
            runner.alg.policy.load_state_dict(source_data['model_state_dict'],strict=True)
            for key in ['total_updates','environment_steps','training_seconds','stage_updates']:
                native_supervisor.state[key]=copy.deepcopy(source_meta['state'][key])
            mode='actor/critic/std transferred; native optimizer reset; simulation reset'
        else:raise ValueError('Unsupported restoration mode')
        if not all(torch.equal(v.cpu(),source_data['model_state_dict'][k]) for k,v in runner.alg.policy.state_dict().items()):raise ValueError('Policy restoration mismatch')
        if trial['checkpoint'] or config['restore_mode']=='full':
            # Compare the actual optimizer payload, not just the number of groups.
            from ..locomotion.spot_v4.contracts import finite_tree
            def same(a,b):
                if torch.is_tensor(a):return torch.equal(a.cpu(),b.cpu())
                if isinstance(a,dict):return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
                if isinstance(a,(tuple,list)):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
                return a==b
            if not same(runner.alg.optimizer.state_dict(),source_data['optimizer_state_dict']):raise ValueError('Optimizer restoration mismatch')
        # Resume uses effective config from DB, not the donor's old reward/course.
        native_supervisor.options=copy.deepcopy(options)
        s=native_supervisor.state;s.update(stage=config['stage'],weights=copy.deepcopy(options['weights']),
            ppo=copy.deepcopy(options['ppo']),candidate=None,training_status='RUNNING',substage='1B',
            speed_range=config['speed_range'][:],num_envs=config['num_envs'],seed=config['seed'])
        dist=copy.deepcopy(DISTRIBUTIONS[config['stage']]);old_stop=dist['stop'];new_stop=config['stop_fraction']
        dist={k:(new_stop if k=='stop' else v*(1-new_stop)/(1-old_stop)) for k,v in dist.items()};s['distribution']=dist
        runner.apply()
        if not trial['checkpoint'] and config.get('mutation',{}):
            mutation=config['mutation']
            if mutation and mutation['group']=='ppo' and mutation['key']=='init_noise_std':
                with torch.no_grad():runner.alg.policy.std.fill_(options['ppo']['init_noise_std'])
        from .experiment_manager import source_hashes
        atomic_json(out/'source_sha256.json',source_hashes())
        dump_yaml(str(out/'env.yaml'),cfg);dump_yaml(str(out/'agent.yaml'),agent)
        atomic_json(out/'launch.json',dict(source=source,source_sha256=__import__('dogfight.autoppo.checkpoint_bank',fromlist=['sha256']).sha256(source),
            restore_mode=mode,start_progress=start_progress,lineage_start=lineage_start,
            optimizer_exact_restored=bool(trial['checkpoint'] or config['restore_mode']=='full'),
            actual_std=runner.alg.policy.std.tolist(),actual_learning_rate=runner.alg.learning_rate,
            actual_clip_param=runner.alg.clip_param,actual_lam=runner.alg.lam,
            commands=dist,speed_range=s['speed_range'],num_envs=config['num_envs'],seed=config['seed']))
        for sig in (signal.SIGTERM,signal.SIGINT):signal.signal(sig,lambda signum,frame:setattr(runner,'stop_requested','USER_SIGNAL'))
        result['restore_mode']=mode
        training_start=time.monotonic()
        def commit(label):
            observed=runner.total_updates-lineage_start;progress=start_progress+observed
            cp=out/f'{label}_{progress:08d}_{uuid.uuid4().hex[:6]}.pt';runner.save(str(cp))
            # Native save renames atomically. Validate the complete file before
            # DB progress can point at it; a torn write is never resumable.
            _,meta=inspect_checkpoint(cp)
            if meta['state']['total_updates']!=runner.total_updates:raise ValueError('Checkpoint counter mismatch')
            fd=os.open(cp,os.O_RDONLY)
            try:os.fsync(fd)
            finally:os.close(fd)
            fd=os.open(cp.parent,os.O_DIRECTORY)
            try:os.fsync(fd)
            finally:os.close(fd)
            with store.transaction():
                store.db.execute('UPDATE trials SET checkpoint=?,progress=?,updated=? WHERE id=?',(str(cp),progress,time.time(),trial_id))
                store.db.execute('UPDATE attempts SET checkpoint=?,observed_updates=?,environment_steps=? WHERE id=?',
                    (str(cp),observed,observed*runner.num_steps_per_env*config['num_envs'],attempt_id))
                store.event('CHECKPOINT_COMMITTED',trial_id,checkpoint=str(cp),progress=progress,lineage_updates=runner.total_updates)
            return cp
        def physical(progress,full,final=False):
            seeds=[103] if smoke or not full else [103,307,911,1301]
            panel=evaluate(runner,out/f'eval_{progress:08d}',full=full,seeds=seeds,raw=full)
            m=metrics(panel,config['stage']);identifier='eval_'+uuid.uuid4().hex
            store.db.execute('INSERT INTO evaluations VALUES(?,?,?,?,?,?,?,?,?,?)',
                (identifier,trial_id,attempt_id,progress,panel['protocol'],int(full),canonical(seeds),
                 str(out/f'eval_{progress:08d}/evaluation_common.json'),canonical(m),time.time()))
            # Evaluation resets simulation and storage. Restore training-only
            # RNG and learner state from a checkpoint, then apply the same config.
            return panel,m
        commit('entry')
        target=trial['target'];last_full=start_progress;last_light=start_progress;latest=None
        while start_progress+runner.total_updates-lineage_start<target:
            if runner.stop_requested or (store.base/'STOP').exists():raise GracefulStop('USER_STOP')
            progress=start_progress+runner.total_updates-lineage_start
            if __import__('shutil').disk_usage(out).free<4*1024**3:raise RuntimeError('DISK_FREE_BELOW_4_GIB')
            n=min(options['monitor']['save_interval'],target-progress,
                  250-(progress-last_light),500-(progress-last_full))
            runner.current_learning_iteration=runner.total_updates;runner.learn(n,init_at_random_ep_len=False)
            progress=start_progress+runner.total_updates-lineage_start;cp=commit('checkpoint')
            final=progress==target;full=final or progress-last_full>=500
            if full or progress-last_light>=250:
                panel,m=physical(progress,full,final);last_light=progress
                if full:
                    last_full=progress
                    previous_ok=config['stage']==0 or qualified(panel,config['stage']-1,options['thresholds'])
                    CheckpointBank(store).register(cp,m,trial_id,panel=panel,options=options,extra=dict(
                        parent_checkpoint=trial['source'],restoration_mode=mode,resumed_from=source,
                        trial_progress=progress,generation=trial['generation'],seed=config['seed'],
                        reproducible_config=config,attempt=attempt_id,prior_stage_qualified=previous_ok))
                    reference=store.get('best_metrics')
                    if not smoke and reference and reference['protocol']==m['protocol'] and RecoveryManager.diagnose(m,reference)=='POLICY_REGRESSION':
                        result.update(status='REJECTED',diagnosis='POLICY_REGRESSION')
                latest=(panel,m,cp)
                if not continuation_safe(m):
                    result.update(status='REJECTED',diagnosis='SEVERE_PHYSICAL_REGRESSION')
                if result['status']=='REJECTED':break
                if (store.base/'STOP').exists():raise GracefulStop('USER_STOP')
        if latest is None:
            progress=start_progress+runner.total_updates-lineage_start;cp=commit('final')
            panel,m=physical(progress,True,True);latest=(panel,m,cp)
        panel,m,cp=latest
        # Independent confirmation for near-ties and potential qualification.
        reference=store.get('best_metrics')
        close=reference is not None and abs(score(m)-score(reference))<.08
        if not smoke and (close or qualified(panel,config['stage'],options['thresholds'])):
            confirm=evaluate(runner,out/'confirmation',full=True,seeds=[2027,4099],raw=True)
            panel=dict(panel,rows=panel['rows']+confirm['rows'],seeds=panel['seeds']+confirm['seeds'])
            m=metrics(panel,config['stage']);atomic_json(out/'confirmed_panel.json',panel)
        if smoke or trial['rung']>=1 or (reference is not None and score(m)>score(reference)+.02):
            from ..locomotion.curriculum_v6_3.evaluation import video
            # Reuse video renderer, but instrument the new observer for overlay.
            from ..locomotion.curriculum_v6_3 import evaluation as old
            saved=old.observe;old.observe=__import__('dogfight.autoppo.stride',fromlist=['observe']).observe
            try:video(runner,out/('smoke_gait.mp4' if smoke else 'candidate_gait.mp4'),'AutoPPO '+trial_id)
            finally:old.observe=saved
        if result['status']=='FAILED':result['status']='COMPLETE'
        result.update(checkpoint=str(cp),metrics=m,panel=panel,progress=store.rows('SELECT progress FROM trials WHERE id=?',(trial_id,))[0]['progress'])
    except BaseException as exc:
        traceback.print_exc()
        is_stop=type(exc).__name__=='GracefulStop' and str(exc).startswith('USER_')
        result.update(status='INTERRUPTED' if is_stop else 'FAILED',error=repr(exc))
        if runner is not None:
            try:
                cp=commit('interrupted');result.update(checkpoint=str(cp),progress=start_progress+runner.total_updates-lineage_start)
            except Exception as save_error:result['save_error']=repr(save_error)
    finally:
        try:
            from .plots import ppo_curves
            ppo_curves(out)
        except Exception as plot_error:result['plot_error']=repr(plot_error)
        result['wall_seconds']=time.monotonic()-started
        atomic_json(out/'result.json',result)
        with store.transaction():
            store.db.execute('UPDATE attempts SET end=?,status=?,wall_seconds=? WHERE id=?',(time.time(),result['status'],result['wall_seconds'],attempt_id))
            store.event('WORKER_EXIT',trial_id,attempt=attempt_id,status=result['status'],error=result.get('error'))
        if runner is not None and runner.writer:runner.writer.close()
        if env is not None:env.close()
        if app is not None:app.close(wait_for_replicator=False,skip_cleanup=True)
        gpu_lock.close();store.close()
    return 0 if result['status'] in ('COMPLETE','INTERRUPTED','REJECTED') else 1
