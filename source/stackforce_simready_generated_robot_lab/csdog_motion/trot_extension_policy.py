"""Three-actor composition: retain the verified lesson20 route below .8m/s."""
import copy
import torch
from .trot_extension import strength
from .trot_policy_routing import with_saved_routing, routing_record
from .training import file_hash

def record(parent):
    return dict(previous_checkpoint=str(parent.resolve()), previous_checkpoint_sha256=file_hash(parent),
        previous_routing=routing_record(parent), activation_mps=[.8, 1.0], observation_slice=[9, 12],
        interpolation='C2 quintic of applied vx; exact previous output for <=.8m/s')

class RoutedExtensionPolicy(torch.nn.Module):
    def __init__(self, new, previous):
        super().__init__()
        self.new = new
        self.previous = previous
    def act_inference(self, obs):
        if obs['policy'].shape[-1] != 76:
            raise ValueError('Expected explicit 76D flat observation layout')
        old = self.previous.act_inference(obs)
        new = self.new.act_inference(obs)
        alpha = strength(obs['policy'][:, 9:12])[:, None]
        return torch.where(alpha == 0, old, old + alpha * (new - old))

def compose(policy, parent):
    previous = copy.deepcopy(policy)
    device = next(policy.parameters()).device
    previous.load_state_dict(torch.load(parent, map_location=device, weights_only=True)['model_state_dict'])
    previous.eval()
    for parameter in previous.parameters():
        parameter.requires_grad_(False)
    previous = with_saved_routing(previous, parent)
    return RoutedExtensionPolicy(policy, previous)
