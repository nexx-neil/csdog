"""Plots from measured physical ticks and PPO log scalars only."""
from pathlib import Path
import json
import numpy as np

def physical(path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    path=Path(path);a=np.load(path)['data'];dt=float(np.load(path)['dt']);a=a[:,0];t=np.arange(len(a))*dt
    fig,axes=plt.subplots(5,1,figsize=(11,12),sharex=True)
    for i,name in enumerate(['LF','RF','LR','RR']):
        axes[0].step(t,a[:,4+i]+i*1.2,label=name,linewidth=.6)
        axes[1].plot(t,a[:,8+i]*1000,label=name,linewidth=.8)
        axes[3].plot(t,a[:,12+i],label=name,linewidth=.8)
    axes[0].set_ylabel('contact + leg offset');axes[0].legend(ncol=4)
    axes[1].set_ylabel('collision clearance mm');axes[1].axhline(15,color='k',ls='--',lw=.7)
    axes[2].plot(t,a[:,0],label='measured vx');axes[2].axhline(.2 if path.name.startswith('forward') else 0,color='k',ls='--',label='command');axes[2].legend();axes[2].set_ylabel('m/s')
    axes[3].set_ylabel('contact-point speed m/s')
    stance=.5+.5*np.tanh(np.sin(a[:,3])/.2);plan=np.stack((1-stance,stance,stance,1-stance),-1);match=(plan*a[:,4:8]+(1-plan)*(1-a[:,4:8])).mean(-1)
    axes[4].plot(t,match,lw=.6);axes[4].set_ylabel('phase match');axes[4].set_xlabel('physical time s')
    fig.suptitle(path.stem+' | environment 0; full metrics use all environments');fig.tight_layout();fig.savefig(path.with_suffix('.png'),dpi=140);plt.close(fig)

def learning(base):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    base=Path(base)
    from ...autoppo.storage import Store
    store=Store(base);allowed={r['id'] for r in store.rows('SELECT id FROM trials WHERE rung>=0')};store.close()
    fig,axes=plt.subplots(2,1,figsize=(10,7),sharex=True)
    for arm in 'ABCD':
        launches=[]
        for path in (base/'trials').glob('*/*/launch.json'):
            if path.parent.parent.name not in allowed:continue
            x=json.loads(path.read_text());o=x['options'];a=('D' if o['phase'] else 'B') if o['collision']=='sole' else ('C' if o['phase'] else 'A')
            if a==arm:launches.append(path.parent)
        rows=[]
        for path in launches:
            p=path/'metrics.jsonl'
            if p.exists():rows += [json.loads(s) for s in p.read_text().splitlines()]
        rows.sort(key=lambda r:r['updates'])
        if rows:
            axes[0].plot([r['environment_steps'] for r in rows],[r['actual_speed'] for r in rows],label=arm,lw=.6)
            axes[1].plot([r['environment_steps'] for r in rows],[min(r['clearance_peak']) for r in rows],label=arm,lw=.6)
    axes[0].set_ylabel('mixed-command batch vx m/s');axes[1].set_ylabel('minimum across legs of batch peak m');axes[1].set_xlabel('environment samples (lineage)');axes[0].legend();fig.suptitle('Training diagnostics; these are not independent acceptance metrics');fig.tight_layout();fig.savefig(base/'reports/training_curves.png',dpi=140);plt.close(fig)
