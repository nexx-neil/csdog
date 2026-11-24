import torch
from csdog_motion.contact_lift_priority import choose_goal

def test_mandatory_goals_keep_priority_for_small_optional_requests():
    basic=torch.tensor([0.,-.005,.005,0.]);full=torch.tensor([.005,-.005,.005,.01]);z=torch.zeros(4)
    value,active=choose_goal(basic,full,z,z)
    assert torch.equal(value,torch.tensor([0.,-.005,.005,.01]))
    assert active.tolist()==[False,False,False,True]

def test_full_forecast_kept_until_offset_and_speed_settle():
    basic=torch.tensor([.005,.005,.005]);full=torch.tensor([0.,-.005,0.])
    value,active=choose_goal(basic,full,torch.tensor([.003,0.,0.]),torch.tensor([0.,.02,0.]))
    assert torch.equal(value,torch.tensor([0.,-.005,.005]))
    assert active.tolist()==[True,True,False]
