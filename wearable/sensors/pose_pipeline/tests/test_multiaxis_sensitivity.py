import unittest

from wearable.sensors.pose_pipeline.analysis.multiaxis_sensitivity import evaluate_multiaxis_error


TOL = 1e-8


class MultiAxisSensitivityTests(unittest.TestCase):
    def test_cero_error_no_cambia_pose(self):
        for target in ("brazo", "antebrazo", "mano"):
            for axis in ("x", "y", "z", "diagonal"):
                result = evaluate_multiaxis_error(target, axis, 0.0)
                self.assertAlmostEqual(result.position_error_mm, 0.0, delta=TOL)
                self.assertAlmostEqual(result.orientation_error_deg, 0.0, delta=TOL)

    def test_twist_local_x_del_brazo_no_mueve_muneca(self):
        result = evaluate_multiaxis_error("brazo", "x", 5.0)
        self.assertAlmostEqual(result.position_error_mm, 0.0, delta=TOL)
        self.assertAlmostEqual(result.orientation_error_deg, 0.0, delta=TOL)

    def test_error_local_y_del_brazo_mueve_muneca(self):
        result = evaluate_multiaxis_error("brazo", "y", 5.0)
        self.assertGreater(result.position_error_mm, 0.0)

    def test_error_local_z_del_antebrazo_mueve_muneca(self):
        result = evaluate_multiaxis_error("antebrazo", "z", 5.0)
        self.assertGreater(result.position_error_mm, 0.0)

    def test_twist_local_x_del_antebrazo_no_mueve_muneca(self):
        result = evaluate_multiaxis_error("antebrazo", "x", 5.0)
        self.assertAlmostEqual(result.position_error_mm, 0.0, delta=TOL)

    def test_error_de_mano_en_cualquier_eje_no_mueve_muneca(self):
        for axis in ("x", "y", "z", "diagonal"):
            result = evaluate_multiaxis_error("mano", axis, 5.0)
            self.assertAlmostEqual(result.position_error_mm, 0.0, delta=TOL)
            self.assertAlmostEqual(result.orientation_error_deg, 5.0, delta=1e-7)

    def test_error_compuesto_en_brazo_mueve_muneca(self):
        result = evaluate_multiaxis_error("brazo", "diagonal", 5.0)
        self.assertGreater(result.position_error_mm, 0.0)

    def test_parametros_invalidos_se_rechazan(self):
        with self.assertRaises(ValueError):
            evaluate_multiaxis_error("sensor_inexistente", "x", 5.0)
        with self.assertRaises(ValueError):
            evaluate_multiaxis_error("brazo", "eje_inexistente", 5.0)


if __name__ == "__main__":
    unittest.main()
