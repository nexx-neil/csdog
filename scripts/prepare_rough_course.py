#!/usr/bin/env python3
"""Generate actual Isaac Lab course meshes; this does not train or evaluate a robot."""
import argparse,json,traceback,hashlib
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--level',choices=('easy','medium','advanced'),default='easy');p.add_argument('--seed',type=int,default=42);AppLauncher.add_app_launcher_args(p);a=p.parse_args()
if a.output.exists():p.error('New output required')
app=AppLauncher(a)
import numpy as np,torch
from isaaclab.terrains import TerrainGenerator
from csdog_motion.rough_curriculum import build_rough_cfg,LEVELS
from csdog_motion.training import file_hash

def main():
 a.output.mkdir(parents=True);np.random.seed(a.seed);torch.manual_seed(a.seed);cfg=build_rough_cfg(a.level,a.seed);gen=TerrainGenerator(cfg,device='cpu');mesh=gen.terrain_mesh;assert np.isfinite(mesh.vertices).all() and len(mesh.faces)>0
 out=a.output/'terrain.ply';mesh.export(out);origins=gen.terrain_origins;assert origins.shape==(4,8,3) and np.isfinite(origins).all()
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 verts=mesh.vertices;faces=mesh.faces;xy=verts[faces,:2];cross=(xy[:,1,0]-xy[:,0,0])*(xy[:,2,1]-xy[:,0,1])-(xy[:,1,1]-xy[:,0,1])*(xy[:,2,0]-xy[:,0,0]);keep=cross>1e-9;f=faces[keep]
 fig,ax=plt.subplots(figsize=(11,6),constrained_layout=True);im=ax.tripcolor(verts[:,0],verts[:,1],f,facecolors=verts[f,2].mean(1),shading='flat',cmap='terrain');ax.set_aspect('equal');ax.set_xlabel('x / m');ax.set_ylabel('y / m');ax.set_title('Isaac Lab generated course: '+a.level+' (geometry only)');fig.colorbar(im,ax=ax,label='surface z / m');fig.savefig(a.output/'map.png',dpi=140);plt.close(fig)
 r={'complete':True,'scope':'Real Isaac Lab generated terrain mesh and origins only; no robot trial, height sensor integration or rough policy training yet','level':a.level,'seed':a.seed,'recipe':LEVELS[a.level],'rows':4,'columns':8,'kinds':list(cfg.sub_terrains),'vertices':len(mesh.vertices),'faces':len(mesh.faces),'mesh_sha256':file_hash(out),'script_sha256':file_hash(__file__),'recipe_source_sha256':file_hash(Path(__file__).resolve().parents[1]/'source/stackforce_simready_generated_robot_lab/csdog_motion/rough_curriculum.py'),'origins':origins.tolist(),'policy_trained':False,'robot_pass_rate':None};(a.output/'summary.json').write_text(json.dumps(r,indent=2)+'\n');print('Generated terrain geometry:',r['vertices'],r['faces'],flush=True)
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
