"""Truth stays here. Controllers receive only own pose and authorized frozen records."""
from dataclasses import dataclass
from math import atan2, hypot, radians, dist
from dogfight_v0.battle.intel_service import IntelService
from dogfight_v0.battle.types import normalize_angle
from dogfight_v0.battle.ray_query import agent_id_from_path
from dogfight.teleop.combat import ExcludingRayQuery

@dataclass(frozen=True)
class Sighting:
    target_id: str
    visible: bool
    distance_m: float | None
    yaw_error_rad: float | None
    target_position_xy: tuple | None
    timestamp_s: float

@dataclass(frozen=True)
class Observation:
    pose: object
    alive: bool
    intel: dict
    sightings: dict
    confirmed_dead: frozenset
    intel_timestamp: float | None

class Perception:
    def __init__(self,agents,query,config,logger):
        self.agents=agents;self.query=query;self.cfg=config;self.logger=logger
        self.intel=IntelService(config['intel_period_s']);self.reset()
    def reset(self):self.intel.reset();self.previous={}
    def observe(self,t):
        if self.intel.update(t,self.agents):self.logger.log(t,'INTEL_UPDATE',snapshot_time_s=t)
        dead=frozenset(n for n,a in self.agents.items() if not a.is_alive());result={}
        for name,observer in self.agents.items():
            op=observer.get_pose();sightings={};q=ExcludingRayQuery(self.query,observer.prim_path)
            for target_id,target in self.agents.items():
                if target_id==name:continue
                tp=target.get_pose();dx,dy=tp.x-op.x,tp.y-op.y;distance=hypot(dx,dy)
                yaw=normalize_angle(atan2(dy,dx)-op.yaw)
                visible=False
                if observer.is_alive() and target.is_alive() and distance<=self.cfg['vision_max_range_m'] and abs(yaw)<=radians(self.cfg['vision_fov_deg']/2):
                    origin=observer.get_muzzle_origin_world()
                    end=(tp.x,tp.y,target.get_muzzle_origin_world()[2]);length=dist(origin,end)
                    if length<1e-8:visible=True
                    else:
                        direction=tuple((end[i]-origin[i])/length for i in range(3))
                        hit=q.raycast_closest(origin,direction,length)
                        visible=not hit.hit or agent_id_from_path(hit.object_path,self.agents)==target_id
                sighting=Sighting(target_id,visible,distance if visible else None,yaw if visible else None,(tp.x,tp.y) if visible else None,t)
                sightings[target_id]=sighting
                key=(name,target_id)
                if visible!=self.previous.get(key,False):self.logger.log(t,'TARGET_VISIBLE' if visible else 'TARGET_LOST',agent_id=name,target_id=target_id)
                self.previous[key]=visible
            # Public deaths contain no position. Snapshots for alive observers/targets only.
            intel={n:r for n,r in self.intel.get_snapshot_for(name).items() if r.alive and n not in dead} if observer.is_alive() else {}
            result[name]=Observation(op,observer.is_alive(),intel,sightings,dead,self.intel.last_update_s)
        return result
