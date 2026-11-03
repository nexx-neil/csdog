"""Real integration ABI and input safety regressions, no simulator needed."""
from pathlib import Path
from types import SimpleNamespace
import copy,json,math
import pytest
import torch
from dogfight.teleop.config import load_settings,CONTRACT
from dogfight.teleop.keyboard import KeyboardTeleopController
from dogfight.teleop.maps import MapRegistry,MAPS
from dogfight.teleop.laser import LaserEmitter
from dogfight.teleop.policy import PolicyLoader,PolicyAdapter
from dogfight_v0.arena.test_map import TestMap as Arena
from dogfight_v0.battle.types import VelocityCommand

def control():
    settings,_=load_settings();clock=[0.]
    return KeyboardTeleopController(settings['teleop'],clock=lambda:clock[0]),clock

@pytest.mark.parametrize('keys,vx,yaw',[('W',1,0),('S',-1,0),('A',0,1),('D',0,-1),('WA',1,1),('WD',1,-1),('SA',-1,1),('SD',-1,-1),('WQ',0,1),('SE',0,-1),('WS',0,0),('AD',0,0),('QE',0,0)])
def test_key_contract(keys,vx,yaw):
    c,_=control()
    for k in keys:c.event(k)
    cmd=c.command(.02)
    assert (0 if cmd.vx==0 else math.copysign(1,cmd.vx))==vx
    assert (0 if cmd.yaw_rate==0 else math.copysign(1,cmd.yaw_rate))==yaw
    assert cmd.vy==0

def test_latched_estop_unlock_release_timeout_focus():
    c,clock=control();c.event('W');assert c.command(.02).vx>0
    c.event('W',False);assert c.command(.02)==VelocityCommand()
    c.event('W');c.event('SPACE');c.event('SPACE',False)
    assert c.command(.02)==VelocityCommand() and c.estop
    c.event('C');assert not c.estop and c.command(.02)==VelocityCommand()
    c.event('W');clock[0]=2.;assert c.command(.02)==VelocityCommand() and c.estop
    c.event('C');c.event('W');c.focus_lost();assert c.command(.02)==VelocityCommand()

def test_reset_exit_requests():
    c,_=control();c.event('R');assert c.reset_requested
    c.event('ESCAPE');assert c.quit_requested and c.estop

def test_map_registry_is_consumed_and_switches_without_robot_changes():
    registry=MapRegistry();registry.register('base',lambda **kw:Arena())
    class Alternate(Arena):
        def get_bounds(self):return (-2.,2.,-2.,2.)
    registry.register('alternate',lambda **kw:Alternate())
    assert registry.create('base').get_bounds()!=registry.create('alternate').get_bounds()
    assert len(MAPS.create('test_map',boundary_walls=True).walls)==6
    assert len(MAPS.create('test_map',boundary_walls=False).walls)==2
    with pytest.raises(ValueError):MAPS.create('missing')

def test_laser_filters_self_without_damage_and_uses_closest_other():
    agent=SimpleNamespace(prim_path='/World/Agents/dog_a',get_muzzle_origin_world=lambda:(0.,0.,1.),get_forward_vector_world=lambda:(1.,0.,0.))
    hits=[dict(path=agent.prim_path+'/base',distance=.1),dict(path='/World/Wall',distance=2.),dict(path='/World/Other',distance=3.)]
    cfg=dict(enabled=True,raycast_enabled=True,damage_enabled=False,max_range=20.)
    laser=LaserEmitter(agent,cfg,lambda *args:hits)
    hit=laser.update();assert hit.object_path=='/World/Wall' and hit.endpoint==(2.,0.,1.)
    hits.clear();assert laser.update().distance==20.

def test_policy_manifest_weight_shape_and_invalid_weight(tmp_path):
    _,cfg=load_settings();actor,meta=PolicyLoader.load(cfg['checkpoint'],cfg['contract'])
    assert actor(torch.zeros(1,50)).shape==(1,12) and meta['iteration']==1043
    bad=tmp_path/'bad.pt';torch.save({'model_state_dict':{'actor.0.weight':torch.zeros(256,48)}},bad)
    with pytest.raises(RuntimeError):PolicyLoader.load(bad,CONTRACT)
    wrong=copy.deepcopy(CONTRACT);wrong['joint_order']=list(reversed(wrong['joint_order']))
    with pytest.raises(ValueError):PolicyLoader.load(cfg['checkpoint'],wrong)

def test_policy_observation_order_clipping_and_no_world_step():
    data=SimpleNamespace(default_joint_pos=torch.zeros(1,12),root_lin_vel_b=torch.tensor([[1.,2.,3.]]),root_ang_vel_b=torch.tensor([[4.,5.,6.]]),projected_gravity_b=torch.tensor([[0.,0.,-1.]]),joint_pos=torch.ones(1,12)*.1,joint_vel=torch.ones(1,12)*.2)
    targets=[]
    robot=SimpleNamespace(device='cpu',data=data,find_joints=lambda names,preserve_order:(list(range(12)),names),set_joint_position_target=lambda value,joint_ids:targets.append(value))
    adapter=PolicyAdapter(robot,lambda x:torch.ones(1,12)*2.,CONTRACT);adapter.set_command(VelocityCommand(.25,0.,.3))
    obs=adapter.observation();assert obs.shape==(1,50)
    assert obs[0,:6].tolist()==[1.,2.,3.,4.,5.,6.]
    assert torch.allclose(obs[0,9:12],torch.tensor([.25,0.,.3]));assert obs[0,48:].tolist()==[0.,1.]
    adapter.step(.02);assert torch.allclose(targets[-1],torch.ones(1,12)*.35)
    assert torch.allclose(adapter.observation()[0,36:48],torch.ones(12))
    with pytest.raises(ValueError):adapter.set_command(VelocityCommand(0,.1,0))
    with pytest.raises(ValueError):adapter.step(.01)


def test_config_selected_map_factory_used_by_runtime(monkeypatch):
    from dogfight.teleop.maps import create_selected_map
    class Alternate(Arena):
        def get_bounds(self):return (-3.,3.,-2.,2.)
    monkeypatch.setitem(MAPS.factories,'unit_alternate',lambda **kw:Alternate())
    settings,_=load_settings(map_name='unit_alternate')
    assert create_selected_map(settings).get_bounds()==(-3.,3.,-2.,2.)


def test_checkpoint_manifest_hash_and_missing_path_rejected(tmp_path):
    import yaml
    from dogfight.common.paths import ROOT
    settings,config=load_settings()
    raw=yaml.safe_load((ROOT/'configs/robots/dog_a_teleop.yaml').read_text())
    wrong=tmp_path/'wrong.pt';wrong.write_bytes(b'invalid checkpoint')
    raw['checkpoint']=str(wrong)
    robot=tmp_path/'robot.yaml';robot.write_text(yaml.safe_dump(raw))
    settings['robots']={'dog_a':str(robot)}
    cfg=tmp_path/'settings.yaml';cfg.write_text(yaml.safe_dump(settings))
    with pytest.raises(ValueError,match='SHA256'):load_settings(cfg)
    raw['checkpoint']=str(tmp_path/'missing.pt');robot.write_text(yaml.safe_dump(raw))
    with pytest.raises(FileNotFoundError):load_settings(cfg)

@pytest.mark.parametrize('symbolic',[True,False])
def test_isaac_keyboard_callback_accepts_string_and_enum_events(symbolic):
    from dogfight.teleop.keyboard import IsaacKeyboard
    controller,_=control();keyboard=IsaacKeyboard.__new__(IsaacKeyboard)
    keyboard.controller=controller;keyboard.focus=SimpleNamespace(focused=lambda:True);keyboard.debug_count=99
    def event(key,kind):
        return SimpleNamespace(input=key if symbolic else SimpleNamespace(name=key),type=kind if symbolic else SimpleNamespace(name=kind))
    assert keyboard.on_event(event('W','KEY_PRESS')) is False
    assert controller.command(.02).vx>0
    keyboard.on_event(event('SPACE','KEY_PRESS'));keyboard.on_event(event('SPACE','KEY_RELEASE'))
    assert controller.estop
    keyboard.on_event(event('C','KEY_PRESS'));assert not controller.estop
    keyboard.on_event(event('ESCAPE','KEY_PRESS'));assert controller.quit_requested
