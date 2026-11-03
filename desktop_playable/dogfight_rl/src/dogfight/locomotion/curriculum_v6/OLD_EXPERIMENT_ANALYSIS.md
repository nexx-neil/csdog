# Evidence reviewed before V6

Sources (unaltered):
- runs/locomotion/csdog_ppo_spot_v4/reports/SPOT_V4_REPAIR_REPORT.md
- runs/locomotion/csdog_ppo_tuning_v5/reports/PPO_HYPERPARAMETER_SEARCH_REPORT.md
- src/dogfight/locomotion/spot_{aligned_v3,v4,v5}/{config,runner,rewards}.py
- src/dogfight/locomotion/spot_v2/contacts.py

V4 2500 on the V5 common 6-second protocol: vx forward -.000140 m/s,
backward -.000251 m/s; yaw +.392821 versus +.4 target, +.022659 versus
-.4 target. Translation had zero strict swing. Reward and one yaw sign did
not establish walking or all-direction success.

V5 recommended policy had 0% strict swing on all four legs across directions.
trial_004 at500 learned yaw about+.323/-.211 but no periodic true translation.
trial_002 at175 held RR elevated (max .103m,82% air), other legs did not swing;
actual +.0406 under backward command was directionally wrong, and vanished by250.
This demonstrates possible movement, not a validated gait. It supports a task
and exploration redesign rather than URDF/inertia edits.

The aligned task inherited all SpotRewardsCfg from the beginning: gait,
clearance, air-time variance, joint position, smoothness and zero-target tracking
could compete with low-speed exploration. V5 candidates also spread effort over
lateral, forward/backward and yaw directions. Its runner hard-stopped at1500
updates/3600 seconds under a search ledger. V6 reuses none of these budget or
reward decisions. The existing contact classifier is intentionally conservative:
full distal mesh clearance, actual contact manifold location, raw force and shin
contact, not a knee-body contact timer advertised as a real foot sensor.

V6 hypotheses: signed task-conditioned progress removes the stationary task
solution's positive motion reward; narrow forward-first sampling reduces task
interference; weaker quality constraints permit exploration; independently
measured swing/stance cycles reject sliding and permanent leg suspension.
These remain hypotheses until actual deterministic evaluation passes. No amount
of reward growth or update count alone confirms them.
