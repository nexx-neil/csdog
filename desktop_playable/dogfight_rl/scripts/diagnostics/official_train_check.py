"""Run the unmodified NVIDIA trainer for exactly one new-task PPO update."""
from pathlib import Path
import os,sys,runpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
import dogfight.locomotion
out=ROOT/'runs/locomotion/csdog_ppo_20261026/official_validation'
out.mkdir(exist_ok=False);os.chdir(out)
script=ROOT.parent/'IsaacLab/scripts/reinforcement_learning/rsl_rl/train.py'
sys.path.insert(0,str(script.parent));sys.argv=[str(script),'--task','Dogfight-CSDog-Velocity-Flat-v0','--num_envs','16','--max_iterations','1','--headless','--device','cuda:0']
runpy.run_path(str(script),run_name='__main__')
