"""Small helpers shared by the Unit 6 algorithms (hidden surfaces, images, shading, shadows).

Extra keys a step may use besides "pixels" / "color" / "shapes" / "text":
    "cells":  [(x, y, colour), ...]   pixels that each have their OWN colour (any CSS colour, e.g. "#7f7f7f")
    "labels": [(x, y, text, colour=None, size=None), ...]   text written inside a cell (current step only)
    "view":   (x_lo, x_hi, y_lo, y_hi)   zoom the grid to this part of the canvas (put it in the first step)
"""
import math

PALETTE = ["#e4572e", "#2e86de", "#2ca02c", "#f5b700"]                       # polygon A, B, C, D
PALETTE6 = ["#e4572e", "#2e86de", "#2ca02c", "#f5b700", "#8e44ad", "#16a085"]  # the six faces of a cube
NAMES = "ABCD"


def gray(v):
    v = max(0, min(255, int(round(v))))
    return "#%02x%02x%02x" % (v, v, v)


def rgb(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in c)


def hex_to_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def label_colour(v):
    """Black text on light cells, white text on dark cells."""
    return "white" if v < 128 else "black"


def inside(poly, x, y):
    """Point in polygon (even-odd rule); points on an edge count as inside."""
    n, c = len(poly), False
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1) == 0 and min(x1, x2) <= x <= max(x1, x2) \
                and min(y1, y2) <= y <= max(y1, y2):
            return True
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def polygon_pixels(poly, size=30):
    """All canvas pixels whose centre is inside the polygon."""
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return [(x, y) for y in range(max(0, int(math.floor(min(ys)))), min(size - 1, int(math.ceil(max(ys)))) + 1)
            for x in range(max(0, int(math.floor(min(xs)))), min(size - 1, int(math.ceil(max(xs)))) + 1)
            if inside(poly, x, y)]


def outline(poly, colour, width=1, style="-"):
    return (list(poly), colour, True, width, style)


def line(a, b, colour, width=1, style="-"):
    return ([a, b], colour, False, width, style)


def cell_box(x, y, colour="orange", width=3):
    """A square drawn around one pixel."""
    return ([(x - .5, y - .5), (x + .5, y - .5), (x + .5, y + .5), (x - .5, y + .5)], colour, True, width, "-")


def rect(x0, y0, x1, y1, colour, width=1, style="-"):
    """Rectangle that covers the pixels x0..x1, y0..y1 (inclusive)."""
    return ([(x0 - .5, y0 - .5), (x1 + .5, y0 - .5), (x1 + .5, y1 + .5), (x0 - .5, y1 + .5)], colour, True, width, style)


def normalize(v):
    m = math.sqrt(sum(c * c for c in v))
    return tuple(c / m for c in v) if m else v


def dot(a, b):
    return sum(p * q for p, q in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])