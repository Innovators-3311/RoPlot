from shapely import Geometry, Polygon, Point
from shapely.affinity import translate, rotate
from typing import Union, Iterable
from matplotlib.axes import Axes
import geopandas as gpd

class Robot:
    shape = None
    _position = Point(0,0)
    rotation = 0
    color="pink"

    def __init__(self, shape: Union[list, tuple, Geometry] ):
        """Create a robot object

        Args:
            shape (tuple or Polygon): The shape of the robot either as length, width or as a polygon.

        **Note:** Shape MIGHT be able to support multiple shapes as a list.
        """
        if isinstance(shape, Geometry):
            self.shape = shape
        else:
            self.shape = self.make_rectangle(*shape)

    def get_position(self):
        return self._position 

    def set_position(self, pos: Union[Iterable, Point]):
        if isinstance(pos, Point):
            self._position = pos
        else: 
            self._position = Point(*pos)

    position = property(get_position, set_position)



    @staticmethod
    def make_rectangle(x: float, y: float):
        """Compute a Shape from the dimensions

        **Note:** Length is along the x axis and width is along y.

        Args:
            dimensions (Iterable): The length, width of the robot (inches)
        """

        # Make a polygon, then center it cuz I'm too lazy to deal with all the
        # -1/2*x's and we only do this once
        shape = Polygon([(0,0), (x, 0), (x, y), (0, y), (0,0)])
        c = shape.centroid 
        return translate(shape, -c.x, -c.y)
    
    def at_location(self, x: float, y: float, rot: float, use_radians=False) -> Polygon:
        """Project the robot to the specified location and rotation

        Args:
            x (float): x offset (inches)
            y (float): y offset (inches)
            rot (float): rotation (degrees)

        Returns:
            Polygon: The projected robot polygon at the given location and rotation.
        """
        rotated = rotate(self.shape, rot, use_radians=use_radians)
        return translate(rotated, x, y)

    # Rotation about +x is CCW, which is counter-intuitive to compass heading. 
    # Make a heading property for convenience.
    def get_heading(self):
        return -self.rotation
    def set_heading(self, heading: float):
        self.rotation = -heading

    heading = property(get_heading, set_heading)

    def get(self):
        """Gets the robot polygon
        """
        return self.at_location(self._position.x, self._position.y, self.rotation)
    
    def draw_on_axes(self, ax: Axes):
        """Draw the robot on a given axes

        Args:
            ax (Axes): Where to draw the robot.
        """
        me = gpd.GeoSeries(self.get()).plot(ax=ax, color=self.color)