# GitHub 上传清单

审计时间：2026-11-03T17:28:57.014972+08:00。本轮只读源码/配置/资产与Git；仅写 github_backup_audit 下五份报告。未操作现有窗口、未启动仿真/训练/测试器、未安装依赖、未改工程。运行中的原系统仍可能自行更新日志，体积是采样快照。

## 体积与边界

|类别|普通文件数|逻辑字节|MiB|
|---|---|---|---|
|必须上传|86|7664841|7.310|
|推荐上传|469|27778351|26.491|
|必须单独备份|9615|42163589708|40210.333|
|不上传|5844|225911342|215.446|

统计口径：普通文件逻辑字节，不是du磁盘分配、不含目录/软链接大小；包含项目内.git普通文件但归入单独备份。两个项目外桌面文件额外纳入必须上传；本轮五份报告不计自身，避免递归体积。不同路径同字节副本在本机占用中逐份计数；仅当前上传集合去路径重。项目外Conda/驱动/云缓存体积未扫描，不纳入上述统计。

必须单独备份表示保留历史/环境恢复价值，且不进入本次可运行Git包；不上传表示不属于本次CSDog包或可重建缓存，绝非允许删除。现有所有文件原地保留。

## 实际目录结构/分组体积

|相对目录/根文件|普通文件数|逻辑字节|
|---|---|---|
|AGENTS.md|1|2854|
|DOGFIGHT_ENVIRONMENT.md|1|7875|
|IsaacLab/.dockerignore|1|493|
|IsaacLab/.git|23|35475636|
|IsaacLab/.gitattributes|1|526|
|IsaacLab/.github|21|71154|
|IsaacLab/.gitignore|1|914|
|IsaacLab/.pre-commit-config.yaml|1|2481|
|IsaacLab/.vscode|8|19982|
|IsaacLab/CITATION.cff|1|6163|
|IsaacLab/CONTRIBUTING.md|1|1770|
|IsaacLab/CONTRIBUTORS.md|1|3132|
|IsaacLab/LICENSE|1|1630|
|IsaacLab/LICENSE-mimic|1|10142|
|IsaacLab/README.md|1|9951|
|IsaacLab/SECURITY.md|1|1708|
|IsaacLab/VERSION|1|6|
|IsaacLab/apps|21|76303|
|IsaacLab/docker|23|75499|
|IsaacLab/docs|605|43132967|
|IsaacLab/environment.yml|1|285|
|IsaacLab/greptile.json|1|32|
|IsaacLab/isaaclab.bat|1|24269|
|IsaacLab/isaaclab.sh|1|30095|
|IsaacLab/logs|36|65329298|
|IsaacLab/outputs|36|305595|
|IsaacLab/pyproject.toml|1|3906|
|IsaacLab/scripts|113|975440|
|IsaacLab/source|1640|12345295|
|IsaacLab/tools|44|139436|
|PROJECT_STRUCTURE.md|1|6223|
|PROJECT_STRUCTURE_AUDIT.md|1|268714|
|REORGANIZATION_MANIFEST.md|1|21941|
|REORGANIZATION_REPORT.md|1|12134|
|archive/AGENTS.md|1|768|
|archive/environment_records|88|70522254|
|archive/historical_validation|177|106375118|
|archive/legacy_compatibility|1754|848603630|
|archive/legacy_dog_a|1552|779793611|
|archive/migration_backups|69|770265392|
|audits/progress_audit_20261103|23|2606093|
|blackhorse_lightstick/AGENTS.md|1|652|
|blackhorse_lightstick/DEVELOPMENT_ENV_REPORT.md|1|11140|
|blackhorse_lightstick/README.md|1|4400|
|blackhorse_lightstick/docs|2|1739541|
|blackhorse_lightstick/firmware|2164|59798623|
|blackhorse_lightstick/tools|15|32498|
|course_presentation/DELIVERY.md|1|1659|
|course_presentation/PROJECT_EVIDENCE.md|1|15628|
|course_presentation/assets|9|2131640|
|course_presentation/lo_profile|36|183143|
|course_presentation/model_audit_readonly.json|1|5251|
|course_presentation/preview|6|1093580|
|course_presentation/scripts|4|20441|
|course_presentation/source_hashes.json|1|4407|
|course_presentation/vendor|311|3650081|
|course_presentation/四足机器人项目_三人分工汇报.pdf|1|436910|
|course_presentation/机器人综合实践赵祥淇-倪帅欣-吕启超组.pptx|1|1282597|
|dogfight_rl/.git|347|15233349|
|dogfight_rl/.gitignore|1|436|
|dogfight_rl/.pytest_cache|5|10736|
|dogfight_rl/AGENTS.md|1|4231|
|dogfight_rl/DOGFIGHT_THREE_DOG_DELIVERY.md|1|10901|
|dogfight_rl/DOGFIGHT_V0_2_DELIVERY.md|1|8165|
|dogfight_rl/DOGFIGHT_V0_INTERFACE_SPEC.md|1|23045|
|dogfight_rl/ENVIRONMENT.md|1|2967|
|dogfight_rl/ENV_LOCK.md|1|1102|
|dogfight_rl/README.md|1|1337|
|dogfight_rl/THIRD_PARTY_NOTICES.md|1|1241|
|dogfight_rl/__pycache__|1|5910|
|dogfight_rl/assets|38|71739217|
|dogfight_rl/configs|16|23375|
|dogfight_rl/csdog_ppo_tuning_v5|21|140298|
|dogfight_rl/docs|8|32943|
|dogfight_rl/launch.py|1|3837|
|dogfight_rl/pyproject.toml|1|193|
|dogfight_rl/runs|5744|39467854694|
|dogfight_rl/scripts|127|1061768|
|dogfight_rl/setup.py|1|277|
|dogfight_rl/src|299|1528681|
|dogfight_rl/tests|60|651470|
|model/meshes|13|1932842|
|model/package.xml|1|269|
|model/robot.preview.urdf|1|13051|
|model/robot.urdf|1|12505|
|peer_csdog_review/FINAL_MIGRATION_RECOMMENDATION.md|1|3012|
|peer_csdog_review/PEER_CSDOG_ARCHIVE_AUDIT.md|1|2872|
|peer_csdog_review/PEER_CSDOG_MODEL_COMPARISON.md|1|3056|
|peer_csdog_review/PEER_CSDOG_PPO_COMPARISON.md|1|3448|
|peer_csdog_review/PEER_CSDOG_RUNTIME_TEST.md|1|5553|
|peer_csdog_review/archive.sha256|1|105|
|peer_csdog_review/archive_listing.json|1|54216|
|peer_csdog_review/archive_listing.txt|1|42358|
|peer_csdog_review/csdog-v2-teleop-v0.1.0-complete.tar.gz|1|12580464|
|peer_csdog_review/evaluate_ours_v61.py|1|3671|
|peer_csdog_review/extracted|260|30159538|
|peer_csdog_review/joint_test.log|1|12140|
|peer_csdog_review/joint_test.py|1|1747|
|peer_csdog_review/ours_gpu.lock|1|0|
|peer_csdog_review/ours_v61_probe|5|4767998|
|peer_csdog_review/ours_v61_probe.log|1|3763|
|peer_csdog_review/outputs|72|321282|
|peer_csdog_review/peer_backward_015.json|1|11003|
|peer_csdog_review/peer_backward_015.log|1|23352|
|peer_csdog_review/peer_backward_025.json|1|11411|
|peer_csdog_review/peer_backward_025.log|1|23760|
|peer_csdog_review/peer_csdog_backward.mp4|1|1136368|
|peer_csdog_review/peer_csdog_forward.mp4|1|1146698|
|peer_csdog_review/peer_csdog_turn.mp4|1|1019080|
|peer_csdog_review/peer_forward_015.json|1|10524|
|peer_csdog_review/peer_forward_015.log|1|22874|
|peer_csdog_review/peer_forward_025.json|1|10014|
|peer_csdog_review/peer_forward_025.log|1|22643|
|peer_csdog_review/peer_joint_pulses.json|1|2022|
|peer_csdog_review/peer_perturbed_backward_015.json|1|11291|
|peer_csdog_review/peer_perturbed_backward_015.log|1|23922|
|peer_csdog_review/peer_perturbed_backward_025.json|1|11408|
|peer_csdog_review/peer_perturbed_backward_025.log|1|24039|
|peer_csdog_review/peer_perturbed_forward_015.json|1|10487|
|peer_csdog_review/peer_perturbed_forward_015.log|1|23118|
|peer_csdog_review/peer_perturbed_forward_025.json|1|9849|
|peer_csdog_review/peer_perturbed_forward_025.log|1|22480|
|peer_csdog_review/peer_perturbed_stand.json|1|10379|
|peer_csdog_review/peer_perturbed_stand.log|1|23010|
|peer_csdog_review/peer_perturbed_turn_left.json|1|10890|
|peer_csdog_review/peer_perturbed_turn_left.log|1|23521|
|peer_csdog_review/peer_perturbed_turn_right.json|1|12539|
|peer_csdog_review/peer_perturbed_turn_right.log|1|25170|
|peer_csdog_review/peer_phase_match.json|1|1549|
|peer_csdog_review/peer_stand.json|1|10483|
|peer_csdog_review/peer_stand.log|1|23112|
|peer_csdog_review/peer_stand_30s.json|1|59706|
|peer_csdog_review/peer_turn_left.json|1|10893|
|peer_csdog_review/peer_turn_left.log|1|23242|
|peer_csdog_review/peer_turn_right.json|1|12577|
|peer_csdog_review/peer_turn_right.log|1|25206|
|peer_csdog_review/peer_video_backward.json|1|8501|
|peer_csdog_review/peer_video_backward.log|1|20394|
|peer_csdog_review/peer_video_forward.json|1|7862|
|peer_csdog_review/peer_video_forward.log|1|19908|
|peer_csdog_review/peer_video_turn.json|1|9380|
|peer_csdog_review/peer_video_turn.log|1|21413|
|peer_csdog_review/safe_extract.py|1|2598|
|peer_csdog_review/stand_test.log|1|11213|
|peer_csdog_review/stand_test.py|1|2439|
|peer_csdog_review/video_backward_frame.png|1|331296|
|peer_csdog_review/video_forward_frame.png|1|350680|
|peer_csdog_review/video_play.py|1|46746|
|peer_csdog_review/video_play_perturbed.py|1|47211|
|peer_csdog_review/video_turn_frame.png|1|323846|
|peer_csdog_review/write_reports.py|1|20171|
|reorganization/20261026|104|4640970|
|格式规范.md|1|23045|

## 必须上传与推荐上传逐文件清单

目标GitHub路径规则：项目内 `dogfight_rl/<rel>` → `desktop_playable/dogfight_rl/<rel>`；`model/<rel>` → `desktop_playable/model/<rel>`；根说明/reorganization/audits保留在desktop_playable对应相对位置；桌面原件仅以脱敏模板提交到dogfight_rl/scripts/teleop/。证据可以按原相对路径显式放行，或复制到独立发布工作副本的docs/desktop_playable/evidence并记录原路径；本轮未复制。全部必要文件类型、调用方详见依赖报告逐项表。

|绝对路径|项目相对路径|字节|类型|调用入口/用途|运行必要|类别|上传方式|理由|
|---|---|---|---|---|---|---|---|---|
|/home/zxq/robot_projects/AGENTS.md|AGENTS.md|2854|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/DOGFIGHT_ENVIRONMENT.md|DOGFIGHT_ENVIRONMENT.md|7875|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/PROJECT_STRUCTURE.md|PROJECT_STRUCTURE.md|6223|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|PROJECT_STRUCTURE_AUDIT.md|268714|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/REORGANIZATION_MANIFEST.md|REORGANIZATION_MANIFEST.md|21941|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/REORGANIZATION_REPORT.md|REORGANIZATION_REPORT.md|12134|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/AUDIT_PROBES.json|audits/progress_audit_20261103/AUDIT_PROBES.json|13581|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/BATTLE_SYSTEM_AUDIT.md|audits/progress_audit_20261103/BATTLE_SYSTEM_AUDIT.md|8062|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/BLOCKERS_AND_ROADMAP.md|audits/progress_audit_20261103/BLOCKERS_AND_ROADMAP.md|10386|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/CHECKPOINT_INVENTORY.json|audits/progress_audit_20261103/CHECKPOINT_INVENTORY.json|311519|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/DIRECTORY_TREE.txt|audits/progress_audit_20261103/DIRECTORY_TREE.txt|1700|.txt|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/ENVIRONMENT_SNAPSHOT.json|audits/progress_audit_20261103/ENVIRONMENT_SNAPSHOT.json|237|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/EVIDENCE_TIMELINE.json|audits/progress_audit_20261103/EVIDENCE_TIMELINE.json|14315|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/FILE_INVENTORY.json|audits/progress_audit_20261103/FILE_INVENTORY.json|1986450|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/FINAL_SUMMARY.md|audits/progress_audit_20261103/FINAL_SUMMARY.md|8270|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/MAP_AUDIT.md|audits/progress_audit_20261103/MAP_AUDIT.md|5080|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/MAP_BATTLE_RESOURCE_INDEX.txt|audits/progress_audit_20261103/MAP_BATTLE_RESOURCE_INDEX.txt|2960|.txt|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/MODEL_AND_RL_AUDIT.md|audits/progress_audit_20261103/MODEL_AND_RL_AUDIT.md|13529|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|audits/progress_audit_20261103/PROGRESS_MATRIX.md|12155|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROJECT_OVERVIEW.md|audits/progress_audit_20261103/PROJECT_OVERVIEW.md|6069|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/README.md|audits/progress_audit_20261103/README.md|3265|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/REFEREE_AUDIT.md|audits/progress_audit_20261103/REFEREE_AUDIT.md|7286|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_HASHES_BEFORE.json|audits/progress_audit_20261103/SOURCE_HASHES_BEFORE.json|33865|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_INTEGRITY.json|audits/progress_audit_20261103/SOURCE_INTEGRITY.json|195|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|90579|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/TEST_EXECUTION.md|audits/progress_audit_20261103/TEST_EXECUTION.md|1463|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/audit_probes.py|audits/progress_audit_20261103/audit_probes.py|4417|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/pytest_results.xml|audits/progress_audit_20261103/pytest_results.xml|1558|.xml|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/audits/progress_audit_20261103/write_audit_reports.py|audits/progress_audit_20261103/write_audit_reports.py|69152|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/AGENTS.md|dogfight_rl/AGENTS.md|4231|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/DOGFIGHT_THREE_DOG_DELIVERY.md|dogfight_rl/DOGFIGHT_THREE_DOG_DELIVERY.md|10901|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/DOGFIGHT_V0_2_DELIVERY.md|dogfight_rl/DOGFIGHT_V0_2_DELIVERY.md|8165|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/DOGFIGHT_V0_INTERFACE_SPEC.md|dogfight_rl/DOGFIGHT_V0_INTERFACE_SPEC.md|23045|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/ENVIRONMENT.md|dogfight_rl/ENVIRONMENT.md|2967|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/ENV_LOCK.md|dogfight_rl/ENV_LOCK.md|1102|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/README.md|dogfight_rl/README.md|1337|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/THIRD_PARTY_NOTICES.md|dogfight_rl/THIRD_PARTY_NOTICES.md|1241|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/IMPORT_MANIFEST.json|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/IMPORT_MANIFEST.json|2203|.json|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/README.md|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/README.md|1693|.md|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/base_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/base_collision.stl|1484|.stl|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_pitch_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_pitch_collision.stl|190484|.stl|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_roll_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_roll_collision.stl|236484|.stl|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_knee_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_knee_collision.stl|53684|.stl|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_pitch_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_pitch_collision.stl|190634|.stl|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_roll_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_roll_collision.stl|236984|.stl|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_knee_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_knee_collision.stl|53734|.stl|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_pitch_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_pitch_collision.stl|197184|.stl|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_roll_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_roll_collision.stl|236234|.stl|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_knee_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_knee_collision.stl|53634|.stl|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_pitch_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_pitch_collision.stl|190784|.stl|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_roll_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_roll_collision.stl|237534|.stl|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_knee_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_knee_collision.stl|53984|.stl|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/robot.urdf|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/robot.urdf|12505|.urdf|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/robot_sim.urdf|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/robot_sim.urdf|18907|.urdf|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/policies/v1/identity.json|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/policies/v1/identity.json|1367|.json|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/policies/v1/model_final.pt|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/policies/v1/model_final.pt|2722815|.pt|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/.asset_hash|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/.asset_hash|32|无扩展|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/config.yaml|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/config.yaml|1719|.yaml|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_base.usd|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_base.usd|2795101|.usd|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_physics.usd|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_physics.usd|6438|.usd|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_robot.usd|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_robot.usd|2075|.usd|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_sensor.usd|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_sensor.usd|645|.usd|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/csdog.usd|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/csdog.usd|1454|.usd|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/assets/ui/dogfight_teleop.svg|dogfight_rl/assets/ui/dogfight_teleop.svg|521|.svg|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/configs/autoppo/csdog-autoppo-lab.service|dogfight_rl/configs/autoppo/csdog-autoppo-lab.service|958|.service|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/configs/autoppo/curriculum.yaml|dogfight_rl/configs/autoppo/curriculum.yaml|258|.yaml|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/configs/autoppo/evaluation.yaml|dogfight_rl/configs/autoppo/evaluation.yaml|543|.yaml|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/configs/autoppo/search_space.yaml|dogfight_rl/configs/autoppo/search_space.yaml|737|.yaml|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/configs/autoppo/system.yaml|dogfight_rl/configs/autoppo/system.yaml|385|.yaml|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/configs/battle/extension.toml|dogfight_rl/configs/battle/extension.toml|426|.toml|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/configs/locomotion/csdog_ppo/model_audit.json|dogfight_rl/configs/locomotion/csdog_ppo/model_audit.json|12619|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/configs/locomotion/csdog_ppo/stage1.json|dogfight_rl/configs/locomotion/csdog_ppo/stage1.json|227|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/configs/locomotion/csdog_ppo/stage2.json|dogfight_rl/configs/locomotion/csdog_ppo/stage2.json|225|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/configs/locomotion/curriculum_v6/default.json|dogfight_rl/configs/locomotion/curriculum_v6/default.json|875|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/configs/locomotion/curriculum_v6_1/default.json|dogfight_rl/configs/locomotion/curriculum_v6_1/default.json|1146|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/configs/robots/csdog_12dof.yaml|dogfight_rl/configs/robots/csdog_12dof.yaml|381|.yaml|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/configs/robots/dog_a_teleop.yaml|dogfight_rl/configs/robots/dog_a_teleop.yaml|1251|.yaml|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/configs/teleop/default.yaml|dogfight_rl/configs/teleop/default.yaml|968|.yaml|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/configs/teleop/fsm_battle.yaml|dogfight_rl/configs/teleop/fsm_battle.yaml|1764|.yaml|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/configs/teleop/single_dog.yaml|dogfight_rl/configs/teleop/single_dog.yaml|612|.yaml|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/docs/BATTLE_GUIDE.md|dogfight_rl/docs/BATTLE_GUIDE.md|1176|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/docs/BATTLE_PACKAGE.md|dogfight_rl/docs/BATTLE_PACKAGE.md|471|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/docs/DOGFIGHT_V0_INTERFACE_SPEC.md|dogfight_rl/docs/DOGFIGHT_V0_INTERFACE_SPEC.md|2071|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/docs/FIRST_PERSON_VIEW.md|dogfight_rl/docs/FIRST_PERSON_VIEW.md|2898|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|19854|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/docs/LOCOMOTION_PPO.md|dogfight_rl/docs/LOCOMOTION_PPO.md|683|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/docs/TELEOP_POLICY_AUDIT.md|dogfight_rl/docs/TELEOP_POLICY_AUDIT.md|4756|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/docs/TRAINING_GUIDE.md|dogfight_rl/docs/TRAINING_GUIDE.md|1034|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/launch.py|dogfight_rl/launch.py|3837|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/pyproject.toml|dogfight_rl/pyproject.toml|193|.toml|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/combat_events/events.jsonl|dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/combat_events/events.jsonl|1401|.jsonl|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/identity.json|dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/identity.json|2993|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/launch.json|dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/launch.json|4868|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/metrics.json|dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/metrics.json|998|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/navigation_trace.jsonl|dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/navigation_trace.jsonl|0|.jsonl|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/physical_navigation_1500.png|dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/physical_navigation_1500.png|948041|.png|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/physical_navigation_500.png|dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/physical_navigation_500.png|929753|.png|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/physical_navigation_result.json|dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/physical_navigation_result.json|616|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/physical_navigation_trace.jsonl|dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/physical_navigation_trace.jsonl|129034|.jsonl|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/trace.json|dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/trace.json|2|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/combat_events/events.jsonl|dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/combat_events/events.jsonl|4840|.jsonl|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/identity.json|dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/identity.json|2989|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/launch.json|dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/launch.json|4868|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/metrics.json|dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/metrics.json|991|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/navigation_trace.jsonl|dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/navigation_trace.jsonl|0|.jsonl|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/physical_range_checks.json|dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/physical_range_checks.json|4094|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/range_beyond_three.png|dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/range_beyond_three.png|946224|.png|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/range_nearest_dog.png|dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/range_nearest_dog.png|910287|.png|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/range_two_meters.png|dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/range_two_meters.png|891964|.png|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/range_wall_occlusion.png|dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/range_wall_occlusion.png|921929|.png|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/trace.json|dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/trace.json|2|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/combat_events/events.jsonl|dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/combat_events/events.jsonl|7741|.jsonl|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/identity.json|dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/identity.json|2993|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/launch.json|dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/launch.json|4915|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/metrics.json|dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/metrics.json|1102|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/navigation_trace.jsonl|dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/navigation_trace.jsonl|670712|.jsonl|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/status.json|dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/status.json|1850|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/trace.json|dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/trace.json|671062|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/combat_events/events.jsonl|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/combat_events/events.jsonl|22893|.jsonl|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_gui_acceptance.json|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_gui_acceptance.json|20278|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_match_20.png|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_match_20.png|1191080|.png|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_reset.png|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_reset.png|1212360|.png|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_result.png|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_result.png|1226284|.png|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_routes_off.png|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_routes_off.png|1189641|.png|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_routes_on.png|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_routes_on.png|1181001|.png|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_routes_restored.png|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_routes_restored.png|1198797|.png|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/identity.json|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/identity.json|2989|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/launch.json|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/launch.json|4831|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/metrics.json|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/metrics.json|1106|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/navigation_trace.jsonl|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/navigation_trace.jsonl|1367331|.jsonl|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/status.json|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/status.json|3170|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/trace.json|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/trace.json|1367758|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/validation_summary.json|dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/validation_summary.json|3065|.json|历史验收记录|否（推荐保留）|推荐上传|普通 Git|保留实际验收证据；不是运行必需|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/delivery_evidence_summary.log|dogfight_rl/runs/validation/fsm_v1_20261103/delivery_evidence_summary.log|3066|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/evidence_summary.log|dogfight_rl/runs/validation/fsm_v1_20261103/evidence_summary.log|3484|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/final_handoff.json|dogfight_rl/runs/validation/fsm_v1_20261103/final_handoff.json|1343|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/fsm_debug_draw_gui.log|dogfight_rl/runs/validation/fsm_v1_20261103/fsm_debug_draw_gui.log|197|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/fsm_debug_draw_unlocked.log|dogfight_rl/runs/validation/fsm_v1_20261103/fsm_debug_draw_unlocked.log|320|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/fsm_delivery_gui.log|dogfight_rl/runs/validation/fsm_v1_20261103/fsm_delivery_gui.log|324|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/fsm_gui_final.log|dogfight_rl/runs/validation/fsm_v1_20261103/fsm_gui_final.log|209|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/fsm_gui_final_v2.log|dogfight_rl/runs/validation/fsm_v1_20261103/fsm_gui_final_v2.log|321|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/git_before.txt|dogfight_rl/runs/validation/fsm_v1_20261103/git_before.txt|12042|.txt|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/handoff_gui.log|dogfight_rl/runs/validation/fsm_v1_20261103/handoff_gui.log|197|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight.json|dogfight_rl/runs/validation/fsm_v1_20261103/preflight.json|5170|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_delivery.log|dogfight_rl/runs/validation/fsm_v1_20261103/preflight_delivery.log|5181|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.json|dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.json|5181|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.log|dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.log|5186|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/protected_assets_after.json|dogfight_rl/runs/validation/fsm_v1_20261103/protected_assets_after.json|3275|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|24936|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/teleop_gui_acceptance.json|dogfight_rl/runs/validation/fsm_v1_20261103/teleop_gui_acceptance.json|69578|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/teleop_gui_regression.log|dogfight_rl/runs/validation/fsm_v1_20261103/teleop_gui_regression.log|866|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_delivery.log|dogfight_rl/runs/validation/fsm_v1_20261103/unit_delivery.log|530|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_final.log|dogfight_rl/runs/validation/fsm_v1_20261103/unit_final.log|530|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_final_v2.log|dogfight_rl/runs/validation/fsm_v1_20261103/unit_final_v2.log|530|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_final_v3.log|dogfight_rl/runs/validation/fsm_v1_20261103/unit_final_v3.log|530|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_final_v4.log|dogfight_rl/runs/validation/fsm_v1_20261103/unit_final_v4.log|530|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_final_v5.log|dogfight_rl/runs/validation/fsm_v1_20261103/unit_final_v5.log|530|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_initial.log|dogfight_rl/runs/validation/fsm_v1_20261103/unit_initial.log|530|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_render_final.log|dogfight_rl/runs/validation/fsm_v1_20261103/unit_render_final.log|530|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_v2.log|dogfight_rl/runs/validation/fsm_v1_20261103/unit_v2.log|530|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_v3.log|dogfight_rl/runs/validation/fsm_v1_20261103/unit_v3.log|530|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/autoppo/audit_physics.py|dogfight_rl/scripts/autoppo/audit_physics.py|4077|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/autoppo/autoppo.py|dogfight_rl/scripts/autoppo/autoppo.py|4167|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/autoppo/finalize_validation.py|dogfight_rl/scripts/autoppo/finalize_validation.py|3995|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/autoppo/install_service.py|dogfight_rl/scripts/autoppo/install_service.py|1180|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/autoppo/smoke_test.py|dogfight_rl/scripts/autoppo/smoke_test.py|2898|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/autoppo/v7.py|dogfight_rl/scripts/autoppo/v7.py|2997|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/autoppo/verify_launch.py|dogfight_rl/scripts/autoppo/verify_launch.py|9820|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/autoppo/write_reports.py|dogfight_rl/scripts/autoppo/write_reports.py|13775|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/battle/run_v02_hud_smoke_tests.py|dogfight_rl/scripts/battle/run_v02_hud_smoke_tests.py|4800|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/battle/run_v0_battle_demo.py|dogfight_rl/scripts/battle/run_v0_battle_demo.py|8834|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/battle/run_v0_gui.py|dogfight_rl/scripts/battle/run_v0_gui.py|2312|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/battle/run_v0_headless.py|dogfight_rl/scripts/battle/run_v0_headless.py|2051|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/battle/run_v0_smoke_tests.py|dogfight_rl/scripts/battle/run_v0_smoke_tests.py|9959|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/analyze_csdog_aligned_v3.py|dogfight_rl/scripts/diagnostics/analyze_csdog_aligned_v3.py|5455|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/analyze_csdog_experiment.py|dogfight_rl/scripts/diagnostics/analyze_csdog_experiment.py|4848|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/analyze_csdog_spot_v2.py|dogfight_rl/scripts/diagnostics/analyze_csdog_spot_v2.py|4202|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/check_environment.py|dogfight_rl/scripts/diagnostics/check_environment.py|3723|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/check_environment.sh|dogfight_rl/scripts/diagnostics/check_environment.sh|776|.sh|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/convert_csdog.py|dogfight_rl/scripts/diagnostics/convert_csdog.py|947|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/csdog_aligned_dynamics.py|dogfight_rl/scripts/diagnostics/csdog_aligned_dynamics.py|6249|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/csdog_aligned_fixture.py|dogfight_rl/scripts/diagnostics/csdog_aligned_fixture.py|3217|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/csdog_aligned_joint_properties.py|dogfight_rl/scripts/diagnostics/csdog_aligned_joint_properties.py|1596|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/csdog_aligned_pd_probe.py|dogfight_rl/scripts/diagnostics/csdog_aligned_pd_probe.py|3227|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/csdog_aligned_unload.py|dogfight_rl/scripts/diagnostics/csdog_aligned_unload.py|5438|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/csdog_physics_check.py|dogfight_rl/scripts/diagnostics/csdog_physics_check.py|3400|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/csdog_reward_gate.py|dogfight_rl/scripts/diagnostics/csdog_reward_gate.py|1364|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/csdog_spot_gate.py|dogfight_rl/scripts/diagnostics/csdog_spot_gate.py|4453|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/csdog_spot_v4_balance.py|dogfight_rl/scripts/diagnostics/csdog_spot_v4_balance.py|8674|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/curriculum_supervisor.py|dogfight_rl/scripts/diagnostics/curriculum_supervisor.py|3302|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/curriculum_v6_1_supervisor.py|dogfight_rl/scripts/diagnostics/curriculum_v6_1_supervisor.py|5956|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/curriculum_v6_3_manager.py|dogfight_rl/scripts/diagnostics/curriculum_v6_3_manager.py|6978|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/manage_nvidia_apt_hold.sh|dogfight_rl/scripts/diagnostics/manage_nvidia_apt_hold.sh|1304|.sh|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/official_train_check.py|dogfight_rl/scripts/diagnostics/official_train_check.py|634|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/plot_spot_v4_validation.py|dogfight_rl/scripts/diagnostics/plot_spot_v4_validation.py|4372|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/run_csdog_aligned_evaluations.py|dogfight_rl/scripts/diagnostics/run_csdog_aligned_evaluations.py|1966|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/seal_csdog_aligned_v3.py|dogfight_rl/scripts/diagnostics/seal_csdog_aligned_v3.py|5986|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/seal_csdog_task.py|dogfight_rl/scripts/diagnostics/seal_csdog_task.py|1851|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/seal_v7_validation.py|dogfight_rl/scripts/diagnostics/seal_v7_validation.py|3491|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/v6_1_comparison_report.py|dogfight_rl/scripts/diagnostics/v6_1_comparison_report.py|9899|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/v6_1_contact_report.py|dogfight_rl/scripts/diagnostics/v6_1_contact_report.py|7688|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/v6_1_experiment_batch.py|dogfight_rl/scripts/diagnostics/v6_1_experiment_batch.py|3337|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/v6_1_finalize.py|dogfight_rl/scripts/diagnostics/v6_1_finalize.py|7167|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/v6_1_history_batch.py|dogfight_rl/scripts/diagnostics/v6_1_history_batch.py|1068|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/v6_1_repair_report.py|dogfight_rl/scripts/diagnostics/v6_1_repair_report.py|8926|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/v6_3_ab_report.py|dogfight_rl/scripts/diagnostics/v6_3_ab_report.py|6789|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/v6_3_failure_analysis.py|dogfight_rl/scripts/diagnostics/v6_3_failure_analysis.py|6142|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/v6_3_history.py|dogfight_rl/scripts/diagnostics/v6_3_history.py|2166|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/v6_3_history_report.py|dogfight_rl/scripts/diagnostics/v6_3_history_report.py|7567|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/v6_3_launch_report.py|dogfight_rl/scripts/diagnostics/v6_3_launch_report.py|2439|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/v7_collision_probe.py|dogfight_rl/scripts/diagnostics/v7_collision_probe.py|8526|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/v7_lift_probe.py|dogfight_rl/scripts/diagnostics/v7_lift_probe.py|3057|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/verify_integrity.py|dogfight_rl/scripts/diagnostics/verify_integrity.py|4935|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/verify_training_runtime.py|dogfight_rl/scripts/diagnostics/verify_training_runtime.py|2486|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/write_csdog_aligned_report.py|dogfight_rl/scripts/diagnostics/write_csdog_aligned_report.py|21538|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/write_csdog_aligned_reward_report.py|dogfight_rl/scripts/diagnostics/write_csdog_aligned_reward_report.py|3763|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/write_csdog_report.py|dogfight_rl/scripts/diagnostics/write_csdog_report.py|19106|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/write_csdog_spot_report.py|dogfight_rl/scripts/diagnostics/write_csdog_spot_report.py|17884|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/evaluate/csdog_12dof.py|dogfight_rl/scripts/evaluate/csdog_12dof.py|9966|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/evaluate/csdog_curriculum_v6.py|dogfight_rl/scripts/evaluate/csdog_curriculum_v6.py|3241|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/evaluate/csdog_curriculum_v6_1.py|dogfight_rl/scripts/evaluate/csdog_curriculum_v6_1.py|3649|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/evaluate/csdog_spot_aligned_v3.py|dogfight_rl/scripts/evaluate/csdog_spot_aligned_v3.py|11809|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/evaluate/csdog_spot_v2.py|dogfight_rl/scripts/evaluate/csdog_spot_v2.py|10356|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/evaluate/csdog_spot_v4.py|dogfight_rl/scripts/evaluate/csdog_spot_v4.py|6371|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/evaluate/csdog_spot_v5.py|dogfight_rl/scripts/evaluate/csdog_spot_v5.py|2031|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/launch_dogfight_fsm.sh|dogfight_rl/scripts/launch_dogfight_fsm.sh|302|.sh|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/scripts/launch_dogfight_teleop.sh|dogfight_rl/scripts/launch_dogfight_teleop.sh|2304|.sh|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/dogfight-fsm.desktop|dogfight_rl/scripts/teleop/dogfight-fsm.desktop|500|.desktop|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/dogfight-teleop.desktop|dogfight_rl/scripts/teleop/dogfight-teleop.desktop|480|.desktop|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/run.py|dogfight_rl/scripts/teleop/run.py|3864|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/summarize_fsm_validation.py|dogfight_rl/scripts/teleop/summarize_fsm_validation.py|3761|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_attached_gui.py|dogfight_rl/scripts/teleop/verify_attached_gui.py|3392|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_desktop_launch.py|dogfight_rl/scripts/teleop/verify_desktop_launch.py|4101|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_fsm_gui.py|dogfight_rl/scripts/teleop/verify_fsm_gui.py|4762|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_keyboard_gui.py|dogfight_rl/scripts/teleop/verify_keyboard_gui.py|3542|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_three_dog_gui.py|dogfight_rl/scripts/teleop/verify_three_dog_gui.py|4723|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/train/csdog_12dof.py|dogfight_rl/scripts/train/csdog_12dof.py|4474|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/train/csdog_curriculum_v6.py|dogfight_rl/scripts/train/csdog_curriculum_v6.py|17746|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/train/csdog_curriculum_v6_1.py|dogfight_rl/scripts/train/csdog_curriculum_v6_1.py|20731|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/train/csdog_curriculum_v6_3.py|dogfight_rl/scripts/train/csdog_curriculum_v6_3.py|10411|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/train/csdog_spot_aligned_v3.py|dogfight_rl/scripts/train/csdog_spot_aligned_v3.py|5070|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/train/csdog_spot_v2.py|dogfight_rl/scripts/train/csdog_spot_v2.py|4474|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/train/csdog_spot_v4.py|dogfight_rl/scripts/train/csdog_spot_v4.py|10736|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/scripts/train/csdog_spot_v5.py|dogfight_rl/scripts/train/csdog_spot_v5.py|6563|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/setup.py|dogfight_rl/setup.py|277|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/__init__.py|dogfight_rl/src/dogfight/__init__.py|75|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/__init__.py|dogfight_rl/src/dogfight/autoppo/__init__.py|82|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/checkpoint_bank.py|dogfight_rl/src/dogfight/autoppo/checkpoint_bank.py|6307|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/config.py|dogfight_rl/src/dogfight/autoppo/config.py|735|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/curriculum_manager.py|dogfight_rl/src/dogfight/autoppo/curriculum_manager.py|1240|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/evaluation.py|dogfight_rl/src/dogfight/autoppo/evaluation.py|4236|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/experiment_manager.py|dogfight_rl/src/dogfight/autoppo/experiment_manager.py|21439|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/gait_audit.py|dogfight_rl/src/dogfight/autoppo/gait_audit.py|8056|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/motion_evaluator.py|dogfight_rl/src/dogfight/autoppo/motion_evaluator.py|4648|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/phase_v7_manager.py|dogfight_rl/src/dogfight/autoppo/phase_v7_manager.py|19225|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/phase_v7_search.py|dogfight_rl/src/dogfight/autoppo/phase_v7_search.py|4567|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/plots.py|dogfight_rl/src/dogfight/autoppo/plots.py|1230|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/recovery_manager.py|dogfight_rl/src/dogfight/autoppo/recovery_manager.py|1580|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/resource_monitor.py|dogfight_rl/src/dogfight/autoppo/resource_monitor.py|1125|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/rewards.py|dogfight_rl/src/dogfight/autoppo/rewards.py|407|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/runtime.py|dogfight_rl/src/dogfight/autoppo/runtime.py|2342|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/search_optimizer.py|dogfight_rl/src/dogfight/autoppo/search_optimizer.py|5495|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/storage.py|dogfight_rl/src/dogfight/autoppo/storage.py|5717|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/stride.py|dogfight_rl/src/dogfight/autoppo/stride.py|8922|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/train_runner.py|dogfight_rl/src/dogfight/autoppo/train_runner.py|14941|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/common/__init__.py|dogfight_rl/src/dogfight/common/__init__.py|48|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/common/paths.py|dogfight_rl/src/dogfight/common/paths.py|1454|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/fsm/__init__.py|dogfight_rl/src/dogfight/fsm/__init__.py|77|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/fsm/controller.py|dogfight_rl/src/dogfight/fsm/controller.py|7329|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/fsm/navigation.py|dogfight_rl/src/dogfight/fsm/navigation.py|6498|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/fsm/perception.py|dogfight_rl/src/dogfight/fsm/perception.py|3112|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/fsm/physical_validation.py|dogfight_rl/src/dogfight/fsm/physical_validation.py|7601|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/fsm/visualization.py|dogfight_rl/src/dogfight/fsm/visualization.py|2392|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/LICENSE.NVIDIA|dogfight_rl/src/dogfight/locomotion/LICENSE.NVIDIA|1630|.NVIDIA|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/README.md|dogfight_rl/src/dogfight/locomotion/README.md|440|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/THIRD_PARTY_NOTICES.md|dogfight_rl/src/dogfight/locomotion/THIRD_PARTY_NOTICES.md|1912|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/__init__.py|dogfight_rl/src/dogfight/locomotion/__init__.py|356|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/budget.py|dogfight_rl/src/dogfight/locomotion/budget.py|1684|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/control_validation/__init__.py|dogfight_rl/src/dogfight/locomotion/control_validation/__init__.py|69|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/control_validation/kinematics.py|dogfight_rl/src/dogfight/locomotion/control_validation/kinematics.py|4595|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6/OLD_EXPERIMENT_ANALYSIS.md|dogfight_rl/src/dogfight/locomotion/curriculum_v6/OLD_EXPERIMENT_ANALYSIS.md|2108|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6/README.md|dogfight_rl/src/dogfight/locomotion/curriculum_v6/README.md|5152|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6/__init__.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6/__init__.py|91|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6/commands.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6/commands.py|407|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6/config.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6/config.py|4697|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6/evaluation.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6/evaluation.py|6990|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6/rewards.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6/rewards.py|2568|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6/runner.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6/runner.py|7375|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6/supervisor.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6/supervisor.py|13522|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/__init__.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/__init__.py|81|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/config.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/config.py|677|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/contacts.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/contacts.py|2739|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/evaluation.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/evaluation.py|5192|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/events.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/events.py|581|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/rewards.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/rewards.py|3330|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/runner.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/runner.py|3734|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/supervisor.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_1/supervisor.py|14038|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/__init__.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/__init__.py|83|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/config.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/config.py|2105|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/evaluation.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/evaluation.py|6433|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/evaluation_version.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/evaluation_version.py|31|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/rewards.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/rewards.py|712|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/runner.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/runner.py|2712|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/stride.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/stride.py|6631|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/supervisor.py|dogfight_rl/src/dogfight/locomotion/curriculum_v6_3/supervisor.py|6742|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/env_cfg.py|dogfight_rl/src/dogfight/locomotion/env_cfg.py|6385|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/mdp.py|dogfight_rl/src/dogfight/locomotion/mdp.py|2484|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/model_audit.py|dogfight_rl/src/dogfight/locomotion/model_audit.py|3664|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/phase_guided_v7/__init__.py|dogfight_rl/src/dogfight/locomotion/phase_guided_v7/__init__.py|81|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/phase_guided_v7/evaluation.py|dogfight_rl/src/dogfight/locomotion/phase_guided_v7/evaluation.py|8171|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/phase_guided_v7/kernel.py|dogfight_rl/src/dogfight/locomotion/phase_guided_v7/kernel.py|3420|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/phase_guided_v7/plots.py|dogfight_rl/src/dogfight/locomotion/phase_guided_v7/plots.py|2965|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/phase_guided_v7/reporting.py|dogfight_rl/src/dogfight/locomotion/phase_guided_v7/reporting.py|8737|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/phase_guided_v7/runtime.py|dogfight_rl/src/dogfight/locomotion/phase_guided_v7/runtime.py|4835|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/phase_guided_v7/trace_metrics.py|dogfight_rl/src/dogfight/locomotion/phase_guided_v7/trace_metrics.py|3029|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/phase_guided_v7/train.py|dogfight_rl/src/dogfight/locomotion/phase_guided_v7/train.py|7111|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/ppo_cfg.py|dogfight_rl/src/dogfight/locomotion/ppo_cfg.py|923|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/robot_cfg.py|dogfight_rl/src/dogfight/locomotion/robot_cfg.py|1267|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/runner.py|dogfight_rl/src/dogfight/locomotion/runner.py|2809|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_aligned_v3/__init__.py|dogfight_rl/src/dogfight/locomotion/spot_aligned_v3/__init__.py|386|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_aligned_v3/budget.py|dogfight_rl/src/dogfight/locomotion/spot_aligned_v3/budget.py|1870|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_aligned_v3/calibration.py|dogfight_rl/src/dogfight/locomotion/spot_aligned_v3/calibration.py|374|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_aligned_v3/config.py|dogfight_rl/src/dogfight/locomotion/spot_aligned_v3/config.py|4083|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_aligned_v3/rewards.py|dogfight_rl/src/dogfight/locomotion/spot_aligned_v3/rewards.py|2419|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_aligned_v3/runner.py|dogfight_rl/src/dogfight/locomotion/spot_aligned_v3/runner.py|1870|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v2/__init__.py|dogfight_rl/src/dogfight/locomotion/spot_v2/__init__.py|85|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v2/budget.py|dogfight_rl/src/dogfight/locomotion/spot_v2/budget.py|1576|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v2/config.py|dogfight_rl/src/dogfight/locomotion/spot_v2/config.py|1783|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v2/contacts.py|dogfight_rl/src/dogfight/locomotion/spot_v2/contacts.py|4597|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v2/rewards.py|dogfight_rl/src/dogfight/locomotion/spot_v2/rewards.py|2616|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v2/runner.py|dogfight_rl/src/dogfight/locomotion/spot_v2/runner.py|892|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v4/__init__.py|dogfight_rl/src/dogfight/locomotion/spot_v4/__init__.py|382|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v4/cli.py|dogfight_rl/src/dogfight/locomotion/spot_v4/cli.py|1353|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v4/config.py|dogfight_rl/src/dogfight/locomotion/spot_v4/config.py|1047|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v4/contracts.py|dogfight_rl/src/dogfight/locomotion/spot_v4/contracts.py|1914|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v4/diagnostic_ik.py|dogfight_rl/src/dogfight/locomotion/spot_v4/diagnostic_ik.py|2263|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v4/evaluation.py|dogfight_rl/src/dogfight/locomotion/spot_v4/evaluation.py|5193|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v4/gait.py|dogfight_rl/src/dogfight/locomotion/spot_v4/gait.py|658|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v4/rewards.py|dogfight_rl/src/dogfight/locomotion/spot_v4/rewards.py|2019|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v4/runner.py|dogfight_rl/src/dogfight/locomotion/spot_v4/runner.py|3878|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v4/runtime.py|dogfight_rl/src/dogfight/locomotion/spot_v4/runtime.py|4482|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v5/__init__.py|dogfight_rl/src/dogfight/locomotion/spot_v5/__init__.py|76|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v5/audit.py|dogfight_rl/src/dogfight/locomotion/spot_v5/audit.py|3353|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v5/config.py|dogfight_rl/src/dogfight/locomotion/spot_v5/config.py|4582|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v5/evaluation.py|dogfight_rl/src/dogfight/locomotion/spot_v5/evaluation.py|4964|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/spot_v5/telemetry.py|dogfight_rl/src/dogfight/locomotion/spot_v5/telemetry.py|5750|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/robots/__init__.py|dogfight_rl/src/dogfight/robots/__init__.py|48|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/robots/csdog_12dof.py|dogfight_rl/src/dogfight/robots/csdog_12dof.py|509|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/__init__.py|dogfight_rl/src/dogfight/teleop/__init__.py|66|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/agent.py|dogfight_rl/src/dogfight/teleop/agent.py|1592|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/combat.py|dogfight_rl/src/dogfight/teleop/combat.py|3555|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/config.py|dogfight_rl/src/dogfight/teleop/config.py|4999|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/first_person.py|dogfight_rl/src/dogfight/teleop/first_person.py|9340|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/hud.py|dogfight_rl/src/dogfight/teleop/hud.py|1285|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/keyboard.py|dogfight_rl/src/dogfight/teleop/keyboard.py|9496|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/laser.py|dogfight_rl/src/dogfight/teleop/laser.py|3451|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/maps.py|dogfight_rl/src/dogfight/teleop/maps.py|2422|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/multi_hud.py|dogfight_rl/src/dogfight/teleop/multi_hud.py|2001|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/multi_runtime.py|dogfight_rl/src/dogfight/teleop/multi_runtime.py|17671|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/policy.py|dogfight_rl/src/dogfight/teleop/policy.py|4110|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/runtime.py|dogfight_rl/src/dogfight/teleop/runtime.py|11988|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/training/__init__.py|dogfight_rl/src/dogfight/training/__init__.py|50|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/training/action_audit_wrapper.py|dogfight_rl/src/dogfight/training/action_audit_wrapper.py|1131|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/training/checkpoints.py|dogfight_rl/src/dogfight/training/checkpoints.py|1753|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/training/deployment.py|dogfight_rl/src/dogfight/training/deployment.py|1688|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/training/ppo.py|dogfight_rl/src/dogfight/training/ppo.py|2292|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/training/reward_terms.py|dogfight_rl/src/dogfight/training/reward_terms.py|5193|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/training/telemetry.py|dogfight_rl/src/dogfight/training/telemetry.py|626|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/__init__.py|dogfight_rl/src/dogfight_v0/__init__.py|214|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/__init__.py|dogfight_rl/src/dogfight_v0/agents/__init__.py|425|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/agent_interface.py|dogfight_rl/src/dogfight_v0/agents/agent_interface.py|756|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/locomotion_interface.py|dogfight_rl/src/dogfight_v0/agents/locomotion_interface.py|367|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/proxy_agent.py|dogfight_rl/src/dogfight_v0/agents/proxy_agent.py|3149|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/real_dog_agent.py|dogfight_rl/src/dogfight_v0/agents/real_dog_agent.py|5216|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/real_locomotion_adapter.py|dogfight_rl/src/dogfight_v0/agents/real_locomotion_adapter.py|2055|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/arena/__init__.py|dogfight_rl/src/dogfight_v0/arena/__init__.py|236|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/arena/map_interface.py|dogfight_rl/src/dogfight_v0/arena/map_interface.py|468|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/arena/spawn_manager.py|dogfight_rl/src/dogfight_v0/arena/spawn_manager.py|1507|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/arena/test_map.py|dogfight_rl/src/dogfight_v0/arena/test_map.py|1906|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/__init__.py|dogfight_rl/src/dogfight_v0/battle/__init__.py|22|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/battle_manager.py|dogfight_rl/src/dogfight_v0/battle/battle_manager.py|11416|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/health_system.py|dogfight_rl/src/dogfight_v0/battle/health_system.py|965|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/intel_service.py|dogfight_rl/src/dogfight_v0/battle/intel_service.py|1732|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/interfaces.py|dogfight_rl/src/dogfight_v0/battle/interfaces.py|2105|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/ray_query.py|dogfight_rl/src/dogfight_v0/battle/ray_query.py|3466|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/scripted_policy.py|dogfight_rl/src/dogfight_v0/battle/scripted_policy.py|1886|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/types.py|dogfight_rl/src/dogfight_v0/battle/types.py|2036|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/visibility_service.py|dogfight_rl/src/dogfight_v0/battle/visibility_service.py|2135|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/weapon_service.py|dogfight_rl/src/dogfight_v0/battle/weapon_service.py|1752|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/config/__init__.py|dogfight_rl/src/dogfight_v0/config/__init__.py|66|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/config/battle_cfg.py|dogfight_rl/src/dogfight_v0/config/battle_cfg.py|1305|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/logging/__init__.py|dogfight_rl/src/dogfight_v0/logging/__init__.py|69|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/logging/battle_logger.py|dogfight_rl/src/dogfight_v0/logging/battle_logger.py|1531|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/navigation/__init__.py|dogfight_rl/src/dogfight_v0/navigation/__init__.py|158|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/navigation/navigation_interface.py|dogfight_rl/src/dogfight_v0/navigation/navigation_interface.py|553|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/navigation/simple_navigation.py|dogfight_rl/src/dogfight_v0/navigation/simple_navigation.py|2470|.py|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/runtime.py|dogfight_rl/src/dogfight_v0/runtime.py|2421|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/sim/__init__.py|dogfight_rl/src/dogfight_v0/sim/__init__.py|69|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/sim/physx_ray_query.py|dogfight_rl/src/dogfight_v0/sim/physx_ray_query.py|703|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/sim/scene.py|dogfight_rl/src/dogfight_v0/sim/scene.py|2683|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/ui/__init__.py|dogfight_rl/src/dogfight_v0/ui/__init__.py|220|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/ui/battle_hud.py|dogfight_rl/src/dogfight_v0/ui/battle_hud.py|6435|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/conftest.py|dogfight_rl/tests/conftest.py|1444|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_autoppo_gait.py|dogfight_rl/tests/test_autoppo_gait.py|3860|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_autoppo_system.py|dogfight_rl/tests/test_autoppo_system.py|13241|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_curriculum_v6.py|dogfight_rl/tests/test_curriculum_v6.py|5484|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_curriculum_v6_1.py|dogfight_rl/tests/test_curriculum_v6_1.py|8469|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_curriculum_v6_3.py|dogfight_rl/tests/test_curriculum_v6_3.py|3733|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_first_person.py|dogfight_rl/tests/test_first_person.py|1044|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_fsm_battle.py|dogfight_rl/tests/test_fsm_battle.py|8106|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_hud.py|dogfight_rl/tests/test_hud.py|1605|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_intel_5s.py|dogfight_rl/tests/test_intel_5s.py|1367|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_locomotion_task.py|dogfight_rl/tests/test_locomotion_task.py|1914|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_navigation.py|dogfight_rl/tests/test_navigation.py|979|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_phase_guided_v7.py|dogfight_rl/tests/test_phase_guided_v7.py|3692|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_phase_v7_manager.py|dogfight_rl/tests/test_phase_v7_manager.py|1969|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_phase_v7_search.py|dogfight_rl/tests/test_phase_v7_search.py|2368|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_phase_v7_trace.py|dogfight_rl/tests/test_phase_v7_trace.py|1547|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_portable_resources.py|dogfight_rl/tests/test_portable_resources.py|1700|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_project_paths.py|dogfight_rl/tests/test_project_paths.py|2495|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_real_adapters.py|dogfight_rl/tests/test_real_adapters.py|1246|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_robot_boundary.py|dogfight_rl/tests/test_robot_boundary.py|2062|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_round.py|dogfight_rl/tests/test_round.py|1398|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_spawn.py|dogfight_rl/tests/test_spawn.py|896|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_spot_aligned_budget.py|dogfight_rl/tests/test_spot_aligned_budget.py|1256|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_spot_v2_budget.py|dogfight_rl/tests/test_spot_v2_budget.py|1095|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_spot_v4.py|dogfight_rl/tests/test_spot_v4.py|4520|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_spot_v5_tuning.py|dogfight_rl/tests/test_spot_v5_tuning.py|1599|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_teleop_v02.py|dogfight_rl/tests/test_teleop_v02.py|6841|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_three_dog_teleop.py|dogfight_rl/tests/test_three_dog_teleop.py|3150|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_training_tools.py|dogfight_rl/tests/test_training_tools.py|2215|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_visibility.py|dogfight_rl/tests/test_visibility.py|1294|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/dogfight_rl/tests/test_weapon.py|dogfight_rl/tests/test_weapon.py|1732|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/model/meshes/base_collision.stl|model/meshes/base_collision.stl|1484|.stl|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/meshes/link_lf_hip_pitch_collision.stl|model/meshes/link_lf_hip_pitch_collision.stl|190484|.stl|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/meshes/link_lf_hip_roll_collision.stl|model/meshes/link_lf_hip_roll_collision.stl|236484|.stl|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/meshes/link_lf_knee_collision.stl|model/meshes/link_lf_knee_collision.stl|53684|.stl|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/meshes/link_lr_hip_pitch_collision.stl|model/meshes/link_lr_hip_pitch_collision.stl|190634|.stl|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/meshes/link_lr_hip_roll_collision.stl|model/meshes/link_lr_hip_roll_collision.stl|236984|.stl|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/meshes/link_lr_knee_collision.stl|model/meshes/link_lr_knee_collision.stl|53734|.stl|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/meshes/link_rf_hip_pitch_collision.stl|model/meshes/link_rf_hip_pitch_collision.stl|197184|.stl|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/meshes/link_rf_hip_roll_collision.stl|model/meshes/link_rf_hip_roll_collision.stl|236234|.stl|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/meshes/link_rf_knee_collision.stl|model/meshes/link_rf_knee_collision.stl|53634|.stl|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/meshes/link_rr_hip_pitch_collision.stl|model/meshes/link_rr_hip_pitch_collision.stl|190784|.stl|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/meshes/link_rr_hip_roll_collision.stl|model/meshes/link_rr_hip_roll_collision.stl|237534|.stl|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/meshes/link_rr_knee_collision.stl|model/meshes/link_rr_knee_collision.stl|53984|.stl|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/package.xml|model/package.xml|269|.xml|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/robot.preview.urdf|model/robot.preview.urdf|13051|.urdf|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/model/robot.urdf|model/robot.urdf|12505|.urdf|设计/后续训练|否（推荐保留）|推荐上传|普通 Git|原始设计权威资产，当前teleop不读取此目录|
|/home/zxq/robot_projects/reorganization/20261026/baseline_isolated_pytest.log|reorganization/20261026/baseline_isolated_pytest.log|99|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|reorganization/20261026/baseline_pytest.log|5559|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/build_indexes.py|reorganization/20261026/build_indexes.py|5227|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/changes.json|reorganization/20261026/changes.json|21085|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/check_static.py|reorganization/20261026/check_static.py|2191|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/checkpoint_index.json|reorganization/20261026/checkpoint_index.json|601997|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/created.json|reorganization/20261026/created.json|1447|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/current_files.json|reorganization/20261026/current_files.json|15491|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/deduplication_candidates.json|reorganization/20261026/deduplication_candidates.json|822813|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/environment_check.log|reorganization/20261026/environment_check.log|500|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/file_mapping.csv|reorganization/20261026/file_mapping.csv|1006652|.csv|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/final_pytest.log|reorganization/20261026/final_pytest.log|368|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|reorganization/20261026/git_diff_before.patch|208117|.patch|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_stat_after.txt|reorganization/20261026/git_diff_stat_after.txt|14960|.txt|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/git_status_after.txt|reorganization/20261026/git_status_after.txt|13455|.txt|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/git_status_before.txt|reorganization/20261026/git_status_before.txt|28602|.txt|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/index_summary.json|reorganization/20261026/index_summary.json|167|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/initial_command_outputs/20261026/git_diff_before.patch|reorganization/20261026/initial_command_outputs/20261026/git_diff_before.patch|0|.patch|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/initial_command_outputs/20261026/git_status_before.txt|reorganization/20261026/initial_command_outputs/20261026/git_status_before.txt|0|.txt|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/initial_command_outputs/20261026/isaaclab_status_before.txt|reorganization/20261026/initial_command_outputs/20261026/isaaclab_status_before.txt|0|.txt|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/integrity_final.json|reorganization/20261026/integrity_final.json|567|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/integrity_initial.json|reorganization/20261026/integrity_initial.json|567|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/isaac_battle_smoke.log|reorganization/20261026/isaac_battle_smoke.log|4768|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/isaaclab_status_before.txt|reorganization/20261026/isaaclab_status_before.txt|0|.txt|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/legacy_mock_pytest.log|reorganization/20261026/legacy_mock_pytest.log|406|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/manifest.json|reorganization/20261026/manifest.json|1587299|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/move_verification.json|reorganization/20261026/move_verification.json|40|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/moves_done.json|reorganization/20261026/moves_done.json|27033|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/operations.py|reorganization/20261026/operations.py|1934|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/AGENTS.md|reorganization/20261026/originals/AGENTS.md|6159|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/DOGFIGHT_ENVIRONMENT.md|reorganization/20261026/originals/DOGFIGHT_ENVIRONMENT.md|7713|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/REORGANIZATION_MANIFEST.md|reorganization/20261026/originals/REORGANIZATION_MANIFEST.md|16439|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/archive/legacy_dog_a/diagnostics/test_dog_a_interface.py|reorganization/20261026/originals/archive/legacy_dog_a/diagnostics/test_dog_a_interface.py|7865|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/archive/legacy_dog_a/training_code/battle_adapters/dog_a_factory.py|reorganization/20261026/originals/archive/legacy_dog_a/training_code/battle_adapters/dog_a_factory.py|2665|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/archive/legacy_dog_a/training_code/battle_adapters/dog_a_locomotion_adapter.py|reorganization/20261026/originals/archive/legacy_dog_a/training_code/battle_adapters/dog_a_locomotion_adapter.py|7394|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/archive/legacy_dog_a/training_code/battle_adapters/real_dog_agent.py|reorganization/20261026/originals/archive/legacy_dog_a/training_code/battle_adapters/real_dog_agent.py|5248|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/archive/legacy_dog_a/training_code/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/train.py|reorganization/20261026/originals/archive/legacy_dog_a/training_code/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/train.py|18491|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/archive/legacy_dog_a/training_code/dogfight/tests/back_gait_reward_sanity.py|reorganization/20261026/originals/archive/legacy_dog_a/training_code/dogfight/tests/back_gait_reward_sanity.py|1935|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/archive/legacy_dog_a/training_code/dogfight/tests/dog_a_x_reward_sanity.py|reorganization/20261026/originals/archive/legacy_dog_a/training_code/dogfight/tests/dog_a_x_reward_sanity.py|10661|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/.gitignore|reorganization/20261026/originals/dogfight_rl/.gitignore|403|无扩展|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/AGENTS.md|reorganization/20261026/originals/dogfight_rl/AGENTS.md|4333|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/README.md|reorganization/20261026/originals/dogfight_rl/README.md|1357|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/configs/battle/extension.toml|reorganization/20261026/originals/dogfight_rl/configs/battle/extension.toml|404|.toml|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/docs/BATTLE_PACKAGE.md|reorganization/20261026/originals/dogfight_rl/docs/BATTLE_PACKAGE.md|173|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/launch.py|reorganization/20261026/originals/dogfight_rl/launch.py|5064|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/pyproject.toml|reorganization/20261026/originals/dogfight_rl/pyproject.toml|154|.toml|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/scripts/battle/run_v02_hud_smoke_tests.py|reorganization/20261026/originals/dogfight_rl/scripts/battle/run_v02_hud_smoke_tests.py|4921|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/scripts/battle/run_v0_battle_demo.py|reorganization/20261026/originals/dogfight_rl/scripts/battle/run_v0_battle_demo.py|8955|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/scripts/battle/run_v0_gui.py|reorganization/20261026/originals/dogfight_rl/scripts/battle/run_v0_gui.py|2433|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/scripts/battle/run_v0_headless.py|reorganization/20261026/originals/dogfight_rl/scripts/battle/run_v0_headless.py|2172|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/scripts/battle/run_v0_smoke_tests.py|reorganization/20261026/originals/dogfight_rl/scripts/battle/run_v0_smoke_tests.py|10080|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/scripts/diagnostics/check_environment.py|reorganization/20261026/originals/dogfight_rl/scripts/diagnostics/check_environment.py|3812|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/scripts/diagnostics/check_environment.sh|reorganization/20261026/originals/dogfight_rl/scripts/diagnostics/check_environment.sh|751|.sh|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/setup.py|reorganization/20261026/originals/dogfight_rl/setup.py|702|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight/common/paths.py|reorganization/20261026/originals/dogfight_rl/src/dogfight/common/paths.py|1428|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight/training/action_audit_wrapper.py|reorganization/20261026/originals/dogfight_rl/src/dogfight/training/action_audit_wrapper.py|1560|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight/training/reward_terms.py|reorganization/20261026/originals/dogfight_rl/src/dogfight/training/reward_terms.py|5602|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/agents/__init__.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/agents/__init__.py|514|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/agents/agent_interface.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/agents/agent_interface.py|1185|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/agents/locomotion_interface.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/agents/locomotion_interface.py|796|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/agents/proxy_agent.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/agents/proxy_agent.py|3578|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/agents/real_locomotion_adapter.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/agents/real_locomotion_adapter.py|2484|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/arena/map_interface.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/arena/map_interface.py|897|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/arena/spawn_manager.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/arena/spawn_manager.py|1936|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/arena/test_map.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/arena/test_map.py|2335|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/battle_manager.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/battle_manager.py|11845|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/health_system.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/health_system.py|1394|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/intel_service.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/intel_service.py|2161|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/interfaces.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/interfaces.py|2534|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/ray_query.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/ray_query.py|3895|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/scripted_policy.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/scripted_policy.py|2315|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/types.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/types.py|2465|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/visibility_service.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/visibility_service.py|2564|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/weapon_service.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/battle/weapon_service.py|2181|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/config/battle_cfg.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/config/battle_cfg.py|1809|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/logging/battle_logger.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/logging/battle_logger.py|1879|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/navigation/navigation_interface.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/navigation/navigation_interface.py|982|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/navigation/simple_navigation.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/navigation/simple_navigation.py|2899|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/runtime.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/runtime.py|2850|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/sim/physx_ray_query.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/sim/physx_ray_query.py|1132|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/sim/scene.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/sim/scene.py|3112|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/ui/battle_hud.py|reorganization/20261026/originals/dogfight_rl/src/dogfight_v0/ui/battle_hud.py|6864|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/tests/conftest.py|reorganization/20261026/originals/dogfight_rl/tests/conftest.py|1562|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/tests/test_hud.py|reorganization/20261026/originals/dogfight_rl/tests/test_hud.py|1703|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/tests/test_intel_5s.py|reorganization/20261026/originals/dogfight_rl/tests/test_intel_5s.py|1465|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/tests/test_navigation.py|reorganization/20261026/originals/dogfight_rl/tests/test_navigation.py|1077|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/tests/test_portable_resources.py|reorganization/20261026/originals/dogfight_rl/tests/test_portable_resources.py|1270|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/tests/test_project_paths.py|reorganization/20261026/originals/dogfight_rl/tests/test_project_paths.py|1955|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/tests/test_real_adapters.py|reorganization/20261026/originals/dogfight_rl/tests/test_real_adapters.py|1344|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/tests/test_round.py|reorganization/20261026/originals/dogfight_rl/tests/test_round.py|1496|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/tests/test_spawn.py|reorganization/20261026/originals/dogfight_rl/tests/test_spawn.py|994|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/tests/test_visibility.py|reorganization/20261026/originals/dogfight_rl/tests/test_visibility.py|1392|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/tests/test_weapon.py|reorganization/20261026/originals/dogfight_rl/tests/test_weapon.py|1830|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/post_move_pytest_initial.log|reorganization/20261026/post_move_pytest_initial.log|5313|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/post_refactor_pytest.log|reorganization/20261026/post_refactor_pytest.log|368|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/rollback.py|reorganization/20261026/rollback.py|2912|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/rollback_preview.json|reorganization/20261026/rollback_preview.json|119|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/seal_current.py|reorganization/20261026/seal_current.py|1099|.py|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/stage_note.txt|reorganization/20261026/stage_note.txt|210|.txt|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/static_validation.json|reorganization/20261026/static_validation.json|147|.json|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/static_validation_output.log|reorganization/20261026/static_validation_output.log|147|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|reorganization/20261026/training_runtime_validation.log|15522|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|reorganization/20261026/training_runtime_validation_final.log|16114|.log|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/robot_projects/格式规范.md|格式规范.md|23045|.md|独立工具/文档|否（推荐保留）|推荐上传|普通 Git|开发/历史溯源/测试恢复；不证明运行已通过|
|/home/zxq/桌面/三狗自主对战.desktop|项目外桌面模板|500|.desktop|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|
|/home/zxq/桌面/机器狗对战环境.desktop|项目外桌面模板|480|.desktop|桌面teleop/FSM/单狗条件入口|是|必须上传|普通 Git|运行闭包（直接调用方详见依赖报告）|

## 必须单独备份/不上传规则

单独备份：archive（旧Dog A原模型、checkpoint、旧代码和迁移tar）、peer_csdog_review（来源完整包和比对证据）、本地.git（全部历史分支/未提交文件须另快照，未来可做bundle但bundle不含未提交内容）、其余assets历史转换候选与runs训练/验证日志、奖励trace与训练权重。Release仅在审查隐私/授权后发布必要精简资产或证据，不把37GB直接推Git/LFS。Conda/Isaac Sim安装、NVIDIA官方资产离线包需独立外部介质备份。

不上传：__pycache__、pyc、pytest临时目录/软链接、lock、运行缓存；IsaacLab整份SDK源码/outputs/logs使用固定上游提交恢复；blackhorse_lightstick、course_presentation是其他交付，不在桌面运行链，需按各自任务备份；不会认定为废弃可删。历史兼容树/迁移备份停用但保留，不能以名称猜测其可删除。

## 大文件与Git LFS

当前必需权重仅2,722,815字节，所有必须上传文件均远小于100MiB，普通Git可满足此静态快照，LFS不是必要条件。经常更换模型时才建议在新分支为指定权重/STL/USD采用LFS；不要对全部*.pt无差别追踪。Release适合独立版本压缩包/精简截图证据；不适合缺少下载校验脚本的隐式运行依赖。GitHub大小规则来源：[large files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)。本地超过50MiB有 369 项，均不在当前必须上传集合。

|字节|绝对路径|类别|
|---|---|---|
|757419982|/home/zxq/robot_projects/archive/migration_backups/previous_migration/backups/pre_migration.tar.gz|必须单独备份|
|76591409|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_v6_2_diagnostics/experiment_2_regression/data/B_200/reward_trace.npz|必须单独备份|
|76552638|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_v6_2_diagnostics/experiment_2_regression/data/B_100/reward_trace.npz|必须单独备份|
|76340271|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_v6_2_diagnostics/experiment_2_regression/data/B_300/reward_trace.npz|必须单独备份|
|76322637|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_v6_2_diagnostics/experiment_2_regression/data/initial/reward_trace.npz|必须单独备份|
|76249232|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_v6_2_diagnostics/experiment_2_regression/data/A_400/reward_trace.npz|必须单独备份|
|76183834|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_v6_2_diagnostics/experiment_2_regression/data/A_200/reward_trace.npz|必须单独备份|
|76177423|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_v6_2_diagnostics/experiment_2_regression/data/A_500/reward_trace.npz|必须单独备份|
|76158996|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_v6_2_diagnostics/experiment_2_regression/data/B_400/reward_trace.npz|必须单独备份|
|76128333|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_v6_2_diagnostics/experiment_2_regression/data/A_300/reward_trace.npz|必须单独备份|
|76097263|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_v6_2_diagnostics/experiment_2_regression/data/A_100/reward_trace.npz|必须单独备份|
|76093141|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_v6_2_diagnostics/experiment_2_regression/data/B_500/reward_trace.npz|必须单独备份|
|75465272|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_autoppo_lab/physical_audit_01/v6_2500/evaluation_common_seed911.npz|必须单独备份|
|75462218|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_autoppo_lab/physical_audit_final/v6_2500/evaluation_common_seed103.npz|必须单独备份|
|75459473|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_autoppo_lab/physical_audit_01/v6_2500/evaluation_common_seed103.npz|必须单独备份|
|75457267|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_autoppo_lab/physical_audit_final/v6_2500/evaluation_common_seed307.npz|必须单独备份|
|75456205|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_autoppo_lab/physical_audit_01/v6_2500/evaluation_common_seed1301.npz|必须单独备份|
|75454777|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_autoppo_lab/physical_audit_01/v6_2500/evaluation_common_seed307.npz|必须单独备份|
|75220715|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_autoppo_lab/trials/trial_8aead410766b/attempt_d73004a46af5/eval_00000250/evaluation_common_seed1301.npz|必须单独备份|
|75208796|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_autoppo_lab/trials/trial_8aead410766b/attempt_d73004a46af5/eval_00000250/evaluation_common_seed911.npz|必须单独备份|
|75208609|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_autoppo_lab/trials/trial_8aead410766b/attempt_d73004a46af5/eval_00000250/evaluation_common_seed103.npz|必须单独备份|
|75206236|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_autoppo_lab/trials/trial_8aead410766b/attempt_d73004a46af5/eval_00000250/evaluation_common_seed307.npz|必须单独备份|
|75192772|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_curriculum_ppo_v6_3/smoke_B_verified2/eval_000002/evaluation_common_seed103.npz|必须单独备份|
|75184868|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_curriculum_ppo_v6_3/history/v6_2500/evaluation_common_seed911.npz|必须单独备份|
|75184868|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_curriculum_ppo_v6_3/ab_B/eval_000000/evaluation_common_seed911.npz|必须单独备份|
|75184868|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_curriculum_ppo_v6_3/ab_A_verified2/eval_000000/evaluation_common_seed911.npz|必须单独备份|
|75184868|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_curriculum_ppo_v6_3/ab_A_verified/eval_000000/evaluation_common_seed911.npz|必须单独备份|
|75175291|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_curriculum_ppo_v6_3/history_preflight/v6_2500/evaluation_common_seed103.npz|必须单独备份|
|75175036|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_curriculum_ppo_v6_3/history/v6_2500/evaluation_common_seed103.npz|必须单独备份|
|75174820|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_curriculum_ppo_v6_3/smoke_B_verified/eval_000000/evaluation_common_seed103.npz|必须单独备份|

## .gitignore阻塞

现有ignore排除了 *.pt/*.pth/*.onnx、runs/，没有.gitattributes。实际check-ignore：
```text
.gitignore:12:*.pt	/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/policies/v1/model_final.pt
```
未来只在独立发布副本中增加 `!assets/csdog_12dof/peer_teleop_v1/policies/v1/model_final.pt`（路径按副本布局调整），并显式选择证据；若用LFS，在新分支先提交.gitattributes再追踪指定路径。不要改当前工作树、不要全局取消runs或所有权重忽略。GitHub不会自动包含被ignore的权重。

## 密钥/隐私/绝对路径/授权

仅对必须/推荐上传文本（≤4MiB）扫描私钥头、GitHub token、AWS访问ID和带字面值的凭据赋值，候选结果如下。二进制和历史.git对象/全部训练日志未逐内容扫描，不能承诺全仓无密钥；未来发布前应对独立候选快照和保留历史运行完整secret scanner。未读取无关个人目录、未输出候选凭据值。

扫描范围内未命中上述高信号凭据规则。

绝对路径/用户信息文本命中位置（只列文件与行，提交前按语义区分模板、溯源证据和运行代码；不要全局替换模型或manifest字节）：

|绝对路径|行|
|---|---|
|/home/zxq/robot_projects/AGENTS.md|3|
|/home/zxq/robot_projects/AGENTS.md|13|
|/home/zxq/robot_projects/PROJECT_STRUCTURE.md|66|
|/home/zxq/robot_projects/PROJECT_STRUCTURE.md|67|
|/home/zxq/robot_projects/PROJECT_STRUCTURE.md|68|
|/home/zxq/robot_projects/PROJECT_STRUCTURE.md|69|
|/home/zxq/robot_projects/PROJECT_STRUCTURE.md|70|
|/home/zxq/robot_projects/PROJECT_STRUCTURE.md|71|
|/home/zxq/robot_projects/PROJECT_STRUCTURE.md|72|
|/home/zxq/robot_projects/PROJECT_STRUCTURE.md|73|
|/home/zxq/robot_projects/PROJECT_STRUCTURE.md|74|
|/home/zxq/robot_projects/PROJECT_STRUCTURE.md|75|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|3|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|96|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|97|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|98|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|99|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|100|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|101|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|102|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|103|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|104|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|112|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|113|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|114|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|115|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|116|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|117|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|118|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|119|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|120|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|121|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|122|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|123|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|124|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|125|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|266|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|346|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|347|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|348|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|349|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|350|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|351|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|352|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|353|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|354|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|355|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|356|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|357|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|358|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|359|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|360|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|361|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|362|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|363|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|364|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|365|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|366|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|367|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|368|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|369|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|370|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|371|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|372|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|373|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|374|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|375|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|376|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|377|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|378|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|379|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|380|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|381|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|382|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|383|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|384|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|385|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|386|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|387|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|388|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|389|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|390|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|391|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|392|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|398|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|413|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|420|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|421|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|422|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|424|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|425|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|426|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|949|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|953|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|954|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|955|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|956|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|957|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|958|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|959|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|960|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|961|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|962|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|963|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|964|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|965|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|966|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|967|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|968|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|969|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|970|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|971|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|972|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|973|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|974|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|975|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|976|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|977|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|978|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|979|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|980|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|981|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|982|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|983|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|984|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|985|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|986|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|987|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|988|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|989|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|990|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|991|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|992|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|993|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|994|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|995|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|996|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|997|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|998|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|999|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|1000|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|1001|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|1002|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|1003|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|1004|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|1005|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|1006|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|1007|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|1008|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|1009|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|1010|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|1011|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|1012|
|/home/zxq/robot_projects/PROJECT_STRUCTURE_AUDIT.md|1013|
|/home/zxq/robot_projects/REORGANIZATION_REPORT.md|3|
|/home/zxq/robot_projects/audits/progress_audit_20261103/BATTLE_SYSTEM_AUDIT.md|11|
|/home/zxq/robot_projects/audits/progress_audit_20261103/BATTLE_SYSTEM_AUDIT.md|13|
|/home/zxq/robot_projects/audits/progress_audit_20261103/BATTLE_SYSTEM_AUDIT.md|15|
|/home/zxq/robot_projects/audits/progress_audit_20261103/BATTLE_SYSTEM_AUDIT.md|34|
|/home/zxq/robot_projects/audits/progress_audit_20261103/BATTLE_SYSTEM_AUDIT.md|45|
|/home/zxq/robot_projects/audits/progress_audit_20261103/BATTLE_SYSTEM_AUDIT.md|61|
|/home/zxq/robot_projects/audits/progress_audit_20261103/BATTLE_SYSTEM_AUDIT.md|70|
|/home/zxq/robot_projects/audits/progress_audit_20261103/BLOCKERS_AND_ROADMAP.md|17|
|/home/zxq/robot_projects/audits/progress_audit_20261103/FINAL_SUMMARY.md|14|
|/home/zxq/robot_projects/audits/progress_audit_20261103/MAP_AUDIT.md|16|
|/home/zxq/robot_projects/audits/progress_audit_20261103/MAP_AUDIT.md|20|
|/home/zxq/robot_projects/audits/progress_audit_20261103/MAP_AUDIT.md|22|
|/home/zxq/robot_projects/audits/progress_audit_20261103/MODEL_AND_RL_AUDIT.md|21|
|/home/zxq/robot_projects/audits/progress_audit_20261103/MODEL_AND_RL_AUDIT.md|46|
|/home/zxq/robot_projects/audits/progress_audit_20261103/MODEL_AND_RL_AUDIT.md|62|
|/home/zxq/robot_projects/audits/progress_audit_20261103/MODEL_AND_RL_AUDIT.md|82|
|/home/zxq/robot_projects/audits/progress_audit_20261103/MODEL_AND_RL_AUDIT.md|86|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|7|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|8|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|9|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|10|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|11|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|12|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|13|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|14|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|15|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|16|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|17|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|18|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|19|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|20|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|21|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|22|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|23|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|24|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|25|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|26|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|27|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|28|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|29|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|30|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|31|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|32|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|33|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|34|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|35|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|36|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|37|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|38|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|39|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|40|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|41|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|42|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|43|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|44|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|45|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|46|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|47|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|48|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|49|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|50|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|51|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROGRESS_MATRIX.md|52|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROJECT_OVERVIEW.md|7|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROJECT_OVERVIEW.md|9|
|/home/zxq/robot_projects/audits/progress_audit_20261103/PROJECT_OVERVIEW.md|62|
|/home/zxq/robot_projects/audits/progress_audit_20261103/README.md|33|
|/home/zxq/robot_projects/audits/progress_audit_20261103/REFEREE_AUDIT.md|7|
|/home/zxq/robot_projects/audits/progress_audit_20261103/REFEREE_AUDIT.md|9|
|/home/zxq/robot_projects/audits/progress_audit_20261103/REFEREE_AUDIT.md|25|
|/home/zxq/robot_projects/audits/progress_audit_20261103/REFEREE_AUDIT.md|27|
|/home/zxq/robot_projects/audits/progress_audit_20261103/REFEREE_AUDIT.md|29|
|/home/zxq/robot_projects/audits/progress_audit_20261103/REFEREE_AUDIT.md|41|
|/home/zxq/robot_projects/audits/progress_audit_20261103/REFEREE_AUDIT.md|43|
|/home/zxq/robot_projects/audits/progress_audit_20261103/REFEREE_AUDIT.md|49|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|7|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|8|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|9|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|10|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|11|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|12|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|13|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|14|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|18|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|22|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|23|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|24|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|28|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|29|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|30|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|31|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|35|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|36|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|37|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|38|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|39|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|40|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|41|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|42|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|43|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|44|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|45|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|46|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|47|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|48|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|49|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|50|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|51|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|55|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|56|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|57|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|58|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|62|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|63|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|64|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|65|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|66|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|67|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|68|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|69|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|73|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|74|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|75|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|76|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|77|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|78|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|79|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|80|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|81|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|82|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|83|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|87|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|88|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|89|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|90|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|91|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|92|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|93|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|97|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|101|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|102|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|103|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|107|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|108|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|112|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|113|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|117|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|118|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|119|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|120|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|121|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|122|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|123|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|127|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|128|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|129|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|130|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|131|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|135|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|136|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|137|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|138|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|139|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|140|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|141|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|142|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|143|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|144|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|145|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|146|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|147|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|151|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|152|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|153|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|154|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|155|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|156|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|157|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|158|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|159|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|160|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|164|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|165|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|166|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|167|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|168|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|169|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|173|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|174|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|175|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|179|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|180|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|181|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|182|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|183|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|184|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|188|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|189|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|190|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|191|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|192|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|193|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|194|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|195|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|199|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|200|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|201|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|202|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|203|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|204|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|205|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|209|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|210|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|211|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|215|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|216|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|217|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|218|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|219|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|220|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|221|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|225|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|226|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|227|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|228|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|229|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|230|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|231|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|232|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|233|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|234|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|235|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|236|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|240|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|241|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|242|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|243|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|244|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|245|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|246|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|247|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|248|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|249|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|250|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|251|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|252|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|256|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|260|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|261|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|262|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|263|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|264|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|265|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|269|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|270|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|271|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|272|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|273|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|274|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|275|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|276|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|277|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|281|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|282|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|286|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|287|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|288|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|289|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|293|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|294|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|295|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|296|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|297|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|298|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|299|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|303|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|304|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|305|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|306|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|307|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|308|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|309|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|310|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|311|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|312|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|313|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|314|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|315|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|316|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|317|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|321|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|322|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|326|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|327|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|328|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|329|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|330|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|331|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|332|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|333|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|334|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|335|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|336|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|340|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|341|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|342|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|346|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|347|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|348|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|349|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|350|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|351|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|352|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|356|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|357|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|358|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|359|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|360|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|361|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|362|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|363|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|364|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|365|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|366|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|367|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|371|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|372|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|373|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|374|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|375|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|376|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|377|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|378|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|379|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|380|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|381|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|382|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|383|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|384|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|388|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|389|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|390|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|391|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|392|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|393|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|394|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|395|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|396|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|397|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|398|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|399|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|400|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|404|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|405|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|406|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|407|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|408|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|409|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|410|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|411|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|415|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|416|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|417|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|421|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|422|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|426|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|427|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|428|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|429|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|430|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|431|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|432|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|433|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|434|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|435|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|439|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|440|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|444|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|448|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|449|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|450|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|451|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|452|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|453|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|454|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|455|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|456|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|457|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|458|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|459|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|460|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|461|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|465|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|466|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|467|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|471|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|472|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|473|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|474|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|475|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|479|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|483|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|484|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|485|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|486|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|487|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|488|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|489|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|493|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|494|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|495|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|496|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|497|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|498|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|502|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|503|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|504|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|505|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|506|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|507|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|511|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|512|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|513|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|514|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|515|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|516|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|517|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|518|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|522|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|523|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|524|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|525|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|526|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|530|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|531|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|532|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|533|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|534|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|535|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|539|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|543|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|544|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|545|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|546|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|547|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|551|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|552|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|553|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|554|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|555|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|556|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|557|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|558|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|559|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|563|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|564|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|568|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|569|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|573|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|574|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|575|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|576|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|580|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|581|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|582|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|583|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|587|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|588|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|589|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|590|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|591|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|595|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|596|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|597|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|598|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|602|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|603|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|607|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|608|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|609|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|610|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|611|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|615|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|616|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|617|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|618|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|619|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|620|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|621|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|622|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|623|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|627|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|628|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|632|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|636|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|637|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|638|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|639|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|640|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|641|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|642|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|643|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|644|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|645|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|649|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|650|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|651|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|652|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|653|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|657|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|658|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|659|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|660|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|661|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|662|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|663|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|664|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|665|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|666|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|667|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|671|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|675|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|676|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|677|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|681|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|682|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|683|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|687|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|691|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|692|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|696|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|697|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|698|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|699|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|700|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|701|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|702|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|703|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|704|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|708|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|709|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|710|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|711|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|712|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|716|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|717|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|718|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|719|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|720|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|721|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|722|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|723|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|724|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|725|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|726|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|727|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|731|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|732|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|733|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|734|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|735|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|739|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|740|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|741|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|742|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|743|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|744|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|745|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|746|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|747|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|748|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|749|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|750|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|751|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|752|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|753|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|757|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|758|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|759|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|760|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|761|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|762|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|763|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|764|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|765|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|766|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|767|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|768|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|769|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|770|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|774|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|775|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|776|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|777|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|778|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|779|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|780|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|781|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|782|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|783|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|784|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|785|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|789|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|790|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|791|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|792|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|793|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|794|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|795|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|799|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|800|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|801|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|802|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|803|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|804|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|805|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|809|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|810|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|811|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|812|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|813|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|814|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|815|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|816|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|817|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|818|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|822|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|823|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|824|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|825|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|826|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|827|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|828|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|829|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|830|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|831|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|832|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|833|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|834|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|835|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|836|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|837|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|841|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|842|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|843|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|844|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|845|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|846|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|847|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|851|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|852|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|853|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|854|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|855|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|856|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|860|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|861|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|862|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|863|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|864|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|865|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|866|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|867|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|868|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|869|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|870|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|871|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|872|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|873|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|874|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|875|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|876|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|877|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|878|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|879|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|880|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|881|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|882|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|883|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|884|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|885|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|886|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|887|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|888|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|892|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|893|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|894|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|895|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|896|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|897|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|898|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|899|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|903|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|904|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|905|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|906|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|907|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|911|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|912|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|913|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|914|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|915|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|916|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|917|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|918|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|919|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|920|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|921|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|922|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|926|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|927|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|928|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|929|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|933|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|934|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|935|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|936|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|937|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|941|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|942|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|946|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|947|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|948|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|952|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|953|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|954|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|955|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|956|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|957|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|961|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|962|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|963|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|964|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|965|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|966|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|967|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|968|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|969|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|970|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|974|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|978|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|979|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|980|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|984|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|985|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|986|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|987|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|988|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|989|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|993|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|994|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|995|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|996|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|997|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|998|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|999|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|1000|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|1001|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|1002|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|1003|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|1004|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|1005|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|1006|
|/home/zxq/robot_projects/audits/progress_audit_20261103/SOURCE_SYMBOL_INDEX.md|1007|
|/home/zxq/robot_projects/audits/progress_audit_20261103/audit_probes.py|5|
|/home/zxq/robot_projects/audits/progress_audit_20261103/write_audit_reports.py|3|
|/home/zxq/robot_projects/audits/progress_audit_20261103/write_audit_reports.py|617|
|/home/zxq/robot_projects/audits/progress_audit_20261103/write_audit_reports.py|647|
|/home/zxq/robot_projects/dogfight_rl/AGENTS.md|28|
|/home/zxq/robot_projects/dogfight_rl/AGENTS.md|38|
|/home/zxq/robot_projects/dogfight_rl/DOGFIGHT_THREE_DOG_DELIVERY.md|7|
|/home/zxq/robot_projects/dogfight_rl/DOGFIGHT_THREE_DOG_DELIVERY.md|8|
|/home/zxq/robot_projects/dogfight_rl/DOGFIGHT_THREE_DOG_DELIVERY.md|9|
|/home/zxq/robot_projects/dogfight_rl/DOGFIGHT_V0_2_DELIVERY.md|9|
|/home/zxq/robot_projects/dogfight_rl/DOGFIGHT_V0_2_DELIVERY.md|10|
|/home/zxq/robot_projects/dogfight_rl/DOGFIGHT_V0_2_DELIVERY.md|11|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/IMPORT_MANIFEST.json|2|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/IMPORT_MANIFEST.json|3|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/config.yaml|1|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/config.yaml|2|
|/home/zxq/robot_projects/dogfight_rl/configs/autoppo/csdog-autoppo-lab.service|4|
|/home/zxq/robot_projects/dogfight_rl/configs/autoppo/csdog-autoppo-lab.service|5|
|/home/zxq/robot_projects/dogfight_rl/configs/autoppo/csdog-autoppo-lab.service|11|
|/home/zxq/robot_projects/dogfight_rl/configs/autoppo/csdog-autoppo-lab.service|12|
|/home/zxq/robot_projects/dogfight_rl/configs/autoppo/csdog-autoppo-lab.service|18|
|/home/zxq/robot_projects/dogfight_rl/configs/locomotion/csdog_ppo/model_audit.json|2|
|/home/zxq/robot_projects/dogfight_rl/docs/DOGFIGHT_V0_INTERFACE_SPEC.md|6|
|/home/zxq/robot_projects/dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|3|
|/home/zxq/robot_projects/dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|7|
|/home/zxq/robot_projects/dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|32|
|/home/zxq/robot_projects/dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|86|
|/home/zxq/robot_projects/dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|87|
|/home/zxq/robot_projects/dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|89|
|/home/zxq/robot_projects/dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|90|
|/home/zxq/robot_projects/dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|98|
|/home/zxq/robot_projects/dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|99|
|/home/zxq/robot_projects/dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|103|
|/home/zxq/robot_projects/dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|104|
|/home/zxq/robot_projects/dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|105|
|/home/zxq/robot_projects/dogfight_rl/docs/FSM_BATTLE_V1_DELIVERY.md|114|
|/home/zxq/robot_projects/dogfight_rl/docs/TELEOP_POLICY_AUDIT.md|7|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/identity.json|10|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/identity.json|11|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/identity.json|45|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/identity.json|46|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/identity.json|80|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/identity.json|81|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/launch.json|3|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/launch.json|5|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/launch.json|9|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/launch.json|19|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/launch.json|20|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/launch.json|21|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/launch.json|119|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/launch.json|120|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/launch.json|121|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_143808_abd016cd/launch.json|122|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/identity.json|10|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/identity.json|11|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/identity.json|45|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/identity.json|46|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/identity.json|80|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/identity.json|81|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/launch.json|3|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/launch.json|5|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/launch.json|9|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/launch.json|19|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/launch.json|20|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/launch.json|21|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/launch.json|119|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/launch.json|120|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/launch.json|121|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163023_6e149374/launch.json|122|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/identity.json|10|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/identity.json|11|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/identity.json|45|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/identity.json|46|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/identity.json|80|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/identity.json|81|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/launch.json|3|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/launch.json|5|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/launch.json|12|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/launch.json|22|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/launch.json|23|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/launch.json|24|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/launch.json|122|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/launch.json|123|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/launch.json|124|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_163643_92147a7d/launch.json|125|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_gui_acceptance.json|2|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_gui_acceptance.json|4|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_gui_acceptance.json|5|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_gui_acceptance.json|6|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_gui_acceptance.json|7|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_gui_acceptance.json|8|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/fsm_gui_acceptance.json|9|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/identity.json|10|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/identity.json|11|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/identity.json|45|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/identity.json|46|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/identity.json|80|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/identity.json|81|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/launch.json|3|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/launch.json|5|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/launch.json|7|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/launch.json|17|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/launch.json|18|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/launch.json|19|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/launch.json|117|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/launch.json|118|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/launch.json|119|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/launch.json|120|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/validation_summary.json|2|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/validation_summary.json|107|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/validation_summary.json|108|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/validation_summary.json|109|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/validation_summary.json|110|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/validation_summary.json|111|
|/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/validation_summary.json|112|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/delivery_evidence_summary.log|2|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/delivery_evidence_summary.log|107|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/delivery_evidence_summary.log|108|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/delivery_evidence_summary.log|109|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/delivery_evidence_summary.log|110|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/delivery_evidence_summary.log|111|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/delivery_evidence_summary.log|112|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/evidence_summary.log|2|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/evidence_summary.log|106|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/evidence_summary.log|107|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/evidence_summary.log|108|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/evidence_summary.log|109|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/evidence_summary.log|110|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/evidence_summary.log|111|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/evidence_summary.log|115|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/final_handoff.json|2|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/fsm_debug_draw_gui.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/fsm_debug_draw_gui.log|2|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/fsm_debug_draw_unlocked.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/fsm_debug_draw_unlocked.log|3|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/fsm_delivery_gui.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/fsm_delivery_gui.log|3|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/fsm_gui_final.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/fsm_gui_final_v2.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/fsm_gui_final_v2.log|3|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/handoff_gui.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/handoff_gui.log|2|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight.json|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight.json|13|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight.json|14|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight.json|15|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight.json|113|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight.json|114|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight.json|115|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight.json|116|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_delivery.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_delivery.log|13|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_delivery.log|14|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_delivery.log|15|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_delivery.log|113|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_delivery.log|114|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_delivery.log|115|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_delivery.log|116|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.json|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.json|13|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.json|14|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.json|15|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.json|113|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.json|114|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.json|115|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.json|116|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.log|13|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.log|14|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.log|15|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.log|113|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.log|114|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.log|115|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/preflight_final.log|116|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|2|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|3|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|4|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|5|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|6|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|7|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|8|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|9|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|10|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|11|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|12|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|13|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|14|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|19|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|21|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/proxy_regression.log|24|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/teleop_gui_acceptance.json|2|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/teleop_gui_acceptance.json|3|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/teleop_gui_acceptance.json|2709|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/teleop_gui_regression.log|86|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_delivery.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_final.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_final_v2.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_final_v3.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_final_v4.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_final_v5.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_initial.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_render_final.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_v2.log|1|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/fsm_v1_20261103/unit_v3.log|1|
|/home/zxq/robot_projects/dogfight_rl/scripts/autoppo/verify_launch.py|119|
|/home/zxq/robot_projects/dogfight_rl/scripts/autoppo/verify_launch.py|121|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/curriculum_v6_3_manager.py|9|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/run_csdog_aligned_evaluations.py|4|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/write_csdog_report.py|17|
|/home/zxq/robot_projects/dogfight_rl/scripts/diagnostics/write_csdog_spot_report.py|154|
|/home/zxq/robot_projects/dogfight_rl/scripts/launch_dogfight_teleop.sh|24|
|/home/zxq/robot_projects/dogfight_rl/scripts/launch_dogfight_teleop.sh|28|
|/home/zxq/robot_projects/dogfight_rl/scripts/launch_dogfight_teleop.sh|29|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/dogfight-fsm.desktop|7|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/dogfight-fsm.desktop|8|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/dogfight-fsm.desktop|9|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/dogfight-fsm.desktop|10|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/dogfight-teleop.desktop|7|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/dogfight-teleop.desktop|8|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/dogfight-teleop.desktop|9|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/dogfight-teleop.desktop|10|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_attached_gui.py|33|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_attached_gui.py|39|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_desktop_launch.py|43|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_desktop_launch.py|53|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_fsm_gui.py|7|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_fsm_gui.py|21|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_fsm_gui.py|35|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_fsm_gui.py|36|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_keyboard_gui.py|41|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_three_dog_gui.py|41|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/verify_three_dog_gui.py|60|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/autoppo/config.py|6|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6/README.md|52|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/phase_guided_v7/reporting.py|43|
|/home/zxq/robot_projects/dogfight_rl/tests/test_curriculum_v6_3.py|54|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|4|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|7|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|10|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|13|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|16|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|19|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|22|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|24|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|26|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|29|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|32|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|34|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|36|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|39|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|42|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|59|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|61|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|63|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|65|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|67|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|69|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|71|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|73|
|/home/zxq/robot_projects/reorganization/20261026/baseline_pytest.log|75|
|/home/zxq/robot_projects/reorganization/20261026/environment_check.log|1|
|/home/zxq/robot_projects/reorganization/20261026/final_pytest.log|1|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|24|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|39|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|40|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|41|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|42|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|51|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|52|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|53|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|54|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|84|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|124|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|125|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|126|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|127|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|139|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|142|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|145|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|146|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|160|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|163|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|166|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|167|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|181|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|184|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|187|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|188|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|202|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|205|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|208|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|209|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|223|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|224|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|234|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|238|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|247|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|248|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|249|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|263|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|266|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|269|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|270|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|284|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|287|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|290|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|291|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|304|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|316|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|317|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|322|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|333|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|334|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|347|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|348|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|362|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|365|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|368|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|369|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|383|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|386|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|389|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|390|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|404|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|407|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|410|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|411|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|425|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|428|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|431|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|432|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|446|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|449|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|452|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|453|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|467|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|470|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|473|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|474|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|488|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|491|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|494|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|495|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|509|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|512|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|515|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|516|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|529|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|530|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|542|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|543|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|555|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|556|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|568|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|580|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|581|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|595|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|598|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|601|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|602|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|616|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|619|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|622|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|623|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|738|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|802|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|1229|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|1517|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|1518|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|1746|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2270|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2271|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2532|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2533|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2552|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2553|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2572|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2573|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2592|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2593|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2612|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2613|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2632|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2633|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2652|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2653|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2721|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|2722|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3097|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3098|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3153|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3154|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3173|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3174|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3235|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3236|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3256|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3275|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3276|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3295|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3296|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3315|
|/home/zxq/robot_projects/reorganization/20261026/git_diff_before.patch|3316|
|/home/zxq/robot_projects/reorganization/20261026/integrity_final.json|1|
|/home/zxq/robot_projects/reorganization/20261026/integrity_initial.json|1|
|/home/zxq/robot_projects/reorganization/20261026/isaac_battle_smoke.log|1|
|/home/zxq/robot_projects/reorganization/20261026/isaac_battle_smoke.log|4|
|/home/zxq/robot_projects/reorganization/20261026/isaac_battle_smoke.log|7|
|/home/zxq/robot_projects/reorganization/20261026/isaac_battle_smoke.log|27|
|/home/zxq/robot_projects/reorganization/20261026/isaac_battle_smoke.log|28|
|/home/zxq/robot_projects/reorganization/20261026/isaac_battle_smoke.log|29|
|/home/zxq/robot_projects/reorganization/20261026/legacy_mock_pytest.log|1|
|/home/zxq/robot_projects/reorganization/20261026/manifest.json|3|
|/home/zxq/robot_projects/reorganization/20261026/originals/AGENTS.md|3|
|/home/zxq/robot_projects/reorganization/20261026/originals/AGENTS.md|26|
|/home/zxq/robot_projects/reorganization/20261026/originals/archive/legacy_dog_a/diagnostics/test_dog_a_interface.py|106|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/AGENTS.md|28|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/README.md|3|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/README.md|8|
|/home/zxq/robot_projects/reorganization/20261026/originals/dogfight_rl/README.md|31|
|/home/zxq/robot_projects/reorganization/20261026/post_move_pytest_initial.log|1|
|/home/zxq/robot_projects/reorganization/20261026/post_move_pytest_initial.log|7|
|/home/zxq/robot_projects/reorganization/20261026/post_move_pytest_initial.log|20|
|/home/zxq/robot_projects/reorganization/20261026/post_move_pytest_initial.log|22|
|/home/zxq/robot_projects/reorganization/20261026/post_move_pytest_initial.log|25|
|/home/zxq/robot_projects/reorganization/20261026/post_move_pytest_initial.log|28|
|/home/zxq/robot_projects/reorganization/20261026/post_move_pytest_initial.log|45|
|/home/zxq/robot_projects/reorganization/20261026/post_move_pytest_initial.log|63|
|/home/zxq/robot_projects/reorganization/20261026/post_move_pytest_initial.log|79|
|/home/zxq/robot_projects/reorganization/20261026/post_refactor_pytest.log|1|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|1|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|2|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|3|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|29|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|31|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|33|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|35|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|37|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|39|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|41|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|43|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|45|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|47|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|49|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|51|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|53|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|55|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|57|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|59|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|61|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|63|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|65|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|67|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|69|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|71|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|73|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|75|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|77|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|79|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|81|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|83|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|85|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|87|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|89|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|91|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation.log|93|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|1|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|2|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|3|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|29|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|31|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|33|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|35|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|37|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|39|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|41|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|43|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|45|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|47|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|49|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|51|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|53|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|55|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|57|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|59|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|61|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|63|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|65|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|67|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|69|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|71|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|73|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|75|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|77|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|79|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|82|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|83|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|84|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|86|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|88|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|90|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|92|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|94|
|/home/zxq/robot_projects/reorganization/20261026/training_runtime_validation_final.log|96|
|/home/zxq/桌面/三狗自主对战.desktop|7|
|/home/zxq/桌面/三狗自主对战.desktop|8|
|/home/zxq/桌面/三狗自主对战.desktop|9|
|/home/zxq/桌面/三狗自主对战.desktop|10|
|/home/zxq/桌面/机器狗对战环境.desktop|7|
|/home/zxq/桌面/机器狗对战环境.desktop|8|
|/home/zxq/桌面/机器狗对战环境.desktop|9|
|/home/zxq/桌面/机器狗对战环境.desktop|10|

原始URDF package.xml作者/邮件、同学导入模型与权重来源、课程汇报姓名、桌面路径、截图和日志中的用户名都需提交前审阅；本轮不改字节。第三方授权：THIRD_PARTY_NOTICES只列早期架构参考，未覆盖同学模型/权重再分发授权；导入包/model README/package.xml不构成明确公开再许可证明。应补来源、作者许可及发布范围；NVIDIA SDK/MDL/官方场景按NVIDIA条款另行安装/备份，不上传整套SDK；IsaacLab保留上游许可证和固定commit。模型/权重公开分发授权是发布阻塞，不能因仓库可访问就认定允许复制所有资源。

## 全部软链接（不上传）

|绝对路径|目标|目标当前存在|
|---|---|---|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_candidate_control_and_rejcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_candidate_control_and_rej0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_cumulative_time_budget_blcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_cumulative_time_budget_bl0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_gate_requires_consecutivecurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_gate_requires_consecutive0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_incomparable_candidate_facurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_incomparable_candidate_fa0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_curriculum_requires_repeacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_curriculum_requires_repea0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_spot_cumulative_time_limicurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_spot_cumulative_time_limi0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_v3_time_cap_and_interruptcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_v3_time_cap_and_interrupt0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_rank_pointer_after_stage_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_rank_pointer_after_stage_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_cumulative_budget_rejectscurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_cumulative_budget_rejects0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_no_infinite_oom_at_minimucurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_no_infinite_oom_at_minimu0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_spot_cumulative_update_licurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_spot_cumulative_update_li0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_halving_and_finite_stagnacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_halving_and_finite_stagna0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_later_generation_does_notcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_later_generation_does_not0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_immutable_boundscurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_immutable_bounds0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_supervisor_resume_preservcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_supervisor_resume_preserv0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_checkpoint_contract_rejeccurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_checkpoint_contract_rejec0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_actor_reconstruction_usescurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_actor_reconstruction_uses0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_restart_falls_back_from_tcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_restart_falls_back_from_t0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_v3_exact_updates_and_sepacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_v3_exact_updates_and_sepa0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_atomic_transaction_rollbacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_atomic_transaction_rollba0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_accepted_candidate_registcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_accepted_candidate_regist0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_exclusive_lock_and_child_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_exclusive_lock_and_child_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_nested_resource_config_frcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_nested_resource_config_fr0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_regression_preserves_rejecurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_regression_preserves_reje0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_invalid_full_data_does_nocurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_invalid_full_data_does_no0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_separate_protocol_cannot_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_separate_protocol_cannot_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_frequency_diagnostic_is_fcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_frequency_diagnostic_is_f0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_run_provenance_and_no_ovecurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_run_provenance_and_no_ove0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_safe_repairs_change_one_fcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_safe_repairs_change_one_f0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_no_trend_never_enters_loncurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_no_trend_never_enters_lon0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_finite_repair_and_equal_bcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_finite_repair_and_equal_b0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_version_reset_preserves_lcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_version_reset_preserves_l0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_policy_manifest_weight_shcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_policy_manifest_weight_sh0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_light_never_promotes_and_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_light_never_promotes_and_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_resume_partially_created_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_resume_partially_created_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_v3_stage_and_total_capscurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_v3_stage_and_total_caps0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_stagnation_stops_before_gcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_stagnation_stops_before_g0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_spot_budget_does_not_readcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_spot_budget_does_not_read0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_nan_and_wrong_dimensions_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_nan_and_wrong_dimensions_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_failed_swing_not_repeatedcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_failed_swing_not_repeated0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_existing_output_is_rejectcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_existing_output_is_reject0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_torn_checkpoint_and_bank_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_torn_checkpoint_and_bank_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_oom_and_nan_recovery_are_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_oom_and_nan_recovery_are_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_gait_regression_cannot_ovcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_gait_regression_cannot_ov0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_search_dedup_restore_and_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_pytest_tmp/test_search_dedup_restore_and_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_candidate_control_and_rejcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_candidate_control_and_rej0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_cumulative_time_budget_blcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_cumulative_time_budget_bl0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_gate_requires_consecutivecurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_gate_requires_consecutive0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_incomparable_candidate_facurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_incomparable_candidate_fa0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_curriculum_requires_repeacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_curriculum_requires_repea0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_spot_cumulative_time_limicurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_spot_cumulative_time_limi0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_v3_time_cap_and_interruptcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_v3_time_cap_and_interrupt0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_rank_pointer_after_stage_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_rank_pointer_after_stage_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_cumulative_budget_rejectscurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_cumulative_budget_rejects0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_no_infinite_oom_at_minimucurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_no_infinite_oom_at_minimu0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_spot_cumulative_update_licurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_spot_cumulative_update_li0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_halving_and_finite_stagnacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_halving_and_finite_stagna0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_later_generation_does_notcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_later_generation_does_not0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_immutable_boundscurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_immutable_bounds0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_supervisor_resume_preservcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_supervisor_resume_preserv0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_checkpoint_contract_rejeccurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_checkpoint_contract_rejec0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_actor_reconstruction_usescurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_actor_reconstruction_uses0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_restart_falls_back_from_tcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_restart_falls_back_from_t0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_v3_exact_updates_and_sepacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_v3_exact_updates_and_sepa0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_atomic_transaction_rollbacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_atomic_transaction_rollba0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_accepted_candidate_registcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_accepted_candidate_regist0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_exclusive_lock_and_child_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_exclusive_lock_and_child_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_nested_resource_config_frcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_nested_resource_config_fr0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_regression_preserves_rejecurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_regression_preserves_reje0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_invalid_full_data_does_nocurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_invalid_full_data_does_no0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_separate_protocol_cannot_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_separate_protocol_cannot_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_frequency_diagnostic_is_fcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_frequency_diagnostic_is_f0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_run_provenance_and_no_ovecurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_run_provenance_and_no_ove0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_safe_repairs_change_one_fcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_safe_repairs_change_one_f0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_no_trend_never_enters_loncurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_no_trend_never_enters_lon0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_finite_repair_and_equal_bcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_finite_repair_and_equal_b0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_version_reset_preserves_lcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_version_reset_preserves_l0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_policy_manifest_weight_shcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_policy_manifest_weight_sh0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_light_never_promotes_and_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_light_never_promotes_and_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_resume_partially_created_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_resume_partially_created_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_v3_stage_and_total_capscurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_v3_stage_and_total_caps0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_stagnation_stops_before_gcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_stagnation_stops_before_g0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_spot_budget_does_not_readcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_spot_budget_does_not_read0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_nan_and_wrong_dimensions_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_nan_and_wrong_dimensions_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_failed_swing_not_repeatedcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_failed_swing_not_repeated0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_existing_output_is_rejectcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_existing_output_is_reject0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_torn_checkpoint_and_bank_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_torn_checkpoint_and_bank_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_oom_and_nan_recovery_are_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_oom_and_nan_recovery_are_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_gait_regression_cannot_ovcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_gait_regression_cannot_ov0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_search_dedup_restore_and_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_pytest_tmp/test_search_dedup_restore_and_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_candidate_control_and_rejcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_candidate_control_and_rej0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_cumulative_time_budget_blcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_cumulative_time_budget_bl0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_gate_requires_consecutivecurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_gate_requires_consecutive0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_incomparable_candidate_facurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_incomparable_candidate_fa0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_curriculum_requires_repeacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_curriculum_requires_repea0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_spot_cumulative_time_limicurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_spot_cumulative_time_limi0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_v3_time_cap_and_interruptcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_v3_time_cap_and_interrupt0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_rank_pointer_after_stage_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_rank_pointer_after_stage_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_cumulative_budget_rejectscurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_cumulative_budget_rejects0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_no_infinite_oom_at_minimucurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_no_infinite_oom_at_minimu0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_spot_cumulative_update_licurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_spot_cumulative_update_li0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_halving_and_finite_stagnacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_halving_and_finite_stagna0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_later_generation_does_notcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_later_generation_does_not0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_immutable_boundscurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_immutable_bounds0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_supervisor_resume_preservcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_supervisor_resume_preserv0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_checkpoint_contract_rejeccurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_checkpoint_contract_rejec0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_actor_reconstruction_usescurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_actor_reconstruction_uses0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_restart_falls_back_from_tcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_restart_falls_back_from_t0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_v3_exact_updates_and_sepacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_v3_exact_updates_and_sepa0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_atomic_transaction_rollbacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_atomic_transaction_rollba0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_accepted_candidate_registcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_accepted_candidate_regist0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_exclusive_lock_and_child_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_exclusive_lock_and_child_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_nested_resource_config_frcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_nested_resource_config_fr0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_checkpoint_manifest_hash_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_checkpoint_manifest_hash_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_regression_preserves_rejecurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_regression_preserves_reje0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_invalid_full_data_does_nocurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_invalid_full_data_does_no0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_separate_protocol_cannot_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_separate_protocol_cannot_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_frequency_diagnostic_is_fcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_frequency_diagnostic_is_f0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_run_provenance_and_no_ovecurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_run_provenance_and_no_ove0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_safe_repairs_change_one_fcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_safe_repairs_change_one_f0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_no_trend_never_enters_loncurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_no_trend_never_enters_lon0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_finite_repair_and_equal_bcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_finite_repair_and_equal_b0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_version_reset_preserves_lcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_version_reset_preserves_l0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_policy_manifest_weight_shcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_policy_manifest_weight_sh0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_light_never_promotes_and_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_light_never_promotes_and_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_resume_partially_created_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_resume_partially_created_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_v3_stage_and_total_capscurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_v3_stage_and_total_caps0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_stagnation_stops_before_gcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_stagnation_stops_before_g0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_spot_budget_does_not_readcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_spot_budget_does_not_read0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_nan_and_wrong_dimensions_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_nan_and_wrong_dimensions_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_failed_swing_not_repeatedcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_failed_swing_not_repeated0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_existing_output_is_rejectcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_existing_output_is_reject0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_torn_checkpoint_and_bank_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_torn_checkpoint_and_bank_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_oom_and_nan_recovery_are_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_oom_and_nan_recovery_are_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_gait_regression_cannot_ovcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_gait_regression_cannot_ov0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_search_dedup_restore_and_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_final_verified_tmp/test_search_dedup_restore_and_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_candidate_control_and_rejcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_candidate_control_and_rej0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_cumulative_time_budget_blcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_cumulative_time_budget_bl0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_gate_requires_consecutivecurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_gate_requires_consecutive0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_incomparable_candidate_facurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_incomparable_candidate_fa0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_curriculum_requires_repeacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_curriculum_requires_repea0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_spot_cumulative_time_limicurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_spot_cumulative_time_limi0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_v3_time_cap_and_interruptcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_v3_time_cap_and_interrupt0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_rank_pointer_after_stage_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_rank_pointer_after_stage_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_cumulative_budget_rejectscurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_cumulative_budget_rejects0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_no_infinite_oom_at_minimucurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_no_infinite_oom_at_minimu0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_spot_cumulative_update_licurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_spot_cumulative_update_li0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_halving_and_finite_stagnacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_halving_and_finite_stagna0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_later_generation_does_notcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_later_generation_does_not0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_immutable_boundscurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_immutable_bounds0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_supervisor_resume_preservcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_supervisor_resume_preserv0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_checkpoint_contract_rejeccurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_checkpoint_contract_rejec0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_actor_reconstruction_usescurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_actor_reconstruction_uses0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_restart_falls_back_from_tcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_restart_falls_back_from_t0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_v3_exact_updates_and_sepacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_v3_exact_updates_and_sepa0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_atomic_transaction_rollbacurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_atomic_transaction_rollba0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_accepted_candidate_registcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_accepted_candidate_regist0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_exclusive_lock_and_child_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_exclusive_lock_and_child_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_nested_resource_config_frcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_nested_resource_config_fr0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_checkpoint_manifest_hash_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_checkpoint_manifest_hash_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_regression_preserves_rejecurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_regression_preserves_reje0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_invalid_full_data_does_nocurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_invalid_full_data_does_no0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_separate_protocol_cannot_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_separate_protocol_cannot_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_frequency_diagnostic_is_fcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_frequency_diagnostic_is_f0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_run_provenance_and_no_ovecurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_run_provenance_and_no_ove0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_safe_repairs_change_one_fcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_safe_repairs_change_one_f0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_no_trend_never_enters_loncurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_no_trend_never_enters_lon0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_finite_repair_and_equal_bcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_finite_repair_and_equal_b0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_version_reset_preserves_lcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_version_reset_preserves_l0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_policy_manifest_weight_shcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_policy_manifest_weight_sh0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_light_never_promotes_and_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_light_never_promotes_and_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_resume_partially_created_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_resume_partially_created_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_v3_stage_and_total_capscurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_v3_stage_and_total_caps0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_stagnation_stops_before_gcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_stagnation_stops_before_g0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_spot_budget_does_not_readcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_spot_budget_does_not_read0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_nan_and_wrong_dimensions_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_nan_and_wrong_dimensions_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_failed_swing_not_repeatedcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_failed_swing_not_repeated0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_existing_output_is_rejectcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_existing_output_is_reject0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_torn_checkpoint_and_bank_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_torn_checkpoint_and_bank_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_oom_and_nan_recovery_are_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_oom_and_nan_recovery_are_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_gait_regression_cannot_ovcurrent|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_gait_regression_cannot_ov0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_search_dedup_restore_and_current|/home/zxq/robot_projects/dogfight_rl/runs/validation/teleop_delivery_pytest_tmp/test_search_dedup_restore_and_0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_tuning_v5/reports/regression_tmp/test_checkpoint_contract_rejeccurrent|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_tuning_v5/reports/regression_tmp/test_checkpoint_contract_rejec0|True|
|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_tuning_v5/reports/final_regression_tmp/test_checkpoint_contract_rejeccurrent|/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_tuning_v5/reports/final_regression_tmp/test_checkpoint_contract_rejec0|True|

生产入口无软链接。测试current链接是pytest临时别名，不是运行缺失依赖。硬链接组如下（若空则无多路径同inode组）：

|inode关联路径|
|---|

## 运行权重SHA256

`/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/policies/v1/model_final.pt`

字节 2722815；SHA256 `283c0ed7ca6500ea0e8f01edc16512b27381ff556790e95900f623584dfa29f7`；无归一化伴随文件；不上传其余 1756 个历史/训练权重作为当前运行依赖。


## 补充：官方地面USD与贴图动态引用实核

只读HTTP取回地面USD至内存，使用Sdf匿名层Import解析（memfd，不创建落盘资产、不启动Kit）。地面自身13622字节，SHA256 `8a21c317d638d33a4e6c20c958a7ed8f4d8c5195efd7e20f1b85178b4a15638a`；无外部USD层引用，但材质引用SDK的OmniPBR.mdl及下面三张贴图。纹理URL按原层所在目录解析，均属外部依赖，没有可列出的项目内绝对路径；不能因本机未缺图就认为Git包自足。

|URL/绝对路径|字节|SHA256|调用入口|必要性/上传方式/理由|
|---|---:|---|---|---|
|https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Environments/Grid/default_environment.usd|13622|`8a21c317d638d33a4e6c20c958a7ed8f4d8c5195efd7e20f1b85178b4a15638a`|maps.build_map → GroundPlaneCfg|是；必须单独备份/官方恢复；NVIDIA资产不直接纳入Git|
|https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Environments/Grid/Materials/Textures/Wireframe_blue.png|111895|`940b96ee8c8e53bd1acbc770d4ca0ac98bed9c96439ab386d1b27dbc9790cc4e`|default_environment.usd材质|渲染恢复需要；必须单独备份/官方恢复；HTTP读取验证；未落盘|
|https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Environments/Grid/Materials/Textures/WireframeBlur_basecolor.png|436257|`deab39088eaf39ed7be951966c5e6bd5e58b90ab64743b0cdc8e5579fd5a99d9`|default_environment.usd材质|渲染恢复需要；必须单独备份/官方恢复；HTTP读取验证；未落盘|
|https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Environments/Grid/Materials/Textures/WireframeBlur_blue.png|1474958|`44fc0e82007bb0bd94631cd7ec45986a71ed74b9413899fbffac13efe151be4b`|default_environment.usd材质|渲染恢复需要；必须单独备份/官方恢复；HTTP读取验证；未落盘|
|/home/zxq/miniconda3/envs/dogfight/lib/python3.11/site-packages/isaacsim/kit/mdl/core/Base/OmniPBR.mdl|15591|`685a82c18b381f1cd29831490e4c356e61dbeac2d86803babc115cd6a4a845db`|模型USD与地面材质|是；随SDK及MDL依赖库整体恢复，不上传Git|

本次已识别并验证三张直接纹理，不把它们写成“未知文件”；尚未将官方资源合法离线落盘、配置新的资产根或执行断网恢复，故离线自足性仍未通过。MDL内部标准库依赖随完整固定SDK恢复，不从中抽取不完整单文件。外部HTTP资源字节不计入本地文件分类体积。


## 补充：敏感文件名与可执行位

对项目范围（不进入.git对象、不过软链接）搜索.env、pem/key、私钥文件名及credentials/secrets配置，仅发现IsaacLab自带5个Docker/模板.env文件，均不在本次上传集合；未发现当前业务上传候选中的独立密钥文件。这不替代完整历史secret scan。

两桌面文件与两个启动wrapper当前均有可执行位；独立恢复副本应保留Git mode 100755，桌面可信任标记属于新机本地元数据。
