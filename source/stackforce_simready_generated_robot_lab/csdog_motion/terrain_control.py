"""Reachable terrain references plus bounded observed low-rate yaw correction."""
from .reachable_clearance import contract as reachable_contract
from .yaw_integral import YawConfig
TAG='csdog_reachable_terrain_yaw_obs175_v32'
YAW=YawConfig(turn_start_radps=.1,turn_full_radps=.3)


def contract(parent):
    value=reachable_contract(parent);value.update(schema_version=32,compatibility_tag=TAG)
    value['support_feedback']['yaw_integral'].update(turn_start_radps=.1,turn_full_radps=.3,scope='terrain-course pure turn .1-.3rad/s; backward scope unchanged; same observed state, .6Nm integral and2Nm total caps')
    return value
