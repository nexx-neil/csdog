"""Explicit early-unloading counterfactual; old controllers keep their weights."""
from .clean_gait import clean_learning_contract
TRANSFER_TAG='csdog_early_support_transfer_residual_obs74_v13'
BACKWARD_TAG="csdog_backward_support_transfer_residual_obs74_v14"
TRANSITION={'unload_lead_phase':.04,'reload_phase':.035}

BACKWARD_TRANSITION=dict(TRANSITION,scope="backward",speed_start_mps=.15,speed_full_mps=.35,backward_yaw_gain_nm_s_rad=4.)


def transfer_contract(backward=False):
    value=clean_learning_contract()
    value.update(schema_version=14 if backward else 13,compatibility_tag=BACKWARD_TAG if backward else TRANSFER_TAG)
    value['support_feedback']=dict(value['support_feedback'],transition=dict(BACKWARD_TRANSITION if backward else TRANSITION))
    value['support_transition_scope']=('smoothly activated for medium/fast backward only; yaw damping gain2→4 in that region; ' if backward else '')+'planned support unload starts before liftoff; C2 force-share ramps; same foot trajectory/gains/limits; explicit counterfactual initialization'
    return value
