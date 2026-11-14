"""
Computer Graphics Algorithm Visualizer - Streamlit version.

Run locally:   streamlit run app.py
Deploy:        push the repo to GitHub -> share.streamlit.io -> pick app.py

This file only replaces the Matplotlib-widget window. The algorithms/ package and the data tables in
main.py (ALGORITHMS, ALGO_INFO, ALGO_DOC, ALGO_EXTRA, legends, colours, result_summary) are reused as they are.
"""
import base64
import html
import json
import math
import time

import matplotlib
matplotlib.use("Agg")                      # no window: figures are only drawn into the web page
import streamlit as st
import streamlit.components.v1 as components

from main import (N, CMAP, ORDER, ALGORITHMS, ALGO_INFO, ALGO_DOC, ALGO_EXTRA,
                  CATEGORY_COLORS, LEGEND, LEGEND_BY_CATEGORY, LEGEND_BY_ALGO, result_summary)

CATEGORIES = list(dict.fromkeys(ALGO_INFO[n][0] for n in ORDER))

ICONS = {"Line drawing": "📏", "Circle drawing": "⭕", "Region filling": "🪣",
         "Clipping": "✂️", "Transformation": "🔄", "Curves": "〰️"}

CSS = """
<style>
:root {--brand: #3b6fd4; --brand2: #7e4fc2; --ink: #1f2430; --line: #dfe4ef; --soft: #f4f6fb;}
.block-container, [data-testid="stMainBlockContainer"] {padding-top: 4.2rem !important; max-width: 1320px;}
header[data-testid="stHeader"] {background: rgba(255,255,255,.75); backdrop-filter: blur(8px);}
footer {visibility: hidden;}

/* ---- sidebar ---- */
section[data-testid="stSidebar"] {background: linear-gradient(180deg, #f7f9fe 0%, #eef1fa 100%);
                                  border-right: 1px solid var(--line);}
.brand {display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.1rem; color: var(--ink);
        margin: 2px 0 10px 0;}
.brand span {display: inline-flex; width: 34px; height: 34px; border-radius: 10px; align-items: center;
             justify-content: center; background: linear-gradient(135deg, var(--brand), var(--brand2)); color: #fff;}
.sect {font-size: .72rem; font-weight: 800; letter-spacing: .1em; color: #6b7488; margin: 14px 0 6px 0;}

/* ---- hero ---- */
.hero {position: relative; overflow: hidden; color: #fff; border-radius: 20px; padding: 22px 28px; margin-bottom: 16px;
       background: radial-gradient(circle at 92% 12%, rgba(255,255,255,.22), transparent 38%),
                   radial-gradient(circle at 70% 120%, rgba(255,255,255,.16), transparent 40%),
                   linear-gradient(115deg, #2f5fc4 0%, #7e4fc2 55%, #c2417a 100%);
       box-shadow: 0 10px 28px rgba(79, 70, 190, .28);}
.hero h1 {color: #fff; font-size: 1.75rem; margin: 0; padding: 0; font-weight: 800; letter-spacing: -.01em;}
.hero p {margin: 6px 0 12px 0; opacity: .94; font-size: .98rem; max-width: 720px;}
.hero .stats {display: flex; flex-wrap: wrap; gap: 8px;}
.hero .stats span {background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.3); padding: 3px 13px;
                   border-radius: 999px; font-size: .78rem; font-weight: 650; backdrop-filter: blur(4px);}

/* ---- cards / containers ---- */
.st-key-stage {padding: 14px 18px 20px 18px !important;}
.st-key-stage div[data-testid="stSlider"] {padding: 0 6px;}
div[data-testid="stExpander"] {border-radius: 14px; border: 1px solid var(--line); background: #fff;}
.st-key-stage, [class*="st-key-card_"] {border-radius: 18px !important; border: 1px solid var(--line) !important;
        background: #fff; box-shadow: 0 2px 10px rgba(31, 36, 48, .05); transition: box-shadow .18s, transform .18s;}
[class*="st-key-card_"]:hover {box-shadow: 0 10px 24px rgba(31, 36, 48, .12); transform: translateY(-2px);}

/* ---- step panel ---- */
.panel {border: 1px solid var(--line); border-left: 6px solid var(--accent, var(--brand)); border-radius: 18px;
        padding: 16px 20px 18px 20px; background: #fff; box-shadow: 0 2px 10px rgba(31, 36, 48, .05);}
.panel .phead {display: flex; align-items: center; justify-content: space-between;}
.pill {display: inline-block; padding: 3px 12px; border-radius: 999px; font-size: .72rem; font-weight: 800;
       letter-spacing: .07em;}
.pill.run {background: #e7eefc; color: #1f3a8a;}
.pill.ok {background: #def5e5; color: #1b7f3b;}
.panel .result {font-size: 1.12rem; font-weight: 800; margin: 10px 0 0 0;}
.panel .meta {display: flex; align-items: center; gap: 10px; margin: 12px 0 4px 0; font-size: .9rem;}
.bar {height: 10px; border-radius: 99px; background: #e8ecf5; overflow: hidden; flex: 1;}
.bar > div {height: 100%; border-radius: 99px; transition: width .25s;}
.tiles {display: flex; gap: 10px; margin: 12px 0 4px 0;}
.tile {flex: 1; background: var(--soft); border: 1px solid var(--line); border-radius: 12px; padding: 8px 12px;}
.tile small {display: block; font-size: .64rem; font-weight: 800; letter-spacing: .1em; color: #6b7488;}
.tile b {font-size: 1.15rem; color: var(--ink);}
.panel .heading {font-size: 1.08rem; font-weight: 800; margin: 14px 0 8px 0; color: var(--ink);}
.panel .body {font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: .82rem; line-height: 1.55;
              white-space: pre-wrap; max-height: 300px; overflow-y: auto; background: var(--soft);
              border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; color: #2b3142;}

/* ---- chips, legend, labels ---- */
.chip {display: inline-block; padding: 2px 11px; border-radius: 999px; color: #fff; font-size: .7rem; font-weight: 750;
       letter-spacing: .04em;}
.legend {display: flex; flex-wrap: wrap; gap: 6px 8px; font-size: .78rem; margin: 10px 0 2px 0;}
.legend span {display: inline-flex; align-items: center; gap: 7px; background: var(--soft); border: 1px solid var(--line);
              padding: 3px 11px; border-radius: 999px;}
.legend i {width: 13px; height: 13px; border: 1px solid #8a93a6; border-radius: 3px; display: inline-block;}
.legend b {width: 20px; height: 4px; border-radius: 2px; display: inline-block;}
.label {font-size: .68rem; font-weight: 800; letter-spacing: .1em; color: #6b7488; margin-top: 10px;}
[class*="st-key-card_"] {padding: 6px 4px;}
div[data-testid="stHorizontalBlock"] {row-gap: 1.1rem;}
.cardhead {color: #fff; padding: 9px 14px; border-radius: 12px; display: flex; justify-content: space-between;
           align-items: center; font-weight: 750; margin-bottom: 10px;}
.cardhead small {font-size: .64rem; letter-spacing: .09em; opacity: .92; font-weight: 750;}
.doc div {white-space: pre-wrap; line-height: 1.8; font-size: .98rem;}
.box {border: 1px solid var(--line); border-radius: 14px; padding: 14px 18px; height: 100%; background: #fff;
      box-shadow: 0 2px 10px rgba(31, 36, 48, .05);}

/* ---- buttons ---- */
div.stButton > button, div[data-testid="stFormSubmitButton"] > button {width: 100%; border-radius: 12px; font-weight: 650;
        transition: transform .12s, box-shadow .12s, border-color .12s;}
div.stButton > button p, div[data-testid="stFormSubmitButton"] > button p {white-space: nowrap; font-size: .88rem; margin: 0;}
div.stButton > button, div[data-testid="stFormSubmitButton"] > button {padding: .3rem .4rem; min-height: 2.5rem;}
button[data-testid^="stBaseButton-secondary"] {background: #fff; border: 1px solid var(--line);}
button[data-testid^="stBaseButton-secondary"]:hover:not(:disabled) {border-color: var(--brand); color: var(--brand);
        transform: translateY(-1px);}
button[data-testid^="stBaseButton-primary"] {background: linear-gradient(135deg, var(--brand), var(--brand2)); border: none;
        color: #fff;}
button[data-testid^="stBaseButton-primary"]:hover:not(:disabled) {box-shadow: 0 6px 16px rgba(79, 70, 190, .35);
        transform: translateY(-1px); color: #fff;}

@media (max-width: 800px) {.hero h1 {font-size: 1.3rem;} .hero {padding: 16px 18px;}}
</style>
"""


# ---------------------------------------------------------------- small helpers
def h(s):
    """Join a multi-line HTML string into one line (markdown would treat indented lines as code)."""
    return "".join(line.strip() for line in s.splitlines())


def esc(text):
    return html.escape(str(text)).replace("\n", "<br>")


def chip(category):
    return (f'<span class="chip" style="background:{CATEGORY_COLORS[category]}">'
            f'{ICONS.get(category, "")} {esc(category.upper())}</span>')


# ---------------------------------------------------------------- drawing (same picture as the desktop version)
def view_limits(algo, steps):
    """Visible grid. Normally N x N; transformations grow it so results at negative / large coordinates stay visible."""
    x_lo = y_lo = 0
    x_hi = y_hi = N - 1
    if ALGO_INFO[algo][0] == "Transformation":
        for stp in steps:
            for shape in stp.get("shapes", []):
                if shape[1] == "purple":                       # the mirror line is very long: it is clipped instead
                    continue
                for x, y in shape[0]:
                    x_lo, x_hi = min(x_lo, int(math.floor(x)) - 1), max(x_hi, int(math.ceil(x)) + 1)
                    y_lo, y_hi = min(y_lo, int(math.floor(y)) - 1), max(y_hi, int(math.ceil(y)) + 1)
    return (x_lo, x_hi), (y_lo, y_hi)


PIXEL_COLOURS = list(CMAP.colors)               # 0 empty, 1 boundary, 2 line/circle, 3 filled, 4 current step, 5 input point
PLOT = 600                                       # size of the grid area inside the SVG, in SVG units
DASH = {"--": "7 5", ":": "2 4", "-.": "8 4 2 4"}


def f1(v):
    return f"{v:.1f}"


def render_svg(algo, steps, i, limits):
    """The grid of step i as an SVG string: pixels, light grid lines, axes, shapes, tick labels and title."""
    (x_lo, x_hi), (y_lo, y_hi) = limits
    W, H = x_hi - x_lo + 1, y_hi - y_lo + 1
    cs = PLOT / max(W, H)                                       # size of one pixel cell
    ml, mt, mr, mb = 36, 40, 12, 28
    pw, ph = W * cs, H * cs
    vw, vh = ml + pw + mr, mt + ph + mb

    def X(x):                                                   # data -> svg (centre of a pixel)
        return ml + (x - x_lo + 0.5) * cs

    def Y(y):
        return mt + (y_hi - y + 0.5) * cs

    cells = {}
    for stp in steps[: i + 1]:                                  # every pixel drawn up to the current step
        colour = stp.get("color", 2)
        for x, y in stp.get("pixels", ()):
            if 0 <= x < N and 0 <= y < N:
                cells[(x, y)] = colour
    now = steps[i]
    if now.get("highlight", True):                              # current step in orange
        for x, y in now.get("pixels", ()):
            if 0 <= x < N and 0 <= y < N:
                cells[(x, y)] = 4

    by_colour = {}
    for (x, y), c in cells.items():
        if c:
            by_colour.setdefault(c, []).append(f"M{f1(ml + (x - x_lo) * cs)} {f1(mt + (y_hi - y) * cs)}"
                                               f"h{f1(cs)}v{f1(cs)}h-{f1(cs)}z")
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f1(vw)} {f1(vh)}" '
           f'font-family="Helvetica, Arial, sans-serif"><rect width="{f1(vw)}" height="{f1(vh)}" fill="#fff"/>',
           f'<clipPath id="c"><rect x="{f1(ml)}" y="{f1(mt)}" width="{f1(pw)}" height="{f1(ph)}"/></clipPath>']
    for c, parts in by_colour.items():
        out.append(f'<path d="{"".join(parts)}" fill="{PIXEL_COLOURS[int(c)]}"/>')

    grid = [f"M{f1(ml + k * cs)} {f1(mt)}v{f1(ph)}" for k in range(W + 1)] + \
           [f"M{f1(ml)} {f1(mt + k * cs)}h{f1(pw)}" for k in range(H + 1)]
    out.append(f'<path d="{"".join(grid)}" stroke="#cdd2dc" stroke-width="0.8" fill="none" shape-rendering="crispEdges"/>')
    if x_lo < 0 or y_lo < 0:                                    # show the axes through the origin
        out.append(f'<path d="M{f1(X(0))} {f1(mt)}v{f1(ph)}M{f1(ml)} {f1(Y(0))}h{f1(pw)}" stroke="dimgray" '
                   f'stroke-width="1.4" fill="none"/>')

    out.append('<g clip-path="url(#c)" fill="none" stroke-linejoin="round" stroke-linecap="round">')
    for shape in now.get("shapes", []):
        pts, colour, closed = shape[:3]
        if not pts:
            continue                                            # e.g. polygon completely outside the window
        width = (shape[3] if len(shape) > 3 else 2) * 1.6
        dash = f' stroke-dasharray="{DASH.get(shape[4], "7 5")}"' if len(shape) > 4 and shape[4] != "-" else ""
        coords = " ".join(f"{f1(X(x))},{f1(Y(y))}" for x, y in pts)
        tag = "polygon" if closed else "polyline"
        out.append(f'<{tag} points="{coords}" stroke="{colour}" stroke-width="{width:.1f}"{dash}/>')
    out.append("</g>")
    out.append(f'<rect x="{f1(ml)}" y="{f1(mt)}" width="{f1(pw)}" height="{f1(ph)}" fill="none" stroke="#9aa3b5" '
               f'stroke-width="1"/>')

    size = 11 if cs >= 18 else 9                                # tick labels (every pixel unless the grid is large)
    gap = max(1, -(-W // 40))
    gap_y = max(1, -(-H // 40))
    out.append(f'<g font-size="{size}" fill="#4a5265">')
    for x in range(x_lo, x_hi + 1, gap):
        out.append(f'<text x="{f1(X(x))}" y="{f1(mt + ph + 17)}" text-anchor="middle">{x}</text>')
    for y in range(y_lo, y_hi + 1, gap_y):
        out.append(f'<text x="{f1(ml - 7)}" y="{f1(Y(y) + size * 0.35)}" text-anchor="end">{y}</text>')
    out.append("</g>")
    out.append(f'<text x="{f1(ml + pw / 2)}" y="24" text-anchor="middle" font-size="17" font-weight="700" '
               f'fill="#1f2430">{html.escape(algo)}  -  step {i + 1} / {len(steps)}</text></svg>')
    return "".join(out)


def chart_html(svg):
    """An <img> with the SVG inside (a data URI): scales to the column width and stays sharp."""
    return ('<img alt="grid" style="width:100%;display:block" src="data:image/svg+xml;base64,'
            + base64.b64encode(svg.encode()).decode() + '">')



@st.cache_data(show_spinner=False, max_entries=6)
def build_frames(algo, run_id, _steps, _limits):
    """All SVG frames and detail panels as JSON. Cached per run, so Next / Prev clicks do not rebuild them."""
    frames = [base64.b64encode(render_svg(algo, _steps, i, _limits).encode()).decode() for i in range(len(_steps))]
    counts, seen = [], set()
    for stp in _steps:
        if stp.get("color") != 5:
            seen.update((x, y) for x, y in stp.get("pixels", []) if 0 <= x < N and 0 <= y < N)
        counts.append(len(seen))
    details = [info_html(algo, _steps, i, counts[i]) for i in range(len(_steps))]
    return (json.dumps(frames).replace("</", "<\\/"), json.dumps(details).replace("</", "<\\/"))


def fullscreen_graph(algo, run_id, steps, limits, start_index, speed_value):
    """Full-screen graph viewer with step details on the right."""
    frames_json, details_json = build_frames(algo, run_id, steps, limits)
    first_detail = json.loads(details_json)[max(0, min(start_index, len(steps) - 1))]
    legend = legend_html(algo)
    safe_algo = esc(algo)
    n = len(steps)
    start_index = max(0, min(start_index, n - 1))
    component_html = f'''<!doctype html>
<html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}} body{{margin:0;font-family:Arial,sans-serif;color:#1f2430}}
#fs-viewer{{width:100%;}}
#open-fullscreen{{border:1px solid #dfe4ef;background:#fff;border-radius:10px;padding:10px 16px;
  font-size:14px;font-weight:700;cursor:pointer;color:#2f5fc4}}
#fs-viewer:fullscreen{{width:100vw;height:100vh;background:#f7f8fc;padding:14px 22px;display:flex;
  flex-direction:column;gap:10px;overflow:auto}}
#fs-viewer:fullscreen #fs-panel{{display:flex}}
#fs-panel{{display:none;flex-direction:column;flex:1;min-height:0;gap:10px}}
.fs-header{{display:flex;justify-content:space-between;align-items:center;gap:12px}}
.fs-header h2{{font-size:18px;margin:0}}
.fs-btn{{border:1px solid #d7ddeb;background:#fff;border-radius:9px;padding:9px 13px;font-weight:650;cursor:pointer}}
.fs-btn.primary{{background:linear-gradient(135deg,#3b6fd4,#7e4fc2);color:#fff;border:0}}
#fs-content{{display:grid;grid-template-columns:minmax(0,2fr) minmax(300px,1fr);gap:14px;flex:1;min-height:0}}
#fs-left{{display:flex;flex-direction:column;gap:10px;min-width:0;min-height:0}}
#fs-graph-wrap{{flex:1;min-height:180px;display:flex;align-items:center;justify-content:center;
  background:#fff;border:1px solid #dfe4ef;border-radius:14px;padding:8px;overflow:hidden}}
#fs-graph{{width:100%;height:100%;object-fit:contain}}
#fs-steps{{min-width:0;min-height:0;overflow:auto;background:#fff;border-radius:14px}}
.panel{{border:1px solid #dfe4ef;border-left:6px solid var(--accent,#3b6fd4);border-radius:18px;
 padding:16px 20px 18px;background:#fff;box-shadow:0 2px 10px rgba(31,36,48,.05)}}
.panel .phead{{display:flex;align-items:center;justify-content:space-between}}
.pill{{display:inline-block;padding:3px 12px;border-radius:999px;font-size:.72rem;font-weight:800;letter-spacing:.07em}}
.pill.run{{background:#e7eefc;color:#1f3a8a}} .pill.ok{{background:#def5e5;color:#1b7f3b}}
.panel .result{{font-size:1.12rem;font-weight:800;margin:10px 0 0}}
.panel .meta{{display:flex;align-items:center;gap:10px;margin:12px 0 4px;font-size:.9rem}}
.bar{{height:10px;border-radius:99px;background:#e8ecf5;overflow:hidden;flex:1}}
.bar>div{{height:100%;border-radius:99px}}
.tiles{{display:flex;gap:10px;margin:12px 0 4px}}
.tile{{flex:1;background:#f4f6fb;border:1px solid #dfe4ef;border-radius:12px;padding:8px 12px}}
.tile small{{display:block;font-size:.64rem;font-weight:800;letter-spacing:.1em;color:#6b7488}}
.tile b{{font-size:1.15rem;color:#1f2430}}
.panel .heading{{font-size:1.08rem;font-weight:800;margin:14px 0 8px;color:#1f2430}}
.panel .body{{font-family:ui-monospace,Consolas,monospace;font-size:.82rem;line-height:1.55;white-space:pre-wrap;
 max-height:300px;overflow-y:auto;background:#f4f6fb;border:1px solid #dfe4ef;border-radius:12px;padding:12px 14px;color:#2b3142}}
.chip{{display:inline-block;padding:2px 11px;border-radius:999px;color:#fff;font-size:.7rem;font-weight:750;letter-spacing:.04em}}
.label{{font-size:.68rem;font-weight:800;letter-spacing:.1em;color:#6b7488;margin-top:10px}}
.fs-controls{{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:8px}}
.fs-controls button{{min-width:88px}}
.fs-range{{display:flex;align-items:center;gap:12px;width:100%;font-size:13px}}
.fs-range input{{flex:1;min-width:100px;accent-color:#3b6fd4}}
.fs-speed{{display:flex;align-items:center;gap:10px;justify-content:center;font-size:13px}}
.fs-speed input{{accent-color:#3b6fd4}}
#fs-legend{{max-height:90px;overflow:auto}}
@media(max-width:800px){{
 #fs-viewer:fullscreen{{padding:8px}}
 #fs-content{{grid-template-columns:1fr;grid-template-rows:minmax(260px,1fr) auto}}
 #fs-steps{{max-height:38vh}}
 .fs-btn{{padding:8px}}
 .fs-controls button{{min-width:70px}}
}}
</style></head><body>
<div id="fs-viewer">
  <button id="open-fullscreen">⛶ Maximize Graph</button>
  <div id="fs-panel">
    <div class="fs-header"><h2>{safe_algo} — Full Screen View</h2>
      <div style="display:flex;gap:8px;align-items:center">
        <span style="font-size:12px;color:#6b7488">Keys: ← → step, Space play/pause, Home / End</span>
        <button class="fs-btn" id="save-png">⬇ Save PNG</button>
        <button class="fs-btn" id="close-fullscreen">✕ Exit Full Screen</button></div></div>
    <div id="fs-content">
      <div id="fs-left">
        <div id="fs-graph-wrap"><img id="fs-graph" alt="{safe_algo} graph"></div>
        <div class="fs-controls">
          <button class="fs-btn" id="first">⏮ First</button>
          <button class="fs-btn" id="prev">◀ Previous</button>
          <button class="fs-btn primary" id="play">▶ Play</button>
          <button class="fs-btn" id="next">Next ▶</button>
          <button class="fs-btn" id="last">Result ⏭</button>
        </div>
        <div class="fs-range"><span id="step-label">Step {start_index + 1} / {n}</span>
          <input id="step-range" type="range" min="1" max="{n}" value="{start_index + 1}"></div>
        <div class="fs-speed"><label for="speed-range">Playback speed</label>
          <input id="speed-range" type="range" min="1" max="10" value="{int(speed_value)}">
          <span id="speed-label">{int(speed_value)} / 10</span></div>
        <div id="fs-legend">{legend}</div>
      </div>
      <div id="fs-steps">{first_detail}</div>
    </div>
  </div>
</div>
<script>
(()=>{{
 const frames={frames_json}, details={details_json}, root=document.getElementById('fs-viewer');
 const img=document.getElementById('fs-graph'), range=document.getElementById('step-range');
 const label=document.getElementById('step-label'), playBtn=document.getElementById('play');
 const speed=document.getElementById('speed-range'), speedLabel=document.getElementById('speed-label');
 const stepPanel=document.getElementById('fs-steps');
 let index={start_index}, timer=null;
 function render(){{
   img.src='data:image/svg+xml;base64,'+frames[index];
   stepPanel.innerHTML=details[index];
   range.value=index+1;
   label.textContent='Step '+(index+1)+' / '+frames.length;
   document.getElementById('first').disabled=index===0;document.getElementById('prev').disabled=index===0;
   document.getElementById('next').disabled=index===frames.length-1;
   document.getElementById('last').disabled=index===frames.length-1;
 }}
 function stop(){{if(timer)clearInterval(timer);timer=null;playBtn.textContent='▶ Play';}}
 function start(){{if(index>=frames.length-1)index=0;render();playBtn.textContent='⏸ Pause';
   timer=setInterval(()=>{{if(index>=frames.length-1){{stop();return;}}index++;render();}},1100-100*Number(speed.value));}}
 document.getElementById('open-fullscreen').addEventListener('click',async()=>{{
   try{{await root.requestFullscreen();}}catch(e){{alert('Full-screen mode is not available in this browser. Please allow full-screen access.');}}
 }});
 document.getElementById('close-fullscreen').addEventListener('click',()=>{{stop();if(document.fullscreenElement)document.exitFullscreen();}});
 document.addEventListener('fullscreenchange',()=>{{if(!document.fullscreenElement)stop();}});
 document.getElementById('first').onclick=()=>{{stop();index=0;render();}};
 document.getElementById('prev').onclick=()=>{{stop();index=Math.max(0,index-1);render();}};
 document.getElementById('next').onclick=()=>{{stop();index=Math.min(frames.length-1,index+1);render();}};
 document.getElementById('last').onclick=()=>{{stop();index=frames.length-1;render();}};
 playBtn.onclick=()=>{{if(timer)stop();else start();}};
 document.addEventListener('keydown',e=>{{
   if(!document.fullscreenElement)return;
   if(e.key==='ArrowRight'){{stop();index=Math.min(frames.length-1,index+1);render();}}
   else if(e.key==='ArrowLeft'){{stop();index=Math.max(0,index-1);render();}}
   else if(e.key==='Home'){{stop();index=0;render();}}
   else if(e.key==='End'){{stop();index=frames.length-1;render();}}
   else if(e.key===' '){{if(timer)stop();else start();}}
   else return;
   e.preventDefault();
 }});
 document.getElementById('save-png').onclick=()=>{{
   const im=new Image();
   im.onload=()=>{{
     const c=document.createElement('canvas');c.width=1400;c.height=Math.round(1400*(im.naturalHeight||1)/(im.naturalWidth||1));
     const g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,c.width,c.height);g.drawImage(im,0,0,c.width,c.height);
     const a=document.createElement('a');a.download='{safe_algo.replace(" ","_")}_step_'+(index+1)+'.png';a.href=c.toDataURL('image/png');a.click();
   }};
   im.src='data:image/svg+xml;base64,'+frames[index];
 }};
 range.oninput=()=>{{stop();index=Number(range.value)-1;render();}};
 speed.oninput=()=>{{speedLabel.textContent=speed.value+' / 10';if(timer){{stop();start();}}}};
 render();
}})();
</script></body></html>'''
    components.html(component_html, height=52, scrolling=False)

def legend_html(algo):
    entries = LEGEND_BY_ALGO.get(algo) or LEGEND_BY_CATEGORY.get(ALGO_INFO[algo][0], LEGEND)
    items = []
    for name, colour, kind in entries:
        if kind == "line":
            swatch = (f'<span style="display:inline-block;width:22px;height:4px;border-radius:2px;background:{colour};'
                      f'margin-right:8px;vertical-align:middle"></span>')
        else:
            swatch = (f'<span style="display:inline-block;width:14px;height:14px;border:1px solid #8a93a6;border-radius:3px;'
                      f'background:{colour};margin-right:8px;vertical-align:middle"></span>')
        items.append(f'<span style="display:inline-block;margin:0 10px 10px 0;padding:5px 13px;border:1px solid #dfe4ef;'
                     f'border-radius:999px;background:#f4f6fb;font-size:.8rem;white-space:nowrap">{swatch}{esc(name)}</span>')
    return f'<div style="margin:14px 0 6px 0;padding:0 2px;line-height:1.2">{"".join(items)}</div>'


def pixel_count(steps, i):
    seen = set()
    for stp in steps[: i + 1]:
        if stp.get("color") == 5:                               # the red input marker is not a plotted pixel
            continue
        seen.update((x, y) for x, y in stp.get("pixels", []) if 0 <= x < N and 0 <= y < N)
    return len(seen)


def info_html(algo, steps, i, count=None):
    """Right-hand panel: status, result (last step), algorithm, progress, tiles, heading + explanation."""
    n, last = len(steps), i == len(steps) - 1
    category = ALGO_INFO[algo][0]
    colour = CATEGORY_COLORS[category]
    lines = steps[i]["text"].split("\n")
    frac = (i + 1) / n
    pill = '<span class="pill ok">&#10003; COMPLETED</span>' if last else '<span class="pill run">&#9679; STEP DETAILS</span>'
    result = ""
    if last:
        text, result_colour = result_summary(algo, steps)
        result = f'<div class="result" style="color:{result_colour}">{esc(text)}</div>'
    bar_colour = "#1b7f3b" if last else colour
    has_pixels = any(stp.get("pixels") for stp in steps)
    tile2 = (f'<div class="tile"><small>PIXELS DRAWN</small><b>{pixel_count(steps, i) if count is None else count}</b></div>' if has_pixels
             else f'<div class="tile"><small>TYPE</small><b style="font-size:.95rem">{esc(category)}</b></div>')
    return (h(f'<div class="panel" style="--accent:{colour}"><div class="phead">{pill}'
              f'<span style="font-size:.85rem;opacity:.7">{round(frac * 100)}%</span></div>{result}'
              f'<div class="meta">{chip(category)}<b style="color:{colour};font-size:1.02rem">{esc(algo)}</b></div>'
              f'<div class="meta"><div class="bar"><div style="width:{frac * 100:.1f}%;background:{bar_colour}"></div></div></div>'
              f'<div class="tiles"><div class="tile"><small>STEP</small><b>{i + 1}</b>'
              f'<span style="opacity:.55"> / {n}</span></div>{tile2}</div>')
            + f'<div class="heading">{esc(lines[0])}</div><div class="body">{esc(chr(10).join(lines[1:]))}</div></div>')


def doc_html(name):
    rows = "".join(f'<div style="padding-left:{level * 26}px">{esc(text)}</div>' for level, text in ALGO_DOC[name])
    return f'<div class="doc" style="padding:8px 14px 10px 14px">{rows}</div>'


# ---------------------------------------------------------------- state and callbacks
def ss():
    return st.session_state


def current_inputs(algo):
    d = ALGORITHMS[algo]
    saved = ss().inputs.get(algo, (d[1], d[3]))
    return ss().get(f"in1_{algo}", saved[0]), ss().get(f"in2_{algo}", saved[1])


def do_run(algo):
    """Run the algorithm on the current inputs and start again at step 1."""
    a, b = current_inputs(algo)
    ss().inputs[algo] = (a, b)
    try:
        steps, error = ALGORITHMS[algo][4](a, b), None
    except Exception as err:                                    # bad input -> shown as an error message
        steps, error = [], str(err)
    ss().run_id += 1
    ss().run = {"algo": algo, "steps": steps, "error": error, "id": ss().run_id,
                "limits": view_limits(algo, steps) if steps else None}
    ss().cur, ss().playing = 0, False


def reset_inputs(algo):
    d = ALGORITHMS[algo]
    ss()[f"in1_{algo}"], ss()[f"in2_{algo}"] = d[1], d[3]
    do_run(algo)


def go(i):
    n = len(ss().run["steps"])
    ss().cur, ss().playing = max(0, min(i, n - 1)), False


def step_by(d):
    go(ss().cur + d)


def from_slider(key):
    go(ss()[key] - 1)


def toggle_play():
    if ss().playing:
        ss().playing = False
    else:
        if ss().cur >= len(ss().run["steps"]) - 1:
            ss().cur = 0
        ss().playing = True


def open_detail(name):
    ss().detail = name


def close_detail():
    ss().detail = None


def open_in_visualizer(name):
    ss().algo, ss().view, ss().detail = name, "Visualizer", None


# ---------------------------------------------------------------- Visualizer view
def sidebar_controls():
    with st.sidebar:
        st.markdown('<div class="brand"><span>🎨</span>PixelPlay - CG Visualizer</div><div class="sect">ALGORITHM</div>',
                    unsafe_allow_html=True)
        ss().algo = st.selectbox("Choose an algorithm", ORDER, index=ORDER.index(ss().algo), key="algo_widget",
                                 format_func=lambda n: f"{ICONS[ALGO_INFO[n][0]]}  {n}", label_visibility="collapsed")
        algo = ss().algo
        category, description, idea = ALGO_INFO[algo]
        st.markdown(h(f'{chip(category)}<p style="margin:8px 0 2px 0;font-size:.9rem">{esc(description)}</p>'
                      f'<div class="label">KEY IDEA</div><p style="font-size:.85rem;margin:2px 0">{esc(idea)}</p>'),
                    unsafe_allow_html=True)
        st.markdown('<div class="sect">INPUT</div>', unsafe_allow_html=True)
        label1, default1, label2, default2, _ = ALGORITHMS[algo]
        saved = ss().inputs.get(algo, (default1, default2))
        with st.form(f"form_{algo}", border=False):
            st.text_input(label1, value=saved[0], key=f"in1_{algo}")
            if label2:
                st.text_input(label2, value=saved[1], key=f"in2_{algo}")
            c1, c2 = st.columns(2)
            run = c1.form_submit_button("Run", type="primary")
            c2.form_submit_button("Reset", on_click=reset_inputs, args=(algo,))
        st.caption("Press Run (or Enter) to apply. Reset restores the default example.")
        with st.expander("Input tips"):
            st.markdown(f"- The grid is **{N} x {N}**: pixel coordinates run from 0 to {N - 1}.\n"
                        "- Separate points with `;` and x, y with `,`  (e.g. `5,5; 22,5; 14,24`).\n"
                        "- Transformation operations are separated by `;` and applied left to right.")
        return run


def visualizer():
    run_clicked = sidebar_controls()
    algo = ss().algo
    if run_clicked or ss().run is None or ss().run["algo"] != algo:
        do_run(algo)
    run = ss().run

    if run["error"]:
        st.error(f"Input error: {run['error']}")
        return
    steps, limits, n = run["steps"], run["limits"], len(run["steps"])

    left, right = st.columns([1.15, 1], gap="large")
    with left:
        stage = st.container(border=True, key="stage")
    with stage:
        chart_box = st.empty()
    info_box = right.empty()

    def draw(i):
        chart_box.markdown(chart_html(render_svg(algo, steps, i, limits)), unsafe_allow_html=True)
        info_box.markdown(info_html(algo, steps, i), unsafe_allow_html=True)

    draw(ss().cur)

    with stage:
        fullscreen_graph(algo, run["id"], steps, limits, ss().cur, ss().get("speed", 4))
        playing = ss().playing
        b1, b2, b3, b4, b5 = st.columns([1, 1, 1.1, 1, 1.25], gap="small")
        b1.button("⏮ First", on_click=go, args=(0,), disabled=ss().cur == 0)
        b2.button("◀ Prev", on_click=step_by, args=(-1,), disabled=ss().cur == 0)
        b3.button("⏸ Pause" if playing else "▶ Play", on_click=toggle_play, type="primary")
        b4.button("Next ▶", on_click=step_by, args=(1,), disabled=ss().cur >= n - 1)
        b5.button("Result ⏭", on_click=go, args=(n - 1,), disabled=ss().cur >= n - 1)
        if n > 1:
            key = f"sl_{run['id']}"
            ss()[key] = ss().cur + 1
            st.slider("Step", 1, n, key=key, on_change=from_slider, args=(key,), disabled=playing)
        speed = st.slider("Speed", 1, 10, 4, key="speed", help="1 = slowest, 10 = fastest")
        st.markdown(legend_html(algo), unsafe_allow_html=True)

    with right:
        with st.expander("Algorithm written out"):
            st.markdown(doc_html(algo), unsafe_allow_html=True)
            time_cost, use_when = ALGO_EXTRA[algo]
            st.markdown(h(f'<div style="padding:4px 14px 14px 14px"><div class="label">TIME / COST</div>'
                          f'<div>{esc(time_cost)}</div><div class="label">USE IT WHEN</div><div>{esc(use_when)}</div></div>'),
                        unsafe_allow_html=True)

    if ss().playing:                                            # autoplay: redraw frame by frame, then settle
        delay = (1100 - 100 * speed) / 1000
        while ss().cur < n - 1:
            started = time.time()
            ss().cur += 1
            draw(ss().cur)
            time.sleep(max(0.0, delay - (time.time() - started)))
        ss().playing = False
        st.rerun()


# ---------------------------------------------------------------- Overview view
def overview_grid():
    c1, c2 = st.columns([3, 1.4])
    counts = {c: sum(ALGO_INFO[n][0] == c for n in ORDER) for c in CATEGORIES}
    counts["All"] = len(ORDER)
    category = c1.segmented_control("Category", ["All"] + CATEGORIES, default="All", key="cat",
                                    format_func=lambda c: f"{ICONS.get(c, '✨')} {c} ({counts[c]})",
                                    label_visibility="collapsed") or "All"
    query = c2.text_input("Search", key="q", placeholder="Search algorithms...", label_visibility="collapsed")
    names = [n for n in ORDER if (category == "All" or ALGO_INFO[n][0] == category)
             and query.lower().strip() in (n + " " + ALGO_INFO[n][1]).lower()]
    if not names:
        st.info("No algorithm matches. Try another category or search word.")
        return
    for row in range(0, len(names), 3):
        cols = st.columns(3, gap="medium")
        for j, name in enumerate(names[row: row + 3]):
            overview_card(cols[j], row + j, name)


def overview_card(col, k, name):
    category, description, idea = ALGO_INFO[name]
    colour = CATEGORY_COLORS[category]
    with col.container(border=True, key=f"card_{k}"):
        st.markdown(h(f'<div class="cardhead" style="background:{colour}"><span>{esc(name)}</span>'
                      f'<small>{ICONS[category]} {esc(category.upper())}</small></div>'
                      f'<div style="font-size:.9rem;line-height:1.5;min-height:4.6em">{esc(description)}</div>'
                      f'<div class="label">KEY IDEA</div>'
                      f'<div style="font-size:.84rem;line-height:1.5;min-height:4.6em;margin-bottom:6px">{esc(idea)}</div>'),
                    unsafe_allow_html=True)
        st.button("View algorithm  ›", key=f"view_{name}", on_click=open_detail, args=(name,))


def overview_detail(name):
    category, description, idea = ALGO_INFO[name]
    colour = CATEGORY_COLORS[category]
    b1, b2, _ = st.columns([1, 1, 2.5])
    b1.button("‹ Back to overview", on_click=close_detail)
    b2.button("▶ Open in Visualizer", on_click=open_in_visualizer, args=(name,), type="primary")
    st.markdown(h(f'<div class="cardhead" style="background:{colour};font-size:1.4rem;padding:12px 18px">'
                  f'<span>{esc(name)}</span><small>{ICONS[category]} {esc(category.upper())}</small></div>'
                  f'<p style="font-style:italic;margin:6px 0 14px 0">{esc(description)}</p>'
                  f'<div class="label" style="color:{colour};opacity:1">ALGORITHM</div><hr style="margin:4px 0 8px 0;opacity:.3">'),
                unsafe_allow_html=True)
    st.markdown(doc_html(name), unsafe_allow_html=True)
    time_cost, use_when = ALGO_EXTRA[name]
    st.write("")
    for col, (label, text) in zip(st.columns(3, gap="medium"),
                                  [("KEY IDEA", idea), ("TIME / COST", time_cost), ("USE IT WHEN", use_when)]):
        col.markdown(h(f'<div class="box"><div class="label" style="color:{colour};opacity:1;margin-top:0">{label}</div>'
                       f'<div style="font-size:.92rem;margin-top:4px">{esc(text)}</div></div>'),
                     unsafe_allow_html=True)


def overview():
    if ss().detail:
        overview_detail(ss().detail)
    else:
        overview_grid()


# ---------------------------------------------------------------- page
def run_app():
    st.set_page_config(page_title="PixelPlay", page_icon="🎨", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    for key, value in {"algo": ORDER[0], "run": None, "run_id": 0, "cur": 0, "playing": False,
                       "inputs": {}, "detail": None}.items():
        ss().setdefault(key, value)

    st.markdown(h(f'<div class="hero"><h1>PixelPlay - Computer Graphics Algorithm Visualizer</h1>'
                  f'<p>Watch line, circle, fill, clipping, transformation and curve algorithms run one step at a time, '
                  f'with every formula and decision explained.</p>'
                  f'<div class="stats"><span>{len(ORDER)} algorithms</span><span>{len(CATEGORIES)} categories</span>'
                  f'<span>step-by-step playback</span><span>live input</span></div></div>'),
                unsafe_allow_html=True)
    view = st.segmented_control("View", ["Visualizer", "Overview"], default="Visualizer", key="view",
                                label_visibility="collapsed") or "Visualizer"
    if view == "Visualizer":
        visualizer()
    else:
        ss().playing = False
        overview()


if __name__ == "__main__":
    run_app()