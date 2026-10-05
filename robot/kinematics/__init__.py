"""Cinemática del manipulador 6R del proyecto."""

from .model_6r import RobotGeometry, DEMO_GEOMETRY, DEMO_LIMITS_DEG
from .forward_kinematics import forward_kinematics, rotation_to_rpy_zyx, rpy_zyx_to_rotation
from .inverse_kinematics import inverse_kinematics, IKSolution

__all__ = [
    "RobotGeometry",
    "DEMO_GEOMETRY",
    "DEMO_LIMITS_DEG",
    "forward_kinematics",
    "rotation_to_rpy_zyx",
    "rpy_zyx_to_rotation",
    "inverse_kinematics",
    "IKSolution",
]
