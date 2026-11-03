"""Pure unit tests; these do NOT claim GUI or PPO physical acceptance."""
from dataclasses import replace
from math import pi
import pytest
from dogfight.fsm.navigation import GridPlanner
from dogfight.fsm.perception import Perception,Observation,Sighting
from dogfight.fsm.controller import BattleFSM
from dogfight.teleop.config import load_settings
from dogfight.teleop.laser import LaserEmitter
from dogfight.teleop.combat import LiveBattleReferee
from dogfight.teleop.keyboard import DualDogKeyboard
from dogfight_v0.agents.proxy_agent import ProxyAgent
from dogfight_v0.arena.test_map import TestMap as Arena
from dogfight_v0.battle.types import Pose2D,IntelRecord,VelocityCommand

class Logger:
    def __init__(self):self.events=[]
    def log(self,t,kind,**kw):self.events.append((t,kind,kw))

def setup():
    settings,_=load_settings('configs/teleop/fsm_battle.yaml')
    agents={n:ProxyAgent(n,'/World/Agents/'+n) for n in settings['participants']}
    for n,x in zip(agents,(-2,0,2)):agents[n].reset(Pose2D(x,-3,0))
    return settings,agents,Logger()

def test_astar_wall_detour_and_simplification():
    planner=GridPlanner(Arena())
    result=planner.plan((-2,0),(2,0));assert result.valid and len(result.points)>2
    assert all(planner.clear(a,b) for a,b in zip(result.points,result.points[1:]))
    assert any(abs(y)>2 for x,y in result.points)
    assert not planner.plan((0,0),(2,0)).valid
    assert planner.plan((-2,0),(-2,0)).reason=='already_there'
    assert planner.plan((-2,0),(0,0)).reason=='goal_blocked'
    assert planner.plan((-9,0),(2,0)).reason=='start_blocked'

def test_unreachable_goal_and_no_corner_cutting():
    from dogfight_v0.arena.test_map import WallSpec
    arena=Arena();arena.walls=[WallSpec('/wall',(0,0,1),(.4,10,2))]
    planner=GridPlanner(arena)
    assert planner.plan((-2,0),(2,0)).reason=='unreachable'
    assert not planner.clear((-.7,-.7),(.7,.7))

def test_intel_not_live_and_invisible_fields_redacted_and_reset():
    cfg,agents,logger=setup()
    # Opaque wall blocks every candidate, independent of truth position.
    p=Perception(agents,lambda *args:[dict(path='/wall',distance=.1)],cfg['autonomy'],logger)
    first=p.observe(0)['dog_a'];old=first.intel['dog_b']
    agents['dog_b'].reset(Pose2D(1,-2,0))
    second=p.observe(4.99)['dog_a'];assert second.intel['dog_b']==old
    sight=second.sightings['dog_b'];assert not sight.visible
    assert sight.target_position_xy is sight.distance_m is sight.yaw_error_rad is None
    assert p.observe(5)['dog_a'].intel['dog_b'].x==1
    assert [t for t,k,_ in logger.events if k=='INTEL_UPDATE']==[0,5]
    p.reset();assert p.observe(0)['dog_a'].intel_timestamp==0

def test_visibility_range_fov_occluders_and_death():
    cfg,agents,logger=setup();blocked=[False]
    p=Perception(agents,lambda *a:[dict(path=agents['dog_c'].prim_path+'/base',distance=.1)] if blocked[0] else [],cfg['autonomy'],logger)
    assert p.observe(0)['dog_a'].sightings['dog_b'].target_position_xy==(0,-3)
    blocked[0]=True;assert not p.observe(.1)['dog_a'].sightings['dog_b'].visible
    blocked[0]=False;agents['dog_a'].reset(Pose2D(-2,-3,pi));assert not p.observe(.2)['dog_a'].sightings['dog_b'].visible
    agents['dog_a'].reset(Pose2D(-2,-3,0));agents['dog_b'].reset(Pose2D(5,-3,0));assert not p.observe(.3)['dog_a'].sightings['dog_b'].visible
    agents['dog_b'].set_alive(False);assert 'dog_b' in p.observe(.4)['dog_a'].confirmed_dead

def observation(pose=Pose2D(-2,-3,0),position=(0,-3),visible=False,t=0,alive=True):
    return Observation(pose,alive,{'dog_b':IntelRecord('dog_b',*position,t,True)},
        {'dog_b':Sighting('dog_b',visible,2. if visible else None,0. if visible else None,position if visible else None,t)},frozenset(),t)

def test_fsm_search_attack_last_seen_dead_and_fire_only_requests():
    cfg,_,logger=setup();f=BattleFSM('dog_a',GridPlanner(Arena()),cfg['autonomy'],logger)
    cmd,fire=f.update(observation(),0);assert f.state=='SEARCH' and f.path and not fire
    cmd,fire=f.update(observation(visible=True,t=1),1);assert f.state=='ATTACK' and fire and cmd.vx==0
    o=observation(t=1.1);o=replace(o,intel={})
    f.update(o,1.1);assert f.state=='SEARCH' and f.goal==(0,-3)
    f.update(replace(o,confirmed_dead=frozenset(['dog_b'])),1.2);assert f.target is None and not f.path
    cmd,fire=f.update(replace(o,alive=False),1.3);assert f.state=='DEAD' and cmd==VelocityCommand() and not fire

def test_replanning_throttled_target_moved_and_recovery():
    cfg,_,logger=setup();f=BattleFSM('dog_a',GridPlanner(Arena()),cfg['autonomy'],logger)
    for t in (0,.1,.2):f.update(observation(position=(2,-3),t=t),t)
    assert len([e for e in logger.events if e[1]=='PATH_PLAN'])==1
    f.update(observation(position=(2, -2),t=1),1)
    assert len([e for e in logger.events if e[1]=='PATH_PLAN'])==2
    # Unmoving own position with sustained forward demand exercises recovery.
    for i in range(11,61):f.update(observation(position=(2,-3),t=i/10),i/10)
    assert any(k=='NAV_STUCK' for _,k,_ in logger.events)
    f.reset();assert f.memory=={} and f.path==[] and f.state=='PATROL'

def test_range_render_nearest_and_damage_share_query_limit():
    cfg,agents,logger=setup();limits=[]
    def query(origin,direction,limit):
        limits.append(limit)
        return [dict(path=agents['dog_a'].prim_path+'/base',distance=.01),dict(path=agents['dog_b'].prim_path+'/base',distance=1.8),dict(path=agents['dog_c'].prim_path+'/base',distance=2.7)] if origin[0]<-1 else []
    b=LiveBattleReferee(agents,query,cfg['battle'],logger)
    laser=LaserEmitter(agents['dog_a'],dict(max_range=3.,raycast_enabled=True,enabled=True),query)
    b.step(.02,fire_requests={'dog_a':True});hit=laser.update()
    assert b.health.get_health('dog_b')==80 and b.health.get_health('dog_c')==100 and hit.distance==1.8
    assert limits and set(limits)=={3.}
    b.reset();b.step(.02,fire_requests={});assert all(b.health.get_health(n)==100 for n in agents)
    far=lambda *args:[dict(path=agents['dog_b'].prim_path+'/base',distance=3.01)]
    b=LiveBattleReferee(agents,far,cfg['battle'],logger);b.step(.02,fire_requests={'dog_a':True})
    assert b.health.get_health('dog_b')==100
    assert LaserEmitter(agents['dog_a'],dict(max_range=3.,raycast_enabled=True,enabled=True),far).update().distance==3

def test_v_toggle_key_repeat_and_pause_reset_unchanged():
    cfg,_,_=setup();keys=DualDogKeyboard(cfg['teleop'])
    assert keys.navigation_visible
    keys.event('V');keys.event('V');assert not keys.navigation_visible
    keys.event('V',False);keys.event('V');assert keys.navigation_visible
    keys.event('SPACE');assert keys.estop
    keys.event('C');assert not keys.estop

def test_follower_cannot_skip_waypoint_through_inflated_wall_corner():
    from dogfight.fsm.navigation import PathFollower
    cfg,_,_=setup();planner=GridPlanner(Arena(),radius=.5)
    follower=PathFollower(cfg['autonomy']);path=[(-.8,-2.2),(.8,-2.2)]
    assert planner.clear(*path)
    assert follower.advance(planner,(-.8,-1.9),path,0)==0
    assert follower.advance(planner,(-.8,-2.18),path,0)==1

def test_planning_drift_reserve_does_not_weaken_tracking_body_collision():
    planner=GridPlanner(Arena(),radius=.6,tracking_radius=.4)
    assert not planner.clear((-.65,-1),(-.65,-2.4))
    assert planner.tracking_clear((-.65,-1),(-.65,-2.4))
    assert not planner.tracking_clear((-.5,-1),(-.5,-2.4))

def test_feedback_repair_uses_measured_start_and_cannot_escape_through_wall():
    planner=GridPlanner(Arena(),radius=.6,tracking_radius=.4)
    repaired=planner.plan_from_feedback((-.65,-1),(-2,-3))
    assert repaired.valid and repaired.points[0]==(-.65,-1)
    assert all(planner.tracking_clear(a,b) for a,b in zip(repaired.points,repaired.points[1:]))
    assert not planner.plan_from_feedback((0,0),(-2,-3)).valid

def test_follower_passed_waypoint_plane_prevents_orbiting():
    from dogfight.fsm.navigation import PathFollower
    cfg,_,_=setup();p=GridPlanner(Arena(),radius=.6,tracking_radius=.4)
    path=[(.6,-2.4),(1.2,-1.8),(2.,0.)]
    assert PathFollower(cfg['autonomy']).advance(p,(1.49,-1.61),path,1)==2
