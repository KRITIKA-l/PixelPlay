from collections import deque
from .bresenham import polygon_outline
from .scanline_fill import scanline_fill


def flood_fill(polygon, seed, size):
    """Flood fill (4-connected, queue).
    The whole shape (outline + inside) is ONE solid colour (blue = the OLD colour).
    Flood fill replaces every connected pixel of the old colour, so the boundary pixels
    are recoloured as well. It stops only at the background (a different colour)."""
    grid = [[0] * size for _ in range(size)]
    shape = set(polygon_outline(polygon))                      # outline pixels
    for step in scanline_fill(polygon):                        # + inside pixels
        shape.update(step["pixels"])
    for x, y in shape:
        grid[y][x] = 2
    if grid[seed[1]][seed[0]] != 2:
        raise ValueError("Seed must be inside the shape")
    old = grid[seed[1]][seed[0]]

    steps = [{"pixels": sorted(shape), "color": 2, "highlight": False,
              "text": ("Draw the solid shape\n"
                       "Outline and inside share one colour (the old colour).\n"
                       "Rule: replace a pixel only if it has the old colour.\n"
                       "The fill stops at the background.")}]
    queue = deque([seed])
    count = 0
    while queue:
        x, y = queue.popleft()
        if x < 0 or x >= size or y < 0 or y >= size:
            continue
        if grid[y][x] != old:
            continue
        grid[y][x] = 3
        count += 1
        steps.append({"pixels": [(x, y)], "color": 3,
                      "text": f"Replace old colour at ({x}, {y})\nAdd its 4 neighbours to the queue\nQueue size = {len(queue)}"})
        queue.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
    steps.append({"pixels": [], "text": (f"Done. {count} pixels recoloured.\n"
                                         "The boundary pixels had the old colour too, so flood fill DID colour the boundary.")})
    return steps