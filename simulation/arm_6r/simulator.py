"""Simulador interactivo FK/IK para el modelo 6R v0.1.

Ejecutar desde la raíz del repositorio:
    python -m simulation.arm_6r.simulator

Smoke test sin abrir ventana:
    python -m simulation.arm_6r.simulator --smoke-test
"""

from __future__ import annotations

import argparse
import math
import os
import sys

import matplotlib
import numpy as np


# Selección de backend:
# - smoke test: Agg (sin interfaz)
# - Codespaces/headless Linux: WebAgg (interfaz en navegador)
# - entorno local con escritorio: TkAgg
_SMOKE_REQUESTED = "--smoke-test" in sys.argv
_HEADLESS = (
    os.environ.get("CODESPACES", "").lower() == "true"
    or (
        sys.platform != "win32"
        and not os.environ.get("DISPLAY")
        and not os.environ.get("WAYLAND_DISPLAY")
    )
)
_GUI_MODE = "desktop"
_GUI_BACKEND_ERROR: Exception | None = None
WEBAGG_PORT = int(os.environ.get("SIMULATOR_PORT", "8988"))

if _SMOKE_REQUESTED:
    matplotlib.use("Agg", force=True)
    _GUI_MODE = "smoke"
elif _HEADLESS:
    matplotlib.use("WebAgg", force=True)
    matplotlib.rcParams["webagg.address"] = "0.0.0.0"
    matplotlib.rcParams["webagg.port"] = WEBAGG_PORT
    matplotlib.rcParams["webagg.open_in_browser"] = False
    _GUI_MODE = "web"
else:
    try:
        import tkinter as tk

        _probe = tk.Tk()
        _probe.withdraw()
        _probe.update_idletasks()
        _probe.destroy()
        matplotlib.use("TkAgg", force=True)
        _GUI_MODE = "desktop"
    except Exception as exc:
        _GUI_BACKEND_ERROR = exc

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, CheckButtons, RadioButtons, Slider

from robot.kinematics.forward_kinematics import (
    forward_kinematics,
    rotation_to_rpy_zyx,
    rpy_zyx_to_rotation,
)
from robot.kinematics.inverse_kinematics import IKSolution, inverse_kinematics
from robot.kinematics.model_6r import DEMO_GEOMETRY, DEMO_LIMITS_DEG


GEOMETRY = DEMO_GEOMETRY
LIMITS_RAD = np.deg2rad(DEMO_LIMITS_DEG)
WORKSPACE_LIMIT = GEOMETRY.l1 + GEOMETRY.l2 + GEOMETRY.lt + 0.35


def _target_transform(position: np.ndarray, rpy_deg: np.ndarray) -> np.ndarray:
    rpy_rad = np.deg2rad(rpy_deg)
    t = np.eye(4, dtype=float)
    t[:3, :3] = rpy_zyx_to_rotation(*rpy_rad)
    t[:3, 3] = position
    return t


def _shortest_joint_delta(q_from: np.ndarray, q_to: np.ndarray) -> np.ndarray:
    return (q_to - q_from + math.pi) % (2.0 * math.pi) - math.pi


class Arm6RSimulator:
    def __init__(self) -> None:
        self.q_current = np.zeros(6, dtype=float)
        self.mode = "FK"
        self.show_frames = False
        self.show_target = True
        self.show_trail = False
        self.tcp_trail: list[np.ndarray] = []
        self.ik_solutions: list[IKSolution] = []
        self.selected_solution_index = 0
        self.ghost_q: np.ndarray | None = None
        self.animation: FuncAnimation | None = None
        self._updating_widgets = False

        fk0 = forward_kinematics(self.q_current, GEOMETRY)
        self.target_position = fk0["p_tcp"].copy()
        self.target_rpy_deg = np.rad2deg(rotation_to_rpy_zyx(fk0["R_tcp"]))

        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        self.fig = plt.figure(figsize=(14, 8))
        self.fig.canvas.manager.set_window_title("Simulador 6R - FK / IK")
        self.ax3d = self.fig.add_axes([0.34, 0.12, 0.63, 0.82], projection="3d")

        self.fig.text(0.03, 0.955, "SIMULADOR 6R — DEMO SINTÉTICA", fontsize=14, weight="bold")
        self.fig.text(
            0.03,
            0.925,
            "L1=1.0, L2=1.0, LT=0.25 | No son dimensiones del robot real",
            fontsize=9,
        )

        mode_ax = self.fig.add_axes([0.03, 0.81, 0.12, 0.09])
        self.mode_radio = RadioButtons(mode_ax, ("FK", "IK"), active=0)
        self.mode_radio.on_clicked(self._on_mode_changed)

        self.joint_sliders: list[Slider] = []
        y = 0.735
        for i in range(6):
            ax = self.fig.add_axes([0.055, y, 0.23, 0.025])
            slider = Slider(
                ax,
                f"J{i+1}",
                DEMO_LIMITS_DEG[i, 0],
                DEMO_LIMITS_DEG[i, 1],
                valinit=0.0,
                valstep=0.5,
            )
            slider.on_changed(self._on_joint_slider)
            self.joint_sliders.append(slider)
            y -= 0.047

        self.target_sliders: list[Slider] = []
        target_specs = [
            ("X", -WORKSPACE_LIMIT, WORKSPACE_LIMIT, self.target_position[0]),
            ("Y", -WORKSPACE_LIMIT, WORKSPACE_LIMIT, self.target_position[1]),
            ("Z", -WORKSPACE_LIMIT, WORKSPACE_LIMIT, self.target_position[2]),
            ("Roll", -180.0, 180.0, self.target_rpy_deg[0]),
            ("Pitch", -180.0, 180.0, self.target_rpy_deg[1]),
            ("Yaw", -180.0, 180.0, self.target_rpy_deg[2]),
        ]
        y = 0.735
        for label, vmin, vmax, init in target_specs:
            ax = self.fig.add_axes([0.055, y, 0.23, 0.025])
            slider = Slider(ax, label, vmin, vmax, valinit=float(init), valstep=0.5)
            slider.on_changed(self._on_target_slider)
            self.target_sliders.append(slider)
            y -= 0.047

        solve_ax = self.fig.add_axes([0.03, 0.405, 0.115, 0.045])
        reach_ax = self.fig.add_axes([0.16, 0.405, 0.115, 0.045])
        zero_ax = self.fig.add_axes([0.03, 0.35, 0.115, 0.045])
        view_ax = self.fig.add_axes([0.16, 0.35, 0.115, 0.045])

        self.solve_button = Button(solve_ax, "Resolver IK")
        self.reach_button = Button(reach_ax, "Alcanzar")
        self.zero_button = Button(zero_ax, "Config. cero")
        self.view_button = Button(view_ax, "Vista iso.")

        self.solve_button.on_clicked(self._solve_ik)
        self.reach_button.on_clicked(self._reach)
        self.zero_button.on_clicked(self._zero_configuration)
        self.view_button.on_clicked(self._reset_view)

        check_ax = self.fig.add_axes([0.03, 0.245, 0.245, 0.085])
        self.checks = CheckButtons(
            check_ax,
            ("Mostrar frames", "Mostrar target", "Trayectoria TCP"),
            (False, True, False),
        )
        self.checks.on_clicked(self._on_check)

        sol_ax = self.fig.add_axes([0.03, 0.11, 0.245, 0.11])
        self.solution_radio = RadioButtons(sol_ax, ("Sin soluciones",), active=0)
        self.solution_radio.on_clicked(self._on_solution_selected)

        self.status_text = self.fig.text(
            0.03,
            0.025,
            "",
            fontsize=9,
            family="monospace",
            va="bottom",
        )

        self._set_mode_visibility()

    def _set_mode_visibility(self) -> None:
        fk_visible = self.mode == "FK"
        for slider in self.joint_sliders:
            slider.ax.set_visible(fk_visible)
        for slider in self.target_sliders:
            slider.ax.set_visible(not fk_visible)

        self.solve_button.ax.set_visible(not fk_visible)
        self.reach_button.ax.set_visible(not fk_visible)
        self.solution_radio.ax.set_visible(not fk_visible)
        self.fig.canvas.draw_idle()

    def _on_mode_changed(self, label: str) -> None:
        self.mode = label
        self.ghost_q = None
        if self.mode == "FK":
            self._sync_joint_sliders()
        self._set_mode_visibility()
        self._refresh()

    def _sync_joint_sliders(self) -> None:
        self._updating_widgets = True
        try:
            for slider, value in zip(self.joint_sliders, np.rad2deg(self.q_current)):
                slider.set_val(float(value))
        finally:
            self._updating_widgets = False

    def _on_joint_slider(self, _value: float) -> None:
        if self._updating_widgets or self.mode != "FK":
            return
        self.q_current = np.deg2rad([slider.val for slider in self.joint_sliders])
        self._append_trail()
        self._refresh()

    def _on_target_slider(self, _value: float) -> None:
        if self._updating_widgets or self.mode != "IK":
            return
        vals = np.array([slider.val for slider in self.target_sliders], dtype=float)
        self.target_position = vals[:3]
        self.target_rpy_deg = vals[3:]
        self.ghost_q = None
        self.ik_solutions = []
        self._replace_solution_radio([])
        self._refresh()

    def _on_check(self, label: str) -> None:
        states = self.checks.get_status()
        self.show_frames, self.show_target, self.show_trail = states
        if label == "Trayectoria TCP" and not self.show_trail:
            self.tcp_trail.clear()
        self._refresh()

    def _replace_solution_radio(self, solutions: list[IKSolution]) -> None:
        old_ax = self.solution_radio.ax
        position = old_ax.get_position()
        old_ax.remove()
        new_ax = self.fig.add_axes(position)

        if solutions:
            labels = [
                f"{i+1}: {s.elbow_branch}/{s.wrist_branch}"
                for i, s in enumerate(solutions)
            ]
        else:
            labels = ["Sin soluciones"]

        self.solution_radio = RadioButtons(new_ax, labels, active=0)
        self.solution_radio.on_clicked(self._on_solution_selected)
        self.solution_radio.ax.set_visible(self.mode == "IK")

    def _on_solution_selected(self, label: str) -> None:
        if not self.ik_solutions or label == "Sin soluciones":
            return
        try:
            index = int(label.split(":", 1)[0]) - 1
        except (ValueError, IndexError):
            return
        if 0 <= index < len(self.ik_solutions):
            self.selected_solution_index = index
            self.ghost_q = self.ik_solutions[index].q.copy()
            self._refresh()

    def _solve_ik(self, _event=None) -> None:
        target = _target_transform(self.target_position, self.target_rpy_deg)
        result = inverse_kinematics(
            target,
            GEOMETRY,
            q_current=self.q_current,
            joint_limits_rad=LIMITS_RAD,
        )

        self.ik_solutions = [s for s in result["solutions"] if s.valid]
        self.selected_solution_index = 0
        self._replace_solution_radio(self.ik_solutions)
        self.ghost_q = self.ik_solutions[0].q.copy() if self.ik_solutions else None
        self._refresh(extra_status=str(result["status"]))

    def _reach(self, _event=None) -> None:
        if not self.ik_solutions:
            self._solve_ik()
        if not self.ik_solutions:
            return

        solution = self.ik_solutions[self.selected_solution_index]
        q_start = self.q_current.copy()
        delta = _shortest_joint_delta(q_start, solution.q)
        frames = 50

        def update(frame: int):
            s = frame / (frames - 1)
            s = 3.0 * s * s - 2.0 * s * s * s
            self.q_current = q_start + s * delta
            self._append_trail()
            self._refresh()
            return ()

        self.animation = FuncAnimation(
            self.fig,
            update,
            frames=frames,
            interval=25,
            repeat=False,
            blit=False,
        )

    def _zero_configuration(self, _event=None) -> None:
        self.q_current = np.zeros(6, dtype=float)
        self.ghost_q = None
        self.tcp_trail.clear()
        self._updating_widgets = True
        try:
            for slider in self.joint_sliders:
                slider.set_val(0.0)
        finally:
            self._updating_widgets = False
        self._refresh()

    def _reset_view(self, _event=None) -> None:
        self.ax3d.view_init(elev=24, azim=-58)
        self.fig.canvas.draw_idle()

    def _append_trail(self) -> None:
        if not self.show_trail:
            return
        p = forward_kinematics(self.q_current, GEOMETRY)["p_tcp"]
        self.tcp_trail.append(p.copy())
        if len(self.tcp_trail) > 500:
            self.tcp_trail.pop(0)

    def _draw_frame(self, transform: np.ndarray, scale: float = 0.15) -> None:
        origin = transform[:3, 3]
        rotation = transform[:3, :3]
        for axis in range(3):
            vec = rotation[:, axis] * scale
            self.ax3d.quiver(
                origin[0],
                origin[1],
                origin[2],
                vec[0],
                vec[1],
                vec[2],
                normalize=False,
            )

    def _draw_robot(self, q: np.ndarray, ghost: bool = False) -> None:
        fk = forward_kinematics(q, GEOMETRY)
        points = fk["key_points"]
        alpha = 0.35 if ghost else 1.0
        linestyle = "--" if ghost else "-"

        self.ax3d.plot(
            points[:, 0],
            points[:, 1],
            points[:, 2],
            marker="o",
            linewidth=2.0,
            linestyle=linestyle,
            alpha=alpha,
        )
        self.ax3d.scatter(
            [points[-1, 0]],
            [points[-1, 1]],
            [points[-1, 2]],
            marker="x",
            s=70,
            alpha=alpha,
        )

        if self.show_frames and not ghost:
            for transform in fk["T"]:
                self._draw_frame(transform)
            self._draw_frame(fk["T_tcp"])

    def _refresh(self, extra_status: str | None = None) -> None:
        self.ax3d.cla()
        self._draw_robot(self.q_current)

        if self.ghost_q is not None:
            self._draw_robot(self.ghost_q, ghost=True)

        if self.show_target:
            self.ax3d.scatter(
                [self.target_position[0]],
                [self.target_position[1]],
                [self.target_position[2]],
                marker="x",
                s=100,
            )

        if self.show_trail and len(self.tcp_trail) >= 2:
            trail = np.vstack(self.tcp_trail)
            self.ax3d.plot(trail[:, 0], trail[:, 1], trail[:, 2], linewidth=1.0)

        lim = WORKSPACE_LIMIT
        self.ax3d.set_xlim(-lim, lim)
        self.ax3d.set_ylim(-lim, lim)
        self.ax3d.set_zlim(-lim, lim)
        self.ax3d.set_xlabel("X")
        self.ax3d.set_ylabel("Y")
        self.ax3d.set_zlabel("Z")
        self.ax3d.set_title(f"Modo {self.mode}")
        self.ax3d.set_box_aspect((1, 1, 1))

        fk = forward_kinematics(self.q_current, GEOMETRY)
        rpy = np.rad2deg(rotation_to_rpy_zyx(fk["R_tcp"]))

        status_lines = [
            f"TCP actual: [{fk['p_tcp'][0]: .3f}, {fk['p_tcp'][1]: .3f}, {fk['p_tcp'][2]: .3f}]",
            f"RPY actual: [{rpy[0]: .1f}, {rpy[1]: .1f}, {rpy[2]: .1f}] deg",
            f"q actual:   {np.array2string(np.rad2deg(self.q_current), precision=1)} deg",
        ]

        if self.mode == "IK":
            status_lines.append(
                f"Target:     [{self.target_position[0]: .3f}, {self.target_position[1]: .3f}, {self.target_position[2]: .3f}]"
            )
            if self.ik_solutions:
                s = self.ik_solutions[self.selected_solution_index]
                status_lines.append(
                    f"IK: {s.elbow_branch}/{s.wrist_branch} | ep={s.position_error:.2e} | eR={math.degrees(s.orientation_error):.2e} deg"
                )
                if s.wrist_singularity:
                    status_lines.append("Aviso: singularidad de muñeca.")
                if s.shoulder_singularity:
                    status_lines.append("Aviso: singularidad sobre eje del hombro.")
            elif extra_status:
                status_lines.append(f"IK STATUS: {extra_status}")

        self.status_text.set_text("\n".join(status_lines))
        self.fig.canvas.draw_idle()

    def show(self) -> None:
        self._reset_view()
        # block=True mantiene vivo el proceso hasta cerrar la ventana.
        plt.show(block=True)


def smoke_test() -> None:
    """Prueba de ejecución sin GUI interactiva."""
    q = np.deg2rad([25.0, 30.0, -55.0, 40.0, 35.0, -70.0])
    fk = forward_kinematics(q, GEOMETRY)
    ik = inverse_kinematics(
        fk["T_tcp"],
        GEOMETRY,
        q_current=np.zeros(6),
        joint_limits_rad=LIMITS_RAD,
    )
    valid = [s for s in ik["solutions"] if s.valid]
    if ik["status"] != "OK" or not valid:
        raise RuntimeError("Smoke test: IK no recuperó una solución válida.")

    best = min(valid, key=lambda s: s.position_error + s.orientation_error)
    if best.position_error > 1e-7 or best.orientation_error > 1e-7:
        raise RuntimeError("Smoke test: error FK/IK fuera de tolerancia.")

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    points = forward_kinematics(best.q, GEOMETRY)["key_points"]
    ax.plot(points[:, 0], points[:, 1], points[:, 2], marker="o")
    fig.canvas.draw()
    plt.close(fig)
    print("SMOKE TEST OK")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulador FK/IK del manipulador 6R")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Valida cálculo y render sin abrir la interfaz.",
    )
    parser.add_argument(
        "--diagnose-gui",
        action="store_true",
        help="Muestra el backend gráfico y el estado de Tk sin abrir el simulador.",
    )
    args = parser.parse_args()

    if args.diagnose_gui:
        print(f"Python: {sys.executable}")
        print(f"Matplotlib: {matplotlib.__version__}")
        print(f"Backend: {matplotlib.get_backend()}")
        print(f"Modo GUI: {_GUI_MODE}")
        print(f"CODESPACES: {os.environ.get('CODESPACES', 'false')}")
        print(f"DISPLAY: {os.environ.get('DISPLAY', '<no definido>')}")
        if _GUI_MODE == "web":
            print(f"WebAgg: OK -> puerto {WEBAGG_PORT}")
            print("En Codespaces abre la pestaña PORTS y abre ese puerto en el navegador.")
        elif _GUI_BACKEND_ERROR is None:
            print("Tk GUI: OK")
        else:
            print(f"Tk GUI: ERROR -> {_GUI_BACKEND_ERROR}")
        return

    if args.smoke_test:
        smoke_test()
        return

    if _GUI_BACKEND_ERROR is not None:
        raise RuntimeError(
            "No se pudo inicializar una ventana gráfica con Tk. "
            "Ejecuta: python -m simulation.arm_6r.simulator --diagnose-gui "
            "para ver el detalle."
        ) from _GUI_BACKEND_ERROR

    if _GUI_MODE == "web":
        print(f"Simulador 6R listo con WebAgg en el puerto {WEBAGG_PORT}.")
        print("En GitHub Codespaces abre la pestaña PORTS, localiza ese puerto y elige Open in Browser.")
        print("Deja esta terminal corriendo mientras uses el simulador.")
    else:
        print(f"Abriendo Simulador 6R con backend {matplotlib.get_backend()}...")

    Arm6RSimulator().show()


if __name__ == "__main__":
    main()
