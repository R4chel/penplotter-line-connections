import vsketch
from shapely.geometry import GeometryCollection, Point, LineString, MultiLineString
from shapely import get_parts, get_coordinates
import numpy as np


class Connection:

    def line(_vsk, p1, p2):
        return LineString([p1, p2])

    def points(vsk, p1, p2):
        max_distance = 10
        path = Connection.line(vsk, p1, p2).segmentize(max_distance)
        points = [Point(p) for p in get_coordinates(path)]

        return points

    def pts(vsk, p1, p2, max_length):
        distance = p1.distance(p2)
        num_steps = int(np.ceil(distance / max_length))
        return np.linspace(np.array([p1.x, p1.y]),
                           np.array([p2.x, p2.y]),
                           num=num_steps,
                           endpoint=True)

    def circles(vsk, p1, p2):
        points = Connection.points(vsk, p1, p2)
        radius = points[0].distance(points[1]) / 2
        return GeometryCollection([p.buffer(radius) for p in points])

    def dashes(vsk, p1, p2):
        points = Connection.points(vsk, p1, p2)
        # This is a bit wrong if for one of odd or even length linestrings but I'm not fixing it now
        return MultiLineString([[points[i], points[i + 1]]
                                for i in range(0,
                                               len(points) - 1, 2)])

    def tbd(vsk, p1, p2):
        pts = Connection.pts(vsk, p1, p2, 10)
        r = 5
        return GeometryCollection([Point(p).buffer(r) for p in pts])


connection_kind = {
    "line": Connection.line,
    "circles": Connection.circles,
    "dashes": Connection.dashes,
    "tbd": Connection.tbd
}


class ConnectorsSketch(vsketch.SketchClass):
    # Sketch parameters:
    debug = vsketch.Param(False)
    width = vsketch.Param(5., decimals=2, unit="in")
    height = vsketch.Param(3., decimals=2, unit="in")
    margin = vsketch.Param(0.1, decimals=3, unit="in")
    landscape = vsketch.Param(True)
    pen_width = vsketch.Param(0.7, decimals=3, min_value=1e-10, unit="mm")
    num_layers = vsketch.Param(1)
    path_kind = vsketch.Param(next(iter(connection_kind.keys())),
                              choices=connection_kind.keys())

    def random_point(self, vsk: vsketch.Vsketch):
        return Point(vsk.random(0, self.width), vsk.random(0, self.height))

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size(f"{self.height}x{self.width}",
                 landscape=self.landscape,
                 center=False)
        self.width = self.width - 2 * self.margin
        self.height = self.height - 2 * self.margin
        vsk.translate(self.margin, self.margin)
        vsk.penWidth(f"{self.pen_width}")

        # implement your sketch here
        layers = [1 + i for i in range(self.num_layers)]
        layer = layers[int(vsk.random(0, len(layers)))]
        vsk.stroke(layer)
        p1 = self.random_point(vsk)
        p2 = self.random_point(vsk)
        shape = connection_kind[self.path_kind](vsk, p1, p2)
        vsk.geometry(shape)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    ConnectorsSketch.display()
