# 本次执行记录

日期2026-11-03。使用冻结解释器，只执行下述7个文件的13项纯CPU测试：test_round.py、test_weapon.py、test_intel_5s.py、test_visibility.py、test_spawn.py、test_navigation.py、test_hud.py。结果13 passed in 0.02s，0失败，见pytest_results.xml。没有执行项目launch.py test全套，避免无关训练工具测试副作用。

环境变量：PYTHONDONTWRITEBYTECODE=1，PYTEST_DISABLE_PLUGIN_AUTOLOAD=1，OMP_NUM_THREADS=1，MKL_NUM_THREADS=1。参数：python -B -m pytest -q -p no:cacheprovider --basetemp=<本审计目录>/pytest_tmp --junitxml=<本审计目录>/pytest_results.xml <上述7文件绝对路径>。conftest使用AnalyticRayQuery，未启动IsaacLab AppLauncher。

另用python3 -B执行audit_probes.py，只导入轻量业务模块与标准库，MemoryLogger不写运行日志。整个探针约0.25秒：URDF结构/惯量，墙后不可见目标距离方位泄漏，24秒模拟时间的直线卡墙，两个Proxy重叠，默认seed42解析单局（120.0167模拟秒）以及0.05秒超时/reset。模拟时间通过Python循环推进，不是120秒墙钟，也不消耗GPU。

探针中的缺陷复现是发现，不是修复后的PASS；同坐标接受说明缺少互斥保障，不是已跑PhysX接触测试。完整默认解析单局有死亡并超时平局，不是三真实机器人或Isaac比赛。物理/GPU/GUI/训练/完整实战均未执行，后续方案见各专项与路线。
