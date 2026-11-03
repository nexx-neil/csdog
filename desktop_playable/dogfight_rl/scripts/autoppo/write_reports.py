"""Generate human reports from real immutable artifacts; never manufacture metrics."""
from pathlib import Path
import sys,json,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from dogfight.autoppo.config import BASE
from dogfight.autoppo.storage import atomic_json
from dogfight.autoppo.motion_evaluator import metrics,score
from dogfight.locomotion.curriculum_v6_3.supervisor import brief

def main():
    r=BASE/'reports';audit=BASE/'physical_audit_final'
    results=json.loads((audit/'results.json').read_text())
    measured={n:metrics(json.loads((audit/n/'evaluation_common.json').read_text())) for n in results}
    rows=['|Checkpoint|前进 m/s|四腿完整周期|滑移 m/s|停止 m/s|停止偏航 rad/s|相对搜索分|','|---|---:|---|---:|---:|---:|---:|']
    for n,m in measured.items():rows.append(f"|{n}|{m['forward_velocity']:.6f}|{m['complete_stride_count']}|{m['support_slip']:.6f}|{m['stop_linear_speed']:.6f}|{m['stop_yaw_rate']:.6f}|{score(m):.6f}|")
    table='\n'.join(rows)
    architecture='''# CSDog AutoPPO Lab 架构

实现包 `src/dogfight/autoppo`，入口 `scripts/autoppo/autoppo.py`。复用冻结Isaac Lab任务、V6/V6.1/V6.3接触/评估/Runner与原生RSL-RL PPO，不修改第三方或机器人资产。无需Optuna，现有Python、SQLite、torch、NumPy、PyYAML和Matplotlib已足够。

数据流：有边界的单因素候选 → SQLite持久队列 → 单GPU原生PPO worker → 同进程物理评估 → 安全筛选/多目标/Pareto保留 → 唯一ID checkpoint bank → 继承/回滚/有限追加预算 → 能力课程。

`experiment_manager.py` 串行调度；`search_optimizer.py` 采样与Successive Halving；`train_runner.py` 使用原生PPO；`motion_evaluator.py` 物理指标与排名；`checkpoint_bank.py` 保留各能力策略；`recovery_manager.py` 分类失败；`curriculum_manager.py` 依据重复验收晋级；`resource_monitor.py` 监控显存/磁盘；`storage.py` 原子文件和SQLite WAL/FULL事务。

默认12候选、256环境，累计档位250/1000/4000更新，保留约4/2组；改善中的精英可追加有界500更新。整个系统无固定总更新上限；连续3批无可靠改善进入BLOCKED_NEEDS_REDESIGN。不会将短期零周期直接视为失败；有安全的运动、摆动改善仍可保留。接近的候选增加2027/4099独立评估种子。搜索种子、参数哈希、来源、预算、结果与所有调整均入库；参数搜索不是严格单因素因果A/B实验。

每250更新轻量评估、500更新或预算终点完整评估；物理评估在同一Isaac进程内运行。不同候选/预算档位间释放仿真并串行启动。每100更新提交可恢复checkpoint，训练监测同时检查数值和物理异常。完整评估的中间优秀模型也进入bank；策略退化保存失败证据，后续候选从受保护bank继承。重要候选和Smoke保存真实视频与训练/接触曲线。

checkpoint先临时写、rename、反序列化校验、fsync文件及父目录，再提交SQLite进度。重启时回收孤儿记录，损坏最新模型回退到已提交可读模型。新执行工作量与分支继承历史分别记录；丢失的未提交进度不会伪装已恢复。物理场景在续训时重置，不能称PhysX无损/逐位恢复。

改变奖励/课程的新候选继承Actor/Critic/std并重置优化器；同一候选续训恢复完整优化器、LR/std/RNG。Smoke另测试完整learner恢复后显式修改熵系数。禁止网络平均/拼接。48维观测、12动作、LF/RF/LR/RR顺序和模型SHA兼容性均检查。

逻辑bank：best_forward、best_gait、best_low_slip、best_stop、best_balanced、best_stage_qualified，以及各课程最佳。实际文件唯一ID，不覆盖。相对best不代表合格；无合格模型时best_stage_qualified保持空。

管理器锁由worker继承，管理器异常退出而worker尚在时锁仍存在。重复start不会产生第二训练器。GPU再使用历史统一gpu.lock。STOP在PPO完整更新边界保存；超时只终止本服务自己的进程组。系统服务Restart=on-failure，有限启动频率；用户服务linger支持重启后恢复。人工stop保留STOP标志，重启不会擅自取消停止。

磁盘不足停止；只允许清理新Lab目录中老旧未提交临时文件，保留全部bank、失败模型和所有历史版本。本次没有自动删除历史文件。

训练成功和机器人运动成功独立：只有真实多技能物理验收反复通过，才记录课程/最终运动成功。长期程序无需Codex持续在线。
'''
    (r/'AUTOPPO_ARCHITECTURE.md').write_text(architecture)
    (r/'AUTOPPO_SEARCH_SPACE.md').write_text('''# 自动搜索空间

权威边界：`configs/autoppo/search_space.yaml`；系统预算：`configs/autoppo/system.yaml`。PPO 3.1.2实参为`learning_rate/entropy_coef/clip_param/lam`，探索初值为`policy.init_noise_std`；`gae_lambda`映射实际`lam`。接口已检查本地安装实现并通过真实续训验证。

优先奖励/课程，再熵/探索，最后学习率/clip/lam。初始LR重点7e-5–1.3e-4，全边界3e-5–3e-4；熵初始0.0025–0.008，全边界0.001–0.02；std初始0.4–0.65，全边界0.3–0.7；clip0.1–0.25；lam0.90–0.97。继承std保留实际训练值，只有显式std变异才重设；实际生效值写入launch.json。

方向进度权重3.5–4.8、跟踪1.5–2.8、摆腿引导0.8–1.6、有效落脚0.8–1.4、周期0.8–1.5、支撑质量0.8–1.5、物理滑移−0.9至−0.35、姿态−0.03至−0.01、平滑−0.004至−0.0015、停止反馈−1.5至−0.8。关节限位、碰撞、终止、机器人资产、力矩、控制与正式阈值不在搜索空间。原50Hz swing保持关闭。

训练速度下界0.12–0.16、上界0.18–0.25m/s，停止占比0.15–0.30。命令任务比例由既有课程分布生成并归一化。初始候选一次改变一类主要因素，记录来源、旧值、新值与原因。继承供体的有效奖励/课程再变异，不平均网络。

250/1000/4000是每个候选的累计新更新档位，不能当作整个系统总上限。OOM分支256→128→64，增加更新数以补偿环境采样量，并保存失败和新的参数哈希；64环境仍OOM时终止该尝试。低环境数候选比较时应参考累计采样量。

排名只使用物理指标。安全bank要求摔倒率<=5%、非法小腿接触比例<=1%、方向不反向；训练过程另有较宽的严重异常屏障，它不构成合格判定。连续目标包含跟踪、四腿最少周期率、早期真实摆动、有效落脚、支撑、滑移、停止平移/偏航。运动不足惩罚防止零运动仅凭低滑移/低漂移胜出；正式验收与这些权重独立。

不同历史供体继承了不同训练成本，不能只凭新增250轮宣称公平算法比较。数据库/模型元数据分别保存历史累计与新采样/时间；相对排名用于选供体。
''')
    (r/'AUTOPPO_EVALUATION_PROTOCOL.md').write_text('''# 统一物理评估协议

协议 `autoppo-500hz-fixed-landing-v2`。真实Isaac Sim动力学，浮动机身、正常重力、确定性Actor输出。500Hz物理、50Hz控制，不设置根速度/位姿制造运动。保持既有地面、PD、力矩和关节限位。

正式面板12秒，训练完整评估种子103/307/911/1301，接近/潜在合格另用2027/4099；轻量6秒、seed103。历史最终对比统一用103/307、256环境，先前另有四种子复评作为补充。每个完整面板覆盖前进0.18/0.25、停止、后退−0.18/−0.25、正负0.3rad/s旋转、组合和方向/停止转换。每条件16个并行试验。初始关节±0.035rad、roll/pitch±0.025rad扰动；固定评估时长和种子协议。

沿用跟踪比例0.7–1.35、滑移<=0.08m/s、停止平移<=0.03m/s、停止偏航绝对值<=0.08rad/s、摔倒<=5%、80%试验通过、每腿>=2可重复完整周期等既有门槛。加上非法小腿接触限制。正式滑移按实际接触点速度、500Hz支撑时长统计。新周期要求支撑40ms、连续严格离地15mm/60ms、600ms内20mm有符号摆动、合理触地、全飞行>=2足支撑，以及首次60ms落脚窗口平均滑移<=0.08。

正负旋转分别测试。纯旋转足端位移投影到命令开始/重置时固定的机身切向方向，避免用瞬时切向量与自身径向点积恒零；平移与组合继续使用有符号机身x方向。四腿独立状态，绝不强制同轨迹。

完整面板为全部256环境逐2ms保存候选/拒绝原因位图/周期事件NPZ及逐事件CSV。原始接触力、碰撞网格净空、足端与机身位姿另外保存12环境诊断子集，每条轨迹附接触时序、高度、足端前后轨迹和原始力图。子集诊断不冒充全环境指标。

候选/失败有多种独立原因，不可将原因计数相加当事件总数。接触不填缝、不删短接触、不引入迟滞。正式统计排除重置和指令稳定前时段；未过滤事件文件保留重置、短接触和所有物理tick以供诊断。

课程：前进→前进/后退→正负旋转→组合/转换；每阶段保留此前全部技能，连续3份完整合格证据且含独立确认种子才晋级。轮数和单次成功不触发晋级。

历史最终对比：

'''+table+'\n\n以上全部未通过Stage 1。相对搜索分用于选择初始供体，不能称已学会步行。\n')
    before=json.loads((audit/'before.json').read_text())['metrics']
    p=json.loads((audit/'v63_B300/evaluation_common.json').read_text());p=dict(p,rows=[x for x in p['rows'] if x['seed']==103]);after=brief(p)
    compare=dict(checkpoint=results['v63_B300']['checkpoint'],seed=103,before=before,after=after,
        interpretation='Same deterministic checkpoint. Metrics retain their meaning; v2 fixes arming edge and first landing window. No valid gait was manufactured.')
    atomic_json(r/'SAME_CHECKPOINT_COMPARISON.json',compare)
    audit_file=r/'GAIT_BUG_AUDIT.md';text=audit_file.read_text()
    marker='\n## 最终v2复评与同checkpoint对照\n'
    if marker in text:text=text.split(marker)[0]
    text+=marker+'\n'+table+'\n\n同一V6.3 B300、seed103：\n\n|指标|旧状态机|v2修复后|\n|---|---:|---:|\n'
    for key in ['vx','support_foot_slip','stop_linear_speed','stop_yaw_rate']:text+=f"|{key}|{before[key]:.9f}|{after[key]:.9f}|\n"
    text+=f"|完整周期LF/RF/LR/RR|{before['complete_stride_count']}|{after['complete_stride_count']}|\n"
    text+='\n新增确认Bug：旧标称40ms支撑的arming在卸载沿实际要求42ms，v2按已完成40ms支撑正确armed。该2ms边界偏差无法解释RF典型80–100ms缺支撑。正式两足支撑条件仍保留。首次60ms窗口修复防止后续静止稀释早期滑移。事件积分/dt原机制正确，未乘50。\n'
    audit_file.write_text(text)
    fix=r/'GAIT_STATE_MACHINE_FIX.md';t=fix.read_text().replace('autoppo-500hz-fixed-landing-v1','autoppo-500hz-fixed-landing-v2')
    if '42ms' not in t:t+='\n另修复40ms arming的物理子步边界偏差（原实际42ms），测试精确40ms旧拒绝/新接受；阈值未降低。全环境物理事件现按2ms导出，不只保留控制步累计。纯yaw采用固定机身切向投影。\n'
    fix.write_text(t)
    recovery='''# 自动恢复与真实接口测试

测试证据：`validation_tests_final.log`、`CHECKPOINT_PROTECTION_FINAL.json`、`../smoke_validation_final_02/SMOKE_PASS.json`。若最终证据尚不存在，不能据本说明声称通过；启动门禁逐项验证实际文件和SHA。

单元/模拟测试覆盖：搜索采样/边界/去重；SQLite事务中断、重开与孤儿回收；队列与分级筛选；Pareto与安全排名；零运动不能超过有前进的未合格锚点；损坏checkpoint拒绝、最新文件损坏回退；NaN、错误输入维度；源模型不覆盖；管理器/子进程继承锁及父进程退出后的排他性；GPU OOM降低环境并补偿预算、最低64不无限重试；数值失败终止；后续批次去重；半批生成后重启补齐；有限无改善进入BLOCKED；重复及独立证据课程晋级。

真实Smoke顺序运行两组、每组2次PPO更新：第一组网络/std迁移且重置优化器；第二组完整恢复Actor/Critic/std/优化器/LR/RNG，并将熵改为0.004后继续。验证48输入/12动作和关节顺序、参数实际变化、模型可反序列化、SQLite真实进度、500Hz评估、事件CSV、视频和曲线。两组GPU进程串行并完整退出。最终Smoke通过systemd用户服务环境执行，检验与长期服务相同的非交互环境。

模拟故障不是实际PPO成功；Smoke通过也不是运动能力通过。先前初版Smoke4更新单独保留，不冒充最终v2证据。训练进程中断在完整PPO更新边界保存；物理场景重置，未承诺物理求解器逐位恢复。
'''
    (r/'AUTOPPO_RECOVERY_TEST.md').write_text(recovery)
    # Publication-ready static comparison using measured physical values only.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    names=list(measured);fig,axes=plt.subplots(2,2,figsize=(11,7))
    for ax,key,label,limit in zip(axes.flat,['forward_velocity','support_slip','stop_linear_speed','stop_yaw_rate'],['Forward m/s','Support slip m/s','Stop m/s','Stop yaw rad/s'],[None,.08,.03,.08]):
        ax.bar(names,[measured[n][key] for n in names]);ax.set_ylabel(label)
        if limit is not None:ax.axhline(limit,color='red',linestyle='--',label='formal limit');ax.legend()
    fig.suptitle('Final v2 deterministic physical comparison: all complete-stride counts remain zero')
    fig.tight_layout();fig.savefig(r/'HISTORICAL_PHYSICAL_COMPARISON.png');plt.close(fig)
    print(r)
if __name__=='__main__':main()
