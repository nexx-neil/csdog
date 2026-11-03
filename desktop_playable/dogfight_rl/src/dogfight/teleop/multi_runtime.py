"""Three real articulations, one shared scheduler, two keyboard pilots, one HP authority."""
import json,math,time,signal,os
from pathlib import Path
from collections import deque
from dataclasses import asdict

def run(app,args,settings,config,out):
    import torch
    import isaaclab.sim as sim_utils
    from isaaclab.sensors import ContactSensor,ContactSensorCfg
    from dogfight_v0.battle.types import Pose2D,VelocityCommand
    from dogfight_v0.config.battle_cfg import BattleConfig
    from dogfight_v0.logging.battle_logger import BattleLogger
    from .runtime import create_robot
    from .maps import create_selected_map,build_map
    from .policy import PolicyLoader,PolicyAdapter
    from .config import load_settings
    from .agent import BattleDogAgent
    from .keyboard import DualDogKeyboard,IsaacKeyboard
    from .laser import PhysXAllHits,LaserEmitter,CylinderLaserVisual
    from .combat import LiveBattleReferee
    autonomous=settings.get('mode')=='fsm_battle'
    ids=settings['participants']
    controller_modes=settings.get('controllers',{'dog_a':'keyboard','dog_b':'keyboard','dog_c':'stand'})
    if args.scenario in ('fsm-recovery','navigation-check'):
        if not autonomous:raise ValueError('fsm-recovery requires fsm_battle')
        controller_modes={'dog_a':'fsm','dog_b':'stand','dog_c':'stand'}
    if any(controller_modes.get(n) not in ('keyboard','fsm','stand') for n in ids):raise ValueError('Invalid controller mode')
    if ids!=['dog_a','dog_b','dog_c']:raise ValueError('Three-dog mode requires canonical dog_a/b/c participants')
    configs={name:load_settings(args.config,robot_id=name)[1] for name in ids}
    c=config['contract'];dt=c['physics_dt'];control_dt=c['policy_dt'];substeps=round(control_dt/dt)
    if any(cfg['contract']!=c or cfg['urdf']!=config['urdf'] for cfg in configs.values()):
        raise ValueError('This integration requires the same verified model/control ABI for all three dogs')
    torch.set_num_threads(2)
    sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=dt,render_interval=substeps,device=args.device,
        enable_scene_query_support=True,physics_material=sim_utils.RigidBodyMaterialCfg(static_friction=1.,dynamic_friction=1.,restitution=0.,friction_combine_mode='multiply',restitution_combine_mode='multiply')))
    arena=create_selected_map(settings);build_map(arena)
    robots={name:create_robot(configs[name],name) for name in ids}
    sensors={name:ContactSensor(ContactSensorCfg(prim_path=f'/World/Agents/{name}/.*',history_length=3,track_air_time=True,update_period=dt)) for name in ids}
    sim.reset()
    for name in ids:robots[name].update(dt);sensors[name].update(dt)
    actors={};adapters={};agents={}
    for name in ids:
        cfg=configs[name];key=cfg['checkpoint']
        if key not in actors:actors[key]=PolicyLoader.load(key,c,robots[name].device)[0]
        adapter=PolicyAdapter(robots[name],actors[key],c);adapters[name]=adapter
        agents[name]=BattleDogAgent(robots[name],adapter,BattleConfig(),agent_id=name,root_height_m=cfg['root_height'],articulation_yaw_from_agent_yaw=c['articulation_yaw_from_agent_yaw'],prim_path=f'/World/Agents/{name}',muzzle_offset=settings['battle']['muzzle_offset'])
    # Runtime-only material bindings; source model/USD and policy bytes are unchanged.
    import omni.usd
    from pxr import UsdShade,Sdf
    stage=omni.usd.get_context().get_stage()
    colors={'dog_a':(.85,.15,.15),'dog_b':(.15,.4,.9),'dog_c':(.15,.75,.3)}
    for name in ids:
        mat=UsdShade.Material.Define(stage,f'/World/IdentityColors/{name}')
        shader=UsdShade.Shader.Define(stage,f'/World/IdentityColors/{name}/Shader');shader.CreateIdAttr('UsdPreviewSurface')
        shader.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(colors[name]);shader.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(.65)
        mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(),'surface')
        UsdShade.MaterialBindingAPI.Apply(stage.GetPrimAtPath(agents[name].prim_path)).Bind(mat,bindingStrength=UsdShade.Tokens.strongerThanDescendants)
    controls=DualDogKeyboard(settings['teleop']);controls.emergency_stop()
    keyboard=IsaacKeyboard(controls) if not args.headless and args.scenario=='interactive' else None
    query=PhysXAllHits();logger=BattleLogger(out,'combat_events',echo=False)
    referee=LiveBattleReferee(agents,query,settings['battle'],logger)
    # One authority for physical and rendered range, also in keyboard mode.
    settings['laser']['max_range']=referee.config.weapon_range_m
    brains={};perception=None;routes=None;next_decision=0.;next_visual=0.;fire_requests={};commands={}
    if autonomous:
        from dogfight.fsm.navigation import GridPlanner
        from dogfight.fsm.controller import BattleFSM
        from dogfight.fsm.perception import Perception
        nav=settings['autonomy'];nav['weapon_range_m']=referee.config.weapon_range_m
        if not (0<nav['attack_enter_m']<nav['attack_exit_m']<nav['weapon_range_m']):raise ValueError('Attack hysteresis must fit inside weapon range')
        planner=GridPlanner(arena,nav['grid_resolution_m'],nav['body_radius_m']+nav['tracking_margin_m'],tracking_radius=nav['body_radius_m'])
        perception=Perception(agents,query,nav,logger)
        brains={n:BattleFSM(n,planner,nav,logger) for n in ids if controller_modes[n]=='fsm'}
        if not args.headless:
            from dogfight.fsm.visualization import RouteVisuals
            routes=RouteVisuals(ids,nav)
    lasers={name:LaserEmitter(agent,dict(settings['laser']),query,None if args.headless else CylinderLaserVisual(settings['laser']['radius'],f'/World/Lasers/{name}')) for name,agent in agents.items()}
    fpv=None;hud=None;held=set();resets=0
    spawns=arena.get_spawn_points()
    if len(spawns)<3:raise ValueError('Map needs three distinct spawn points')
    def reset(poses=None):
        nonlocal resets,next_decision,next_visual
        poses=poses or dict(zip(ids,spawns[:3]))
        if len({(p.x,p.y) for p in poses.values()})!=3 or any(not arena.is_position_valid(p.x,p.y) for p in poses.values()):raise ValueError('Invalid/overlapping map spawns')
        for name in ids:
            agents[name].reset(poses[name]);robots[name].reset();sensors[name].reset()
            robots[name].set_joint_position_target(robots[name].data.default_joint_pos.clone());robots[name].write_data_to_sim()
        held.clear();referee.reset();controls.emergency_stop();controls.reset_requested=False
        if perception:perception.reset()
        for brain in brains.values():brain.reset()
        commands.clear();fire_requests.clear();next_decision=0.;next_visual=0.
        if routes:routes.clear()
        if fpv:fpv.reset_tracking()
        resets+=1
        if autonomous:logger.log(0.,'AUTONOMY_RESET',policy_steps={n:a.steps for n,a in adapters.items()},intel_next_s=0.,paths={n:b.path for n,b in brains.items()})
    reset()
    sim.set_camera_view((9,-12,12),(0,0,.25))
    if not args.headless:
        from .multi_hud import ThreeDogHUD
        from .first_person import StackedFirstPersonViews
        hud=ThreeDogHUD(settings['battle'],autonomous)
        if settings['first_person']['enabled']:fpv=StackedFirstPersonViews(agents,settings['first_person'])
    # Let Kit finish processing newly authored materials/cameras, then explicitly
    # reset the round so GUI stage initialization cannot restore asset-origin poses.
    if not args.headless:sim.render();reset();sim.forward()
    def stop_signal(signum,frame):controls.emergency_stop();controls.quit_requested=True
    for sig in (signal.SIGINT,signal.SIGTERM):signal.signal(sig,stop_signal)
    identity=dict(pid=os.getpid(),mode='fsm_battle' if autonomous else 'three_real_dog_battle',shared_physics=True,physics_dt=dt,policy_dt=control_dt,physics_device=args.device,
        agents={name:dict(urdf=configs[name]['urdf'],checkpoint=configs[name]['checkpoint'],prim_path=agents[name].prim_path,joints=list(robots[name].joint_names),controlled_order=c['joint_order'],mass_kg=float(robots[name].root_physx_view.get_masses().sum()),control=controller_modes[name]) for name in ids})
    (out/'identity.json').write_text(json.dumps(identity,indent=2));print('THREE_DOG_READY '+str(out),flush=True)
    trajectory=(out/'navigation_trace.jsonl').open('w') if autonomous else None
    if autonomous and args.autostart:controls.event('C')
    trace=deque(maxlen=6000);frame=0;start=time.monotonic();min_heights={name:100. for name in ids};max_tilts={name:0. for name in ids}
    # Bounded validation modes explicitly inject controller commands or reset test poses.
    if args.scenario=='combat':
        # Clear lane from existing map data: first two points share the lower spawn y.
        a=spawns[0];reset({'dog_a':Pose2D(a.x,a.y,0.),'dog_b':Pose2D(a.x+2.,a.y,math.atan2(1.2,-1.)),
            'dog_c':Pose2D(a.x+1.,a.y+1.2,math.atan2(-1.2,-1.))})
        controls.event('C')
    if args.scenario=='occlusion':
        wall=arena.get_navigation_data()['walls'][0]
        reset({'dog_a':Pose2D(wall.center[0]-1.3,wall.center[1],0.),'dog_b':Pose2D(wall.center[0]+1.3,wall.center[1],math.pi),'dog_c':spawns[2]})
        controls.event('C')
    if args.scenario=='wall':
        wall=arena.get_navigation_data()['walls'][0]
        reset({'dog_a':Pose2D(wall.center[0]-.9,wall.center[1],0.),'dog_b':spawns[1],'dog_c':spawns[2]})
        controls.event('C');controls.event('W')
    if args.scenario=='fsm-recovery':
        # Dedicated physical obstruction fixture, not a competition round.
        # A navigates toward C's intel; B's real corpse is an unmodelled obstacle.
        for _ in range(20):
            for robot in robots.values():robot.write_data_to_sim()
            sim.step(render=False)
            for n in ids:robots[n].update(dt);sensors[n].update(dt)
        a=spawns[0];reset({'dog_a':Pose2D(a.x,a.y,0.),'dog_b':Pose2D(a.x+1.2,a.y,0.),'dog_c':Pose2D(a.x+4,a.y,math.pi)})
        referee.health.kill('dog_b');agents['dog_b'].set_alive(False)
        logger.log(0.,'VALIDATION_OBSTRUCTION',target_id='dog_b',fixture='corpse; no world or root constraints')
        controls.event('C');sim.forward()
    try:
        if args.scenario=='navigation-check':
            from dogfight.fsm.physical_validation import navigation_check
            navigation_check(sim,robots,sensors,agents,arena,reset,dt,out,settings['autonomy'],routes,referee,hud,controls,args.headless)
            controls.quit_requested=True
        if args.scenario=='range-check':
            from dogfight.fsm.physical_validation import range_checks
            range_checks(sim,robots,sensors,agents,referee,lasers,arena,reset,dt,out)
            controls.quit_requested=True
        while app.is_running() and not controls.quit_requested:
            if args.duration and frame*control_dt>=args.duration:break
            if keyboard:keyboard.poll()
            else:controls.heartbeat()
            if args.scenario=='dual-motion':
                if frame==0:controls.event('C');controls.event('W');controls.event('NUMPAD_2')
                if frame==150:controls.event('W',False);controls.event('NUMPAD_2',False);controls.event('A');controls.event('NUMPAD_6')
                if frame==250:controls.event('SPACE')
            if args.scenario=='wall':
                if frame==400:controls.event('SPACE')
                if frame==450:controls.event('R')
            if controls.reset_requested:reset();sim.forward()
            if perception and not referee.over and referee.time_s+1e-8>=next_decision:
                observations=perception.observe(referee.time_s)
                for name,brain in brains.items():commands[name],fire_requests[name]=brain.update(observations[name],referee.time_s)
                next_decision=referee.time_s+settings['autonomy']['decision_period_s']
            for name,agent in agents.items():
                if controller_modes[name]=='stand' or args.scenario in ('combat','occlusion') or not agent.is_alive() or referee.over:
                    agent.stop()
                    if name not in held:
                        target=robots[name].data.default_joint_pos.clone() if agent.is_alive() and not referee.over else robots[name].data.joint_pos.clone()
                        robots[name].set_joint_position_target(target);held.add(name)
                else:
                    held.discard(name)
                    command=(commands.get(name,VelocityCommand()) if controller_modes[name]=='fsm' else controls.command_for(name,control_dt))
                    agent.set_velocity_command(VelocityCommand() if controls.estop else command);agent.update(control_dt)
            # Apply all three targets before advancing one shared world step.
            for sub in range(substeps):
                for robot in robots.values():robot.write_data_to_sim()
                if not sim.is_playing():controls.emergency_stop();sim.play()
                sim.step(render=False)
                for name in ids:robots[name].update(dt);sensors[name].update(dt)
            # Publish current GPU articulation link poses before CPU PhysX scene queries.
            sim.forward()
            referee.step(control_dt,paused=controls.estop,fire_requests=({n:(fire_requests.get(n,False) if controller_modes[n]=='fsm' else controller_modes[n]=='keyboard') for n in ids} if autonomous else None))
            for name,brain in brains.items():
                if not agents[name].is_alive():
                    brain.transition('DEAD',referee.time_s);brain.target=None;brain.goal=None;brain.distance=None;brain.visible=False;brain.clear_path('dead');fire_requests[name]=False
                elif referee.over:
                    brain.clear_path('round_over');brain.target=None;brain.goal=None;brain.distance=None;brain.visible=False;brain.fire=False;fire_requests[name]=False
                elif brain.target and not agents[brain.target].is_alive():
                    brain.target=None;brain.goal=None;brain.clear_path('target_dead');brain.fire=False;fire_requests[name]=False;commands[name]=VelocityCommand()
            hits={}
            for name,laser in lasers.items():
                laser.config['enabled']=settings['laser']['enabled'] and agents[name].is_alive()
                hit=laser.update();hits[name]=dict(path=hit.object_path,distance=hit.distance)
            state=referee.state()
            if brains:state['navigation']={n:b.status() for n,b in brains.items()}
            if routes and (referee.over or frame*control_dt+1e-8>=next_visual):
                routes.update(agents,brains,controls.navigation_visible);next_visual=frame*control_dt+settings['autonomy']['visual_period_s']
            if fpv:fpv.update(control_dt,state if frame%10==0 else None)
            if hud and frame%10==0:hud.update(state,agents,controls)
            if not args.headless and frame%2==0:sim.render()
            agent_rows={}
            for name in ids:
                d=robots[name].data;z=float(d.root_pos_w[0,2]);tilt=float(d.projected_gravity_b[0,:2].norm())
                min_heights[name]=min(min_heights[name],z);max_tilts[name]=max(max_tilts[name],tilt)
                agent_rows[name]=dict(pose=asdict(agents[name].get_pose()),command=asdict(agents[name].last_velocity_command),
                    actual_velocity=[float(d.root_lin_vel_b[0,0]),float(d.root_lin_vel_b[0,1]),float(d.root_ang_vel_b[0,2])],root_z=z,tilt=tilt,**state['agents'][name],laser=hits[name])
                if not math.isfinite(z):raise RuntimeError(f'Nonfinite robot state: {name}')
                if agents[name].is_alive() and (z<.2 or tilt>.85):controls.emergency_stop('robot_instability:'+name)
            record=dict(t=round((frame+1)*control_dt,4),match=state,agents=agent_rows,estop=controls.estop,stop_reason=controls.last_stop_reason)
            if fpv:record['first_person']=fpv.last
            if routes and frame%25==0:record['route_visuals']=routes.diagnostics()
            if frame%5==0:
                trace.append(record)
                if trajectory:trajectory.write(json.dumps(record)+'\n')
            if frame%25==0:(out/'status.json').write_text(json.dumps(record))
            frame+=1
            if autonomous and args.exit_on_result and referee.over:break
            if not args.headless:
                target=start+frame*control_dt
                if time.monotonic()<target:time.sleep(min(control_dt,target-time.monotonic()))
    finally:
        for agent in agents.values():agent.stop()
        if trajectory:trajectory.close()
        if routes:routes.clear()
        if keyboard:keyboard.close()
        if fpv:fpv.close()
        if hud:hud.close()
        summary=dict(mode='fsm_battle' if autonomous else 'three_real_dog_battle',scenario=args.scenario,frames=frame,sim_seconds=frame*control_dt,wall_seconds=time.monotonic()-start,
            reset_count=resets,minimum_root_z=min_heights,maximum_tilt=max_tilts,match=referee.state(),
            event_counts={kind:sum(e.event_type==kind for e in logger.events) for kind in ('SHOT_FIRED','DAMAGE','DEATH','ROUND_END')},
            first_person_count=len(fpv.views) if fpv else 0,first_person_docked=fpv.docked if fpv else False,
            navigation_visible=controls.navigation_visible,policy_steps={n:a.steps for n,a in adapters.items()},
            main_camera_preserved=(str(fpv.main.viewport_api.camera_path)==fpv.main_camera) if fpv and fpv.main else None)
        (out/'metrics.json').write_text(json.dumps(summary,indent=2));(out/'trace.json').write_text(json.dumps(list(trace)))
        print('THREE_DOG_RESULT '+json.dumps(summary),flush=True)
    return 0
