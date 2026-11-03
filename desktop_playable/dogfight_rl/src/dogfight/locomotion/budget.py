"""Persistent experiment-wide 300-update / 2400-second hard budget, including smoke runs."""
from pathlib import Path
import fcntl,json,time,os
class Budget:
 def __init__(self,root,name,updates,max_seconds):
  self.root=Path(root);self.path=self.root/'training_budget.json';self.name=name;self.requested=updates;self.maximum=max_seconds;self.started=time.monotonic();self.completed=0
  self.lock=(self.root/'training_budget.lock').open('a');fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  self.data=json.loads(self.path.read_text()) if self.path.exists() else {'max_updates':300,'max_seconds':2400,'official_validation_reservation':1,'runs':[]}
  consumed=1+sum(x['completed_updates'] if x['status']!='RUNNING' else x['reserved_updates'] for x in self.data['runs'])
  elapsed=sum(x['seconds'] for x in self.data['runs'])
  if updates<1 or consumed+updates>300 or elapsed>=2400:raise RuntimeError('Cumulative training budget exceeded')
  self.allowed_seconds=min(max_seconds,2400-elapsed);self.row={'name':name,'reserved_updates':updates,'completed_updates':0,'seconds':0.,'status':'RUNNING'};self.data['runs'].append(self.row);self.save()
 def save(self):
  tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(self.data,indent=2));os.replace(tmp,self.path)
 def update(self):
  self.completed+=1;self.row.update(completed_updates=self.completed,seconds=time.monotonic()-self.started);self.save()
 def expired(self):return time.monotonic()-self.started>=self.allowed_seconds
 def close(self,status):
  self.row.update(status=status,seconds=time.monotonic()-self.started,completed_updates=self.completed);self.save();fcntl.flock(self.lock,fcntl.LOCK_UN);self.lock.close()
