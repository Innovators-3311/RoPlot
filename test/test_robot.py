
from unittest import TestCase
from shapely import Point, Geometry
from roplot import Robot

class TestRobot(TestCase):
    
    def test_rectangle_initialization(self):
        """Tests initializing the robot as a rectangle.
        """
        r = Robot((16, 16))

    def test_geometry_initialization(self):
        """Tests initializing the robot as a rectangle.
        """
        r = Robot((16, 16))

    def test_centroid_is_zero(self):
        "Be sure the robot is centered properly (0,0)"
        r = Robot((16, 16))
        self.assertEqual(r.get().centroid, Point(0,0))

    def test_set_position(self):
        r = Robot((16,16))
        POS = (8,8)
        r.position = POS
        self.assertEqual(r.position, Point(POS))
    
    def test_set_heading(self):
        """Test setting the heading"""
        r = Robot((16,16))
        heading = 12
        r.heading = heading
        self.assertEqual(r.rotation, -heading, "Rotation should be -heading")

    def test_set_rotation(self):
        """Test setting the rotation"""
        r = Robot((16,16))
        rotation = 12
        r.rotation = rotation
        self.assertEqual(r.heading, -rotation, "Rotation should be -heading")

