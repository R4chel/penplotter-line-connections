import vsketch
from shapely.geometry import Point, LineString, MultiLineString
from shapely import get_parts, get_coordinates

class Connection:

    def line(vsk, p1, p2):
        return LineString([p1, p2])

    def circles(vsk, p1, p2):
        path = Connection.line(vsk, p1, p2)
        return path

    def dashes(vsk, p1, p2):
        path = Connection.line(vsk, p1, p2).segmentize(10)
        coords = get_coordinates(path)
        # This is a bit wrong if for one of odd or even length linestrings but I'm not fixing it now
        return MultiLineString([[coords[i], coords[i+1]] for i in range(0, len(coords)-1, 2) ])


connection_kind = {
    "line": Connection.line,
    "circles": Connection.circles,
    "dashes": Connection.dashes,
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
