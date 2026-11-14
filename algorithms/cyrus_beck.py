def cyrus_beck(x1, y1, x2, y2, win):
    """Cyrus-Beck parametric line clipping against a rectangular window.
    P(t) = P0 + t*D, 0 <= t <= 1.  For every window edge (outward normal n, point PE on the edge):
        num = n . (P0 - PE),  den = n . D,  t = -num / den
    den < 0  -> line is entering  -> tE = max(tE, t)
    den > 0  -> line is leaving   -> tL = min(tL, t)
    Accept if tE <= tL, otherwise reject."""
    xmin, ymin, xmax, ymax = win
    window = ([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)], "red", True)
    original = ([(x1, y1), (x2, y2)], "lightgray", False)
    dx, dy = x2 - x1, y2 - y1
    edges = [("LEFT", (-1, 0), (xmin, ymin)), ("RIGHT", (1, 0), (xmax, ymin)),
             ("BOTTOM", (0, -1), (xmin, ymin)), ("TOP", (0, 1), (xmin, ymax))]
    te, tl = 0.0, 1.0

    def seg(a, b, colour):
        return ([(x1 + a * dx, y1 + a * dy), (x1 + b * dx, y1 + b * dy)], colour, False)

    steps = [{"text": (f"Cyrus-Beck: parametric form\nP(t) = P0 + t (P1 - P0),  0 <= t <= 1\n"
                       f"P0 = ({x1:g}, {y1:g}),  D = P1 - P0 = ({dx:g}, {dy:g})\n"
                       "Start with tE = 0 (entering), tL = 1 (leaving).\n"
                       "For each edge: num = n.(P0 - PE),  den = n.D,  t = -num/den"),
              "shapes": [window, seg(0, 1, "blue")]}]
    if dx == 0 and dy == 0:
        inside = xmin <= x1 <= xmax and ymin <= y1 <= ymax
        steps.append({"text": ("The line is a single point\n" + ("Point inside -> ACCEPT" if inside else "Point outside -> REJECT")),
                      "shapes": [window, ([(x1, y1)], "green" if inside else "gray", False)]})
        return steps

    for name, (nx, ny), (ex, ey) in edges:
        num = nx * (x1 - ex) + ny * (y1 - ey)
        den = nx * dx + ny * dy
        head = f"Edge {name}: n = ({nx}, {ny})\nnum = n.(P0 - PE) = {num:g},  den = n.D = {den:g}\n"
        if den == 0:
            if num > 0:
                steps.append({"text": head + "den = 0: the line is parallel to this edge and OUTSIDE it\n-> REJECT",
                              "shapes": [window, original]})
                return steps
            steps.append({"text": head + "den = 0: parallel to this edge but inside it\n-> this edge gives no limit",
                          "shapes": [window, original, seg(te, tl, "blue")]})
            continue
        t = -num / den
        if den < 0:
            te = max(te, t)
            kind = f"den < 0 -> ENTERING\nt = {t:.3f},  tE = max(tE, t) = {te:.3f}"
        else:
            tl = min(tl, t)
            kind = f"den > 0 -> LEAVING\nt = {t:.3f},  tL = min(tL, t) = {tl:.3f}"
        steps.append({"text": head + kind + f"\nCurrent interval: tE = {te:.3f}, tL = {tl:.3f}",
                      "shapes": [window, original, seg(te, tl, "blue") if te <= tl else seg(0, 0, "blue")]})

    if te > tl:
        steps.append({"text": f"tE = {te:.3f} > tL = {tl:.3f}\n-> the line is completely OUTSIDE\n-> REJECT",
                      "shapes": [window, original]})
    else:
        a, b = (x1 + te * dx, y1 + te * dy), (x1 + tl * dx, y1 + tl * dy)
        steps.append({"text": (f"tE = {te:.3f} <= tL = {tl:.3f}\n-> ACCEPT the part between them\n"
                               f"Clipped line: ({a[0]:.2f}, {a[1]:.2f}) to ({b[0]:.2f}, {b[1]:.2f})"),
                      "shapes": [window, original, seg(te, tl, "green")]})
    return steps