"""V1: sensibilidad del pipeline a desincronización temporal sintética.

Este análisis NO modela una IMU ni un bus de comunicación específicos. Estudia
qué ocurre cuando las orientaciones de brazo, antebrazo y mano corresponden a
instantes ligeramente distintos mientras el operador se está moviendo.

También separa dos fenómenos que no deben confundirse:

1. Desincronización relativa: los tres sensores pertenecen a instantes distintos.
2. Retardo común: los tres sensores pertenecen al mismo instante, pero ese instante
   es anterior al tiempo de referencia. Esto es principalmente latencia, no skew
   entre sensores.

Ejecutar desde la raíz del repositorio:

    python wearable/sensors/pose_pipeline/analysis/desynchronization.py
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
from wearable.sensors.pose_pipeline.pipeline import SegmentCalibration, UpperLimbModel, estimate_hand_pose
from wearable.sensors.pose_pipeline.synthetic import quaternion_from_axis_angle, synthetic_sample


L_BRAZO_M = 0.30
L_ANTEBRAZO_M = 0.25
EJE_Z = (0.0, 0.0, 1.0)
MODELO = UpperLimbModel(L_BRAZO_M, L_ANTEBRAZO_M)
CALIBRACION_IDEAL = SegmentCalibration()

# Pose en el instante de referencia. Valores sintéticos, no datos del usuario.
ANGULO_BRAZO_REF_DEG = 20.0
ANGULO_ANTEBRAZO_REF_DEG = 55.0
ANGULO_MANO_REF_DEG = 30.0

# Velocidades angulares sintéticas para caracterizar sensibilidad temporal.
VEL_BRAZO_DEG_S = 45.0
VEL_ANTEBRAZO_DEG_S = 90.0
VEL_MANO_DEG_S = 120.0

SKEWS_MS = (0.0, 5.0, 10.0, 20.0, 50.0)


@dataclass(frozen=True)
class DesynchronizationMetrics:
    requested_skew_ms: float
    measured_skew_ms: float
    position_error_mm: float
    orientation_error_deg: float
    upper_offset_ms: float
    forearm_offset_ms: float
    hand_offset_ms: float


@dataclass(frozen=True)
class CommonDelayMetrics:
    delay_ms: float
    measured_skew_ms: float
    position_error_mm: float
    orientation_error_deg: float


def _orientation_at(reference_angle_deg: float, velocity_deg_s: float, time_offset_s: float):
    """Orientación para movimiento angular constante alrededor de Z."""
    return quaternion_from_axis_angle(
        EJE_Z,
        reference_angle_deg + velocity_deg_s * time_offset_s,
    )


def _pose_at_offsets(
    upper_offset_s: float,
    forearm_offset_s: float,
    hand_offset_s: float,
    upper_velocity_deg_s: float = VEL_BRAZO_DEG_S,
    forearm_velocity_deg_s: float = VEL_ANTEBRAZO_DEG_S,
    hand_velocity_deg_s: float = VEL_MANO_DEG_S,
):
    q_upper = _orientation_at(ANGULO_BRAZO_REF_DEG, upper_velocity_deg_s, upper_offset_s)
    q_fore = _orientation_at(ANGULO_ANTEBRAZO_REF_DEG, forearm_velocity_deg_s, forearm_offset_s)
    q_hand = _orientation_at(ANGULO_MANO_REF_DEG, hand_velocity_deg_s, hand_offset_s)

    return estimate_hand_pose(
        synthetic_sample("brazo", q_upper, timestamp_s=upper_offset_s),
        synthetic_sample("antebrazo", q_fore, timestamp_s=forearm_offset_s),
        synthetic_sample("mano", q_hand, timestamp_s=hand_offset_s),
        CALIBRACION_IDEAL,
        CALIBRACION_IDEAL,
        CALIBRACION_IDEAL,
        MODELO,
    )


def _ideal_pose():
    return _pose_at_offsets(0.0, 0.0, 0.0)


def simulate_relative_skew(
    skew_ms: float,
    upper_velocity_deg_s: float = VEL_BRAZO_DEG_S,
    forearm_velocity_deg_s: float = VEL_ANTEBRAZO_DEG_S,
    hand_velocity_deg_s: float = VEL_MANO_DEG_S,
) -> DesynchronizationMetrics:
    """Simula muestras repartidas alrededor del instante de referencia.

    Para un skew total Δt:
      brazo      -> -Δt/2
      antebrazo  -> +Δt/2
      mano       -> 0

    Así, max(timestamp)-min(timestamp) = Δt.
    """
    if skew_ms < 0.0:
        raise ValueError("skew_ms no puede ser negativo")

    half_s = (skew_ms / 1000.0) / 2.0
    upper_offset_s = -half_s
    forearm_offset_s = half_s
    hand_offset_s = 0.0

    ideal = _ideal_pose()
    reconstructed = _pose_at_offsets(
        upper_offset_s,
        forearm_offset_s,
        hand_offset_s,
        upper_velocity_deg_s,
        forearm_velocity_deg_s,
        hand_velocity_deg_s,
    )

    return DesynchronizationMetrics(
        requested_skew_ms=skew_ms,
        measured_skew_ms=reconstructed.sensor_time_skew_s * 1000.0,
        position_error_mm=vector_distance(ideal.position_h_m, reconstructed.position_h_m) * 1000.0,
        orientation_error_deg=quaternion_angular_distance_deg(
            ideal.orientation_h_wxyz,
            reconstructed.orientation_h_wxyz,
        ),
        upper_offset_ms=upper_offset_s * 1000.0,
        forearm_offset_ms=forearm_offset_s * 1000.0,
        hand_offset_ms=hand_offset_s * 1000.0,
    )


def simulate_common_delay(
    delay_ms: float,
    upper_velocity_deg_s: float = VEL_BRAZO_DEG_S,
    forearm_velocity_deg_s: float = VEL_ANTEBRAZO_DEG_S,
    hand_velocity_deg_s: float = VEL_MANO_DEG_S,
) -> CommonDelayMetrics:
    """Simula las 3 IMUs perfectamente sincronizadas, pero todas atrasadas."""
    if delay_ms < 0.0:
        raise ValueError("delay_ms no puede ser negativo")

    offset_s = -(delay_ms / 1000.0)
    ideal = _ideal_pose()
    delayed = _pose_at_offsets(
        offset_s,
        offset_s,
        offset_s,
        upper_velocity_deg_s,
        forearm_velocity_deg_s,
        hand_velocity_deg_s,
    )

    return CommonDelayMetrics(
        delay_ms=delay_ms,
        measured_skew_ms=delayed.sensor_time_skew_s * 1000.0,
        position_error_mm=vector_distance(ideal.position_h_m, delayed.position_h_m) * 1000.0,
        orientation_error_deg=quaternion_angular_distance_deg(
            ideal.orientation_h_wxyz,
            delayed.orientation_h_wxyz,
        ),
    )


def run_skew_sweep(skews_ms: Iterable[float] = SKEWS_MS) -> list[DesynchronizationMetrics]:
    return [simulate_relative_skew(skew_ms) for skew_ms in skews_ms]


def _print_relative_skew() -> None:
    print("\n" + "=" * 100)
    print("CASO 1: DESINCRONIZACIÓN RELATIVA ENTRE LAS 3 IMUs")
    print("=" * 100)

    print("TENEMOS:")
    print(f"  Brazo en t_ref:       {ANGULO_BRAZO_REF_DEG:.1f}° a {VEL_BRAZO_DEG_S:.1f}°/s")
    print(f"  Antebrazo en t_ref:   {ANGULO_ANTEBRAZO_REF_DEG:.1f}° a {VEL_ANTEBRAZO_DEG_S:.1f}°/s")
    print(f"  Mano en t_ref:        {ANGULO_MANO_REF_DEG:.1f}° a {VEL_MANO_DEG_S:.1f}°/s")
    print("  Para cada skew, brazo se toma antes, antebrazo después y mano en t_ref.")
    print("  Velocidades y skews son escenarios SINTÉTICOS de análisis.")

    print("\nCALCULAMOS:")
    print("  1. Pose ideal: las 3 orientaciones corresponden exactamente a t_ref.")
    print("  2. Pose desincronizada: cada segmento corresponde a un instante distinto.")
    print("  3. El pipeline reporta max(timestamp) - min(timestamp).")
    print("  4. Comparamos posición de muñeca y orientación de mano contra la pose ideal.")

    print("\nOBTENEMOS:")
    print("  Skew pedido | Skew medido | Error posición | Error orientación")
    print("  ----------- | ----------- | -------------- | -----------------")
    for result in run_skew_sweep():
        print(
            f"  {result.requested_skew_ms:>8.1f} ms | "
            f"{result.measured_skew_ms:>8.1f} ms | "
            f"{result.position_error_mm:>11.3f} mm | "
            f"{result.orientation_error_deg:>14.3f}°"
        )


def _print_common_delay() -> None:
    print("\n" + "=" * 100)
    print("CASO 2: RETARDO COMÚN, PERO SENSORES SINCRONIZADOS ENTRE SÍ")
    print("=" * 100)

    print("TENEMOS:")
    print("  Las 3 IMUs corresponden al mismo instante, pero todas llegan atrasadas.")
    print("  Por tanto, el skew interno entre sensores debe permanecer en 0 ms.")

    print("\nCALCULAMOS:")
    print("  1. Reconstruimos la pose antigua, internamente consistente.")
    print("  2. La comparamos con la pose actual en t_ref.")
    print("  3. El error observado es efecto de latencia temporal, no de desincronización interna.")

    print("\nOBTENEMOS:")
    print("  Retardo común | Skew medido | Error posición | Error orientación")
    print("  ------------- | ----------- | -------------- | -----------------")
    for delay_ms in SKEWS_MS:
        result = simulate_common_delay(delay_ms)
        print(
            f"  {result.delay_ms:>10.1f} ms | "
            f"{result.measured_skew_ms:>8.1f} ms | "
            f"{result.position_error_mm:>11.3f} mm | "
            f"{result.orientation_error_deg:>14.3f}°"
        )


def main() -> None:
    print("\nV1 - DESINCRONIZACIÓN DINÁMICA DEL PIPELINE DE POSE")
    print("Los tiempos y velocidades son SINTÉTICOS; no representan requisitos ya adoptados.")

    _print_relative_skew()
    _print_common_delay()

    print("\n" + "=" * 100)
    print("LECTURA DEL RESULTADO")
    print("=" * 100)
    print("- Con el operador quieto, un skew temporal por sí solo no cambia la pose.")
    print("- Durante movimiento, muestras de instantes distintos pueden deformar la reconstrucción.")
    print("- El efecto del mismo skew aumenta cuando aumenta la velocidad de movimiento.")
    print("- Un retardo idéntico en las 3 IMUs produce skew interno 0 ms, pero sigue siendo latencia.")
    print("- Esta separación nos permitirá derivar requisitos distintos de sincronización y latencia.")
    print("- Todavía NO definimos cuántos milisegundos son aceptables para el wearable físico.")


if __name__ == "__main__":
    main()
