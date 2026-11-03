"""Teleop combat authority reuses V0 HP/weapon rules, independent from input and joints."""
from dogfight_v0.battle.health_system import HealthSystem
from dogfight_v0.battle.weapon_service import WeaponService
from dogfight_v0.battle.types import RayHit
from dogfight_v0.config.battle_cfg import BattleConfig

class ExcludingRayQuery:
    def __init__(self,all_hits,self_path):self.all_hits=all_hits;self.self_path=self_path
    def raycast_closest(self,origin,direction,max_distance):
        hits=[h for h in self.all_hits(origin,direction,max_distance)
              if 0 <= h['distance'] <= max_distance and h['path'] and not (h['path']==self.self_path or h['path'].startswith(self.self_path+'/'))]
        if not hits:return RayHit(False)
        hit=min(hits,key=lambda h:h['distance'])
        return RayHit(True,hit['path'],hit['distance'])

class LiveBattleReferee:
    def __init__(self,agents,all_hits,config,logger):
        self.agents=agents;self.settings=config;self.logger=logger
        self.config=BattleConfig(max_health=config['max_health'],weapon_damage=config['damage'],
            weapon_cooldown_s=config['cooldown_s'],weapon_range_m=config.get('weapon_range_m',config.get('range_m')),round_time_limit_s=config['time_limit_s'])
        self.health=HealthSystem(self.config.max_health)
        self.weapons={name:WeaponService(self.config,ExcludingRayQuery(all_hits,agent.prim_path)) for name,agent in agents.items()}
        self.reset()
    def reset(self):
        self.time_s=0.;self.over=False;self.winner=None;self.draw=False;self.paused=True
        self.health.reset(list(self.agents))
        for name,agent in self.agents.items():agent.set_alive(True);self.weapons[name].reset()
        self.logger.log(0.,'ROUND_START',mode='THREE_REAL_DOG_TELEOP')
    def step(self,dt,paused=False,fire_requests=None):
        self.paused=paused
        if self.over or paused:return
        self.time_s+=dt
        if self.settings['damage_enabled']:
            for name,agent in self.agents.items():
                if fire_requests is not None and not fire_requests.get(name,False):continue
                result=self.weapons[name].fire(agent,self.agents,self.time_s)
                if not result.fired:continue
                self.logger.log(self.time_s,'SHOT_FIRED',agent_id=name,hit_object_path=result.hit_object_path,distance_m=result.distance_m)
                if result.hit:
                    target=result.hit_agent_id
                    hp=self.health.apply_damage(target,result.damage,name)
                    self.logger.log(self.time_s,'DAMAGE',agent_id=target,target_id=name,amount=result.damage,health=hp)
                    if not self.health.is_alive(target):
                        self.agents[target].set_alive(False)
                        self.logger.log(self.time_s,'DEATH',agent_id=target,target_id=name)
        alive=[name for name in self.agents if self.health.is_alive(name)]
        if len(alive)<=1 or self.time_s>=self.config.round_time_limit_s:
            self.over=True;self.winner=alive[0] if len(alive)==1 else None;self.draw=self.winner is None
            for agent in self.agents.values():agent.stop()
            self.logger.log(self.time_s,'ROUND_END',winner=self.winner,draw=self.draw)
    def state(self):
        return dict(time_s=self.time_s,round_over=self.over,winner=self.winner,draw=self.draw,paused=self.paused,
            max_health=self.config.max_health,agents={name:dict(health=self.health.get_health(name),alive=self.health.is_alive(name)) for name in self.agents})
