"""Demo legible del pipeline de pose del operador.

La idea de este archivo no es sustituir las pruebas automáticas, sino mostrar
paso a paso qué datos tenemos, qué calcula el pipeline y qué resultado produce.

Se puede ejecutar desde la raíz del repositorio con:

    python wearable/sensors/pose_pipeline/demo.py

O como módulo:

    python -m wearable.sensors.pose_pipeline.demo
"""

from __future__ import annotations

import sys
from math import degrees
from pathlib import Path

# Permite usar el botón Run de Codespaces aunque el archivo se ejecute directamente.
if __package__ in (None, ""):
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from wearable.sensors.pose_pipeline.pipeline import (
    IDENTITY_Q,
    SegmentCalibration,
    UpperLimbModel,
    estimate_hand_pose,
)
from wearable.sensors.pose_pipeline.synthetic import (
    quaternion_from_axis_angle,
    synthetic_sample,
)


L_BRAZO = 0.30
L_ANTEBRAZO = 0.25
MODELO = UpperLimbModel(
    upper_arm_length_m=L_BRAZO,
    forearm_length_m=L_ANTEBRAZO,
)
CALIBRACION_IDEAL = SegmentCalibration()


def _formatear_vector(vector: tuple[float, float, float]) -> str:
    return f"X={vector[0]:.3f} m, Y={vector[1]:.3f} m, Z={vector[2]:.3f} m"


def _angulo_del_quaternion_z(q: tuple[float, float, float, float]) -> float:
    """Devuelve el ángulo alrededor de Z para los ejemplos simples de la demo."""
    w, _, _, z = q
    from math import atan2

    return degrees(2.0 * atan2(z, w))


def _encabezado(numero: int, titulo: str) -> None:
    print("\n" + "=" * 72)
    print(f"EJEMPLO {numero}: {titulo}")
    print("=" * 72)


def ejemplo_brazo_extendido() -> None:
    _encabezado(1, "brazo y antebrazo completamente extendidos")

    print("TENEMOS:")
    print(f"  Longitud del brazo:      {L_BRAZO:.2f} m")
    print(f"  Longitud del antebrazo:  {L_ANTEBRAZO:.2f} m")
    print("  Brazo apuntando hacia +X")
    print("  Antebrazo apuntando hacia +X")
    print("  Mano sin giro adicional")

    brazo = synthetic_sample("brazo", IDENTITY_Q)
    antebrazo = synthetic_sample("antebrazo", IDENTITY_Q)
    mano = synthetic_sample("mano", IDENTITY_Q)

    print("\nCALCULAMOS:")
    print("  Codo    = R_brazo * [L_brazo, 0, 0]")
    print("  Muñeca  = Codo + R_antebrazo * [L_antebrazo, 0, 0]")
    print(f"  En este caso: X = {L_BRAZO:.2f} + {L_ANTEBRAZO:.2f} = {L_BRAZO + L_ANTEBRAZO:.2f} m")

    pose = estimate_hand_pose(
        brazo,
        antebrazo,
        mano,
        CALIBRACION_IDEAL,
        CALIBRACION_IDEAL,
        CALIBRACION_IDEAL,
        MODELO,
    )

    print("\nOBTENEMOS:")
    print(f"  Codo:    {_formatear_vector(pose.elbow_position_h_m)}")
    print(f"  Muñeca:  {_formatear_vector(pose.position_h_m)}")
    print("  Resultado esperado: la muñeca queda a 0.55 m al frente del hombro.")


def ejemplo_codo_90() -> None:
    _encabezado(2, "codo doblado 90° hacia arriba")

    print("TENEMOS:")
    print(f"  Longitud del brazo:      {L_BRAZO:.2f} m")
    print(f"  Longitud del antebrazo:  {L_ANTEBRAZO:.2f} m")
    print("  Brazo apuntando hacia +X")
    print("  Antebrazo girado -90° alrededor de Y, por lo que apunta hacia +Z")

    brazo = synthetic_sample("brazo", IDENTITY_Q)
    antebrazo = synthetic_sample(
        "antebrazo",
        quaternion_from_axis_angle((0.0, 1.0, 0.0), -90.0),
    )
    mano = synthetic_sample("mano", IDENTITY_Q)

    print("\nCALCULAMOS:")
    print("  El brazo coloca el codo 0.30 m al frente.")
    print("  El antebrazo agrega 0.25 m hacia arriba.")
    print("  Muñeca = [0.30, 0.00, 0.00] + [0.00, 0.00, 0.25]")

    pose = estimate_hand_pose(
        brazo,
        antebrazo,
        mano,
        CALIBRACION_IDEAL,
        CALIBRACION_IDEAL,
        CALIBRACION_IDEAL,
        MODELO,
    )

    print("\nOBTENEMOS:")
    print(f"  Codo:    {_formatear_vector(pose.elbow_position_h_m)}")
    print(f"  Muñeca:  {_formatear_vector(pose.position_h_m)}")
    print("  Resultado esperado: 0.30 m al frente y 0.25 m arriba.")


def ejemplo_giro_mano() -> None:
    _encabezado(3, "giramos sólo la mano 30°")

    print("TENEMOS:")
    print("  Brazo y antebrazo en la misma posición del ejemplo 2.")
    print("  La mano gira 30° alrededor de Z.")
    print("  La muñeca NO debe cambiar de posición por girar solamente la mano.")

    brazo = synthetic_sample("brazo", IDENTITY_Q)
    antebrazo = synthetic_sample(
        "antebrazo",
        quaternion_from_axis_angle((0.0, 1.0, 0.0), -90.0),
    )
    mano = synthetic_sample(
        "mano",
        quaternion_from_axis_angle((0.0, 0.0, 1.0), 30.0),
    )

    print("\nCALCULAMOS:")
    print("  Posición de muñeca = brazo + antebrazo.")
    print("  Orientación final  = orientación de la IMU de la mano.")
    print("  Por eso el giro de la mano afecta orientación, no la posición de muñeca.")

    pose = estimate_hand_pose(
        brazo,
        antebrazo,
        mano,
        CALIBRACION_IDEAL,
        CALIBRACION_IDEAL,
        CALIBRACION_IDEAL,
        MODELO,
    )

    print("\nOBTENEMOS:")
    print(f"  Muñeca:             {_formatear_vector(pose.position_h_m)}")
    print(f"  Quaternion mano:    {tuple(round(v, 6) for v in pose.orientation_h_wxyz)}")
    print(f"  Giro alrededor de Z: {_angulo_del_quaternion_z(pose.orientation_h_wxyz):.1f}°")
    print("  Resultado esperado: misma muñeca del ejemplo 2 y mano girada 30°.")


def main() -> None:
    print("\nDEMO DEL PIPELINE DE POSE DEL OPERADOR")
    print("Esta demo usa datos sintéticos. Todavía no representa IMUs físicas.")
    print("Frame humano: +X al frente, +Y a la izquierda, +Z hacia arriba.")

    ejemplo_brazo_extendido()
    ejemplo_codo_90()
    ejemplo_giro_mano()

    print("\n" + "=" * 72)
    print("FIN DE LA DEMO")
    print("Las pruebas automáticas siguen siendo las que validan el código.")
    print("Esta demo sólo hace visible la lógica de los cálculos.")
    print("=" * 72)


if __name__ == "__main__":
    main()
