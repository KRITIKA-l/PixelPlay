import random
from ._common import gray, label_colour, cell_box, rect, line, normalize

X0, Y0, OX = 1, 1, 11            # the 8 x 8 input image has its lower-left pixel at (1, 1), the output at (11, 1)
VIEW = (0, 19, 0, 10)
SIZE = 8


def preset(name):
    r = random.Random(3)
    if name == "edge":
        return [[(40 if c < 4 else 200) + ((row * 5 + c * 3) % 9) - 4 for c in range(SIZE)] for row in range(SIZE)]
    if name == "gradient":
        return [[min(255, 20 + c * 28 + row * 3) for c in range(SIZE)] for row in range(SIZE)]
    if name == "dot":
        return [[220 if 3 <= row <= 5 and 3 <= c <= 5 else 60 + ((row + c) % 3) * 4 for c in range(SIZE)] for row in range(SIZE)]
    if name == "letter":                                                              # an "F": easy to see when it is turned
        rows = ["11111100", "11000000", "11000000", "11111000", "11000000", "11000000", "11000000", "11000000"]
        return [[230 if ch == "1" else 40 for ch in row] for row in rows]
    img = [[120 + r.randint(-10, 10) for _ in range(SIZE)] for _ in range(SIZE)]      # "noise": flat grey + salt & pepper
    for row, c, v in ((1, 2, 255), (2, 5, 0), (4, 1, 0), (5, 6, 255), (6, 3, 255), (3, 3, 0)):
        img[row][c] = v
    return img


IMAGES = ("noise", "edge", "gradient", "dot", "letter")

# name -> (title, 3x3 kernel, divisor, how the sum becomes a grey value, description)
KERNELS = {
    "mean": ("Mean (box) blur", [[1, 1, 1], [1, 1, 1], [1, 1, 1]], 9, "round", "every pixel becomes the average of its 3 x 3 neighbourhood: smooths noise but blurs edges"),
    "gaussian": ("Gaussian blur", [[1, 2, 1], [2, 4, 2], [1, 2, 1]], 16, "round", "weighted average: the centre counts most, so blurring is gentler than the mean filter"),
    "sharpen": ("Sharpen", [[0, -1, 0], [-1, 5, -1], [0, -1, 0]], 1, "clamp", "the centre is boosted and the neighbours subtracted, so edges stand out"),
    "sobelx": ("Sobel X (vertical edges)", [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], 1, "abs", "responds to brightness change from left to right"),
    "sobely": ("Sobel Y (horizontal edges)", [[-1, -2, -1], [0, 0, 0], [1, 2, 1]], 1, "abs", "responds to brightness change from bottom to top"),
    "laplacian": ("Laplacian (edges)", [[0, 1, 0], [1, -4, 1], [0, 1, 0]], 1, "abs", "second derivative: bright where the brightness changes sharply in any direction"),
    "median": ("Median", None, 1, "round", "the middle value of the 9 sorted neighbours: removes salt-and-pepper noise and keeps edges"),
    "negative": ("Negative (point operation)", None, 1, "round", "v' = 255 - v, each pixel is changed on its own"),
    "brighten": ("Brightness +60 (point operation)", None, 1, "round", "v' = min(255, v + 60)"),
    "threshold": ("Threshold at 128 (point operation)", None, 1, "round", "v' = 255 if v >= 128 else 0: a black-and-white image"),
}
POINT_OPS = ("negative", "brighten", "threshold")


def read_image(text):
    t = text.strip().lower()
    if t in IMAGES:
        return preset(t)
    try:
        vals = [int(float(v)) for v in t.replace(",", " ").split()]
    except ValueError:
        raise ValueError("Image: noise, edge, gradient, dot, letter - or 64 grey values (0-255)")
    if len(vals) != SIZE * SIZE or any(not 0 <= v <= 255 for v in vals):
        raise ValueError("Image: noise, edge, gradient, dot, letter - or 64 grey values (0-255)")
    return [vals[r * SIZE:(r + 1) * SIZE] for r in range(SIZE)]


def pos(img_x, row, base):
    """Image pixel (column, row-from-top) -> grid cell. Row 0 is the TOP row of the picture."""
    return base + img_x, Y0 + SIZE - 1 - row


def image_filter(name, image_text):
    name = name.strip().lower()
    if name not in KERNELS:
        raise ValueError("Filter: " + ", ".join(KERNELS))
    img = read_image(image_text)
    title, kernel, div, post, desc = KERNELS[name]
    point = name in POINT_OPS
    out = [[None] * SIZE for _ in range(SIZE)]
    labels_in = [(*pos(c, r, X0), str(img[r][c]), label_colour(img[r][c])) for r in range(SIZE) for c in range(SIZE)]
    heads = [(X0 + 3.5, Y0 + SIZE + 1.2, "INPUT", "black", 0.6), (OX + 3.5, Y0 + SIZE + 1.2, "OUTPUT", "black", 0.6)]
    cells_in = [(*pos(c, r, X0), gray(img[r][c])) for r in range(SIZE) for c in range(SIZE)]
    frame = [rect(X0, Y0, X0 + 7, Y0 + 7, "black", 2), rect(OX, Y0, OX + 7, Y0 + 7, "black", 2)]

    def out_labels():
        return [(*pos(c, r, OX), str(out[r][c]), label_colour(out[r][c])) for r in range(SIZE) for c in range(SIZE)
                if out[r][c] is not None]

    steps = [{"view": VIEW, "cells": cells_in, "pixels": [], "shapes": frame, "labels": heads + labels_in,
              "text": ("Image processing: " + title + "\n"
                       "A digital image is a grid of pixels; a grey-level image stores one number per pixel "
                       "(0 = black ... 255 = white). The 8 x 8 image on the left is the input.\n" + desc.capitalize() + ".\n" +
                       ("Point operation: each output pixel depends only on the same input pixel."
                        if point else
                        "Neighbourhood (filter) operation: slide a 3 x 3 window over the image; each output pixel is computed "
                        "from the 9 pixels under the window.") + "\n" +
                       (f"Kernel (divide the sum by {div}):\n" + "\n".join("[ " + "  ".join(f"{k:2d}" for k in row) + " ]" for row in kernel)
                        if kernel else ""))}]
    if not point:
        for r in range(SIZE):
            for c in range(SIZE):
                if r in (0, SIZE - 1) or c in (0, SIZE - 1):
                    out[r][c] = img[r][c]
        cells_b = [(*pos(c, r, OX), gray(out[r][c])) for r in range(SIZE) for c in range(SIZE) if out[r][c] is not None]
        steps.append({"cells": cells_b, "pixels": [], "shapes": frame, "labels": heads + labels_in + out_labels(),
                      "text": ("Border pixels\nThe outer ring has no complete 3 x 3 window, so it is copied unchanged.\n"
                               "(Other choices: pad with zeros, repeat the edge pixels, or shrink the output.)")})
    rng = range(SIZE) if point else range(1, SIZE - 1)
    for r in rng:
        for c in rng:
            v = img[r][c]
            x, y = pos(c, r, X0)
            ox, oy = pos(c, r, OX)
            if point:
                res = {"negative": 255 - v, "brighten": min(255, v + 60), "threshold": 255 if v >= 128 else 0}[name]
                text = (f"Pixel ({c}, {r}): input = {v}\n" +
                        {"negative": f"255 - {v} = {res}", "brighten": f"min(255, {v} + 60) = {res}",
                         "threshold": f"{v} >= 128 is {v >= 128} -> {res}"}[name])
                win = [cell_box(x, y)]
            else:
                win_vals = [[img[r + dr][c + dc] for dc in (-1, 0, 1)] for dr in (-1, 0, 1)]
                flat = [v2 for row in win_vals for v2 in row]
                if name == "median":
                    s = sorted(flat)
                    res = s[4]
                    calc = f"Sorted: {s}\nMedian = 5th value = {res}"
                else:
                    total = sum(win_vals[i][j] * kernel[i][j] for i in range(3) for j in range(3))
                    terms = " + ".join(f"{win_vals[i][j]}*{kernel[i][j]}" for i in range(3) for j in range(3))
                    calc = f"Sum = {terms} = {total}\n"
                    if div != 1:
                        calc += f"Divide by {div}: {total / div:.2f}\n"
                    val = total / div
                    if post == "abs":
                        res = min(255, abs(round(val)))
                        calc += f"Take |value| and clamp to 0..255 -> {res}"
                    elif post == "clamp":
                        res = max(0, min(255, round(val)))
                        calc += f"Clamp to 0..255 -> {res}"
                    else:
                        res = int(round(val))
                        calc += f"Round -> {res}"
                text = (f"Pixel ({c}, {r}): window centred here\n" +
                        "\n".join("  ".join(f"{q:3d}" for q in row) for row in win_vals) + "\n" + calc)
                win = [rect(x - 1, y - 1, x + 1, y + 1, "orange", 3)]
            out[r][c] = res
            steps.append({"cells": [(ox, oy, gray(res))], "pixels": [],
                          "shapes": frame + win + [cell_box(ox, oy), line((x + .5, y), (ox - .5, oy), "orange", 1, "--")],
                          "labels": heads + labels_in + out_labels(), "text": text})
    steps.append({"pixels": [], "shapes": frame, "labels": heads + labels_in + out_labels(),
                  "text": (f"Done: {title}\nOutput image complete ({SIZE * SIZE if point else (SIZE - 2) ** 2} pixels computed).\n"
                           "Compare the two images: the numbers show exactly what the operation did.")})
    return steps