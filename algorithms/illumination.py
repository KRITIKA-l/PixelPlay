import math
from ._common import gray, normalize, dot, cell_box, outline


def phong_terms(N, L, ka, kd, ks, n):
    """(ambient, diffuse, specular) for a unit normal N, unit light vector L, viewer V = (0, 0, 1)."""
    nl = dot(N, L)
    R = tuple(2 * nl * N[i] - L[i] for i in range(3))
    diffuse = kd * max(0.0, nl)
    specular = ks * max(0.0, R[2]) ** n if nl > 0 else 0.0
    return ka, diffuse, specular, nl, R


def illumination(cx, cy, r, light, ka, kd, ks, n):
    """Phong illumination model on a sphere, built up in three layers: ambient, + diffuse, + specular."""
    L = normalize(light)
    pts = [(x, y) for y in range(cy - r, cy + r + 1) for x in range(cx - r, cx + r + 1)
           if (x - cx) ** 2 + (y - cy) ** 2 <= r * r and 0 <= x < 30 and 0 <= y < 30]
    ring = outline([(cx + r * math.cos(t * math.pi / 24), cy + r * math.sin(t * math.pi / 24)) for t in range(48)], "lightgray", 1)
    sx, sy = cx - max(1, round(0.3 * r)), cy + max(1, round(0.35 * r))          # sample point
    nx, ny = (sx - cx) / r, (sy - cy) / r
    N = (nx, ny, math.sqrt(max(0.0, 1 - nx * nx - ny * ny)))
    amb, dif, spe, nl, R = phong_terms(N, L, ka, kd, ks, n)
    f3 = lambda v: "(" + ", ".join(f"{c:.2f}" for c in v) + ")"
    sample = (f"Sample point ({sx}, {sy}) (orange box):\nN = (({sx} - {cx})/{r}, ({sy} - {cy})/{r}, sqrt(1 - nx^2 - ny^2)) = {f3(N)}\n"
              f"N . L = {nl:.3f}\nR = 2 (N . L) N - L = {f3(R)},   R . V = {R[2]:.3f}\n")

    def layer(mode):
        cells = []
        for x, y in pts:
            px, py = (x - cx) / r, (y - cy) / r
            Np = (px, py, math.sqrt(max(0.0, 1 - px * px - py * py)))
            a, d, s, _, _ = phong_terms(Np, L, ka, kd, ks, n)
            i = a + (d if mode >= 2 else 0) + (s if mode >= 3 else 0)
            cells.append((x, y, gray(255 * min(1.0, i))))
        return cells

    steps = [{"pixels": [(cx, cy)], "color": 5, "highlight": False, "shapes": [ring],
              "text": ("Phong illumination model on a sphere\n"
                       f"Centre ({cx}, {cy}), radius {r}. Light direction L = {f3(L)} (towards the light), viewer V = (0, 0, 1).\n"
                       f"ka = {ka:g} (ambient), kd = {kd:g} (diffuse), ks = {ks:g} (specular), shininess n = {n:g}.\n"
                       "I = ka*Ia + kd*Il*max(0, N.L) + ks*Il*max(0, R.V)^n,   Ia = Il = 1, clamped to 0..1.\n"
                       "The sphere normal at a pixel is N = ((x - xc)/r, (y - yc)/r, sqrt(1 - ...)).\n"
                       "Next: add the three terms one at a time. Grey level = 255 * I.")},
             {"cells": layer(1), "pixels": [], "shapes": [ring],
              "text": ("Ambient light only\nI = ka = " + f"{ka:g}" + "\nEvery pixel gets the same grey: the sphere looks like a flat disc.\n"
                       "Ambient light stands for light bounced around the room, coming from no particular direction.")},
             {"cells": layer(2), "pixels": [], "shapes": [ring, cell_box(sx, sy)],
              "text": ("Ambient + diffuse (Lambert)\nI = ka + kd max(0, N.L)\n" + sample +
                       f"diffuse = {kd:g} * {max(0, nl):.3f} = {dif:.3f}\n"
                       "Surfaces facing the light are bright, surfaces turned away fall back to ambient: the sphere now looks round.")},
             {"cells": layer(3), "pixels": [], "shapes": [ring, cell_box(sx, sy)],
              "text": ("Ambient + diffuse + specular (Phong)\nI = ka + kd max(0, N.L) + ks max(0, R.V)^n\n" + sample +
                       f"specular = {ks:g} * max(0, {R[2]:.3f})^{n:g} = {spe:.3f}\n"
                       f"I = {amb:.3f} + {dif:.3f} + {spe:.3f} = {min(1.0, amb + dif + spe):.3f}\n"
                       "The specular term adds the shiny highlight where the mirror direction R points at the viewer. "
                       "A larger n makes the highlight smaller and sharper.")},
             {"pixels": [], "shapes": [ring],
              "text": ("Done: illumination model complete\n"
                       "Ambient gives a base level, diffuse gives the 3-D shape, specular gives the shine.\n"
                       "Computing I at every pixel is Phong shading; computing it only at polygon vertices and "
                       "interpolating is Gouraud shading (see the next algorithms).")}]
    return steps