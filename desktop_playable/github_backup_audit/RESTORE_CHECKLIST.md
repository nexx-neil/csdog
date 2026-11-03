# 独立恢复与验收清单

审计时间：2026-11-03T17:28:57.014972+08:00。本轮只读源码/配置/资产与Git；仅写 github_backup_audit 下五份报告。未操作现有窗口、未启动仿真/训练/测试器、未安装依赖、未改工程。运行中的原系统仍可能自行更新日志，体积是采样快照。

## 恢复前提与本轮状态

本轮完成静态闭包、文件存在性、manifest与Actor只读加载；未在新机恢复、未重启桌面系统、未运行GUI或物理验收。不要将下列操作说明当作已执行结果。现有桌面仍有运行进程；后续验收应在独立机器/工作副本，避免触发当前锁或影响运行。

## 软件与环境版本

|组件|本机实际版本/身份|
|---|---|
|OS|Ubuntu22.04.5LTS / x86_64|
|GPU|NVIDIA GeForce RTX4070 Laptop GPU / 8188MiB|
|NVIDIA driver|580.178.04|
|Python|3.11.16|
|torch / torchvision|2.7.0+cu128 / 0.22.0+cu128|
|Isaac Sim|5.1.0.0|
|IsaacLab源码|v2.3.2 / 37ddf626871758333d6ed89cf64ad702aef127d0|
|IsaacLab元数据|isaaclab0.54.2 / isaaclab-rl0.4.7（发行包版本与Git tag不能混为一谈）|
|RSL-RL|rsl-rl-lib3.1.2（当前推理不调用训练runner）|
|PyYAML / NumPy / Gymnasium|6.0.2 / 1.26.0 / 1.2.1|
|FastAPI / Starlette|0.115.7 / 0.49.1；已知冲突保留，本轮不升级；不表示存在网页服务|

本机安装必须单独备份：Conda env整体/conda与pip发行信息、Isaac Sim/Kit官方安装与扩展、IsaacLab固定提交、兼容显卡驱动/CUDA runtime、合法官方场景离线包。Git可提交：版本清单、源代码、模型及授权、ABI和SHA、启动脚本、模板、恢复说明。不得提交Conda整目录、Xauthority、用户配置、设备缓存、token。下面版本元数据不等于一个经过重装验证的pip requirements；不要无差别pip install或升级黄金环境。

## 恢复顺序（尚未执行）

1. 独立机器使用Ubuntu22.04.5与兼容NVIDIA/RTX桌面。按官方安装渠道恢复上述Isaac Sim/IsaacLab固定版本；接受所需许可。优先使用获授权的冻结环境外部备份，保留原机环境。不要以pip升级修复FastAPI冲突。
2. 取得独立备份分支完整快照，保持desktop_playable/dogfight_rl、可选model、IsaacLab兄弟结构。校验下面模型/权重SHA，并核对manifest全部17项。若采用LFS必须确认2,722,815字节实际权重，而非文本指针。
3. 正确注册固定IsaacLab editable源码和必要依赖，确认Python解释器指向恢复环境；DOGFIGHT_ISAACLAB仅改变paths常量，不重写site-packages里的editable指向。不要复制旧绝对.pth而忽略真实目录。
4. 在独立副本导出DOGFIGHT_PYTHON。脚本launch.py和wrapper均使用此变量；无需激活Conda。首次运行可写runs与usd目录（hash不匹配会重转换）；原件仍只读保留。
5. 准备X11桌面、libX11、DISPLAY/Xauthority，不照抄DISPLAY=:1或/run/user/1000；这些是会话资源。桌面模板按实际绝对路径生成，设可执行/可信任仅在新机执行。
6. 处理官方地面在线/离线依赖，再按验收表运行两个入口；建立新的独立run，保存stdout、identity、metrics、events和截图。

## 启动脚本模板（可提交模板，未创建/执行）

```bash
#!/usr/bin/env bash
set -euo pipefail
# 此模板保存到dogfight_rl/scripts/start_restored_fsm.sh
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export DOGFIGHT_PYTHON="${DOGFIGHT_PYTHON:-$HOME/miniconda3/envs/dogfight/bin/python}"
export PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1
exec "$PROJECT_ROOT/scripts/launch_dogfight_fsm.sh" "$@"
```
键盘对战将最后一行改为launch_dogfight_teleop.sh；单狗兼容入口追加 --config configs/teleop/single_dog.yaml。现有wrapper负责flock、日志、图形会话与信号。

## 桌面快捷方式模板（安装时替换占位符）

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=三狗自主对战
Comment=三狗PPO运动策略与FSM自主对战
Exec=/ABS/PATH/desktop_playable/dogfight_rl/scripts/launch_dogfight_fsm.sh
TryExec=/ABS/PATH/desktop_playable/dogfight_rl/scripts/launch_dogfight_fsm.sh
Path=/ABS/PATH/desktop_playable/dogfight_rl
Icon=/ABS/PATH/desktop_playable/dogfight_rl/assets/ui/dogfight_teleop.svg
Terminal=false
Categories=Education;Science;
StartupNotify=true
```
另一快捷方式Name=机器狗对战环境、Exec/TryExec换teleop脚本。Desktop Entry不会按shell展开$HOME或~；安装时填真实绝对路径，路径有空格需按Desktop Entry参数转义规则处理。DOGFIGHT_PYTHON可在生成的Exec中用env显式传入；图形会话通常不继承终端shell自定义变量。不得把原机Xauthority内容或凭据写入模板。

## 模型与策略验收依据

|路径（相对dogfight_rl）|字节|SHA256|
|---|---|---|
|assets/csdog_12dof/peer_teleop_v1/IMPORT_MANIFEST.json|2203|ec4597fe2b04fd9363bb126a1d04642c1c81a2d31a0ecf13014a1e64912f6503|
|assets/csdog_12dof/peer_teleop_v1/model/README.md|1693|676f3b2d0e7926328ba0cdc887d034d29e7771e9f15947a3456281b6d11dd7fb|
|assets/csdog_12dof/peer_teleop_v1/model/meshes/base_collision.stl|1484|9c93aa72fd27c40d50539c5cbf45d5e0418986f6f0a09481c363969ed5eb6079|
|assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_pitch_collision.stl|190484|04945bf61bf4f2e49ca242de5069a1fab2bda87e2da1b5704bbd2a04ce100b80|
|assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_roll_collision.stl|236484|a942c5e921a3b5bbd17f2f53a5fcf439526b8aec6eaed38cc92575b16b904043|
|assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_knee_collision.stl|53684|cb0146a5bc3f73180ed02082054dd9fb8cd634c3abd3f38b75aee8090f1a3beb|
|assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_pitch_collision.stl|190634|cba39b20e1a2e078ea98122d99c3fb5a86dd87ee0b2b8d2cbce268208dfca5d8|
|assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_roll_collision.stl|236984|c3a5d8e7282b55c3d114e46ad34c29f34ff6c4927b009de3dd07ac2ebe27b957|
|assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_knee_collision.stl|53734|7fa626081e4394d74cc615afe4c0e51323013875c607dc57e2a38c4be6df6c23|
|assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_pitch_collision.stl|197184|b276f7c04b288794a97f3a78fb1acc404a9e0123cd90002424cdf36bb1710666|
|assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_roll_collision.stl|236234|cdd1f1a41f4160d680d91290f3b219ac997ea544758b08d419601daebfb22fa4|
|assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_knee_collision.stl|53634|6418e0c18075866d356c1bdc3dcf4f364fedc16caa219e65345382c1e5bacf31|
|assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_pitch_collision.stl|190784|6f1fc0b7b00902bdd611ec403f03d5eacfbfe165350470699bf2dbfce7c926c7|
|assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_roll_collision.stl|237534|b5ac7b6b6beb836cf1d5d18e3f8ec08ae87133cb0bc0d875757a02a35f53e04f|
|assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_knee_collision.stl|53984|eda21673b014b7b392d1f1ebbc0aa31dabd3d4a351244a92a135f8aeb46c9dd8|
|assets/csdog_12dof/peer_teleop_v1/model/robot.urdf|12505|20034d94c7c45094480ac8ec56c461b3deeaa7a210d9abd8c789d346ce8e362d|
|assets/csdog_12dof/peer_teleop_v1/model/robot_sim.urdf|18907|4806d4e0c2db659a37e9f595d739df60121d2640895f505a0aec4277779566d1|
|assets/csdog_12dof/peer_teleop_v1/policies/v1/identity.json|1367|c19c46fb1aeba1798b2ee312d406fca76cf04b47138a050ed885c85b004fea58|
|assets/csdog_12dof/peer_teleop_v1/policies/v1/model_final.pt|2722815|283c0ed7ca6500ea0e8f01edc16512b27381ff556790e95900f623584dfa29f7|
|assets/csdog_12dof/peer_teleop_v1/usd/.asset_hash|32|bda720f860072d6c8279aeb802f1a5c08ee2a3f1264091d1cb899637e41c7d6c|
|assets/csdog_12dof/peer_teleop_v1/usd/config.yaml|1719|94cf330b7710bbcef2f73e5a40f327e000bec9ec58deab6d148841110d60b850|
|assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_base.usd|2795101|117e10f6355e9cfc8c358ea7ba34bd9e967abfe52066e2ca3d1ee4d051d31bd7|
|assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_physics.usd|6438|b9b88f0dcc877db305fe25bbdfbe121aa0da363512762b6abc46f18a84802e80|
|assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_robot.usd|2075|86955b2ec66230d7f62ddb7de93f7605759c30d3864a56d90ccd0e3a47421adf|
|assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_sensor.usd|645|52ead801b34026fd03733d314bf3b01649346b984bde43a05000b939daab5959|
|assets/csdog_12dof/peer_teleop_v1/usd/csdog.usd|1454|4da8504deee2e1c831eb74e11b829de42320c65885bdc943d0c2ebc82122a9f1|

ABI：50观测/12动作，lr→lf→rf→rr各1/2/3关节；ELU 50-256-256-128-12；dt=.005/policy_dt=.02；action_scale=.35/clip1；PD40/1.5，12Nm/10rad/s，默认角全0；不归一化。禁止拿当前其他训练checkpoint按同为12DOF/50维就替换。

## 官方场景/材质离线阻塞

地图的墙体与灯光是程序生成；地面GroundPlaneCfg默认在线USD，来自 https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Environments/Grid/default_environment.usd 。当前软件中OmniPBR.mdl是SDK资产，不在Git闭包里。在线成功启动不能证明断网可恢复；应在独立恢复机用NVIDIA允许的离线资产包，追踪地面USD所有子层/纹理/MDL并保存独立校验清单。审计不扫描用户全局缓存，也不下载落盘/改地图；此项在验证完整官方资源树前保持阻塞。

## 独立验收表（全部待执行；不要勾选为PASS）

|步骤|具体操作/观察|必须保存的证据|本轮状态|
|---|---|---|---|
|静态预检|冻结Python -B：load_settings三配置+PolicyLoader；校验模型和checkpoint hash、ABI、所有本地USD层存在|stdout、SHA清单；本轮原机纯加载已通过|新机未测|
|桌面启动|先运行teleop再退出，再启动fsm；既人工双击也gio启动检查，确认非仅终端能启动|launcher日志、进程入口、窗口截图、identity.json|未测|
|模型/地图|3个独立Articulation，root自由、关节顺序正确、同权重独立history；中央墙/外墙/地面可见|identity、质量/关节/根高度、截图|未测|
|键盘|点击主窗口C解除锁停；A狗W/S/A/D/组合/Q/E；B数字小键盘各键与5停止；非数字区不控制B|真实按键事件、command与actual_velocity/pose轨迹|未测|
|停止/焦点|松手对应轴归零；Space锁停、C解锁、失焦/超时锁停、R重置锁停、Esc退出|命令、锁停原因、计时/HP/路径清空记录；漂移单列|未测|
|碰撞|低速撞中央墙、四边界，狗间/尸体阻挡；确认不是根位姿强制移动|contacts、位置轨迹/视频、碰撞schema|未测|
|三狗扣血|teleop A/B驾驶与C站立模式，再验证三FSM；单次伤害20/冷却1秒、死亡/胜负/暂停/重置|combat_events、HP/计时、metrics与HUD截图|未测|
|射程/遮挡|物理2米命中、超过3米不伤害、墙遮挡、两狗串列只先命中；量实际枪口到最近命中距离|physical_range_checks、PhysX距离与可见线长度/端点截图|未测|
|导航/路线|FSM按C自主，绕中央墙目标；观察A*膨胀与真实PPO跟踪；V显示/隐藏，R/死亡/结束无旧线|navigation_trace、计划事件、三色线/路点截图/缓冲计数|未测|
|HUD/三视角|主相机保留，三路视角数量3，血量/目标/导航/状态随运行改变|截图与identity/status|未测|
|独立离线恢复|断网新用户/新路径运行，检查地面/纹理/MDL无缺失，不依赖原机/home/zxq|网络隔离条件、错误日志、资源清单|阻塞/未测|
|180秒/多轮|明确执行完整超时并多轮重置，记录倒地/卡住/失败；不以提前获胜代替超时测试|完整events/metrics/视频|未测|
|网页端|当前无实现或网页入口；无可执行网页验收项|如将来新增应另立实现与验收|未实现证据|

## 恢复后可用的项目验收器（本轮未执行）

`scripts/teleop/verify_keyboard_gui.py`、`verify_three_dog_gui.py`、`verify_fsm_gui.py`、`verify_desktop_launch.py`等包含硬编码桌面/路径与截图输出，先在恢复副本审阅后再用；不可直接对当前窗口注入。物理专项参数 --scenario range-check/navigation-check/fsm-recovery 会写新run和摆位夹具，仅在独立副本明确记录场景，不把夹具当自然比赛。正式CLI是 launch.py teleop / fsm_battle；测试器可写文件且单元测试会创建临时目录，故本轮没有运行。

## 已知行为边界

PPO停车前漂/转向侧漂，停止是零指令而非机械刹车；CPU PhysX为三狗射线正确性的当前要求，RTX渲染仍用GPU。FSM非动态避障/SLAM/战斗RL，卡住恢复有限；严重倒地可能安全暂停。地图导航仅平面轴对齐墙体；更换地图/策略需重新验收，不承诺任意模型或地图直接可用。

## 环境发行包快照（只读元数据，可提交）

|distribution|version|
|---|---|
|Farama-Notifications|0.0.6|
|GitPython|3.1.62|
|Jinja2|3.1.6|
|Markdown|3.10.3|
|MarkupSafe|2.1.3|
|Pint|0.20.1|
|PyJWT|2.14.0|
|PyYAML|6.0.2|
|Pygments|2.21.0|
|Rtree|1.3.0|
|Werkzeug|3.1.8|
|absl-py|2.5.0|
|aioboto3|15.1.0|
|aiobotocore|2.24.0|
|aiodns|3.1.1|
|aiofiles|23.2.1|
|aiohappyeyeballs|2.4.4|
|aiohttp|3.11.11|
|aioitertools|0.11.0|
|aiosignal|1.3.2|
|annotated-types|0.8.0|
|antlr4-python3-runtime|4.9.3|
|anyio|4.14.2|
|anytree|2.13.0|
|asteval|1.0.6|
|asttokens|3.0.2|
|async-timeout|5.0.1|
|attrs|25.1.0|
|awscrt|0.23.8|
|azure-core|1.28.0|
|azure-identity|1.13.0|
|azure-storage-blob|12.17.0|
|boto3|1.39.11|
|botocore|1.39.11|
|certifi|2026.7.22|
|cffi|2.1.1|
|charset-normalizer|3.3.2|
|click|8.1.7|
|cloudpickle|3.1.2|
|cmeel|0.61.0|
|cmeel-assimp|5.4.3.1|
|cmeel-boost|1.83.0|
|cmeel-console-bridge|1.0.2.3|
|cmeel-octomap|1.10.0|
|cmeel-qhull|8.0.2.1|
|cmeel-tinyxml|2.6.2.3|
|cmeel-urdfdom|3.1.1.1|
|cmeel-zlib|1.3.2|
|comm|0.2.3|
|contourpy|1.3.1|
|coverage|7.4.4|
|cryptography|44.0.0|
|cycler|0.11.0|
|daqp|0.7.2|
|decorator|5.3.1|
|dex_retargeting|0.4.6|
|eigenpy|3.5.1|
|einops|0.8.2|
|executing|2.2.1|
|fastapi|0.115.7|
|filelock|3.13.1|
|flaky|3.8.1|
|flatdict|4.0.1|
|fonttools|4.55.3|
|frozenlist|1.5.0|
|fsspec|2024.6.1|
|gitdb|4.0.12|
|grpcio|1.83.1|
|gunicorn|23.0.0|
|gymnasium|1.2.1|
|h11|0.16.0|
|h5py|3.16.0|
|hf-xet|1.6.0|
|hidapi|0.14.0.post2|
|hpp-fcl|2.4.4|
|httptools|0.6.1|
|huggingface_hub|0.36.2|
|hydra-core|1.3.6|
|idna|3.10|
|idna-ssl|1.1.0|
|imageio|2.37.0|
|imageio-ffmpeg|0.6.0|
|importlib_metadata|9.0.1|
|iniconfig|2.3.0|
|ipython|8.32.0|
|ipython_pygments_lexers|1.1.1|
|ipywidgets|8.1.5|
|isaaclab|0.54.2|
|isaaclab_assets|0.2.4|
|isaaclab_contrib|0.0.2|
|isaaclab_mimic|1.0.16|
|isaaclab_rl|0.4.7|
|isaaclab_tasks|0.11.12|
|isaacsim|5.1.0.0|
|isaacsim-app|5.1.0.0|
|isaacsim-asset|5.1.0.0|
|isaacsim-benchmark|5.1.0.0|
|isaacsim-code-editor|5.1.0.0|
|isaacsim-core|5.1.0.0|
|isaacsim-cortex|5.1.0.0|
|isaacsim-example|5.1.0.0|
|isaacsim-extscache-kit|5.1.0.0|
|isaacsim-extscache-kit-sdk|5.1.0.0|
|isaacsim-extscache-physics|5.1.0.0|
|isaacsim-gui|5.1.0.0|
|isaacsim-kernel|5.1.0.0|
|isaacsim-replicator|5.1.0.0|
|isaacsim-rl|5.1.0.0|
|isaacsim-robot|5.1.0.0|
|isaacsim-robot-motion|5.1.0.0|
|isaacsim-robot-setup|5.1.0.0|
|isaacsim-ros1|5.1.0.0|
|isaacsim-ros2|5.1.0.0|
|isaacsim-sensor|5.1.0.0|
|isaacsim-storage|5.1.0.0|
|isaacsim-template|5.1.0.0|
|isaacsim-test|5.1.0.0|
|isaacsim-utils|5.1.0.0|
|isodate|0.6.1|
|jedi|0.20.0|
|jmespath|1.0.1|
|junitparser|5.0.3|
|jupyterlab_widgets|3.0.17|
|kiwisolver|1.4.4|
|llvmlite|0.42.0|
|loop-rate-limiters|1.2.0|
|lxml|6.1.3|
|matplotlib|3.10.3|
|matplotlib-inline|0.2.2|
|ml_dtypes|0.5.4|
|moviepy|2.2.1|
|mpmath|1.3.0|
|msal|1.27.0|
|msal-extensions|1.0.0|
|multidict|6.1.0|
|nest-asyncio|1.5.6|
|networkx|3.3|
|nlopt|2.7.1|
|numba|0.59.1|
|numpy|1.26.0|
|nvidia-cublas-cu12|12.8.3.14|
|nvidia-cuda-cupti-cu12|12.8.57|
|nvidia-cuda-nvrtc-cu12|12.8.61|
|nvidia-cuda-runtime-cu12|12.8.57|
|nvidia-cudnn-cu12|9.7.1.26|
|nvidia-cufft-cu12|11.3.3.41|
|nvidia-cufile-cu12|1.13.0.11|
|nvidia-curand-cu12|10.3.9.55|
|nvidia-cusolver-cu12|11.7.2.55|
|nvidia-cusparse-cu12|12.5.7.53|
|nvidia-cusparselt-cu12|0.6.3|
|nvidia-nccl-cu12|2.26.2|
|nvidia-nvjitlink-cu12|12.8.61|
|nvidia-nvtx-cu12|12.8.55|
|oauthlib|3.2.2|
|omegaconf|2.3.1|
|onnx|1.18.0|
|onnx-ir|1.0.0|
|onnxscript|0.5.0|
|opencv-python-headless|4.11.0.86|
|orjson|3.12.0|
|osqp|0.6.7.post3|
|packaging|23.0|
|parso|0.8.7|
|pexpect|4.9.0|
|pillow|11.3.0|
|pin|2.7.0|
|pin-pink|3.1.0|
|pip|26.2.1|
|pluggy|1.6.0|
|portalocker|2.7.0|
|prettytable|3.3.0|
|proglog|0.1.12|
|prompt_toolkit|3.0.53|
|propcache|0.2.1|
|protobuf|7.36.1|
|psutil|5.9.8|
|ptyprocess|0.7.0|
|pure_eval|0.2.4|
|pycares|4.8.0|
|pycparser|3.0|
|pydantic|2.11.10|
|pydantic_core|2.33.2|
|pyglet|1.5.31|
|pyparsing|3.0.9|
|pyperclip|1.8.0|
|pypng|0.20220715.0|
|pytest|9.1.1|
|pytest-mock|3.15.1|
|python-dateutil|2.9.0.post0|
|python-dotenv|1.2.3|
|python-multipart|0.0.20|
|pytransform3d|3.16.0|
|pytz|2024.1|
|pyvers|0.2.3|
|qdldl|0.1.7.post5|
|qpsolvers|4.13.0|
|qrcode|7.4.2|
|quadprog|0.1.13|
|regex|2026.9.10|
|requests|2.32.3|
|requests-oauthlib|1.3.1|
|rsl-rl-lib|3.1.2|
|s3transfer|0.13.1|
|safetensors|0.8.0|
|scipy|1.15.3|
|sentry-sdk|2.29.1|
|setuptools|80.9.0|
|six|1.17.0|
|smmap|5.0.3|
|stack-data|0.6.3|
|starlette|0.49.1|
|sympy|1.13.3|
|tensorboard|2.21.0|
|tensorboard-data-server|0.7.2|
|tensordict|0.14.2|
|tokenizers|0.22.2|
|toml|0.10.2|
|tomli|2.4.1|
|torch|2.7.0+cu128|
|torchaudio|2.7.0|
|torchvision|0.22.0+cu128|
|tornado|6.5.1|
|tqdm|4.70.1|
|traitlets|5.16.1|
|transformers|4.57.6|
|trimesh|4.5.1|
|triton|3.3.0|
|typing-inspection|0.4.2|
|typing_extensions|4.12.2|
|urllib3|2.7.0|
|uvicorn|0.29.0|
|warp-lang|1.17.0|
|watchdog|4.0.0|
|wcwidth|0.8.3|
|websockets|12.0|
|wheel|0.45.1|
|widgetsnbextension|4.0.16|
|wrapt|1.16.0|
|yarl|1.18.3|
|zipp|4.1.0|

## Conda包身份（只读conda-meta；不含用户路径/渠道token）

|name|version|build|subdir|
|---|---|---|---|
|_libgcc_mutex|0.1|main|linux-64|
|_openmp_mutex|5.1|52_gnu|linux-64|
|bzip2|1.0.8|h5eee18b_6|linux-64|
|ca-certificates|2026.8.13|h06a4308_0|linux-64|
|ld_impl_linux-64|2.44|h9e0c5a2_3|linux-64|
|libexpat|2.8.4|h7354ed3_0|linux-64|
|libffi|3.4.8|h06d3fd0_3|linux-64|
|libgcc|15.2.0|h69a1729_8|linux-64|
|libgcc-ng|15.2.0|h166f726_8|linux-64|
|libnsl|2.0.0|h5eee18b_0|linux-64|
|libstdcxx|15.2.0|h39759b7_8|linux-64|
|libuuid|1.41.5|h5eee18b_0|linux-64|
|libxcb|1.17.0|h9b100fa_0|linux-64|
|libzlib|1.3.2|h47b2149_0|linux-64|
|ncurses|6.6|hfaaeb4e_0|linux-64|
|openssl|3.5.8|h1b28b03_0|linux-64|
|pip|26.2.1|pyhc872135_0|noarch|
|pthread-stubs|0.3|h47b2149_2|linux-64|
|python|3.11.16|h17756b0_0|linux-64|
|readline|8.3|hc2a1206_0|linux-64|
|sqlite|3.53.4|h795bf6d_0|linux-64|
|tk|8.6.15|h54e0aa7_0|linux-64|
|tzdata|2026c|he532380_0|noarch|
|xorg-libx11|1.8.13|h65de747_0|linux-64|
|xorg-libxau|1.0.12|h9b100fa_0|linux-64|
|xorg-libxdmcp|1.1.5|h9b100fa_0|linux-64|
|xorg-xorgproto|2025.1|h47b2149_0|linux-64|
|xz|5.8.2|h448239c_0|linux-64|
|zlib|1.3.2|h47b2149_0|linux-64|


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
