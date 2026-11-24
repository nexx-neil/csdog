#!/usr/bin/env python3
"""Render exported PLY surfaces without launching or changing a simulation."""
import argparse,json
from pathlib import Path
import numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--library',type=Path,required=True);a=p.parse_args()
plt.rcParams.update({'font.family':'Noto Sans CJK JP','axes.unicode_minus':False})
names={'flat':'平地对照','pyramid_slope':'金字塔坡','inverted_slope':'凹形坡','pyramid_stairs':'金字塔台阶','inverted_stairs':'凹形台阶','blocks':'随机方块','waves':'连续波浪','rails':'连续横栏','scattered_obstacles':'散布障碍','rough':'细碎起伏','compound':'坡→台阶→碎块','double_box':'双层平台','stepping_stones':'踏石','gap':'沟槽','pit':'双层浅坑','crawl_ring':'低顶通道'}
for item in json.loads((a.library/'summary.json').read_text())['entries']:
 folder=Path(item['folder']);summary=json.loads((folder/'summary.json').read_text());mesh=trimesh.load_mesh(folder/'terrain.ply',process=False);v=mesh.vertices;faces=mesh.faces;normal=mesh.face_normals
 n=12 if item['group']=='walking'else 4;rows=(n+3)//4;fig=plt.figure(figsize=(15,3.5*rows),layout='constrained')
 fig.suptitle(f"{item['level']}｜{'连续行走场景'if n==12 else'跳跃/钻行技能预留场景'}｜仅几何预览，不代表已能通过",fontsize=14)
 for col,kind in enumerate(summary['scenario']['kinds']):
  origin=np.array(summary['origins'][2][col]);lo=origin[:2]-3.00001;hi=origin[:2]+3.00001
  select=(v[faces,:2]>=lo).all((1,2)) & (v[faces,:2]<=hi).all((1,2)) & (normal[:,2]>.01)
  f=faces[select];center=v[f].mean(1);f=f[center[:,2]>-.4]
  # Drop unused vertices so solid-base undersides do not distort axes or color ranges.
  ids,inverse=np.unique(f,return_inverse=True);local=v[ids].copy();local[:,:2]-=origin[:2];ff=inverse.reshape(-1,3)
  # A real vertical ray pass removes false diagonal occlusions caused by painter-sorting
  # overlapping native box surfaces in matplotlib. Missing hits remain holes.
  surface=trimesh.Trimesh(vertices=local,faces=ff,process=False)
  gx,gy=np.meshgrid(np.linspace(-2.995,2.995,101),np.linspace(-2.995,2.995,101),indexing='ij')
  starts=np.column_stack((gx.ravel(),gy.ravel(),np.full(gx.size,float(local[:,2].max())+1)))
  locations,ray_ids,_=surface.ray.intersects_location(starts,np.tile([0.,0.,-1.],(gx.size,1)),multiple_hits=False)
  hz=np.full(gx.size,np.nan);hz[ray_ids]=locations[:,2];hz=hz.reshape(gx.shape)
  ax=fig.add_subplot(rows,4,col+1,projection='3d');ax.plot_surface(gx,gy,hz,cmap='terrain',linewidth=0,antialiased=False,rcount=101,ccount=101)
  top=max(.06,float(local[:,2].max())+.02);bottom=min(-.01,float(local[:,2].min())-.01)
  ax.set(xlim=(-3,3),ylim=(-3,3),zlim=(bottom,top),xticks=[],yticks=[],zticks=[round(bottom,2),round(top,2)]);ax.set_box_aspect((1,1,.3));ax.view_init(37,-55);ax.set_title(f'{col}  {names[kind]}',fontsize=11);ax.tick_params(labelsize=7)
 fig.savefig(folder/'catalog_top.png',dpi=125);plt.close(fig);print('Rendered',folder.name)
