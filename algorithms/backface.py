import math
from ._common import PALETTE6, cross, normalize, inside, outline, line


def backface_culling(cx, cy, size, ry, rx):
    """Back-face culling on a cube viewed from +z (orthographic, z is dropped).
    A face is hidden (back-facing) when its outward normal N points away from the viewer: N . V <= 0."""
    h = size / 2.0
    names = ["front (+z)", "back (-z)", "right (+x)", "left (-x)", "top (+y)", "bottom (-y)"]
    base = [[(-h, -h, h), (h, -h, h), (h, h, h), (-h, h, h)],
            [(-h, -h, -h), (-h, h, -h), (h, h, -h), (h, -h, -h)],
            [(h, -h, -h), (h, h, -h), (h, h, h), (h, -h, h)],
            [(-h, -h, -h), (-h, -h, h), (-h, h, h), (-h, h, -h)],
            [(-h, h, -h), (-h, h, h), (h, h, h), (h, h, -h)],
            [(-h, -h, -h), (h, -h, -h), (h, -h, h), (-h, -h, h)]]

    def rot(p):
        x, y, z = p
        a = math.radians(ry)
        c, s = math.cos(a), math.sin(a)
        x, z = x * c + z * s, -x * s + z * c
        a = math.radians(rx)
        c, s = math.cos(a), math.sin(a)
        y, z = y * c - z * s, y * s + z * c
        return (x, y, z)

    faces = [[rot(p) for p in f] for f in base]
    flat = [[(cx + p[0], cy + p[1]) for p in f] for f in faces]
    V = (0, 0, 1)
    info = []
    for f in faces:
        n = cross(tuple(f[1][i] - f[0][i] for i in range(3)), tuple(f[2][i] - f[1][i] for i in range(3)))
        info.append((n, normalize(n)))
    visible = [i[1][2] > 1e-9 for i in info]
    gray_faces = [outline(f, "lightgray") for f in flat]

    def f3(p):
        return "(" + ", ".join(f"{v:.1f}" for v in p) + ")"

    steps = [{"text": ("Back-face culling\n"
                       f"Cube of edge {size:g} at ({cx:g}, {cy:g}), rotated {ry:g} deg about Y, then {rx:g} deg about X.\n"
                       "The viewer is on the +z axis, so the view vector is V = (0, 0, 1).\n"
                       "For each face take its OUTWARD normal N = (v1 - v0) x (v2 - v1).\n"
                       "N . V > 0: the face looks at the viewer -> visible.\n"
                       "N . V <= 0: the face looks away -> back face, hidden (not drawn)."),
              "shapes": gray_faces}]
    decided = {}
    for k in range(6):
        n, nh = info[k]
        centre = (sum(p[0] for p in flat[k]) / 4, sum(p[1] for p in flat[k]) / 4)
        shapes = []
        for j in range(6):
            if j in decided:
                shapes.append(outline(flat[j], "green", 3) if decided[j] else outline(flat[j], "red", 1, "--"))
            elif j != k:
                shapes.append(outline(flat[j], "lightgray"))
        shapes.append(outline(flat[k], "orange", 3))
        shapes.append(line(centre, (centre[0] + nh[0] * 4, centre[1] + nh[1] * 4), "purple", 3))
        vis = visible[k]
        steps.append({"shapes": shapes,
                      "text": (f"Face {k + 1}: {names[k]}\n"
                               f"v0 = {f3(faces[k][0])}\nv1 = {f3(faces[k][1])}\nv2 = {f3(faces[k][2])}\n"
                               f"N = (v1 - v0) x (v2 - v1) = {f3(n)}\n"
                               f"Unit normal = {f3(nh)}  (purple arrow)\n"
                               f"N . V = {nh[2]:.3f}\n" +
                               ("N . V > 0 -> front face: VISIBLE" if vis else "N . V <= 0 -> back face: HIDDEN"))})
        decided[k] = vis

    cells, finals = [], []
    for x in range(int(cx - size), int(cx + size) + 2):
        for y in range(int(cy - size), int(cy + size) + 2):
            if 0 <= x < 30 and 0 <= y < 30:
                for k in range(6):
                    if visible[k] and inside(flat[k], x, y):
                        cells.append((x, y, PALETTE6[k]))
    for k in range(6):
        if visible[k]:
            finals.append(outline(flat[k], "black", 2))
    vis_names = [names[k] for k in range(6) if visible[k]]
    steps.append({"cells": cells, "pixels": [], "shapes": finals,
                  "text": (f"Done: {len(vis_names)} of 6 faces are visible\n"
                           "Visible: " + ", ".join(vis_names) + "\n"
                           "Hidden faces are removed before any filling, so about half of the polygons are never processed.\n"
                           "This test is enough on its own only for a single convex solid; overlapping objects "
                           "still need the Z-buffer or another method.")})
    return steps