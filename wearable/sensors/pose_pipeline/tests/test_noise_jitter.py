import unittest

from wearable.sensors.pose_pipeline.analysis.noise_jitter import (
    simulate_moving_forearm,
    simulate_stationary_jitter,
)


TOL = 1e-9


class NoiseJitterTests(unittest.TestCase):
    def test_cero_ruido_da_cero_error_en_reposo(self):
        result = simulate_stationary_jitter(0.0, samples=50, seed=1)
        self.assertAlmostEqual(result.position_rms_error_mm, 0.0, delta=TOL)
        self.assertAlmostEqual(result.orientation_rms_error_deg, 0.0, delta=TOL)

    def test_cero_ruido_da_cero_error_en_movimiento(self):
        result = simulate_moving_forearm(0.0, samples=50, seed=1)
        self.assertAlmostEqual(result.position_rms_error_mm, 0.0, delta=TOL)
        self.assertAlmostEqual(result.orientation_rms_error_deg, 0.0, delta=TOL)

    def test_ruido_positivo_produce_jitter_en_reposo(self):
        result = simulate_stationary_jitter(0.5, samples=100, seed=2)
        self.assertGreater(result.position_rms_error_mm, 0.0)
        self.assertGreater(result.orientation_rms_error_deg, 0.0)

    def test_mayor_sigma_aumenta_error_rms_con_misma_semilla(self):
        low = simulate_stationary_jitter(0.2, samples=200, seed=3)
        high = simulate_stationary_jitter(1.0, samples=200, seed=3)
        self.assertGreater(high.position_rms_error_mm, low.position_rms_error_mm)
        self.assertGreater(high.orientation_rms_error_deg, low.orientation_rms_error_deg)

    def test_simulacion_es_reproducible_con_misma_semilla(self):
        a = simulate_stationary_jitter(0.5, samples=120, seed=99)
        b = simulate_stationary_jitter(0.5, samples=120, seed=99)
        self.assertAlmostEqual(a.position_rms_error_mm, b.position_rms_error_mm, delta=TOL)
        self.assertAlmostEqual(a.orientation_rms_error_deg, b.orientation_rms_error_deg, delta=TOL)
        self.assertAlmostEqual(a.position_peak_to_peak_mm, b.position_peak_to_peak_mm, delta=TOL)

    def test_ruido_en_movimiento_produce_error_respecto_a_trayectoria_ideal(self):
        result = simulate_moving_forearm(0.5, samples=100, seed=4)
        self.assertGreater(result.position_rms_error_mm, 0.0)
        self.assertGreater(result.orientation_rms_error_deg, 0.0)

    def test_sigma_negativo_se_rechaza(self):
        with self.assertRaises(ValueError):
            simulate_stationary_jitter(-0.1)
        with self.assertRaises(ValueError):
            simulate_moving_forearm(-0.1)

    def test_numero_de_muestras_invalido_se_rechaza(self):
        with self.assertRaises(ValueError):
            simulate_stationary_jitter(0.5, samples=0)
        with self.assertRaises(ValueError):
            simulate_moving_forearm(0.5, samples=1)


if __name__ == "__main__":
    unittest.main()
