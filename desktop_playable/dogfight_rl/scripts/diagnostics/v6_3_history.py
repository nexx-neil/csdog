from pathlib import Path
import sys,json,copy,hashlib,fcntl
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'runs/locomotion/csdog_curriculum_ppo_v6_3'
def main():
    import torch
    torch.set_num_threads(4)
    lock=(ROOT/'runs/locomotion/csdog_curriculum_v6/gpu.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    from isaaclab.app import AppLauncher
    app=AppLauncher(headless=True,enable_cameras=True).app
    import gymnasium as gym
    from dogfight.locomotion.curriculum_v6_1.config import build
    from dogfight.locomotion.curriculum_v6_1.runner import Runner,Wrapper
    from dogfight.locomotion.curriculum_v6_1.supervisor import Supervisor,atomic_json
    from dogfight.locomotion.curriculum_v6_3.evaluation import evaluate,video
    (OUT/'history').mkdir(exist_ok=True)
    inventory=json.loads((OUT/'checkpoint_inventory.json').read_text());options=copy.deepcopy(inventory[0]['options']);options.update(schema=6.1,variant='control');options['weights']['gait_guide']=0
    cfg,agent=build(options,256,42,'cuda:0');cfg.viewer.resolution=(960,640)
    env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg,render_mode='rgb_array');runner=Runner(Wrapper(env,clip_actions=None),agent.to_dict(),device='cuda:0',log_dir=None,supervisor=Supervisor(OUT/'history',options))
    try:
        for name,item in zip(['v6_2500','v62_B100','v62_B300'],inventory):
            dest=OUT/'history'/name
            if (dest/'DONE.json').exists():continue
            runner.restore(item['path']);runner.supervisor.options=copy.deepcopy(options);runner.supervisor.state['weights']=copy.deepcopy(options['weights']);runner.apply()
            evaluate(runner,dest,tag='common',seeds=[103,307,911,1301],raw=True)
            video(runner,dest/'gait.mp4',name)
            atomic_json(dest/'DONE.json',dict(status='COMPLETE',checkpoint=item['path'],no_ppo_updates=True))
            print('HISTORICAL_COMPLETE',name,flush=True)
    except BaseException:
        import traceback
        traceback.print_exc()
    finally:env.close();app.close(wait_for_replicator=False,skip_cleanup=True)
if __name__=='__main__':main()
