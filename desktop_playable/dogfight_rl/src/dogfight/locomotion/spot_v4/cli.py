"""Supervisor propagates native simulator failures even if Kit exits with status zero."""
import json,os,sys,subprocess,signal
def supervise(script,launch,out,log_name='train.log'):
 token=json.loads(launch.read_text())['token'];env=os.environ.copy();env['CSDOG_V4_WORKER_TOKEN']=token
 child=subprocess.Popen([sys.executable,str(script.resolve()),'--_worker',str(launch.resolve())],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,env=env,start_new_session=True)
 previous={}
 def forward(signum,frame):
  if child.poll() is None:child.send_signal(signum)
 for sig in [signal.SIGINT,signal.SIGTERM]:previous[sig]=signal.signal(sig,forward)
 try:
  with (out/log_name).open('w') as log:
   for line in child.stdout:
    sys.stdout.write(line);sys.stdout.flush();log.write(line);log.flush()
  rc=child.wait();path=out/'result.json'
  if not path.exists():
   print(f'ERROR: simulation exited before a valid result (code {rc}). Inspect {out/log_name}; native GPU abort/OOM may require fewer environments.',file=sys.stderr);return 1
  data=json.loads(path.read_text())
  if data['status'] not in ['COMPLETE','DRY_RUN_PASS','INTERRUPTED','EVALUATION_PASS']:return 1
  print(f'Saved result: {path}',flush=True)
  return 130 if data['status']=='INTERRUPTED' else 0
 finally:
  for sig,handler in previous.items():signal.signal(sig,handler)
