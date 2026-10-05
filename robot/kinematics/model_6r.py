"""Parámetros del modelo cinemático 6R.

Los valores DEMO son sintéticos y adimensionales. No representan dimensiones
ni límites mecánicos del manipulador físico del proyecto.
"""

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class RobotGeometry:
    """Geometría mínima usada por la FK/IK analítica v0.1."""

    l1: float
    l2: float
    lt: float

    def __post_init__(self) -> None:
        for name, value in (("l1", self.l1), ("l2", self.l2), ("lt", self.lt)):
            if value <= 0:
                raise ValueError(f"{name} debe ser mayor que cero.")


# Banco de pruebas normalizado acordado para el simulador.
DEMO_GEOMETRY = RobotGeometry(l1=1.0, l2=1.0, lt=0.25)

# Límites sintéticos para la UI. No deben usarse como límites del robot real.
DEMO_LIMITS_DEG = np.array(
    [
        [-180.0, 180.0],
        [-180.0, 180.0],
        [-180.0, 180.0],
        [-180.0, 180.0],
        [-180.0, 180.0],
        [-180.0, 180.0],
    ],
    dtype=float,
)
