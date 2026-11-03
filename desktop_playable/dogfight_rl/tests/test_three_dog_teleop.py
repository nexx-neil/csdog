"""Independent pilots and continuous-laser HP rules; no simulator or weights modified."""
import pytest
from dogfight.teleop.keyboard import DualDogKeyboard
from dogfight.teleop.combat import LiveBattleReferee
from dogfight.teleop.config import load_settings
from dogfight_v0.agents.proxy_agent import ProxyAgent
from dogfight_v0.battle.types import Pose2D,VelocityCommand

@pytest.mark.parametrize('key,vx,yaw',[(8,1,0),(2,-1,0),(4,0,1),(6,0,-1),(7,1,1),(9,1,-1),(1,-1,1),(3,-1,-1),(5,0,0)])
def test_keypad_nine_keys(key,vx,yaw):
    cfg,_=load_settings();c=DualDogKeyboard(cfg['teleop']);c.event(f'NUMPAD_{key}')
    b=c.command_for('dog_b',.02)
    assert (b.vx>0)-(b.vx<0)==vx
    assert (b.yaw_rate>0)-(b.yaw_rate<0)==yaw
    assert c.command_for('dog_a',.02)==VelocityCommand()

def test_pilots_independent_global_stop_and_numrow_ignored():
    cfg,_=load_settings();c=DualDogKeyboard(cfg['teleop'])
    c.event('W');c.event('NUMPAD_2')
    assert c.command_for('dog_a',.02).vx>0 and c.command_for('dog_b',.02).vx<0
    c.event('NUMPAD_5');assert c.command_for('dog_b',.02)==VelocityCommand()
    assert c.command_for('dog_a',.02).vx>0
    c.event('SPACE');c.event('SPACE',False)
    assert c.estop and c.command_for('dog_a',.02)==c.command_for('dog_b',.02)==VelocityCommand()
    c.event('C');c.event('8');assert c.command_for('dog_b',.02)==VelocityCommand()
    c.event('NUMPAD_7');c.focus_lost();assert c.estop
    c.event('R');assert c.reset_requested
    c.reset_requested=False;assert not c.reset_requested
    c.event('ESCAPE');assert c.quit_requested

class Logger:
    def __init__(self):self.events=[]
    def log(self,*args,**kwargs):self.events.append((args,kwargs))

def battle(all_hits):
    agents={n:ProxyAgent(n,f'/World/Agents/{n}') for n in ['dog_a','dog_b','dog_c']}
    for n,x in [('dog_a',0),('dog_b',2),('dog_c',4)]:agents[n].reset(Pose2D(x,0,0))
    cfg=dict(damage_enabled=True,max_health=100.,damage=20.,cooldown_s=1.,range_m=20.,time_limit_s=180.)
    return LiveBattleReferee(agents,all_hits,cfg,Logger())

def test_continuous_laser_damage_cooldown_death_and_reset():
    def hits(origin,*args):
        return [{'path':'/World/Agents/dog_a/base','distance':.1},{'path':'/World/Agents/dog_b/base','distance':1.5}] if origin[0]<1 else []
    b=battle(hits);b.step(.02);assert b.health.get_health('dog_b')==80
    b.step(.5);assert b.health.get_health('dog_b')==80
    for _ in range(4):b.step(1.)
    assert b.health.get_health('dog_b')==0 and not b.agents['dog_b'].is_alive()
    b.reset();assert all(b.health.get_health(n)==100 and a.is_alive() for n,a in b.agents.items())

def test_wall_blocks_damage_and_pause_freezes_time():
    b=battle(lambda *args:[{'path':'/World/Wall','distance':.3},{'path':'/World/Agents/dog_b/base','distance':2.}])
    b.step(.1,paused=True);assert b.time_s==0
    b.step(.1);assert all(b.health.get_health(n)==100 for n in b.agents)

def test_last_survivor_and_timeout():
    b=battle(lambda *args:[])
    for n in ['dog_b','dog_c']:b.health.kill(n);b.agents[n].set_alive(False)
    b.step(.02);assert b.over and b.winner=='dog_a'
    b.reset();b.step(180);assert b.over and b.draw
