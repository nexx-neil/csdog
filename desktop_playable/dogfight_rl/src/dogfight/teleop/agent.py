"""V0 real articulation agent with a configurable body-frame muzzle."""
from dogfight_v0.agents.real_dog_agent import RealDogAgent

class TeleopRealDogAgent(RealDogAgent):
    def __init__(self,*args,muzzle_offset,**kwargs):
        super().__init__(*args,**kwargs);self.muzzle_offset=tuple(muzzle_offset)
    def _rotate(self,v):
        q=[float(x) for x in self.articulation.data.root_quat_w[self._environment_index]]
        w,x,y,z=q;a,b,c=v
        # q * vector * q^-1, matching Isaac's wxyz convention.
        return ((1-2*y*y-2*z*z)*a+2*(x*y-w*z)*b+2*(x*z+w*y)*c,
                2*(x*y+w*z)*a+(1-2*x*x-2*z*z)*b+2*(y*z-w*x)*c,
                2*(x*z-w*y)*a+2*(y*z+w*x)*b+(1-2*x*x-2*y*y)*c)
    def get_forward_vector_world(self): return self._rotate((1.,0.,0.))
    def get_muzzle_origin_world(self):
        offset=self._rotate(self.muzzle_offset)
        p=self.articulation.data.root_pos_w[self._environment_index]
        return tuple(float(p[i])+offset[i] for i in range(3))

class BattleDogAgent(TeleopRealDogAgent):
    """V0 planar aiming: level rays through body height, not above the target's roof."""
    def get_forward_vector_world(self):
        from math import cos,sin
        yaw=self.get_pose().yaw
        return cos(yaw),sin(yaw),0.
    def get_muzzle_origin_world(self):
        from math import cos,sin
        pose=self.get_pose();x,y,z=self.muzzle_offset
        root_z=float(self.articulation.data.root_pos_w[self._environment_index,2])
        return (pose.x+cos(pose.yaw)*x-sin(pose.yaw)*y,
                pose.y+sin(pose.yaw)*x+cos(pose.yaw)*y,root_z+z)
