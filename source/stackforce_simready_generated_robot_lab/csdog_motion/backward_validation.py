"""Frozen unseen speeds/mixes/transitions that actually activate the backward controller."""

def backward_holdout_cases():
    commands={'stand':[0.,0.,0.],'forward':[.45,0.,0.],'back_slow':[-.22,0.,0.],
        'back_mid':[-.32,0.,0.],'back_high':[-.42,0.,0.],'back_fast':[-.47,0.,0.],
        'back_left':[-.32,.10,0.],'back_right':[-.32,-.10,0.],
        'back_yaw_left':[-.32,0.,.12],'back_yaw_right':[-.32,0.,-.12],
        'back_combined':[-.25,.08,.10],'left':[0.,.325,0.],'right':[0.,-.325,0.],
        'turn_left':[0.,0.,.5],'turn_right':[0.,0.,-.5]}
    cases=[{'name':n,'profile':[[20.,c]],'protected':True} for n,c in commands.items()]
    cases.extend([
        {'name':'back_start_stop','profile':[[2.6,[0.,0.,0.]],[8.1,[-.32,0.,0.]],[12.3,[0.,0.,0.]],[16.4,[-.42,0.,0.]],[20.,[0.,0.,0.]]],'protected':False},
        {'name':'reverse','profile':[[5.3,[.32,0.,0.]],[10.7,[-.32,0.,0.]],[15.2,[.25,0.,0.]],[20.,[0.,0.,0.]]],'protected':False},
        {'name':'back_switch','profile':[[4.2,[-.32,.08,0.]],[9.4,[-.32,0.,.12]],[14.6,[-.32,0.,-.12]],[17.5,[-.32,-.08,0.]],[20.,[0.,0.,0.]]],'protected':False},
    ])
    return cases
