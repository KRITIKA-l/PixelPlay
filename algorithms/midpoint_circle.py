def midpoint_circle(cx, cy, r):
    """Midpoint circle algorithm. Each step plots 8 symmetric points."""
    steps = []
    x = 0
    y = r
    p = 1 - r

    while x <= y:
        points = [(cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y), (cx - x, cy - y),
                  (cx + y, cy + x), (cx - y, cy + x), (cx + y, cy - x), (cx - y, cy - x)]
        choice = "p < 0 -> choose East (y stays)" if p < 0 else "p >= 0 -> choose South-East (y decreases)"
        steps.append({
            "pixels": points,
            "color": 2,
            "text": (f"x = {x}, y = {y}\nDecision p = {p}\n{choice}\n"
                     f"Plot 8 symmetric points around ({cx},{cy})")
        })
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
    return steps
