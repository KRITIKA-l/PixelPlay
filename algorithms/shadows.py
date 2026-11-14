from ._common import outline, line, cell_box

GROUND, SHADOW = "#c8c8c8", "#555555"


def shadows(poly, light, size=30):
    """Shadow of an object on the ground (y = 0) cast by a point light, drawn in side view.
    Every vertex P is projected from the light L onto the ground: the ray L -> P is extended until y = 0."""
    lx, ly = light
    if any(p[1] >= ly for p in poly):
        raise ValueError("The light must be higher than every point of the object (light y > object y)")
    if any(p[1] < 0 for p in poly):
        raise ValueError("The object must be on or above the ground (y >= 0)")
    ground = [(x, 0, GROUND) for x in range(size)]
    obj = outline(poly, "blue", 2)
    lpix = [(int(round(lx)), int(round(ly)))]
    hits = [lx + (p[0] - lx) * ly / (ly - p[1]) for p in poly]
    rays = [line((lx, ly), (h, 0), "gold", 1, "--") for h in hits]
    steps = [{"cells": ground, "pixels": lpix, "color": 5, "highlight": False, "shapes": [obj],
              "text": ("Shadow projection (side view)\n"
                       f"Point light L = ({lx:g}, {ly:g}) (red), object in blue, ground = the grey line y = 0.\n"
                       "A point P is in shadow where the ray from the light through P hits the ground.\n"
                       "Ray: P' = L + t (P - L); it reaches y = 0 when t = Ly / (Ly - Py), so\n"
                       "x' = Lx + (Px - Lx) * Ly / (Ly - Py)\n"
                       "Project every vertex; the shadow is the stretch between the left-most and right-most x'.")}]
    for k, p in enumerate(poly):
        steps.append({"pixels": [], "shapes": [obj] + rays[:k] + [line((lx, ly), (hits[k], 0), "orange", 3)],
                      "text": (f"Vertex {k + 1}: P = ({p[0]}, {p[1]})\nt = Ly / (Ly - Py) = {ly:g} / ({ly:g} - {p[1]}) = {ly / (ly - p[1]):.3f}\n"
                               f"x' = {lx:g} + ({p[0]} - {lx:g}) * {ly / (ly - p[1]):.3f} = {hits[k]:.2f}\n"
                               f"Shadow point on the ground: ({hits[k]:.2f}, 0)")})
    lo, hi = min(hits), max(hits)
    a, b = int(round(lo)), int(round(hi))
    left = hits.index(lo)
    right = hits.index(hi)
    cells = [(x, 0, SHADOW) for x in range(max(0, a), min(size - 1, b) + 1)]
    steps.append({"cells": cells, "pixels": [], "shapes": [obj] + rays +
                  [line((lx, ly), (lo, 0), "red", 2), line((lx, ly), (hi, 0), "red", 2)],
                  "text": (f"Shadow on the ground\nLeft-most shadow point x' = {lo:.2f} (vertex {left + 1}), right-most x' = {hi:.2f} (vertex {right + 1}).\n"
                           f"Ground pixels x = {a} .. {b} are dark.\n"
                           "The two red rays are the edges of the shadow volume: everything between them behind the object is in shadow." +
                           ("\n(Part of the shadow lies outside the grid.)" if a < 0 or b >= size else ""))})
    steps.append({"pixels": [], "shapes": [obj] + rays,
                  "text": (f"Done: shadow length = {hi - lo:.2f} pixels\n"
                           "A light closer to the object makes a longer, wider shadow; a light far away "
                           "(like the sun) makes parallel rays and a shadow the same size as the object.\n"
                           "Other methods: shadow volumes and shadow maps (render the scene from the light and store depths).")})
    return steps