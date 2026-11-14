from ._common import PALETTE, hex_to_rgb, rgb, polygon_pixels, outline


def transparency(back, front, alpha):
    """Alpha blending of a transparent FRONT polygon over an opaque BACK polygon on a white background."""
    cb, cf, cw = hex_to_rgb(PALETTE[1]), hex_to_rgb(PALETTE[0]), (255, 255, 255)
    blend = lambda f, b: tuple(alpha * f[i] + (1 - alpha) * b[i] for i in range(3))
    pb, pf = set(polygon_pixels(back)), set(polygon_pixels(front))
    both, only_front, only_back = pb & pf, pf - pb, pb - pf
    over_white, over_back = blend(cf, cw), blend(cf, cb)
    swapped = tuple((1 - alpha) * cf[i] + alpha * cb[i] for i in range(3))
    fmt = lambda c: "(" + ", ".join(str(int(round(v))) for v in c) + ")"
    outs = [outline(back, PALETTE[1], 1), outline(front, PALETTE[0], 1)]
    steps = [{"shapes": outs, "pixels": [],
              "text": ("Transparency (alpha blending)\n"
                       f"Back polygon (blue, opaque) and front polygon (red, alpha = {alpha:g}); background is white.\n"
                       "alpha = 1 means opaque, alpha = 0 means invisible.\n"
                       "Blended colour:  C = alpha * C_front + (1 - alpha) * C_behind   (for each of R, G, B)\n"
                       f"C_front = {fmt(cf)},  C_back = {fmt(cb)},  white = (255, 255, 255)")},
             {"pixels": sorted(pb), "color": PALETTE[1], "highlight": False, "shapes": outs,
              "text": f"Step 1: draw the back polygon\nOpaque, so its pixels simply get C_back = {fmt(cb)}.\n{len(pb)} pixels."},
             {"cells": [(x, y, rgb(over_white)) for x, y in sorted(only_front)], "pixels": [], "shapes": outs,
              "text": (f"Step 2: front polygon over the white background ({len(only_front)} pixels)\n"
                       f"C = {alpha:g} * {fmt(cf)} + {1 - alpha:g} * (255, 255, 255)\nC = {fmt(over_white)}\n"
                       "The red is washed out: a transparent red over white looks light red.")}]
    if both:
        steps.append({"cells": [(x, y, rgb(over_back)) for x, y in sorted(both)], "pixels": [], "shapes": outs,
                      "text": (f"Step 3: front polygon over the back polygon ({len(both)} pixels)\n"
                               f"C = {alpha:g} * {fmt(cf)} + {1 - alpha:g} * {fmt(cb)}\nC = {fmt(over_back)}\n"
                               "The back polygon shows through the front one: a mix of red and blue.")})
    else:
        steps.append({"pixels": [], "shapes": outs, "text": "Step 3: the polygons do not overlap\nNo pixel needs to mix the two colours. Try polygons that overlap."})
    steps.append({"pixels": [], "shapes": outs,
                  "text": ("Done: transparency complete\n"
                           f"Overlap colour = {fmt(over_back)}.  If the order were swapped (blue in front with the same alpha) "
                           f"it would be {fmt(swapped)}.\nBlending depends on the ORDER, so transparent polygons are drawn "
                           "back to front after all opaque ones.")})
    return steps