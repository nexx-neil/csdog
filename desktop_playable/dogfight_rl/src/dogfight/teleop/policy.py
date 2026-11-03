"""Exact peer actor inference ABI; no optimizer, runner or training imports."""
import math
import torch
from torch import nn
from dogfight_v0.battle.types import VelocityCommand
from .config import CONTRACT

class PolicyLoader:
    @staticmethod
    def load(path, contract, device='cpu'):
        if contract != CONTRACT:
            raise ValueError('Unsupported policy ABI')
        payload = torch.load(path, map_location=device, weights_only=True)
        state = payload['model_state_dict']
        if any('normalizer' in k or 'running_mean' in k for k in state):
            raise ValueError('Observation normalization unsupported by this ABI')
        layers=[]
        dims=[50,256,256,128,12]
        for a,b in zip(dims[:-1],dims[1:]):
            if layers: layers.append(nn.ELU())
            layers.append(nn.Linear(a,b))
        actor=nn.Sequential(*layers).to(device)
        actor_state={k.removeprefix('actor.'):v for k,v in state.items() if k.startswith('actor.')}
        actor.load_state_dict(actor_state, strict=True)
        if not all(torch.isfinite(v).all() for v in actor.parameters()):
            raise ValueError('Non-finite actor weights')
        return actor.eval(), {'iteration':payload.get('iter'), 'architecture':dims}

class PolicyAdapter:
    """Compute targets only. World stepping belongs exclusively to the scheduler."""
    supports_lateral_velocity = False  # No local lateral-motion acceptance evidence.
    def __init__(self, robot, actor, contract):
        self.robot=robot; self.actor=actor; self.contract=contract
        self.ids,names=robot.find_joints(contract['joint_order'],preserve_order=True)
        if list(names)!=contract['joint_order'] or len(set(self.ids))!=12:
            raise ValueError(f'Robot joint mapping mismatch: {names}')
        if not torch.allclose(robot.data.default_joint_pos[:,self.ids],torch.zeros(1,12,device=robot.device)):
            raise ValueError('Peer policy requires zero default joint angles')
        self.previous=torch.zeros(1,12,device=robot.device)
        self.reset()
    @property
    def command(self): return VelocityCommand(self._command.vx,self._command.vy,self._command.yaw_rate)
    def reset(self):
        self._command=VelocityCommand();self.previous.zero_();self.steps=0
    def set_command(self, command):
        if not all(math.isfinite(v) for v in (command.vx,command.vy,command.yaw_rate)):
            raise ValueError('Non-finite velocity command')
        if abs(command.vy)>1e-8: raise ValueError('dog_a adapter: vy not validated; lateral velocity disabled')
        if abs(command.vx)>.4 or abs(command.yaw_rate)>.4:
            raise ValueError('Command outside peer Teleop trained range')
        self._command=VelocityCommand(command.vx,0.,command.yaw_rate)
    def observation(self):
        d=self.robot.data
        cmd=torch.tensor([[self._command.vx,0.,self._command.yaw_rate]],device=self.robot.device)
        phase=torch.tensor([self.steps*self.contract['policy_dt']/self.contract['gait_cycle_time']%1.],device=self.robot.device)
        return torch.cat((d.root_lin_vel_b,d.root_ang_vel_b,d.projected_gravity_b,cmd,
            d.joint_pos[:,self.ids]-d.default_joint_pos[:,self.ids],d.joint_vel[:,self.ids],
            self.previous,torch.stack((torch.sin(2*torch.pi*phase),torch.cos(2*torch.pi*phase)),dim=1)),dim=-1)
    @torch.inference_mode()
    def compute_action(self, observation):
        if observation.shape!=(1,50) or not torch.isfinite(observation).all():
            raise ValueError('Invalid 50-dimensional policy observation')
        return self.actor(observation).clamp(-1.,1.)
    def step(self, dt):
        if not math.isclose(dt,self.contract['policy_dt'],abs_tol=1e-8):
            raise ValueError('Policy must run at exactly 50 Hz')
        action=self.compute_action(self.observation())
        if not torch.isfinite(action).all(): raise RuntimeError('Non-finite policy action')
        self.robot.set_joint_position_target(action*.35+self.robot.data.default_joint_pos[:,self.ids],joint_ids=self.ids)
        self.previous=action.clone();self.steps+=1
