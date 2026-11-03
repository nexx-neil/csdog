"""Read-only common physical evaluation of complete V6 or V6.1 checkpoints."""
from pathlib import Path
import argparse,sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--num-envs',type=int,default=256);p.add_argument('--headless',action='store_true');p.add_argument('--video',action='store_true');p.add_argument('--raw-contact',action='store_true');p.add_argument('--contact-probe',action='store_true')
    a=p.parse_args()
    if a.output_dir.exists():p.error('Output exists')
    import torch,fcntl
    torch.set_num_threads(4)
    data=torch.load(a.checkpoint,map_location='cpu',weights_only=False);meta=data['infos']['curriculum_v6']
    lock=(ROOT/'runs/locomotion/csdog_curriculum_v6/gpu.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    a.output_dir.mkdir(parents=True)
    from isaaclab.app import AppLauncher
    app=AppLauncher(headless=a.headless,enable_cameras=a.video).app;env=None
    try:
        import gymnasium as gym
        from dogfight.locomotion.curriculum_v6.config import build
        from dogfight.locomotion.curriculum_v6.runner import Runner
        from dogfight.locomotion.curriculum_v6_1.runner import Wrapper
        from dogfight.locomotion.curriculum_v6.supervisor import Supervisor,atomic_json,assess
        from dogfight.locomotion.curriculum_v6_1.evaluation import evaluate
        options=meta['options']
        if 'gait_guide' in options['weights']:
            from dogfight.locomotion.curriculum_v6_1.config import build
            from dogfight.locomotion.curriculum_v6_1.runner import Runner
            from dogfight.locomotion.curriculum_v6_1.supervisor import Supervisor
        cfg,agent=build(options,a.num_envs,42,'cuda:0')
        if a.video:cfg.episode_length_s=60.
        env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg,render_mode='rgb_array' if a.video else None)
        supervisor=Supervisor(a.output_dir,options,meta['state'])
        runner=Runner(Wrapper(env,clip_actions=None),agent.to_dict(),device='cuda:0',log_dir=None,supervisor=supervisor)
        runner.restore(a.checkpoint);runner.apply()
        summary=evaluate(runner,a.output_dir,full=True,tag='common',raw=a.raw_contact,seeds_override=[103] if a.contact_probe else None)
        if a.contact_probe:
            summary.update(full=False,diagnostic_only=True);atomic_json(a.output_dir/'evaluation_common.json',summary)
        atomic_json(a.output_dir/'acceptance.json',assess(summary,supervisor.state['stage'],options['thresholds']))
        if a.video:
            import imageio.v2 as imageio
            from dogfight.locomotion.spot_v4.evaluation import rollout
            commands=torch.zeros(6,a.num_envs,3,device='cuda:0');commands[0:2,:,0]=.18;commands[3:5,:,0]=.25
            with imageio.get_writer(a.output_dir/'forward_stop.mp4',fps=25) as writer:
                with torch.inference_mode():rollout(runner.env,runner.get_inference_policy(),commands,12.,103,writer=writer,title='CSDog physical PPO '+a.checkpoint.name)
        atomic_json(a.output_dir/'provenance.json',dict(checkpoint=str(a.checkpoint.resolve()),updates=runner.total_updates,diagnostic_only=a.contact_probe,contact_version=summary['contact_version'],root_velocity_override=False,seeds=summary['seeds'],physics_dt=.002,control_dt=.02))
    finally:
        if env is not None:env.close()
        app.close(wait_for_replicator=False,skip_cleanup=True)
if __name__=='__main__':main()
