"""Run in the extracted foundation folder: python3 -m unittest -v test_data_tools."""
import unittest
from data_tools import parse_minutes, validate_record, summary


class DataTests(unittest.TestCase):
    def test_minutes_boundaries(self):
        for value in (0, 30, 1440):
            with self.subTest(value=value):
                self.assertEqual(parse_minutes(value), value)

    def test_minutes_rejections(self):
        for value in (-1, 1441, "30", True, None, 30.0):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_minutes(value)

    def test_record_shape(self):
        for value in ([], {}, {"learner": "Loki", "minutes": 30, "admin": True},
                      {"learner": " ", "minutes": 30}):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_record(value)

    def test_selection_boundary(self):
        record = {"learner": "Loki", "minutes": 30}
        self.assertEqual(summary(record, 30), "learner=Loki minutes=30 selected=True")
        self.assertEqual(summary(record, 31), "learner=Loki minutes=30 selected=False")


if __name__ == "__main__":
    unittest.main()
