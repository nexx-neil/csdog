"""Independent deterministic V6 evaluation; accepts only complete V6 learner checkpoints."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--num-envs',type=int,default=256);p.add_argument('--headless',action='store_true');p.add_argument('--video',action='store_true');a=p.parse_args()
    if a.output_dir.exists():p.error('Output directory exists')
    if a.num_envs<16 or a.num_envs%16:p.error('--num-envs must be divisible by 16')
    import torch
    data=torch.load(a.checkpoint,map_location='cpu',weights_only=False);meta=(data.get('infos') or {}).get('curriculum_v6')
    if not meta:p.error('Full V6 checkpoint required')
    a.output_dir.mkdir(parents=True)
    import fcntl
    lock_path=ROOT/'runs/locomotion/csdog_curriculum_v6/gpu.lock';lock_path.parent.mkdir(parents=True,exist_ok=True)
    gpu_lock=lock_path.open('a');fcntl.flock(gpu_lock,fcntl.LOCK_EX)
    from isaaclab.app import AppLauncher
    app=AppLauncher(headless=a.headless,enable_cameras=a.video).app
    env=None;runner=None
    try:
        import gymnasium as gym
        from dogfight.locomotion.curriculum_v6.config import build
        from dogfight.locomotion.curriculum_v6.runner import Runner,Wrapper
        from dogfight.locomotion.curriculum_v6.supervisor import Supervisor,atomic_json,assess
        from dogfight.locomotion.curriculum_v6.evaluation import evaluate
        cfg,agent=build(meta['options'],a.num_envs,42,'cuda:0')
        env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg,render_mode='rgb_array' if a.video else None)
        supervisor=Supervisor(a.output_dir,meta['options'],meta['state'])
        runner=Runner(Wrapper(env,clip_actions=None),agent.to_dict(),device='cuda:0',log_dir=None,supervisor=supervisor)
        runner.restore(a.checkpoint);runner.apply()
        summary=evaluate(runner,a.output_dir,full=True,tag='independent')
        atomic_json(a.output_dir/'acceptance.json',assess(summary,3,meta['options']['thresholds']))
        if a.video:
            cfg.episode_length_s=60.
            import imageio.v2 as imageio
            from dogfight.locomotion.spot_v4.evaluation import rollout
            sequence=[(.18,0),(0,0),(-.18,0),(0,0),(0,.3),(0,-.3),(.18,.3),(.18,-.3),(-.18,.3),(-.18,-.3),(0,0)]
            commands=torch.zeros(len(sequence),a.num_envs,3,device='cuda:0')
            for k,(x,z) in enumerate(sequence):commands[k,:,0]=x;commands[k,:,2]=z
            with imageio.get_writer(a.output_dir/'all_directions.mp4',fps=25) as writer:
                rollout(runner.env,runner.get_inference_policy(),commands,2.*len(sequence),137,writer=writer,title='CSDog V6 deterministic PPO')
        atomic_json(a.output_dir/'provenance.json',dict(checkpoint=str(a.checkpoint.resolve()),updates=runner.total_updates,simulation_reset=True,actor='deterministic',root_velocity_override=False))
    finally:
        if env is not None:env.close()
        app.close(wait_for_replicator=False,skip_cleanup=True)
if __name__=='__main__':main()
