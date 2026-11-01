import math


def scanline_fill(polygon):
    """Scan-line polygon fill. One step per scan line.
    Edges use the half-open rule  y_low <= y < y_high  so a vertex shared by two edges is not
    counted twice. The TOP scan line is the exception: the upper end of each edge is included
    there, so a flat top edge (or a top corner) is filled too."""
    n = len(polygon)
    ys = [p[1] for p in polygon]
    top = max(ys)
    steps = []
    outline = [(polygon, "gray", True)]

    for y in range(min(ys), top + 1):
        xs = []
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]
            if y1 == y2:
                continue                       # skip horizontal edges
            low, high = min(y1, y2), max(y1, y2)
            if low <= y < high or (y == top and high == top):
                xs.append(round(x1 + (y - y1) * (x2 - x1) / (y2 - y1), 6))
        xs.sort()

        pixels, spans = [], []
        for i in range(0, len(xs) - 1, 2):
            start, end = math.ceil(xs[i]), math.floor(xs[i + 1])
            spans.append((start, end))
            pixels += [(x, y) for x in range(start, end + 1)]

        text = (f"Scan line y = {y}" + (" (top row)" if y == top else "") + "\n"
                f"Intersections: {[round(v, 2) for v in xs]}\n"
                f"Sorted, then fill between pairs:\n{spans}")
        if y == top:
            text += "\nTop row: the upper end of each edge counts, so the top edge / corners are filled."
        steps.append({"pixels": pixels, "color": 3, "shapes": outline, "text": text})
    return steps