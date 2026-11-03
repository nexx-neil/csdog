"""Separate 320-update / 1800-second locked ledger. Old budget is never opened."""
import fcntl,json,time,os
class Budget:
 def __init__(self,root,name,updates):
  self.path=root/'training_budget.json';self.lock=(root/'training_budget.lock').open('a');fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  self.started=time.monotonic();self.completed=0
  self.data=json.loads(self.path.read_text()) if self.path.exists() else dict(max_updates=320,max_seconds=1800,runs=[])
  used=sum(x['reserved_updates'] if x['status']=='RUNNING' else x['completed_updates'] for x in self.data['runs']);elapsed=sum(x['seconds'] for x in self.data['runs'])
  if updates<1 or updates>150 or used+updates>320 or elapsed>=1800:raise RuntimeError('Spot v2 budget exhausted')
  self.allowed_seconds=1800-elapsed;self.row=dict(name=name,reserved_updates=updates,completed_updates=0,seconds=0.,status='RUNNING');self.data['runs'].append(self.row);self.save()
 def save(self):
  tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(self.data,indent=2));os.replace(tmp,self.path)
 def update(self):
  if self.completed>=self.row['reserved_updates']:raise RuntimeError('Reserved update limit reached')
  self.completed+=1;self.row.update(completed_updates=self.completed,seconds=time.monotonic()-self.started);self.save()
 def expired(self):return time.monotonic()-self.started>=self.allowed_seconds
 def close(self,status):
  self.row.update(status=status,seconds=time.monotonic()-self.started,completed_updates=self.completed);self.save();fcntl.flock(self.lock,fcntl.LOCK_UN);self.lock.close()
