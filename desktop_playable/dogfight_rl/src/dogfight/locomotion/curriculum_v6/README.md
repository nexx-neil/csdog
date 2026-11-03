# CSDog curriculum PPO V6

Official frozen RSL-RL PPO 3.1.2, one 48-observation / 12-action actor-critic,
[512,256,128] ELU, 24 steps, 5 epochs, 4 minibatches; LR fixed 1e-4, std .4.
The original CSDog asset, explicit zero-delay PD 25/.8, 10 Nm/3 rad/s limits,
.2 action scale and true PhysX distal contact classifier are reused. No old
network weights, Spot reward bundle, synthetic root motion or model edits.

Training order is forward+stop, forward/backward+stop, both yaw signs with
retention, combinations and transitions. Every sampled command has vy=0.
Stage distributions are explicit in commands.py; V6 never adds lateral commands.
Full gates use deterministic actions and three fixed reset seeds plus a rotating held-out seed with joint/roll/pitch
perturbations. Each skill must pass on EVERY seed/target and for three full
windows. At 256 envs each case has 16 trials per seed (64 total).

Thresholds are versioned in configs/locomotion/curriculum_v6/default.json and
are NEVER adjusted by the supervisor. Gates require signed tracking .7–1.35,
falls <=5%, lateral speed <=.05 m/s, stance slip <=.08 m/s, turn translation
<=.06 m/s and four legs with repeated >=60 ms strict swings, distal contact
switches, >15mm full-geometry clearance, raw force <1N and no shin contact.
80% of per-seed trials must qualify. Stop requires <=.03 m/s and <=.08 rad/s.
These are conservative initial thresholds, not a claim of achievable gait.

Progress is actual*sign(command)/abs(command), safely gated at .04. Moving
tracking is centered on stationary tracking; zero-yaw objectives provide no
positive constant on forward tasks. Distinct stop reward applies only at zero
command. Weak stance slip and completed swing rewards are active immediately;
no forced diagonal gait. Quality costs increase only on observed repeat swings.
Safety termination, contact penalties, limits and motors are never relaxed.

Local supervisor owns all decisions and writes metrics.jsonl, TensorBoard,
TRAINING_STATUS.json, STATUS_SUMMARY.md, evaluation JSON/NPZ, events.jsonl and
atomic checkpoints. Ordinary training console is redirected; no model polling
is required. Light evaluation is every250 updates, full every500, saves100.
These intervals are monitoring cadence, NOT stage or training duration caps.
Six full windows with no actual-motion score improvement initiate a matched
500-update control and 500-update single-factor candidate from the same anchor.
Up to three repairs per stage, then BLOCKED_NEEDS_REDESIGN. Regression preserves
the rejected checkpoint and returns to the best verified anchor. Thresholds,
URDF, motor limits and inertia are outside the repair whitelist. Safe bounds:
LR [3e-5,3e-4], std <=.65, weak-cost halving, swing incentive <=1,
command amplitude [0.12,0.18] candidate and failed-direction sampling x1.5.
Control and adjusted arms use identical evaluation seeds and environment count.

Resume restores actor, critic, optimizer, std, learning rate, RNG, curriculum,
weights, distributions, global executed update/sample counts and repair history.
**The simulator resets; PhysX caches/partial episodes are not restored. This is
full learner/curriculum resume, not bit-exact simulator continuation.** Rollbacks
preserve all executed sampling counts, including rejected/control branches.
Only full V6 checkpoints are accepted; no weights-only option.

Commands use /home/zxq/miniconda3/envs/dogfight/bin/python. From project root:

```bash
python scripts/train/csdog_curriculum_v6.py --smoke-test --iterations 3 --num-envs 32 --headless --experiment-name smoke_unique
python scripts/train/csdog_curriculum_v6.py --auto-curriculum --auto-recovery --iterations unlimited --num-envs 256 --headless --seed 42 --experiment-name fresh_unique
python scripts/train/csdog_curriculum_v6.py --auto-curriculum --auto-recovery --iterations unlimited --num-envs 256 --headless --experiment-name resumed_unique --resume --checkpoint /absolute/path/latest.pt
python scripts/diagnostics/curriculum_supervisor.py status --run-dir /absolute/path/run
python scripts/diagnostics/curriculum_supervisor.py stop --run-dir /absolute/path/run
python scripts/evaluate/csdog_curriculum_v6.py --checkpoint /absolute/path/best_motion.pt --output-dir /absolute/path/new_eval --headless
```

For detached, locally supervised operation use the `run` watchdog command with
`--run-dir` equal to the chosen run path and pass training arguments after `--`.
A STOP file or SIGTERM requests a safe-boundary checkpoint. On native process
crash the watchdog marks BLOCKED and records exit status; it never blindly
restarts the same broken configuration. Low disk (<5 GiB), nonfinite PPO and
persistent severe physics/update anomalies stop computation. Checkpoint aliases
are atomically replaced; evaluated_N snapshots and rejected branches are retained.
Use a NEW experiment name for every fresh run or resumed session.

Final report is generated on every terminal state. Only SUCCESS automatically
requests a separate deterministic combined-motion video. A video of an unqualified
policy never proves success. Earlier PPO failures are retained in OLD_EXPERIMENT_ANALYSIS.md.
