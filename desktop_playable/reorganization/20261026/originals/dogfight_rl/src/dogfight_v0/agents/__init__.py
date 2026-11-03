from .agent_interface import AgentInterface
from .locomotion_interface import LocomotionInterface
from .proxy_agent import ProxyAgent
from .real_dog_agent import RealDogAgent
from .dog_a_locomotion_adapter import DogALocomotionAdapter
from .real_locomotion_adapter import MockRealLocomotionAdapter, RealLocomotionAdapter

__all__ = [
    "AgentInterface",
    "LocomotionInterface",
    "ProxyAgent",
    "RealDogAgent",
    "DogALocomotionAdapter",
    "RealLocomotionAdapter",
    "MockRealLocomotionAdapter",
]
