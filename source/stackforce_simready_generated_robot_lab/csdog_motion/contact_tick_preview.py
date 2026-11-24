"""Inspect every20ms execution tick within the same240ms basic preview horizon."""
from .contact_basic_reserve import contract as parent_contract
TAG='csdog_contact_datum_tick_preview_obs175_v55'
PREVIEW_SECONDS=tuple(i*.02 for i in range(13))
def contract(parent):
    d=parent_contract(parent);d.update(schema_version=55,compatibility_tag=TAG)
    d['height']['automatic_workspace_preview']['preview_seconds']=list(PREVIEW_SECONDS)
    d['height']['contact_datum']['preview']='v54 mandatory basic preview,30mrad forecast reserve; inspect every20ms control tick from0through240ms instead of every40ms; same response model, no change to physical execution/reference/allocator or acceptance'
    return d
