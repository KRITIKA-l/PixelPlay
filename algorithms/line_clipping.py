LEFT, RIGHT, BOTTOM, TOP = 1, 2, 4, 8


def region_code(x, y, win):
    xmin, ymin, xmax, ymax = win
    code = 0
    if x < xmin: code |= LEFT
    elif x > xmax: code |= RIGHT
    if y < ymin: code |= BOTTOM
    elif y > ymax: code |= TOP
    return code


def cohen_sutherland(x1, y1, x2, y2, win):
    """Cohen-Sutherland line clipping. Returns a list of steps."""
    xmin, ymin, xmax, ymax = win
    window = ([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)], "red", True)
    c1, c2 = region_code(x1, y1, win), region_code(x2, y2, win)
    original = ([(x1, y1), (x2, y2)], "lightgray", False)
    steps = [{"text": f"Original line\nP1=({x1},{y1}) code={c1:04b}\nP2=({x2},{y2}) code={c2:04b}\n(bits: Top Bottom Right Left)",
              "shapes": [window, ([(x1, y1), (x2, y2)], "blue", False)]}]

    while True:
        line = ([(x1, y1), (x2, y2)], "blue", False)
        if c1 == 0 and c2 == 0:
            steps.append({"text": "Both codes are 0000\n-> line is completely INSIDE\n-> ACCEPT",
                          "shapes": [window, original, ([(x1, y1), (x2, y2)], "green", False)]})
            break
        if c1 & c2:
            steps.append({"text": f"code1 AND code2 = {c1 & c2:04b} (not 0)\n-> line is completely OUTSIDE\n-> REJECT",
                          "shapes": [window, original]})
            break
        out = c1 if c1 else c2
        if out & TOP:
            x, y = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1), ymax
            side = "TOP"
        elif out & BOTTOM:
            x, y = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1), ymin
            side = "BOTTOM"
        elif out & RIGHT:
            x, y = xmax, y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            side = "RIGHT"
        else:
            x, y = xmin, y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            side = "LEFT"
        if out == c1:
            x1, y1 = x, y
            c1 = region_code(x1, y1, win)
        else:
            x2, y2 = x, y
            c2 = region_code(x2, y2, win)
        steps.append({"text": f"Outside point clipped against {side}\nNew point = ({x:.2f}, {y:.2f})\n"
                              f"code1={c1:04b}, code2={c2:04b}",
                      "shapes": [window, original, ([(x1, y1), (x2, y2)], "blue", False)]})
    return steps
