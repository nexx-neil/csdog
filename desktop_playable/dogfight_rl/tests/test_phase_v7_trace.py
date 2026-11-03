import numpy as np
from dogfight.locomotion.phase_guided_v7.trace_metrics import swing_counts

def test_descent_does_not_erase_real_flight():
 a=np.zeros((100,2,28));a[:,:,4:8]=1
 a[20:70,:,4:8]=0;a[20:55,:,8:12]=.025;a[55:70,:,8:12]=.008
 assert (swing_counts(a)==1).all()
def test_chatter_and_hanging_cannot_count_completed_swing():
 a=np.zeros((100,2,28));a[:,:,4:8]=1;a[20:25,:,4:8]=0;a[20:25,:,8:12]=.02
 assert not swing_counts(a).any()
 a[20:,:,4:8]=0;a[20:,:,8:12]=.025
 assert not swing_counts(a).any()

def good_row():
 return dict(target_velocity=[.2,0,0],tilt_q95=.1,foot_speed=.02,joint_velocity_rms=.1,fall_fraction=0.,shin_rate=0.,support_slip=.03,tracking_quantiles=[.9,1.1],lateral_rms=.01,phase_match_q10=.8,min_swing_per_env=5,cycle_q10=[3]*4,clearance_peak=[.025]*4,translation_rms=.2,yaw_abs=.01,contact_duty=[.5]*4)
def test_phase_match_alone_never_qualifies():
 from dogfight.locomotion.phase_guided_v7.trace_metrics import qualify_row
 r=good_row();assert qualify_row(r)
 r['min_swing_per_env']=0;assert not qualify_row(r)
 r=good_row();r['tracking_quantiles']=[0,0];assert not qualify_row(r)
 r=good_row();del r['foot_speed'];assert not qualify_row(r)
def test_stopping_requires_quiet_support_not_only_zero_body_speed():
 from dogfight.locomotion.phase_guided_v7.trace_metrics import qualify_row
 r=good_row();r.update(target_velocity=[0,0,0],translation_rms=.01,contact_duty=[1]*4)
 assert qualify_row(r)
 r['foot_speed']=.2;assert not qualify_row(r)
 r['foot_speed']=.01;r['contact_duty'][0]=0;assert not qualify_row(r)
