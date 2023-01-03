# This file defines the field map based on a field image and the coordinates (in inches)

import numpy as np
from itertools import product
import geopandas as gpd
from shapely import to_geojson
from shapely.geometry import LineString, Polygon, Point, MultiPolygon, MultiLineString
from typing import List, Callable
from matplotlib.axes import Axes
from folium.folium import Map
from folium import GeoJson, Icon, DivIcon, Marker, Circle

def style_line_color(color:str) -> Callable:
    def sf(nonsense):
        return {"color": color}
    return sf
   
def style_marker_color(color:str) -> Callable:
    def sf(nonsense):
        return {"markerColor": color}
    return sf
   


OFFSETS = np.array([1,2,3,4,5]) * 24

class JunctionsPowerPlay:
    """Store the locations of various junctions.
    """
    ground = [Point(i,j) for i,j in product(OFFSETS[0:5:2], OFFSETS[0:5:2])]
    low = [ Point(i,j) for i,j in list(product(OFFSETS[[1,3]], OFFSETS[[0, 4]]))
                                + list(product(OFFSETS[[0,4]], OFFSETS[[1, 3]])) ]
    medium = [ Point(i,j) for i,j in product(OFFSETS[[1,3]], OFFSETS[[1, 3]])]
    high = [ Point(OFFSETS[1], OFFSETS[2]), Point(OFFSETS[2], OFFSETS[1]),
             Point(OFFSETS[2], OFFSETS[3]), Point(OFFSETS[3], OFFSETS[2]) ]
    COLORSET = [("ground", "#000"), 
                ("high", "#FF8"),
                ("medium", "#FD4"),
                ("low", "#FB0")]
    STYLE_SET = {

    }

    @classmethod
    def all(cls) -> List[Point]:
        """Return all the junctions

        Returns:
            List[Point]: _description_
        """
        return (cls.ground + cls.low + cls.medium + cls.high)

    @classmethod
    def draw_on_axis(cls, ax: Axes):
        """Draws junctions on the given axis using geopandas.GeoSeries.plot

      import ..  """
        for junction, color in cls.COLORSET:
            s = gpd.GeoSeries(getattr(cls, junction))
            s.plot(ax=ax, color=color)
    
    @classmethod
    def add_to(cls, map: Map) -> None:
        """Add the junctions to a specified map object

        Args:
            map (Map): _description_
        """
        for junction_type, color in cls.COLORSET:
            for junction in getattr(cls, junction_type):
                Circle([junction.x, junction.y], 
                        radius=2, fillColor=color, fillOpacity=1.0,
                        weight=1, color="black", #Dark stroke
                        popup=junction_type,).add_to(map)            
    
class FieldLines:
    _lines = gpd.GeoDataFrame([])

    @classmethod
    def by_color(cls, color):
        return list(cls._lines[cls._lines.color==color]["shape"])

    @classmethod
    @property
    def all_lines(cls):
        return list(cls._lines["shape"])
    
    @classmethod
    def draw_on_axes(cls, ax):
        """Draws field lines on an axis using geopandas.GeoSeries.plot()
        """
        for k,v in cls._lines.T.items():
            gpd.GeoSeries(v['shape']).plot(color=v['color'], ax=ax, linewidth=5.0)
    
    # TODO: Figure out how to make these the right colors.
    @classmethod
    def add_to(cls, map):
        """Return a GeoJSON Representation

        Returns:
            GeoJson: The Field Lines as JSON. 
        """
        for color in ("red", "blue"):
            gj = GeoJson(gpd.GeoSeries(cls.by_color(color)).to_json(),
                        style_function=style_line_color(color))
            gj.add_to(map)


class FieldLinesPowerPlay(FieldLines):
    _lines = gpd.GeoDataFrame([
        {"name": "substation",
        "color": "blue",
        "width": 2,
        "shape": MultiLineString([((0, 72-12), (12, 72)),
                                ((12, 72), (0, 72+12))])
        },
        {"name": "substation",
        "color": "red",
        "width": 2,
        "shape": MultiLineString([((144, 72-12), (144-12, 72)), 
                                ((144-12, 72), (144, 72+12))])
        },
        {"name": "terminal", 
        "color": "blue",
        "width": 2.0,
        "shape": LineString(((0, 12), (12, 0)))
        },
        {"name": "terminal", 
        "color": "blue",
        "width": 2.0,
        "shape": LineString(((144-0, 144-12), (144-12, 144-0)))
        },
        {"name": "terminal", 
        "color": "red",
        "width": 2.0,
        "shape": LineString(((144-0, 12), (144-12, 0)))
        },
        {"name": "terminal", 
        "color": "red",
        "width": 2.0,
        "shape": LineString(((0, 144-12), (12, 144-0)))
        },
        {"name": "cone stack", 
        "color": "blue",
        "width": 2.0,
        "shape": LineString(((60, 0), (60, 24)))
        },
        {"name": "cone stack", 
        "color": "blue",
        "width": 2.0,
        "shape": LineString(((60, 144-24), (60, 144)))
        },
        {"name": "cone stack", 
        "color": "red",
        "width": 2.0,
        "shape": LineString(((144-60, 0), (144-60, 24)))
        },
        {"name": "cone stack", 
        "color": "red",
        "width": 2.0,
        "shape": LineString(((144-60, 144-24), (144-60, 144)))
        },
        
    ])


class Field:
    FIELD_COLOR="#AAA"
    border = Polygon([(0,0), (0, 144), (144,144), (144,0), (0,0)])

    def draw_on_axes(self, ax):
        gpd.GeoSeries(self.border).plot(ax=ax, color=self.FIELD_COLOR)


class FieldPowerPlay(Field):
    """ Field 
    Represents the field.

    Store and draw the field and its obstacles. Determine if the robot is
    inside the field or hitting obstacles.
    """
    junctions = JunctionsPowerPlay()
    field_lines = FieldLinesPowerPlay()

    def style_function(self, junk) -> dict: 
        return {"lineColor": "black", 
                "color": self.FIELD_COLOR}

    def draw_on_axes(self, ax: Axes):
        """Draws the field on the given axes

        Args:
            ax (Axes): _description_
        """
        super().draw_on_axes(ax)
        self.field_lines.draw_on_axes(ax)
        self.junctions.draw_on_axis(ax)

    def add_to(self, map: Map, show_junctions=True): 
        GeoJson(to_geojson(self.border), 
                style_function=style_line_color("black")).add_to(map)
        if show_junctions:
            self.junctions.add_to(map)
        self.field_lines.add_to(map)


