"""Standalone plots from actual native PPO telemetry."""
import json
from pathlib import Path

def ppo_curves(directory):
    directory=Path(directory);path=directory/'metrics.jsonl'
    if not path.exists():return
    rows=[json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not rows:return
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(3,2,figsize=(12,9),sharex=True)
    for ax,keys in zip(axes.flat,[['linear_error'],['slip','physics_slip'],['complete_stride_count'],['kl'],['exploration_std'],['contribution_progress','contribution_swing_credit','contribution_stride_credit','contribution_physical_slip','contribution_stop_feedback']]):
        for key in keys:
            if key in rows[0]:ax.plot([r['total_updates'] for r in rows],[r.get(key,0) for r in rows],label=key)
        if ax.lines:ax.legend(fontsize=7)
        ax.grid(alpha=.2)
    axes[2,0].set_xlabel('Lineage PPO updates (includes inherited training)');axes[2,1].set_xlabel('Lineage PPO updates')
    fig.suptitle('Native PPO telemetry; physical acceptance is evaluated separately')
    fig.tight_layout();fig.savefig(directory/'ppo_curves.png');plt.close(fig)
