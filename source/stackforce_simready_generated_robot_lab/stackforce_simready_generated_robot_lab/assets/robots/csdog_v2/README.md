# CSDog v2 asset

Source archive: `assets/v2_robot_urdf.zip` (kept outside Git by the repository's
archive ignore rule). This directory is intentionally separate from
`generated_robot`, which remains the asset used by
`Template-GeneratedRobot-Direct-v0` and its historical checkpoints.

- Source archive SHA256: `747f07a4bab6bd5a7a8bb8079243bd8baa30611a90d5f25db77164ea12bd2133`
- Extracted URDF SHA256: `20034d94c7c45094480ac8ec56c461b3deeaa7a210d9abd8c789d346ce8e362d`

The extracted files are preserved byte-for-byte. Do not silently replace the
URDF limits, inertial values, or meshes. Any derived collision asset must use a
new filename and record its generation command and source SHA256.

Static gate:

```bash
python scripts/audit_urdf.py \
  source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/robot.urdf \
  --expectations config/csdog_v2_urdf_expectations.json \
  --json-output experiments/results/2026-10-29/csdog_v2_static_audit.json \
  --markdown-output experiments/2026-10-29_CSDOG_V2_STATIC_AUDIT.md
```

The current physics-readiness gate is expected to fail until the hardware
limits have traceable provenance and the training collision representation is
approved.
