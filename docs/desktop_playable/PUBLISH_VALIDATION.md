# 桌面备份发布验证（2026-11-03）

本记录对应 `backup/2026-11-03-desktop-playable`，基于远端 main `0ac3f5c59ea6719581bfc0f492583db5aa7237fd`。只在独立发布副本整理；原工程、训练权重和运行环境未修改，未操作正在运行的仿真。

## 内容与历史

上传范围是审计清单的555项源文件（86必需、469推荐），原始逻辑字节35,443,192，约33.80 MiB，另加审计报告与发布文档。两项实际桌面文件转换为`.desktop.in`模板；发布副本README更新为最新状态；.gitignore仅在副本增加指定权重/证据例外。没有复制全部训练checkpoint；新增运行权重恰好1项。官方场景/MDL、SDK与训练历史按恢复清单另行恢复。

原 main 所有原路径文件保留，仅根README更新；更新前README原文保存在HISTORICAL_MAIN_README.md。资产历史分支不改。本地副本分支用于备份，不表示已合并main。

## 本轮实际执行

1. 复制后逐项SHA核对：原字节复制项零差异；之后源文件再校验零变化。唯一主动改写的复制源码内容是发布副本README；桌面模板、ignore和新增文档变更均单独记录。
2. 在新路径调用`load_settings`及`PolicyLoader.load`验证default/fsm_battle/single_dog：全部通过；iter1043，网络50→256→256→128→12。解析后的URDF与checkpoint均指向独立快照内部，而非原机业务树。
3. 运行冻结Python的轻量单元测试：

```bash
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1   /path/to/dogfight/bin/python -B -m pytest -q -p no:cacheprovider   --basetemp=/path/to/independent-publish/pytest_tmp   tests/test_teleop_v02.py tests/test_three_dog_teleop.py   tests/test_fsm_battle.py tests/test_first_person.py
```

结果：**52 passed in 1.11s**。仅在独立发布目录写临时测试数据，无Kit/物理GUI启动。

4. 262个Python文件AST解析通过。对候选快照文本扫描私钥头、GitHub token、AWS访问ID和字面凭据赋值，未命中；不声称这等于第三方认证的完整secret审计。登录凭据位于仓库外且不纳入提交。
5. 必需策略SHA256：`283c0ed7ca6500ea0e8f01edc16512b27381ff556790e95900f623584dfa29f7`，2,722,815字节。归一化关闭，无独立normalizer需要补传。

## 明确未执行

没有训练、安装/升级核心环境、重启桌面或在新机运行GUI。没有将历史GUI PASS算成本轮GUI结果。全部外墙方向、完整180秒超时、多小时多轮可靠性、独立机器和断网恢复仍待执行。地图官方在线资产引用已识别，不代表离线资源包已建立。整库历史integrity和全部训练工具依赖未上传的归档/实验数据，不属于本轻量备份验收承诺。

模型与权重沿用原来源和原有许可状态；备份不增加再许可。历史审计中的“未提交/未推送”等是审计时间事实，后续发布状态以Git提交和远端分支为准。

## 自校验

在仓库根执行`sha256sum -c docs/desktop_playable/SNAPSHOT_SHA256SUMS`，核对新增快照与README。清单不包含自己和Git元数据。该校验不需要启动仿真或修改环境。
