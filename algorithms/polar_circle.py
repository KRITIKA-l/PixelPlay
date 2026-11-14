import math


def polar_circle(cx, cy, r, sym=4):
    """Polar (parametric) circle algorithm.
    x = r cos(theta), y = r sin(theta), step d_theta = 1 / r.
    sym = 4: theta runs 0 .. 90 deg and every step plots 4 symmetric points (one per quadrant).
    sym = 8: theta runs 0 .. 45 deg and every step plots 8 symmetric points (one per octant)."""
    steps = []
    dt = 1 / r if r > 0 else 1
    limit = math.pi / 2 if sym == 4 else math.pi / 4
    eps = 1e-9
    e = r + 1.5
    style = ("mediumpurple", False, 1, "--")
    dividers = [([(cx - e, cy), (cx + e, cy)],) + style, ([(cx, cy - e), (cx, cy + e)],) + style]
    if sym == 8:
        dividers += [([(cx - e, cy - e), (cx + e, cy + e)],) + style, ([(cx - e, cy + e), (cx + e, cy - e)],) + style]
    name = "quadrant" if sym == 4 else "octant"
    deg = lambda t: math.degrees(t)

    steps.append({
        "pixels": [(cx, cy)],
        "color": 5,
        "highlight": False,
        "shapes": dividers,
        "text": (f"Input: centre ({cx}, {cy}), radius r = {r}\n"
                 "Only the centre is marked (red) - the circle is not drawn yet.\n"
                 f"Angle step d_theta = 1 / r = {dt:.4f} rad = {deg(dt):.2f} degrees\n"
                 f"theta runs from 0 to {deg(limit):.0f} degrees; the dashed lines cut the circle into {sym} {name}s.\n"
                 f"Each step: x = r cos(theta), y = r sin(theta), round, then plot {sym} symmetric points.")
    })

    k = 0
    while True:
        t = min(k * dt, limit)                      # the last step is clamped to exactly the limit angle
        last = t >= limit - eps
        fx, fy = r * math.cos(t), r * math.sin(t)
        x, y = round(fx), round(fy)
        if sym == 4:
            pts = [(cx + x, cy + y), (cx - x, cy + y), (cx - x, cy - y), (cx + x, cy - y)]
            listing = f"Q1 ({pts[0][0]},{pts[0][1]})   Q2 ({pts[1][0]},{pts[1][1]})\nQ3 ({pts[2][0]},{pts[2][1]})   Q4 ({pts[3][0]},{pts[3][1]})"
        else:
            pts = [(cx + y, cy + x), (cx + x, cy + y), (cx - x, cy + y), (cx - y, cy + x),
                   (cx - y, cy - x), (cx - x, cy - y), (cx + x, cy - y), (cx + y, cy - x)]
            t8 = [f"Oct{j + 1} ({pts[j][0]},{pts[j][1]})" for j in range(8)]
            listing = "\n".join(f"{t8[j]}   {t8[j + 1]}" for j in range(0, 8, 2))
        nxt = (f"theta reached {deg(limit):.0f} degrees -> stop." if last else
               f"Next: theta = theta + d_theta = {deg(min(t + dt, limit)):.2f} degrees")
        steps.append({
            "pixels": pts,
            "color": 2,
            "shapes": dividers,
            "text": (f"Step {k}: theta = {deg(t):.2f} degrees\n"
                     f"x = {r} * cos(theta) = {fx:.2f}  ->  {x}\n"
                     f"y = {r} * sin(theta) = {fy:.2f}  ->  {y}\n"
                     f"Plot the {sym} symmetric points, one per {name}:\n{listing}\n{nxt}")
        })
        if last:
            break
        k += 1
    return steps