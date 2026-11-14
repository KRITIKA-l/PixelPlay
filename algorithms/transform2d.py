"""2-D transformations with 3x3 homogeneous matrices.
Every function returns a list of steps (same format as the other algorithms).
Colours used in "shapes":  gray = original, skyblue = shape before the current operation,
blue = shape being built, orange = current vertex, green = final result, purple = mirror line."""
import math

ORIGINAL, BEFORE, BUILDING, MARK, RESULT, MIRROR = "gray", "skyblue", "blue", "orange", "green", "purple"


# ---------- small matrix helpers ----------
def identity(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def fmt(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def fmt_matrix(m):
    return "\n".join("[ " + "   ".join(fmt(v) for v in row) + " ]" for row in m)


def fmt_pts(pts):
    return ", ".join(f"({fmt(x)}, {fmt(y)})" for x, y in pts)


def apply(m, p):
    x, y = p
    return (m[0][0] * x + m[0][1] * y + m[0][2], m[1][0] * x + m[1][1] * y + m[1][2])


def marker(p, r=0.35, colour=MARK):
    x, y = p
    return ([(x - r, y - r), (x + r, y - r), (x + r, y + r), (x - r, y + r)], colour, True)


# ---------- the basic operations: (label, matrix, why) ----------
def op_translate(tx, ty):
    return (f"Translation by ({fmt(tx)}, {fmt(ty)})",
            [[1, 0, tx], [0, 1, ty], [0, 0, 1]],
            "x' = x + tx,   y' = y + ty")


def op_scale(sx, sy):
    return (f"Scaling by ({fmt(sx)}, {fmt(sy)}) about the origin",
            [[sx, 0, 0], [0, sy, 0], [0, 0, 1]],
            "x' = x * sx,   y' = y * sy")


def op_rotate(angle):
    a = math.radians(angle)
    c, s = math.cos(a), math.sin(a)
    return (f"Rotation by {fmt(angle)} deg about the origin",
            [[c, -s, 0], [s, c, 0], [0, 0, 1]],
            "x' = x cos(a) - y sin(a),   y' = x sin(a) + y cos(a)   (counter-clockwise)")


REFLECTIONS = {
    "x-axis": ([[1, 0, 0], [0, -1, 0], [0, 0, 1]], "x' = x,   y' = -y"),
    "y-axis": ([[-1, 0, 0], [0, 1, 0], [0, 0, 1]], "x' = -x,   y' = y"),
    "origin": ([[-1, 0, 0], [0, -1, 0], [0, 0, 1]], "x' = -x,   y' = -y"),
    "y=x": ([[0, 1, 0], [1, 0, 0], [0, 0, 1]], "x' = y,   y' = x"),
    "y=-x": ([[0, -1, 0], [-1, 0, 0], [0, 0, 1]], "x' = -y,   y' = -x"),
}


def op_reflect(kind):
    if kind not in REFLECTIONS:
        raise ValueError("Reflection must be one of: x-axis, y-axis, origin, y=x, y=-x")
    m, why = REFLECTIONS[kind]
    return (f"Reflection about {kind}", m, why)


# ---------- the engine: runs a list of operations and records the steps ----------
def transform_steps(polygon, ops, title, mirror=None):
    polygon = [(float(x), float(y)) for x, y in polygon]
    extra = [mirror] if mirror else []
    original = (polygon, ORIGINAL, True)
    steps = [{"text": (f"{title}\nOriginal shape, {len(polygon)} vertices:\n{fmt_pts(polygon)}\n"
                       "Each point is written as (x, y, 1) so every 2-D transformation is a 3 x 3 matrix product:\n"
                       "P' = M . P\n"
                       "Each new vertex is calculated first (shown as a point); the edge that joins it is drawn in the next step."),
              "shapes": extra + [original]}]
    current, total = list(polygon), identity(3)
    n = len(polygon)
    for k, (label, m, why) in enumerate(ops, 1):
        total = mat_mul(m, total)
        steps.append({"text": f"Operation {k} of {len(ops)}: {label}\n{why}\nMatrix M{k}:\n{fmt_matrix(m)}\n"
                              "Nothing of the new shape is drawn yet: each vertex is calculated, then its edge is drawn.",
                      "shapes": extra + [original, (current, BEFORE, True)]})
        new = []
        for i, p in enumerate(current, 1):
            q = apply(m, p)
            new.append(q)
            note = (f"\nOnly the point is marked now; the edge {i - 1}' -> {i}' is drawn in the next step."
                    if i >= 2 else "\nFirst new vertex: no edge yet.")
            steps.append({"text": (f"Operation {k}, vertex {i}: ({fmt(p[0])}, {fmt(p[1])}) -> ({fmt(q[0])}, {fmt(q[1])})\n"
                                   f"x' = {fmt(m[0][0])}*{fmt(p[0])} + {fmt(m[0][1])}*{fmt(p[1])} + {fmt(m[0][2])} = {fmt(q[0])}\n"
                                   f"y' = {fmt(m[1][0])}*{fmt(p[0])} + {fmt(m[1][1])}*{fmt(p[1])} + {fmt(m[1][2])} = {fmt(q[1])}"
                                   + note),
                          "shapes": extra + [original, (current, BEFORE, True)]
                                    + ([(new[:-1], BUILDING, False)] if len(new) > 2 else [])
                                    + [marker(v, 0.2, BUILDING) for v in new[:-1]] + [marker(p), marker(q)]})
            if i >= 2:
                steps.append({"text": f"Operation {k}: draw edge {i - 1}' -> {i}'\nJoin the new vertices {i - 1} and {i}.",
                              "shapes": extra + [original, (current, BEFORE, True), (list(new), BUILDING, False)]
                                        + [marker(v, 0.2, BUILDING) for v in new]})
        steps.append({"text": f"Operation {k}: close the shape\nThe last edge joins vertex {n}' back to vertex 1'.",
                      "shapes": extra + [original, (current, BEFORE, True), (new, BUILDING, True)]})
        current = new
        if len(ops) > 1 and k < len(ops):
            steps.append({"text": f"Operation {k} done\nNew vertices:\n{fmt_pts(current)}\nThis shape is the input of operation {k + 1}.",
                          "shapes": extra + [original, (current, BUILDING, True)]})
    names = " . ".join(f"M{k}" for k in range(len(ops), 0, -1))
    steps.append({"text": (f"Done: transformation complete\nComposite matrix M = {names}\n{fmt_matrix(total)}\n"
                           f"Final vertices:\n{fmt_pts(current)}\n"
                           "(The matrices are multiplied right to left: the first operation is the right-most.)"
                           if len(ops) > 1 else
                           f"Done: transformation complete\nFinal vertices:\n{fmt_pts(current)}"),
                  "shapes": extra + [original, (current, RESULT, True)]})
    return steps


# ---------- the five algorithms ----------
def translation(polygon, tx, ty):
    return transform_steps(polygon, [op_translate(tx, ty)], "Translation")


def about_point(op, fx, fy):
    """Run `op` about the point (fx, fy):  T(-f) -> op -> T(+f)."""
    if fx == 0 and fy == 0:
        return [op]
    return [(f"Move the fixed point ({fmt(fx)}, {fmt(fy)}) to the origin",) + op_translate(-fx, -fy)[1:],
            op,
            (f"Move the fixed point back to ({fmt(fx)}, {fmt(fy)})",) + op_translate(fx, fy)[1:]]


def scaling(polygon, sx, sy, fx=0, fy=0):
    ops = about_point(op_scale(sx, sy), fx, fy)
    if (fx, fy) != (0, 0):
        ops[1] = (f"Scaling by ({fmt(sx)}, {fmt(sy)}) about the origin",) + ops[1][1:]
    return transform_steps(polygon, ops, f"Scaling about the fixed point ({fmt(fx)}, {fmt(fy)})")


def rotation(polygon, angle, px=0, py=0):
    return transform_steps(polygon, about_point(op_rotate(angle), px, py),
                           f"Rotation by {fmt(angle)} deg about the pivot ({fmt(px)}, {fmt(py)})")


def reflection(polygon, kind):
    """kind: x-axis, y-axis, origin, y=x, y=-x, or a parallel line  x=c  /  y=c."""
    kind = kind.strip().lower().replace(" ", "")
    big = 100
    if kind in REFLECTIONS:
        ops = [op_reflect(kind)]
        lines = {"x-axis": [(-big, 0), (big, 0)], "y-axis": [(0, -big), (0, big)], "origin": [(-big, 0), (big, 0)],
                 "y=x": [(-big, -big), (big, big)], "y=-x": [(-big, big), (big, -big)]}
        mirror = (lines[kind], MIRROR, False)
        if kind == "origin":
            mirror = ([(0, -big), (0, big)], MIRROR, False)
    elif kind.startswith(("x=", "y=")):
        try:
            c = float(kind[2:])
        except ValueError:
            raise ValueError("Reflection must be one of: x-axis, y-axis, origin, y=x, y=-x, x=c, y=c")
        if kind[0] == "x":
            ops = about_point_axis(c, 0, "y-axis")
            mirror = ([(c, -big), (c, big)], MIRROR, False)
        else:
            ops = about_point_axis(0, c, "x-axis")
            mirror = ([(-big, c), (big, c)], MIRROR, False)
    else:
        raise ValueError("Reflection must be one of: x-axis, y-axis, origin, y=x, y=-x, x=c, y=c")
    return transform_steps(polygon, ops, f"Reflection about {kind}", mirror)


def about_point_axis(cx, cy, axis):
    """Reflect about a line parallel to an axis: translate, reflect about the axis, translate back."""
    return [(f"Move the mirror line to the {axis}",) + op_translate(-cx, -cy)[1:],
            op_reflect(axis),
            ("Move the mirror line back",) + op_translate(cx, cy)[1:]]


def parse_ops(text):
    """'T 4 3; R 45; S 2 2; F y=x'  ->  list of operations (applied left to right)."""
    ops = []
    for part in text.split(";"):
        t = part.replace(",", " ").split()
        if not t:
            continue
        name, args = t[0].upper(), t[1:]
        try:
            if name == "T" and len(args) == 2:
                ops.append(op_translate(*map(float, args)))
            elif name == "S" and len(args) == 2:
                ops.append(op_scale(*map(float, args)))
            elif name == "R" and len(args) == 1:
                ops.append(op_rotate(float(args[0])))
            elif name == "F" and len(args) == 1:
                ops.append(op_reflect(args[0].lower()))
            else:
                raise ValueError
        except ValueError:
            raise ValueError("Use: T tx ty;  S sx sy;  R angle;  F x-axis|y-axis|origin|y=x|y=-x   (separate with ;)")
    if not ops:
        raise ValueError("Enter at least one operation, e.g.  T 4 3; R 45")
    return ops


def composite(polygon, ops_text):
    ops = parse_ops(ops_text)
    return transform_steps(polygon, ops, f"Composite transformation ({len(ops)} operations)")