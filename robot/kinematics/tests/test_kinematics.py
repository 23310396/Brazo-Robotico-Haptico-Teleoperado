import math

import numpy as np

from robot.kinematics.forward_kinematics import (
    forward_kinematics,
    orientation_error_angle,
)
from robot.kinematics.inverse_kinematics import inverse_kinematics
from robot.kinematics.model_6r import DEMO_GEOMETRY, DEMO_LIMITS_DEG


LIMITS_RAD = np.deg2rad(DEMO_LIMITS_DEG)


def test_zero_configuration_tcp_position():
    fk = forward_kinematics(np.zeros(6), DEMO_GEOMETRY)
    expected = np.array(
        [
            DEMO_GEOMETRY.l1 + DEMO_GEOMETRY.l2 + DEMO_GEOMETRY.lt,
            0.0,
            0.0,
        ]
    )
    assert np.allclose(fk["p_tcp"], expected, atol=1e-10)


def test_wrist_center_does_not_move_with_wrist_joints():
    base = np.deg2rad([20.0, 35.0, -50.0, 0.0, 0.0, 0.0])
    moved = base.copy()
    moved[3:] = np.deg2rad([70.0, -40.0, 110.0])
    p1 = forward_kinematics(base, DEMO_GEOMETRY)["p_wrist"]
    p2 = forward_kinematics(moved, DEMO_GEOMETRY)["p_wrist"]
    assert np.allclose(p1, p2, atol=1e-10)


def test_fk_ik_fk_round_trip_general_pose():
    q_source = np.deg2rad([25.0, 30.0, -55.0, 40.0, 35.0, -70.0])
    target = forward_kinematics(q_source, DEMO_GEOMETRY)["T_tcp"]
    result = inverse_kinematics(
        target,
        DEMO_GEOMETRY,
        q_current=np.zeros(6),
        joint_limits_rad=LIMITS_RAD,
    )
    assert result["status"] == "OK"
    valid = [s for s in result["solutions"] if s.valid]
    assert valid
    best = min(valid, key=lambda s: s.position_error + s.orientation_error)
    fk_check = forward_kinematics(best.q, DEMO_GEOMETRY)
    assert np.linalg.norm(fk_check["p_tcp"] - target[:3, 3]) < 1e-8
    assert orientation_error_angle(target[:3, :3], fk_check["R_tcp"]) < 1e-8


def test_unreachable_target_is_reported():
    target = np.eye(4)
    target[:3, 3] = np.array([10.0, 0.0, 0.0])
    result = inverse_kinematics(target, DEMO_GEOMETRY)
    assert result["status"] == "UNREACHABLE"
    assert result["solutions"] == []


def test_wrist_singularity_is_detected_from_fk_target():
    q_source = np.deg2rad([15.0, 20.0, -35.0, 25.0, 0.0, 50.0])
    target = forward_kinematics(q_source, DEMO_GEOMETRY)["T_tcp"]
    result = inverse_kinematics(
        target,
        DEMO_GEOMETRY,
        q_current=q_source,
        joint_limits_rad=LIMITS_RAD,
    )
    assert result["status"] == "OK"
    assert any(s.wrist_singularity for s in result["solutions"])


def test_rotation_matrices_are_proper():
    q = np.deg2rad([10.0, -20.0, 30.0, 40.0, -50.0, 60.0])
    r = forward_kinematics(q, DEMO_GEOMETRY)["R_tcp"]
    assert np.allclose(r.T @ r, np.eye(3), atol=1e-10)
    assert math.isclose(float(np.linalg.det(r)), 1.0, abs_tol=1e-10)
