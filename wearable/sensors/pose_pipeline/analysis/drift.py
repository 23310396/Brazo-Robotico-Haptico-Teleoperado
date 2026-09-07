"""V1: sensibilidad del pipeline a drift angular sintético.

Este análisis NO modela una IMU comercial específica. Introduce una deriva angular
progresiva y controlada con el tiempo para estudiar cómo una orientación que se
aleja lentamente de su valor real afecta la pose reconstruida.

La primera versión estudia drift lineal alrededor del eje Z, sin filtros,
recenter ni correcciones. La intención es caracterizar primero el problema antes
de diseñar una estrategia de mitigación.

Ejecutar desde la raíz del repositorio:

    python wearable/sensors/pose_pipeline/analysis/drift.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from statistics import mean
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
EJE_Z = (0.0, 0.0, 1.0)
MODELO = UpperLimbModel(L_BRAZO_M, L_ANTEBRAZO_M)
CALIBRACION_IDEAL = SegmentCalibration()

# Escenarios sintéticos: NO son especificaciones de una IMU real.
DURACION_S = 60.0
MUESTRAS = 301
TASAS_DRIFT_DEG_S = (0.0, 0.01, 0.05, 0.10, 0.25)

# Pose real fija elegida únicamente para el análisis sintético.
ANGULO_BRAZO_REAL_DEG = 20.0
ANGULO_ANTEBRAZO_REAL_DEG = 55.0
ANGULO_MANO_REAL_DEG = 30.0


@dataclass(frozen=True)
class DriftMetrics:
    target: str
    drift_rate_deg_s: float
    duration_s: float
    samples: int
    final_drift_deg: float
    position_rms_error_mm: float
    position_max_error_mm: float
    position_final_error_mm: float
    orientation_rms_error_deg: float
    orientation_max_error_deg: float
    orientation_final_error_deg: float


def _rms(values: list[float]) -> float:
    if not values:
        return 0.0
    return sqrt(mean(value * value for value in values))


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


def _real_orientations() -> tuple[Quaternion, Quaternion, Quaternion]:
    return (
        quaternion_from_axis_angle(EJE_Z, ANGULO_BRAZO_REAL_DEG),
        quaternion_from_axis_angle(EJE_Z, ANGULO_ANTEBRAZO_REAL_DEG),
        quaternion_from_axis_angle(EJE_Z, ANGULO_MANO_REAL_DEG),
    )


def _with_z_drift(q_real: Quaternion, drift_deg: float) -> Quaternion:
    q_drift = quaternion_from_axis_angle(EJE_Z, drift_deg)
    return quaternion_multiply(q_real, q_drift)


def simulate_linear_drift(
    target: str,
    drift_rate_deg_s: float,
    duration_s: float = DURACION_S,
    samples: int = MUESTRAS,
) -> DriftMetrics:
    """Simula drift lineal en una pose real que permanece físicamente fija.

    target:
        - "brazo"
        - "antebrazo"
        - "mano"
        - "todos"

    drift_rate_deg_s puede ser positivo o negativo; el signo representa la
    dirección de la deriva. Las métricas reportan magnitud del error resultante.
    """
    if target not in {"brazo", "antebrazo", "mano", "todos"}:
        raise ValueError(f"Objetivo de drift no reconocido: {target}")
    if duration_s <= 0.0:
        raise ValueError("duration_s debe ser mayor que cero")
    if samples <= 1:
        raise ValueError("samples debe ser mayor que uno")

    q_upper_real, q_fore_real, q_hand_real = _real_orientations()
    ideal = _pose(q_upper_real, q_fore_real, q_hand_real)

    position_errors_mm: list[float] = []
    orientation_errors_deg: list[float] = []

    for index in range(samples):
        fraction = index / (samples - 1)
        elapsed_s = fraction * duration_s
        drift_deg = drift_rate_deg_s * elapsed_s

        q_upper = q_upper_real
        q_fore = q_fore_real
        q_hand = q_hand_real

        if target in {"brazo", "todos"}:
            q_upper = _with_z_drift(q_upper_real, drift_deg)
        if target in {"antebrazo", "todos"}:
            q_fore = _with_z_drift(q_fore_real, drift_deg)
        if target in {"mano", "todos"}:
            q_hand = _with_z_drift(q_hand_real, drift_deg)

        reconstructed = _pose(q_upper, q_fore, q_hand)

        position_errors_mm.append(
            vector_distance(ideal.position_h_m, reconstructed.position_h_m) * 1000.0
        )
        orientation_errors_deg.append(
            quaternion_angular_distance_deg(
                ideal.orientation_h_wxyz,
                reconstructed.orientation_h_wxyz,
            )
        )

    return DriftMetrics(
        target=target,
        drift_rate_deg_s=drift_rate_deg_s,
        duration_s=duration_s,
        samples=samples,
        final_drift_deg=drift_rate_deg_s * duration_s,
        position_rms_error_mm=_rms(position_errors_mm),
        position_max_error_mm=max(position_errors_mm),
        position_final_error_mm=position_errors_mm[-1],
        orientation_rms_error_deg=_rms(orientation_errors_deg),
        orientation_max_error_deg=max(orientation_errors_deg),
        orientation_final_error_deg=orientation_errors_deg[-1],
    )


def run_sweep(
    target: str,
    rates_deg_s: Iterable[float] = TASAS_DRIFT_DEG_S,
) -> list[DriftMetrics]:
    return [simulate_linear_drift(target, rate) for rate in rates_deg_s]


def _print_case(target: str, descripcion: str) -> None:
    print("\n" + "=" * 106)
    print(f"CASO: {descripcion}")
    print("=" * 106)

    print("TENEMOS:")
    print(f"  Pose física fija durante:       {DURACION_S:.1f} s")
    print(f"  Brazo real:                     {ANGULO_BRAZO_REAL_DEG:.1f}°")
    print(f"  Antebrazo real:                 {ANGULO_ANTEBRAZO_REAL_DEG:.1f}°")
    print(f"  Mano real:                      {ANGULO_MANO_REAL_DEG:.1f}°")
    print(f"  Segmento(s) con drift:          {target}")
    print("  La deriva crece linealmente con el tiempo alrededor de Z.")

    print("\nCALCULAMOS:")
    print("  1. La pose física real permanece constante.")
    print("  2. La orientación medida acumula drift = tasa * tiempo.")
    print("  3. Reconstruimos la pose en cada instante sin ninguna corrección.")
    print("  4. Comparamos contra la pose ideal fija.")
    print("  5. Reportamos error final, máximo y RMS durante el ensayo.")

    print("\nOBTENEMOS:")
    print("  Tasa drift | Drift final | RMS posición | Final posición | RMS orientación | Final orientación")
    print("  ---------- | ----------- | ------------ | -------------- | --------------- | -----------------")
    for result in run_sweep(target):
        print(
            f"  {result.drift_rate_deg_s:>8.2f}°/s | "
            f"{result.final_drift_deg:>9.2f}° | "
            f"{result.position_rms_error_mm:>9.3f} mm | "
            f"{result.position_final_error_mm:>11.3f} mm | "
            f"{result.orientation_rms_error_deg:>12.3f}° | "
            f"{result.orientation_final_error_deg:>14.3f}°"
        )


def main() -> None:
    print("\nV1 - DRIFT ANGULAR DEL PIPELINE DE POSE")
    print("Las tasas de drift son SINTÉTICAS y no representan una IMU comercial.")
    print("Esta etapa NO aplica filtros, magnetómetro, clutch ni recenter.")

    _print_case("brazo", "drift únicamente en la IMU del brazo")
    _print_case("antebrazo", "drift únicamente en la IMU del antebrazo")
    _print_case("mano", "drift únicamente en la IMU de la mano")
    _print_case("todos", "el mismo drift afecta simultáneamente las tres IMUs")

    print("\n" + "=" * 106)
    print("LECTURA DEL RESULTADO")
    print("=" * 106)
    print("- El drift es un error acumulativo: la orientación se aleja progresivamente del valor real.")
    print("- Drift en brazo/antebrazo puede desplazar progresivamente la muñeca reconstruida.")
    print("- Drift sólo en mano afecta orientación de salida, no posición de muñeca en este modelo.")
    print("- Esta simulación caracteriza el problema antes de elegir una estrategia de corrección.")
    print("- Todavía NO definimos una tasa de drift aceptable para el wearable físico.")


if __name__ == "__main__":
    main()
