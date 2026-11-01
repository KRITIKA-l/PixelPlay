def sutherland_hodgman(polygon, win):
    """Sutherland-Hodgman polygon clipping. One step per window edge."""
    xmin, ymin, xmax, ymax = win
    window = ([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)], "red", True)
    original = (polygon, "lightgray", True)

    def inside(p, edge):
        return {"LEFT": p[0] >= xmin, "RIGHT": p[0] <= xmax,
                "BOTTOM": p[1] >= ymin, "TOP": p[1] <= ymax}[edge]

    def intersect(s, e, edge):
        if edge in ("LEFT", "RIGHT"):
            x = xmin if edge == "LEFT" else xmax
            return (x, s[1] + (e[1] - s[1]) * (x - s[0]) / (e[0] - s[0]))
        y = ymin if edge == "BOTTOM" else ymax
        return (s[0] + (e[0] - s[0]) * (y - s[1]) / (e[1] - s[1]), y)

    steps = [{"text": "Original polygon and clip window.\nClip against LEFT, RIGHT, BOTTOM, TOP\none after another.",
              "shapes": [window, (polygon, "blue", True)]}]
    current = list(polygon)
    for edge in ("LEFT", "RIGHT", "BOTTOM", "TOP"):
        inp, current = current, []
        if not inp:
            break
        s = inp[-1]
        for e in inp:
            if inside(e, edge):
                if not inside(s, edge):
                    current.append(intersect(s, e, edge))     # out -> in
                current.append(e)
            elif inside(s, edge):
                current.append(intersect(s, e, edge))         # in -> out
            s = e
        steps.append({"text": f"After clipping against {edge}\nInput vertices: {len(inp)}\nOutput vertices: {len(current)}\n"
                              "Rules per edge S->E:\n in->in : keep E\n in->out: keep intersection\n out->in: intersection, E\n out->out: nothing",
                      "shapes": [window, original, (current, "green", True)]})
    return steps
