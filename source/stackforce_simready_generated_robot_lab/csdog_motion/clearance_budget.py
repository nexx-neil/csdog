"""Explicit reference identity: reserve joint workspace for terrain compensation."""
import copy

TAG='csdog_clearance_budget_obs175_v29'
EXTRA_LIFT_CAP_M=.004


def contract(parent):
    value=copy.deepcopy(parent)
    value.update(schema_version=29,compatibility_tag=TAG)
    value['rough_sensing']['extra_swing_lift_cap_m']=EXTRA_LIFT_CAP_M
    value['rough_sensing']['clearance_scope']='base32mm lift retained; sensor surplus capped4mm to reserve terrain-height IK workspace; same actuator/target/error bounds'
    return value
