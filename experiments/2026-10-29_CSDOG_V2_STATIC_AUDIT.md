# CSDog URDF 静态审计

- 总门禁：**FAIL**
- 结构门禁：**PASS**
- 物理就绪门禁：**FAIL**
- Git commit：`6ec43f8961dc7191dc73714ebca2b11727151c54`
- URDF：`/home/ni/robot_projects/csdog/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/robot.urdf`
- link / revolute joint：13 / 12
- 总质量：7.60426080 kg
- 零位形整机质心：`[-0.00199211644471868, -2.194660748605407e-05, -0.07396200884466289]` m
- mesh：13 个，collision 三角形合计 38635

## 已证实问题

- `UNIFORM_TEMPLATE_LIMITS` [review_required] all 12 joints use one identical limit tuple; mechanical/electrical provenance is not recorded
- `FULL_ROTATION_POSITION_LIMITS` [review_required] revolute joints use approximately ±pi; self-collision is disabled and real hard stops are unverified
- `HIGH_POLY_COLLISION` [review_required] 12 collision meshes exceed 1000 triangles

## 警告与待测试假设

- `VISUAL_COLLISION_MESH_REUSE` [warning] all 13 collision meshes are also used as visuals; independent low-poly collision provenance is absent
- `COM_REQUIRES_DYNAMIC_VALIDATION` [hypothesis] zero-pose COM is computed from URDF, but support polygon margin and loaded hardware COM still require simulation/CAD validation
- `CONTACT_PATCH_UNVERIFIED` [hypothesis] mesh existence does not prove watertight foot collision, stable contact patches, or correct friction behavior

## 关节顺序与限位

| # | 名称 | parent → child | axis | lower | upper | effort | velocity |
|---:|---|---|---|---:|---:|---:|---:|
| 0 | `joint_lr_1` | `base` → `link_lr_hip_roll` | `[-1.0, 0.0, 0.0]` | -3.14 | 3.14 | 10.0 | 3.0 |
| 1 | `joint_lr_2` | `link_lr_hip_roll` → `link_lr_hip_pitch` | `[0.0, 0.99914919, 0.04124191]` | -3.14 | 3.14 | 10.0 | 3.0 |
| 2 | `joint_lr_3` | `link_lr_hip_pitch` → `link_lr_knee` | `[0.0, 0.99914919, 0.04124191]` | -3.14 | 3.14 | 10.0 | 3.0 |
| 3 | `joint_lf_1` | `base` → `link_lf_hip_roll` | `[1.0, 0.0, 0.0]` | -3.14 | 3.14 | 10.0 | 3.0 |
| 4 | `joint_lf_2` | `link_lf_hip_roll` → `link_lf_hip_pitch` | `[0.0, 0.99961862, 0.02761531]` | -3.14 | 3.14 | 10.0 | 3.0 |
| 5 | `joint_lf_3` | `link_lf_hip_pitch` → `link_lf_knee` | `[0.0, 0.99961862, 0.02761531]` | -3.14 | 3.14 | 10.0 | 3.0 |
| 6 | `joint_rf_1` | `base` → `link_rf_hip_roll` | `[1.0, 0.0, 0.0]` | -3.14 | 3.14 | 10.0 | 3.0 |
| 7 | `joint_rf_2` | `link_rf_hip_roll` → `link_rf_hip_pitch` | `[0.0, -0.99961862, 0.02761531]` | -3.14 | 3.14 | 10.0 | 3.0 |
| 8 | `joint_rf_3` | `link_rf_hip_pitch` → `link_rf_knee` | `[0.0, -0.99961862, 0.02761531]` | -3.14 | 3.14 | 10.0 | 3.0 |
| 9 | `joint_rr_1` | `base` → `link_rr_hip_roll` | `[-1.0, 0.0, 0.0]` | -3.14 | 3.14 | 10.0 | 3.0 |
| 10 | `joint_rr_2` | `link_rr_hip_roll` → `link_rr_hip_pitch` | `[0.0, -0.99914919, 0.04124191]` | -3.14 | 3.14 | 10.0 | 3.0 |
| 11 | `joint_rr_3` | `link_rr_hip_pitch` → `link_rr_knee` | `[0.0, -0.99914919, 0.04124191]` | -3.14 | 3.14 | 10.0 | 3.0 |

## 门禁结论

Static structure is valid, but simulation/training is blocked until every review_required item has verified provenance.
