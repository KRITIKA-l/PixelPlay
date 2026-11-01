"""
Computer Graphics Algorithm Visualizer  (Python + Matplotlib + NumPy)

Run:  python main.py
Two tabs:
  Visualizer - choose an algorithm, enter the input (or keep the default), click Run,
               then use Next / Prev / Play to see the algorithm step by step.
  Overview   - one card per algorithm; click a card to read that algorithm written out step by step
               (the detail page also has a button to open it in the Visualizer).
"""
import re
import textwrap

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button, RadioButtons, Slider, TextBox

from algorithms import (dda_line, bresenham_line, midpoint_circle, boundary_fill, flood_fill,
                        scanline_fill, cohen_sutherland, sutherland_hodgman)

N = 30   # the canvas is an N x N pixel grid
# colours: 0 empty, 1 boundary, 2 line/circle pixel, 3 filled pixel, 4 current step
CMAP = ListedColormap(["white", "black", "royalblue", "limegreen", "orange"])


# ---------- reading the user's input ----------
def numbers(text, count):
    try:
        values = [float(t) for t in text.replace(",", " ").split()]
    except ValueError:
        raise ValueError("Please enter numbers only, separated by commas")
    if len(values) != count:
        raise ValueError(f"Expected {count} numbers, got {len(values)}")
    return values


def points(text):
    pts = [tuple(numbers(p, 2)) for p in text.split(";") if p.strip()]
    if len(pts) < 3:
        raise ValueError("Enter at least 3 points like: x,y; x,y; x,y")
    return pts


def to_pixels(values):
    for v in values:
        if v != int(v) or not 0 <= v < N:
            raise ValueError(f"Pixel coordinates must be integers from 0 to {N - 1}")
    return [int(v) for v in values]


def in_canvas(values):
    for v in values:
        if not 0 <= v < N:
            raise ValueError(f"Coordinates must be between 0 and {N - 1}")
    return values


# ---------- one entry per algorithm: labels, default inputs, function ----------
ALGORITHMS = {
    "DDA": ("Line: x1,y1,x2,y2", "3,2,25,13", "", "",
            lambda a, b: dda_line(*to_pixels(numbers(a, 4)))),
    "Bresenham": ("Line: x1,y1,x2,y2", "3,2,25,13", "", "",
                  lambda a, b: bresenham_line(*to_pixels(numbers(a, 4)))),
    "Midpoint Circle": ("Circle: xc,yc,r", "15,15,10", "", "",
                        lambda a, b: circle(a)),
    "Boundary Fill": ("Polygon: x,y; x,y; ...", "5,5;22,5;22,16;14,24;5,16", "Seed: x,y", "12,10",
                      lambda a, b: boundary_fill([tuple(to_pixels(p)) for p in points(a)],
                                                 tuple(to_pixels(numbers(b, 2))), N)),
    "Flood Fill": ("Polygon: x,y; x,y; ...", "5,5;22,5;22,16;14,24;5,16", "Seed: x,y", "12,10",
                   lambda a, b: flood_fill([tuple(to_pixels(p)) for p in points(a)],
                                           tuple(to_pixels(numbers(b, 2))), N)),
    "Scanline Fill": ("Polygon: x,y; x,y; ...", "4,4;24,4;24,24;14,12;4,24", "", "",
                      lambda a, b: scanline_fill([tuple(to_pixels(p)) for p in points(a)])),
    "Line Clipping": ("Line: x1,y1,x2,y2", "2,2,27,20", "Window: xmin,ymin,xmax,ymax", "8,8,22,20",
                      lambda a, b: cohen_sutherland(*in_canvas(numbers(a, 4)), window(b))),
    "Polygon Clipping": ("Polygon: x,y; x,y; ...", "5,5;25,8;20,26;10,22;2,14", "Window: xmin,ymin,xmax,ymax", "8,8,22,20",
                         lambda a, b: sutherland_hodgman(points(a), window(b))),
}

# ---------- text shown on each algorithm's page and on its Overview card ----------
# name -> (category, one-line description, key idea)
ALGO_INFO = {
    "DDA": ("Line drawing",
            "Draws a line by stepping along the longer axis in equal floating-point increments.",
            "Each step adds x_inc and y_inc to the exact point, then rounds it to the nearest pixel."),
    "Bresenham": ("Line drawing",
                  "Draws a line using only integer arithmetic and an error term to pick the next pixel.",
                  "The error value decides at every step whether to move in x, in y, or in both."),
    "Midpoint Circle": ("Circle drawing",
                        "Draws a circle by plotting one octant and mirroring it into the other seven.",
                        "A decision parameter p tells whether the midpoint is inside or outside the circle."),
    "Boundary Fill": ("Region filling",
                      "Fills a region from a seed pixel and stops at pixels of the boundary colour.",
                      "Spreads to the 4 neighbours using a stack; the boundary itself is never recoloured."),
    "Flood Fill": ("Region filling",
                   "Replaces every connected pixel of the old colour, starting from a seed pixel.",
                   "Spreads using a queue; the old colour is the test, so the outline is recoloured too."),
    "Scanline Fill": ("Region filling",
                      "Fills a polygon row by row using where each scan line crosses the polygon edges.",
                      "Sort the x intersections of a line, then fill between each pair of them."),
    "Line Clipping": ("Clipping",
                      "Cohen-Sutherland: cuts a line to a rectangular window using 4-bit region codes.",
                      "Accept if both codes are 0, reject if they share a bit, otherwise clip at an edge."),
    "Polygon Clipping": ("Clipping",
                         "Sutherland-Hodgman: clips a polygon against the window one edge at a time.",
                         "Each window edge turns the vertex list into a new one using four in/out rules."),
}
# ---------- the algorithm written out properly (shown when a card is clicked) ----------
# name -> list of (indent level, text)
ALGO_DOC = {
    "DDA": [
        (0, "1.  dx = x2 - x1,   dy = y2 - y1"),
        (0, "2.  length = max(|dx|, |dy|)"),
        (0, "3.  x_inc = dx / length,   y_inc = dy / length"),
        (0, "4.  x = x1,   y = y1"),
        (0, "5.  Repeat (length + 1) times:"),
        (1, "a.  Plot the pixel (round(x), round(y))"),
        (1, "b.  x = x + x_inc,   y = y + y_inc"),
    ],
    "Bresenham": [
        (0, "1.  dx = |x2 - x1|,   dy = |y2 - y1|"),
        (0, "2.  sx = 1 if x1 < x2 else -1,   sy = 1 if y1 < y2 else -1"),
        (0, "3.  x = x1,   y = y1,   error = dx - dy"),
        (0, "4.  Repeat:"),
        (1, "a.  Plot the pixel (x, y)"),
        (1, "b.  If (x, y) = (x2, y2), stop"),
        (1, "c.  e2 = 2 * error"),
        (1, "d.  If e2 > -dy:   error = error - dy,   x = x + sx"),
        (1, "e.  If e2 < dx:   error = error + dx,   y = y + sy"),
    ],
    "Midpoint Circle": [
        (0, "1.  x = 0,   y = r,   p = 1 - r"),
        (0, "2.  While x <= y:"),
        (1, "a.  Plot the 8 symmetric points (xc +/- x, yc +/- y) and (xc +/- y, yc +/- x)"),
        (1, "b.  x = x + 1"),
        (1, "c.  If p < 0:   p = p + 2x + 1"),
        (1, "d.  Else:   y = y - 1,   p = p + 2(x - y) + 1"),
    ],
    "Boundary Fill": [
        (0, "1.  Draw the polygon outline in the boundary colour"),
        (0, "2.  Push the seed pixel on a stack"),
        (0, "3.  While the stack is not empty:"),
        (1, "a.  Pop a pixel (x, y)"),
        (1, "b.  If it is the boundary colour or already filled: skip it (do not spread)"),
        (1, "c.  Otherwise: fill it with the new colour"),
        (1, "d.  Push its 4 neighbours (right, left, up, down)"),
        (0, "4.  The boundary pixels are never recoloured"),
    ],
    "Flood Fill": [
        (0, "1.  Draw the shape in the old colour"),
        (0, "2.  old = colour of the seed pixel;  add the seed to a queue"),
        (0, "3.  While the queue is not empty:"),
        (1, "a.  Remove a pixel (x, y)"),
        (1, "b.  If its colour is not old: skip it (do not spread)"),
        (1, "c.  Otherwise: replace it with the new colour"),
        (1, "d.  Add its 4 neighbours (right, left, up, down)"),
        (0, "4.  The outline has the old colour too, so it is recoloured as well"),
    ],
    "Scanline Fill": [
        (0, "1.  For every scan line y from y_min up to y_max:"),
        (1, "a.  For each non-horizontal edge crossing y (its upper end counts only on the top row):"),
        (2, "x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)"),
        (1, "b.  Sort the x intersections"),
        (1, "c.  Take them in pairs (x_i, x_i+1)"),
        (1, "d.  Fill the pixels from ceil(x_i) to floor(x_i+1)"),
    ],
    "Line Clipping": [
        (0, "1.  Give each end point a 4-bit region code (Top, Bottom, Right, Left)"),
        (0, "2.  Repeat:"),
        (1, "a.  If both codes are 0000:   ACCEPT the line"),
        (1, "b.  If code1 AND code2 is not 0:   REJECT the line"),
        (1, "c.  Otherwise pick an end point that is outside the window"),
        (1, "d.  Move it to the window edge it crosses (TOP, BOTTOM, RIGHT, LEFT), e.g."),
        (2, "TOP:   x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1),   y = ymax"),
        (1, "e.  Recompute its code and repeat"),
    ],
    "Polygon Clipping": [
        (0, "1.  For each window edge in turn (LEFT, RIGHT, BOTTOM, TOP):"),
        (1, "a.  Go through every polygon edge S -> E and build a new vertex list:"),
        (2, "S in,  E in:     output E"),
        (2, "S in,  E out:    output the intersection"),
        (2, "S out, E in:     output the intersection, then E"),
        (2, "S out, E out:    output nothing"),
        (1, "b.  The new list is the input for the next window edge"),
        (0, "2.  After the last edge, the list is the clipped polygon"),
    ],
}

# name -> (time / cost, use it when)
ALGO_EXTRA = {
    "DDA": ("O(n), n = max(|dx|, |dy|). One float add and one rounding per pixel.",
            "Learning or simple tools. Slower than Bresenham because of float maths."),
    "Bresenham": ("O(n), n = max(|dx|, |dy|). Integer additions only, no rounding.",
                  "Almost always: fast, exact and no float error builds up."),
    "Midpoint Circle": ("O(r). Integer only; one octant is computed, 8 pixels per step.",
                        "Drawing circles quickly. The same idea works for ellipses."),
    "Boundary Fill": ("O(P), P = pixels in the region. Needs a one-colour boundary.",
                      "The region is outlined in a single colour (paint tools)."),
    "Flood Fill": ("O(P), P = pixels in the region. Needs a one-colour region.",
                   "The region has one colour but a mixed edge (paint-bucket tool)."),
    "Scanline Fill": ("O(H x E): H scan lines, E edges. No seed point, no stack or queue.",
                      "Filling polygons fast, e.g. in renderers."),
    "Line Clipping": ("At most 4 clip steps per line. Cheap accept / reject tests first.",
                      "Many lines, most of them fully inside or fully outside."),
    "Polygon Clipping": ("O(4 x V): every vertex is tested against the 4 window edges.",
                         "Clipping polygons to a rectangle (concave shapes may keep extra edges)."),
}

CATEGORY_COLORS = {"Line drawing": "#3b6fd4", "Circle drawing": "#7e4fc2",
                   "Region filling": "#2f9a45", "Clipping": "#d9702a"}

# ---------- legend entries: (text, colour, "box" for a pixel / "line" for a drawn line) ----------
LEGEND = [("Boundary / outline", "black", "box"), ("Line / circle / shape pixel", "royalblue", "box"),
          ("Filled pixel", "limegreen", "box"), ("Current step", "orange", "box"),
          ("Clipping window", "red", "line")]

TAB_ON, TAB_OFF = "#bcd4ff", "0.85"


def result_summary(algo, steps):
    """(text, colour) for the final step: Accepted / Rejected, 'Filled X pixels' or 'X pixels plotted'."""
    last = steps[-1]["text"]
    if algo == "Line Clipping":
        return ("Accepted", "darkgreen") if "ACCEPT" in last else ("Rejected", "red")
    if algo == "Polygon Clipping":
        m = re.search(r"Output vertices: (\d+)", last)
        n = int(m.group(1)) if m else 0
        return (f"Accepted ({n} vertices)", "darkgreen") if n else ("Rejected", "red")
    if algo in ("Boundary Fill", "Flood Fill", "Scanline Fill"):
        n = len({p for st in steps if st.get("color") == 3 for p in st.get("pixels", [])})
        return f"Filled {n} {'pixel' if n == 1 else 'pixels'}", "darkgreen"
    n = len({p for st in steps for p in st.get("pixels", [])})
    return f"{n} {'pixel' if n == 1 else 'pixels'} plotted", "darkgreen"


def circle(text):
    xc, yc, r = to_pixels(numbers(text, 3))
    if xc - r < 0 or yc - r < 0 or xc + r >= N or yc + r >= N:
        raise ValueError("The circle must fit inside the grid")
    return midpoint_circle(xc, yc, r)


def window(text):
    xmin, ymin, xmax, ymax = in_canvas(numbers(text, 4))
    if xmin >= xmax or ymin >= ymax:
        raise ValueError("Window needs xmin < xmax and ymin < ymax")
    return xmin, ymin, xmax, ymax


# ---------- the program window ----------
class App:
    def __init__(self):
        self.steps, self.i, self.timer = [], 0, None
        self.algo, self.error, self.tab, self.scale = "DDA", None, "Visualizer", 1.0
        self.cards, self.hover, self.detail_name = [], None, None

        self.fig = plt.figure(figsize=(11.5, 6.6))
        self.title = self.fig.suptitle("Computer Graphics Algorithm Visualizer", fontsize=14, fontweight="bold", y=0.985)
        try:
            self.fig.canvas.manager.set_window_title("Computer Graphics Algorithm Visualizer")
        except Exception:
            pass

        # --- tab bar ---
        self.tab_buttons = {}
        for k, name in enumerate(["Visualizer", "Overview"]):
            b = Button(self.fig.add_axes([0.01 + k * 0.10, 0.90, 0.095, 0.045]), name)
            b.on_clicked(lambda e, n=name: self.set_tab(n))
            self.tab_buttons[name] = b

        # --- visualizer widgets ---
        self.ax = self.fig.add_axes([0.22, 0.20, 0.52, 0.66])
        self.info = self.fig.add_axes([0.76, 0.33, 0.23, 0.53])     # step details panel
        self.info.axis("off")
        self.legend = self.fig.add_axes([0.76, 0.16, 0.23, 0.15])   # colour legend
        self.draw_legend()

        self.radio_ax = self.fig.add_axes([0.01, 0.40, 0.18, 0.46])
        self.radio_ax.set_title("Algorithm", fontweight="bold")
        self.radio = RadioButtons(self.radio_ax, list(ALGORITHMS))
        self.radio.on_clicked(self.choose)

        self.box1 = TextBox(self.fig.add_axes([0.22, 0.10, 0.28, 0.045]), "")
        self.box2 = TextBox(self.fig.add_axes([0.56, 0.10, 0.20, 0.045]), "")

        self.box1.on_submit(lambda text: self.run())      # Enter key runs the algorithm
        self.box2.on_submit(lambda text: self.run())
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)

        names = ["Run", "|< Reset", "< Prev", "Next >", "Play", "Show Result"]
        self.buttons = {}
        for k, name in enumerate(names):
            b = Button(self.fig.add_axes([0.22 + k * 0.09, 0.02, 0.08, 0.05]), name)
            self.buttons[name] = b
        self.buttons["Run"].on_clicked(lambda e: self.run())
        self.buttons["|< Reset"].on_clicked(lambda e: self.show(0))
        self.buttons["< Prev"].on_clicked(lambda e: self.show(self.i - 1))
        self.buttons["Next >"].on_clicked(lambda e: self.show(self.i + 1))
        self.buttons["Play"].on_clicked(lambda e: self.play())
        self.buttons["Show Result"].on_clicked(lambda e: self.show_result())

        # speed slider: 1 = slow, 10 = fast
        self.speed = Slider(self.fig.add_axes([0.86, 0.035, 0.11, 0.03]), "Speed ", 1, 10, valinit=4, valstep=1)
        self.speed.on_changed(self.set_speed)

        # axes that belong to the Visualizer tab (hidden while the Overview tab is open)
        self.visualizer_axes = [self.ax, self.info, self.legend, self.radio_ax,
                                self.box1.ax, self.box2.ax, self.speed.ax] + \
                               [b.ax for b in self.buttons.values()]

        # widgets of the Visualizer tab: switched off while another tab is open, so that they
        # cannot redraw themselves (hover / blitting) on top of the Overview
        self.visualizer_widgets = [self.radio, self.box1, self.box2, self.speed] + list(self.buttons.values())

        # --- overview widgets: an opaque white page that covers the whole area under the tab bar ---
        self.over = self.new_page()
        self.draw_overview()

        # --- detail page (opened when a card is clicked) ---
        self.detail = self.new_page()
        self.back = Button(self.fig.add_axes([0.22, 0.90, 0.09, 0.045]), "< Back")
        self.open_btn = Button(self.fig.add_axes([0.32, 0.90, 0.15, 0.045]), "Open in Visualizer")
        self.back.on_clicked(lambda e: self.show_grid())
        self.open_btn.on_clicked(lambda e: self.open_algo(self.detail_name))
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_move)

        self.timer = self.fig.canvas.new_timer(interval=self.delay())
        self.timer.add_callback(self.tick)
        self.choose("DDA")
        self.set_tab("Visualizer")
        self.fig.canvas.mpl_connect("resize_event", self.rescale)

    # ---------- tabs ----------
    def new_page(self):
        """An axes on top of everything below the tab bar, with an opaque white background."""
        page = self.fig.add_axes([0, 0, 1, 0.89])
        page.set_zorder(10)
        page.set_xlim(0, 1)
        page.set_ylim(0, 1)
        page.axis("off")
        page.add_patch(Rectangle((0, 0), 1, 1, transform=page.transAxes, facecolor="white",
                                 edgecolor="none", zorder=0))
        return page

    def clear_page(self, page):
        """Remove everything drawn on an overview / detail page and put the white backdrop back."""
        for artist in list(page.patches) + list(page.texts) + list(page.lines):
            artist.remove()
        page.add_patch(Rectangle((0, 0), 1, 1, transform=page.transAxes, facecolor="white",
                                 edgecolor="none", zorder=0))

    def set_tab(self, tab):
        self.tab = tab
        self.detail_name = None
        if tab != "Visualizer":
            self.stop()
        for name, b in self.tab_buttons.items():
            colour = TAB_ON if name == tab else TAB_OFF
            b.color = b.hovercolor = colour
            b.ax.set_facecolor(colour)
        self.refresh()

    def refresh(self):
        """Show only the page that belongs to the current tab / view."""
        vis = self.tab == "Visualizer"
        detail = self.tab == "Overview" and self.detail_name is not None
        grid = self.tab == "Overview" and not detail
        for a in self.visualizer_axes:
            a.set_visible(vis)
        for w in self.visualizer_widgets:
            w.active = vis
        self.over.set_visible(grid)
        self.detail.set_visible(detail)
        for b in (self.back, self.open_btn):
            b.ax.set_visible(detail)
            b.active = detail
        self.fig.canvas.draw_idle()

    def show_detail(self, name):
        self.detail_name = name
        self.draw_detail(name)
        self.refresh()

    def show_grid(self):
        self.detail_name = None
        self.refresh()

    def open_algo(self, name):
        """Select the algorithm in the radio list and show it in the Visualizer."""
        self.radio.eventson = False               # we call choose() ourselves
        self.radio.set_active(list(ALGORITHMS).index(name))
        self.radio.eventson = True
        self.choose(name)
        self.set_tab("Visualizer")

    def draw_detail(self, name):
        """The card page: the algorithm written out step by step."""
        d = self.detail
        self.clear_page(d)
        category, line, idea = ALGO_INFO[name]
        colour = CATEGORY_COLORS[category]
        x0, y0, w, h = 0.10, 0.03, 0.80, 0.94
        d.add_patch(Rectangle((x0, y0), w, h, facecolor="#f8f9fb", edgecolor="#b5bcc7", linewidth=1.2))
        d.add_patch(Rectangle((x0, y0 + h - 0.12), w, 0.12, facecolor=colour, edgecolor=colour))
        d.text(x0 + 0.025, y0 + h - 0.06, name, color="white", fontsize=self.fs(20), fontweight="bold", va="center")
        d.text(x0 + w - 0.025, y0 + h - 0.06, category.upper(), color="white", fontsize=self.fs(10),
               fontweight="bold", ha="right", va="center")
        d.text(x0 + 0.025, y0 + h - 0.17, line, fontsize=self.fs(11.5), style="italic", va="center", color="#333333")
        d.text(x0 + 0.025, y0 + h - 0.235, "ALGORITHM", color=colour, fontsize=self.fs(10), fontweight="bold", va="center")
        d.plot([x0 + 0.025, x0 + w - 0.025], [y0 + h - 0.26] * 2, color="#b5bcc7", linewidth=0.8)
        y = y0 + h - 0.31
        for level, text in ALGO_DOC[name]:
            d.text(x0 + 0.03 + level * 0.035, y, text, fontsize=self.fs(11.5), va="center", color="#222222")
            y -= 0.044
        extra = ALGO_EXTRA[name]
        for k, (label, text) in enumerate([("KEY IDEA", idea), ("TIME / COST", extra[0]), ("USE IT WHEN", extra[1])]):
            cx = x0 + 0.025 + k * 0.26
            d.text(cx, y0 + 0.235, label, color=colour, fontsize=self.fs(9), fontweight="bold", va="center")
            d.text(cx, y0 + 0.205, textwrap.fill(text, 32), fontsize=self.fs(10), va="top", linespacing=1.35, color="#333333")
        d.set_xlim(0, 1)
        d.set_ylim(0, 1)

    # ---------- overview cards ----------
    def draw_overview(self):
        self.clear_page(self.over)
        self.cards, self.hover = [], None
        cols, rows, gx, gy = 4, 2, 0.014, 0.03
        w = (1 - (cols + 1) * gx) / cols
        h = (1 - (rows + 1) * gy) / rows
        for k, name in enumerate(ALGORITHMS):
            r, c = divmod(k, cols)
            x = gx + c * (w + gx)
            y = 1 - gy - (r + 1) * h - r * gy
            category, line, idea = ALGO_INFO[name]
            colour = CATEGORY_COLORS[category]
            body = Rectangle((x, y), w, h, facecolor="#f8f9fb", edgecolor="#b5bcc7", linewidth=1.2)
            self.over.add_patch(body)
            self.over.add_patch(Rectangle((x, y + h * 0.80), w, h * 0.20, facecolor=colour, edgecolor=colour))
            self.over.text(x + w / 2, y + h * 0.90, name, color="white", fontsize=self.fs(12.5),
                           fontweight="bold", ha="center", va="center")
            self.over.text(x + 0.012, y + h * 0.745, category.upper(), color=colour, fontsize=self.fs(8),
                           fontweight="bold", va="center")
            self.over.text(x + 0.012, y + h * 0.69, textwrap.fill(line, 33), fontsize=self.fs(9.5), va="top", linespacing=1.35)
            self.over.text(x + 0.012, y + h * 0.40, "KEY IDEA", color="gray", fontsize=self.fs(8), fontweight="bold", va="top")
            self.over.text(x + 0.012, y + h * 0.35, textwrap.fill(idea, 36), fontsize=self.fs(9), va="top",
                           linespacing=1.35, color="#333333")
            self.over.text(x + w - 0.012, y + h * 0.05, "Click to view  >", color=colour, fontsize=self.fs(9),
                           fontweight="bold", ha="right", va="center")
            self.cards.append((name, x, y, w, h, body))

    def card_at(self, event):
        if event.inaxes is not self.over:
            return None
        for name, x, y, w, h, body in self.cards:
            if x <= event.xdata <= x + w and y <= event.ydata <= y + h:
                return name
        return None

    def on_click(self, event):
        if self.tab != "Overview" or self.detail_name is not None:
            return
        name = self.card_at(event)
        if name:
            self.show_detail(name)

    def on_move(self, event):
        """Highlight the card under the mouse."""
        if self.tab != "Overview" or self.detail_name is not None:
            return
        name = self.card_at(event)
        if name == self.hover:
            return
        self.hover = name
        for card_name, x, y, w, h, body in self.cards:
            on = card_name == name
            body.set_linewidth(3 if on else 1.2)
            body.set_edgecolor(CATEGORY_COLORS[ALGO_INFO[card_name][0]] if on else "#b5bcc7")
        self.fig.canvas.draw_idle()

    # ---------- visualizer ----------
    def choose(self, name):
        """Algorithm selected: load its labels and default input, then run it."""
        self.algo = name
        label1, default1, label2, default2, _ = ALGORITHMS[name]
        self.set_box_titles()
        self.highlight_radio()
        for box, value in ((self.box1, default1), (self.box2, default2)):
            box.eventson = False              # do not trigger Run while filling defaults
            box.set_val(value)
            box.eventson = True
        self.run()

    def highlight_radio(self):
        """Selected algorithm: bold and in its category colour."""
        colour = CATEGORY_COLORS[ALGO_INFO[self.algo][0]]
        for label in self.radio.labels:
            selected = label.get_text() == self.algo
            label.set_fontweight("bold" if selected else "normal")
            label.set_color(colour if selected else "black")

    def fs(self, size):
        """Font size scaled with the window size."""
        return size * self.scale

    def set_box_titles(self):
        label1, _, label2, _, _ = ALGORITHMS[self.algo]
        self.box1.ax.set_title(label1, fontsize=self.fs(8), loc="left")
        self.box2.ax.set_title(label2, fontsize=self.fs(8), loc="left")

    def rescale(self, event=None):
        """Window resized: scale every text with it and redraw the pages."""
        w, h = self.fig.get_size_inches()
        scale = max(0.6, min(w / 11.5, h / 6.6))
        if abs(scale - self.scale) < 0.04:
            return
        self.scale = scale
        self.title.set_fontsize(self.fs(14))
        for b in list(self.buttons.values()) + list(self.tab_buttons.values()) + [self.back, self.open_btn]:
            b.label.set_fontsize(self.fs(10))
        for label in self.radio.labels:
            label.set_fontsize(self.fs(10))
        self.radio_ax.title.set_fontsize(self.fs(12))
        for box in (self.box1, self.box2):
            box.text_disp.set_fontsize(self.fs(10))
        self.set_box_titles()
        self.speed.label.set_fontsize(self.fs(10))
        self.speed.valtext.set_fontsize(self.fs(10))
        self.legend.clear()
        self.draw_legend()
        self.draw()
        self.draw_overview()
        if self.detail_name:
            self.draw_detail(self.detail_name)
        self.fig.canvas.draw_idle()

    def run(self):
        self.stop()
        try:
            self.steps = ALGORITHMS[self.algo][4](self.box1.text, self.box2.text)
            self.error = None
        except Exception as err:
            self.steps, self.error = [], str(err)
        self.show(0)

    def show(self, i):
        if self.steps:
            self.i = max(0, min(i, len(self.steps) - 1))
        self.draw()

    def play(self):
        if self.timer and self.buttons["Play"].label.get_text() == "Pause":
            self.stop()
        elif self.steps:
            if self.i >= len(self.steps) - 1:
                self.i = 0
            self.buttons["Play"].label.set_text("Pause")
            self.timer.start()

    def stop(self):
        self.timer.stop()
        self.buttons["Play"].label.set_text("Play")

    def on_key(self, event):
        if self.tab != "Visualizer":
            return
        if self.box1.capturekeystrokes or self.box2.capturekeystrokes:
            return                            # user is typing in a box
        if event.key == "right":
            self.show(self.i + 1)
        elif event.key == "left":
            self.show(self.i - 1)

    def delay(self):
        """Milliseconds between steps while playing (speed 1 = 1000 ms, speed 10 = 100 ms)."""
        return int(1100 - 100 * self.speed.val)

    def set_speed(self, value):
        self.timer.interval = self.delay()

    def show_result(self):
        """Skip all the steps and show the final output directly."""
        self.stop()
        self.show(len(self.steps) - 1)

    def draw_legend(self):
        """Colour legend."""
        self.legend.clear()
        self.legend.axis("off")
        for k, (name, color, kind) in enumerate(LEGEND):
            y = 0.88 - k * 0.19
            if kind == "line":
                self.legend.add_line(Line2D([0.02, 0.10], [y, y], color=color, linewidth=3,
                                            transform=self.legend.transAxes))
            else:
                self.legend.add_patch(Rectangle((0.02, y - 0.07), 0.08, 0.14, facecolor=color,
                                                edgecolor="gray", linewidth=0.4, transform=self.legend.transAxes))
            self.legend.text(0.15, y, name, va="center", fontsize=self.fs(9), transform=self.legend.transAxes)

    def tick(self):
        if self.i >= len(self.steps) - 1:
            self.stop()
            self.fig.canvas.draw_idle()
        else:
            self.show(self.i + 1)

    def draw(self):
        ax = self.ax
        ax.clear()
        self.info.clear()
        self.info.axis("off")
        if not self.steps:
            self.info.text(0, 1, "INPUT ERROR\n\n" + str(self.error or ""), va="top", color="red", fontsize=self.fs(10))
            self.fig.canvas.draw_idle()
            return

        # build the pixel grid from every step up to the current one
        grid = np.zeros((N, N))
        for step in self.steps[: self.i + 1]:
            for x, y in step.get("pixels", []):
                if 0 <= x < N and 0 <= y < N:
                    grid[y][x] = step.get("color", 2)
        for x, y in self.steps[self.i].get("pixels", []):
            if 0 <= x < N and 0 <= y < N and self.steps[self.i].get("highlight", True):
                grid[y][x] = 4                       # highlight the current step

        ax.imshow(grid, cmap=CMAP, vmin=0, vmax=4, origin="lower", extent=(-0.5, N - 0.5, -0.5, N - 0.5))
        ax.set_xticks(range(N))
        ax.set_yticks(range(N))
        ax.set_xticks(np.arange(-0.5, N, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, N, 1), minor=True)
        ax.grid(which="minor", color="lightgray", linewidth=0.5)
        ax.tick_params(labelsize=self.fs(6), which="both", length=0)
        for pts, color, closed in self.steps[self.i].get("shapes", []):
            if not pts:
                continue                         # e.g. polygon completely outside the window
            xs = [p[0] for p in pts] + ([pts[0][0]] if closed else [])
            ys = [p[1] for p in pts] + ([pts[0][1]] if closed else [])
            ax.plot(xs, ys, color=color, linewidth=2)
        ax.set_title(f"{self.algo}  -  step {self.i + 1} / {len(self.steps)}", fontsize=self.fs(12))

        self.draw_info()
        self.fig.canvas.draw_idle()

    def draw_info(self):
        """Right-hand panel: header, algorithm, step + progress bar, result (last step), heading, explanation."""
        info, t = self.info, self.info.transAxes          # place everything in 0..1 panel coordinates
        n = len(self.steps)
        last = self.i == n - 1
        colour = CATEGORY_COLORS[ALGO_INFO[self.algo][0]]
        pos = info.get_position()
        w_in, h_in = pos.width * self.fig.get_figwidth(), pos.height * self.fig.get_figheight()
        pad = 0.06                                         # same left margin for every row

        info.add_patch(Rectangle((0, 0), 1, 1, transform=t, facecolor="#f5f7fa", edgecolor="gray"))
        y = 0.955
        info.text(pad, y, "\u2713 COMPLETED" if last else "STEP DETAILS", fontsize=self.fs(12.5),
                  fontweight="bold", va="top", transform=t, color="darkgreen" if last else "navy")
        y -= 0.07
        if last:                                           # Accepted / Rejected, Filled X pixels, X pixels plotted
            text, result_colour = result_summary(self.algo, self.steps)
            info.text(pad, y, text, fontsize=self.fs(11.5), fontweight="bold", va="top", transform=t,
                      color=result_colour)
            y -= 0.065
        info.text(pad, y, self.algo, fontsize=self.fs(12), fontweight="bold", va="top", transform=t, color=colour)
        y -= 0.06
        info.text(pad, y, f"Step {self.i + 1} of {n}", fontsize=self.fs(10.5), va="top", transform=t)
        y -= 0.055

        # progress bar
        frac, bar_w = (self.i + 1) / n, 0.66
        info.add_patch(Rectangle((pad, y - 0.025), bar_w, 0.025, transform=t, facecolor="#dde2ea", edgecolor="none"))
        info.add_patch(Rectangle((pad, y - 0.025), bar_w * frac, 0.025, transform=t,
                                 facecolor="darkgreen" if last else colour, edgecolor="none"))
        info.text(pad + bar_w + 0.04, y - 0.0125, f"{round(frac * 100)}%", fontsize=self.fs(10), va="center",
                  transform=t)
        y -= 0.065
        info.plot([pad, 1 - pad], [y, y], color="gray", linewidth=0.8, transform=t)
        y -= 0.035

        # bold heading (first line of the step text), then the explanation below it
        lines = self.steps[self.i]["text"].split("\n")
        hsize = self.fs(12)
        heading = textwrap.fill(lines[0], max(12, int(0.88 * w_in / (0.66 * hsize / 72))))
        info.text(pad, y, heading, fontsize=hsize, fontweight="bold", va="top", linespacing=1.25, transform=t)
        y -= (heading.count("\n") + 1) * hsize * 1.25 / 72 / h_in + 0.035

        # explanation: the largest font size that still fits in the space that is left
        avail_in = max(0.2, (y - 0.03) * h_in)
        for size in (10.5, 9.5, 8.5, 7.5, 6.5):
            fsz = self.fs(size)
            chars = max(12, int(0.88 * w_in / (0.6 * fsz / 72)))
            body = "\n".join(textwrap.fill(l, chars) for l in lines[1:])
            if (body.count("\n") + 1) * fsz * 1.45 / 72 <= avail_in:
                break
        info.text(pad, y, body, fontsize=fsz, va="top", linespacing=1.45, transform=t)
        info.set_xlim(0, 1)
        info.set_ylim(0, 1)
        self.fig.canvas.draw_idle()


if __name__ == "__main__":
    App()
    plt.show()