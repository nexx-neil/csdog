# CSDog v2 操作手册（仿真训练）

## 当前边界

- 仿真任务：`CSDog-V2-Locomotion-Direct-v0`
- 标定任务：`CSDog-V2-Calibration-Direct-v0`
- v1 任务保持不变；v1 checkpoint 不可用于 v2。
- GO-M8010-6 的峰值数据只用于仿真安全包络。连续力矩、实机硬限位和热保护未确认前，不允许部署到硬件。

## 每次开始前

```bash
cd /home/ni/robot_projects/csdog
source /home/ni/miniconda3/etc/profile.d/conda.sh
conda activate dogfight
git status --short
```

## 查看门禁

```bash
python scripts/run_csdog_v2_gates.py \
  --json-output experiments/results/2026-10-29/csdog_v2_gates.json \
  --markdown-output experiments/2026-10-29_CSDOG_V2_GATES.md
```

报告的 `next_stage` 是唯一应继续的阶段。当前行为门禁下一项是 `contact_and_gait`；2 轮 PPO smoke 只证明软件链路可用，不证明机器人会走。

## 分阶段训练

第一阶段只训练前后：

```bash
python scripts/rsl_rl/train.py \
  --task CSDog-V2-Locomotion-Direct-v0 \
  --num_envs 1024 --max_iterations 300 --seed 42 \
  --command_axes x --command_limit 0.4 --headless
```

每 50 轮保存一次 checkpoint。到 100、200、300 轮时用固定命令评估；若 200 轮仍没有命令跟随，应停训检查奖励、接触和动作，不应直接增加轮数。

第二阶段在通过前后评估后加入左右，第三阶段再加入 yaw。不要一次把三个轴全部放开。

续训时可以给出精确 checkpoint 名；训练入口会自动避免把同名的
`.metadata.json` sidecar 当成 PyTorch 权重。

## 结果位置

- 训练：`logs/rsl_rl/csdog_v2_locomotion/<时间>/`
- 最终 PyTorch：`model_final.pt`
- 兼容标签：`model_final.pt.metadata.json`
- ONNX：`exported/policies/policy.onnx`
- 门禁证据：`experiments/results/2026-10-29/`

`logs/` 不提交到 Git；配置、脚本和小型 JSON 门禁报告提交。
