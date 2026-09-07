"""V1: sensibilidad de la pose a errores residuales de calibración sensor-segmento.

Este análisis separa dos cosas:

1. La IMU puede estar montada con un offset físico respecto al segmento.
2. La calibración intenta estimar y compensar ese offset.

Si la compensación es exacta, el montaje chueco no introduce error residual.
Si la compensación es imperfecta, queda un error angular que se propaga a la
posición de muñeca o a la orientación de mano.

Ejecutar desde la raíz del repositorio:

    python wearable/sensors/pose_pipeline/analysis/calibration_sensitivity.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# Permite usar el botón Run de Codespaces aunque el archivo se ejecute directo.
if __package__ in (None, ""):
    repo_root = Path(__file__).resolve().parents[4]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from wearable.sensors.pose_pipeline.analysis.angular_sensitivity import (
    quaternion_angular_distance_deg,
    vector_distance,
)
from wearable.sensors.pose_pipeline.pipeline import (
    IDENTITY_Q,
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
EJE_Z = (0.0, 0.0, 1.0)
OFFSET_MONTAJE_REAL_DEG = 10.0
ERRORES_RESIDUALES_DEG = (0.0, 0.5, 1.0, 2.0, 5.0)

# Pose real elegida sólo para hacer la demo fácil de leer.
ANGULO_BRAZO_REAL_DEG = 0.0
ANGULO_ANTEBRAZO_REAL_DEG = 45.0
ANGULO_MANO_REAL_DEG = 30.0

MODELO = UpperLimbModel(L_BRAZO_M, L_ANTEBRAZO_M)
CALIBRACION_IDEAL = SegmentCalibration()


@dataclass(frozen=True)
class CalibrationSensitivityResult:
    target: str
    true_segment_angle_deg: float
    true_mount_offset_deg: float
    estimated_mount_offset_deg: float
    residual_calibration_error_deg: float
    position_error_m: float
    orientation_error_deg: float


def _real_orientations():
    return (
        quaternion_from_axis_angle(EJE_Z, ANGULO_BRAZO_REAL_DEG),
        quaternion_from_axis_angle(EJE_Z, ANGULO_ANTEBRAZO_REAL_DEG),
        quaternion_from_axis_angle(EJE_Z, ANGULO_MANO_REAL_DEG),
    )


def _ideal_pose():
    q_upper, q_fore, q_hand = _real_orientations()
    return estimate_hand_pose(
        synthetic_sample("brazo", q_upper),
        synthetic_sample("antebrazo", q_fore),
        synthetic_sample("mano", q_hand),
        CALIBRACION_IDEAL,
        CALIBRACION_IDEAL,
        CALIBRACION_IDEAL,
        MODELO,
    )


def evaluate_calibration_error(
    target: str,
    true_mount_offset_deg: float,
    estimated_mount_offset_deg: float,
) -> CalibrationSensitivityResult:
    """Simula montaje físico + compensación estimada para un solo segmento."""

    q_upper_real, q_fore_real, q_hand_real = _real_orientations()
    q_mount = quaternion_from_axis_angle(EJE_Z, true_mount_offset_deg)
    q_correction_est = quaternion_from_axis_angle(EJE_Z, -estimated_mount_offset_deg)

    q_upper_measured = q_upper_real
    q_fore_measured = q_fore_real
    q_hand_measured = q_hand_real

    upper_cal = CALIBRACION_IDEAL
    fore_cal = CALIBRACION_IDEAL
    hand_cal = CALIBRACION_IDEAL

    if target == "brazo":
        q_upper_measured = quaternion_multiply(q_upper_real, q_mount)
        upper_cal = SegmentCalibration(q_s_b=q_correction_est)
        true_segment_angle_deg = ANGULO_BRAZO_REAL_DEG
    elif target == "antebrazo":
        q_fore_measured = quaternion_multiply(q_fore_real, q_mount)
        fore_cal = SegmentCalibration(q_s_b=q_correction_est)
        true_segment_angle_deg = ANGULO_ANTEBRAZO_REAL_DEG
    elif target == "mano":
        q_hand_measured = quaternion_multiply(q_hand_real, q_mount)
        hand_cal = SegmentCalibration(q_s_b=q_correction_est)
        true_segment_angle_deg = ANGULO_MANO_REAL_DEG
    else:
        raise ValueError(f"Objetivo de calibración no reconocido: {target}")

    reconstructed = estimate_hand_pose(
        synthetic_sample("brazo", q_upper_measured),
        synthetic_sample("antebrazo", q_fore_measured),
        synthetic_sample("mano", q_hand_measured),
        upper_cal,
        fore_cal,
        hand_cal,
        MODELO,
    )
    ideal = _ideal_pose()

    residual = true_mount_offset_deg - estimated_mount_offset_deg

    return CalibrationSensitivityResult(
        target=target,
        true_segment_angle_deg=true_segment_angle_deg,
        true_mount_offset_deg=true_mount_offset_deg,
        estimated_mount_offset_deg=estimated_mount_offset_deg,
        residual_calibration_error_deg=residual,
        position_error_m=vector_distance(ideal.position_h_m, reconstructed.position_h_m),
        orientation_error_deg=quaternion_angular_distance_deg(
            ideal.orientation_h_wxyz,
            reconstructed.orientation_h_wxyz,
        ),
    )


def run_residual_sweep(
    target: str,
    residual_errors_deg: Iterable[float] = ERRORES_RESIDUALES_DEG,
) -> list[CalibrationSensitivityResult]:
    results = []
    for residual in residual_errors_deg:
        estimated_offset = OFFSET_MONTAJE_REAL_DEG - residual
        results.append(
            evaluate_calibration_error(
                target,
                OFFSET_MONTAJE_REAL_DEG,
                estimated_offset,
            )
        )
    return results


def _print_case(target: str, descripcion: str) -> None:
    print("\n" + "=" * 86)
    print(f"CASO: {descripcion}")
    print("=" * 86)

    if target == "brazo":
        angulo_real = ANGULO_BRAZO_REAL_DEG
    elif target == "antebrazo":
        angulo_real = ANGULO_ANTEBRAZO_REAL_DEG
    else:
        angulo_real = ANGULO_MANO_REAL_DEG

    print("TENEMOS:")
    print(f"  Segmento analizado:              {target}")
    print(f"  Orientación real del segmento:   {angulo_real:.1f}° alrededor de Z")
    print(f"  IMU montada físicamente:         {OFFSET_MONTAJE_REAL_DEG:.1f}° chueca")
    print("  Si conocemos exactamente ese offset, la calibración puede corregirlo.")

    print("\nCALCULAMOS:")
    print("  IMU medida = orientación real + offset físico de montaje")
    print("  Orientación reconstruida = IMU medida - offset estimado por calibración")
    print("  Error residual = offset real - offset estimado")
    print("  Después comparamos la pose reconstruida contra la pose ideal.")

    print("\nOBTENEMOS:")
    print("  Offset estimado | Error residual | Error posición muñeca | Error orientación mano")
    print("  -------------- | -------------- | --------------------- | ----------------------")
    for result in run_residual_sweep(target):
        print(
            f"  {result.estimated_mount_offset_deg:>13.1f}° | "
            f"{result.residual_calibration_error_deg:>12.1f}° | "
            f"{result.position_error_m * 1000:>18.3f} mm | "
            f"{result.orientation_error_deg:>19.3f}°"
        )


def _print_example_45_deg() -> None:
    result = evaluate_calibration_error("antebrazo", 10.0, 8.0)

    print("\n" + "=" * 86)
    print("EJEMPLO DIRECTO: EL CASO DE 45° QUE DISCUTIMOS")
    print("=" * 86)
    print("TENEMOS:")
    print("  Antebrazo real:                 45.0°")
    print("  IMU montada 10.0° chueca:      la lectura equivale a 55.0°")
    print("  Nuestra calibración estima:      8.0° de offset")

    print("\nCALCULAMOS:")
    print("  55.0° - 8.0° = 47.0°")
    print("  Deberíamos haber recuperado 45.0°")
    print("  Por tanto quedan 2.0° de error residual de calibración")

    print("\nOBTENEMOS:")
    print(f"  Error residual angular:        {result.residual_calibration_error_deg:.1f}°")
    print(f"  Error de posición de muñeca:   {result.position_error_m * 1000:.3f} mm")
    print("  Este valor coincide con la sensibilidad de un antebrazo de 0.25 m ante 2° de error.")


def main() -> None:
    print("\nV1 - SENSIBILIDAD A ERRORES DE CALIBRACIÓN")
    print("Los offsets y errores usados son SINTÉTICOS; no son especificaciones de hardware.")
    print("La idea es separar montaje físico, compensación de calibración y error residual.")

    _print_example_45_deg()
    _print_case("brazo", "error residual de calibración en la IMU del brazo")
    _print_case("antebrazo", "error residual de calibración en la IMU del antebrazo")
    _print_case("mano", "error residual de calibración en la IMU de la mano")

    print("\n" + "=" * 86)
    print("LECTURA DEL RESULTADO")
    print("=" * 86)
    print("- Una IMU puede estar montada chueca y aun así funcionar si el offset se conoce bien.")
    print("- Lo importante es el ERROR RESIDUAL que queda después de la calibración.")
    print("- Error residual en brazo/antebrazo se convierte en error de posición de muñeca.")
    print("- Error residual en mano afecta orientación de salida, no posición de muñeca.")
    print("- Aún no definimos cuánto error residual es aceptable para el wearable físico.")


if __name__ == "__main__":
    main()
