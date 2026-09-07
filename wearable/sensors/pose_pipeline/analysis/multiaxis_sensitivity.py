"""Sensibilidad 3D del pipeline a errores angulares por eje.

Este análisis amplía las pruebas previas, que se concentraron principalmente en
perturbaciones alrededor de Z. Aquí se usa una pose espacial no trivial y se
inyectan errores locales alrededor de X, Y, Z y un eje diagonal.

Los errores son escenarios sintéticos; no representan especificaciones de una
IMU real ni criterios de aceptación del proyecto.

Ejecutar desde la raíz del repositorio:

    python wearable/sensors/pose_pipeline/analysis/multiaxis_sensitivity.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

if __package__ in (None, ""):
    repo_root = Path(__file__).resolve().parents[4]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from wearable.sensors.pose_pipeline.analysis.angular_sensitivity import (
    quaternion_angular_distance_deg,
    vector_distance,
)
from wearable.sensors.pose_pipeline.pipeline import (
    Quaternion,
    SegmentCalibration,
    UpperLimbModel,
    estimate_hand_pose,
    quaternion_multiply,
)
from wearable.sensors.pose_pipeline.synthetic import (
    quaternion_from_axis_angle,
    synthetic_sample,
)


L_BRAZO_M = 0.30
L_ANTEBRAZO_M = 0.25
MODELO = UpperLimbModel(L_BRAZO_M, L_ANTEBRAZO_M)
CALIBRACION_IDEAL = SegmentCalibration()

EJES = {
    "x": (1.0, 0.0, 0.0),
    "y": (0.0, 1.0, 0.0),
    "z": (0.0, 0.0, 1.0),
    "diagonal": (1.0, 1.0, 1.0),
}
ANGULOS_PRUEBA_DEG = (1.0, 2.0, 5.0)


@dataclass(frozen=True)
class MultiAxisResult:
    target: str
    axis_name: str
    injected_error_deg: float
    position_error_mm: float
    orientation_error_deg: float


def _compose_xyz(x_deg: float, y_deg: float, z_deg: float) -> Quaternion:
    """Compone una orientación 3D no trivial para los casos sintéticos."""
    qx = quaternion_from_axis_angle(EJES["x"], x_deg)
    qy = quaternion_from_axis_angle(EJES["y"], y_deg)
    qz = quaternion_from_axis_angle(EJES["z"], z_deg)
    return quaternion_multiply(quaternion_multiply(qz, qy), qx)


def _real_orientations() -> tuple[Quaternion, Quaternion, Quaternion]:
    return (
        _compose_xyz(15.0, -20.0, 30.0),
        _compose_xyz(-10.0, 25.0, 55.0),
        _compose_xyz(20.0, -15.0, 40.0),
    )


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


def evaluate_multiaxis_error(target: str, axis_name: str, error_deg: float) -> MultiAxisResult:
    if target not in {"brazo", "antebrazo", "mano"}:
        raise ValueError(f"Objetivo no reconocido: {target}")
    if axis_name not in EJES:
        raise ValueError(f"Eje no reconocido: {axis_name}")

    q_upper_real, q_fore_real, q_hand_real = _real_orientations()
    ideal = _pose(q_upper_real, q_fore_real, q_hand_real)

    q_error = quaternion_from_axis_angle(EJES[axis_name], error_deg)
    q_upper = q_upper_real
    q_fore = q_fore_real
    q_hand = q_hand_real

    # Postmultiplicar modela aquí un error expresado respecto al frame local del sensor/segmento.
    if target == "brazo":
        q_upper = quaternion_multiply(q_upper_real, q_error)
    elif target == "antebrazo":
        q_fore = quaternion_multiply(q_fore_real, q_error)
    else:
        q_hand = quaternion_multiply(q_hand_real, q_error)

    reconstructed = _pose(q_upper, q_fore, q_hand)

    return MultiAxisResult(
        target=target,
        axis_name=axis_name,
        injected_error_deg=error_deg,
        position_error_mm=vector_distance(ideal.position_h_m, reconstructed.position_h_m) * 1000.0,
        orientation_error_deg=quaternion_angular_distance_deg(
            ideal.orientation_h_wxyz,
            reconstructed.orientation_h_wxyz,
        ),
    )


def run_sweep(
    target: str,
    angle_deg: float = 5.0,
    axes: Iterable[str] = EJES.keys(),
) -> list[MultiAxisResult]:
    return [evaluate_multiaxis_error(target, axis_name, angle_deg) for axis_name in axes]


def main() -> None:
    print("\nV1 - SENSIBILIDAD ESPACIAL / MULTIEJE DEL PIPELINE")
    print("Los errores son SINTÉTICOS y se aplican en el frame local del segmento.")

    print("\nTENEMOS:")
    print("  Una pose 3D no trivial de brazo, antebrazo y mano.")
    print("  Inyectamos el mismo error alrededor de X, Y, Z y un eje diagonal.")
    print("  X local coincide con el eje longitudinal usado por el modelo geométrico.")

    print("\nCALCULAMOS:")
    print("  1. Pose ideal 3D.")
    print("  2. Pose con una perturbación local de 5° en un solo segmento.")
    print("  3. Error de posición de muñeca y orientación de mano.")

    for target in ("brazo", "antebrazo", "mano"):
        print(f"\nOBTENEMOS — {target.upper()}:")
        print("  Eje      | Error posición | Error orientación")
        print("  -------- | -------------- | -----------------")
        for result in run_sweep(target):
            print(
                f"  {result.axis_name:<8} | "
                f"{result.position_error_mm:>11.3f} mm | "
                f"{result.orientation_error_deg:>14.3f}°"
            )

    print("\nLECTURA DEL RESULTADO:")
    print("- El pipeline no debe validarse sólo con giros en un plano.")
    print("- Un giro local alrededor del eje longitudinal X de brazo/antebrazo no desplaza su extremo en este modelo.")
    print("- Errores alrededor de Y/Z o ejes compuestos sí pueden desplazar la muñeca.")
    print("- Cualquier error angular en la IMU de mano aparece como error de orientación de salida.")
    print("- Esto caracteriza geometría 3D; no define todavía precisión aceptable de una IMU real.")


if __name__ == "__main__":
    main()
