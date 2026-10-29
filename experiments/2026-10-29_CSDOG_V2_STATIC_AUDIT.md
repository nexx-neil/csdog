# CSDog URDF 静态审计

- 总门禁：**PASS**
- 结构门禁：**PASS**
- 仿真就绪门禁：**PASS**
- 实机部署门禁：**FAIL**
- Git commit：`24e953977fa39167fb9996550d21a207823f317d`
- URDF：`/home/ni/robot_projects/csdog/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/robot_sim.urdf`
- link / revolute joint：17 / 12
- 总质量：7.60826080 kg
- 零位形整机质心：`[-0.001969337824172592, -2.2316319256457074e-05, -0.07412472017214804]` m
- mesh：13 个，collision 三角形合计 0

## 已证实问题

- 无。

## 实机部署阻断项

- `HARDWARE_LIMITS_UNVERIFIED` [hardware_blocker] continuous torque and assembled mechanical hard stops are unverified; simulation results must not be deployed to hardware

## 警告与待测试假设

- `COM_REQUIRES_DYNAMIC_VALIDATION` [hypothesis] zero-pose COM is computed from URDF, but support polygon margin and loaded hardware COM still require simulation/CAD validation
- `CONTACT_PATCH_UNVERIFIED` [hypothesis] mesh existence does not prove watertight foot collision, stable contact patches, or correct friction behavior

## 关节顺序与限位

| # | 名称 | parent → child | axis | lower | upper | effort | velocity |
|---:|---|---|---|---:|---:|---:|---:|
| 0 | `joint_lr_1` | `base` → `link_lr_hip_roll` | `[-1.0, 0.0, 0.0]` | -0.65 | 0.65 | 12.0 | 10.0 |
| 1 | `joint_lr_2` | `link_lr_hip_roll` → `link_lr_hip_pitch` | `[0.0, 0.99914919, 0.04124191]` | -1.4 | 1.4 | 12.0 | 10.0 |
| 2 | `joint_lr_3` | `link_lr_hip_pitch` → `link_lr_knee` | `[0.0, 0.99914919, 0.04124191]` | -1.8 | 1.8 | 12.0 | 10.0 |
| 3 | `joint_lf_1` | `base` → `link_lf_hip_roll` | `[1.0, 0.0, 0.0]` | -0.65 | 0.65 | 12.0 | 10.0 |
| 4 | `joint_lf_2` | `link_lf_hip_roll` → `link_lf_hip_pitch` | `[0.0, 0.99961862, 0.02761531]` | -1.4 | 1.4 | 12.0 | 10.0 |
| 5 | `joint_lf_3` | `link_lf_hip_pitch` → `link_lf_knee` | `[0.0, 0.99961862, 0.02761531]` | -1.8 | 1.8 | 12.0 | 10.0 |
| 6 | `joint_rf_1` | `base` → `link_rf_hip_roll` | `[1.0, 0.0, 0.0]` | -0.65 | 0.65 | 12.0 | 10.0 |
| 7 | `joint_rf_2` | `link_rf_hip_roll` → `link_rf_hip_pitch` | `[0.0, -0.99961862, 0.02761531]` | -1.4 | 1.4 | 12.0 | 10.0 |
| 8 | `joint_rf_3` | `link_rf_hip_pitch` → `link_rf_knee` | `[0.0, -0.99961862, 0.02761531]` | -1.8 | 1.8 | 12.0 | 10.0 |
| 9 | `joint_rr_1` | `base` → `link_rr_hip_roll` | `[-1.0, 0.0, 0.0]` | -0.65 | 0.65 | 12.0 | 10.0 |
| 10 | `joint_rr_2` | `link_rr_hip_roll` → `link_rr_hip_pitch` | `[0.0, -0.99914919, 0.04124191]` | -1.4 | 1.4 | 12.0 | 10.0 |
| 11 | `joint_rr_3` | `link_rr_hip_pitch` → `link_rr_knee` | `[0.0, -0.99914919, 0.04124191]` | -1.8 | 1.8 | 12.0 | 10.0 |
| 12 | `joint_link_lr_sole_fixed` | `link_lr_knee` → `link_lr_sole` | `[1.0, 0.0, 0.0]` | None | None | None | None |
| 13 | `joint_link_lf_sole_fixed` | `link_lf_knee` → `link_lf_sole` | `[1.0, 0.0, 0.0]` | None | None | None | None |
| 14 | `joint_link_rf_sole_fixed` | `link_rf_knee` → `link_rf_sole` | `[1.0, 0.0, 0.0]` | None | None | None | None |
| 15 | `joint_link_rr_sole_fixed` | `link_rr_knee` → `link_rr_sole` | `[1.0, 0.0, 0.0]` | None | None | None | None |

## 门禁结论

Static simulation gate passed; hardware deployment remains separately gated.
