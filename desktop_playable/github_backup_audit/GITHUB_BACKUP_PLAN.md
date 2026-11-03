# GitHub 备份方案（仅提案，未执行）

审计时间：2026-11-03T17:28:57.014972+08:00。本轮只读源码/配置/资产与Git；仅写 github_backup_audit 下五份报告。未操作现有窗口、未启动仿真/训练/测试器、未安装依赖、未改工程。运行中的原系统仍可能自行更新日志，体积是采样快照。

## 审计结论

本机完整桌面三狗系统尚未由远端main或历史资产包完整覆盖。历史包保存了同SHA策略/模型，但新增多机体调度、遥控、FSM/A*、原生路线、射线裁判/HP、三视角HUD及桌面入口属于本地新增。建议在独立备份分支保留全部远端旧代码，并新增本地可运行快照。

|类别|普通文件数|逻辑字节|MiB|
|---|---|---|---|
|必须上传|86|7664841|7.310|
|推荐上传|469|27778351|26.491|
|必须单独备份|9615|42163589708|40210.333|
|不上传|5844|225911342|215.446|

## 阻塞清单

1. 发布内容授权未闭环：同学模型/权重和原始CAD需明确再分发许可；原通知不覆盖它们。
2. 地面依赖NVIDIA云资产，离线场景/材质/贴图闭包尚需合法离线包和独立断网验收；Conda/Isaac Sim/SDK不是本项目Git的一部分。
3. 本地.git无remote、分支基线与目标GitHub main不同，存在大量删除/修改/未跟踪；不能直接push本地main、不能git add -A吞入历史删除。
4. 权重被.gitignore排除，必须在发布副本加指定路径例外或LFS；只上传源码会启动失败。
5. 桌面模板需按新机器生成绝对路径；editable IsaacLab安装路径需重建；尚未执行干净机器独立恢复验收。
6. GitHub API限流导致Release列表未核实；已用ls-remote和固定提交codeload完成main、相关分支、资产包当前快照核验，历史提交图/Release附件不作未验证假设。

## 最小改动目录方案

保持本机原地运行，不移动、覆盖或制造兼容链接。未来在另一发布工作副本从远端main固定提交0ac3f5c59ea6719581bfc0f492583db5aa7237fd创建 `backup/2026-11-03-desktop-playable`；保存原source/scripts/assets及所有历史提交。新增命名空间：
```text
<GitHub仓库原内容全部保留>
desktop_playable/
  dogfight_rl/
    launch.py, src/, configs/, scripts/, tests/, docs/
    assets/csdog_12dof/peer_teleop_v1/
    assets/ui/dogfight_teleop.svg
    .gitignore, pyproject.toml, setup.py, 环境说明
  model/                 # 推荐：原始设计，不替代实际robot_sim.urdf
  AGENTS.md, PROJECT_STRUCTURE.md, DOGFIGHT_ENVIRONMENT.md
  reorganization/, audits/ # 推荐：选定溯源证据
  github_backup_audit/    # 本五报告
docs/desktop_playable/
  RESTORE.md, environment lock, 验收证据索引
```
新命名空间保留dogfight_rl和model兄弟关系，common.paths无需改；IsaacLab由恢复步骤在desktop_playable/IsaacLab检出固定版本或正确注册editable路径，不能新建旧01/02/03布局兼容链接。若仅恢复桌面，根model不被当前teleop读取，但推荐保留设计原件。

## 上传策略与顺序

第一阶段：人工审核本清单与授权/隐私；单独离线备份当前工作树、.git和历史训练。第二阶段：准备独立候选快照，仅复制清单文件到发布副本，原件不变；权重保持原字节并SHA校验。第三阶段：在副本调整ignore/模板/文档、生成版本锁和内容SHA清单，完成恢复验收。第四阶段：仅对新分支做可审阅提交，给用户审查差异及统计，用户明确授权后才推送。main和历史资产分支保持原样，不强推。以上步骤均未在本轮执行。

必须上传集合直接走普通Git，总量见表；推荐源码/测试/文档/原始model走Git，截图可精简后Git或Release。训练历史与大tar默认外部备份；不将全部checkpoint纳入LFS。LFS仅在后续决定长期版本化二进制时对明确路径使用，并验证新机安装git-lfs、取回实体而非指针。

## 对现有可运行工程的改动建议（本轮零实施）

保留现有脚本、配置、URDF、checkpoint、manifest和SDK字节；新机恢复先尽量保持相同目录结构并用DOGFIGHT_PYTHON指定解释器。仅在独立发布副本生成脱敏桌面文件、环境清单和ignore例外。若要离线运行，应在独立恢复副本实现明确的官方ground资产根配置/本地路径选项并合法备份子资源，再验证物理与渲染一致；不要为了离线直接删地面/换碰撞或修改源模型。

## 完成标准

必须文件SHA、Actor ABI、地图生成和本地USD引用通过；干净用户/目标路径不含/home/zxq硬依赖；两个桌面入口都独立启动；键盘/停止/碰撞/HP/遮挡/射程/路线/三视角按RESTORE_CHECKLIST逐项记录；历史旧代码仍可在原分支追溯；main/历史资产分支未变化。尚未达到新机验收标准，本轮只完成备份审计与清单。


官方地面资源补充：本轮已经在内存解析云端default_environment.usd，确认其引用3张Wireframe贴图和SDK OmniPBR.mdl；直接贴图的URL/体积/SHA及验证结果见RESTORE_CHECKLIST末尾。尚未建立合法离线资源包及完成断网恢复，发布前离线验收阻塞仍保留。
