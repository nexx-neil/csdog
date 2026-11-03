"""Explicit reset-only test fixtures; never invoked during an autonomous match."""
import json,math
from dogfight_v0.battle.types import Pose2D

def range_checks(sim,robots,sensors,agents,referee,lasers,arena,reset,dt,out):
    ids=list(agents);spawn=arena.get_spawn_points();a=spawn[0];wall=arena.get_navigation_data()['walls'][0]
    rows=[]
    # Warm the first physics tick before custom test resets; Kit initializes poses once.
    for _ in range(20):
        for robot in robots.values():robot.write_data_to_sim()
        sim.step(render=False)
        for n in ids:robots[n].update(dt);sensors[n].update(dt)
    for scenario in ('two_meters','beyond_three','wall_occlusion','nearest_dog'):
        if scenario=='wall_occlusion':
            poses={ids[0]:Pose2D(wall.center[0]-2.4,wall.center[1],0),ids[1]:Pose2D(wall.center[0]+.7,wall.center[1],math.pi),ids[2]:spawn[2]}
        else:
            poses={ids[0]:Pose2D(a.x,a.y,0),ids[1]:Pose2D(a.x+(4 if scenario=='beyond_three' else 2),a.y,math.pi),ids[2]:(Pose2D(a.x+3,a.y,math.pi) if scenario=='nearest_dog' else spawn[2])}
        reset(poses);sim.forward()
        # Let real collision shapes settle with ordinary joint PD. Not a PPO test.
        for _ in range(100):
            for robot in robots.values():robot.write_data_to_sim()
            sim.step(render=False)
            for n in ids:robots[n].update(dt);sensors[n].update(dt)
        sim.forward()
        from .perception import Perception
        perception=Perception(agents,lasers[ids[0]].query,dict(intel_period_s=5.,vision_max_range_m=6.,vision_fov_deg=140.),referee.logger)
        visibility=perception.observe(0)[ids[0]].sightings[ids[1]]
        hit=lasers[ids[0]].update();referee.step(.02,fire_requests={ids[0]:True})
        event=next(e for e in reversed(referee.logger.events) if e.event_type=='SHOT_FIRED')
        hp={n:referee.health.get_health(n) for n in ids}
        visual=lasers[ids[0]].visual
        rendered_length=float(visual.geom.GetHeightAttr().Get()*visual.scale.Get()[2]) if visual else None
        expected=referee.config.max_health-referee.config.weapon_damage if scenario in ('two_meters','nearest_dog') else referee.config.max_health
        consistent=hit.object_path==event.data['hit_object_path'] and (event.data['distance_m'] is None or abs(hit.distance-event.data['distance_m'])<1e-4) and (rendered_length is None or abs(rendered_length-hit.distance)<1e-4)
        row=dict(scenario=scenario,target_visible=visibility.visible,rendered_length_m=rendered_length,poses={n:dict(x=ag.get_pose().x,y=ag.get_pose().y) for n,ag in agents.items()},health=hp,laser_distance=hit.distance,laser_path=hit.object_path,laser_endpoint=hit.endpoint,weapon=event.to_dict(),consistent=consistent,
                 passed=hp[ids[1]]==expected and hp[ids[2]]==referee.config.max_health and hit.distance<=referee.config.weapon_range_m and consistent and (visibility.visible == (scenario!='wall_occlusion')))
        rows.append(row);sim.render();sim.render()
        if visual:
            import subprocess,os
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','x11grab','-i',os.environ['DISPLAY'],'-frames:v','1','-update','1',str(out/f'range_{scenario}.png')],check=True)
    (out/'physical_range_checks.json').write_text(json.dumps(rows,indent=2))
    if not all(r['passed'] for r in rows):raise RuntimeError('Physical range acceptance failed; see physical_range_checks.json')

def navigation_check(sim,robots,sensors,agents,arena,reset,dt,out,nav,routes,referee,hud,controls,headless):
    """Measured-pose path following around the existing wall, no enemy observation injection."""
    import time
    from dataclasses import asdict
    from .navigation import GridPlanner,PathFollower
    ids=list(agents);wall=arena.get_navigation_data()['walls'][0];spawns=arena.get_spawn_points()
    start=(wall.center[0]-2.,wall.center[1]);goal=(wall.center[0]+2.,wall.center[1])
    for _ in range(20):
        for robot in robots.values():robot.write_data_to_sim()
        sim.step(render=False)
        for n in ids:robots[n].update(dt);sensors[n].update(dt)
    reset({ids[0]:Pose2D(*start,0.),ids[1]:spawns[0],ids[2]:spawns[2]});sim.forward()
    planner=GridPlanner(arena,nav['grid_resolution_m'],nav['body_radius_m']+nav['tracking_margin_m'],tracking_radius=nav['body_radius_m']);plan=planner.plan(start,goal)
    if not plan.valid:raise RuntimeError('Navigation validation goal cannot be planned: '+plan.reason)
    follower=PathFollower(nav);index=1;rows=[];began=time.monotonic();replans=0
    referee.logger.log(0.,'NAVIGATION_VALIDATION_PLAN',points=plan.points,goal=goal)
    class Debug:
        def status(self):return dict(state='NAV_TEST',target_id=None,navigation_goal=goal,distance_m=math.dist((agents[ids[0]].get_pose().x,agents[ids[0]].get_pose().y),goal),visible=False,planning='ok',path=plan.points[index:],waypoint=plan.points[index] if index<len(plan.points) else None,fire=False)
    brain=Debug()
    for frame in range(round(90/.02)):
        pose=agents[ids[0]].get_pose();p=(pose.x,pose.y)
        index=follower.advance(planner,p,plan.points,index)
        if index>=len(plan.points):break
        if not planner.tracking_clear(p,plan.points[index]):
            plan=planner.plan_from_feedback(p,goal);replans+=1;index=1
            if not plan.valid:break
        cmd=follower.command(pose,plan.points[index]);agents[ids[0]].set_velocity_command(cmd);agents[ids[0]].update(.02)
        for _ in range(round(.02/dt)):
            for robot in robots.values():robot.write_data_to_sim()
            sim.step(render=False)
            for n in ids:robots[n].update(dt);sensors[n].update(dt)
        sim.forward()
        if frame%5==0:
            d=robots[ids[0]].data
            rows.append(dict(t=(frame+1)*.02,pose=asdict(agents[ids[0]].get_pose()),command=asdict(cmd),waypoint_index=index,path=plan.points,root_z=float(d.root_pos_w[0,2]),tilt=float(d.projected_gravity_b[0,:2].norm())))
        if frame%500==0:
            print('PPO_NAVIGATION_CHECK',frame*.02,asdict(agents[ids[0]].get_pose()),'waypoint',index,flush=True)
        if frame in (500,1500) and not headless:
            import subprocess,os
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','x11grab','-i',os.environ['DISPLAY'],'-frames:v','1','-update','1',str(out/f'physical_navigation_{frame}.png')],check=True)
        if rows and (rows[-1]['root_z']<.2 or rows[-1]['tilt']>.85):break
        if not headless and frame%10==0:
            if routes:routes.update(agents,{ids[0]:brain})
            state=referee.state();state['navigation']={ids[0]:brain.status()}
            if hud:hud.update(state,agents,controls)
            sim.render()
        if not headless:
            delay=began+(frame+1)*.02-time.monotonic()
            if delay>0:time.sleep(min(.02,delay))
    agents[ids[0]].stop();pose=agents[ids[0]].get_pose();error=math.dist((pose.x,pose.y),goal)
    result=dict(passed=error<=nav['waypoint_tolerance_m'],goal=goal,end=asdict(pose),error_m=error,sim_seconds=(frame+1)*.02,wall_seconds=time.monotonic()-began,replans=replans,initial_path=rows[0]['path'] if rows else [],minimum_root_z=min((r['root_z'] for r in rows),default=0.),max_tilt=max((r['tilt'] for r in rows),default=0.))
    (out/'physical_navigation_trace.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (out/'physical_navigation_result.json').write_text(json.dumps(result,indent=2))
    if not result['passed']:raise RuntimeError('Physical PPO path tracking failed; see physical_navigation_result.json')
