"""Interfaz web del banco de pruebas cinemático 6R.

Se ejecuta mediante:
    python -m simulation.arm_6r.simulator

La FK/IK viven en robot/kinematics. Este archivo sólo maneja la interfaz.
"""

from __future__ import annotations

import math

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
import streamlit.components.v1 as components

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
ANIMATION_FRAMES = 60
ANIMATION_DURATION_MS = 2500

# Paleta fija para que la vista normal y la animación se vean iguales.
PLOT_BG = "#0E1117"
PLOT_TEXT = "#FAFAFA"
PLOT_GRID = "#2B3139"
ROBOT_COLOR = "#6EC5FF"
TCP_COLOR = "#1F9CF0"
TARGET_COLOR = "#FF4B4B"
GHOST_COLOR = "#8A6F75"
TRAIL_COLOR = "#7EC8E3"

TEST_PRESETS = {
    "A — alcanzable frontal": {
        "position": np.array([1.50, 0.50, 0.70], dtype=float),
        "rpy": np.array([0.0, 0.0, 0.0], dtype=float),
    },
    "B — alcanzable lateral": {
        "position": np.array([0.90, -1.10, 0.80], dtype=float),
        "rpy": np.array([0.0, 0.0, 0.0], dtype=float),
    },
    "C — plegado extremo": {
        "position": np.array([0.35, 0.05, 0.30], dtype=float),
        "rpy": np.array([0.0, 0.0, 0.0], dtype=float),
    },
    "D — inalcanzable": {
        "position": np.array([2.60, 0.00, 0.25], dtype=float),
        "rpy": np.array([0.0, 0.0, 0.0], dtype=float),
    },
}


def target_transform(position: np.ndarray, rpy_deg: np.ndarray) -> np.ndarray:
    t = np.eye(4, dtype=float)
    t[:3, :3] = rpy_zyx_to_rotation(*np.deg2rad(rpy_deg))
    t[:3, 3] = position
    return t


def shortest_joint_delta(q_from: np.ndarray, q_to: np.ndarray) -> np.ndarray:
    return (q_to - q_from + math.pi) % (2.0 * math.pi) - math.pi


def _sync_pair(source_key: str, target_key: str) -> None:
    """Sincroniza dos widgets que representan exactamente la misma variable."""
    st.session_state[target_key] = float(st.session_state[source_key])


def _set_pair(base_key: str, value: float) -> None:
    st.session_state[f"{base_key}_slider"] = float(value)
    st.session_state[f"{base_key}_number"] = float(value)


def _get_pair(base_key: str) -> float:
    return float(st.session_state[f"{base_key}_number"])


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

    for i, angle in enumerate(np.rad2deg(st.session_state.q_current)):
        for suffix in ("slider", "number"):
            key = f"joint_{i}_{suffix}"
            if key not in st.session_state:
                st.session_state[key] = float(angle)

    target_defaults = {
        "target_x": float(st.session_state.target_position[0]),
        "target_y": float(st.session_state.target_position[1]),
        "target_z": float(st.session_state.target_position[2]),
        "target_roll": float(st.session_state.target_rpy_deg[0]),
        "target_pitch": float(st.session_state.target_rpy_deg[1]),
        "target_yaw": float(st.session_state.target_rpy_deg[2]),
    }
    for base_key, value in target_defaults.items():
        for suffix in ("slider", "number"):
            key = f"{base_key}_{suffix}"
            if key not in st.session_state:
                st.session_state[key] = value

    defaults = {
        "ik_solutions": [],
        "ik_status": "Sin resolver",
        "ik_reason": None,
        "solved_signature": None,
        "selected_solution": 0,
        "trail": [],
        "preset_select": "A — alcanzable frontal",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def sync_joint_widgets() -> None:
    for i, angle in enumerate(np.rad2deg(st.session_state.q_current)):
        _set_pair(f"joint_{i}", float(angle))


def clear_ik_result() -> None:
    st.session_state.ik_solutions = []
    st.session_state.ik_status = "Sin resolver"
    st.session_state.ik_reason = None
    st.session_state.solved_signature = None
    st.session_state.selected_solution = 0


def set_zero() -> None:
    st.session_state.q_current = np.zeros(6, dtype=float)
    st.session_state.trail = []
    clear_ik_result()
    sync_joint_widgets()


def set_target_values(position: np.ndarray, rpy_deg: np.ndarray) -> None:
    position = np.asarray(position, dtype=float)
    rpy_deg = np.asarray(rpy_deg, dtype=float)

    st.session_state.target_position = position.copy()
    st.session_state.target_rpy_deg = rpy_deg.copy()

    for base_key, value in zip(
        ("target_x", "target_y", "target_z"),
        position,
    ):
        _set_pair(base_key, float(value))

    for base_key, value in zip(
        ("target_roll", "target_pitch", "target_yaw"),
        rpy_deg,
    ):
        _set_pair(base_key, float(value))

    clear_ik_result()


def set_target_from_current_pose() -> None:
    """Copia la pose FK actual al target sin redondear los valores internos."""
    fk = forward_kinematics(st.session_state.q_current, GEOMETRY)
    position = fk["p_tcp"].copy()
    rpy_deg = np.rad2deg(rotation_to_rpy_zyx(fk["R_tcp"]))
    set_target_values(position, rpy_deg)


def load_selected_preset() -> None:
    preset = TEST_PRESETS[st.session_state.preset_select]
    set_target_values(preset["position"], preset["rpy"])


def paired_control(
    label: str,
    base_key: str,
    minimum: float,
    maximum: float,
    *,
    slider_step: float,
    number_step: float,
    number_format: str,
) -> float:
    """Dibuja slider + entrada numérica sincronizados."""
    st.markdown(f"**{label}**")
    col_slider, col_number = st.columns([3.2, 1.15], gap="small")

    slider_key = f"{base_key}_slider"
    number_key = f"{base_key}_number"

    with col_slider:
        st.slider(
            f"{label} slider",
            minimum,
            maximum,
            step=slider_step,
            key=slider_key,
            label_visibility="collapsed",
            on_change=_sync_pair,
            args=(slider_key, number_key),
        )

    with col_number:
        st.number_input(
            f"{label} exacto",
            min_value=minimum,
            max_value=maximum,
            step=number_step,
            format=number_format,
            key=number_key,
            label_visibility="collapsed",
            on_change=_sync_pair,
            args=(number_key, slider_key),
        )

    return _get_pair(base_key)


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
            marker=dict(size=6, color=ROBOT_COLOR),
            line=dict(width=7, color=ROBOT_COLOR),
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=[points[-1, 0]],
            y=[points[-1, 1]],
            z=[points[-1, 2]],
            mode="markers",
            name="TCP",
            marker=dict(size=8, symbol="diamond", color=TCP_COLOR),
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
                marker=dict(size=5, color=GHOST_COLOR),
                line=dict(width=5, dash="dash", color=GHOST_COLOR),
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
                marker=dict(size=9, symbol="x", color=TARGET_COLOR),
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
                line=dict(width=3, color=TRAIL_COLOR),
            )
        )

    lim = WORKSPACE_LIMIT
    axis_style = dict(
        backgroundcolor=PLOT_BG,
        gridcolor=PLOT_GRID,
        zerolinecolor=PLOT_GRID,
        color=PLOT_TEXT,
    )

    fig.update_layout(
        template="plotly_dark",
        height=690,
        margin=dict(l=0, r=0, b=0, t=35),
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=PLOT_TEXT),
        scene=dict(
            bgcolor=PLOT_BG,
            xaxis=dict(title="X", range=[-lim, lim], **axis_style),
            yaxis=dict(title="Y", range=[-lim, lim], **axis_style),
            zaxis=dict(title="Z", range=[-lim, lim], **axis_style),
            aspectmode="cube",
        ),
        legend=dict(
            orientation="h",
            font=dict(color=PLOT_TEXT),
            bgcolor="rgba(0,0,0,0)",
        ),
        uirevision="keep-camera",
    )
    return fig


def build_animation_html(
    q_start: np.ndarray,
    q_end: np.ndarray,
    *,
    target_position: np.ndarray | None,
    target_rotation: np.ndarray | None,
) -> tuple[str, list[np.ndarray]]:
    """Genera todos los frames una sola vez y deja la reproducción al navegador."""
    delta = shortest_joint_delta(q_start, q_end)
    q_path: list[np.ndarray] = []

    for index in range(ANIMATION_FRAMES):
        u = index / (ANIMATION_FRAMES - 1)
        smooth = 3.0 * u * u - 2.0 * u * u * u
        q_path.append(q_start + smooth * delta)

    fig = build_figure(
        q_path[0],
        target_position=target_position,
        target_rotation=target_rotation,
        show_frames=False,
        trail=None,
    )

    frames: list[go.Frame] = []
    for index, q in enumerate(q_path):
        fk = forward_kinematics(q, GEOMETRY)
        points = fk["key_points"]
        frames.append(
            go.Frame(
                name=str(index),
                traces=[0, 1],
                data=[
                    go.Scatter3d(
                        x=points[:, 0],
                        y=points[:, 1],
                        z=points[:, 2],
                        mode="lines+markers",
                        marker=dict(size=6, color=ROBOT_COLOR),
                        line=dict(width=7, color=ROBOT_COLOR),
                    ),
                    go.Scatter3d(
                        x=[points[-1, 0]],
                        y=[points[-1, 1]],
                        z=[points[-1, 2]],
                        mode="markers",
                        marker=dict(size=8, symbol="diamond", color=TCP_COLOR),
                    ),
                ],
            )
        )

    fig.frames = frames
    frame_ms = int(round(ANIMATION_DURATION_MS / (ANIMATION_FRAMES - 1)))

    html = pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs=True,
        auto_play=True,
        animation_opts={
            "frame": {"duration": frame_ms, "redraw": True},
            "transition": {"duration": 0},
            "fromcurrent": True,
            "mode": "immediate",
        },
        config={"responsive": True, "displaylogo": False},
    )
    html = (
        f"<style>html,body{{margin:0;background:{PLOT_BG};color:{PLOT_TEXT};}}</style>"
        + html
    )
    return html, q_path


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
    st.session_state.ik_reason = result.get("reason")
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


def ik_status_values(
    signature_ok: bool,
    solution: IKSolution | None,
) -> tuple[str, str, str]:
    if not signature_ok:
        return "PENDIENTE", "SIN RESOLVER", "—"

    status = st.session_state.ik_status
    if status == "UNREACHABLE":
        return "INALCANZABLE", "UNREACHABLE", "—"
    if status == "NO_VALID_SOLUTION":
        return "ALCANZABLE*", "SIN SOLUCIÓN VÁLIDA", "—"
    if solution is None:
        return "PENDIENTE", status.upper(), "—"

    singularities: list[str] = []
    if solution.wrist_singularity:
        singularities.append("MUÑECA")
    if solution.shoulder_singularity:
        singularities.append("HOMBRO")

    singularity_text = " + ".join(singularities) if singularities else "NO"
    return "ALCANZABLE", "OK", singularity_text


st.set_page_config(page_title="Simulador 6R", layout="wide")
ensure_state()

st.title("Simulador 6R — banco de pruebas cinemático v2")
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
    st.button(
        "Configuración cero",
        use_container_width=True,
        on_click=set_zero,
    )

if mode == "FK":
    with st.sidebar:
        st.subheader("Articulaciones")
        values_deg: list[float] = []

        for i in range(6):
            values_deg.append(
                paired_control(
                    f"J{i + 1} [°]",
                    f"joint_{i}",
                    float(DEMO_LIMITS_DEG[i, 0]),
                    float(DEMO_LIMITS_DEG[i, 1]),
                    slider_step=0.01,
                    number_step=0.01,
                    number_format="%.2f",
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

    st.plotly_chart(
        build_figure(
            st.session_state.q_current,
            show_frames=show_frames,
            trail=st.session_state.trail if show_trail else None,
        ),
        use_container_width=True,
    )

else:
    with st.sidebar:
        st.button(
            "Usar pose actual como target",
            use_container_width=True,
            on_click=set_target_from_current_pose,
        )

        st.subheader("Casos de prueba")
        st.selectbox(
            "Preset",
            options=list(TEST_PRESETS.keys()),
            key="preset_select",
        )
        st.button(
            "Cargar preset",
            use_container_width=True,
            on_click=load_selected_preset,
        )

        st.subheader("Target — posición")
        x = paired_control(
            "X",
            "target_x",
            -WORKSPACE_LIMIT,
            WORKSPACE_LIMIT,
            slider_step=0.001,
            number_step=0.001,
            number_format="%.4f",
        )
        y = paired_control(
            "Y",
            "target_y",
            -WORKSPACE_LIMIT,
            WORKSPACE_LIMIT,
            slider_step=0.001,
            number_step=0.001,
            number_format="%.4f",
        )
        z = paired_control(
            "Z",
            "target_z",
            -WORKSPACE_LIMIT,
            WORKSPACE_LIMIT,
            slider_step=0.001,
            number_step=0.001,
            number_format="%.4f",
        )
        target_position = np.array([x, y, z], dtype=float)
        st.session_state.target_position = target_position

        st.subheader("Target — orientación")
        roll = paired_control(
            "Roll [°]",
            "target_roll",
            -180.0,
            180.0,
            slider_step=0.01,
            number_step=0.01,
            number_format="%.2f",
        )
        pitch = paired_control(
            "Pitch [°]",
            "target_pitch",
            -180.0,
            180.0,
            slider_step=0.01,
            number_step=0.01,
            number_format="%.2f",
        )
        yaw = paired_control(
            "Yaw [°]",
            "target_yaw",
            -180.0,
            180.0,
            slider_step=0.01,
            number_step=0.01,
            number_format="%.2f",
        )
        target_rpy = np.array([roll, pitch, yaw], dtype=float)
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
            f"{i + 1}: {solution.elbow_branch} / {solution.wrist_branch}"
            for i, solution in enumerate(solutions)
        ]
        st.radio(
            "Solución IK",
            options=list(range(len(labels))),
            format_func=lambda index: labels[index],
            horizontal=True,
            key="selected_solution",
        )

    solution = selected_solution() if signature_ok else None
    ghost_q = solution.q if solution is not None else None
    target = target_transform(target_position, target_rpy)

    plot_slot = st.empty()

    col_reach, col_target, col_ik, col_sing = st.columns([1.1, 1, 1, 1])
    with col_reach:
        reach_pressed = st.button(
            "Alcanzar",
            disabled=solution is None,
            use_container_width=True,
        )

    target_status, ik_status, singularity_status = ik_status_values(
        signature_ok,
        solution,
    )
    with col_target:
        st.metric("TARGET", target_status)
    with col_ik:
        st.metric("IK", ik_status)
    with col_sing:
        st.metric("SINGULARIDAD", singularity_status)

    if reach_pressed and solution is not None:
        animation_html, q_path = build_animation_html(
            st.session_state.q_current.copy(),
            solution.q.copy(),
            target_position=target[:3, 3] if show_target else None,
            target_rotation=target[:3, :3] if show_target else None,
        )

        if show_trail:
            for q_step in q_path:
                tcp = forward_kinematics(q_step, GEOMETRY)["p_tcp"]
                st.session_state.trail.append(tcp.copy())
            st.session_state.trail = st.session_state.trail[-500:]

        st.session_state.q_current = solution.q.copy()
        sync_joint_widgets()

        with plot_slot.container():
            components.html(
                animation_html,
                height=700,
                scrolling=False,
            )
    else:
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

    if st.session_state.ik_reason:
        st.caption(st.session_state.ik_reason)

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
    if (
        solution is not None
        and st.session_state.solved_signature == current_target_signature()
    ):
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
