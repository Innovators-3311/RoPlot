from unittest import TestCase
from roplot.field import FieldLinesPowerPlay, FieldPowerPlay

from shapely import Geometry

class TestFieldLines(TestCase):
    FieldLines = FieldLinesPowerPlay

    def test_by_color(self):
        """Tests whether by_color returns colors"""
        blues = self.FieldLines.by_color("blue")
        reds = self.FieldLines.by_color("red")
        self.assertIsInstance(blues, list, "by_color doesn't return a list.")
        self.assertIsInstance(reds, list, "by_color doesn't always return a list.")
        self.assertEqual(len(reds), len(blues), "Red and Blue lengths should match")

    def test_class_all_lines(self):
        """Tests that all lines returns a list of Geometries"""
        self.assertEqual(len(self.FieldLines.all_lines), 10, "There should be 10 field lines")
        for item in self.FieldLines.all_lines:
            self.assertIsInstance(item, Geometry, "All field lines should be geometries")

    def test_instance_all_lines(self):
        """Tests that all lines returns a list of Geometries"""
        fl = self.FieldLines()
        self.assertEqual(len(fl.all_lines), 10, "There should be 10 field lines")
        for item in fl.all_lines:
            self.assertIsInstance(item, Geometry, "All field lines should be geometries")

class TestField(TestCase):
    pass
