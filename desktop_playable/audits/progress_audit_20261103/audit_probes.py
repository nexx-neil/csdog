"""仅CPU、内存规则与URDF只读探针；唯一输出在本审计目录。"""
from pathlib import Path
import sys,json,hashlib,math,xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
R=Path('/home/zxq/robot_projects'); A=Path(__file__).parent
sys.path.insert(0,str(R/'dogfight_rl/src'))
from dogfight_v0.agents.proxy_agent import ProxyAgent
from dogfight_v0.arena.test_map import TestMap
from dogfight_v0.arena.spawn_manager import SpawnManager
from dogfight_v0.battle.types import Pose2D,VelocityCommand
from dogfight_v0.config.battle_cfg import BattleConfig
from dogfight_v0.battle.visibility_service import VisibilityService
from dogfight_v0.battle.ray_query import AnalyticRayQuery
from dogfight_v0.navigation.simple_navigation import SimpleNavigation
from dogfight_v0.battle.battle_manager import BattleManager
from dogfight_v0.battle.health_system import HealthSystem
from dogfight_v0.battle.weapon_service import WeaponService
from dogfight_v0.battle.intel_service import IntelService
from dogfight_v0.battle.scripted_policy import ScriptedBattlePolicy
class MemoryLogger:
 def __init__(self):self.events=[]
 def log(self,*args,**kwargs):self.events.append([args,kwargs])
m=TestMap();c=BattleConfig();agents={n:ProxyAgent(n,'/World/Agents/'+n,position_validator=m.is_position_valid) for n in ('dog_a','dog_b','dog_c')};q=AnalyticRayQuery(m.walls,agents);v=VisibilityService(c,q,agents)
agents['dog_a'].reset(Pose2D(-2,0,0));agents['dog_b'].reset(Pose2D(2,0,math.pi));agents['dog_c'].reset(Pose2D(0,4,0))
z=v.observe_target(agents['dog_a'],agents['dog_b'])
nav=SimpleNavigation(c);nav.set_goal('dog_a',(2,0))
for i in range(1200):agents['dog_a'].set_velocity_command(nav.compute_command(agents['dog_a'],.02));agents['dog_a'].update(.02)
p=agents['dog_a'].get_pose()
results={'invisible_target_information':{'visible':z.visible,'distance_m':z.distance_m,'yaw_error_rad':z.yaw_error_rad,'reconstructed_xy':[-2+z.distance_m*math.cos(z.yaw_error_rad),z.distance_m*math.sin(z.yaw_error_rad)]},'blocked_direct_navigation_24s':{'final_xy':[p.x,p.y],'goal_reached':nav.goal_reached('dog_a')},'proxy_interagent_overlap':{}}
for n in ('dog_a','dog_b'):agents[n].reset(Pose2D(-4,-4,0))
results['proxy_interagent_overlap']={'same_xy_allowed':agents['dog_a'].get_pose()==agents['dog_b'].get_pose()}
# 正式manager与正式规则，解析射线代替PhysX，纯CPU单局与超时。
for name,config in [('baseline',c),('timeout',BattleConfig(round_time_limit_s=.05))]:
 log=MemoryLogger();b=BattleManager(config,m,SpawnManager(),agents,SimpleNavigation(config),IntelService(5),VisibilityService(config,q,agents),WeaponService(config,q),HealthSystem(100),{n:ScriptedBattlePolicy(config) for n in agents},log)
 b.reset(seed=42);b.start_round()
 for i in range(7300):
  b.step(1/60)
  if b.is_round_over():break
 results[name+'_analytic_round']={'state':b.get_match_state(),'event_counts':{kind:sum(e[0][1]==kind for e in log.events) for kind in ['SHOT_FIRED','SHOT_HIT','DAMAGE','DEATH','ROUND_END']}}
 b.reset(seed=43);results[name+'_analytic_round']['reset_health']={n:b.health.get_health(n) for n in agents}
# 使用标准库计算惯量正定主子式，机械真实性另行验证。
u=R/'model/robot.urdf';root=ET.parse(u).getroot();links=[]
for l in root.findall('link'):
 inert=l.find('inertial'); ii=inert.find('inertia');x={k:float(v) for k,v in ii.attrib.items()};a,b,d,e,f,g=[x[k] for k in ('ixx','ixy','ixz','iyy','iyz','izz')];det=a*(e*g-f*f)-b*(b*g-f*d)+d*(b*f-e*d)
 links.append({'name':l.get('name'),'mass':float(inert.find('mass').get('value')),'com':inert.find('origin').attrib,'inertia':x,'positive_definite':a>0 and a*e-b*b>0 and det>0,'visuals':len(l.findall('visual')),'collisions':len(l.findall('collision'))})
results['model']={'sha256':hashlib.sha256(u.read_bytes()).hexdigest(),'links':links,'total_mass':sum(l['mass'] for l in links),'joints':[{'name':j.get('name'),'type':j.get('type'),'parent':j.find('parent').get('link'),'child':j.find('child').get('link'),'axis':j.find('axis').attrib,'limit':j.find('limit').attrib} for j in root.findall('joint')],'mesh_files':len(list((R/'model/meshes').glob('*')))}
(A/'AUDIT_PROBES.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)); print(json.dumps({k:v for k,v in results.items() if k!='model'},ensure_ascii=False,indent=2));print('model',len(links),results['model']['total_mass'],all(l['positive_definite'] for l in links))
