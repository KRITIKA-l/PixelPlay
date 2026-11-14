"""3-D transformations with 4x4 homogeneous matrices, shown on a cube.
To draw the cube on the 2-D grid the scene is turned by a FIXED viewing rotation (VIEW_Y about the
y-axis, then VIEW_X about the x-axis) and then projected orthographically (z is dropped).
The viewing rotation is only for display; it is not one of the user's transformations."""
import math
from .transform2d import mat_mul, identity, fmt, fmt_matrix

ORIGINAL, BUILDING, RESULT = "gray", "blue", "green"
VIEW_Y, VIEW_X = math.radians(25), math.radians(20)
EDGES = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]


def cube(x, y, z, s):
    return [(x, y, z), (x + s, y, z), (x + s, y + s, z), (x, y + s, z),
            (x, y, z + s), (x + s, y, z + s), (x + s, y + s, z + s), (x, y + s, z + s)]


def project(p):
    x, y, z = p
    x1 = x * math.cos(VIEW_Y) + z * math.sin(VIEW_Y)
    z1 = -x * math.sin(VIEW_Y) + z * math.cos(VIEW_Y)
    return (x1, y * math.cos(VIEW_X) - z1 * math.sin(VIEW_X))


def edges(vertices, colour):
    return [([project(vertices[a]), project(vertices[b])], colour, False) for a, b in EDGES]


def apply(m, p):
    x, y, z = p
    return tuple(m[i][0] * x + m[i][1] * y + m[i][2] * z + m[i][3] for i in range(3))


def fmt3(p):
    return f"({fmt(p[0])}, {fmt(p[1])}, {fmt(p[2])})"


# ---------- operations: (label, matrix, why) ----------
def op_translate(tx, ty, tz):
    return (f"Translation by ({fmt(tx)}, {fmt(ty)}, {fmt(tz)})",
            [[1, 0, 0, tx], [0, 1, 0, ty], [0, 0, 1, tz], [0, 0, 0, 1]],
            "x' = x + tx,  y' = y + ty,  z' = z + tz")


def op_scale(sx, sy, sz):
    return (f"Scaling by ({fmt(sx)}, {fmt(sy)}, {fmt(sz)}) about the origin",
            [[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]],
            "x' = x*sx,  y' = y*sy,  z' = z*sz")


def op_rotate(axis, angle):
    a = math.radians(angle)
    c, s = math.cos(a), math.sin(a)
    if axis == "X":
        m, why = [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], "x' = x,  y' = y cos - z sin,  z' = y sin + z cos"
    elif axis == "Y":
        m, why = [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], "x' = x cos + z sin,  y' = y,  z' = -x sin + z cos"
    else:
        m, why = [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], "x' = x cos - y sin,  y' = x sin + y cos,  z' = z"
    return (f"Rotation by {fmt(angle)} deg about the {axis}-axis (right-hand rule)", m, why)


PLANES = {"xy": (1, 1, -1), "yz": (-1, 1, 1), "xz": (1, -1, 1)}


def op_reflect(plane):
    if plane not in PLANES:
        raise ValueError("Reflection plane must be xy, yz or xz")
    sx, sy, sz = PLANES[plane]
    flipped = {"xy": "z", "yz": "x", "xz": "y"}[plane]
    return (f"Reflection about the {plane}-plane",
            [[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]],
            f"The {flipped} coordinate changes sign, the other two stay")


def parse_ops(text):
    """'T 4 2 2; S 1 1 1; RX 30; RY 20; RZ 45; F xy'  ->  list of operations (applied left to right)."""
    ops = []
    for part in text.split(";"):
        t = part.replace(",", " ").split()
        if not t:
            continue
        name, args = t[0].upper(), t[1:]
        try:
            if name == "T" and len(args) == 3:
                ops.append(op_translate(*map(float, args)))
            elif name == "S" and len(args) == 3:
                ops.append(op_scale(*map(float, args)))
            elif name in ("RX", "RY", "RZ") and len(args) == 1:
                ops.append(op_rotate(name[1], float(args[0])))
            elif name == "F" and len(args) == 1:
                ops.append(op_reflect(args[0].lower()))
            else:
                raise ValueError
        except ValueError:
            raise ValueError("Use: T tx ty tz;  S sx sy sz;  RX/RY/RZ angle;  F xy|yz|xz   (separate with ;)")
    if not ops:
        raise ValueError("Enter at least one operation, e.g.  T 4 2 2; RY 30")
    return ops


def transform3d(corner, size, ops_text):
    """corner = (x, y, z) of the cube, size = edge length, ops_text = operations separated by ;"""
    ops = parse_ops(ops_text)
    start = cube(*corner, size)
    steps = [{"text": ("3-D transformation of a cube\n"
                       f"Cube corner {fmt3(corner)}, edge length {fmt(size)}.\n"
                       "Each point is written as (x, y, z, 1): every 3-D transformation is a 4 x 4 matrix product P' = M . P.\n"
                       "For display only, the cube is viewed after a fixed rotation (Y 25, X 20 deg) and projected by dropping z."),
              "shapes": edges(start, BUILDING)}]
    current, total = start, identity(4)
    for k, (label, m, why) in enumerate(ops, 1):
        total = mat_mul(m, total)
        new = [apply(m, p) for p in current]
        steps.append({"text": (f"Operation {k} of {len(ops)}: {label}\n{why}\nMatrix M{k}:\n{fmt_matrix(m)}\n"
                               f"Example: vertex 1 {fmt3(current[0])} -> {fmt3(new[0])}"),
                      "shapes": edges(start, ORIGINAL) + edges(current, "skyblue") + edges(new, BUILDING)})
        current = new
    names = " . ".join(f"M{k}" for k in range(len(ops), 0, -1))
    final = (f"Done: transformation complete\nComposite matrix M = {names}\n{fmt_matrix(total)}\n"
             "(multiplied right to left: the first operation is the right-most)\n"
             f"Vertex 1: {fmt3(start[0])} -> {fmt3(current[0])}") if len(ops) > 1 else \
            f"Done: transformation complete\nVertex 1: {fmt3(start[0])} -> {fmt3(current[0])}"
    steps.append({"text": final, "shapes": edges(start, ORIGINAL) + edges(current, RESULT)})
    return steps