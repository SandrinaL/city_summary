import unittest

from processing.preprocessing import add_expensive_flag, add_warm_clothes_flag


class PreprocessingTests(unittest.TestCase):
    def test_warm_clothes_true_when_cold(self):
        weather = {"temp_c": -3.2}
        result = add_warm_clothes_flag(weather)
        self.assertTrue(result["warm_clothes"])

    def test_warm_clothes_false_when_warm(self):
        weather = {"temp_c": 10.0}
        result = add_warm_clothes_flag(weather)
        self.assertFalse(result["warm_clothes"])

    def test_expensive_true_over_100(self):
        result = add_expensive_flag(150.0)
        self.assertTrue(result["expensive"])

    def test_expensive_false_below_100(self):
        result = add_expensive_flag(92.15)
        self.assertFalse(result["expensive"])


if __name__ == "__main__":
    unittest.main()