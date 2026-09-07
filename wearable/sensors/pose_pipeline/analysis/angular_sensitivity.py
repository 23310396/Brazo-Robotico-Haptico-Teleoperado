"""V1: sensibilidad de la pose reconstruida a errores angulares sintéticos.

Este archivo NO supone que una IMU real tenga estos errores. Los ángulos usados
son escenarios controlados para entender cuánto error cartesiano puede producir
una orientación incorrecta en cada segmento.

Se puede ejecutar desde la raíz del repositorio con:

    python wearable/sensors/pose_pipeline/analysis/angular_sensitivity.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from math import acos, degrees, sqrt
from pathlib import Path
from typing import Iterable

# Permite usar el botón Run de Codespaces aunque el archivo se ejecute directo.
if __package__ in (None, ""):
    repo_root = Path(__file__).resolve().parents[4]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from wearable.sensors.pose_pipeline.pipeline import (
    IDENTITY_Q,
    Quaternion,
    SegmentCalibration,
    UpperLimbModel,
    estimate_hand_pose,
)
from wearable.sensors.pose_pipeline.synthetic import (
    quaternion_from_axis_angle,
    synthetic_sample,
)


L_BRAZO_M = 0.30
L_ANTEBRAZO_M = 0.25
ANGULOS_PRUEBA_DEG = (0.5, 1.0, 2.0, 5.0, 10.0)
EJE_ERROR = (0.0, 0.0, 1.0)

MODELO = UpperLimbModel(L_BRAZO_M, L_ANTEBRAZO_M)
CALIBRACION_IDEAL = SegmentCalibration()


@dataclass(frozen=True)
class SensitivityResult:
    target: str
    injected_error_deg: float
    position_error_m: float
    orientation_error_deg: float


def vector_distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def quaternion_angular_distance_deg(q1: Quaternion, q2: Quaternion) -> float:
    """Ángulo mínimo entre dos orientaciones representadas por quaternions."""
    dot = abs(sum(a * b for a, b in zip(q1, q2)))
    dot = max(-1.0, min(1.0, dot))
    return degrees(2.0 * acos(dot))


def _pose(q_upper: Quaternion, q_fore: Quaternion, q_hand: Quaternion):
    return estimate_hand_pose(
        synthetic_sample("brazo", q_upper),
        synthetic_sample("antebrazo", q_fore),
        synthetic_sample("mano", q_hand),
        CALIBRACION_IDEAL,
        CALIBRACION_IDEAL,
        CALIBRACION_IDEAL,
        MODELO,
    )


def evaluate_angular_error(target: str, angle_deg: float) -> SensitivityResult:
    """Inyecta un error conocido en una o varias orientaciones.

    target:
        - "brazo"
        - "antebrazo"
        - "brazo+antebrazo"
        - "mano"
    """
    q_error = quaternion_from_axis_angle(EJE_ERROR, angle_deg)

    q_upper = IDENTITY_Q
    q_fore = IDENTITY_Q
    q_hand = IDENTITY_Q

    if target == "brazo":
        q_upper = q_error
    elif target == "antebrazo":
        q_fore = q_error
    elif target == "brazo+antebrazo":
        q_upper = q_error
        q_fore = q_error
    elif target == "mano":
        q_hand = q_error
    else:
        raise ValueError(f"Objetivo de error no reconocido: {target}")

    ideal = _pose(IDENTITY_Q, IDENTITY_Q, IDENTITY_Q)
    perturbed = _pose(q_upper, q_fore, q_hand)

    return SensitivityResult(
        target=target,
        injected_error_deg=angle_deg,
        position_error_m=vector_distance(ideal.position_h_m, perturbed.position_h_m),
        orientation_error_deg=quaternion_angular_distance_deg(
            ideal.orientation_h_wxyz,
            perturbed.orientation_h_wxyz,
        ),
    )


def run_sweep(target: str, angles_deg: Iterable[float] = ANGULOS_PRUEBA_DEG) -> list[SensitivityResult]:
    return [evaluate_angular_error(target, angle) for angle in angles_deg]


def _print_case(target: str, descripcion: str) -> None:
    print("\n" + "=" * 78)
    print(f"CASO: {descripcion}")
    print("=" * 78)

    print("TENEMOS:")
    print(f"  Longitud de brazo:      {L_BRAZO_M:.2f} m")
    print(f"  Longitud de antebrazo:  {L_ANTEBRAZO_M:.2f} m")
    print("  Pose ideal: brazo y antebrazo extendidos hacia +X")
    print("  Eje del error sintético: Z")
    print(f"  Errores probados: {', '.join(f'{a:g}°' for a in ANGULOS_PRUEBA_DEG)}")

    print("\nCALCULAMOS:")
    print("  1. Pose ideal de la muñeca.")
    print(f"  2. Sumamos un error angular únicamente en: {target}.")
    print("  3. Volvemos a reconstruir la pose.")
    print("  4. Medimos la distancia entre muñeca ideal y muñeca perturbada.")
    print("  5. Medimos también el error de orientación final de la mano.")

    print("\nOBTENEMOS:")
    print("  Error angular | Error posición muñeca | Error orientación mano")
    print("  ------------- | --------------------- | ----------------------")
    for result in run_sweep(target):
        print(
            f"  {result.injected_error_deg:>11.1f}° | "
            f"{result.position_error_m * 1000:>18.3f} mm | "
            f"{result.orientation_error_deg:>19.3f}°"
        )


def main() -> None:
    print("\nV1 - SENSIBILIDAD ANGULAR DEL PIPELINE")
    print("Los valores de error son SINTÉTICOS y sirven para estudiar sensibilidad.")
    print("No representan especificaciones de una IMU real ni límites aceptados.")

    _print_case(
        "brazo",
        "error únicamente en la orientación del brazo",
    )
    _print_case(
        "antebrazo",
        "error únicamente en la orientación del antebrazo",
    )
    _print_case(
        "brazo+antebrazo",
        "el mismo error angular afecta brazo y antebrazo",
    )
    _print_case(
        "mano",
        "error únicamente en la orientación de la mano",
    )

    print("\n" + "=" * 78)
    print("LECTURA DEL RESULTADO")
    print("=" * 78)
    print("- Error en brazo/antebrazo puede convertirse en error de posición de muñeca.")
    print("- Si ambos segmentos comparten el error, el desplazamiento puede ser mayor.")
    print("- Error sólo en la mano no mueve la muñeca en este modelo, pero sí cambia")
    print("  directamente la orientación que después recibiría el mapping del robot.")
    print("- Todavía NO definimos qué error es aceptable para la tesis.")


if __name__ == "__main__":
    main()
