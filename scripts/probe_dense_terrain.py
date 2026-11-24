"""Read-only dense contact probe, using unchanged original48 gates."""
from pathlib import Path
p=Path(__file__).with_name('probe_scanned_rough_turns.py')
s=p.read_text().replace('from csdog_motion.terrain_turn_evaluation import evaluate','from csdog_motion.terrain_dense_evaluation import evaluate')
exec(compile(s,str(p),'exec'))
