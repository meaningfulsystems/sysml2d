"""
sysmld graph — topology-only SVG with circles and straight lines.

Produces a spider-web view with:
  - circles for nodes (labelled)
  - straight lines for connections (solid)
  - dashed lines for boundary inputs
  - Sugiyama rank order to minimise crossings
  - colored rank bands

Also writes a companion .graph.json with computed ranks and suggested
starting coordinates for the LLM to use in the artistic pass.

Usage:
    sysmld graph intent.json
    sysmld graph intent.json --output foo.graph.svg
    sysmld graph intent.json --direction left-right
"""

from __future__ import annotations

import json
import math
from html import escape
from pathlib import Path
from typing import Any

from .layout import compute as _layout

# ── visual constants ──────────────────────────────────────────────────────────
R            = 10      # node dot radius — small, like a spiderweb junction
RANK_GAP     = 160     # centre-to-centre between ranks
COL_GAP      = 120     # centre-to-centre between nodes in the same rank
MARGIN       = 80      # canvas edge → nearest node centre
FONT_SIZE    = 11
SMALL_FONT   = 9

LINE_COLOR   = "#64748B"   # solid edges
DASH_COLOR   = "#CBD5E1"   # boundary input edges (dashed)
DOT_COLOR    = "#1E40AF"   # node fill
DOT_STROKE   = "#1E293B"
TEXT_COLOR   = "#1E293B"


# ── public API ────────────────────────────────────────────────────────────────

def graph_from_spec(spec: dict[str, Any], direction: str | None = None) -> tuple[str, dict]:
    """Return (svg_text, position_data) from a compose intent spec."""
    direction = direction or spec.get("direction", "top-down")
    nodes     = spec.get("nodes", {})
    edges     = spec.get("edges", [])
    binputs   = spec.get("boundary_inputs", [])
    nids = list(nodes.keys())

    # Delegate layout to the shared engine.
    lo = _layout(nids, edges, direction,
                 col_gap=COL_GAP, rank_gap=RANK_GAP, margin=MARGIN,
                 rank_wrap=spec.get("rank_wrap"),
                 target_aspect=float(spec.get("target_aspect", 1.618)))

    rank        = lo.rank
    pos_in_rank = lo.pos_in_rank
    rank_groups = lo.rank_groups
    cx_map      = lo.cx
    cy_map      = lo.cy
    canvas_w    = lo.canvas_w
    canvas_h    = lo.canvas_h
    n_ranks     = lo.n_ranks
    flip        = lo.flip
    vertical    = lo.vertical
    all_ranks   = sorted(rank_groups)

    # ── 4. SVG rendering ───────────────────────────────────────────────────
    body: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{canvas_w:.0f}" height="{canvas_h:.0f}" '
        f'viewBox="0 0 {canvas_w:.0f} {canvas_h:.0f}">',
        "<defs>",
        f'<style>'
        f'text{{font-family:Arial,sans-serif;fill:{TEXT_COLOR}}}'
        f'.lbl{{font-size:{FONT_SIZE}px;text-anchor:middle}}'
        f'.edge-lbl{{font-size:{SMALL_FONT}px;fill:{LINE_COLOR};text-anchor:middle}}'
        f'</style>',
        "</defs>",
        f'<rect width="{canvas_w:.0f}" height="{canvas_h:.0f}" fill="#FFFFFF"/>',
    ]

    # Edges (drawn under nodes).
    def _endpoint(src_cx, src_cy, tgt_cx, tgt_cy, offset):
        """Point on circle perimeter toward target."""
        dx, dy = tgt_cx - src_cx, tgt_cy - src_cy
        d = math.hypot(dx, dy)
        if d < 1:
            return src_cx, src_cy
        return src_cx + dx / d * offset, src_cy + dy / d * offset

    for e in edges:
        s, t = e["from"], e["to"]
        if s not in cx_map or t not in cx_map:
            continue
        x1, y1 = _endpoint(cx_map[s], cy_map[s], cx_map[t], cy_map[t], R)
        x2, y2 = _endpoint(cx_map[t], cy_map[t], cx_map[s], cy_map[s], R)
        body.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{LINE_COLOR}" stroke-width="1.5"/>'
        )
        if e.get("label"):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            # Small offset perpendicular to line to avoid overlapping the line itself.
            dx, dy = x2 - x1, y2 - y1
            d = math.hypot(dx, dy) or 1
            nx, ny = -dy / d * 10, dx / d * 10
            body.append(
                f'<text class="edge-lbl" x="{mx + nx:.1f}" y="{my + ny:.1f}">'
                f'{escape(e["label"])}</text>'
            )

    # Boundary input edges (dashed).
    # Origin: the canvas edge NEAREST to the target node, so the line never
    # travels across the diagram and through other nodes.
    for bi in binputs:
        t = bi["to"]
        if t not in cx_map:
            continue
        tx, ty = cx_map[t], cy_map[t]
        if vertical:
            # Come from whichever horizontal edge (top or bottom) is closer.
            oy = 0 if ty <= canvas_h / 2 else canvas_h
            ox = tx
        else:
            ox = 0 if tx <= canvas_w / 2 else canvas_w
            oy = ty

        x2, y2 = _endpoint(tx, ty, ox, oy, R)
        body.append(
            f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{DASH_COLOR}" stroke-width="1.5" stroke-dasharray="6,4"/>'
        )
        if bi.get("label"):
            mx, my = (ox + x2) / 2, (oy + y2) / 2
            body.append(
                f'<text class="edge-lbl" x="{mx + 6:.1f}" y="{my:.1f}" '
                f'text-anchor="start">{escape(bi["label"])}</text>'
            )

    # Nodes — small filled circles with labels outside.
    for n in nids:
        cx, cy = cx_map[n], cy_map[n]
        label  = nodes[n].get("label", n) if isinstance(nodes.get(n), dict) else str(nodes.get(n, n))
        lines  = (label or n).replace("\\n", "\n").splitlines() or [n]
        lh     = FONT_SIZE + 3

        body.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R}" '
            f'fill="{DOT_COLOR}" stroke="{DOT_STROKE}" stroke-width="1.5"/>'
        )
        # Label below the circle (or above if near top edge).
        label_y = cy + R + FONT_SIZE + 2
        if label_y + len(lines) * lh > canvas_h - 4:
            label_y = cy - R - (len(lines) - 1) * lh - 4
        for li, line in enumerate(lines):
            body.append(
                f'<text class="lbl" x="{cx:.1f}" y="{label_y + li * lh:.1f}">'
                f'{escape(line)}</text>'
            )

    body.append("</svg>")
    svg = "\n".join(body) + "\n"

    # Position data for LLM.
    pos_data = {
        "direction": direction,
        "ranks": {str(r): grp for r, grp in sorted(rank_groups.items())},
        "nodes": {
            n: {
                "rank":             rank[n],
                "position_in_rank": pos_in_rank[n],
                "cx":               round(cx_map[n]),
                "cy":               round(cy_map[n]),
            }
            for n in nids
        },
    }
    return svg, pos_data


def graph_file(
    input_path: Path,
    output_path: Path | None = None,
    direction: str | None = None,
) -> tuple[Path, Path]:
    with input_path.open(encoding="utf-8") as fh:
        spec = json.load(fh)
    svg_text, pos_data = graph_from_spec(spec, direction)
    svg_path  = output_path or input_path.with_stem(input_path.stem + ".graph").with_suffix(".svg")
    json_path = svg_path.with_suffix(".json")
    svg_path.write_text(svg_text,                        encoding="utf-8")
    json_path.write_text(json.dumps(pos_data, indent=2) + "\n", encoding="utf-8")
    return svg_path, json_path
