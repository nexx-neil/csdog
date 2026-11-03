"""One shared physics scheduler. Agent.update computes targets, never steps the world."""
import json,math,time,signal
from pathlib import Path
from collections import deque
from dataclasses import asdict


def create_robot(config,robot_id):
    import isaaclab.sim as sim
    from isaaclab.assets import Articulation,ArticulationCfg
    from isaaclab.actuators import ImplicitActuatorCfg
    from dogfight.common.paths import ASSETS
    c=config['contract']
    cfg=ArticulationCfg(prim_path='/World/Agents/'+robot_id,spawn=sim.UrdfFileCfg(
        asset_path=config['urdf'],usd_dir=str(ASSETS/'csdog_12dof/peer_teleop_v1/usd'),usd_file_name='csdog.usd',
        fix_base=False,merge_fixed_joints=False,self_collision=False,replace_cylinders_with_capsules=True,
        activate_contact_sensors=True,
        rigid_props=sim.RigidBodyPropertiesCfg(disable_gravity=False,retain_accelerations=False,
            linear_damping=0.,angular_damping=0.,max_linear_velocity=20.,max_angular_velocity=30.,max_depenetration_velocity=2.),
        articulation_props=sim.ArticulationRootPropertiesCfg(enabled_self_collisions=False,solver_position_iteration_count=8,solver_velocity_iteration_count=2),
        joint_drive=sim.UrdfConverterCfg.JointDriveCfg(gains=sim.UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=0.,damping=0.))),
        init_state=ArticulationCfg.InitialStateCfg(pos=(0,0,config['root_height']),joint_pos={n:0. for n in c['joint_order']}),
        actuators={'legs':ImplicitActuatorCfg(joint_names_expr=c['joint_order'],stiffness=c['stiffness'],damping=c['damping'],effort_limit_sim=c['effort_limit'],velocity_limit_sim=c['velocity_limit'])},
        soft_joint_pos_limit_factor=.9)
    return Articulation(cfg)


def run(app,args,settings,config,out):
    import torch
    import isaaclab.sim as sim_utils
    from isaaclab.sensors import ContactSensor,ContactSensorCfg
    from dogfight_v0.battle.types import Pose2D,VelocityCommand
    from dogfight_v0.config.battle_cfg import BattleConfig
    from dogfight_v0.agents.agent_interface import AgentInterface
    from .maps import create_selected_map,build_map
    from .policy import PolicyLoader,PolicyAdapter
    from .agent import TeleopRealDogAgent
    from .keyboard import KeyboardTeleopController,IsaacKeyboard
    from .laser import LaserEmitter,PhysXAllHits,CylinderLaserVisual
    torch.set_num_threads(2)
    c=config['contract'];dt=c['physics_dt'];control_dt=c['policy_dt'];decimation=round(control_dt/dt)
    sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=dt,render_interval=decimation,device=args.device,
        enable_scene_query_support=True,physics_material=sim_utils.RigidBodyMaterialCfg(static_friction=1.,dynamic_friction=1.,restitution=0.,friction_combine_mode='multiply',restitution_combine_mode='multiply')))
    arena=create_selected_map(settings);build_map(arena)
    robot=create_robot(config,settings["robot"])
    contacts=ContactSensor(ContactSensorCfg(prim_path='/World/Agents/'+settings['robot']+'/.*',history_length=3,track_air_time=True,update_period=dt))
    sim.reset();robot.update(dt);contacts.update(dt)
    actor,metadata=PolicyLoader.load(config['checkpoint'],c,robot.device)
    adapter=PolicyAdapter(robot,actor,c)
    agent=TeleopRealDogAgent(robot,adapter,BattleConfig(),agent_id=settings['robot'],root_height_m=config['root_height'],
        articulation_yaw_from_agent_yaw=c['articulation_yaw_from_agent_yaw'],prim_path='/World/Agents/'+settings['robot'],muzzle_offset=config['muzzle_offset'])
    if not isinstance(agent,AgentInterface):raise TypeError('Real dog violates V0 AgentInterface')
    spawn=arena.get_spawn_points()[settings['map']['spawn_index']]
    if not arena.is_position_valid(spawn.x,spawn.y):raise ValueError('Invalid map spawn')
    first_person=None
    def reset(pose=spawn):
        if not arena.is_position_valid(pose.x,pose.y):raise ValueError('Reset pose is invalid')
        agent.reset(pose);robot.reset();contacts.reset()
        if first_person is not None:first_person.reset_tracking()
        robot.set_joint_position_target(robot.data.default_joint_pos.clone());robot.write_data_to_sim()
    reset()
    sim.set_camera_view((spawn.x+2.5,spawn.y-2.5,1.9),(spawn.x,spawn.y,.35))
    visual=CylinderLaserVisual(settings['laser']['radius']) if not args.headless else None
    laser=LaserEmitter(agent,settings['laser'],PhysXAllHits(),visual)
    control=KeyboardTeleopController(settings['teleop']);keyboard=None;hud=None
    if not args.headless and args.scenario=='interactive':keyboard=IsaacKeyboard(control)
    if not args.headless:
        from .hud import TeleopHUD
        hud=TeleopHUD()
        if settings.get("first_person",{}).get("enabled",True):
            from .first_person import FirstPersonView
            first_person=FirstPersonView(agent,settings.get("first_person",{}))
    def exit_signal(signum,frame):control.quit_requested=True;control.emergency_stop()
    for sig in (signal.SIGINT,signal.SIGTERM):signal.signal(sig,exit_signal)
    trace=deque(maxlen=6000);segments=[];min_z=100.;max_tilt=0.;start=time.monotonic();frame=0;reset_count=0
    identity=dict(pid=__import__("os").getpid(),model=config['urdf'],checkpoint=config['checkpoint'],policy_manifest=config['policy_manifest'],map=settings['map'],robot=settings['robot'],contract=c,actor=metadata,body_names=robot.body_names,joint_names=robot.joint_names,controlled_joints=c['joint_order'],root_fixed=robot.is_fixed_base,mass_kg=float(robot.root_physx_view.get_masses().sum()),actual_stiffness=robot.data.joint_stiffness[0,adapter.ids].cpu().tolist(),actual_damping=robot.data.joint_damping[0,adapter.ids].cpu().tolist(),actual_limits=robot.data.joint_pos_limits[0,adapter.ids].cpu().tolist())
    (out/'identity.json').write_text(json.dumps(identity,indent=2));print('TELEOP_READY '+str(out),flush=True)
    # Validation injects key events into the same controller; it does not simulate human GUI input.
    cases=[('release',[],2.),('W',['W'],3.),('S',['S'],3.),('A',['A'],3.),('D',['D'],3.),
           ('WA',['W','A'],3.),('WD',['W','D'],3.),('SA',['S','A'],3.),('SD',['S','D'],3.),
           ('QW',['W','Q'],3.),('EW',['W','E'],3.),('estop',['W','SPACE'],2.),('unlock',['SPACE','C','W'],2.)]
    if args.scenario=='wall':cases=[('wall',['W'],8.),('wall_release',[],1.)]
    if args.scenario=='laser':cases=[('laser_wall',[],1.),('laser_turn',['Q'],2.)]
    case_index=-1;case_step=0;case_data=[];case_start_pose=None;phase='interactive';planned=0
    try:
        while app.is_running() and not control.quit_requested:
            if args.duration and frame*control_dt>=args.duration:break
            if args.scenario!='interactive':
                if case_index<0 or case_step>=planned:
                    if case_index>=0:
                        final=agent.get_pose();vs=[r['actual_velocity'] for r in case_data]
                        segments.append(dict(name=phase,keys=cases[case_index][1],start_pose=asdict(case_start_pose),end_pose=asdict(final),
                            displacement_m=math.hypot(final.x-case_start_pose.x,final.y-case_start_pose.y),
                            yaw_delta=math.atan2(math.sin(final.yaw-case_start_pose.yaw),math.cos(final.yaw-case_start_pose.yaw)),
                            mean_actual_velocity=[sum(v[i] for v in vs)/len(vs) for i in range(3)],
                            final_command=case_data[-1]['command'],min_z=min(r['root_z'] for r in case_data),
                            laser_hits=sorted(set(r['laser_hit'] for r in case_data if r['laser_hit'])),
                            max_contact_force=max(r['max_contact_force'] for r in case_data)))
                    case_index+=1
                    if case_index>=len(cases):break
                    phase,keys,seconds=cases[case_index];planned=round(seconds/control_dt);case_step=0;case_data=[]
                    control.pressed.clear();control.estop=False;control.output=VelocityCommand()
                    if args.scenario=='wall' or args.scenario=='laser':
                        if case_index==0:
                            wall=arena.get_navigation_data()['walls'][0]
                            reset(Pose2D(wall.center[0]-1.3,wall.center[1],0.))
                    else: reset(Pose2D(spawn.x,spawn.y,0.))
                    reset_count+=1
                    for key in keys:control.event(key)
                    case_start_pose=agent.get_pose();print('TELEOP_CASE '+phase,flush=True)
                control.heartbeat();case_step+=1
            elif keyboard: keyboard.poll()
            else:control.heartbeat()
            if control.reset_requested:
                control.reset_requested=False;reset();reset_count+=1;control.emergency_stop()
            command=control.command(control_dt)
            agent.set_velocity_command(command);agent.update(control_dt)
            for substep in range(decimation):
                robot.write_data_to_sim()
                # Kit Space may pause its timeline. Never enter IsaacLab's blocking paused step loop.
                if not sim.is_playing():
                    control.emergency_stop();sim.play()
                sim.step(render=False)
                robot.update(dt);contacts.update(dt)
            hit=laser.update()
            if first_person is not None:first_person.update(control_dt)
            if not args.headless and frame%2==0:sim.render()
            pose=agent.get_pose();data=robot.data
            actual=[float(data.root_lin_vel_b[0,0]),float(data.root_lin_vel_b[0,1]),float(data.root_ang_vel_b[0,2])]
            z=float(data.root_pos_w[0,2]);tilt=float(data.projected_gravity_b[0,:2].norm());min_z=min(min_z,z);max_tilt=max(max_tilt,tilt)
            record=dict(t=round((frame+1)*control_dt,4),phase=phase,pose=asdict(pose),command=asdict(command),actual_velocity=actual,
                root_z=z,tilt=tilt,laser_hit=hit.object_path,laser_distance=hit.distance,laser_origin=agent.get_muzzle_origin_world(),laser_endpoint=hit.endpoint,
                max_contact_force=float(contacts.data.net_forces_w.norm(dim=-1).max()),horizontal_contact_force=float(contacts.data.net_forces_w[:,:,:2].norm(dim=-1).max()),estop=control.estop)
            if first_person is not None:record['first_person']=first_person.last
            if args.scenario!='interactive':case_data.append(record)
            if frame%5==0:trace.append(record)
            if not math.isfinite(z) or z<.20 or tilt>.85 or not arena.is_position_valid(pose.x,pose.y):
                # A wall contact can invalidate the conservative map center margin; no teleport or forced velocity.
                if z<.20 or tilt>.85 or not math.isfinite(z):control.emergency_stop()
            if hud and frame%10==0:hud.update(settings,config,agent,control,hit)
            if frame%25==0:(out/'status.json').write_text(json.dumps(record))
            frame+=1
            if not args.headless:
                # Wall-clock pacing measured against simulation elapsed, no accumulated sleep drift.
                target=start+frame*control_dt
                if time.monotonic()<target:time.sleep(min(control_dt,target-time.monotonic()))
    finally:
        agent.stop()
        if keyboard:keyboard.close()
        if first_person is not None:first_person.close()
        if hud:hud.close()
        summary=dict(frames=frame,sim_seconds=frame*control_dt,wall_seconds=time.monotonic()-start,
            minimum_root_z=min_z,maximum_tilt=max_tilt,reset_count=reset_count,segments=segments,
            laser_damage_enabled=False,root_motion_method='joint_position_targets_only; root writes only explicit reset',
            render_enabled=not args.headless,keyboard_attached=keyboard is not None,
            first_person=first_person.last if first_person is not None else None)
        (out/'metrics.json').write_text(json.dumps(summary,indent=2));(out/'trace.json').write_text(json.dumps(list(trace)))
        print('TELEOP_RESULT '+json.dumps(summary),flush=True)
    return 0
