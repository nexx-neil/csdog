"""Passive IK snapshots and post-failure hypothetical height probes; no control changes."""
from collections import deque
import json
import torch

def install(env):
    original=env.reference_model.solve
    env.workspace_diagnostic_calls=deque(maxlen=8)
    def recorded(target,*args,**kwargs):
        q,error=original(target,*args,**kwargs)
        margin=torch.minimum(q-env.reference_model.lower,env.reference_model.upper-q).amin(2)
        if bool(((error>.00005)|(margin<.01)).any()):
            env.workspace_diagnostic_calls.append({'step':env.common_step_counter,'phase':env.motion.phase.detach().clone(),'applied':env.motion.applied.detach().clone(),'target':target.detach().clone(),'q':q.detach().clone(),'error':error.detach().clone(),'margin':margin.detach().clone(),'iterations':kwargs.get('iterations',args[1]if len(args)>1 else None)})
        return q,error
    env.reference_model.solve=recorded
    env.workspace_original_solve=original

def save(env,path,exception):
    def serial(x):return x.detach().cpu().tolist()if torch.is_tensor(x)else x
    records=[];lower=env.reference_model.lower;upper=env.reference_model.upper
    for item in env.workspace_diagnostic_calls:
        d={k:serial(v)for k,v in item.items()};affected=(item['error']>.00005)|(item['margin']<.01);d['affected_env_leg_indices']=torch.nonzero(affected).cpu().tolist();records.append(d)
    probes=[]
    # These candidates are never sent to env.step or the robot. They intentionally
    # ignore ground-contact consistency and do not constitute feasible whole-body plans.
    if records:
        last=env.workspace_diagnostic_calls[-1]
        for dz in [-.02,-.01,0.,.01,.02,.03]:
            target=last['target'].clone();target[:,:,2]-=dz
            q,e=env.workspace_original_solve(target,initial=last['q'],iterations=64);margin=torch.minimum(q-lower,upper-q).amin(2)
            probes.append({'hypothetical_body_up_m':dz,'ik_error_m':serial(e),'joint_margin_rad':serial(margin),'all_legs_ik_under_50um':bool((e<=.00005).all()),'all_legs_with_10mrad_reserve':bool((margin>=.01).all()),'physical_execution':False,'ground_contact_consistency_checked':False})
    r=env._robot.data
    from .adaptive_speed import adaptive_reference
    _,stance=adaptive_reference(env.motion.phase,env.motion.applied[:,:3],env.reference_nominal,env.reference_config,blend=env.motion.blend)
    d={'complete':True,'scope':'passive snapshots; hypothetical target changes evaluated only after failure, never executed; no policy/reference/limits changes','exception':repr(exception),'step':env.common_step_counter,'leg_order':['lr','lf','rf','rr'],'environment_direction_index':'environment modulo6;0forward1backward2left3right4leftturn5rightturn','lower_rad':serial(lower),'upper_rad':serial(upper),'joint_names':list(env.cfg.actuated_joint_names),'root_position_w':serial(r.root_pos_w),'root_quaternion_w':serial(r.root_quat_w),'projected_gravity_b':serial(r.projected_gravity_b),'root_ground_and_feet_ground_w':serial(env._surfaces()),'actual_foot_position_w':serial(r.body_pos_w[:,env._robot_foot_ids]),'stance_mask':serial(stance),'blend':serial(env.motion.blend),'recent_critical_solver_calls':records,'offline_common_height_probes':probes}
    path.write_text(json.dumps(d,indent=2)+'\n')
