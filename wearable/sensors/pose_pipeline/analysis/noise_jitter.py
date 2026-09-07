"""V1: sensibilidad del pipeline a ruido/jitter angular sintético.

Este análisis NO modela una IMU comercial específica. Genera perturbaciones
angulares aleatorias, reproducibles mediante una semilla, para estudiar cómo
pequeñas variaciones de orientación se propagan a la pose reconstruida.

Se analizan dos situaciones:

1. Brazo quieto: la pose real permanece constante y las orientaciones medidas
   fluctúan alrededor del valor real.
2. Antebrazo en movimiento: existe una trayectoria ideal y las muestras medidas
   se perturban alrededor de esa trayectoria.

Ejecutar desde la raíz del repositorio:

    python wearable/sensors/pose_pipeline/analysis/noise_jitter.py
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from statistics import mean, pstdev

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

# Escenarios sintéticos de estudio, NO especificaciones de sensores reales.
SIGMAS_RUIDO_DEG = (0.0, 0.1, 0.5, 1.0, 2.0)
MUESTRAS_QUIETO = 500
MUESTRAS_MOVIMIENTO = 300
SEMILLA_BASE = 20260906

# Pose real elegida sólo para la simulación estática.
ANGULO_BRAZO_QUIETO_DEG = 20.0
ANGULO_ANTEBRAZO_QUIETO_DEG = 55.0
ANGULO_MANO_QUIETA_DEG = 30.0


@dataclass(frozen=True)
class JitterMetrics:
    sigma_noise_deg: float
    samples: int
    position_rms_error_mm: float
    position_mean_error_mm: float
    position_std_error_mm: float
    position_peak_to_peak_mm: float
    orientation_rms_error_deg: float
    orientation_std_error_deg: float
    orientation_peak_to_peak_deg: float


@dataclass(frozen=True)
class MotionNoiseMetrics:
    sigma_noise_deg: float
    samples: int
    position_rms_error_mm: float
    position_max_error_mm: float
    orientation_rms_error_deg: float
    orientation_max_error_deg: float


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


def _with_z_noise(q_real: Quaternion, noise_deg: float) -> Quaternion:
    """Aplica una perturbación angular alrededor de Z a una orientación real."""
    q_noise = quaternion_from_axis_angle(EJE_Z, noise_deg)
    return quaternion_multiply(q_real, q_noise)


def _rms(values: list[float]) -> float:
    if not values:
        return 0.0
    return sqrt(mean(value * value for value in values))


def simulate_stationary_jitter(
    sigma_noise_deg: float,
    samples: int = MUESTRAS_QUIETO,
    seed: int = SEMILLA_BASE,
) -> JitterMetrics:
    """Simula las 3 IMUs alrededor de una pose fija con ruido gaussiano independiente."""
    if sigma_noise_deg < 0.0:
        raise ValueError("sigma_noise_deg no puede ser negativo")
    if samples <= 0:
        raise ValueError("samples debe ser mayor que cero")

    rng = random.Random(seed)

    q_upper_real = quaternion_from_axis_angle(EJE_Z, ANGULO_BRAZO_QUIETO_DEG)
    q_fore_real = quaternion_from_axis_angle(EJE_Z, ANGULO_ANTEBRAZO_QUIETO_DEG)
    q_hand_real = quaternion_from_axis_angle(EJE_Z, ANGULO_MANO_QUIETA_DEG)
    ideal = _pose(q_upper_real, q_fore_real, q_hand_real)

    position_errors_mm: list[float] = []
    orientation_errors_deg: list[float] = []

    for _ in range(samples):
        upper_noise = rng.gauss(0.0, sigma_noise_deg)
        fore_noise = rng.gauss(0.0, sigma_noise_deg)
        hand_noise = rng.gauss(0.0, sigma_noise_deg)

        reconstructed = _pose(
            _with_z_noise(q_upper_real, upper_noise),
            _with_z_noise(q_fore_real, fore_noise),
            _with_z_noise(q_hand_real, hand_noise),
        )

        position_errors_mm.append(
            vector_distance(ideal.position_h_m, reconstructed.position_h_m) * 1000.0
        )
        orientation_errors_deg.append(
            quaternion_angular_distance_deg(
                ideal.orientation_h_wxyz,
                reconstructed.orientation_h_wxyz,
            )
        )

    return JitterMetrics(
        sigma_noise_deg=sigma_noise_deg,
        samples=samples,
        position_rms_error_mm=_rms(position_errors_mm),
        position_mean_error_mm=mean(position_errors_mm),
        position_std_error_mm=pstdev(position_errors_mm),
        position_peak_to_peak_mm=max(position_errors_mm) - min(position_errors_mm),
        orientation_rms_error_deg=_rms(orientation_errors_deg),
        orientation_std_error_deg=pstdev(orientation_errors_deg),
        orientation_peak_to_peak_deg=max(orientation_errors_deg) - min(orientation_errors_deg),
    )


def simulate_moving_forearm(
    sigma_noise_deg: float,
    samples: int = MUESTRAS_MOVIMIENTO,
    seed: int = SEMILLA_BASE,
    forearm_start_deg: float = 20.0,
    forearm_end_deg: float = 80.0,
) -> MotionNoiseMetrics:
    """Compara una trayectoria ideal con la misma trayectoria perturbada por ruido."""
    if sigma_noise_deg < 0.0:
        raise ValueError("sigma_noise_deg no puede ser negativo")
    if samples <= 1:
        raise ValueError("samples debe ser mayor que uno")

    rng = random.Random(seed)
    q_upper_real = quaternion_from_axis_angle(EJE_Z, ANGULO_BRAZO_QUIETO_DEG)

    position_errors_mm: list[float] = []
    orientation_errors_deg: list[float] = []

    for index in range(samples):
        fraction = index / (samples - 1)
        forearm_angle = forearm_start_deg + fraction * (forearm_end_deg - forearm_start_deg)
        hand_angle = forearm_angle + 10.0

        q_fore_real = quaternion_from_axis_angle(EJE_Z, forearm_angle)
        q_hand_real = quaternion_from_axis_angle(EJE_Z, hand_angle)
        ideal = _pose(q_upper_real, q_fore_real, q_hand_real)

        upper_noise = rng.gauss(0.0, sigma_noise_deg)
        fore_noise = rng.gauss(0.0, sigma_noise_deg)
        hand_noise = rng.gauss(0.0, sigma_noise_deg)

        reconstructed = _pose(
            _with_z_noise(q_upper_real, upper_noise),
            _with_z_noise(q_fore_real, fore_noise),
            _with_z_noise(q_hand_real, hand_noise),
        )

        position_errors_mm.append(
            vector_distance(ideal.position_h_m, reconstructed.position_h_m) * 1000.0
        )
        orientation_errors_deg.append(
            quaternion_angular_distance_deg(
                ideal.orientation_h_wxyz,
                reconstructed.orientation_h_wxyz,
            )
        )

    return MotionNoiseMetrics(
        sigma_noise_deg=sigma_noise_deg,
        samples=samples,
        position_rms_error_mm=_rms(position_errors_mm),
        position_max_error_mm=max(position_errors_mm),
        orientation_rms_error_deg=_rms(orientation_errors_deg),
        orientation_max_error_deg=max(orientation_errors_deg),
    )


def _print_stationary_sweep() -> None:
    print("\n" + "=" * 96)
    print("CASO 1: BRAZO QUIETO CON JITTER ANGULAR")
    print("=" * 96)

    print("TENEMOS:")
    print(f"  Brazo real:       {ANGULO_BRAZO_QUIETO_DEG:.1f}°")
    print(f"  Antebrazo real:   {ANGULO_ANTEBRAZO_QUIETO_DEG:.1f}°")
    print(f"  Mano real:        {ANGULO_MANO_QUIETA_DEG:.1f}°")
    print(f"  Muestras por escenario: {MUESTRAS_QUIETO}")
    print("  A cada IMU le agregamos ruido gaussiano independiente alrededor de Z.")
    print("  Sigma es sólo un parámetro sintético de estudio.")

    print("\nCALCULAMOS:")
    print("  1. Pose ideal fija.")
    print("  2. Generamos múltiples lecturas con pequeñas variaciones angulares.")
    print("  3. Reconstruimos la pose para cada lectura.")
    print("  4. Comparamos cada muestra contra la pose ideal.")
    print("  5. Reportamos RMS, desviación estándar y pico a pico del error.")

    print("\nOBTENEMOS:")
    print("  Sigma | RMS posición | Std posición | P-P posición | RMS orientación | P-P orientación")
    print("  ----- | ------------ | ------------ | ------------ | --------------- | ---------------")
    for sigma in SIGMAS_RUIDO_DEG:
        result = simulate_stationary_jitter(sigma)
        print(
            f"  {sigma:>4.1f}° | "
            f"{result.position_rms_error_mm:>9.3f} mm | "
            f"{result.position_std_error_mm:>9.3f} mm | "
            f"{result.position_peak_to_peak_mm:>9.3f} mm | "
            f"{result.orientation_rms_error_deg:>12.3f}° | "
            f"{result.orientation_peak_to_peak_deg:>12.3f}°"
        )


def _print_motion_sweep() -> None:
    print("\n" + "=" * 96)
    print("CASO 2: ANTEBRAZO EN MOVIMIENTO CON RUIDO ANGULAR")
    print("=" * 96)

    print("TENEMOS:")
    print("  El antebrazo recorre una trayectoria sintética de 20° a 80°.")
    print(f"  Muestras por trayectoria: {MUESTRAS_MOVIMIENTO}")
    print("  A las tres orientaciones se agrega ruido gaussiano independiente.")

    print("\nCALCULAMOS:")
    print("  1. Para cada instante calculamos la pose ideal de la trayectoria.")
    print("  2. Generamos la lectura perturbada de las tres IMUs.")
    print("  3. Reconstruimos la pose con ruido.")
    print("  4. Medimos error de posición y orientación respecto a la trayectoria ideal.")

    print("\nOBTENEMOS:")
    print("  Sigma | RMS posición | Máx posición | RMS orientación | Máx orientación")
    print("  ----- | ------------ | ------------ | --------------- | ---------------")
    for sigma in SIGMAS_RUIDO_DEG:
        result = simulate_moving_forearm(sigma)
        print(
            f"  {sigma:>4.1f}° | "
            f"{result.position_rms_error_mm:>9.3f} mm | "
            f"{result.position_max_error_mm:>9.3f} mm | "
            f"{result.orientation_rms_error_deg:>12.3f}° | "
            f"{result.orientation_max_error_deg:>12.3f}°"
        )


def main() -> None:
    print("\nV1 - RUIDO / JITTER DEL PIPELINE DE POSE")
    print("Los niveles de ruido son SINTÉTICOS y no representan una IMU real.")
    print("La semilla aleatoria es fija para que tú y GitHub obtengan los mismos resultados.")

    _print_stationary_sweep()
    _print_motion_sweep()

    print("\n" + "=" * 96)
    print("LECTURA DEL RESULTADO")
    print("=" * 96)
    print("- Incluso con el brazo quieto, ruido angular puede producir jitter cartesiano.")
    print("- El ruido de brazo/antebrazo afecta la posición reconstruida de la muñeca.")
    print("- El ruido de la IMU de mano aparece directamente como jitter de orientación.")
    print("- Durante movimiento podemos medir cuánto se separa la trayectoria reconstruida de la ideal.")
    print("- Todavía NO elegimos filtro ni definimos niveles aceptables de ruido.")


if __name__ == "__main__":
    main()
