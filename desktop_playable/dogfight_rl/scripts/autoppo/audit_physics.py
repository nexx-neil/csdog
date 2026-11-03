"""Read-only historical policy evaluation in one Isaac Sim process."""
from pathlib import Path
import sys,json,copy,fcntl,argparse,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--seeds',nargs='+',type=int,default=[103,307,911,1301]);p.add_argument('--names',nargs='+',default=['v6_2500','v62_B100','v63_B300']);p.add_argument('--resume',action='store_true');a=p.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=a.resume)
    import torch
    torch.set_num_threads(4)
    inventory=json.loads((ROOT/'runs/locomotion/csdog_curriculum_ppo_v6_3/checkpoint_inventory.json').read_text())
    paths=dict(v6_2500=inventory[0]['path'],v62_B100=inventory[1]['path'],v63_B300=str(ROOT/'runs/locomotion/csdog_curriculum_ppo_v6_3/ab_B/final.pt'))
    from dogfight.autoppo.config import default_options
    options=default_options()
    lock=(ROOT/'runs/locomotion/csdog_curriculum_v6/gpu.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    from isaaclab.app import AppLauncher
    app=AppLauncher(headless=True,enable_cameras=True).app
    env=None
    try:
        import gymnasium as gym
        from dogfight.autoppo.runtime import build,Wrapper,Runner
        from dogfight.autoppo.evaluation import evaluate,brief
        from dogfight.locomotion.curriculum_v6_3.evaluation import evaluate as old_evaluate
        from dogfight.locomotion.curriculum_v6_1.supervisor import Supervisor,atomic_json
        from dogfight.locomotion.spot_v4.runtime import preflight
        cfg,agent=build(options,256,42,'cuda:0');cfg.viewer.resolution=(960,640)
        env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg,render_mode='rgb_array')
        atomic_json(out/'preflight.json',preflight(env))
        runner=Runner(Wrapper(env,clip_actions=None),agent.to_dict(),device='cuda:0',log_dir=None,supervisor=Supervisor(out,options))
        results=json.loads((out/'results.json').read_text()) if a.resume and (out/'results.json').exists() else {}
        from dogfight.autoppo.stride import PROTOCOL
        for name in a.names:
            if name in results:
                panel_path=out/name/'evaluation_common.json'
                panel=json.loads(panel_path.read_text())
                if panel['protocol']!=PROTOCOL or panel['seeds']!=a.seeds:raise ValueError('Cannot resume a different evaluation protocol')
                if not all((out/name/f'stride_events_seed{seed}.npz').is_file() for seed in a.seeds):raise ValueError('Completed evaluation lacks physical event records')
                print('PRESERVED_COMPLETED_EVALUATION',name,flush=True);continue
            if (out/name).exists():(out/name).rename(out/(name+'_interrupted_'+str(int(time.time()))))
            path=paths[name];runner.restore(path)
            runner.supervisor.options=copy.deepcopy(options)
            runner.supervisor.state.update(weights=copy.deepcopy(options['weights']),ppo=copy.deepcopy(options['ppo']),distribution=None)
            runner.apply()
            if name==a.names[0] and not (out/'before.json').exists():
                old=old_evaluate(runner,out/(name+'_before'),seeds=[a.seeds[0]],raw=True)
                atomic_json(out/'before.json',dict(checkpoint=path,metrics=brief(old)))
            panel=evaluate(runner,out/name,seeds=a.seeds,raw=True)
            results[name]=dict(checkpoint=path,metrics=brief(panel),protocol=panel['protocol'])
            atomic_json(out/'results.json',results)
            print('PHYSICAL_EVALUATION_COMPLETE',name,results[name]['metrics'],flush=True)
        atomic_json(out/'DONE.json',dict(status='PASS',ppo_updates=0,results=results))
    except BaseException as e:
        import traceback
        traceback.print_exc()
        (out/'ERROR.json').write_text(json.dumps(dict(error=repr(e))))
        raise
    finally:
        if env is not None:env.close()
        app.close(wait_for_replicator=False,skip_cleanup=True)
if __name__=='__main__':main()
