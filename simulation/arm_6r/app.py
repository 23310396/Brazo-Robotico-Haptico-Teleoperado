"""Interfaz web del banco de pruebas cinemático 6R.

Se ejecuta mediante:
    python -m simulation.arm_6r.simulator

La FK/IK viven en robot/kinematics. Este archivo sólo maneja la interfaz.
"""

from __future__ import annotations

import math
import time

import numpy as np
import plotly.graph_objects as go
import streamlit as st

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


def target_transform(position: np.ndarray, rpy_deg: np.ndarray) -> np.ndarray:
    t = np.eye(4, dtype=float)
    t[:3, :3] = rpy_zyx_to_rotation(*np.deg2rad(rpy_deg))
    t[:3, 3] = position
    return t


def shortest_joint_delta(q_from: np.ndarray, q_to: np.ndarray) -> np.ndarray:
    return (q_to - q_from + math.pi) % (2.0 * math.pi) - math.pi


def ensure_state() -> None:
    if "q_current" not in st.session_state:
        st.session_state.q_current = np.zeros(6, dtype=float)

    fk0 = forward_kinematics(st.session_state.q_current, GEOMETRY)

    if "target_position" not in st.session_state:
        st.session_state.target_position = fk0["p_tcp"].copy()
    if "target_rpy_deg" not in st.session_state:
        st.session_state.target_rpy_deg = np.rad2deg(
            rotation_to_rpy_zyx(fk0["R_tcp"])
        )

    target_defaults = {
        "target_x": float(st.session_state.target_position[0]),
        "target_y": float(st.session_state.target_position[1]),
        "target_z": float(st.session_state.target_position[2]),
        "target_roll": float(st.session_state.target_rpy_deg[0]),
        "target_pitch": float(st.session_state.target_rpy_deg[1]),
        "target_yaw": float(st.session_state.target_rpy_deg[2]),
    }
    for key, value in target_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "ik_solutions" not in st.session_state:
        st.session_state.ik_solutions = []
    if "ik_status" not in st.session_state:
        st.session_state.ik_status = "Sin resolver"
    if "solved_signature" not in st.session_state:
        st.session_state.solved_signature = None
    if "selected_solution" not in st.session_state:
        st.session_state.selected_solution = 0
    if "trail" not in st.session_state:
        st.session_state.trail = []

    for i, angle in enumerate(np.rad2deg(st.session_state.q_current)):
        key = f"joint_{i}"
        if key not in st.session_state:
            st.session_state[key] = float(angle)


def sync_joint_widgets() -> None:
    for i, angle in enumerate(np.rad2deg(st.session_state.q_current)):
        st.session_state[f"joint_{i}"] = float(angle)


def set_zero() -> None:
    st.session_state.q_current = np.zeros(6, dtype=float)
    st.session_state.trail = []
    st.session_state.ik_solutions = []
    st.session_state.ik_status = "Sin resolver"
    sync_joint_widgets()


def add_frame(fig: go.Figure, transform: np.ndarray, scale: float = 0.16) -> None:
    origin = transform[:3, 3]
    rotation = transform[:3, :3]
    names = ("x", "y", "z")
    for axis, name in enumerate(names):
        endpoint = origin + scale * rotation[:, axis]
        fig.add_trace(
            go.Scatter3d(
                x=[origin[0], endpoint[0]],
                y=[origin[1], endpoint[1]],
                z=[origin[2], endpoint[2]],
                mode="lines",
                name=f"frame {name}",
                showlegend=False,
                hoverinfo="skip",
                line=dict(width=4),
            )
        )


def build_figure(
    q_current: np.ndarray,
    *,
    ghost_q: np.ndarray | None = None,
    target_position: np.ndarray | None = None,
    target_rotation: np.ndarray | None = None,
    show_frames: bool = False,
    trail: list[np.ndarray] | None = None,
) -> go.Figure:
    fig = go.Figure()
    fk = forward_kinematics(q_current, GEOMETRY)
    points = fk["key_points"]

    fig.add_trace(
        go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode="lines+markers",
            name="Robot actual",
            marker=dict(size=6),
            line=dict(width=7),
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=[points[-1, 0]],
            y=[points[-1, 1]],
            z=[points[-1, 2]],
            mode="markers",
            name="TCP",
            marker=dict(size=8, symbol="diamond"),
        )
    )

    if ghost_q is not None:
        ghost = forward_kinematics(ghost_q, GEOMETRY)["key_points"]
        fig.add_trace(
            go.Scatter3d(
                x=ghost[:, 0],
                y=ghost[:, 1],
                z=ghost[:, 2],
                mode="lines+markers",
                name="Solución IK",
                marker=dict(size=5),
                line=dict(width=5, dash="dash"),
                opacity=0.4,
            )
        )

    if target_position is not None:
        fig.add_trace(
            go.Scatter3d(
                x=[target_position[0]],
                y=[target_position[1]],
                z=[target_position[2]],
                mode="markers",
                name="Target",
                marker=dict(size=9, symbol="x"),
            )
        )
        if target_rotation is not None:
            t_target = np.eye(4, dtype=float)
            t_target[:3, :3] = target_rotation
            t_target[:3, 3] = target_position
            add_frame(fig, t_target, scale=0.20)

    if show_frames:
        for transform in fk["T"]:
            add_frame(fig, transform)
        add_frame(fig, fk["T_tcp"])

    if trail and len(trail) >= 2:
        arr = np.vstack(trail)
        fig.add_trace(
            go.Scatter3d(
                x=arr[:, 0],
                y=arr[:, 1],
                z=arr[:, 2],
                mode="lines",
                name="Trayectoria TCP",
                line=dict(width=3),
            )
        )

    lim = WORKSPACE_LIMIT
    fig.update_layout(
        height=690,
        margin=dict(l=0, r=0, b=0, t=35),
        scene=dict(
            xaxis=dict(title="X", range=[-lim, lim]),
            yaxis=dict(title="Y", range=[-lim, lim]),
            zaxis=dict(title="Z", range=[-lim, lim]),
            aspectmode="cube",
        ),
        legend=dict(orientation="h"),
        uirevision="keep-camera",
    )
    return fig


def current_target_signature() -> tuple[float, ...]:
    return tuple(
        np.round(
            np.concatenate(
                [
                    np.asarray(st.session_state.target_position, dtype=float),
                    np.asarray(st.session_state.target_rpy_deg, dtype=float),
                ]
            ),
            8,
        )
    )


def resolve_ik() -> None:
    target = target_transform(
        np.asarray(st.session_state.target_position, dtype=float),
        np.asarray(st.session_state.target_rpy_deg, dtype=float),
    )
    result = inverse_kinematics(
        target,
        GEOMETRY,
        q_current=st.session_state.q_current,
        joint_limits_rad=LIMITS_RAD,
    )
    valid = [solution for solution in result["solutions"] if solution.valid]
    st.session_state.ik_solutions = valid
    st.session_state.ik_status = str(result["status"])
    st.session_state.selected_solution = 0
    st.session_state.solved_signature = current_target_signature()


def selected_solution() -> IKSolution | None:
    solutions: list[IKSolution] = st.session_state.ik_solutions
    if not solutions:
        return None
    index = int(st.session_state.selected_solution)
    if index < 0 or index >= len(solutions):
        return solutions[0]
    return solutions[index]


def animate_to_solution(placeholder) -> None:
    solution = selected_solution()
    if solution is None:
        return

    q_start = st.session_state.q_current.copy()
    delta = shortest_joint_delta(q_start, solution.q)
    frames = 35
    trail_enabled = st.session_state.get("show_trail", False)

    for frame in range(frames):
        u = frame / (frames - 1)
        smooth = 3.0 * u * u - 2.0 * u * u * u
        q = q_start + smooth * delta
        if trail_enabled:
            tcp = forward_kinematics(q, GEOMETRY)["p_tcp"]
            st.session_state.trail.append(tcp.copy())
            st.session_state.trail = st.session_state.trail[-500:]

        target = target_transform(
            np.asarray(st.session_state.target_position, dtype=float),
            np.asarray(st.session_state.target_rpy_deg, dtype=float),
        )
        placeholder.plotly_chart(
            build_figure(
                q,
                target_position=target[:3, 3],
                target_rotation=target[:3, :3],
                show_frames=st.session_state.get("show_frames", False),
                trail=st.session_state.trail,
            ),
            use_container_width=True,
        )
        time.sleep(0.025)

    st.session_state.q_current = solution.q.copy()
    sync_joint_widgets()


st.set_page_config(page_title="Simulador 6R", layout="wide")
ensure_state()

st.title("Simulador 6R — banco de pruebas cinemático")
st.caption(
    "DEMO SINTÉTICA: L1 = 1.0, L2 = 1.0, LT = 0.25. "
    "Estos valores no son dimensiones del manipulador físico."
)

with st.sidebar:
    st.header("Control")
    mode = st.radio("Modo", ("FK", "IK"), horizontal=True)
    show_frames = st.checkbox("Mostrar frames", key="show_frames")
    show_trail = st.checkbox("Trayectoria TCP", key="show_trail")
    show_target = st.checkbox("Mostrar target", value=True, key="show_target")

    if st.button("Configuración cero", use_container_width=True, on_click=set_zero):
        pass

if mode == "FK":
    with st.sidebar:
        st.subheader("Articulaciones")
        values_deg = []
        for i in range(6):
            values_deg.append(
                st.slider(
                    f"J{i + 1} [°]",
                    float(DEMO_LIMITS_DEG[i, 0]),
                    float(DEMO_LIMITS_DEG[i, 1]),
                    step=0.5,
                    key=f"joint_{i}",
                )
            )

    st.session_state.q_current = np.deg2rad(np.asarray(values_deg, dtype=float))
    if show_trail:
        tcp = forward_kinematics(st.session_state.q_current, GEOMETRY)["p_tcp"]
        if not st.session_state.trail or np.linalg.norm(
            tcp - st.session_state.trail[-1]
        ) > 1e-6:
            st.session_state.trail.append(tcp.copy())
            st.session_state.trail = st.session_state.trail[-500:]

    plot_slot = st.empty()
    plot_slot.plotly_chart(
        build_figure(
            st.session_state.q_current,
            show_frames=show_frames,
            trail=st.session_state.trail if show_trail else None,
        ),
        use_container_width=True,
    )

else:
    with st.sidebar:
        st.subheader("Target — posición")
        target_position = np.array(
            [
                st.slider(
                    "X",
                    -WORKSPACE_LIMIT,
                    WORKSPACE_LIMIT,
                    value=float(st.session_state.target_position[0]),
                    step=0.01,
                    key="target_x",
                ),
                st.slider(
                    "Y",
                    -WORKSPACE_LIMIT,
                    WORKSPACE_LIMIT,
                    value=float(st.session_state.target_position[1]),
                    step=0.01,
                    key="target_y",
                ),
                st.slider(
                    "Z",
                    -WORKSPACE_LIMIT,
                    WORKSPACE_LIMIT,
                    value=float(st.session_state.target_position[2]),
                    step=0.01,
                    key="target_z",
                ),
            ],
            dtype=float,
        )
        st.session_state.target_position = target_position

        st.subheader("Target — orientación")
        target_rpy = np.array(
            [
                st.slider(
                    "Roll [°]",
                    -180.0,
                    180.0,
                    value=float(st.session_state.target_rpy_deg[0]),
                    step=1.0,
                    key="target_roll",
                ),
                st.slider(
                    "Pitch [°]",
                    -180.0,
                    180.0,
                    value=float(st.session_state.target_rpy_deg[1]),
                    step=1.0,
                    key="target_pitch",
                ),
                st.slider(
                    "Yaw [°]",
                    -180.0,
                    180.0,
                    value=float(st.session_state.target_rpy_deg[2]),
                    step=1.0,
                    key="target_yaw",
                ),
            ],
            dtype=float,
        )
        st.session_state.target_rpy_deg = target_rpy

        if st.button("Resolver IK", type="primary", use_container_width=True):
            resolve_ik()

    signature_ok = st.session_state.solved_signature == current_target_signature()
    solutions: list[IKSolution] = (
        st.session_state.ik_solutions if signature_ok else []
    )

    if st.session_state.solved_signature is not None and not signature_ok:
        st.info("El target cambió. Presiona **Resolver IK** otra vez.")

    if solutions:
        labels = [
            f"{i + 1}: {s.elbow_branch} / {s.wrist_branch}"
            for i, s in enumerate(solutions)
        ]
        chosen = st.radio(
            "Solución IK",
            options=list(range(len(labels))),
            format_func=lambda i: labels[i],
            horizontal=True,
            key="selected_solution",
        )
        st.session_state.selected_solution = chosen

    solution = selected_solution() if signature_ok else None
    ghost_q = solution.q if solution is not None else None
    target = target_transform(target_position, target_rpy)

    plot_slot = st.empty()
    plot_slot.plotly_chart(
        build_figure(
            st.session_state.q_current,
            ghost_q=ghost_q,
            target_position=target[:3, 3] if show_target else None,
            target_rotation=target[:3, :3] if show_target else None,
            show_frames=show_frames,
            trail=st.session_state.trail if show_trail else None,
        ),
        use_container_width=True,
    )

    col_reach, col_status = st.columns([1, 3])
    with col_reach:
        reach_pressed = st.button(
            "Alcanzar",
            disabled=solution is None,
            use_container_width=True,
        )
    with col_status:
        st.write(f"**IK status:** {st.session_state.ik_status}")

    if reach_pressed and solution is not None:
        animate_to_solution(plot_slot)
        st.rerun()

fk_current = forward_kinematics(st.session_state.q_current, GEOMETRY)
rpy_current = np.rad2deg(rotation_to_rpy_zyx(fk_current["R_tcp"]))

st.divider()
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("TCP actual")
    st.code(
        "X = {:.4f}\nY = {:.4f}\nZ = {:.4f}".format(*fk_current["p_tcp"])
    )
with c2:
    st.subheader("Orientación actual")
    st.code(
        "Roll  = {:.2f}°\nPitch = {:.2f}°\nYaw   = {:.2f}°".format(
            *rpy_current
        )
    )
with c3:
    st.subheader("q actual")
    st.code(np.array2string(np.rad2deg(st.session_state.q_current), precision=2))

if mode == "IK":
    solution = selected_solution()
    if solution is not None and st.session_state.solved_signature == current_target_signature():
        st.write(
            f"**Verificación FK de la solución:** "
            f"error de posición = {solution.position_error:.3e}; "
            f"error de orientación = {math.degrees(solution.orientation_error):.3e}°."
        )
        if solution.wrist_singularity:
            st.warning("La solución está en singularidad de muñeca.")
        if solution.shoulder_singularity:
            st.warning("El centro de muñeca está sobre el eje del hombro.")

st.caption(
    "La animación de Alcanzar es una interpolación articular para visualización. "
    "No es planeación de trayectoria ni control del robot físico."
)
