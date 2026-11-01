def bresenham_line(x1, y1, x2, y2):
    """Bresenham line drawing (all slopes). Returns a list of steps."""
    steps = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    x, y = x1, y1
    error = dx - dy
    k = 0

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
        for s in bresenham_line(x1, y1, x2, y2):
            pixels += s["pixels"]
    return pixels
