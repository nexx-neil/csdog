"""Short read-only training imports and archived USD dependency check; no environment/training."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from isaaclab.app import AppLauncher
app = AppLauncher(headless=True, device="cpu").app
try:
    import json
    import torch
    import yaml
    from pxr import UsdUtils
    from rsl_rl.runners import OnPolicyRunner
    from dogfight.training.action_audit_wrapper import ActionAuditRslRlVecEnvWrapper
    from dogfight.training.ppo import make_runner_config
    from dogfight.training.deployment import load_actor
    archive = ROOT.parent / "archive/legacy_dog_a"
    raw = yaml.safe_load((archive / "configs/training/back_gait_primitive_recovery.yaml").read_text())
    cfg = make_runner_config(raw["ppo"], device="cpu", iterations=1, experiment_name="import_validation_only")
    assert cfg.max_iterations == 1
    actor, scale = load_actor(archive / "checkpoints_and_runs/back_gait_primitive_recovery/model_final.pt",
                             raw, "cpu", observation_dimension=48, action_dimension=12)
    assert scale == 0.5 and torch.isfinite(actor(torch.zeros(1, 48))).all()
    roots = [archive / "assets/dog_a/dog_a.usd",
             archive / "assets/dog_a/usd_attempt_002_named_joints/dog_a.usd",
             archive / "assets/dog_a_symmetric_v1/usd/dog_a_symmetric_v1.usd"]
    layers = set()
    unresolved = []
    for root in roots:
        dependencies, assets, missing = UsdUtils.ComputeAllDependencies(str(root))
        assert dependencies, root
        layers.update(layer.realPath for layer in dependencies)
        unresolved.extend(str(x) for x in missing)
    # OmniPBR is supplied by the installed Isaac MDL library, not an archived USD sublayer.
    internal_missing = [x for x in unresolved if not x.endswith("OmniPBR.mdl")]
    assert not internal_missing, internal_missing
    mdl = Path(sys.prefix) / "lib/python3.11/site-packages/isaacsim/kit/mdl/core/Base/OmniPBR.mdl"
    assert mdl.is_file(), mdl
    print("TRAINING_RESOURCE_VALIDATION " + json.dumps(dict(status="PASS", wrapper_import=True,
        ppo_config=True, legacy_actor_explicit_load=True, actor_output_scale=scale,
        usd_roots=len(roots), usd_layers=len(layers), unresolved=unresolved,
        new_model_environment="NOT_IMPLEMENTED", training_updates=0, external_mdl=str(mdl))), flush=True)
finally:
    app.close(wait_for_replicator=False, skip_cleanup=True)
