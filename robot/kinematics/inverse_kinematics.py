"""Cinemática inversa analítica v0.1 del manipulador 6R."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np

from .forward_kinematics import forward_kinematics, orientation_error_angle
from .model_6r import RobotGeometry


@dataclass
class IKSolution:
    q: np.ndarray
    elbow_branch: str
    wrist_branch: str
    position_error: float
    orientation_error: float
    wrist_singularity: bool
    shoulder_singularity: bool
    within_limits: bool = True

    @property
    def valid(self) -> bool:
        return self.within_limits


def wrap_to_pi(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def _wrap_q(q: Iterable[float]) -> np.ndarray:
    return np.array([wrap_to_pi(float(v)) for v in q], dtype=float)


def _r03(q1: float, q2: float, q3: float) -> np.ndarray:
    s23 = math.sin(q2 + q3)
    c23 = math.cos(q2 + q3)
    s1 = math.sin(q1)
    c1 = math.cos(q1)
    return np.array(
        [
            [-s23 * c1, s1, c1 * c23],
            [-s1 * s23, -c1, s1 * c23],
            [c23, 0.0, s23],
        ],
        dtype=float,
    )


def _within_limits(q: np.ndarray, joint_limits_rad: np.ndarray | None) -> bool:
    if joint_limits_rad is None:
        return True
    limits = np.asarray(joint_limits_rad, dtype=float)
    if limits.shape != (6, 2):
        raise ValueError("joint_limits_rad debe tener forma (6, 2).")
    return bool(np.all(q >= limits[:, 0]) and np.all(q <= limits[:, 1]))


def inverse_kinematics(
    target_transform: np.ndarray,
    geometry: RobotGeometry,
    *,
    q_current: Iterable[float] | None = None,
    joint_limits_rad: np.ndarray | None = None,
    eps: float = 1e-9,
    reach_tol: float = 1e-9,
) -> dict[str, object]:
    """Resuelve la IK analítica para la rama frontal de hombro.

    Genera elbow-up/down y wrist-normal/flip. En singularidad de muñeca
    conserva q4 actual cuando se dispone de q_current.
    """
    target = np.asarray(target_transform, dtype=float)
    if target.shape != (4, 4):
        raise ValueError("target_transform debe ser una matriz 4x4.")

    r_d = target[:3, :3]
    p_d = target[:3, 3]

    if not np.allclose(r_d.T @ r_d, np.eye(3), atol=1e-7):
        raise ValueError("La orientación objetivo no es una matriz de rotación ortonormal.")
    if not math.isclose(float(np.linalg.det(r_d)), 1.0, abs_tol=1e-7):
        raise ValueError("La orientación objetivo debe tener determinante +1.")

    current = np.zeros(6, dtype=float) if q_current is None else np.asarray(list(q_current), dtype=float)
    if current.shape != (6,):
        raise ValueError("q_current debe contener 6 ángulos.")

    p_w = p_d - geometry.lt * r_d[:, 2]
    x_w, y_w, z_w = (float(v) for v in p_w)
    radial = math.hypot(x_w, y_w)

    shoulder_singularity = radial < eps
    q1 = float(current[0]) if shoulder_singularity else math.atan2(y_w, x_w)

    l1, l2 = geometry.l1, geometry.l2
    d_cos = (radial * radial + z_w * z_w - l1 * l1 - l2 * l2) / (2.0 * l1 * l2)

    if d_cos > 1.0 + reach_tol or d_cos < -1.0 - reach_tol:
        return {
            "status": "UNREACHABLE",
            "reason": "El centro de muñeca queda fuera del alcance geométrico de L1 y L2.",
            "p_wrist_target": p_w,
            "solutions": [],
        }

    d_cos = max(-1.0, min(1.0, d_cos))
    sin_abs = math.sqrt(max(0.0, 1.0 - d_cos * d_cos))
    solutions: list[IKSolution] = []

    for elbow_sign, elbow_name in ((1.0, "elbow+"), (-1.0, "elbow-")):
        q3 = math.atan2(elbow_sign * sin_abs, d_cos)
        q2 = math.atan2(z_w, radial) - math.atan2(
            l2 * math.sin(q3),
            l1 + l2 * math.cos(q3),
        )

        r_w = _r03(q1, q2, q3).T @ r_d
        s5_abs = math.hypot(float(r_w[0, 2]), float(r_w[1, 2]))
        wrist_singularity = s5_abs < eps
        wrist_candidates: list[tuple[float, float, float, str]] = []

        if not wrist_singularity:
            q5 = math.atan2(s5_abs, float(r_w[2, 2]))
            q4 = math.atan2(float(r_w[1, 2]), float(r_w[0, 2]))
            q6 = math.atan2(float(r_w[2, 1]), -float(r_w[2, 0]))
            wrist_candidates.append((q4, q5, q6, "wrist+"))
            wrist_candidates.append((q4 + math.pi, -q5, q6 + math.pi, "wrist-flip"))
        else:
            q4 = float(current[3])
            if float(r_w[2, 2]) >= 0.0:
                q5 = 0.0
                phi = math.atan2(float(r_w[1, 0]), float(r_w[0, 0]))
                q6 = phi - q4
            else:
                q5 = math.pi
                delta = math.atan2(-float(r_w[1, 0]), -float(r_w[0, 0]))
                q6 = q4 - delta
            wrist_candidates.append((q4, q5, q6, "wrist-singular"))

        for q4, q5, q6, wrist_name in wrist_candidates:
            q = _wrap_q([q1, q2, q3, q4, q5, q6])
            fk = forward_kinematics(q, geometry)
            p_err = float(np.linalg.norm(fk["p_tcp"] - p_d))
            r_err = orientation_error_angle(r_d, fk["R_tcp"])
            within = _within_limits(q, joint_limits_rad)
            solutions.append(
                IKSolution(
                    q=q,
                    elbow_branch=elbow_name,
                    wrist_branch=wrist_name,
                    position_error=p_err,
                    orientation_error=r_err,
                    wrist_singularity=wrist_singularity,
                    shoulder_singularity=shoulder_singularity,
                    within_limits=within,
                )
            )

    unique: list[IKSolution] = []
    for candidate in solutions:
        is_duplicate = any(
            np.linalg.norm(
                np.array([wrap_to_pi(a - b) for a, b in zip(candidate.q, existing.q)])
            ) < 1e-8
            for existing in unique
        )
        if not is_duplicate:
            unique.append(candidate)

    status = "OK" if any(s.valid for s in unique) else "NO_VALID_SOLUTION"
    return {
        "status": status,
        "reason": None if status == "OK" else "Las soluciones geométricas violan los límites configurados.",
        "p_wrist_target": p_w,
        "solutions": unique,
    }
