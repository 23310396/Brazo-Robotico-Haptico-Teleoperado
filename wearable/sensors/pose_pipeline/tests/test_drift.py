import unittest

from wearable.sensors.pose_pipeline.analysis.drift import simulate_linear_drift


TOL = 1e-9


class DriftTests(unittest.TestCase):
    def test_cero_drift_no_produce_error(self):
        result = simulate_linear_drift("brazo", 0.0)
        self.assertAlmostEqual(result.position_rms_error_mm, 0.0, delta=TOL)
        self.assertAlmostEqual(result.position_final_error_mm, 0.0, delta=TOL)
        self.assertAlmostEqual(result.orientation_rms_error_deg, 0.0, delta=TOL)
        self.assertAlmostEqual(result.orientation_final_error_deg, 0.0, delta=TOL)

    def test_drift_de_mano_no_mueve_la_muneca(self):
        result = simulate_linear_drift("mano", 0.10, duration_s=20.0, samples=101)
        self.assertAlmostEqual(result.final_drift_deg, 2.0, delta=TOL)
        self.assertAlmostEqual(result.position_final_error_mm, 0.0, delta=TOL)
        self.assertAlmostEqual(result.orientation_final_error_deg, 2.0, delta=1e-7)

    def test_drift_de_antebrazo_mueve_la_muneca(self):
        result = simulate_linear_drift("antebrazo", 0.10, duration_s=20.0, samples=101)
        self.assertAlmostEqual(result.final_drift_deg, 2.0, delta=TOL)
        self.assertGreater(result.position_final_error_mm, 0.0)
        self.assertAlmostEqual(result.orientation_final_error_deg, 0.0, delta=TOL)

    def test_drift_de_brazo_mueve_la_muneca(self):
        result = simulate_linear_drift("brazo", 0.10, duration_s=20.0, samples=101)
        self.assertGreater(result.position_final_error_mm, 0.0)
        self.assertAlmostEqual(result.orientation_final_error_deg, 0.0, delta=TOL)

    def test_mayor_tasa_produce_mayor_error_final(self):
        low = simulate_linear_drift("antebrazo", 0.02, duration_s=30.0, samples=101)
        high = simulate_linear_drift("antebrazo", 0.10, duration_s=30.0, samples=101)
        self.assertGreater(high.position_final_error_mm, low.position_final_error_mm)

    def test_tasa_negativa_tambien_es_valida(self):
        result = simulate_linear_drift("mano", -0.10, duration_s=20.0, samples=101)
        self.assertAlmostEqual(result.final_drift_deg, -2.0, delta=TOL)
        self.assertAlmostEqual(result.orientation_final_error_deg, 2.0, delta=1e-7)

    def test_todos_afectan_posicion_y_orientacion(self):
        result = simulate_linear_drift("todos", 0.05, duration_s=20.0, samples=101)
        self.assertGreater(result.position_final_error_mm, 0.0)
        self.assertGreater(result.orientation_final_error_deg, 0.0)

    def test_parametros_invalidos_se_rechazan(self):
        with self.assertRaises(ValueError):
            simulate_linear_drift("sensor_inexistente", 0.10)
        with self.assertRaises(ValueError):
            simulate_linear_drift("brazo", 0.10, duration_s=0.0)
        with self.assertRaises(ValueError):
            simulate_linear_drift("brazo", 0.10, samples=1)


if __name__ == "__main__":
    unittest.main()
