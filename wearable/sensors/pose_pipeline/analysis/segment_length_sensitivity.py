"""Sensibilidad del pipeline a errores en las longitudes del brazo y antebrazo.

La reconstrucción geométrica usa longitudes de segmento medidas físicamente. Si
esas longitudes se introducen con error, la orientación puede ser perfecta y aun
así la posición de codo/muñeca quedar desplazada.

Los errores usados aquí son escenarios sintéticos y no representan todavía una
incertidumbre real de medición del usuario.

Ejecutar desde la raíz del repositorio:

    python wearable/sensors/pose_pipeline/analysis/segment_length_sensitivity.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

if __package__ in (None, ""):
    repo_root = Path(__file__).resolve().parents[4]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from wearable.sensors.pose_pipeline.analysis.angular_sensitivity import vector_distance
from wearable.sensors.pose_pipeline.pipeline import (
    SegmentCalibration,
    UpperLimbModel,
    estimate_hand_pose,
    quaternion_multiply,
)
from wearable.sensors.pose_pipeline.synthetic import quaternion_from_axis_angle, synthetic_sample


L_BRAZO_REAL_M = 0.30
L_ANTEBRAZO_REAL_M = 0.25
CALIBRACION_IDEAL = SegmentCalibration()
EJE_X = (1.0, 0.0, 0.0)
EJE_Y = (0.0, 1.0, 0.0)
EJE_Z = (0.0, 0.0, 1.0)
ERRORES_LONGITUD_MM = (-20.0, -10.0, -5.0, 0.0, 5.0, 10.0, 20.0)


@dataclass(frozen=True)
class LengthSensitivityResult:
    upper_error_mm: float
    forearm_error_mm: float
    elbow_error_mm: float
    wrist_error_mm: float


def _compose_xyz(x_deg: float, y_deg: float, z_deg: float):
    qx = quaternion_from_axis_angle(EJE_X, x_deg)
    qy = quaternion_from_axis_angle(EJE_Y, y_deg)
    qz = quaternion_from_axis_angle(EJE_Z, z_deg)
    return quaternion_multiply(quaternion_multiply(qz, qy), qx)


def _orientations():
    # Pose 3D sintética no colineal para evitar que ambos errores de longitud se sumen trivialmente.
    return (
        _compose_xyz(10.0, -20.0, 30.0),
        _compose_xyz(-15.0, 25.0, 70.0),
        _compose_xyz(20.0, -10.0, 45.0),
    )


def _pose(model: UpperLimbModel):
    q_upper, q_fore, q_hand = _orientations()
    return estimate_hand_pose(
        synthetic_sample("brazo", q_upper),
        synthetic_sample("antebrazo", q_fore),
        synthetic_sample("mano", q_hand),
        CALIBRACION_IDEAL,
        CALIBRACION_IDEAL,
        CALIBRACION_IDEAL,
        model,
    )


def evaluate_length_error(upper_error_mm: float, forearm_error_mm: float) -> LengthSensitivityResult:
    estimated_upper_m = L_BRAZO_REAL_M + upper_error_mm / 1000.0
    estimated_forearm_m = L_ANTEBRAZO_REAL_M + forearm_error_mm / 1000.0

    if estimated_upper_m <= 0.0 or estimated_forearm_m <= 0.0:
        raise ValueError("Las longitudes estimadas deben permanecer positivas")

    ideal = _pose(UpperLimbModel(L_BRAZO_REAL_M, L_ANTEBRAZO_REAL_M))
    reconstructed = _pose(UpperLimbModel(estimated_upper_m, estimated_forearm_m))

    return LengthSensitivityResult(
        upper_error_mm=upper_error_mm,
        forearm_error_mm=forearm_error_mm,
        elbow_error_mm=vector_distance(ideal.elbow_position_h_m, reconstructed.elbow_position_h_m) * 1000.0,
        wrist_error_mm=vector_distance(ideal.position_h_m, reconstructed.position_h_m) * 1000.0,
    )


def main() -> None:
    print("\nV1 - SENSIBILIDAD A LONGITUDES DE SEGMENTOS")
    print("Los errores de longitud son SINTÉTICOS; no son mediciones reales del operador.")

    print("\nTENEMOS:")
    print(f"  Longitud real sintética de brazo:     {L_BRAZO_REAL_M * 1000:.1f} mm")
    print(f"  Longitud real sintética de antebrazo: {L_ANTEBRAZO_REAL_M * 1000:.1f} mm")
    print("  Las orientaciones son correctas y se mantiene una pose 3D fija.")

    print("\nCALCULAMOS:")
    print("  1. Pose ideal con longitudes reales.")
    print("  2. Pose usando longitudes medidas con error.")
    print("  3. Error de posición de codo y muñeca.")

    print("\nOBTENEMOS — ERROR SÓLO EN LONGITUD DE BRAZO:")
    print("  Error longitud | Error codo | Error muñeca")
    print("  -------------- | ---------- | ------------")
    for error_mm in ERRORES_LONGITUD_MM:
        result = evaluate_length_error(error_mm, 0.0)
        print(f"  {error_mm:>9.1f} mm | {result.elbow_error_mm:>8.3f} mm | {result.wrist_error_mm:>10.3f} mm")

    print("\nOBTENEMOS — ERROR SÓLO EN LONGITUD DE ANTEBRAZO:")
    print("  Error longitud | Error codo | Error muñeca")
    print("  -------------- | ---------- | ------------")
    for error_mm in ERRORES_LONGITUD_MM:
        result = evaluate_length_error(0.0, error_mm)
        print(f"  {error_mm:>9.1f} mm | {result.elbow_error_mm:>8.3f} mm | {result.wrist_error_mm:>10.3f} mm")

    print("\nLECTURA DEL RESULTADO:")
    print("- El error de longitud del brazo desplaza codo y muñeca aunque las IMUs sean perfectas.")
    print("- El error de longitud del antebrazo no mueve el codo, pero sí desplaza la muñeca.")
    print("- La orientación de mano no depende de estas longitudes en la arquitectura actual.")
    print("- En hardware real necesitaremos un procedimiento reproducible para medir longitudes de segmento.")


if __name__ == "__main__":
    main()
