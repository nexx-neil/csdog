"""Independent, restricted-observation FSM. Outputs velocity and fire requests only."""
from math import dist
from dogfight_v0.battle.types import VelocityCommand
from .navigation import PathFollower

class BattleFSM:
    def __init__(self,agent_id,planner,config,logger):
        self.id=agent_id;self.planner=planner;self.cfg=config;self.logger=logger;self.follower=PathFollower(config);self.reset()
    def reset(self):
        self.state='PATROL';self.target=None;self.goal=None;self.path=[];self.index=0;self.plan_status='idle'
        self.last_plan=-1e9;self.last_intel=None;self.memory={};self.last_goal=None;self.plan_target=None
        self.progress_anchor=None;self.progress_time=0.;self.recover_until=0.;self.recover_count=0
        self.visible=False;self.distance=None;self.command=VelocityCommand();self.fire=False;self.failure_since=None
    def event(self,t,kind,**data):self.logger.log(t,kind,agent_id=self.id,**data)
    def transition(self,state,t):
        if state!=self.state:self.event(t,'FSM_STATE',previous=self.state,state=state);self.state=state
    def clear_path(self,status='idle'):self.path=[];self.index=0;self.plan_status=status
    def update(self,o,t):
        self.command=VelocityCommand();self.fire=False;p=(o.pose.x,o.pose.y)
        if not o.alive:
            self.transition('DEAD',t);self.target=None;self.goal=None;self.distance=None;self.visible=False;self.clear_path('dead');return self.command,False
        for n in o.confirmed_dead:self.memory.pop(n,None)
        for n,r in o.intel.items():
            if n!=self.id and n not in o.confirmed_dead and (n not in self.memory or r.timestamp_s>=self.memory[n][1]):self.memory[n]=((r.x,r.y),r.timestamp_s)
        visible={n:s for n,s in o.sightings.items() if s.visible and n!=self.id and n not in o.confirmed_dead}
        for n,s in visible.items():self.memory[n]=(s.target_position_xy,s.timestamp_s)
        old=self.target
        if visible:
            nearest=min(visible,key=lambda n:visible[n].distance_m)
            # Hold an existing visible target unless another is substantially nearer.
            self.target=old if old in visible and visible[old].distance_m<=visible[nearest].distance_m+self.cfg['target_hold_margin_m'] else nearest
        elif old not in self.memory:
            self.target=min(self.memory,key=lambda n:dist(p,self.memory[n][0])) if self.memory else None
        if self.target!=old:
            self.clear_path();self.last_goal=None;self.recover_count=0;self.failure_since=None
            self.event(t,'TARGET_CHANGED',target_id=self.target,previous=old)
        if self.target is None:
            self.goal=None;self.distance=None;self.visible=False;self.clear_path();self.transition('PATROL',t)
            self.command=VelocityCommand(yaw_rate=self.cfg['search_yaw_rate']);return self.command,False
        self.goal=self.memory[self.target][0];self.distance=dist(p,self.goal);self.visible=self.target in visible
        sight=visible.get(self.target)
        if self.state=='RECOVER' and t<self.recover_until:
            self.command=VelocityCommand(vx=-self.cfg['recover_speed'] if self.recover_until-t>self.cfg['recover_turn_s'] else 0.,yaw_rate=0. if self.recover_until-t>self.cfg['recover_turn_s'] else self.cfg['max_yaw_rate'])
            return self.command,False
        entry=self.cfg['attack_enter_m'];exit_range=self.cfg['attack_exit_m']
        if sight and self.distance<=(exit_range if self.state=='ATTACK' else entry):
            self.transition('ATTACK',t);self.clear_path('aiming')
            yaw=sight.yaw_error_rad
            self.command=VelocityCommand(yaw_rate=self.turn(yaw))
            self.fire=abs(yaw)<=self.cfg['fire_yaw_tolerance_rad'] and self.distance<=self.cfg['weapon_range_m']
            self.progress_anchor=None
            return self.command,self.fire
        self.transition('CHASE' if sight else 'SEARCH',t)
        reason=None
        if self.target!=self.plan_target:reason='target_changed'
        elif self.last_intel!=o.intel_timestamp:reason='intel_update'
        elif self.last_goal is None or dist(self.goal,self.last_goal)>=self.cfg['replan_target_delta_m']:reason='target_moved'
        elif not self.path:reason='no_path'
        elif self.index<len(self.path) and not self.planner.tracking_clear(p,self.path[self.index]):reason='path_invalid'
        if reason and t-self.last_plan>=self.cfg['min_plan_interval_s']:
            result=self.planner.plan_from_feedback(p,self.goal);self.last_plan=t;self.last_goal=self.goal;self.last_intel=o.intel_timestamp;self.plan_target=self.target
            self.path=result.points if result.valid else [];self.index=1 if len(self.path)>1 else 0;self.plan_status=result.reason
            if result.valid:self.failure_since=None
            self.event(t,'PATH_PLAN',target_id=self.target,goal=self.goal,valid=result.valid,reason=result.reason,replan_reason=reason,points=self.path)
        if not self.path:
            if self.failure_since is None:self.failure_since=t
            if t-self.failure_since>=self.cfg['stuck_timeout_s'] and self.recover_count<self.cfg['recover_max_attempts']:
                self.recover_count+=1;self.failure_since=t
                self.transition('RECOVER',t);self.recover_until=t+self.cfg['recover_reverse_s']+self.cfg['recover_turn_s']
                self.event(t,'NAV_STUCK',attempt=self.recover_count,reason='plan_failure')
            else:self.command=VelocityCommand(yaw_rate=self.cfg['search_yaw_rate'])
            return self.command,False
        self.index=self.follower.advance(self.planner,p,self.path,self.index)
        if self.index==len(self.path):
            self.clear_path('arrived');self.command=VelocityCommand(yaw_rate=self.cfg['search_yaw_rate']);self.progress_anchor=None
            return self.command,False
        waypoint=self.path[self.index]
        if not self.planner.tracking_clear(p,waypoint):
            self.clear_path('path_invalid');return self.command,False
        self.command=self.follower.command(o.pose,waypoint)
        speed=self.command.vx
        if self.progress_anchor is None:
            self.progress_anchor=p;self.progress_time=t
        elif dist(p,self.progress_anchor)>=self.cfg['progress_min_m']:
            self.progress_anchor=p;self.progress_time=t;self.recover_count=0
        elif speed==0.:self.progress_time=t
        elif t-self.progress_time>=self.cfg['stuck_timeout_s']:
            self.clear_path('stuck');self.recover_count+=1;self.progress_time=t
            if self.recover_count<=self.cfg['recover_max_attempts']:
                self.transition('RECOVER',t);self.recover_until=t+self.cfg['recover_reverse_s']+self.cfg['recover_turn_s'];self.event(t,'NAV_STUCK',attempt=self.recover_count)
            self.command=VelocityCommand()
        return self.command,False
    def turn(self,error):
        if abs(error)<self.cfg['yaw_deadband_rad']:return 0.
        return max(-self.cfg['max_yaw_rate'],min(self.cfg['max_yaw_rate'],error*self.cfg['yaw_gain']))
    def status(self):
        return dict(state=self.state,target_id=self.target,navigation_goal=self.goal,distance_m=self.distance,visible=self.visible,
                    planning=self.plan_status,path=self.path[self.index:],waypoint=self.path[self.index] if self.index<len(self.path) else None,fire=self.fire)
