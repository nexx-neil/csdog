"""Pure configuration; no simulation import or environment modification."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'runs/locomotion/csdog_autoppo_lab'
PYTHON=Path('/home/zxq/miniconda3/envs/dogfight/bin/python')

def default_options():
    o=json.loads((ROOT/'configs/locomotion/curriculum_v6_1/default.json').read_text())
    o.update(schema=6.3,variant='control',initial_substage='1B',contact_validated=True)
    o['weights'].update(gait_guide=0.,swing=0.,swing_credit=1.,touchdown_credit=1.,
                        stride_credit=1.,support_quality=1.,physical_slip=-.6,stop_feedback=-1.)
    o['ppo'].update(clip_param=.2,lam=.95)
    o['monitor']['save_interval']=100
    return o
