import unittest

from wearable.sensors.pose_pipeline.analysis.calibration_sensitivity import (
    evaluate_calibration_error,
)


TOL = 1e-9


class CalibrationSensitivityTests(unittest.TestCase):
    def test_calibracion_perfecta_elimina_offset_de_montaje(self):
        result = evaluate_calibration_error("antebrazo", 10.0, 10.0)
        self.assertAlmostEqual(result.residual_calibration_error_deg, 0.0, delta=TOL)
        self.assertAlmostEqual(result.position_error_m, 0.0, delta=TOL)
        self.assertAlmostEqual(result.orientation_error_deg, 0.0, delta=TOL)

    def test_error_residual_de_2_grados_en_antebrazo(self):
        result = evaluate_calibration_error("antebrazo", 10.0, 8.0)
        self.assertAlmostEqual(result.residual_calibration_error_deg, 2.0, delta=TOL)
        self.assertAlmostEqual(result.position_error_m * 1000.0, 8.7262032186, delta=1e-6)
        self.assertAlmostEqual(result.orientation_error_deg, 0.0, delta=TOL)

    def test_error_residual_de_2_grados_en_brazo(self):
        result = evaluate_calibration_error("brazo", 10.0, 8.0)
        self.assertAlmostEqual(result.position_error_m * 1000.0, 10.4714438624, delta=1e-6)
        self.assertAlmostEqual(result.orientation_error_deg, 0.0, delta=TOL)

    def test_error_residual_en_mano_no_mueve_muneca(self):
        result = evaluate_calibration_error("mano", 10.0, 8.0)
        self.assertAlmostEqual(result.position_error_m, 0.0, delta=TOL)
        self.assertAlmostEqual(result.orientation_error_deg, 2.0, delta=1e-7)

    def test_mayor_error_residual_aumenta_error_de_posicion(self):
        low = evaluate_calibration_error("antebrazo", 10.0, 9.0)
        high = evaluate_calibration_error("antebrazo", 10.0, 5.0)
        self.assertGreater(high.position_error_m, low.position_error_m)

    def test_sin_compensacion_queda_todo_el_offset(self):
        result = evaluate_calibration_error("antebrazo", 10.0, 0.0)
        self.assertAlmostEqual(result.residual_calibration_error_deg, 10.0, delta=TOL)
        self.assertGreater(result.position_error_m, 0.0)

    def test_objetivo_invalido_se_rechaza(self):
        with self.assertRaises(ValueError):
            evaluate_calibration_error("sensor_inexistente", 10.0, 8.0)


if __name__ == "__main__":
    unittest.main()
