import math


def dda_line(x1, y1, x2, y2):
    """DDA line drawing. Returns a list of steps."""
    steps = []
    dx = x2 - x1
    dy = y2 - y1
    length = max(abs(dx), abs(dy))

    if length == 0:
        return [{"pixels": [(x1, y1)], "color": 2, "text": "Both points are the same pixel"}]

    x_inc = dx / length
    y_inc = dy / length
    x, y = x1, y1

    for i in range(length + 1):
        px = math.floor(x + 0.5)          # round half up
        py = math.floor(y + 0.5)
        steps.append({
            "pixels": [(px, py)],
            "color": 2,
            "text": (f"Step {i}\ndx={dx}, dy={dy}, length={length}\n"
                     f"x_inc={x_inc:.3f}, y_inc={y_inc:.3f}\n"
                     f"Exact point = ({x:.2f}, {y:.2f})\nPlot pixel ({px}, {py})")
        })
        x += x_inc
        y += y_inc
    return steps
