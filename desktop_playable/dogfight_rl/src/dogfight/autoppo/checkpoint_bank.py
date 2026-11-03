"""Immutable full-learner snapshots and transactional logical best names."""
from pathlib import Path
import hashlib,os,shutil,time,uuid,json
from .storage import atomic_json,canonical
from .motion_evaluator import score,safe,qualified

NAMES=('best_forward','best_gait','best_low_slip','best_stop','best_balanced','best_stage_qualified')

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def inspect_checkpoint(path):
    import torch
    from ..locomotion.spot_v4.contracts import IDENTITY,finite_tree
    path=Path(path)
    if path.suffix!='.pt' or path.name.startswith('.'):raise ValueError('Uncommitted checkpoint')
    d=torch.load(path,map_location='cpu',weights_only=False)
    m=(d.get('infos') or {}).get('curriculum_v6')
    if not m or m.get('identity')!=IDENTITY:raise ValueError('Incompatible checkpoint identity')
    if not d.get('optimizer_state_dict') or not finite_tree(d):raise ValueError('Incomplete or nonfinite checkpoint')
    model=d['model_state_dict'];expected={'std':(12,)}
    for side,final in [('actor',12),('critic',1)]:
        sizes=[48,512,256,128,final]
        for i in range(4):
            expected[f'{side}.{i*2}.weight']=(sizes[i+1],sizes[i])
            expected[f'{side}.{i*2}.bias']=(sizes[i+1],)
    if set(model)!=set(expected) or any(tuple(model[k].shape)!=v for k,v in expected.items()):raise ValueError('Incompatible network dimensions')
    if not bool((model['std']>0).all()):raise ValueError('Invalid exploration std')
    return d,m

class CheckpointBank:
    def __init__(self,store):self.store=store;self.directory=store.base/'checkpoint_bank';self.directory.mkdir(exist_ok=True)
    def register(self,path,metrics,trial=None,panel=None,options=None,extra=None):
        d,m=inspect_checkpoint(path);identifier='cp_'+uuid.uuid4().hex
        target=self.directory/(identifier+'.pt');tmp=target.with_suffix('.tmp')
        digest=sha256(path)
        try:
            with Path(path).open('rb') as source,tmp.open('xb') as dest:
                shutil.copyfileobj(source,dest);dest.flush();os.fsync(dest.fileno())
            if sha256(tmp)!=digest:raise ValueError('Checkpoint changed during copy')
            os.replace(tmp,target)
            fd=os.open(target.parent,os.O_DIRECTORY)
            try:os.fsync(fd)
            finally:os.close(fd)
        finally:
            if tmp.exists():tmp.unlink()
        metadata=dict(source=str(Path(path).resolve()),trial_id=trial,options=options or m['options'],
                      learner_options=m['options'],stage=m['state']['stage'],
                      lineage_ppo_updates=m['state']['total_updates'],
                      lineage_environment_steps=m['state']['environment_steps'],
                      lineage_training_seconds=m['state']['training_seconds'],
                      learning_rate=m['learning_rate'],exploration_std=d['model_state_dict']['std'].tolist(),
                      identity=m['identity'],optimizer_state_entries=len(d['optimizer_state_dict']['state']),
                      optimizer_and_rng_in_checkpoint=True,simulation_state_restored=False,
                      evaluation_protocol=metrics['protocol'],**(extra or {}))
        atomic_json(target.with_suffix('.json'),metadata)
        with self.store.transaction():
            self.store.db.execute('INSERT INTO checkpoints VALUES(?,?,?,?,?,?,?)',
                (identifier,str(target),digest,trial,canonical(metadata),canonical(metrics),time.time()))
            self.store.event('CHECKPOINT_REGISTERED',trial,id=identifier,path=str(target),sha256=digest)
            self._rank(panel,metadata['stage'])
        return dict(id=identifier,path=str(target),sha256=digest,trial_id=trial,options=metadata['options'])
    def _rank(self,panel,stage):
        rows=self.entries(stage=stage)
        current=rows[-1]['metrics'] if rows else None
        valid=[r for r in rows if safe(r['metrics']) and r['metrics']['protocol']==current['protocol'] and (stage==0 or r['metadata'].get('prior_stage_qualified',False))]
        if not valid:return
        keys=dict(best_forward=lambda r:r['metrics']['forward_velocity'],
                  best_gait=lambda r:(r['metrics']['gait_fraction'],r['metrics'].get('min_complete_per_trial',0),r['metrics'].get('early_swing_min_per_trial',0)),
                  best_low_slip=lambda r:-r['metrics']['support_slip'],
                  best_stop=lambda r:-(r['metrics']['stop_linear_speed']/.03+r['metrics']['stop_yaw_rate']/.08),
                  best_balanced=lambda r:score(r['metrics']))
        for name,key in keys.items():
            candidate=max(valid,key=key)
            self.store.db.execute('INSERT INTO bank_names VALUES(?,?) ON CONFLICT(name) DO UPDATE SET checkpoint_id=excluded.checkpoint_id',(name,candidate['id']))
        if panel:
            # Only the currently measured candidate may be certified; never infer
            # stage qualification from a scalar score or another candidate's panel.
            if qualified(panel,stage,rows[-1]['metadata']['options']['thresholds']):
                latest=rows[-1]['id']
                for name in ['best_stage_qualified',f'best_stage_{stage+1}']:
                    self.store.db.execute('INSERT INTO bank_names VALUES(?,?) ON CONFLICT(name) DO UPDATE SET checkpoint_id=excluded.checkpoint_id',(name,latest))
    def entries(self,stage=None):
        rows=self.store.rows('SELECT * FROM checkpoints ORDER BY created')
        for r in rows:
            r['metrics']=json.loads(r['metrics']);r['metadata']=json.loads(r['metadata']);r['options']=r['metadata']['options']
        return [r for r in rows if stage is None or r['metadata']['stage']==stage]
    def names(self):
        rows=self.store.rows('SELECT b.name,c.* FROM bank_names b JOIN checkpoints c ON b.checkpoint_id=c.id')
        return {r['name']:dict(id=r['id'],path=r['path'],sha256=r['sha256'],trial_id=r['trial_id'],
                     options=json.loads(r['metadata'])['options'],config=json.loads(r['metadata']).get('reproducible_config'),stage=json.loads(r['metadata'])['stage'],prior_stage_qualified=json.loads(r['metadata']).get('prior_stage_qualified',False),metrics=json.loads(r['metrics'])) for r in rows}
