"""Earlier basic-trajectory intervention with a stricter forecast reserve."""
from .contact_datum import contract as parent_contract
TAG='csdog_contact_datum_basic_reserve30_obs175_v54'
RESERVE_RAD=.03
def contract(parent):
    d=parent_contract(parent);d.update(schema_version=54,compatibility_tag=TAG)
    d['height']['automatic_workspace_preview']['joint_reserve_rad']=RESERVE_RAD
    d['height']['automatic_workspace_preview']['infeasible_forecast_selection']='original v36 feasible-prefix/earliest-violation selection, with stricter30mrad forecast reserve; executed limits unchanged'
    d['height']['contact_datum']['preview']='basic32mm trajectory as v49; increase forecast joint reserve20to30mrad to act before state/ground prediction error consumes the margin; optional10mm surplus remains independently allocated at execution and never forces the body up merely to preserve optional lift'
    return d
