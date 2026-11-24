"""Keyboard intents confined to the measured single-axis / mixed envelope."""
from .speed_learning import LEGACY_LIMITS, SPEED_LIMITS


def keyboard_twist(pressed, speed='normal'):
    if speed not in ('normal', 'fast', 'agile'):
        raise ValueError('Unknown keyboard speed')
    direction = [int('W' in pressed)-int('S' in pressed),
                 int('A' in pressed)-int('D' in pressed),
                 int('Q' in pressed)-int('E' in pressed)]
    single = sum(x != 0 for x in direction) <= 1
    if speed == 'agile' and single:
        # -.6 remains diagnostic: its mean yaw bias has not passed acceptance.
        return [direction[0]*(.6 if direction[0]>0 else .5), direction[1]*.4, direction[2]*.8]
    limits = SPEED_LIMITS if speed == 'fast' and single else LEGACY_LIMITS
    return [sign*limit for sign, limit in zip(direction, limits)]
