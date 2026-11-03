"""Diagnostic Cartesian/body feedback only. Never imported by PPO configuration."""
import numpy as np
LEGS=('lf','rf','lr','rr')
class LegKinematics:
 def __init__(self,audit):
  self.origins=np.array([[next(x for x in audit['joints'] if x['name']==f'joint_{leg}_{j}')['origin'] for j in [1,2,3]] for leg in LEGS])
  self.axes=np.array([[next(x for x in audit['joints'] if x['name']==f'joint_{leg}_{j}')['axis'] for j in [1,2,3]] for leg in LEGS]);self.axes/=np.linalg.norm(self.axes,axis=-1,keepdims=True)
  self.tips=np.array([audit['feet_local'][f'link_{leg}_knee'] for leg in LEGS])
  self.default=np.array([[audit['standing_pose'][f'joint_{leg}_{j}'] for j in [1,2,3]] for leg in LEGS])
 def forward(self,q,jacobian=False):
  shape=q.shape[:-1];rot=np.broadcast_to(np.eye(3),(*shape,3,3)).copy();pos=np.zeros((*shape,3));pivots=[];axes=[]
  for j in range(3):
   pos+=np.einsum('...ij,...j->...i',rot,self.origins[:,j]);pivots.append(pos.copy());axis=np.broadcast_to(self.axes[:,j],pos.shape)
   axes.append(np.einsum('...ij,...j->...i',rot,axis))
   cross=np.zeros((*shape,3,3));x,y,z=np.moveaxis(axis,-1,0);cross[...,0,1]=-z;cross[...,0,2]=y;cross[...,1,0]=z;cross[...,1,2]=-x;cross[...,2,0]=-y;cross[...,2,1]=x
   angle=q[...,j,None,None];r=np.eye(3)+np.sin(angle)*cross+(1.-np.cos(angle))*(cross@cross);rot=rot@r
  tip=pos+np.einsum('...ij,...j->...i',rot,self.tips)
  if not jacobian:return tip
  jac=np.stack([np.cross(a,tip-p) for a,p in zip(axes,pivots)],axis=-1)
  return tip,jac
 def inverse(self,target,q,iterations=6):
  q=q.copy()
  for _ in range(iterations):
   tip,jac=self.forward(q,True);error=target-tip
   step=np.einsum('...ji,...j->...i',jac,np.linalg.solve(jac@np.swapaxes(jac,-1,-2)+np.eye(3)*2e-5,error))
   q=np.clip(q+np.clip(step,-.06,.06),self.default-1.1,self.default+1.1)
  return q

def support_margin(com_xy,triangle):
 """Signed distance in metres, positive inside either triangle winding."""
 edges=np.roll(triangle,-1,axis=-2)-triangle;relative=com_xy[...,None,:]-triangle
 signed=edges[...,0]*relative[...,1]-edges[...,1]*relative[...,0]
 area=edges[...,0,0]*edges[...,1,1]-edges[...,0,1]*edges[...,1,0]
 signed*=np.where(area>=0,1.,-1.)[...,None]
 return np.min(signed/np.linalg.norm(edges,axis=-1).clip(1e-8),axis=-1)
