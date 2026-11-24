"""Mandatory basic reachability first, substantial optional lift demand second."""
import torch
from .contact_datum import contract as parent_contract
TAG='csdog_contact_datum_lift_priority_obs175_v52'
ACTIVATION_M=.01
SETTLED_OFFSET_M=.002
SETTLED_SPEED_MPS=.01
def choose_goal(basic,full,value,velocity):
    active=(value.abs()>SETTLED_OFFSET_M)|(velocity.abs()>SETTLED_SPEED_MPS)
    substantial=full.abs()>=ACTIVATION_M-1e-7
    return torch.where(active|substantial,full,basic),active|substantial
def contract(parent):
    d=parent_contract(parent);d.update(schema_version=52,compatibility_tag=TAG)
    d['height']['contact_datum']['preview']='two response-aware forecasts with identical previous goal: mandatory basic32mm reference and full sensed optional10mm surplus; retain basic goal while settled unless optional goal magnitude>=10mm; while body offset>2mm or speed>10mm/s continue full goal through settling; execution and all original allocator/physical guards unchanged'
    d['height']['contact_datum']['optional_activation_m']=ACTIVATION_M
    return d
