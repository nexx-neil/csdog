"""Passive history of reference ground queries, excluding hypothetical preview rays."""
from collections import deque
import json

def install(env):
    env.terrain_query_history=deque(maxlen=30);env._query_diagnostic_scope='other'
    original_reference=env._reference;original_plan=env._plan_height;original_rays=env._rays
    def reference(*args,**kwargs):
        previous=env._query_diagnostic_scope;env._query_diagnostic_scope='reference'
        try:return original_reference(*args,**kwargs)
        finally:env._query_diagnostic_scope=previous
    def plan(*args,**kwargs):
        previous=env._query_diagnostic_scope;env._query_diagnostic_scope='preview'
        try:return original_plan(*args,**kwargs)
        finally:env._query_diagnostic_scope=previous
    def rays(positions):
        ground=original_rays(positions)
        if env._query_diagnostic_scope=='reference'and positions.ndim==3 and positions.shape[1]==4:
            item={'xy_w':positions[:,:,:2].detach().cpu().tolist(),'ground_z_w':ground.detach().cpu().tolist()}
            if not env.terrain_query_history or env.terrain_query_history[-1]['step']!=env.common_step_counter:
                c=env.height_coordinator;r=env._robot.data
                env.terrain_query_history.append({'step':env.common_step_counter,'phase':env.motion.phase.detach().cpu().tolist(),'root_position_w':r.root_pos_w.detach().cpu().tolist(),'height_offset_m':c.value.detach().cpu().tolist(),'height_goal_m':c.goal.detach().cpu().tolist(),'first':item,'last':item})
            else:env.terrain_query_history[-1]['last']=item
        return ground
    env._reference=reference;env._plan_height=plan;env._rays=rays

def save(env,path):
    path.write_text(json.dumps({'scope':'passive actual reference queries only; preview rays excluded; no controller changes','frames':list(env.terrain_query_history)},indent=2)+'\n')
