from dataclasses import dataclass,  field
from typing import TypeAlias
from lerobot.cameras import CameraConfig
from ..config import RobotConfig

@dataclass
class PIPERFollowerConfig:
    """Base configuration class for PIPER Follower robots."""

    can_name: str = "can0"

    enable_timeout_s: float = 5.0

    gripper_effort: int = 1000

    joint_speed: int = 30

    # cameras
    cameras: dict[str, CameraConfig] = field(default_factory=dict)

@RobotConfig.register_subclass("piper_follower")
@dataclass
class PIPERFollowerRobotConfig(RobotConfig, PIPERFollowerConfig):
    pass

PiperFollowerConfig: TypeAlias = PIPERFollowerRobotConfig
