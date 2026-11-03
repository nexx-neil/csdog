# 右侧机器狗第一视角

2026-11-03新增。启动桌面“机器狗对战环境”后，主视角保留在左边，右边自动显示 `DOG A | First Person` 实时视图；不需要按V切换，两画面同时显示。原WASD/QE/Space/C/R/Esc不变，先点击仿真窗口，按C解锁。

相机位于机身前上方，位置和朝向跟随真实机器人；使用水平稳定的yaw视角，减轻行走时的俯仰/横滚晃动。R重置时同时清空相机平滑历史，避免镜头从旧位置飞回出生点。左侧主视角相机没有被替换，仍能手动缩放/旋转。第一视角显示真实场景和常亮激光，不是预录视频，也没有改变PPO的50维观测或动作。

实现：`src/dogfight/teleop/first_person.py`；运行集成位于`src/dogfight/teleop/runtime.py`。相机只是USD视觉Prim，既不参与碰撞，也不推动机器人；右侧使用独立ViewportWidget，与主画面共用场景，不另开Isaac进程或训练器。

配置在`configs/teleop/default.yaml`的`first_person`：

- `enabled`：是否显示第一视角。
- `resolution: [640, 360]`：第二视口渲染分辨率，控制8GB显存开销。
- `offset: [0.22, 0.0, 0.16]`：相对根部的前/左/上偏移（米，水平yaw坐标）。
- `horizontal_fov_deg: 85`、`pitch_deg: -6`：视野和轻微俯视。
- `position_smoothing: .06`、`yaw_smoothing: .08`：平滑时间（秒）。
- `right_fraction: .34`：右侧占主区域约34%。
- `hide_editors: true`：暂时收起Stage/Property等编辑页，给双视口留空间；编辑工具仍可从Window菜单打开。需要编辑工具时可从Window菜单重新打开，或改false后重启。

配置重启生效，不进行运行中热加载。备份在`runs/validation/first_person_current.txt`指向目录的backup/中。

## 实际验证

- `runs/validation/first_person_unit.log`：27项相关CPU测试通过，含相机前上位置、转向、角度跨±π、平滑和重置。
- `runs/battle/teleop/20261103_124045_32640a25/`：16模拟秒GUI运动，完成前进/后退/双向转向等片段；首次界面截图和metrics保留。
- `runs/battle/teleop/20261103_124217_3f8c9b93/`：最终布局12模拟秒GUI测试，601次相机更新；docked=true，全部记录main_camera_unchanged=true；约13.36墙钟秒。截图`first_person_verified.png`已实际查看，左主视角、右机身第一视角及激光均可见。
- 新增视口时观察显存约5.56GB，未并行启动其他Isaac；此为单次观察，不是所有场景的上限保证。
- 桌面入口键盘回归日志：`runs/validation/first_person_keyboard_gui.log`；最终结果在`runs/validation/desktop_launch_acceptance.json`与对应run中。

没有安装依赖、重新训练或修改模型权重。最初使用旧dockInWindow接口时产生弃用提示，已改为当前WindowHandle.dock_in，最终布局通过实际GUI验证。
