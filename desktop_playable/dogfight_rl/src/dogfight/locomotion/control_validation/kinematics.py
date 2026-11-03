"""URDF FK, geometric Jacobian and bounded DLS IK; SI units, base frame."""
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial.transform import Rotation
LEGS = ('lf', 'rf', 'lr', 'rr')

def vec(node, key, default='0 0 0'):
    return np.fromstring(node.get(key, default), sep=' ')

class Kinematics:
    def __init__(self, urdf, tips, default):
        self.tree = ET.parse(urdf).getroot()
        self.chains = [[self.tree.find(f"joint[@name='joint_{leg}_{j}']") for j in (1,2,3)] for leg in LEGS]
        self.origin = np.array([[vec(j.find('origin'),'xyz') for j in chain] for chain in self.chains])
        self.rotation = np.array([[Rotation.from_euler('xyz',vec(j.find('origin'),'rpy')).as_matrix() for j in chain] for chain in self.chains])
        self.axes = np.array([[vec(j.find('axis'),'xyz') for j in chain] for chain in self.chains])
        self.axes /= np.linalg.norm(self.axes,axis=-1,keepdims=True)
        self.lower = np.array([[float(j.find('limit').get('lower')) for j in chain] for chain in self.chains])
        self.upper = np.array([[float(j.find('limit').get('upper')) for j in chain] for chain in self.chains])
        self.tips = np.array([tips[f'link_{leg}_knee'] for leg in LEGS])
        self.default = np.array([[default[f'joint_{leg}_{j}'] for j in (1,2,3)] for leg in LEGS])
    def forward(self,q,jacobian=False):
        q=np.asarray(q); shape=q.shape[:-1]
        rot=np.broadcast_to(np.eye(3),(*shape,3,3)).copy();pos=np.zeros((*shape,3));pivots=[];axes=[]
        for j in range(3):
            pos+=np.einsum('...ij,...j->...i',rot,self.origin[:,j]);rot=rot@self.rotation[:,j]
            pivots.append(pos.copy());axis=np.broadcast_to(self.axes[:,j],pos.shape)
            axes.append(np.einsum('...ij,...j->...i',rot,axis))
            cross=np.zeros((*shape,3,3));x,y,z=np.moveaxis(axis,-1,0)
            cross[...,0,1]=-z;cross[...,0,2]=y;cross[...,1,0]=z;cross[...,1,2]=-x;cross[...,2,0]=-y;cross[...,2,1]=x
            angle=q[...,j,None,None];rot=rot@(np.eye(3)+np.sin(angle)*cross+(1-np.cos(angle))*(cross@cross))
        tip=pos+np.einsum('...ij,...j->...i',rot,self.tips)
        return (tip,np.stack([np.cross(a,tip-p) for a,p in zip(axes,pivots)],axis=-1)) if jacobian else tip
    def within_limits(self,q):
        return ((q>=self.lower)&(q<=self.upper)).all(-1)
    def inverse(self,target,q=None,iterations=60,tolerance=1e-5):
        target=np.asarray(target);q=np.broadcast_to(self.default,target.shape).copy() if q is None else np.array(q,copy=True)
        for _ in range(iterations):
            tip,jac=self.forward(q,True);error=target-tip
            if np.max(np.linalg.norm(error,axis=-1))<tolerance:break
            step=np.einsum('...ji,...j->...i',jac,np.linalg.solve(jac@np.swapaxes(jac,-1,-2)+np.eye(3)*1e-6,error))
            q=np.clip(q+np.clip(step,-.12,.12),self.lower,self.upper)
        error=np.linalg.norm(target-self.forward(q),axis=-1)
        return q,error,(error<tolerance)&self.within_limits(q)

def support_margin(com,triangle):
    edges=np.roll(triangle,-1,axis=-2)-triangle;rel=com[...,None,:]-triangle
    cross=edges[...,0]*rel[...,1]-edges[...,1]*rel[...,0]
    area=edges[...,0,0]*edges[...,1,1]-edges[...,0,1]*edges[...,1,0]
    return np.min(cross*np.where(area>=0,1.,-1.)[...,None]/np.linalg.norm(edges,axis=-1).clip(1e-9),axis=-1)

def leg_gravity(kin, q, world_rotation):
    """Generalized compensation for each leg's own URDF masses (no payload)."""
    shape=q.shape[:-1];rot=np.broadcast_to(np.eye(3),(*shape,3,3)).copy();pos=np.zeros((*shape,3));pivots=[];axes=[];torque=np.zeros_like(q)
    for j in range(3):
        pos+=np.einsum('...ij,...j->...i',rot,kin.origin[:,j]);rot=rot@kin.rotation[:,j]
        pivots.append(pos.copy());axes.append(np.einsum('...ij,...j->...i',rot,kin.axes[:,j]))
        mats=Rotation.from_rotvec((q[...,j,None]*kin.axes[:,j]).reshape(-1,3)).as_matrix().reshape(*shape,3,3);rot=rot@mats
        offsets=[];masses=[]
        for chain in kin.chains:
            link=kin.tree.find(f"link[@name='{chain[j].find('child').get('link')}']");inert=link.find('inertial');offsets.append(vec(inert.find('origin'),'xyz'));masses.append(float(inert.find('mass').get('value')))
        c=pos+np.einsum('nlij,lj->nli',rot,np.array(offsets))
        # Rotation transpose maps world upward gravity compensation into base frame.
        up=np.einsum('nji,j->ni',world_rotation,np.array([0.,0.,9.81]))
        for k in range(j+1):torque[...,k]+=np.einsum('nli,ni->nl',np.cross(axes[k],c-pivots[k]),up)*masses
    return torque
