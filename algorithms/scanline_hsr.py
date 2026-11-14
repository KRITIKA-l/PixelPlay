import math
from ._common import PALETTE, NAMES, outline, line


def row_spans(poly, y, top):
    """x-intersections of a polygon with scan line y and the filled spans (same rule as the scan-line fill)."""
    xs, n = [], len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if y1 == y2:
            continue
        low, high = min(y1, y2), max(y1, y2)
        if low <= y < high or (y == top and high == top):
            xs.append(round(x1 + (y - y1) * (x2 - x1) / (y2 - y1), 6))
    xs.sort()
    spans = [(math.ceil(xs[i]), math.floor(xs[i + 1])) for i in range(0, len(xs) - 1, 2)]
    return xs, [s for s in spans if s[0] <= s[1]]


def scanline_hsr(polys, size=30):
    """Scan-line hidden surface removal. One step per scan line: find the spans of every polygon, then in the
    overlapping parts show the polygon with the smallest z. polys: list of (vertices, z)."""
    n = len(polys)
    zs = [z for v, z in polys]
    tops = [max(p[1] for p in v) for v, z in polys]
    outs = [outline(v, PALETTE[k], 1) for k, (v, z) in enumerate(polys)]
    ymin = min(p[1] for v, z in polys for p in v)
    ymax = max(tops)
    steps = [{"text": ("Scan-line hidden surface removal\n"
                       f"{n} polygons, each with one depth z (smaller z = nearer).\n"
                       "For every scan line y:\n"
                       " 1. find where each polygon crosses the line -> its span(s) [x_start, x_end]\n"
                       " 2. cut the line wherever a span starts or ends\n"
                       " 3. in every part, show the polygon with the smallest z\n"
                       "Only one scan line is kept in memory at a time."),
              "shapes": outs}]
    painted = {}
    for y in range(ymin, ymax + 1):
        spans = [row_spans(v, y, tops[k])[1] for k, (v, z) in enumerate(polys)]
        if not any(spans):
            continue
        owner, cand = {}, {}
        for x in range(size):
            c = [k for k in range(n) if any(a <= x <= b for a, b in spans[k])]
            if c:
                cand[x] = c
                owner[x] = min(c, key=lambda k: zs[k])
        cells = [(x, y, PALETTE[k]) for x, k in owner.items()]
        for x, k in owner.items():
            painted[(x, y)] = k

        def groups(mapping, test):
            out, cur = [], None
            for x in sorted(mapping):
                v = mapping[x]
                if not test(v):
                    cur = None
                    continue
                if cur and cur[2] == v and cur[1] == x - 1:
                    cur[1] = x
                else:
                    cur = [x, x, v]
                    out.append(cur)
            return out

        overlaps = [f"x {a}..{b}: " + " vs ".join(f"{NAMES[k]} (z = {zs[k]:g})" for k in c) + f" -> show {NAMES[min(c, key=lambda k: zs[k])]}"
                    for a, b, c in groups(cand, lambda c: len(c) > 1)]
        visible = [f"{NAMES[k]}: x {a}..{b}" for a, b, k in groups(owner, lambda k: True)]
        span_txt = "\n".join(f"Polygon {NAMES[k]} span: " + (", ".join(f"[{a}, {b}]" for a, b in spans[k]) or "none")
                             for k in range(n))
        steps.append({"cells": cells, "pixels": [],
                      "shapes": outs + [line((-0.5, y), (size - 0.5, y), "orange", 2)],
                      "text": (f"Scan line y = {y}\n{span_txt}\n" +
                               ("Overlapping parts:\n" + "\n".join(overlaps) + "\n" if overlaps else "No overlap on this line.\n") +
                               "Visible: " + "; ".join(visible))})
    counts = [sum(1 for v in painted.values() if v == k) for k in range(n)]
    steps.append({"pixels": [], "shapes": outs,
                  "text": ("Done: all scan lines processed\n" +
                           "\n".join(f"Polygon {NAMES[k]}: {counts[k]} visible pixels" for k in range(n)) +
                           "\nNo z-buffer for the whole screen is needed: only the current line is resolved.")})
    return steps