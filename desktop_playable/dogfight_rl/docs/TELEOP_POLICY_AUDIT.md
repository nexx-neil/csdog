# DOGFIGHT V0.2 接入前兼容性审计

审查日期：2026-11-03。先读取工程AGENTS、PROJECT_STRUCTURE、格式规范.md及audits/progress_audit_20261103/FINAL_SUMMARY.md，再核对实际源码和权重；没有重新训练。

## 实际来源与保存原则

实际目录确认是 `/home/zxq/robot_projects/peer_csdog_review`。原任务为解压项目中的 `CSDog-V2-Teleop-Direct-v0`，配置在 `tasks/direct/csdog_v2/csdog_v2_env_cfg.py`，观测/动作实际运算在 `tasks/direct/generated_robot/generated_robot_env.py:66–107`。

当前正式业务工程未找到可复用的当前dog_a/b/c资源目录；归档中同名旧Dog A/B不属于当前模型。故未恢复旧布局，也未创建空dog_b/c目录。使用既有 `assets/csdog_12dof/peer_teleop_v1/` 管理资源，`configs/robots/dog_a_teleop.yaml` 管理身份，`src/dogfight/teleop/` 管理适配器；沿用V0 VelocityCommand、AgentInterface及RealDogAgent。

复制17份模型/网格/权重资源至正式assets，原件保留；来源与逐文件SHA见 `assets/csdog_12dof/peer_teleop_v1/IMPORT_MANIFEST.json`。没有复制另一套PPO库、训练器或同名正式源码。

## 实际运动ABI

|项目|审查结果|
|---|---|
|权重|原发布包 `logs/rsl_rl/csdog_v2_teleop/2026-10-29_17-42-40_qweasd_mixed100/model_final.pt`，iter=1043|
|网络|本次torch.load(weights_only=True)检查actor各层为50→256→256→128→12，ELU；critic50→256→256→128→1；std12|
|归一化|原配置无Actor/Critic观测归一化；当前加载器严格检查模型张量和声明，拒绝不支持normalizer|
|观测顺序|0:3机身线速度，3:6机身角速度，6:9重力投影，9:12机身vx/vy/yaw命令，12:24关节角减默认，24:36关节速度，36:48上次裁剪动作，48:50相位sin/cos|
|相位|episode时钟模0.5秒；适配器reset时归零，每控制步递增；无随机命令采样|
|动作|12位置目标；Actor输出裁剪±1，乘0.35，再加默认关节角（全0）；上次动作使用裁剪值，非raw输出|
|关节动作顺序|joint_lr_1/2/3，joint_lf_1/2/3，joint_rf_1/2/3，joint_rr_1/2/3；find_joints preserve_order=True|
|物理/控制|物理dt=.005秒200Hz；decimation4；策略dt=.02秒50Hz|
|驱动|Implicit PD Kp40/Kd1.5，12Nm、10rad/s；软位置范围系数.9；关节限位来自训练robot_sim.urdf|
|姿态与轴|根部自由、重力开启，初始z=.41m，默认12角全0；+X前/+Y左/+Z上，训练模型与控制yaw偏置0|
|碰撞|训练robot_sim.urdf；17link，12活动关节+4固定sole，merge_fixed_joints=False，self_collision=False，cylinders→capsules，与原任务一致|
|摩擦|原任务1/1、multiply，地面与全局仿真保持该配置|
|命令|默认前后±.25m/s、yaw±.3rad/s，来自当地已测范围；横移未当地验收，adapter明确拒绝非零vy|

原始 `model/robot.urdf` 与同学原始robot.urdf字节相同（20034d94c7c45094480ac8ec56c461b3deeaa7a210d9abd8c789d346ce8e362d），但**训练使用robot_sim.urdf**，含4个独立sole、不同限位/碰撞/驱动。本地V6的48维观测、LF/RF/LR/RR顺序、PD25/.8及10Nm/3rad/s不可混入。同为50维的V7也不自动兼容。

当前PolicyLoader只恢复Actor推理，不创建optimizer、OnPolicyRunner或奖励/训练环境；严格核对配置与策略identity（SHA、观测/关节/动作/频率/PD/网络）。张量无法自行证明观测语义，所以更换策略需要相应完整ABI声明，不能仅按文件名改路径。

## 实施边界

现有三Proxy工厂、TestMap、BattleManager、WeaponService、HealthSystem、BattleHUD没有改写。唯一修改的既有入口是launch.py，新增teleop分派和仅teleop的exec信号传递。修改前备份路径见 `runs/validation/teleop_v02_current.txt` 指向目录的 `backup/launch.py`；同目录preexisting_sources.json记录既有源码SHA。

新TeleopRealDogAgent继承既有RealDogAgent，补充全姿态body-frame枪口与前向计算；不让裁判操作关节。PolicyAdapter.step只算目标；runtime每控制周期为所有目标统一推进4次物理，adapter从不sim.step。只有初始化/明确reset写根节点状态，正常运动始终是关节位置目标+真实接触。

原同学键位A/D原为横移，本次用户要求A/D转向，因此只替换输入映射，不改变PPO观测命令含义。Q/E优先把期望vx归零；不承诺策略能物理零平移。Space锁零命令，C解除，焦点丢失锁停，输入poll间隔超时锁停；松手立即清零对应轴。

已知策略问题：停车有前漂、转向有侧漂，低速指令不等于物理刹车。任务限于一狗遥控，不接HP或伤害，不修历史导航/情报问题。激光仅视觉和物理query，保持旧WeaponService不变。
