#!/usr/bin/env python3
"""Unified entrypoints for the frozen Dogfight project."""
from __future__ import annotations
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
from shared.paths import ROOT, TRAINING, BATTLE, PYTHON, project_path

TASK = TRAINING / 'python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1'
DEFAULT_CONFIG = TRAINING / 'configs/back_gait_primitive_recovery.yaml'
DEFAULT_CHECKPOINT = TRAINING / 'logs/back_gait_primitive_recovery/model_final.pt'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task', choices=['train-a','validate-a','gui-a','train-b','validate-b','gui-b','train-c','validate-c','gui-c','tensorboard','battle','battle-gui','battle-smoke','battle-real-a-test','test','integrity','script','check-environment'])
    parser.add_argument('--dry-run', action='store_true')
    args, rest = parser.parse_known_args()
    if args.task.endswith(('-b','-c')):
        parser.error(f'{args.task}: 本机缺少对应机器狗的模型、配置和训练入口。Dog C 的远程环境报告不等于本机可运行资源。')
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:8]
    env = dict(os.environ)
    env.pop('LD_LIBRARY_PATH', None)
    env.update(PYTHONPATH=os.pathsep.join([str(ROOT), str(BATTLE/'source/dogfight_v0')]), PYTHONNOUSERSITE='1', OMNI_KIT_ACCEPT_EULA='YES', TERM='xterm')
    python = str(PYTHON)
    if not PYTHON.is_file():
        parser.error(f'Frozen Python missing: {PYTHON}')
    def has(flag): return any(x == flag or x.startswith(flag+'=') for x in rest)
    def value(flag):
        for i,x in enumerate(rest):
            if x == flag and i+1<len(rest): return rest[i+1]
            if x.startswith(flag+'='): return x.split('=',1)[1]
        return None
    # Root-relative inputs/outputs resolve independently of the caller working directory.
    for flag in ('--config','--checkpoint','--resume','--output','--output-dir','--trajectory','--video-dir','--log-dir'):
        for i,x in enumerate(rest):
            if x == flag and i+1<len(rest): rest[i+1] = str(project_path(rest[i+1]))
            elif x.startswith(flag+'='): rest[i] = flag+'='+str(project_path(x.split('=',1)[1]))
    task = args.task
    output_parent = None
    if task in ('train-a','validate-a','gui-a'):
        script = 'train.py' if task=='train-a' else 'validate.py' if task=='validate-a' else 'evaluate.py'
        command=[python,str(TASK/script)]
        if not has('--config'):command += ['--config',str(DEFAULT_CONFIG)]
        if task=='train-a':
            if not has('--resume'): command += ['--resume',str(DEFAULT_CHECKPOINT)]
            if not has('--output-dir'): command += ['--output-dir',str(TRAINING/'logs/new_runs'/stamp)]
            if not has('--headless'): command += ['--headless']
        else:
            if not has('--output'):
                output_parent=TRAINING/'logs/validation'/stamp
                command += ['--output',str(output_parent/'result.json')]
            if task=='gui-a':
                if not has('--checkpoint'):command+=['--checkpoint',str(DEFAULT_CHECKPOINT)]
                if not has('--num-envs'):command+=['--num-envs','1']
            elif not has('--headless'): command+=['--headless']
    elif task=='tensorboard': command=[python,'-m','tensorboard.main','--logdir',str(TRAINING/'logs'),'--host','127.0.0.1']
    elif task in ('battle','battle-gui','battle-smoke','battle-real-a-test'):
        name={'battle':'run_v0_headless.py','battle-gui':'run_v0_battle_demo.py','battle-smoke':'run_v0_smoke_tests.py','battle-real-a-test':'run_dog_a_battle_integration_test.py'}[task]
        command=[python,str(BATTLE/'scripts/v0'/name)]
    elif task=='test':command=[python,'-m','pytest','-q',str(ROOT/'tests')]
    elif task=='integrity':command=[python,str(ROOT/'migration/verify_integrity.py')]
    elif task=='check-environment':command=[python,str(ROOT/'shared/scripts/check_environment.py')]
    else:
        if not rest:parser.error('script requires a project Python or Shell script path')
        script=project_path(rest.pop(0)).resolve()
        if not script.is_relative_to(ROOT):parser.error('script must be inside the project')
        command=[python if script.suffix=='.py' else 'bash',str(script)]
    command+=rest
    # Reject overwrite targets before starting Isaac Sim. Historical scripts remain available,
    # but new launcher outputs must always be fresh.
    for flag in ('--output','--output-dir','--trajectory','--video-dir','--log-dir'):
        target=value(flag)
        if target and Path(target).exists():parser.error(f'refusing to overwrite existing output: {target}')
    print(json.dumps({'command':command,'cwd':str(ROOT),'python':python},ensure_ascii=False),flush=True)
    if args.dry_run:return 0
    if output_parent:output_parent.mkdir(parents=True,exist_ok=False)
    return subprocess.run(command,env=env,cwd=ROOT).returncode
if __name__=='__main__':sys.exit(main())
