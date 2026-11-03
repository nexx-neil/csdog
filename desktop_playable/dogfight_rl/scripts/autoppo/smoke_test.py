"""Two short real GPU jobs, followed by exact resume with changed entropy.

This is validation only, not a search batch or a claim of learned motion.
"""
from pathlib import Path
import argparse,sys,json,copy,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from dogfight.autoppo.config import BASE,default_options
from dogfight.autoppo.experiment_manager import ExperimentManager
from dogfight.autoppo.storage import canonical,atomic_json
from dogfight.autoppo.checkpoint_bank import sha256

def main():
    p=argparse.ArgumentParser();p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    manager=ExperimentManager(a.output);manager.acquire();results=[]
    try:
        options=default_options()
        config=dict(options=options,num_envs=256,seed=42,stage=0,speed_range=[.12,.25],stop_fraction=.15,
                    restore_mode='weights',source_sha256=sha256(a.checkpoint),mutation=None)
        manager.search.validate(config)
        trial_id=manager.store.add_trial(config,0,0,2,a.checkpoint,hashlib.sha256(canonical(config).encode()).hexdigest())
        trial,attempt=manager.store.claim();result=manager.run_child(trial,attempt,smoke=True)
        manager.adopt_result(trial,attempt,result);results.append(result)
        if result['status']!='COMPLETE' or result['progress']!=2:raise RuntimeError('First PPO smoke failed: '+str(result.get('error')))
        # Resume the exact new full learner, then apply a bounded entropy change.
        # This is explicitly a full learner continuation with a hyperparameter
        # change; reward and observations remain identical.
        config=copy.deepcopy(config);config['restore_mode']='full';config['options']['ppo']['entropy_coef']=.004
        config['source_sha256']=sha256(result['checkpoint'])
        config['mutation']=dict(group='ppo',key='entropy_coef',before=.0025,reason='resume interface smoke')
        manager.search.validate(config)
        trial_id=manager.store.add_trial(config,0,0,2,result['checkpoint'],hashlib.sha256(canonical(config).encode()).hexdigest())
        trial,attempt=manager.store.claim();result=manager.run_child(trial,attempt,smoke=True)
        manager.adopt_result(trial,attempt,result);results.append(result)
        if result['status']!='COMPLETE' or result['progress']!=2:raise RuntimeError('Second PPO smoke failed: '+str(result.get('error')))
        atomic_json(a.output/'SMOKE_PASS.json',dict(status='PASS',new_updates=4,sequential_jobs=2,
            full_learner_restore_verified=True,changed_entropy=.004,
            checkpoints=[r['checkpoint'] for r in results],evaluations=[r['metrics'] for r in results]))
        manager.report()
    finally:manager.store.close();manager.lock.close()
if __name__=='__main__':main()
