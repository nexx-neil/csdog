#!/usr/bin/env python3
"""Export the independent terrain library; geometry generation is not robot validation."""
import argparse,json,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--seed',type=int,default=12011);AppLauncher.add_app_launcher_args(p);a=p.parse_args()
if a.output.exists():p.error('New output required')
app=AppLauncher(a)
import numpy as np,torch
from isaaclab.terrains import TerrainGenerator
from csdog_motion.terrain_library import build_library_cfg,scenario,LEVELS
from csdog_motion.training import file_hash

class RecordedGenerator(TerrainGenerator):
 def _get_terrain_mesh(self,difficulty,cfg):
  self._latest_difficulty=float(difficulty);return super()._get_terrain_mesh(difficulty,cfg)
 def _add_sub_terrain(self,mesh,origin,row,col,cfg):
  if not hasattr(self,'records'):self.records=[];self.samples={}
  assert np.isfinite(mesh.vertices).all() and len(mesh.faces)>0
  self.records.append({'row':row,'column':col,'kind':list(self.cfg.sub_terrains)[col],'actual_difficulty':self._latest_difficulty,'vertices':len(mesh.vertices),'faces':len(mesh.faces),'local_origin':origin.tolist()})
  if row==2:self.samples[col]=mesh.copy()
  return super()._add_sub_terrain(mesh,origin,row,col,cfg)

def poster(gen,path,title):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 cols=4;rows=(len(gen.samples)+cols-1)//cols
 fig=plt.figure(figsize=(15,3.6*rows),layout='constrained');fig.suptitle(title+' | generated geometry; robot ability unvalidated',fontsize=13)
 for col,mesh in gen.samples.items():
  ax=fig.add_subplot(rows,cols,col+1,projection='3d');v=mesh.vertices;f=mesh.faces;normal=mesh.face_normals
  # Show surfaces, including the skill ring; hide only the deep underside of solid bases.
  f=f[(normal[:,2]>-.1)&(v[f,2].mean(1)>-.4)]
  ax.plot_trisurf(v[:,0],v[:,1],v[:,2],triangles=f,cmap='terrain',linewidth=0,antialiased=False)
  ax.set_title(f'{col}: '+list(gen.cfg.sub_terrains)[col],fontsize=10);ax.set_xlim(-3,3);ax.set_ylim(-3,3);ax.set_zlim(-.3 if len(gen.samples)==4 else -.1,max(.35,float(v[:,2].max())+.05));ax.set_box_aspect((1,1,.35));ax.view_init(35,-55);ax.set_xticks([-3,0,3]);ax.set_yticks([-3,0,3]);ax.tick_params(labelsize=7)
 fig.savefig(path,dpi=125);plt.close(fig)

def main():
 a.output.mkdir(parents=True);entries=[]
 for level in LEVELS:
  for group in ('walking','skills'):
   np.random.seed(a.seed);torch.manual_seed(a.seed);cfg=build_library_cfg(level,group,a.seed);gen=RecordedGenerator(cfg,device='cpu');folder=a.output/(level+'_'+group);folder.mkdir();mesh=folder/'terrain.ply';gen.terrain_mesh.export(mesh);assert gen.terrain_origins.shape==(3,cfg.num_cols,3) and np.isfinite(gen.terrain_origins).all()
   poster(gen,folder/'catalog.png',level+' / '+group)
   d={'complete':True,'geometry_only':True,'robot_pass_rate':None,'scenario':scenario(level,group,a.seed,2),'cells':gen.records,'origins':gen.terrain_origins.tolist(),'mesh_sha256':file_hash(mesh),'vertices':len(gen.terrain_mesh.vertices),'faces':len(gen.terrain_mesh.faces),'generator_version':'installed IsaacLab2.3.2','source_sha256':file_hash(Path(__file__).resolve().parents[1]/'source/stackforce_simready_generated_robot_lab/csdog_motion/terrain_library.py')};(folder/'summary.json').write_text(json.dumps(d,indent=2)+'\n');entries.append({'level':level,'group':group,'folder':str(folder.resolve()),'cells':len(gen.records)});print('GENERATED',level,group,len(gen.records),flush=True)
 (a.output/'summary.json').write_text(json.dumps({'complete':True,'entries':entries,'total_tiles':sum(x['cells']for x in entries),'robot_validation':'NOT_IMPLIED_BY_MESH_GENERATION'},indent=2)+'\n')
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
