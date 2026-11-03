"""Bounded single-factor search, Successive Halving and compatible inheritance."""
import copy,hashlib,math,random
import yaml
from .config import ROOT,default_options
from .storage import canonical
from .motion_evaluator import pareto,score

class SearchOptimizer:
    def __init__(self,store):
        self.store=store
        self.space=yaml.safe_load((ROOT/'configs/autoppo/search_space.yaml').read_text())
        self.system=yaml.safe_load((ROOT/'configs/autoppo/system.yaml').read_text())
    def validate(self,config):
        o=config['options'];base=default_options()
        if o['thresholds']!=base['thresholds']:raise ValueError('Formal thresholds are immutable')
        for key,value in o['weights'].items():
            if key in self.space['rewards']:
                lo,hi=self.space['rewards'][key]
                if not lo<=value<=hi:raise ValueError('Reward out of range: '+key)
            elif value!=base['weights'].get(key):raise ValueError('Protected reward changed: '+key)
        if set(o['weights'])!=set(base['weights']):raise ValueError('Reward set changed')
        for key,(lo,hi) in self.space['ppo'].items():
            if not lo<=o['ppo'][key]<=hi:raise ValueError('PPO out of range: '+key)
        if o['ppo']['schedule']!='fixed':raise ValueError('Only fixed LR has been validated')
        if config['num_envs'] not in [64,128,256]:raise ValueError('Environment budget invalid')
        lo,hi=config['speed_range']
        if not .12<=lo<=.16 or not .18<=hi<=.25 or lo>=hi:raise ValueError('Unsafe command range')
        if not .15<=config['stop_fraction']<=.30:raise ValueError('Stop curriculum out of range')
        return config
    def generate(self,generation,stage,donors,diagnosis=None,count=None,seed_offset=0):
        if not donors:raise ValueError('No verified donor checkpoints')
        rng=random.Random(self.system['seed']+generation*1009+stage*79)
        trials=[]
        preferred={'NO_VALID_STRIDE':['swing_credit','touchdown_credit','support_quality'],
                   'INSUFFICIENT_SUPPORT':['swing_credit','support_quality','smoothness'],
                   'STANDING_LOCAL_OPTIMUM':['progress','swing_credit'],
                   'WRONG_DIRECTION':['progress','tracking'],
                   'POLICY_REGRESSION':['smoothness','support_quality'],
                   'STOP_DRIFT':['stop_feedback'], 'SLIDING_REWARD_EXPLOIT':['physical_slip','support_quality']}.get(diagnosis,[])
        factors=[('reward',k) for k in preferred]+[('reward',k) for k in ['swing_credit','support_quality','physical_slip','stop_feedback']]
        if generation>=2:factors += [('ppo','clip_param'),('ppo','lam'),('reward','tracking'),('reward','posture'),('reward','smoothness')]
        factors += [('course','stop_fraction'),('course','speed_max'),('ppo','entropy_coef'),('ppo','init_noise_std'),('ppo','learning_rate')]
        for attempt in range(100):
            if len(trials)>=(self.system['population'] if count is None else count):break
            donor=donors[attempt%len(donors)]
            options=copy.deepcopy(donor.get('options') or default_options())
            config=dict(options=options,num_envs=256,seed=self.system['seed']+seed_offset+len(trials),stage=stage,
                        speed_range=copy.deepcopy((donor.get('config') or {}).get('speed_range',[.12,.25])),stop_fraction=(donor.get('config') or {}).get('stop_fraction',.15),restore_mode='weights',
                        source_sha256=donor['sha256'],parent_trial=donor.get('trial_id'),mutation=None)
            before=copy.deepcopy(config)
            # One baseline per source, then one-factor changes. Changed reward/
            # curriculum always starts a fresh native optimizer, preserving weights/std.
            if attempt>=len(donors):
                group,key=factors[(attempt-len(donors))%len(factors)]
                if group=='reward':
                    lo,hi=self.space['rewards'][key];options['weights'][key]=round(rng.uniform(lo,hi),7)
                elif group=='ppo':
                    lo,hi=self.space['initial_ppo_focus'].get(key,self.space['ppo'][key])
                    value=math.exp(rng.uniform(math.log(lo),math.log(hi))) if key=='learning_rate' else rng.uniform(lo,hi)
                    options['ppo'][key]=round(value,9)
                elif key=='stop_fraction':config['stop_fraction']=round(rng.uniform(.15,.30),5)
                else:config['speed_range'][1]=round(rng.uniform(.18,.25),5)
                config['mutation']=dict(group=group,key=key,reason=diagnosis or 'bounded prioritized search',before=before)
            self.validate(config)
            digest=hashlib.sha256(canonical(config).encode()).hexdigest()
            trial=self.store.add_trial(config,generation,stage,self.system['budgets'][0],donor['path'],digest)
            if trial:trials.append(trial)
        if not trials:raise RuntimeError('No untested combinations remain')
        return trials
    def select(self,rows,count):
        entries=[dict(r,metrics=__import__('json').loads(r['metrics'])) for r in rows if r.get('metrics')]
        # Preserve Pareto variety, then fill by balanced continuous score. Tiny
        # differences are resolved by confirmation seeds before this method.
        front=sorted(pareto(entries),key=lambda r:score(r['metrics']),reverse=True)
        rest=sorted([r for r in entries if r not in front],key=lambda r:score(r['metrics']),reverse=True)
        return [r['id'] for r in (front+rest)[:count]]
