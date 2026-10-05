"""Launcher del simulador 6R.

Uso normal:
    python -m simulation.arm_6r.simulator

Smoke test:
    python -m simulation.arm_6r.simulator --smoke-test

Diagnóstico:
    python -m simulation.arm_6r.simulator --diagnose-gui
"""

from __future__ import annotations

import argparse
import importlib
import os
from pathlib import Path
import subprocess
import sys

import numpy as np

from robot.kinematics.forward_kinematics import forward_kinematics
from robot.kinematics.inverse_kinematics import inverse_kinematics
from robot.kinematics.model_6r import DEMO_GEOMETRY, DEMO_LIMITS_DEG


LIMITS_RAD = np.deg2rad(DEMO_LIMITS_DEG)


def smoke_test() -> None:
    q = np.deg2rad([25.0, 30.0, -55.0, 40.0, 35.0, -70.0])
    fk = forward_kinematics(q, DEMO_GEOMETRY)
    result = inverse_kinematics(
        fk["T_tcp"],
        DEMO_GEOMETRY,
        q_current=np.zeros(6),
        joint_limits_rad=LIMITS_RAD,
    )
    valid = [solution for solution in result["solutions"] if solution.valid]
    if result["status"] != "OK" or not valid:
        raise RuntimeError("Smoke test: la IK no devolvió una solución válida.")

    best = min(valid, key=lambda s: s.position_error + s.orientation_error)
    if best.position_error > 1e-7 or best.orientation_error > 1e-7:
        raise RuntimeError("Smoke test: error FK/IK fuera de tolerancia.")

    for package in ("streamlit", "plotly"):
        importlib.import_module(package)

    print("SMOKE TEST OK")


def diagnose() -> None:
    import streamlit
    import plotly

    print(f"Python: {sys.executable}")
    print(f"Streamlit: {streamlit.__version__}")
    print(f"Plotly: {plotly.__version__}")
    print(f"Codespaces: {os.environ.get('CODESPACES', 'false')}")
    print(f"Puerto del simulador: {os.environ.get('SIMULATOR_PORT', '8501')}")
    print("Interfaz: navegador (Streamlit + Plotly)")


def launch() -> None:
    app_path = Path(__file__).with_name("app.py").resolve()
    port = os.environ.get("SIMULATOR_PORT", "8501")
    codespaces = os.environ.get("CODESPACES", "").lower() == "true"

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.address=0.0.0.0",
        f"--server.port={port}",
        "--browser.gatherUsageStats=false",
    ]

    if codespaces:
        command.append("--server.headless=true")
        print(f"Simulador 6R listo para Codespaces en el puerto {port}.")
        print("Abre la pestaña PORTS y usa Open in Browser sobre ese puerto.")
        print("Deja esta terminal corriendo mientras uses el simulador.")
    else:
        command.append("--server.headless=false")
        print(f"Abriendo Simulador 6R en el navegador (puerto {port})...")

    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Launcher del simulador 6R")
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--diagnose-gui", action="store_true")
    args = parser.parse_args()

    if args.smoke_test:
        smoke_test()
        return
    if args.diagnose_gui:
        diagnose()
        return

    launch()


if __name__ == "__main__":
    main()
