"""Reusable policy tools preserve explicit dimensions and run provenance."""
import json
import pytest
import torch
from dogfight.training.checkpoints import create_run, validate_policy_identity
from dogfight.training.deployment import load_actor
from dogfight.training.reward_terms import foot_slip_signal

def test_run_provenance_and_no_overwrite(tmp_path):
    config = tmp_path / "config.yaml"
    config.write_text("model_id: independent_robot")
    path = tmp_path / "run"
    spec = dict(model_id="independent_robot", observation_definition=["vx", "vy"], action_definition=["joint_custom"])
    create_run(path, **spec, config_paths=[config])
    manifest = json.loads((path / "run_manifest.json").read_text())
    validate_policy_identity(manifest, **spec)
    with pytest.raises(ValueError, match="identity mismatch"):
        validate_policy_identity(manifest, **{**spec, "model_id": "csdog_12dof"})
    with pytest.raises(FileExistsError):
        create_run(path, **spec, config_paths=[config])
    assert len(manifest["configs"][0]["sha256"]) == 64
    assert manifest["source_checkpoint"] is None

def test_actor_reconstruction_uses_explicit_nonlegacy_dimensions(tmp_path):
    original = torch.nn.Sequential(torch.nn.Linear(3, 4), torch.nn.ELU(), torch.nn.Linear(4, 2))
    checkpoint = tmp_path / "policy.pt"
    torch.save({"model_state_dict": {"actor."+key: value for key, value in original.state_dict().items()},
                "infos": {"actor_output_scale": 0.3}}, checkpoint)
    actor, scale = load_actor(checkpoint, {"ppo": {"activation": "elu", "actor_hidden_dims": [4]}},
                              "cpu", observation_dimension=3, action_dimension=2)
    value = torch.tensor([[0.2, -0.1, 0.7]])
    assert torch.equal(actor(value), original(value))
    assert scale == 0.3
    with pytest.raises(RuntimeError):
        load_actor(checkpoint, {"ppo": {"activation": "elu", "actor_hidden_dims": [4]}},
                   "cpu", observation_dimension=48, action_dimension=12)

def test_reward_kernel_masks_noncontact_feet():
    contact = torch.tensor([[True, False]])
    velocity = torch.tensor([[[3., 4.], [100., 100.]]])
    assert foot_slip_signal(contact, velocity).item() == 25.0
