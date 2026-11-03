"""Simulated search/recovery tests. No Isaac app or GPU is started."""
import copy,json,hashlib,os,subprocess,sys
from pathlib import Path
import pytest
from dogfight.autoppo.storage import Store,canonical,atomic_json
from dogfight.autoppo.config import default_options
from dogfight.autoppo.search_optimizer import SearchOptimizer
from dogfight.autoppo.motion_evaluator import score,pareto,qualified,safe
from dogfight.autoppo.recovery_manager import RecoveryManager
from dogfight.autoppo.experiment_manager import ExperimentManager
from dogfight.autoppo.checkpoint_bank import inspect_checkpoint,CheckpointBank

def measurement(**kwargs):
    d=dict(forward_velocity=.18,tracking=.9,tracking_error=.02,complete_stride_count=[2,2,2,2],
        min_complete_per_trial=2.,gait_fraction=.8,touchdown_count=12,stable_support_seconds=1,
        support_slip=.06,stop_linear_speed=.02,stop_yaw_rate=.05,fall_rate=0,illegal_contact=0,
        rejection_counts={},protocol='test-500hz',seeds=[103,307],seconds=12)
    return dict(d,**kwargs)

def candidate():
    return dict(options=default_options(),num_envs=256,seed=42,stage=0,speed_range=[.12,.25],
                stop_fraction=.15,restore_mode='weights',source_sha256='abc',mutation=None)

def test_search_dedup_restore_and_queue(tmp_path):
    s=Store(tmp_path);search=SearchOptimizer(s)
    donors=[dict(path='/read-only/history.pt',sha256='abc',options=default_options())]
    ids=search.generate(1,0,donors,'NO_VALID_STRIDE');assert len(ids)==12
    rows=s.rows('SELECT * FROM trials');assert len({r['hash'] for r in rows})==12
    c=json.loads(rows[0]['config']);assert s.add_trial(c,1,0,250,donors[0]['path'],rows[0]['hash']) is None
    first,attempt=s.claim();assert first['id']==ids[0]
    assert s.rows('SELECT status FROM trials WHERE id=?',(ids[0],))[0]['status']=='RUNNING'
    s.close();s=Store(tmp_path);s.repair_orphans()
    assert s.rows('SELECT status FROM trials WHERE id=?',(ids[0],))[0]['status']=='QUEUED'
    assert s.get('stage',0)==0
    s.close()

def test_atomic_transaction_rollback(tmp_path):
    s=Store(tmp_path)
    with pytest.raises(RuntimeError):
        with s.transaction():s.set('stage',3);raise RuntimeError('simulated power loss')
    assert s.get('stage') is None
    path=tmp_path/'status.json';atomic_json(path,{'old':1});(tmp_path/'.status.json.tmp').write_text('{')
    assert json.loads(path.read_text())=={'old':1}
    atomic_json(path,{'new':2});assert json.loads(path.read_text())=={'new':2}

def test_safety_and_pareto():
    a=measurement();bad=measurement(forward_velocity=.5,fall_rate=.8)
    assert safe(a) and not safe(bad);assert score(a)>score(bad)
    slide=measurement(support_slip=.3,complete_stride_count=[0]*4,gait_fraction=0,min_complete_per_trial=0)
    still=measurement(forward_velocity=0,tracking=0,gait_fraction=0,min_complete_per_trial=0,complete_stride_count=[0]*4)
    assert score(a)>score(slide) and score(a)>score(still)
    low_slip=measurement(support_slip=.01,stop_yaw_rate=.5)
    assert len(pareto([{'metrics':a},{'metrics':low_slip}]))==2
    # Seed repetition cannot improve normalized score.
    b=copy.deepcopy(a);b['complete_stride_count']=[4]*4;b['seeds']=[103,307,911,1301]
    assert score(a)==score(b)

def test_immutable_bounds(tmp_path):
    search=SearchOptimizer(Store(tmp_path));search.validate(candidate())
    for key,value in [('limits',0),('progress',0),('physical_slip',0)]:
        c=candidate();c['options']['weights'][key]=value
        with pytest.raises(ValueError):search.validate(c)
    c=candidate();c['options']['thresholds']['stop_speed']=.3
    with pytest.raises(ValueError):search.validate(c)
    c=candidate();c['options']['ppo']['lam']=.99
    with pytest.raises(ValueError):search.validate(c)

def test_failure_classification():
    assert RecoveryManager.process_failure('CUDA out of memory')=='GPU_OOM'
    assert RecoveryManager.process_failure('NONFINITE_PPO NaN')=='NUMERICAL_INSTABILITY'
    assert RecoveryManager.process_failure('Identity mismatch')=='CHECKPOINT_INCOMPATIBLE'
    assert RecoveryManager.diagnose(measurement(forward_velocity=0))=='STANDING_LOCAL_OPTIMUM'
    assert RecoveryManager.diagnose(measurement(stop_yaw_rate=.4))=='STOP_DRIFT'
    assert RecoveryManager.diagnose(measurement(complete_stride_count=[0]*4,rejection_counts={'INSUFFICIENT_SUPPORT':100}))=='INSUFFICIENT_SUPPORT'

def test_exclusive_lock_and_child_inheritance(tmp_path):
    a=ExperimentManager(tmp_path);a.acquire();b=ExperimentManager(tmp_path)
    with pytest.raises(RuntimeError):b.acquire()
    # A worker inherits the same lock; parent exit/restart cannot overlap it.
    child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(.3)'],pass_fds=(a.lock.fileno(),))
    a.lock.close()
    c=ExperimentManager(tmp_path)
    with pytest.raises(RuntimeError):c.acquire()
    child.wait();c.acquire();c.lock.close()

@pytest.fixture
def checkpoint(tmp_path):
    import torch
    from dogfight.locomotion.spot_v4.contracts import IDENTITY
    model={'std':torch.ones(12)*.4}
    for side,final in [('actor',12),('critic',1)]:
        sizes=[48,512,256,128,final]
        for i in range(4):model[f'{side}.{i*2}.weight']=torch.zeros(sizes[i+1],sizes[i]);model[f'{side}.{i*2}.bias']=torch.zeros(sizes[i+1])
    meta=dict(identity=IDENTITY,state=dict(stage=0,total_updates=10,environment_steps=61440,training_seconds=2),options=default_options(),learning_rate=.0001)
    p=tmp_path/'valid.pt';torch.save(dict(model_state_dict=model,optimizer_state_dict={'state':{},'param_groups':[{}]},infos={'curriculum_v6':meta}),p)
    return p

def test_torn_checkpoint_and_bank_preservation(tmp_path,checkpoint):
    partial=tmp_path/'partial.pt';partial.write_bytes(checkpoint.read_bytes()[:128])
    with pytest.raises(Exception):inspect_checkpoint(partial)
    s=Store(tmp_path/'lab');bank=CheckpointBank(s)
    before=checkpoint.read_bytes();a=bank.register(checkpoint,measurement())
    assert checkpoint.read_bytes()==before
    assert Path(a['path']).read_bytes()==before
    assert set(bank.names())=={'best_forward','best_gait','best_low_slip','best_stop','best_balanced'}
    assert 'best_stage_qualified' not in bank.names()
    b=bank.register(checkpoint,measurement(support_slip=.2))
    assert a['path']!=b['path'] and Path(a['path']).exists()

def test_nan_and_wrong_dimensions_rejected(tmp_path,checkpoint):
    import torch
    d=torch.load(checkpoint,weights_only=False);d['model_state_dict']['std'][0]=float('nan');torch.save(d,tmp_path/'nan.pt')
    with pytest.raises(ValueError):inspect_checkpoint(tmp_path/'nan.pt')
    d=torch.load(checkpoint,weights_only=False);d['model_state_dict']['actor.0.weight']=torch.zeros(512,47);torch.save(d,tmp_path/'wrong.pt')
    with pytest.raises(ValueError):inspect_checkpoint(tmp_path/'wrong.pt')

def test_halving_and_finite_stagnation(tmp_path):
    m=ExperimentManager(tmp_path);s=m.store;s.set('generation',1);s.set('stage',0);s.set('best_metrics',measurement());s.set('batch_start_score',score(measurement()));s.set('generation_stage',0)
    for i in range(12):
        c=candidate();c['seed']=i;trial=s.add_trial(c,1,0,250,'/read-only.pt',str(i))
        value=measurement(support_slip=.05+i*.01)
        s.db.execute("UPDATE trials SET status='COMPLETE',progress=250,metrics=?,score=? WHERE id=?",(canonical(value),score(value),trial))
    assert m.finish_rung()
    assert len(s.rows("SELECT * FROM trials WHERE status='QUEUED'"))==4
    s.db.execute("UPDATE trials SET status='COMPLETE',progress=target WHERE status='QUEUED'")
    assert m.finish_rung();assert len(s.rows("SELECT * FROM trials WHERE status='QUEUED'"))==2
    s.db.execute("UPDATE trials SET status='COMPLETE',progress=target WHERE status='QUEUED'")
    s.set('stagnant_batches',2)
    assert not m.finish_rung();assert s.get('status')=='BLOCKED_NEEDS_REDESIGN'
    assert (tmp_path/'reports/BLOCKED.md').exists()

def test_oom_and_nan_recovery_are_bounded(tmp_path):
    m=ExperimentManager(tmp_path);s=m.store
    c=candidate();trial=s.add_trial(c,1,0,250,'/read-only.pt','first');row,attempt=s.claim()
    m.adopt_result(row,attempt,dict(status='FAILED',error='CUDA out of memory'))
    rows=s.rows('SELECT * FROM trials');assert len(rows)==2
    lower=next(r for r in rows if r['id']!=trial)
    assert json.loads(lower['config'])['num_envs']==128 and lower['target']==500
    row,attempt=s.claim();m.adopt_result(row,attempt,dict(status='FAILED',error='NONFINITE_PPO'))
    assert not s.rows("SELECT id FROM trials WHERE status='QUEUED'")


def test_later_generation_does_not_repeat_failed_baseline(tmp_path):
    s=Store(tmp_path);search=SearchOptimizer(s)
    donors=[dict(path='/history.pt',sha256='same',options=default_options())]
    first=search.generate(1,0,donors);second=search.generate(2,0,donors)
    assert len(first)==len(second)==12
    assert len(s.rows('SELECT id FROM trials'))==24


def test_no_infinite_oom_at_minimum_envs(tmp_path):
    m=ExperimentManager(tmp_path);s=m.store;c=candidate();c['num_envs']=64
    s.add_trial(c,1,0,1000,'/history.pt','at_min');row,attempt=s.claim()
    m.adopt_result(row,attempt,dict(status='FAILED',error='CUDA out of memory'))
    assert len(s.rows('SELECT id FROM trials'))==1
    assert not s.rows("SELECT id FROM trials WHERE status='QUEUED'")


def test_restart_falls_back_from_torn_latest(tmp_path,checkpoint):
    m=ExperimentManager(tmp_path/'lab');s=m.store;c=candidate()
    trial=s.add_trial(c,1,0,250,str(checkpoint),'one')
    partial=tmp_path/'broken.pt';partial.write_bytes(b'incomplete')
    s.db.execute('UPDATE trials SET progress=20,checkpoint=? WHERE id=?',(str(partial),trial))
    s.event('CHECKPOINT_COMMITTED',trial,checkpoint=str(checkpoint),progress=10,lineage_updates=10)
    m.reconcile_checkpoints()
    row=s.rows('SELECT progress,checkpoint FROM trials WHERE id=?',(trial,))[0]
    assert row['progress']==10 and row['checkpoint']==str(checkpoint)
    assert partial.exists() and checkpoint.exists()


def test_moving_unqualified_anchor_beats_zero_motion():
    moving=measurement(forward_velocity=.248,tracking=.98,gait_fraction=0,
        complete_stride_count=[0]*4,min_complete_per_trial=0,touchdown_count=0,
        stable_support_seconds=0,support_slip=.096,stop_linear_speed=.084,stop_yaw_rate=.352)
    standing=measurement(forward_velocity=0,tracking=0,gait_fraction=0,
        complete_stride_count=[0]*4,min_complete_per_trial=0,touchdown_count=0,
        stable_support_seconds=0,support_slip=0,stop_linear_speed=0,stop_yaw_rate=0)
    assert score(moving)>score(standing)
    assert not safe(measurement(fall_rate=.06))


def passing_panel(seeds=None):
    from dogfight.autoppo.stride import PROTOCOL
    base=dict(is_stop=False,valid=True,fall_rate=0.,velocity=[.18,0,0],yaw=0.,yaw_abs=.01,
        speed_xy=.18,lateral_speed=0.,tilt=.02,support_slip_speed=.02,tracking_ratios=[1.],
        pure_yaw=False,periodic_legs=4,gait_trial_fraction=1.,complete_stride_ratio=1.,
        complete_stride_legs=4,illegal_shank_fraction=0.,replicates=16,
        **{leg+'_swing_ratio':.1 for leg in ['LF','RF','LR','RR']})
    stop=dict(base,test='stop',is_stop=True,speed_xy=.01,yaw_abs=.02,tracking_ratios=[])
    return dict(full=True,protocol=PROTOCOL,seeds=seeds or [103,307],seconds=12,
                rows=[dict(base,test='forward'),stop])

def test_curriculum_requires_repeated_independent_evidence(tmp_path):
    from dogfight.autoppo.curriculum_manager import CurriculumManager
    s=Store(tmp_path);s.set('stage',0);c=CurriculumManager(s,default_options()['thresholds'])
    panel=passing_panel()
    assert not c.observe(panel,'one.pt')
    assert not c.observe(panel,'one.pt')
    assert len(s.get('qualification_0'))==1
    assert not c.observe(panel,'two.pt')
    assert c.observe(passing_panel([2027,4099]),'three.pt')
    assert s.get('stage')==1
    assert not qualified(panel,1,default_options()['thresholds'])

def test_resume_partially_created_search_batch(tmp_path):
    m=ExperimentManager(tmp_path);s=m.store
    donor=dict(path='/history.pt',sha256='same',options=default_options())
    m.donors=lambda:[donor]
    s.set('generation',1);s.set('generation_stage',0);s.set('stage',0);s.set('generation_building',True)
    m.search.generate(1,0,[donor],count=1)
    first=s.rows('SELECT id FROM trials')[0]['id']
    m.complete_generation()
    assert len(s.rows('SELECT id FROM trials'))==12
    assert s.rows('SELECT id FROM trials WHERE id=?',(first,))
    assert not s.get('generation_building')


def test_worker_has_no_undefined_global_names():
    # Statically inspect the production worker without importing Isaac Sim.
    # This catches metadata/exception paths that a two-update run may not reach.
    import symtable,builtins
    from dogfight.autoppo.config import ROOT
    path=ROOT/'src/dogfight/autoppo/train_runner.py'
    table=symtable.symtable(path.read_text(),str(path),'exec')
    module_names={s.get_name() for s in table.get_symbols() if s.is_assigned() or s.is_imported()}
    worker=next(c for c in table.get_children() if c.get_name()=='worker')
    globals_used={s.get_name() for s in worker.get_symbols() if s.is_global() and s.is_referenced()}
    assert not globals_used-module_names-set(dir(builtins))
