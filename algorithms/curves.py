"""Curve drawing: Bezier (Bernstein blending), uniform cubic B-spline, Hermite.
Each step computes one point of the curve. The grid pixel is plotted and the exact curve so far is drawn as a line."""
import math

CONTROL, CURVE, TANGENT = "gray", "blue", "purple"


def px(p):
    return (math.floor(p[0] + 0.5), math.floor(p[1] + 0.5))


def _state(poly, curve, extra=()):
    shapes = [(poly, CONTROL, False)] + list(extra)
    if len(curve) > 1:
        shapes.append((list(curve), CURVE, False))
    return shapes


def bezier_curve(points, samples=20):
    n = len(points) - 1                                         # degree
    poly = [tuple(map(float, p)) for p in points]
    steps = [{"text": (f"Bezier curve of degree {n}\n{len(points)} control points define the control polygon (gray).\n"
                       "Q(t) = sum  C(n,i) (1-t)^(n-i) t^i  P_i,   0 <= t <= 1\n"
                       "The curve starts at P0, ends at P_n and is pulled towards the other points."),
              "shapes": [(poly, CONTROL, False)]}]
    curve = []
    for k in range(samples + 1):
        t = k / samples
        b = [math.comb(n, i) * (1 - t) ** (n - i) * t ** i for i in range(n + 1)]
        q = (sum(b[i] * poly[i][0] for i in range(n + 1)), sum(b[i] * poly[i][1] for i in range(n + 1)))
        curve.append(q)
        blend = ",  ".join(f"B{i}={v:.3f}" for i, v in enumerate(b))
        steps.append({"pixels": [px(q)], "color": 2, "shapes": _state(poly, curve),
                      "text": f"t = {t:.2f}\nBlending functions (sum = {sum(b):.1f}):\n{blend}\n"
                              f"Q(t) = ({q[0]:.2f}, {q[1]:.2f})\nPlot pixel {px(q)}"})
    return steps


def bspline_curve(points, samples=10):
    if len(points) < 4:
        raise ValueError("A cubic B-spline needs at least 4 control points")
    poly = [tuple(map(float, p)) for p in points]
    segs = len(poly) - 3
    steps = [{"text": (f"Uniform cubic B-spline\n{len(poly)} control points give {segs} curve segments.\n"
                       "Segment i uses P_i .. P_i+3:\n"
                       "Q(t) = 1/6 [ (1-t)^3 P_i + (3t^3-6t^2+4) P_i+1 + (-3t^3+3t^2+3t+1) P_i+2 + t^3 P_i+3 ]\n"
                       "The curve does NOT pass through the control points, but is smooth (C2) at the joins."),
              "shapes": [(poly, CONTROL, False)]}]
    curve = []
    for s in range(segs):
        p = poly[s:s + 4]
        for k in range(samples + 1):
            if s > 0 and k == 0:
                continue                                        # same point as t = 1 of the previous segment
            t = k / samples
            b = [(1 - t) ** 3 / 6, (3 * t ** 3 - 6 * t ** 2 + 4) / 6, (-3 * t ** 3 + 3 * t ** 2 + 3 * t + 1) / 6, t ** 3 / 6]
            q = (sum(b[i] * p[i][0] for i in range(4)), sum(b[i] * p[i][1] for i in range(4)))
            curve.append(q)
            blend = ",  ".join(f"B{i}={v:.3f}" for i, v in enumerate(b))
            steps.append({"pixels": [px(q)], "color": 2, "shapes": _state(poly, curve),
                          "text": f"Segment {s + 1} of {segs},  t = {t:.1f}\nUses P{s}..P{s + 3}\nBasis: {blend}\n"
                                  f"Q(t) = ({q[0]:.2f}, {q[1]:.2f})\nPlot pixel {px(q)}"})
    return steps


def hermite_curve(p1, p4, r1, r4, samples=20):
    """p1, p4 = end points, r1, r4 = tangent vectors at the end points."""
    p1, p4, r1, r4 = [tuple(map(float, v)) for v in (p1, p4, r1, r4)]
    tangents = [([p1, (p1[0] + r1[0] / 4, p1[1] + r1[1] / 4)], TANGENT, False),
                ([p4, (p4[0] + r4[0] / 4, p4[1] + r4[1] / 4)], TANGENT, False)]
    steps = [{"text": (f"Hermite curve\nEnd points P1 = {p1}, P4 = {p4}\nTangent vectors R1 = {r1}, R4 = {r4}\n"
                       "Q(t) = h1 P1 + h2 P4 + h3 R1 + h4 R4\n"
                       "h1 = 2t^3 - 3t^2 + 1,  h2 = -2t^3 + 3t^2,  h3 = t^3 - 2t^2 + t,  h4 = t^3 - t^2\n"
                       "(Tangents are drawn in purple at 1/4 of their length.)"),
              "shapes": [([p1, p4], CONTROL, False)] + tangents}]
    curve = []
    for k in range(samples + 1):
        t = k / samples
        h = [2 * t ** 3 - 3 * t ** 2 + 1, -2 * t ** 3 + 3 * t ** 2, t ** 3 - 2 * t ** 2 + t, t ** 3 - t ** 2]
        q = tuple(h[0] * p1[i] + h[1] * p4[i] + h[2] * r1[i] + h[3] * r4[i] for i in range(2))
        curve.append(q)
        blend = ",  ".join(f"h{i + 1}={v:.3f}" for i, v in enumerate(h))
        steps.append({"pixels": [px(q)], "color": 2,
                      "shapes": [([p1, p4], CONTROL, False)] + tangents + ([(list(curve), CURVE, False)] if len(curve) > 1 else []),
                      "text": f"t = {t:.2f}\n{blend}\nQ(t) = ({q[0]:.2f}, {q[1]:.2f})\nPlot pixel {px(q)}"})
    return steps