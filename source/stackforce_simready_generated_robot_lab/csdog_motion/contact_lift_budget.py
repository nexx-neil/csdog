"""Reserve half the optional sensed lift in height preview; execution is unchanged."""
from .contact_datum import contract as parent_contract
TAG='csdog_contact_datum_half_lift_preview_obs175_v51'
PREVIEW_SURPLUS_FRACTION=.5
def contract(parent):
    value=parent_contract(parent);value.update(schema_version=51,compatibility_tag=TAG)
    value['height']['contact_datum']['preview']='v49 measured world datum prediction; reserve half the currently sensed optional surplus lift (maximum5mm) in advance; original executed reference may request full10mm and retains the same surplus allocator and hard guards'
    value['height']['contact_datum']['preview_surplus_fraction']=PREVIEW_SURPLUS_FRACTION
    return value
