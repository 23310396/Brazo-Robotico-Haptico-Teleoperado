"""Pipeline geométrico para estimar la pose de la mano desde 3 IMUs.

El núcleo es independiente del modelo comercial de IMU: recibe quaternions
(w, x, y, z), aplica calibración sensor-segmento conocida y reconstruye la
posición de la muñeca con las longitudes de brazo y antebrazo.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterable, Tuple

Vector3 = Tuple[float, float, float]
Quaternion = Tuple[float, float, float, float]
Matrix3 = Tuple[
    Tuple[float, float, float],
    Tuple[float, float, float],
    Tuple[float, float, float],
]

IDENTITY_Q: Quaternion = (1.0, 0.0, 0.0, 0.0)


@dataclass(frozen=True)
class OrientationSample:
    """Orientación de una IMU en un instante dado."""

    sensor_id: str
    timestamp_s: float
    quaternion_n_s: Quaternion
    valid: bool = True


@dataclass(frozen=True)
class SegmentCalibration:
    """Rotaciones conocidas para expresar un segmento en el frame humano.

    q_h_n: frame de navegación de la IMU -> frame humano H.
    q_s_b: frame del segmento corporal B -> frame del sensor S.

    La orientación final del segmento es q_h_b = q_h_n * q_n_s * q_s_b.
    """

    q_h_n: Quaternion = IDENTITY_Q
    q_s_b: Quaternion = IDENTITY_Q


@dataclass(frozen=True)
class UpperLimbModel:
    upper_arm_length_m: float
    forearm_length_m: float

    def __post_init__(self) -> None:
        if self.upper_arm_length_m <= 0.0:
            raise ValueError("upper_arm_length_m debe ser mayor que cero")
        if self.forearm_length_m <= 0.0:
            raise ValueError("forearm_length_m debe ser mayor que cero")


@dataclass(frozen=True)
class HandPoseEstimate:
    timestamp_s: float
    position_h_m: Vector3
    orientation_h_wxyz: Quaternion
    elbow_position_h_m: Vector3
    sensor_time_skew_s: float
    valid: bool


def _as_quaternion(values: Iterable[float]) -> Quaternion:
    q = tuple(float(v) for v in values)
    if len(q) != 4:
        raise ValueError("Un quaternion debe contener 4 componentes (w, x, y, z)")
    return q  # type: ignore[return-value]


def normalize_quaternion(q: Quaternion) -> Quaternion:
    q = _as_quaternion(q)
    norm = sqrt(sum(component * component for component in q))
    if norm == 0.0:
        raise ValueError("No se puede normalizar un quaternion de norma cero")
    return tuple(component / norm for component in q)  # type: ignore[return-value]


def quaternion_multiply(q1: Quaternion, q2: Quaternion) -> Quaternion:
    w1, x1, y1, z1 = normalize_quaternion(q1)
    w2, x2, y2, z2 = normalize_quaternion(q2)
    return normalize_quaternion(
        (
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        )
    )


def quaternion_to_matrix(q: Quaternion) -> Matrix3:
    w, x, y, z = normalize_quaternion(q)
    return (
        (1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)),
        (2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w)),
        (2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y)),
    )


def rotate_vector(q: Quaternion, vector: Vector3) -> Vector3:
    matrix = quaternion_to_matrix(q)
    x, y, z = vector
    return (
        matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z,
        matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z,
        matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z,
    )


def calibrated_segment_orientation(
    sample: OrientationSample,
    calibration: SegmentCalibration,
) -> Quaternion:
    if not sample.valid:
        raise ValueError(f"Muestra inválida para {sample.sensor_id}")
    return quaternion_multiply(
        quaternion_multiply(calibration.q_h_n, sample.quaternion_n_s),
        calibration.q_s_b,
    )


def _add(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def estimate_hand_pose(
    upper_arm: OrientationSample,
    forearm: OrientationSample,
    hand: OrientationSample,
    upper_arm_calibration: SegmentCalibration,
    forearm_calibration: SegmentCalibration,
    hand_calibration: SegmentCalibration,
    model: UpperLimbModel,
) -> HandPoseEstimate:
    """Reconstruye posición de muñeca y orientación de mano en el frame H."""

    samples = (upper_arm, forearm, hand)
    if not all(sample.valid for sample in samples):
        raise ValueError("Las tres muestras deben ser válidas")

    q_h_u = calibrated_segment_orientation(upper_arm, upper_arm_calibration)
    q_h_f = calibrated_segment_orientation(forearm, forearm_calibration)
    q_h_m = calibrated_segment_orientation(hand, hand_calibration)

    upper_arm_vector = rotate_vector(q_h_u, (model.upper_arm_length_m, 0.0, 0.0))
    forearm_vector = rotate_vector(q_h_f, (model.forearm_length_m, 0.0, 0.0))

    elbow = upper_arm_vector
    wrist = _add(elbow, forearm_vector)

    timestamps = tuple(sample.timestamp_s for sample in samples)
    skew = max(timestamps) - min(timestamps)

    return HandPoseEstimate(
        timestamp_s=max(timestamps),
        position_h_m=wrist,
        orientation_h_wxyz=q_h_m,
        elbow_position_h_m=elbow,
        sensor_time_skew_s=skew,
        valid=True,
    )
