"""Unified deterministic V5 evaluation; optional V4 renderer is reused for videos."""
from pathlib import Path
import sys,argparse,json,hashlib
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--headless',action='store_true');p.add_argument('--seconds',type=float,default=6.)
 a=p.parse_args();out=a.output_dir.resolve();root=R/'runs/locomotion/csdog_ppo_tuning_v5'
 if not out.is_relative_to(root) or out.exists():p.error('Use a new output under the V5 runs directory')
 from dogfight.locomotion.spot_v4.contracts import validate_identity
 validate_identity(a.checkpoint)
 out.mkdir(parents=True)
 import yaml,torch,numpy as np
 torch.set_num_threads(4)
 from isaaclab.app import AppLauncher
 app=AppLauncher(headless=a.headless,device='cuda:0').app
 import gymnasium as gym
 from dogfight.locomotion.spot_v5.config import build
 from dogfight.locomotion.spot_v5.evaluation import evaluate
 from dogfight.locomotion.spot_v4.contracts import TASK
 from dogfight.locomotion.spot_v4.runtime import load_learner,preflight
 from dogfight.locomotion.spot_v5.telemetry import Wrapper
 from rsl_rl.runners import OnPolicyRunner
 cfg,agent=build(yaml.safe_load(a.config.read_text()),32,734)
 env=gym.make(TASK,cfg=cfg);preflight(env);runner=OnPolicyRunner(Wrapper(env,clip_actions=None),agent.to_dict(),device='cuda:0')
 source=load_learner(runner,a.checkpoint,weights_only=True,restore_rng=False)
 summary=evaluate(runner,out,source['source_checkpoint_updates'],a.seconds)
 (out/'provenance.json').write_text(json.dumps(dict(checkpoint=source,ppo_updates=0,config=str(a.config)),indent=2));(out/'result.json').write_text(json.dumps(dict(status='COMPLETE',ppo_updates=0),indent=2))
 env.close();app.close(wait_for_replicator=False,skip_cleanup=True)
if __name__=='__main__':main()
