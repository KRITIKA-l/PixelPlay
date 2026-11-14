import math
from ._common import PALETTE, NAMES, cell_box, outline


def zbuffer(tris, size=30):
    """Z-buffer (depth buffer). One step per pixel that a triangle covers.
    tris: list of triangles, each ((x1,y1,z1), (x2,y2,z2), (x3,y3,z3)).  Smaller z = nearer to the viewer."""
    n = len(tris)
    planes = []
    for k, t in enumerate(tris):
        (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = t
        nx = (y2 - y1) * (z3 - z1) - (z2 - z1) * (y3 - y1)
        ny = (z2 - z1) * (x3 - x1) - (x2 - x1) * (z3 - z1)
        nz = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
        if abs(nz) < 1e-9:
            raise ValueError(f"Triangle {NAMES[k]} is degenerate (its 3 points lie on a line)")
        a, b = -nx / nz, -ny / nz
        planes.append((a, b, z1 - a * x1 - b * y1))              # z = a x + b y + c

    outlines = [outline([(p[0], p[1]) for p in t], PALETTE[k]) for k, t in enumerate(tris)]
    desc = "\n".join(f"Triangle {NAMES[k]}: z = {pl[0]:.2f} x + {pl[1]:.2f} y + {pl[2]:.2f}" for k, pl in enumerate(planes))
    steps = [{"text": (f"Z-buffer algorithm: {n} triangles\n"
                       "Two buffers: the frame buffer (colour of each pixel) and the z-buffer (depth of each pixel).\n"
                       "z-buffer starts at infinity (everything is far away), frame buffer starts white.\n"
                       "Smaller z = nearer to the viewer.\n"
                       "For every pixel of every triangle: z = depth of the triangle at that pixel.\n"
                       "If z < z-buffer: draw the pixel and store z.  Otherwise ignore it.\n"
                       "The triangles can come in ANY order.\n" + desc),
              "shapes": outlines}]

    zbuf = [[math.inf] * size for _ in range(size)]
    owner = {}
    rejected = 0
    for k, t in enumerate(tris):
        a, b, c = planes[k]
        xs, ys = [p[0] for p in t], [p[1] for p in t]
        for y in range(max(0, math.floor(min(ys))), min(size - 1, math.ceil(max(ys))) + 1):
            for x in range(max(0, math.floor(min(xs))), min(size - 1, math.ceil(max(xs))) + 1):
                e = []
                for i in range(3):
                    xa, ya, _ = t[i]
                    xb, yb, _ = t[(i + 1) % 3]
                    e.append((xb - xa) * (y - ya) - (yb - ya) * (x - xa))
                if not (all(v >= -1e-9 for v in e) or all(v <= 1e-9 for v in e)):
                    continue                                       # pixel is outside this triangle
                z = a * x + b * y + c
                cur = zbuf[y][x]
                cur_txt = "infinity" if cur == math.inf else f"{cur:.2f}"
                head = (f"Triangle {NAMES[k]}, pixel ({x}, {y})\nz = {a:.2f}*{x} + {b:.2f}*{y} + {c:.2f} = {z:.2f}\n"
                        f"z-buffer[{x}][{y}] = {cur_txt}\n")
                if z < cur - 1e-9:
                    zbuf[y][x] = z
                    owner[(x, y)] = k
                    steps.append({"pixels": [(x, y)], "color": PALETTE[k], "highlight": False,
                                  "shapes": outlines + [cell_box(x, y)], "labels": [(x, y, f"{z:.1f}")],
                                  "text": head + f"{z:.2f} < {cur_txt}: nearer -> draw triangle {NAMES[k]} here "
                                                 f"and set z-buffer = {z:.2f}"})
                else:
                    rejected += 1
                    steps.append({"pixels": [], "shapes": outlines + [cell_box(x, y, "gray")],
                                  "text": head + f"{z:.2f} >= {cur_txt}: farther (or equal) -> ignore, the pixel is hidden"})
    counts = [sum(1 for v in owner.values() if v == k) for k in range(n)]
    steps.append({"pixels": [], "shapes": outlines,
                  "text": ("Done: all triangles processed\n" +
                           "\n".join(f"Triangle {NAMES[k]}: {counts[k]} visible pixels" for k in range(n)) +
                           f"\n{rejected} pixel tests failed (hidden surface removed).\n"
                           "Cost: one depth compare per covered pixel; extra memory = one z value per pixel.")})
    return steps