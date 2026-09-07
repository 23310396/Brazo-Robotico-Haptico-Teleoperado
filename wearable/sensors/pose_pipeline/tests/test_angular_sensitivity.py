import unittest

from wearable.sensors.pose_pipeline.analysis.angular_sensitivity import (
    evaluate_angular_error,
)


TOL = 1e-9


class AngularSensitivityTests(unittest.TestCase):
    def test_sin_error_no_hay_error_de_posicion(self):
        result = evaluate_angular_error("brazo", 0.0)
        self.assertAlmostEqual(result.position_error_m, 0.0, delta=TOL)
        self.assertAlmostEqual(result.orientation_error_deg, 0.0, delta=TOL)

    def test_error_en_brazo_mueve_la_muneca(self):
        result = evaluate_angular_error("brazo", 2.0)
        self.assertGreater(result.position_error_m, 0.0)
        self.assertAlmostEqual(result.orientation_error_deg, 0.0, delta=TOL)

    def test_error_en_antebrazo_mueve_la_muneca(self):
        result = evaluate_angular_error("antebrazo", 2.0)
        self.assertGreater(result.position_error_m, 0.0)
        self.assertAlmostEqual(result.orientation_error_deg, 0.0, delta=TOL)

    def test_error_compartido_mueve_mas_que_un_segmento(self):
        upper = evaluate_angular_error("brazo", 2.0)
        fore = evaluate_angular_error("antebrazo", 2.0)
        both = evaluate_angular_error("brazo+antebrazo", 2.0)
        self.assertGreater(both.position_error_m, upper.position_error_m)
        self.assertGreater(both.position_error_m, fore.position_error_m)

    def test_error_en_mano_no_mueve_la_muneca(self):
        result = evaluate_angular_error("mano", 5.0)
        self.assertAlmostEqual(result.position_error_m, 0.0, delta=TOL)
        self.assertAlmostEqual(result.orientation_error_deg, 5.0, delta=1e-7)

    def test_error_crece_con_el_angulo(self):
        low = evaluate_angular_error("brazo", 1.0)
        high = evaluate_angular_error("brazo", 5.0)
        self.assertGreater(high.position_error_m, low.position_error_m)

    def test_objetivo_invalido_se_rechaza(self):
        with self.assertRaises(ValueError):
            evaluate_angular_error("sensor_inexistente", 2.0)


if __name__ == "__main__":
    unittest.main()
