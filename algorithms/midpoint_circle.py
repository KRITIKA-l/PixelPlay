def octant_lines(cx, cy, r):
    """Thin dashed dividers (horizontal, vertical, both diagonals) that cut the circle into its 8 octants."""
    e = r + 1.5
    style = ("mediumpurple", False, 1, "--")
    return [([(cx - e, cy), (cx + e, cy)],) + style, ([(cx, cy - e), (cx, cy + e)],) + style,
            ([(cx - e, cy - e), (cx + e, cy + e)],) + style, ([(cx - e, cy + e), (cx + e, cy - e)],) + style]


def octants(cx, cy, x, y):
    """The 8 symmetric points in octant order 1..8 (counter-clockwise from the +x axis) and a text listing."""
    pts = [(cx + y, cy + x), (cx + x, cy + y), (cx - x, cy + y), (cx - y, cy + x),
           (cx - y, cy - x), (cx - x, cy - y), (cx + x, cy - y), (cx + y, cy - x)]
    t = [f"Oct{k + 1} ({pts[k][0]},{pts[k][1]})" for k in range(8)]
    return pts, "\n".join(f"{t[k]}   {t[k + 1]}" for k in range(0, 8, 2))


def midpoint_circle(cx, cy, r):
    """Midpoint circle algorithm. Each step plots 8 symmetric points."""
    steps = []
    x = 0
    y = r
    p = 1 - r

    steps.append({
        "pixels": [(cx, cy)],
        "color": 5,
        "highlight": False,
        "shapes": octant_lines(cx, cy, r),
        "text": (f"Input: centre ({cx}, {cy}), radius r = {r}\n"
                 "Only the centre is marked (red) - the circle is not drawn yet.\n"
                 "Start at (x, y) = (0, r) with p = 1 - r = " + str(p) + "\n"
                 "The dashed lines cut the circle into its 8 octants.\n"
                 "Each step below plots 8 symmetric points, one in each octant.")
    })

    while x <= y:
        points, listing = octants(cx, cy, x, y)
        choice = "p < 0 -> choose East (y stays)" if p < 0 else "p >= 0 -> choose South-East (y decreases)"
        steps.append({
            "pixels": points,
            "color": 2,
            "shapes": octant_lines(cx, cy, r),
            "text": (f"x = {x}, y = {y}\nDecision p = {p}\n{choice}\n"
                     f"Plot the 8 symmetric points, one per octant:\n{listing}")
        })
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
    return steps