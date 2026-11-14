import math
from ._common import gray, label_colour, cell_box, rect, line
from .image_filter import read_image, pos, X0, Y0, OX, VIEW, SIZE
from .transform2d import parse_ops, mat_mul, fmt, fmt_matrix


def inverse(m):
    a, b, tx = m[0]
    c, d, ty = m[1]
    det = a * d - b * c
    if abs(det) < 1e-9:
        raise ValueError("This transformation squashes the image to a line (determinant 0) and cannot be inverted")
    ia, ib, ic, id_ = d / det, -b / det, -c / det, a / det
    return [[ia, ib, -(ia * tx + ib * ty)], [ic, id_, -(ic * tx + id_ * ty)], [0, 0, 1]]


def image_geometry(ops_text, image_text):
    """Geometric transformation of an image with INVERSE mapping + nearest-neighbour sampling."""
    ops = parse_ops(ops_text)
    img = read_image(image_text)
    centre = (SIZE - 1) / 2
    total = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    for _, m, _ in ops:
        total = mat_mul(m, total)
    to0 = [[1, 0, -centre], [0, 1, -centre], [0, 0, 1]]
    back = [[1, 0, centre], [0, 1, centre], [0, 0, 1]]
    M = mat_mul(back, mat_mul(total, to0))                      # transform about the image centre
    Minv = inverse(M)

    value = lambda u, v: img[SIZE - 1 - v][u]                   # u = column, v = row counted from the BOTTOM
    cells_in = [(X0 + u, Y0 + v, gray(value(u, v))) for v in range(SIZE) for u in range(SIZE)]
    labels_in = [(X0 + u, Y0 + v, str(value(u, v)), label_colour(value(u, v))) for v in range(SIZE) for u in range(SIZE)]
    heads = [(X0 + 3.5, Y0 + SIZE + 1.2, "SOURCE", "black", 0.6), (OX + 3.5, Y0 + SIZE + 1.2, "RESULT", "black", 0.6)]
    frame = [rect(X0, Y0, X0 + 7, Y0 + 7, "black", 2), rect(OX, Y0, OX + 7, Y0 + 7, "black", 2)]
    out = {}

    def out_labels():
        return [(OX + u, Y0 + v, str(g), label_colour(g)) for (u, v), g in out.items()]

    steps = [{"view": VIEW, "cells": cells_in, "pixels": [], "shapes": frame, "labels": heads + labels_in,
              "text": ("Geometric transformation of an image\n"
                       "Operations: " + "; ".join(label for label, _, _ in ops) + ".\n"
                       "All of them are done about the image centre, so M = T(c) . M_ops . T(-c):\n" + fmt_matrix(M) + "\n"
                       "Forward mapping (source -> result) leaves holes and overlaps.\n"
                       "So we use INVERSE mapping: for every RESULT pixel find where it comes from, "
                       "(u, v) = M^-1 (u', v'), and copy the nearest source pixel.\n"
                       "If that point is outside the source image the result pixel is black.")}]
    for v in range(SIZE - 1, -1, -1):
        for u in range(SIZE):
            us = Minv[0][0] * u + Minv[0][1] * v + Minv[0][2]
            vs = Minv[1][0] * u + Minv[1][1] * v + Minv[1][2]
            ru, rv = math.floor(us + 0.5), math.floor(vs + 0.5)
            ok = 0 <= ru < SIZE and 0 <= rv < SIZE
            g = value(ru, rv) if ok else 0
            out[(u, v)] = g
            shapes = frame + [cell_box(OX + u, Y0 + v)]
            if ok:
                shapes += [cell_box(X0 + ru, Y0 + rv), line((X0 + ru + .5, Y0 + rv), (OX + u - .5, Y0 + v), "orange", 1, "--")]
            steps.append({"cells": [(OX + u, Y0 + v, gray(g))], "pixels": [], "shapes": shapes,
                          "labels": heads + labels_in + out_labels(),
                          "text": (f"Result pixel (u', v') = ({u}, {v})\n"
                                   f"u = {fmt(Minv[0][0])}*{u} + {fmt(Minv[0][1])}*{v} + {fmt(Minv[0][2])} = {us:.2f}\n"
                                   f"v = {fmt(Minv[1][0])}*{u} + {fmt(Minv[1][1])}*{v} + {fmt(Minv[1][2])} = {vs:.2f}\n"
                                   f"Nearest source pixel: ({ru}, {rv})\n" +
                                   (f"Copy its value {g} to the result" if ok else "Outside the source image -> black (0)"))})
    steps.append({"pixels": [], "shapes": frame, "labels": heads + labels_in + out_labels(),
                  "text": ("Done: geometric transformation complete\n"
                           "Nearest-neighbour sampling is fast but gives jagged edges; bilinear interpolation (averaging "
                           "the 4 nearest pixels) gives smoother results.")})
    return steps