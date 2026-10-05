"""Cinemática directa del manipulador 6R.

Convención DH estándar v0.1:
i | theta_i       | d_i | a_i | alpha_i
1 | q1            | 0   | 0   | +pi/2
2 | q2            | 0   | L1  | 0
3 | q3 + pi/2     | 0   | 0   | +pi/2
4 | q4            | L2  | 0   | -pi/2
5 | q5            | 0   | 0   | +pi/2
6 | q6            | 0   | 0   | 0

El TCP se coloca a una distancia LT sobre +z6.
"""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np

from .model_6r import RobotGeometry


def _dh(theta: float, d: float, a: float, alpha: float) -> np.ndarray:
    ct = math.cos(theta)
    st = math.sin(theta)
    ca = math.cos(alpha)
    sa = math.sin(alpha)
    return np.array(
        [
            [ct, -st * ca, st * sa, a * ct],
            [st, ct * ca, -ct * sa, a * st],
            [0.0, sa, ca, d],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def rpy_zyx_to_rotation(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """Convierte roll-pitch-yaw a R usando Rz(yaw) @ Ry(pitch) @ Rx(roll).

    Los argumentos se expresan en radianes.
    """
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)

    rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]], dtype=float)
    ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]], dtype=float)
    rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]], dtype=float)
    return rz @ ry @ rx


def rotation_to_rpy_zyx(rotation: np.ndarray, eps: float = 1e-9) -> np.ndarray:
    """Convierte una matriz R a roll-pitch-yaw ZYX.

    En gimbal lock devuelve una representación válida fijando yaw=0.
    """
    r = np.asarray(rotation, dtype=float)
    if r.shape != (3, 3):
        raise ValueError("rotation debe ser una matriz 3x3.")

    sp = -float(r[2, 0])
    sp = max(-1.0, min(1.0, sp))
    pitch = math.asin(sp)

    cp = math.cos(pitch)
    if abs(cp) > eps:
        roll = math.atan2(r[2, 1], r[2, 2])
        yaw = math.atan2(r[1, 0], r[0, 0])
    else:
        roll = math.atan2(-r[0, 1], r[1, 1])
        yaw = 0.0

    return np.array([roll, pitch, yaw], dtype=float)


def forward_kinematics(
    q: Iterable[float],
    geometry: RobotGeometry,
) -> dict[str, object]:
    """Calcula FK completa y puntos clave.

    Parameters
    ----------
    q:
        Seis ángulos articulares [rad].
    geometry:
        L1, L2 y LT.

    Returns
    -------
    dict
        Incluye T_tcp, R_tcp, p_tcp, transformaciones acumuladas y puntos
        hombro-codo-muñeca-TCP para visualización.
    """
    q_arr = np.asarray(list(q), dtype=float)
    if q_arr.shape != (6,):
        raise ValueError("q debe contener exactamente 6 ángulos.")

    q1, q2, q3, q4, q5, q6 = q_arr
    l1, l2, lt = geometry.l1, geometry.l2, geometry.lt

    a_mats = [
        _dh(q1, 0.0, 0.0, math.pi / 2.0),
        _dh(q2, 0.0, l1, 0.0),
        _dh(q3 + math.pi / 2.0, 0.0, 0.0, math.pi / 2.0),
        _dh(q4, l2, 0.0, -math.pi / 2.0),
        _dh(q5, 0.0, 0.0, math.pi / 2.0),
        _dh(q6, 0.0, 0.0, 0.0),
    ]

    transforms = [np.eye(4, dtype=float)]
    current = transforms[0]
    for a_i in a_mats:
        current = current @ a_i
        transforms.append(current.copy())

    t_tool = np.eye(4, dtype=float)
    t_tool[2, 3] = lt
    t_tcp = transforms[-1] @ t_tool

    shoulder = transforms[0][:3, 3].copy()
    elbow = transforms[2][:3, 3].copy()
    wrist = transforms[4][:3, 3].copy()
    tcp = t_tcp[:3, 3].copy()

    return {
        "q": q_arr,
        "A": a_mats,
        "T": transforms,
        "T_tcp": t_tcp,
        "R_tcp": t_tcp[:3, :3].copy(),
        "p_tcp": tcp,
        "p_wrist": wrist,
        "key_points": np.vstack([shoulder, elbow, wrist, tcp]),
    }


def position_error(target: np.ndarray, actual: np.ndarray) -> float:
    return float(np.linalg.norm(np.asarray(target) - np.asarray(actual)))


def orientation_error_angle(target: np.ndarray, actual: np.ndarray) -> float:
    """Error angular mínimo entre dos orientaciones, en radianes."""
    r_err = np.asarray(target).T @ np.asarray(actual)
    value = (float(np.trace(r_err)) - 1.0) / 2.0
    value = max(-1.0, min(1.0, value))
    return math.acos(value)
