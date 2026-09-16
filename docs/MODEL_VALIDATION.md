# 模型包静态检查

检查日期：2026-09-16

## 文件

```text
local_mu3x59rz_5j49gz_urdf_stl.zip
SHA256: 98F7742E33F6F9E5B4F88ADEFDA0FCAF82827F3AFDCA129D4AFC59639EC22C55

Stackforce-simready-generated_robot-isaac-lab.zip
SHA256: CAB2E4728AD6F595DBC26EA4C3669BF9606033F793384CB0B60A7154CD145C0F
```

压缩包作为模型交换产物单独保存，不建议反复提交不同副本到 Git。

## 通过项

- URDF 可被 XML 解析；
- 13 个 link，12 个 revolute joint；
- 12 个关节形成四条完整的三级串联腿；
- 93 个 mesh 全部存在；
- Isaac Lab 包使用正确的 `../meshes/` 相对路径；
- 坐标报告为 `z_up_x_forward`，并记录了 CAD 导入时绕 Z 轴 `-90 deg` 预旋转；
- 动作维度为 12，观测拼接结果为 48；
- Isaac Lab 工程中的 16 个 Python 文件通过语法编译。

## 需要动态验证

- 每个关节的真实物理含义和正方向；
- 零位构型是否合理；
- 真实站立高度；
- CAD 几何估算质量是否符合真实部件；
- 关节机械限位、电机力矩和速度；
- 复杂 mesh collision 在 PhysX 中的稳定性和性能；
- 腿段、机身与地面的非期望接触。

## 不应直接采用的模板值

```text
init position z      1.0 m
base height target   0.98 m
minimum base height  0.441 m
joint limits         [-1.57, 1.57] rad（全部相同）
effort limit         10 N·m（全部相同）
velocity limit       5 rad/s（全部相同）
default joint angle  0 rad（全部关节）
```

## 结论

这套文件可以作为 Linux Isaac Lab 项目框架和模型资产使用，但在完成单环境 GUI、物理参数校准、简化碰撞和 30 秒站立测试以前，不视为正式训练就绪。

