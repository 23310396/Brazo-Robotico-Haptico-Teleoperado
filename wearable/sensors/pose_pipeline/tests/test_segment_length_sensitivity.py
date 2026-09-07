import unittest

from wearable.sensors.pose_pipeline.analysis.segment_length_sensitivity import evaluate_length_error


TOL = 1e-8


class SegmentLengthSensitivityTests(unittest.TestCase):
    def test_longitudes_correctas_no_producen_error(self):
        result = evaluate_length_error(0.0, 0.0)
        self.assertAlmostEqual(result.elbow_error_mm, 0.0, delta=TOL)
        self.assertAlmostEqual(result.wrist_error_mm, 0.0, delta=TOL)

    def test_error_de_brazo_mueve_codo_y_muneca(self):
        result = evaluate_length_error(10.0, 0.0)
        self.assertAlmostEqual(result.elbow_error_mm, 10.0, delta=1e-7)
        self.assertAlmostEqual(result.wrist_error_mm, 10.0, delta=1e-7)

    def test_error_de_antebrazo_no_mueve_codo(self):
        result = evaluate_length_error(0.0, 10.0)
        self.assertAlmostEqual(result.elbow_error_mm, 0.0, delta=TOL)
        self.assertAlmostEqual(result.wrist_error_mm, 10.0, delta=1e-7)

    def test_signo_del_error_individual_no_cambia_magnitud(self):
        positive = evaluate_length_error(5.0, 0.0)
        negative = evaluate_length_error(-5.0, 0.0)
        self.assertAlmostEqual(positive.wrist_error_mm, negative.wrist_error_mm, delta=1e-7)

    def test_error_combined_depende_de_geometria(self):
        result = evaluate_length_error(10.0, 10.0)
        self.assertGreater(result.wrist_error_mm, 0.0)
        self.assertLessEqual(result.wrist_error_mm, 20.0 + 1e-7)

    def test_mayor_error_individual_produce_mayor_desplazamiento(self):
        low = evaluate_length_error(5.0, 0.0)
        high = evaluate_length_error(20.0, 0.0)
        self.assertGreater(high.wrist_error_mm, low.wrist_error_mm)

    def test_longitud_estimadas_no_pueden_ser_no_positivas(self):
        with self.assertRaises(ValueError):
            evaluate_length_error(-300.0, 0.0)
        with self.assertRaises(ValueError):
            evaluate_length_error(0.0, -250.0)


if __name__ == "__main__":
    unittest.main()
