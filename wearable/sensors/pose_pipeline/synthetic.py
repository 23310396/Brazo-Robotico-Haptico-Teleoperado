"""Utilidades para generar orientaciones sintéticas antes de usar IMUs reales."""

from math import cos, radians, sin
from typing import Tuple

from .pipeline import OrientationSample, Quaternion


def quaternion_from_axis_angle(axis: Tuple[float, float, float], angle_deg: float) -> Quaternion:
    ax, ay, az = axis
    norm = (ax * ax + ay * ay + az * az) ** 0.5
    if norm == 0.0:
        raise ValueError("El eje de rotación no puede ser cero")

    ax, ay, az = ax / norm, ay / norm, az / norm
    half = radians(angle_deg) / 2.0
    s = sin(half)
    return (cos(half), ax * s, ay * s, az * s)


def synthetic_sample(sensor_id: str, quaternion: Quaternion, timestamp_s: float = 0.0) -> OrientationSample:
    return OrientationSample(
        sensor_id=sensor_id,
        timestamp_s=timestamp_s,
        quaternion_n_s=quaternion,
        valid=True,
    )
