"""Map-driven, inflated 2D A* with collision-checked simplification."""
from dataclasses import dataclass, field
import heapq
import math

@dataclass
class Plan:
    valid: bool
    reason: str
    points: list = field(default_factory=list)

class GridPlanner:
    def __init__(self, arena, resolution=.2, radius=.40, tracking_radius=None):
        if resolution <= 0 or radius <= 0:raise ValueError('Positive grid resolution and body radius required')
        self.arena=arena;self.resolution=resolution;self.radius=radius
        self.bounds=arena.get_bounds()
        self.boxes=[(a-radius,b+radius,c-radius,d+radius) for a,b,c,d in (w.bounds_xy for w in arena.get_navigation_data()['walls'])]
        a,b,c,d=self.bounds
        self.nx=math.floor((b-a)/resolution)+1;self.ny=math.floor((d-c)/resolution)+1
        self.free={(i,j) for i in range(self.nx) for j in range(self.ny) if self.valid(self.point((i,j)))}
        # Planned clearance includes a drift reserve. Tracking still enforces the body envelope.
        self.tracker=GridPlanner(arena,resolution,tracking_radius) if tracking_radius is not None else None
    def tracking_clear(self,p,q):return self.tracker.clear(p,q) if self.tracker else self.clear(p,q)
    def valid(self,p):
        x,y=p;a,b,c,d=self.bounds;r=self.radius
        return a+r<=x<=b-r and c+r<=y<=d-r and self.arena.is_position_valid(x,y) and not any(l<=x<=h and lo<=y<=hi for l,h,lo,hi in self.boxes)
    def clear(self,p,q):
        if not self.valid(p) or not self.valid(q):return False
        # Segment/AABB slab intersection includes grazing contacts.
        for a,b,c,d in self.boxes:
            low,high=0.,1.
            for origin,delta,lo,hi in ((p[0],q[0]-p[0],a,b),(p[1],q[1]-p[1],c,d)):
                if abs(delta)<1e-12:
                    if origin<lo or origin>hi:low,high=1.,0.;break
                else:
                    u,v=sorted(((lo-origin)/delta,(hi-origin)/delta));low=max(low,u);high=min(high,v)
            if low<=high:return False
        # Respect additional map-defined forbidden areas, also in smoothed paths.
        n=max(1,math.ceil(math.dist(p,q)/(self.resolution/3)))
        return all(self.arena.is_position_valid(p[0]+(q[0]-p[0])*i/n,p[1]+(q[1]-p[1])*i/n) for i in range(n+1))
    def point(self,c):return (self.bounds[0]+c[0]*self.resolution,self.bounds[2]+c[1]*self.resolution)
    def cell(self,p):
        i=round((p[0]-self.bounds[0])/self.resolution);j=round((p[1]-self.bounds[2])/self.resolution)
        candidates=[(x,y) for x in range(i-1,i+2) for y in range(j-1,j+2) if (x,y) in self.free and self.clear(p,self.point((x,y)))]
        return min(candidates,key=lambda c:math.dist(p,self.point(c))) if candidates else None
    def plan_from_feedback(self,start,goal):
        result=self.plan(start,goal)
        if result.reason!='start_blocked' or not self.tracker or not self.tracker.valid(start):return result
        # Recover only the extra drift reserve, never a body/obstacle overlap.
        candidates=sorted((c for c in self.free if math.dist(start,self.point(c))<=self.radius-self.tracker.radius+2*self.resolution),key=lambda c:math.dist(start,self.point(c)))
        for cell in candidates:
            point=self.point(cell)
            if not self.tracker.clear(start,point):continue
            repaired=self.plan(point,goal)
            if repaired.valid:return Plan(True,'start_margin_recovery',[tuple(start)]+repaired.points)
        return result
    def plan(self,start,goal):
        start=tuple(start);goal=tuple(goal)
        if not self.valid(start):return Plan(False,'start_blocked')
        if not self.valid(goal):return Plan(False,'goal_blocked')
        if math.dist(start,goal)<1e-6:return Plan(True,'already_there',[goal])
        s,g=self.cell(start),self.cell(goal)
        if s is None or g is None:return Plan(False,'grid_attachment_failed')
        frontier=[(0.,s)];cost={s:0.};parents={s:None};closed=set()
        while frontier:
            _,u=heapq.heappop(frontier)
            if u in closed:continue
            if u==g:break
            closed.add(u)
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                v=(u[0]+dx,u[1]+dy)
                if v not in self.free or not self.clear(self.point(u),self.point(v)):continue
                nc=cost[u]+math.hypot(dx,dy)
                if nc<cost.get(v,float('inf')):
                    cost[v]=nc;parents[v]=u;heapq.heappush(frontier,(nc+math.dist(v,g),v))
        if g not in parents:return Plan(False,'unreachable')
        chain=[];u=g
        while u is not None:chain.append(self.point(u));u=parents[u]
        raw=[start]+list(reversed(chain))+[goal];result=[start];i=0
        while i<len(raw)-1:
            j=len(raw)-1
            while j>i+1 and not self.clear(raw[i],raw[j]):j-=1
            if not self.clear(raw[i],raw[j]):return Plan(False,'invalid_segment')
            result.append(raw[j]);i=j
        return Plan(True,'ok',result)


class PathFollower:
    """Closed loop planar tracking; own measured pose in, PPO velocity command out."""
    def __init__(self,config):self.cfg=config
    def advance(self,planner,position,path,index):
        while index<len(path):
            tolerance=self.cfg.get('corner_waypoint_tolerance_m',self.cfg['waypoint_tolerance_m']) if index+1<len(path) else self.cfg['waypoint_tolerance_m']
            distance=math.dist(position,path[index])
            passed=False
            if index>0 and index+1<len(path):
                incoming=(path[index][0]-path[index-1][0],path[index][1]-path[index-1][1])
                passed=sum((position[k]-path[index][k])*incoming[k] for k in (0,1))>=0 and distance<=self.cfg['waypoint_tolerance_m']+.15
            if distance>tolerance and not passed:break
            # A tolerance circle may overlap a corner; never skip into an obstructed segment.
            if index+1<len(path) and not planner.tracking_clear(position,path[index+1]):break
            index+=1
        return index
    def command(self,pose,waypoint):
        from dogfight_v0.battle.types import VelocityCommand,normalize_angle
        error=normalize_angle(math.atan2(waypoint[1]-pose.y,waypoint[0]-pose.x)-pose.yaw)
        yaw=0. if abs(error)<self.cfg['yaw_deadband_rad'] else max(-self.cfg['max_yaw_rate'],min(self.cfg['max_yaw_rate'],error*self.cfg['yaw_gain']))
        return VelocityCommand(vx=self.cfg['max_speed'] if abs(error)<self.cfg['drive_yaw_tolerance_rad'] else 0.,yaw_rate=yaw)
