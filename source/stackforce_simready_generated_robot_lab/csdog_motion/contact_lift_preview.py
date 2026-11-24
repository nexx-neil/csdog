"""Plan the same sensed surplus lift as the executed reference, before allocation."""
from .contact_datum import contract as parent_contract
TAG='csdog_contact_datum_full_lift_preview_obs175_v50'
def contract(parent):
    value=parent_contract(parent);value.update(schema_version=50,compatibility_tag=TAG)
    value['height']['contact_datum']['preview']='v49 measured world datum prediction; include full currently sensed surplus lift at every forecast phase, not only the basic32mm trajectory; execution still may shrink surplus under the original allocator/guards'
    return value
