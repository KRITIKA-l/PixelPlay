def bresenham_line(x1, y1, x2, y2, show_ends=True):
    """Bresenham line drawing (all slopes). Returns a list of steps.
    The first step marks both end points (show_ends=False leaves that step out)."""
    steps = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    x, y = x1, y1
    error = dx - dy
    k = 0

    if show_ends:
        steps.append({
            "pixels": [(x1, y1), (x2, y2)],
            "color": 5,
            "highlight": False,
            "text": (f"Input: the line to draw\nStart pixel ({x1}, {y1}) and end pixel ({x2}, {y2}) are marked in red.\n"
                     f"dx = {dx}, dy = {dy}, sx = {sx}, sy = {sy}, error = dx - dy = {error}\n"
                     "The line is now drawn from the start to the end.")
        })

    while True:
        e2 = 2 * error
        steps.append({
            "pixels": [(x, y)],
            "color": 2,
            "text": (f"Step {k}\nPlot pixel ({x}, {y})\n"
                     f"error = {error}, 2*error = {e2}\n"
                     f"If 2*error > -dy ({-dy}): move in x\n"
                     f"If 2*error < dx ({dx}): move in y")
        })
        if x == x2 and y == y2:
            break
        if e2 > -dy:
            error -= dy
            x += sx
        if e2 < dx:
            error += dx
            y += sy
        k += 1
    return steps


def polygon_outline(polygon):
    """Pixels of a polygon outline (uses Bresenham for every edge)."""
    pixels = []
    for i in range(len(polygon)):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % len(polygon)]
        for s in bresenham_line(x1, y1, x2, y2, show_ends=False):
            pixels += s["pixels"]
    return pixels