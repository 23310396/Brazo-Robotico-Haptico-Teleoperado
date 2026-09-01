import unittest

from wearable.sensors.pose_pipeline.pipeline import (
    IDENTITY_Q,
    SegmentCalibration,
    UpperLimbModel,
    estimate_hand_pose,
    quaternion_multiply,
)
from wearable.sensors.pose_pipeline.synthetic import quaternion_from_axis_angle, synthetic_sample


TOL = 1e-9


def assert_vector_close(testcase, actual, expected, tol=TOL):
    for got, want in zip(actual, expected):
        testcase.assertAlmostEqual(got, want, delta=tol)


def assert_same_rotation(testcase, q1, q2, tol=TOL):
    # q y -q representan exactamente la misma rotación.
    dot = abs(sum(a * b for a, b in zip(q1, q2)))
    testcase.assertAlmostEqual(dot, 1.0, delta=tol)


class PosePipelineTests(unittest.TestCase):
    def setUp(self):
        self.model = UpperLimbModel(upper_arm_length_m=0.30, forearm_length_m=0.25)
        self.identity_cal = SegmentCalibration()

    def estimate(self, q_upper=IDENTITY_Q, q_fore=IDENTITY_Q, q_hand=IDENTITY_Q, **calibrations):
        return estimate_hand_pose(
            synthetic_sample("upper_arm", q_upper),
            synthetic_sample("forearm", q_fore),
            synthetic_sample("hand", q_hand),
            calibrations.get("upper", self.identity_cal),
            calibrations.get("fore", self.identity_cal),
            calibrations.get("hand", self.identity_cal),
            self.model,
        )

    def test_brazo_y_antebrazo_rectos_suman_longitudes(self):
        pose = self.estimate()
        assert_vector_close(self, pose.position_h_m, (0.55, 0.0, 0.0))
        assert_vector_close(self, pose.elbow_position_h_m, (0.30, 0.0, 0.0))

    def test_codo_a_90_grados_hacia_arriba(self):
        # Rotar +X hacia +Z requiere -90° alrededor de Y con nuestra convención.
        q_fore = quaternion_from_axis_angle((0.0, 1.0, 0.0), -90.0)
        pose = self.estimate(q_fore=q_fore)
        assert_vector_close(self, pose.position_h_m, (0.30, 0.0, 0.25))

    def test_rotar_solo_la_mano_no_mueve_la_muneca(self):
        base = self.estimate()
        q_hand = quaternion_from_axis_angle((1.0, 0.0, 0.0), 30.0)
        rotated = self.estimate(q_hand=q_hand)
        assert_vector_close(self, rotated.position_h_m, base.position_h_m)
        assert_same_rotation(self, rotated.orientation_h_wxyz, q_hand)

    def test_calibracion_corrige_sensor_montado_chueco(self):
        offset = quaternion_from_axis_angle((0.0, 0.0, 1.0), 20.0)
        correction = quaternion_from_axis_angle((0.0, 0.0, 1.0), -20.0)
        upper_cal = SegmentCalibration(q_s_b=correction)
        pose = self.estimate(q_upper=offset, upper=upper_cal)
        assert_vector_close(self, pose.elbow_position_h_m, (0.30, 0.0, 0.0))
        assert_vector_close(self, pose.position_h_m, (0.55, 0.0, 0.0))

    def test_quaternion_y_su_negativo_dan_la_misma_pose(self):
        q = quaternion_from_axis_angle((0.0, 0.0, 1.0), 45.0)
        negative_q = tuple(-v for v in q)
        pose_a = self.estimate(q_upper=q, q_fore=q, q_hand=q)
        pose_b = self.estimate(q_upper=negative_q, q_fore=negative_q, q_hand=negative_q)
        assert_vector_close(self, pose_a.position_h_m, pose_b.position_h_m)
        assert_same_rotation(self, pose_a.orientation_h_wxyz, pose_b.orientation_h_wxyz)

    def test_reporta_desincronizacion_entre_sensores(self):
        pose = estimate_hand_pose(
            synthetic_sample("upper_arm", IDENTITY_Q, 1.000),
            synthetic_sample("forearm", IDENTITY_Q, 1.015),
            synthetic_sample("hand", IDENTITY_Q, 1.010),
            self.identity_cal,
            self.identity_cal,
            self.identity_cal,
            self.model,
        )
        self.assertAlmostEqual(pose.sensor_time_skew_s, 0.015, delta=TOL)
        self.assertAlmostEqual(pose.timestamp_s, 1.015, delta=TOL)

    def test_longitudes_invalidas_se_rechazan(self):
        with self.assertRaises(ValueError):
            UpperLimbModel(0.0, 0.25)
        with self.assertRaises(ValueError):
            UpperLimbModel(0.30, -0.25)

    def test_quaternion_cero_se_rechaza(self):
        with self.assertRaises(ValueError):
            self.estimate(q_upper=(0.0, 0.0, 0.0, 0.0))

    def test_composicion_de_calibracion_y_sensor(self):
        q_sensor = quaternion_from_axis_angle((0.0, 0.0, 1.0), 10.0)
        q_correction = quaternion_from_axis_angle((0.0, 0.0, 1.0), -10.0)
        composed = quaternion_multiply(q_sensor, q_correction)
        assert_same_rotation(self, composed, IDENTITY_Q)


if __name__ == "__main__":
    unittest.main()
