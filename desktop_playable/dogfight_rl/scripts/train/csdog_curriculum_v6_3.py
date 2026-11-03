"""Matched V6.3 arms or capability-gated unlimited continuation, native RSL-RL PPO."""
from pathlib import Path
import sys,copy,json,argparse,fcntl,signal,os,time,traceback,hashlib,random
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
BASE=ROOT/'runs/locomotion/csdog_curriculum_ppo_v6_3'
def equal(x,y):
    import torch
    if torch.is_tensor(x):return torch.equal(x.cpu(),y.cpu())
    if isinstance(x,dict):return x.keys()==y.keys() and all(equal(x[k],y[k]) for k in x)
    if isinstance(x,(list,tuple)):return len(x)==len(y) and all(equal(a,b) for a,b in zip(x,y))
    return x==y

def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['arm','long'],required=True);p.add_argument('--arm',choices=['A','B'],default='B');p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--smoke',action='store_true')
    a=p.parse_args();out=a.output.resolve()
    if out.exists():raise FileExistsError('Refusing overwrite: '+str(out))
    if a.mode=='arm' and not (BASE/'reports/V6_3_HISTORICAL_GAIT_ANALYSIS.md').exists():raise RuntimeError('Historical physical analysis required')
    if not (BASE/'reports/TESTS_PASSED.json').exists():raise RuntimeError('Timing and adversarial tests required')
    if a.mode=='long' and not json.loads((BASE/'CONTINUATION_GATE.json').read_text()).get('allowed'):raise RuntimeError('V6.3 continuation gate rejected')
    import torch,numpy as np
    torch.set_num_threads(4);torch.manual_seed(42);np.random.seed(42);random.seed(42)
    from dogfight.locomotion.curriculum_v6_3.supervisor import Supervisor,atomic_json
    source=torch.load(a.checkpoint,map_location='cpu',weights_only=False);meta=source['infos']['curriculum_v6']
    # Load all runtime imports only after AppLauncher.
    from isaaclab.app import AppLauncher
    lock=(ROOT/'runs/locomotion/csdog_curriculum_v6/gpu.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    app=AppLauncher(headless=True,enable_cameras=True).app;env=None;runner=None
    out.mkdir(parents=True);(out/'pid').write_text(str(os.getpid()))
    options=None;supervisor=None
    try:
        import gymnasium as gym
        from isaaclab.utils.io import dump_yaml
        from dogfight.locomotion.curriculum_v6_3.config import build,options_from
        from dogfight.locomotion.curriculum_v6_3.runner import Runner,Wrapper,GracefulStop
        from dogfight.locomotion.curriculum_v6_3.evaluation import evaluate,brief,video
        from dogfight.locomotion.spot_v4.runtime import preflight
        options=copy.deepcopy(meta['options']) if a.mode=='long' and meta['options'].get('schema')==6.3 else options_from(meta['options'],a.arm)
        supervisor=Supervisor(out,options)
        cfg,agent=build(options,256,42,'cuda:0');cfg.viewer.resolution=(960,640)
        # The preserved V6.2 early-swing observer uses inference_mode internally.
        # Delay its first call until Isaac Lab has allocated mutable reset caches.
        # The formal training weight is restored before Wrapper/Runner creation.
        delayed_guide=float(cfg.rewards.gait_guide.weight)
        if delayed_guide:cfg.rewards.gait_guide.weight=0.
        env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg,render_mode='rgb_array');atomic_json(out/'preflight.json',preflight(env))
        if delayed_guide:
            term=env.unwrapped.reward_manager.get_term_cfg('gait_guide');term.weight=delayed_guide;env.unwrapped.reward_manager.set_term_cfg('gait_guide',term)
            cfg.rewards.gait_guide.weight=delayed_guide
        runner=Runner(Wrapper(env,clip_actions=None),agent.to_dict(),device='cuda:0',log_dir=str(out/'TensorBoard'),supervisor=supervisor)
        runner.restore(a.checkpoint)
        if a.mode=='arm':
            supervisor.options=copy.deepcopy(options);supervisor.state['weights']=copy.deepcopy(options['weights']);supervisor.state['ppo']=copy.deepcopy(options['ppo']);supervisor.state['distribution']=None
        assert equal(source['model_state_dict'],runner.alg.policy.state_dict()),'Actor/critic/std restoration differs'
        assert equal(source['optimizer_state_dict'],runner.alg.optimizer.state_dict()),'Optimizer restoration differs'
        runner.apply();supervisor.state.update(seed=42,num_envs=256,training_status='RUNNING')
        start=runner.total_updates
        atomic_json(out/'launch.json',dict(mode=a.mode,arm=a.arm,source=str(a.checkpoint),source_sha256=hashlib.sha256(a.checkpoint.read_bytes()).hexdigest(),budget=(2 if a.smoke else 300) if a.mode=='arm' else None,start_update=start,num_envs=256,seed=42,policy_exact=True,optimizer_exact=True,restore_mode='full learner with optimizer and RNG; physics reset',initial_lr=runner.alg.learning_rate,smoke=a.smoke))
        files=list((ROOT/'src/dogfight/locomotion/curriculum_v6_3').glob('*.py'))+[Path(__file__)]
        atomic_json(out/'source_sha256.json',{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files})
        dump_yaml(str(out/'env.yaml'),cfg);dump_yaml(str(out/'agent.yaml'),agent)
        def stop(sig,frame):runner.stop_requested='USER_SIGNAL_'+str(sig)
        signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
        runner.save(str(out/'initial.pt'))
        def evaluate_at(n,seeds=None,raw=False):
            summary=evaluate(runner,out/f'eval_{n:06d}',full=True,tag='common',seeds=seeds or [103,307,911,1301],raw=raw)
            supervisor.state['last_evaluation']=summary;supervisor.publish(summary);return summary
        baseline=evaluate_at(0,seeds=[103] if a.smoke else None)
        if a.mode=='arm':
            runner.restore(a.checkpoint);supervisor.options=copy.deepcopy(options);supervisor.state['weights']=copy.deepcopy(options['weights']);supervisor.state['ppo']=copy.deepcopy(options['ppo']);supervisor.state['distribution']=None;runner.apply()
            # The second exact restore reinstates the historical V6 Supervisor
            # payload. Keep the newly measured V6.3 baseline for status fields.
            supervisor.state['last_evaluation']=baseline
            for n in ([2] if a.smoke else [50,100,200,300]):
                if (out/'STOP').exists() or runner.stop_requested:raise GracefulStop('USER_STOP')
                runner.current_learning_iteration=runner.total_updates
                runner.learn(n-(runner.total_updates-start),init_at_random_ep_len=False)
                runner.save(str(out/f'additional_{n:03d}.pt'))
                summary=evaluate_at(n,seeds=[103] if a.smoke else None,raw=(n==300 and not a.smoke))
                f=[r for r in summary['rows'] if r['test']=='forward']
                if max(r['fall_rate'] for r in f)>.15 or min(r['velocity'][0] for r in f)<0:raise RuntimeError('SEVERE_PHYSICAL_REGRESSION')
            if not a.smoke:
                evaluate_at(301,seeds=[2027,4099],raw=True)
                video(runner,out/'final_gait.mp4','V6.3 '+a.arm+' +300')
            supervisor.state['training_status']='EXPERIMENT_COMPLETE';runner.save(str(out/'final.pt'))
        else:
            supervisor.register(baseline,str(out/'initial.pt'));last_full=runner.total_updates;last_light=runner.total_updates
            while True:
                if (out/'STOP').exists() or runner.stop_requested:raise GracefulStop('USER_STOP')
                import shutil
                if shutil.disk_usage(out).free<4*1024**3:raise RuntimeError('DISK_FREE_BELOW_4_GIB')
                m=supervisor.options['monitor'];candidate=supervisor.state['candidate']
                n=min(m['save_interval'],m['light_interval']-(runner.total_updates-last_light),m['full_interval']-(runner.total_updates-last_full))
                if candidate:n=min(n,m['candidate_updates']-(runner.total_updates-candidate['start_update']))
                runner.current_learning_iteration=runner.total_updates;runner.learn(n,init_at_random_ep_len=False)
                full=runner.total_updates-last_full>=m['full_interval'] or bool(candidate and runner.total_updates-candidate['start_update']>=m['candidate_updates'])
                if full or runner.total_updates-last_light>=m['light_interval']:
                    summary=evaluate(runner,out/f'eval_{runner.total_updates}',full=full,tag='common',seeds=candidate['evaluation_seeds'] if candidate else [103,307,911,1301]);last_light=runner.total_updates
                    supervisor.state['last_evaluation']=summary
                    if full:
                        last_full=runner.total_updates;cp=out/f'evaluated_{runner.total_updates:08d}.pt';runner.save(str(cp))
                        decision=supervisor.observe(summary,str(cp));runner.save(str(cp));action=decision['action']
                        if action in ['rollback','candidate_control','candidate_adjust']:
                            supervisor.event('ROLLBACK',reason=decision.get('reason',action),checkpoint=decision['checkpoint'],rejected_checkpoint=str(cp))
                            restored=runner.restore(decision['checkpoint'],restore_supervisor=False)
                            if action=='rollback':
                                for key in ['weights','ppo','distribution','speed_range','substage']:supervisor.state[key]=copy.deepcopy(restored['state'][key])
                            if action=='candidate_adjust':supervisor.adjust(decision['diagnosis'],summary)
                        runner.apply();runner.save(str(out/'latest.pt'))
                        if action=='advance':runner.save(str(out/f'stage_{supervisor.state["stage"]+1}_entry.pt'))
                        if action in ['blocked','success']:break
                    supervisor.publish(summary)
            runner.save(str(out/'final.pt'))
    except BaseException as exc:
        traceback.print_exc()
        if supervisor:
            supervisor.state.update(training_status='INTERRUPTED' if type(exc).__name__=='GracefulStop' and str(exc).startswith('USER_') else 'BLOCKED_NEEDS_REDESIGN',diagnosis=str(exc))
            supervisor.event('PROCESS_STOP',error=repr(exc))
        if runner:runner.save(str(out/'interrupted.pt'))
        atomic_json(out/'ERROR.json',dict(error=repr(exc)))
    finally:
        if supervisor:supervisor.publish()
        if runner and runner.writer:runner.writer.close()
        if env:env.close()
        app.close(wait_for_replicator=False,skip_cleanup=True)
if __name__=='__main__':main()
