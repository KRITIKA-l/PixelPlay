from collections import deque
from .bresenham import polygon_outline


def _inside(polygon, seed):
    """Even-odd point-in-polygon test."""
    x, y = seed
    inside = False
    n = len(polygon)
    for i in range(n):
        (x1, y1), (x2, y2) = polygon[i], polygon[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def boundary_fill(polygon, seed, size):
    """Boundary fill (4-connected, queue).
    The outline has ONE boundary colour (black). The fill stops when it meets that colour,
    so the boundary itself is NEVER recoloured - only the inside is filled.
    Every time the fill hits a boundary pixel it is shown as its own step."""
    grid = [[0] * size for _ in range(size)]
    boundary = set(polygon_outline(polygon))
    for x, y in boundary:
        grid[y][x] = 1
    if grid[seed[1]][seed[0]] == 1:
        raise ValueError("Seed is on the boundary - choose a point inside the polygon")
    if not _inside(polygon, seed):
        raise ValueError("Seed is outside the polygon - the fill would leak over the whole canvas. Choose a point inside.")

    steps = [{"pixels": sorted(boundary), "color": 1, "highlight": False,
              "text": ("Draw the polygon outline\n"
                       "Rule: fill a pixel only if it is not boundary and not already filled.\n"
                       "The fill stops when it reaches the boundary.\n"
                       "The fill spreads in all 4 directions at once (right, left, up, down), growing outwards from the seed.\n"
                       "Each boundary hit is shown as a step.")}]
    stack = deque([(seed[0], seed[1], None)])   # (x, y, pixel it was reached from) - a queue, so it spreads in a wave
    hit = set()                             # boundary pixels already reported
    count = 0
    skipped = 0                             # already-filled pixels met again
    while stack:
        x, y, src = stack.popleft()
        if x < 0 or x >= size or y < 0 or y >= size:
            continue
        if grid[y][x] == 1:                 # boundary colour -> do not fill, do not spread
            if (x, y) not in hit:
                hit.add((x, y))
                steps.append({"pixels": [(x, y)], "color": 1,
                              "text": (f"Boundary hit at ({x}, {y})\n"
                                       f"Reached from ({src[0]}, {src[1]})\n"
                                       "Pixel has the boundary colour -> do NOT fill it\n"
                                       "Its neighbours are not added\n"
                                       f"Queue size = {len(stack)}")})
            continue
        if grid[y][x] == 3:                 # already filled
            skipped += 1
            continue
        grid[y][x] = 3
        count += 1
        steps.append({"pixels": [(x, y)], "color": 3,
                      "text": f"Fill pixel ({x}, {y})\nAdd its 4 neighbours (right, left, up, down) to the queue\nQueue size = {len(stack)}\n"
                              f"Already-filled neighbours skipped so far = {skipped}"})
        stack.extend([(x + 1, y, (x, y)), (x - 1, y, (x, y)), (x, y + 1, (x, y)), (x, y - 1, (x, y))])
    steps.append({"pixels": [], "text": (f"Done. {count} pixels filled.\n"
                                         f"{len(hit)} boundary pixels were hit and left unchanged.\n"
                                         f"{skipped} already-filled neighbours were skipped.\n"
                                         "The boundary stays black: boundary fill does NOT colour the boundary.")})
    return steps