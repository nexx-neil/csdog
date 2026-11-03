"""Camera tracking math must not modify agent/robot state."""
import math
import pytest
from dogfight.teleop.first_person import FirstPersonPose

def test_camera_in_front_and_above_with_level_horizon():
    c=FirstPersonPose({});eye,target=c.update((1,2,.4),0,.02)
    assert eye==pytest.approx((1.22,2,.56))
    assert target[0]>eye[0] and target[1]==eye[1] and target[2]<eye[2]

def test_rotates_left_and_snaps_on_reset():
    c=FirstPersonPose({});c.update((0,0,.4),0,.02);c.reset()
    eye,target=c.update((0,0,.4),math.pi/2,.02)
    assert eye==pytest.approx((0,.22,.56),abs=1e-8)
    assert target[1]>eye[1]

def test_yaw_wrap_takes_short_route_and_position_is_smoothed():
    c=FirstPersonPose({});a,_=c.update((0,0,.4),math.pi-.01,.02)
    b,_=c.update((.1,0,.4),-math.pi+.01,.02)
    assert abs(c.yaw-math.pi)<.02
    assert 0<b[0]-a[0]<.1

def test_teleport_resets_filter_instead_of_flying_across_map():
    c=FirstPersonPose({});c.update((0,0,.4),0,.02)
    eye,_=c.update((4,3,.4),0,.02)
    assert eye==pytest.approx((4.22,3,.56))
