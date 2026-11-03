"""Locked, stage-limited 230-update / 1200-second ledger, independent of all older budgets."""
import json,fcntl,time,os
class Budget:
 caps={'smoke':5,'first':120,'second':100,'validation':5}
 def __init__(self,root,name,updates):
  self.path=root/'training_budget.json';self.lock=(root/'training_budget.lock').open('a')
  fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB);self.started=time.monotonic();self.completed=0
  self.data=json.loads(self.path.read_text()) if self.path.exists() else dict(max_updates=230,max_seconds=1200,runs=[])
  if any(x['status']=='RUNNING' for x in self.data['runs']):raise RuntimeError('Unfinished reservation requires audit, no automatic restart')
  used=sum(x['completed_updates'] for x in self.data['runs']);elapsed=sum(x['seconds'] for x in self.data['runs'])
  stage_used=sum(x['completed_updates'] for x in self.data['runs'] if x['name']==name)
  if name not in self.caps or updates<1 or updates+stage_used>self.caps[name] or used+updates>230 or elapsed>=1200:raise RuntimeError('V3 training budget exceeded')
  self.allowed_seconds=1200-elapsed;self.row=dict(name=name,reserved_updates=updates,completed_updates=0,seconds=0.,status='RUNNING');self.data['runs'].append(self.row);self.save()
 def save(self):
  p=self.path.with_suffix('.tmp');p.write_text(json.dumps(self.data,indent=2));os.replace(p,self.path)
 def update(self):
  if self.completed>=self.row['reserved_updates']:raise RuntimeError('Reserved PPO updates exhausted')
  self.completed+=1;self.row.update(completed_updates=self.completed,seconds=time.monotonic()-self.started);self.save()
 def expired(self):return time.monotonic()-self.started>=self.allowed_seconds
 def close(self,status):
  self.row.update(status=status,completed_updates=self.completed,seconds=time.monotonic()-self.started);self.save()
  fcntl.flock(self.lock,fcntl.LOCK_UN);self.lock.close()
