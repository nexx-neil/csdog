"""Validate checkpoint/video coverage, actual metadata and frozen historical files."""
from pathlib import Path
import json,hashlib,subprocess,os,sys
import torch,numpy as np
import imageio.v2 as imageio
from PIL import Image
R=Path(__file__).resolve().parents[2];E=R/'runs/locomotion/csdog_ppo_spot_aligned_v3';O=E/'reports';P=E/'protection'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finite(x):
 if torch.is_tensor(x):return bool(torch.isfinite(x).all())
 if isinstance(x,dict):return all(finite(v) for v in x.values())
 if isinstance(x,(list,tuple)):return all(finite(v) for v in x)
 return True
checkpoint_rows=[];model_digests={}
for stage in ['smoke','first','second']:
 for p in sorted((E/stage).glob('*.pt')):
  state=torch.load(p,map_location='cpu',weights_only=False);assert finite(state),p
  model=state['model_state_dict'];h=hashlib.sha256()
  for key,value in sorted(model.items()):
   h.update(key.encode())
   if torch.is_tensor(value):h.update(value.cpu().contiguous().numpy().tobytes())
  digest=h.hexdigest();model_digests[str(p)]=digest
  if stage=='first' and p.stem in ['final','update_0120']:video=E/'videos/first/all_directions.mp4'
  elif stage=='second' and p.stem=='final':video=E/'videos/second/all_directions.mp4'
  else:video=E/'videos'/stage/p.stem/'all_directions.mp4'
  assert video.exists(),video
  checkpoint_rows.append(dict(checkpoint=str(p),sha256=sha(p),all_tensors_finite=True,iteration=int(state['iter']),model_digest=digest,actual_video=str(video)))
assert model_digests[str(E/'first/update_0120.pt')]==model_digests[str(E/'first/final.pt')]
(O/'checkpoint_visualization_manifest.json').write_text(json.dumps(checkpoint_rows,indent=2))
(O/'checkpoint_validation.json').write_text(json.dumps(dict(checkpoints=checkpoint_rows,count=len(checkpoint_rows),unique_model_states=len(set(model_digests.values()))),indent=2))
# All comparison scenes are floating; fixed fixture evidence is explicitly separate.
for folder in ['comparison_stage2','comparison_v2_b','comparison_v2_c','evaluation_first','evaluation_second']:
 d=np.load(E/folder/'diagnostics.npz')
 assert all(np.isfinite(d[k]).all() for k in ['q','target','qd','torque','velocity','foot_height','raw_action','projected_joint_force'])
 assert (E/folder/'summary_validated.json').exists()
for stage in ['first','second']:
 video=E/'videos'/stage/'all_directions.mp4';slow=video.with_name('all_directions_slow2x.mp4')
 if not slow.exists():
  subprocess.run(['ffmpeg','-v','error','-n','-i',str(video),'-vf','setpts=2.0*PTS','-r','25','-an','-c:v','libx264','-crf','20',str(slow)],check=True)
meta={}
for video in (E/'videos').rglob('*.mp4'):
 raw=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height,nb_frames,avg_frame_rate:format=duration','-of','json',str(video)],text=True));meta[str(video)]=raw
(O/'video_metadata.json').write_text(json.dumps(meta,indent=2))
for stage in ['stage2','v2_b','v2_c','first','second']:
 video=E/'videos'/stage/'all_directions.mp4';reader=imageio.get_reader(video);fps=reader.get_meta_data()['fps']
 grid=Image.new('RGB',(960,720))
 for i,t in enumerate([1.,5.5,13.5,29.5]):
  im=Image.fromarray(reader.get_data(round(t*fps)));im.thumbnail((480,360));grid.paste(im,((i%2)*480,(i//2)*360))
 grid.save(O/(stage+'_video_preview.png'));reader.close()
# A one-cycle close temporal review, all frames are decoded from the actual movie.
reader=imageio.get_reader(E/'videos/second/all_directions.mp4');grid=Image.new('RGB',(960,720))
for i,t in enumerate([5.0,5.12,5.24,5.36]):
 im=Image.fromarray(reader.get_data(round(t*25)));im.thumbnail((480,360));grid.paste(im,((i%2)*480,(i//2)*360))
grid.save(O/'second_forward_cycle_review.png');reader.close()
# Only remove newly created pytest convenience symlinks; keep all target fixtures.
removed=[]
for folder in ['test_tmp','test_full_tmp']:
 for p in (E/folder).glob('*current'):
  if p.is_symlink():removed.append(dict(pointer=str(p),target=os.readlink(p)));p.unlink()
(P/'pytest_pointer_cleanup.json').write_text(json.dumps(dict(removed_only_new_pytest_pointers=removed,target_data_preserved=True),indent=2))
before=json.loads((P/'before_sha256.json').read_text());bad=[p for p,h in before.items() if not Path(p).is_file() or sha(Path(p))!=h]
git_status=subprocess.check_output(['git','-C',str(R.parent/'IsaacLab'),'status','--porcelain'],text=True)
integrity=dict(status='PASS' if not bad and not git_status else 'FAIL',protected_file_count=len(before),changed_files=bad,isaaclab_git_status=git_status,isaaclab_commit=subprocess.check_output(['git','-C',str(R.parent/'IsaacLab'),'rev-parse','HEAD'],text=True).strip())
(P/'integrity_after.json').write_text(json.dumps(integrity,indent=2));assert integrity['status']=='PASS',integrity
sources=list((R/'src/dogfight/locomotion/spot_aligned_v3').glob('*.py'))+list((R/'scripts').rglob('*aligned*.py'))+[R/'tests/test_spot_aligned_budget.py']
(P/'added_sources.json').write_text(json.dumps({str(p):sha(p) for p in sources},indent=2))
budget=json.loads((E/'training_budget.json').read_text());total=sum(x['completed_updates'] for x in budget['runs']);seconds=sum(x['seconds'] for x in budget['runs'])
assert total==225 and seconds<1200 and all(x['status']=='COMPLETE' for x in budget['runs'])
completion=dict(status='PASS_EXECUTION_WITH_GAIT_LIMITATIONS',ppo_updates=total,training_seconds=seconds,regression_tests=45,checkpoint_count=len(checkpoint_rows),unique_visualized_policies=len(set(model_digests.values())),normal_four_leg_gait=False,floating_open_loop_lift_gate=False,unloaded_fixture_lift=True,long_training_started=False,long_training_recommended=False,historical_integrity=integrity['status'])
(O/'completion_check.json').write_text(json.dumps(completion,indent=2))
print(json.dumps(completion),flush=True)
manifest={str(p.relative_to(E)):sha(p) for p in E.rglob('*') if p.is_file() and p.name!='artifact_manifest.json'}
(E/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2))
