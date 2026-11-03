"""Read-only URDF/STL inspection and numerical standing-pose calibration."""
from pathlib import Path
import json, hashlib, struct
import xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[3]
MODEL=ROOT.parent/'model'
def mesh_vertices(path):
 b=path.read_bytes();n=struct.unpack_from('<I',b,80)[0]
 if len(b)==84+n*50:
  return np.ndarray((n,),dtype=np.dtype([('normal','<f4',3),('v','<f4',(3,3)),('attr','<u2')]),buffer=b,offset=84)['v'].reshape(-1,3).astype(float)
 return np.array([list(map(float,line.split()[1:])) for line in b.decode().splitlines() if line.strip().startswith('vertex')])
def inspect():
 tree=ET.parse(MODEL/'robot.urdf').getroot();links={l.attrib['name']:l for l in tree.findall('link')};joints=tree.findall('joint')
 data={'urdf':str(MODEL/'robot.urdf'),'sha256':hashlib.sha256((MODEL/'robot.urdf').read_bytes()).hexdigest(),'links':{},'joints':[],'feet_local':{},'standing_pose':{},'standing_foot_positions':{},'joint_order_note':'URDF declaration order is not runtime articulation order'}
 for name,l in links.items():
  inert=l.find('inertial');iv=inert.find('inertia').attrib;i=np.array([[float(iv['ixx']),float(iv['ixy']),float(iv['ixz'])],[float(iv['ixy']),float(iv['iyy']),float(iv['iyz'])],[float(iv['ixz']),float(iv['iyz']),float(iv['izz'])]])
  v=mesh_vertices(MODEL/l.find('collision/geometry/mesh').attrib['filename'])
  data['links'][name]=dict(mass=float(inert.find('mass').attrib['value']),inertia_eigenvalues=np.linalg.eigvalsh(i).tolist(),collision_bounds=[v.min(0).tolist(),v.max(0).tolist()])
  assert np.linalg.eigvalsh(i).min()>0
  if name.endswith('_knee'):
   # Distal mesh cap, independent of current joint rotations.
   norm=np.linalg.norm(v,axis=1);point=v[norm>norm.max()-0.006].mean(0);data['feet_local'][name]=point.tolist()
 for j in joints:
  data['joints'].append(dict(name=j.attrib['name'],type=j.attrib['type'],parent=j.find('parent').attrib['link'],child=j.find('child').attrib['link'],origin=list(map(float,j.find('origin').attrib['xyz'].split())),axis=list(map(float,j.find('axis').attrib['xyz'].split())),limits={k:float(v) for k,v in j.find('limit').attrib.items()}))
 for leg in ['lf','rf','lr','rr']:
  chain=[next(j for j in data['joints'] if j['name']==f'joint_{leg}_{n}') for n in [1,2,3]]
  point=np.array(data['feet_local'][f'link_{leg}_knee'])
  def fk(q):
   rot=np.eye(3);pos=np.zeros(3)
   for a,j in zip(q,chain):
    pos+=rot@np.array(j['origin']);axis=np.array(j['axis']);axis/=np.linalg.norm(axis);rot=rot@Rotation.from_rotvec(a*axis).as_matrix()
   return pos+rot@point
  target=np.array([0.215 if leg[1]=='f' else -0.215,0.16 if leg[0]=='l' else -0.16,-0.35])
  fit=least_squares(lambda q:fk(q)-target,[0.,0.,0.],bounds=(-1.7,1.7),xtol=1e-12,ftol=1e-12,gtol=1e-12)
  assert np.linalg.norm(fit.fun)<0.002,(leg,fit.fun)
  data['standing_pose'].update({j['name']:float(q) for j,q in zip(chain,fit.x)})
  data['standing_foot_positions'][leg]=fk(fit.x).tolist()
 data['mass_kg']=sum(x['mass'] for x in data['links'].values());data['actuated_joints']=len(joints)
 data['root_height_m']=0.355;data['base_frame']='+X inferred front from lf/rf hip locations; +Y left; +Z up; verify physical response'
 assert len(joints)==12 and all(j['type']=='revolute' for j in data['joints'])
 return data
if __name__=='__main__':
 out=ROOT/'configs/locomotion/csdog_ppo/model_audit.json';out.parent.mkdir(parents=True,exist_ok=True);data=inspect();out.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({k:v for k,v in data.items() if k not in ['links','joints']},indent=2))
