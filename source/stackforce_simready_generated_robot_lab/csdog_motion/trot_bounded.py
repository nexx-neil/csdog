"""Explicit <=.95 flat inference envelope for the v45 C2 return proposal."""
import copy
import torch
from .trot_return import reference,period,duty,contract as parent_contract,valid_request as parent_valid
TAG='csdog_bounded_plateau_trot_obs76_v47'
CAP=.95

def valid_request(twist):
    return parent_valid(twist)&(twist[:,0]<=CAP+1e-6)

def contract(base):
    value=parent_contract(base);value.update(schema_version=47,compatibility_tag=TAG)
    value['command_envelope']['forward_single_axis_extension_mps']=CAP
    value['forward_extension']['command_range_mps']=[.8,CAP]
    value['bounded_inference']={'forward_cap_mps':CAP,'reference_family':'v45 C2 plateau return','source_training_range_mps':[.65,1.0],'learning_not_resumed':True,'above_cap_requests':'rejected before command shaping','unbounded_1_0_selection':'separate; no pass inferred'}
    return value

def cases(holdout=False):
    speeds=[.8+(CAP-.8)*x for x in (.2,.55,.85)]+[CAP] if holdout else [.8,.85,.9,CAP]
    out=[dict(name='bounded_forward_'+format(s,'.4f'),profile=[[20.,[s,0,0]]],protected=True)for s in sorted(set(speeds))]
    out += [dict(name='bounded_stop',profile=[[2.3,[0,0,0]],[10.7,[CAP,0,0]],[20.,[0,0,0]]],protected=False),dict(name='bounded_turn',profile=[[7.7,[CAP,0,0]],[13.3,[0,0,-.8]],[20.,[0,-.4,0]]],protected=False),dict(name='bounded_reverse',profile=[[7.3,[CAP,0,0]],[13.7,[-.5,0,0]],[20.,[0,0,0]]],protected=False)]
    return out
