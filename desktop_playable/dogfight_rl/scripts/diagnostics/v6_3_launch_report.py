"""Write the factual V6.3 launch/blocked report from saved local state."""
from pathlib import Path
import json,os,time

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'runs/locomotion/csdog_curriculum_ppo_v6_3'

def main():
    gate=json.loads((BASE/'CONTINUATION_GATE.json').read_text())
    lines=['# V6.3 长期训练启动报告','短程继续训练资格：**'+('通过' if gate['allowed'] else '未通过')+'**；Stage 1正式验收：**'+('通过' if gate['formal_stage1_passed'] else '未通过')+'**。','',f"判定：`{gate['decision']}`。"]
    if gate['allowed']:
        active=Path((BASE/'ACTIVE_RUN').read_text().strip());status=json.loads((active/'TRAINING_STATUS.json').read_text())
        try:
            pid=int((active/'pid').read_text());cmd=Path(f'/proc/{pid}/cmdline').read_bytes();alive=b'csdog_curriculum_v6_3.py' in cmd
        except Exception:pid=None;alive=False
        metrics=status.get('physical_metrics') or {}
        checkpoints=sorted(active.glob('*.pt'))
        lines+=['',f"实际运行目录：`{active}`。训练进程PID `{pid}`，已核对命令行为V6.3训练入口；存活：`{alive}`。",f"当前PPO更新 `{status.get('total_updates')}`，课程 `{status.get('stage_name')}`；Supervisor心跳年龄 `{time.time()-status['heartbeat_unix']:.1f}s`。",f"当前物理指标：`{json.dumps(metrics,ensure_ascii=False)}`。",f"checkpoint数量 `{len(checkpoints)}`；最新文件：`{checkpoints[-1] if checkpoints else None}`。",'GPU执行、更新计数增长和checkpoint写入需要由启动后的实测值共同确认；本报告只写入当前已观察到的状态。安全停止和恢复由同一管理器完成。']
    else:
        lines+=['','按预设安全门禁止启动长期训练器。没有创建伪运行进程，也没有进入Stage 2。失败原因与下一项最值得验证的问题见A/B报告和资格JSON。']
    lines+=['','管理命令：','','```bash',f"{ROOT.parent.parent / 'miniconda3/envs/dogfight/bin/python'} {ROOT/'scripts/diagnostics/curriculum_v6_3_manager.py'} status",f"{ROOT.parent.parent / 'miniconda3/envs/dogfight/bin/python'} {ROOT/'scripts/diagnostics/curriculum_v6_3_manager.py'} stop",f"{ROOT.parent.parent / 'miniconda3/envs/dogfight/bin/python'} {ROOT/'scripts/diagnostics/curriculum_v6_3_manager.py'} resume",'```']
    (BASE/'reports/V6_3_TRAINING_LAUNCH_REPORT.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
