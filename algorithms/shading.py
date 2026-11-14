import math
from ._common import gray, normalize, dot, outline, line
from .illumination import phong_terms

KA, KD, KS, NSHINE = 0.15, 0.6, 0.7, 30
DOME = 14.0


def intensity(N, L):
    a, d, s, _, _ = phong_terms(N, L, KA, KD, KS, NSHINE)
    return min(1.0, a + d + s)


def lerp(a, b, t):
    if isinstance(a, tuple):
        return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))
    return a + (b - a) * t


def shade_triangle(tri, light, method):
    """Flat, Gouraud or Phong shading of one triangle, one scan line per step."""
    L = normalize(light)
    cx = sum(p[0] for p in tri) / 3
    cy = sum(p[1] for p in tri) / 3
    normals = [normalize(((p[0] - cx) / DOME, (p[1] - cy) / DOME, 1.0)) for p in tri]     # a dome-like surface
    inten = [intensity(n, L) for n in normals]
    face = normalize(tuple(sum(n[i] for n in normals) for i in range(3)))
    face_i = intensity(face, L)
    f3 = lambda v: "(" + ", ".join(f"{c:.2f}" for c in v) + ")"
    out = outline(tri, "black", 1)
    ys = [p[1] for p in tri]
    top, bottom = max(ys), min(ys)
    names = {"flat": "Flat shading", "gouraud": "Gouraud shading", "phong": "Phong shading"}
    how = {"flat": "ONE intensity for the whole polygon, computed from its face normal.",
           "gouraud": "Compute the intensity at the 3 VERTICES, then interpolate the intensity along the edges and across each scan line.",
           "phong": "Interpolate the NORMAL along the edges and across each scan line, then compute the intensity at EVERY pixel."}[method]
    vtext = "\n".join(f"V{i + 1} ({tri[i][0]}, {tri[i][1]}): N = {f3(normals[i])}, I = {inten[i]:.2f}" for i in range(3))
    arrows = [line(tri[i], (tri[i][0] + normals[i][0] * 4, tri[i][1] + normals[i][1] * 4), "purple", 2) for i in range(3)]
    steps = [{"pixels": [], "shapes": [out] + (arrows if method == "phong" else []),
              "labels": [(tri[i][0], tri[i][1], f"{inten[i]:.2f}", "white" if inten[i] < .5 else "black") for i in range(3)] if method == "gouraud" else [],
              "text": (f"{names[method]}\n{how}\n"
                       f"Light L = {f3(L)}, viewer V = (0, 0, 1); ka = {KA}, kd = {KD}, ks = {KS}, n = {NSHINE}.\n"
                       "The vertex normals fan out like a dome (a curved surface approximated by a flat triangle).\n" + vtext +
                       (f"\nFace normal = average of the 3 = {f3(face)}, I = {face_i:.2f}" if method == "flat" else ""))}]
    edges = [(tri[i], tri[(i + 1) % 3], i, (i + 1) % 3) for i in range(3)]
    attr = inten if method == "gouraud" else normals
    count = 0
    for y in range(bottom, top + 1):
        hits = []
        for a, b, ia, ib in edges:
            if a[1] == b[1]:
                continue
            lo, hi = min(a[1], b[1]), max(a[1], b[1])
            if lo <= y < hi or (y == top and hi == top):
                t = (y - a[1]) / (b[1] - a[1])
                at = lerp(attr[ia], attr[ib], t) if method != "flat" else None
                hits.append((a[0] + t * (b[0] - a[0]), at, f"V{ia + 1}V{ib + 1}", t))
        if len(hits) < 2:
            continue
        hits.sort(key=lambda h: h[0])
        left, right = hits[0], hits[-1]
        x_a, x_b = math.ceil(round(left[0], 6)), math.floor(round(right[0], 6))
        if x_a > x_b:
            continue
        cells = []
        for x in range(x_a, x_b + 1):
            s = (x - left[0]) / (right[0] - left[0]) if right[0] > left[0] else 0.0
            if method == "flat":
                i_pix = face_i
            elif method == "gouraud":
                i_pix = lerp(left[1], right[1], s)
            else:
                i_pix = intensity(normalize(lerp(left[1], right[1], s)), L)
            cells.append((x, y, gray(255 * max(0.0, min(1.0, i_pix)))))
        count += len(cells)
        if method == "flat":
            body = f"All pixels get I = {face_i:.2f}"
        elif method == "gouraud":
            body = (f"Left edge {left[2]} at x = {left[0]:.2f}: I_L = {left[1]:.2f}\nRight edge {right[2]} at x = {right[0]:.2f}: I_R = {right[1]:.2f}\n"
                    f"Pixel intensity = I_L + (I_R - I_L)(x - x_L)/(x_R - x_L)\nFirst pixel x = {x_a}: I = {lerp(left[1], right[1], (x_a - left[0]) / (right[0] - left[0]) if right[0] > left[0] else 0):.2f}")
        else:
            nl_, nr_ = normalize(left[1]), normalize(right[1])
            mid = (x_a + x_b) // 2
            sm = (mid - left[0]) / (right[0] - left[0]) if right[0] > left[0] else 0.0
            nm = normalize(lerp(left[1], right[1], sm))
            body = (f"Left edge {left[2]} at x = {left[0]:.2f}: N_L = {f3(nl_)}\nRight edge {right[2]} at x = {right[0]:.2f}: N_R = {f3(nr_)}\n"
                    f"Interpolate N across the line, re-normalise it, then compute I per pixel.\n"
                    f"Pixel x = {mid}: N = {f3(nm)} -> I = {intensity(nm, L):.2f}")
        steps.append({"cells": cells, "pixels": [], "shapes": [out, line((x_a - .5, y), (x_b + .5, y), "orange", 2)],
                      "text": f"Scan line y = {y}{' (top row)' if y == top else ''}\nFill x = {x_a} .. {x_b} ({x_b - x_a + 1} pixels)\n{body}"})
    notes = {"flat": "Flat shading is cheapest (one intensity per polygon) but shows every facet as a separate patch.",
             "gouraud": "Gouraud interpolates intensities: smooth, but a highlight inside the polygon is missed because it is not at a vertex (compare with Phong shading).",
             "phong": "Phong shading interpolates normals: the highlight in the middle of the polygon appears, at the price of an illumination calculation for every pixel."}
    steps.append({"pixels": [], "shapes": [out], "text": f"Done: {count} pixels shaded\n{notes[method]}"})
    return steps