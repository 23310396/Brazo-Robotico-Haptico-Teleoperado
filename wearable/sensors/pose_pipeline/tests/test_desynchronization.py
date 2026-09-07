import unittest

from wearable.sensors.pose_pipeline.analysis.desynchronization import (
    simulate_common_delay,
    simulate_relative_skew,
)


TOL = 1e-9


class DesynchronizationTests(unittest.TestCase):
    def test_cero_skew_no_produce_error(self):
        result = simulate_relative_skew(0.0)
        self.assertAlmostEqual(result.measured_skew_ms, 0.0, delta=TOL)
        self.assertAlmostEqual(result.position_error_mm, 0.0, delta=TOL)
        self.assertAlmostEqual(result.orientation_error_deg, 0.0, delta=TOL)

    def test_pipeline_reporta_el_skew_solicitado(self):
        result = simulate_relative_skew(20.0)
        self.assertAlmostEqual(result.requested_skew_ms, 20.0, delta=TOL)
        self.assertAlmostEqual(result.measured_skew_ms, 20.0, delta=1e-9)

    def test_skew_durante_movimiento_produce_error_de_pose(self):
        result = simulate_relative_skew(20.0)
        self.assertGreater(result.position_error_mm, 0.0)
        self.assertGreater(result.orientation_error_deg, 0.0)

    def test_skew_con_operador_quieto_no_cambia_pose(self):
        result = simulate_relative_skew(
            50.0,
            upper_velocity_deg_s=0.0,
            forearm_velocity_deg_s=0.0,
            hand_velocity_deg_s=0.0,
        )
        self.assertAlmostEqual(result.measured_skew_ms, 50.0, delta=1e-9)
        self.assertAlmostEqual(result.position_error_mm, 0.0, delta=TOL)
        self.assertAlmostEqual(result.orientation_error_deg, 0.0, delta=TOL)

    def test_mayor_skew_aumenta_error_con_misma_velocidad(self):
        low = simulate_relative_skew(5.0)
        high = simulate_relative_skew(50.0)
        self.assertGreater(high.position_error_mm, low.position_error_mm)
        self.assertGreater(high.orientation_error_deg, low.orientation_error_deg)

    def test_mayor_velocidad_aumenta_efecto_del_mismo_skew(self):
        slow = simulate_relative_skew(
            20.0,
            upper_velocity_deg_s=20.0,
            forearm_velocity_deg_s=40.0,
            hand_velocity_deg_s=50.0,
        )
        fast = simulate_relative_skew(
            20.0,
            upper_velocity_deg_s=80.0,
            forearm_velocity_deg_s=160.0,
            hand_velocity_deg_s=200.0,
        )
        self.assertGreater(fast.position_error_mm, slow.position_error_mm)
        self.assertGreater(fast.orientation_error_deg, slow.orientation_error_deg)

    def test_retardo_comun_tiene_skew_cero_pero_error_de_seguimiento(self):
        result = simulate_common_delay(20.0)
        self.assertAlmostEqual(result.measured_skew_ms, 0.0, delta=TOL)
        self.assertGreater(result.position_error_mm, 0.0)
        self.assertGreater(result.orientation_error_deg, 0.0)

    def test_parametros_temporales_negativos_se_rechazan(self):
        with self.assertRaises(ValueError):
            simulate_relative_skew(-1.0)
        with self.assertRaises(ValueError):
            simulate_common_delay(-1.0)


if __name__ == "__main__":
    unittest.main()
