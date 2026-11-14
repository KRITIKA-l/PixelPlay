from ._common import PALETTE, NAMES, polygon_pixels, outline, rect


def area_subdivision(polys, size=30):
    """Warnock area-subdivision algorithm. polys: list of (vertices, z). Smaller z = nearer.
    A square region is either simple enough to paint at once or it is cut into 4 quarters."""
    n = len(polys)
    cover = [set(polygon_pixels(v, size)) for v, z in polys]
    zs = [z for v, z in polys]
    outs = [outline(v, PALETTE[k], 1) for k, (v, z) in enumerate(polys)]
    top = 1
    while top < size:
        top *= 2
    names = lambda idx: ", ".join(NAMES[i] for i in idx) or "none"

    steps = [{"text": ("Area subdivision (Warnock)\n"
                       f"{n} polygons, each with one depth z (smaller z = nearer).\n"
                       f"Start with the whole {top} x {top} window as one region. For every region compare it with each polygon:\n"
                       " disjoint: the polygon does not touch the region\n"
                       " surrounding: the polygon covers the whole region\n"
                       " contained / intersecting: the polygon is inside / partly inside the region\n"
                       "Simple cases are painted at once, otherwise the region is cut into 4 quarters.\n"
                       "Orange = region being examined, light gray = regions already examined."),
              "shapes": outs}]
    seen = []
    painted = {}
    regions = direct = 0
    stack = [(0, 0, top)]
    while stack:
        x0, y0, s = stack.pop()
        pix = [(x, y) for y in range(y0, min(y0 + s, size)) for x in range(x0, min(x0 + s, size))]
        if not pix:
            continue                                                 # region lies completely outside the canvas
        regions += 1
        rset = set(pix)
        inter, cls = [], []
        for i in range(n):
            part = cover[i] & rset
            inter.append(part)
            if not part:
                cls.append("disjoint")
            elif len(part) == len(pix):
                cls.append("surrounding")
            elif len(part) == len(cover[i]):
                cls.append("contained")
            else:
                cls.append("intersecting")
        act = [i for i in range(n) if cls[i] != "disjoint"]
        x1, y1 = x0 + s - 1, y0 + s - 1
        head = (f"Region x {x0}..{x1}, y {y0}..{y1} ({s} x {s})\n" +
                "\n".join(f"Polygon {NAMES[i]} (z = {zs[i]:g}): {cls[i]}" for i in range(n)) + "\n")
        shape = seen + outs + [rect(x0, y0, x1, y1, "orange", 3)]
        paint = None
        if not act:
            case = "Case 1: every polygon is disjoint -> region stays background (nothing to draw)"
        elif len(act) == 1:
            i = act[0]
            paint = (i, inter[i])
            case = (f"Case 2/3: only polygon {NAMES[i]} touches the region -> background, then paint the part of "
                    f"{NAMES[i]} inside it ({len(inter[i])} pixels)" if cls[i] != "surrounding" else
                    f"Case 3: only polygon {NAMES[i]} touches the region and it surrounds it -> paint the whole region with {NAMES[i]}")
        else:
            surr = [i for i in act if cls[i] == "surrounding"]
            best = min(surr, key=lambda i: zs[i]) if surr else None
            if best is not None and all(zs[best] < zs[j] for j in act if j != best):
                paint = (best, rset)
                case = (f"Case 4: polygons {names(act)} touch the region; surrounding polygon {NAMES[best]} "
                        f"(z = {zs[best]:g}) is nearer than all the others -> paint the whole region with {NAMES[best]}")
            elif s == 1:
                best = min(act, key=lambda i: zs[i])
                paint = (best, rset)
                case = f"Single pixel: polygons {names(act)} cover it -> the nearest one (smallest z) is {NAMES[best]}"
            else:
                case = (f"Polygons {names(act)} touch the region and no surrounding polygon is in front of all "
                        f"-> too complex: cut the region into 4 quarters of {s // 2} x {s // 2}")
        if paint:
            i, pixset = paint
            for p in pixset:
                painted[p] = i
            direct += 1
            steps.append({"pixels": sorted(pixset), "color": PALETTE[i], "highlight": False, "shapes": shape,
                          "text": head + case})
            seen.append(rect(x0, y0, x1, y1, "lightgray", 1))
        elif not act:
            steps.append({"pixels": [], "shapes": shape, "text": head + case})
            seen.append(rect(x0, y0, x1, y1, "lightgray", 1))
        else:
            steps.append({"pixels": [], "shapes": shape, "text": head + case})
            seen.append(rect(x0, y0, x1, y1, "#e3e3e3", 1, "--"))
            h = s // 2
            for qx, qy in ((x0 + h, y0 + h), (x0, y0 + h), (x0 + h, y0), (x0, y0)):    # popped as: bottom-left first
                stack.append((qx, qy, h))
    counts = [sum(1 for v in painted.values() if v == k) for k in range(n)]
    steps.append({"pixels": [], "shapes": outs + seen,
                  "text": ("Done: every region is resolved\n" +
                           "\n".join(f"Polygon {NAMES[k]}: {counts[k]} visible pixels" for k in range(n)) +
                           f"\n{regions} regions examined, {direct} of them painted directly.\n"
                           "Large simple areas are finished in one step; only regions along the polygon edges are cut down "
                           "to small squares.")})
    return steps