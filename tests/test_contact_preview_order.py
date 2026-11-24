import torch
from csdog_motion.contact_preview_order import select_height
from csdog_motion.workspace_height_priority import select_height as old_select

def test_equal_unavoidable_immediate_violation_uses_later_response():
    e=torch.zeros(1,3,3,4);m=torch.ones_like(e)*.1;c=torch.tensor([-.02,0.,.02]);m[:,:,0]=0.;m[:,1,1]=-.02;m[:,2,1]=-.03
    new,good=select_height(e,m,c,torch.tensor([0.]));old,_=old_select(e,m,c,torch.tensor([0.]))
    assert not good.item() and old.item()==0. and new.item()==c[0].item()

def test_full_feasible_choices_preserve_original_cost_selection():
    e=torch.zeros(2,3,3,4);m=torch.ones_like(e)*.1;c=torch.tensor([-.01,0.,.01]);e[0,1]=.002
    previous=torch.tensor([-.01,.01]);new,good=select_height(e,m,c,previous);old,was_good=old_select(e,m,c,previous)
    assert torch.equal(new,old) and torch.equal(good,was_good) and good.all()

def test_earliest_violation_beats_better_distant_constraints():
    e=torch.zeros(1,3,3,4);m=torch.ones_like(e)*.1;c=torch.tensor([-.02,0.,.02]);m[:,0,0]=.01;m[:,1,0]=0.;m[:,2,0]=-.01;m[:,0,1:]=-.1
    new,good=select_height(e,m,c,torch.tensor([0.]));assert new.item()==c[0].item() and not good.item()
