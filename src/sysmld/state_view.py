"""
sysmld stm — deterministic state machine (StateView) layout and composition.

State machine connections reference state box elements directly — no port
elements are created.  The side and offset are stored in the connection
anchor, not in a separate port element.  This keeps state machine diagrams
clean: no port squares, just arrows between rounded state boxes.

Input format (stm.json):

{
  "diagram":     "my-stm",
  "kind":        "StateView",
  "name":        "My State Machine",
  "subject":     "myControl",
  "model_files": ["model.sysml"],
  "aliases":     { ... },
  "direction":   "left-right",     (left-right or top-down; default left-right)
  "default_w":   130,
  "default_h":   60,
    "states": {
    "id": {
      "label":     "Display Name",
      "model_ref": "alias-or-qname",
      "parent":    "parent-state-id",
      "composite": true,
      "concurrent": true,
      "region":    "region-id",
      "regions":   ["control", "health"],
      "initial":   true,
      "final":     true,
      "w": 140, "h": 64
    }
  },
  "transitions": [
    {"from": "a", "to": "b", "label": "event [guard] / action",
     "model_ref": "alias-or-qname"}
  ],
  "styles": { ... }
}
"""

from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from .layout import compute as _layout

# ── Layout constants ──────────────────────────────────────────────────────────
CANVAS_MARGIN   = 40
BND_PAD         = 50
DEFAULT_W       = 130
DEFAULT_H       = 60
INITIAL_SIZE    = 20
FINAL_SIZE      = 24
COL_GAP         = 80
RANK_GAP        = 120
BACK_ARC_STEP   = 28
BACK_ARC_MARGIN = 36
SELF_LOOP_H     = 28
CORNER_RADIUS   = 8    # all transition bends use this radius


def compose_stm(spec: dict[str, Any]) -> dict[str, Any]:
    direction   = spec.get("direction", "left-right")
    default_w   = int(spec.get("default_w", DEFAULT_W))
    default_h   = int(spec.get("default_h", DEFAULT_H))
    states_spec = spec.get("states", {})
    trans_spec  = spec.get("transitions", [])
    aliases     = spec.get("aliases", {})

    all_ids = list(states_spec.keys())
    children_by_parent: dict[str, list[str]] = defaultdict(list)
    for sid, state in states_spec.items():
        if state.get("parent"):
            children_by_parent[str(state["parent"])].append(sid)
    container_ids = {
        sid for sid, state in states_spec.items()
        if state.get("composite")
    }
    container_ids.update(children_by_parent)
    nested_initial_ids = {
        sid for sid, state in states_spec.items()
        if state.get("initial") and state.get("parent")
    }
    layout_ids = [
        sid for sid in all_ids
        if sid not in container_ids and sid not in nested_initial_ids
    ]

    def _container_depth(sid: str) -> int:
        depth = 0
        parent = states_spec.get(sid, {}).get("parent")
        seen = {sid}
        while parent and parent in states_spec and parent not in seen:
            depth += 1
            seen.add(str(parent))
            parent = states_spec[parent].get("parent")
        return depth

    def _container_entry_state(container_id: str) -> str | None:
        children = children_by_parent.get(container_id, [])
        for child in children:
            if child in nested_initial_ids:
                target = next(
                    (
                        transition["to"]
                        for transition in trans_spec
                        if transition["from"] == child
                        and transition["to"] in states_spec
                    ),
                    None,
                )
                if target:
                    return target
        for child in children:
            if child not in container_ids and child not in nested_initial_ids:
                return child
        return None

    def _layout_endpoint(sid: str) -> str | None:
        if sid in layout_ids:
            return sid
        if sid in container_ids:
            return _container_entry_state(sid)
        if sid in nested_initial_ids:
            return next(
                (
                    transition["to"]
                    for transition in trans_spec
                    if transition["from"] == sid
                    and transition["to"] in layout_ids
                ),
                None,
            )
        return None

    def sw(sid):
        d = states_spec[sid]
        if d.get("initial"): return INITIAL_SIZE
        if d.get("final"):   return FINAL_SIZE
        return int(d.get("w", default_w))

    def sh(sid):
        d = states_spec[sid]
        if d.get("initial"): return INITIAL_SIZE
        if d.get("final"):   return FINAL_SIZE
        return int(d.get("h", default_h))

    # ── Forward edge detection (BFS — avoids cycle-caused rank collapse) ──────
    in_deg: dict[str, int] = defaultdict(int)
    for t in trans_spec:
        src = _layout_endpoint(t["from"])
        tgt = _layout_endpoint(t["to"])
        if src in layout_ids and tgt in layout_ids and src != tgt:
            in_deg[tgt] += 1

    sources = [s for s in layout_ids if in_deg.get(s, 0) == 0]
    visited: set[str] = set(sources)
    q: deque[str] = deque(sources)
    fwd_set: set[tuple[str, str]] = set()
    while q:
        node = q.popleft()
        for t in trans_spec:
            src = _layout_endpoint(t["from"])
            tgt = _layout_endpoint(t["to"])
            if src != node:
                continue
            if tgt not in visited and tgt in layout_ids:
                visited.add(tgt)
                q.append(tgt)
                fwd_set.add((node, tgt))

    layout_edges = [{"from": f, "to": t} for f, t in fwd_set]

    # ── Sugiyama layout ───────────────────────────────────────────────────────
    vertical = direction in ("top-down", "bottom-up")
    avg_w = sum(sw(s) for s in layout_ids) / max(len(layout_ids), 1)
    avg_h = sum(sh(s) for s in layout_ids) / max(len(layout_ids), 1)
    lo = _layout(
        layout_ids, layout_edges, direction,
        col_gap  = COL_GAP  + (avg_w if vertical else avg_h),
        rank_gap = RANK_GAP + (avg_h if vertical else avg_w),
        margin   = CANVAS_MARGIN + BND_PAD + max(default_w, default_h) // 2,
    )
    cx_map, cy_map, rank = lo.cx, lo.cy, lo.rank

    # ── Element boxes ─────────────────────────────────────────────────────────
    boxes: dict[str, tuple[int, int, int, int]] = {
        sid: (round(cx_map[sid] - sw(sid) / 2),
              round(cy_map[sid] - sh(sid) / 2),
              sw(sid), sh(sid))
        for sid in layout_ids
    }
    for sid in all_ids:
        if sid not in nested_initial_ids:
            continue
        target = next(
            (transition["to"] for transition in trans_spec if transition["from"] == sid and transition["to"] in boxes),
            None,
        )
        if not target:
            continue
        tx, ty, tw, th = boxes[target]
        if vertical:
            x = round(tx + tw / 2 - sw(sid) / 2)
            y = round(ty - 35)
        else:
            x = round(tx - 35)
            y = round(ty + th / 2 - sh(sid) / 2)
        boxes[sid] = (x, y, sw(sid), sh(sid))
        cx_map[sid] = x + sw(sid) / 2
        cy_map[sid] = y + sh(sid) / 2
        rank[sid] = max(0, rank.get(target, 1) - 1)
    for container_id in sorted(container_ids, key=_container_depth, reverse=True):
        children = [sid for sid in children_by_parent.get(container_id, []) if sid in boxes]
        if not children:
            continue
        child_boxes = [boxes[sid] for sid in children]
        internal_back_count = _internal_backward_count(container_id, trans_spec, states_spec, rank)
        left = min(x for x, y, w, h in child_boxes) - 45
        top = min(y for x, y, w, h in child_boxes) - 70
        right = max(x + w for x, y, w, h in child_boxes) + 45
        bottom_pad = 45 + max(0, internal_back_count - 1) * BACK_ARC_STEP
        bottom = max(y + h for x, y, w, h in child_boxes) + bottom_pad
        boxes[container_id] = (round(left), round(top), round(right - left), round(bottom - top))
        cx_map[container_id] = (left + right) / 2
        cy_map[container_id] = (top + bottom) / 2
        rank[container_id] = min(rank.get(child, 0) for child in children)

    boxes, cx_map, cy_map = _separate_external_container_neighbors(
        boxes, cx_map, cy_map, states_spec, trans_spec, container_ids, vertical
    )

    # ── Count backward transitions for spacing ────────────────────────────────
    n_back = sum(
        1 for t in trans_spec
        if t["from"] in layout_ids and t["to"] in layout_ids
        and t["from"] != t["to"]
        and rank.get(t["from"], 0) > rank.get(t["to"], 0)
    )

    # ── Boundary from (possibly shifted) box positions ────────────────────────
    bx = min(x     for x, y, w, h in boxes.values()) - BND_PAD
    by = min(y     for x, y, w, h in boxes.values()) - BND_PAD
    bw = max(x + w for x, y, w, h in boxes.values()) - bx + BND_PAD
    bh = max(y + h for x, y, w, h in boxes.values()) - by + BND_PAD

    if n_back > 0 and vertical:
        bw += BACK_ARC_MARGIN + (n_back - 1) * BACK_ARC_STEP
    elif n_back > 0:
        bw += BACK_ARC_MARGIN + (n_back - 1) * BACK_ARC_STEP
        bh += BACK_ARC_MARGIN + (n_back - 1) * BACK_ARC_STEP

    canvas_w = bx + bw + CANVAS_MARGIN
    canvas_h = by + bh + CANVAS_MARGIN

    # ── Classify transitions ──────────────────────────────────────────────────
    forward_trans, backward_trans, self_trans, container_trans = [], [], [], []
    for t in trans_spec:
        src, tgt = t["from"], t["to"]
        if src not in boxes or tgt not in boxes:
            continue
        if src == tgt:
            self_trans.append(t)
        elif src in container_ids or tgt in container_ids:
            container_trans.append(t)
        elif rank.get(src, 0) <= rank.get(tgt, 0):
            forward_trans.append(t)
        else:
            backward_trans.append(t)

    # ── Face assignment (side + offset per connection end, no port elements) ──
    # Track how many connections use each face of each state.
    src_face_usage: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    tgt_face_usage: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))

    def _exit_side(src, tgt):
        if vertical:
            if cy_map[src] < cy_map[tgt]: return "bottom", "top"
            if cy_map[src] > cy_map[tgt]: return "top",    "bottom"
            return ("right", "left") if cx_map[src] < cx_map[tgt] else ("left", "right")
        else:
            if cx_map[src] < cx_map[tgt]: return "right", "left"
            if cx_map[src] > cx_map[tgt]: return "left",  "right"
            return ("bottom", "top") if cy_map[src] < cy_map[tgt] else ("top", "bottom")

    # First pass: collect face usage counts.
    fwd_faces: dict[int, tuple[str, str]] = {}  # index in forward_trans → (src_face, tgt_face)
    for i, t in enumerate(forward_trans):
        sf, tf = _exit_side(t["from"], t["to"])
        fwd_faces[i] = (sf, tf)
        src_face_usage[t["from"]][sf].append(i)
        tgt_face_usage[t["to"]][tf].append(i)

    # Second pass: compute offsets based on position in face list.
    conn_src_anchor: dict[int, tuple[str, float]] = {}
    conn_tgt_anchor: dict[int, tuple[str, float]] = {}
    for sid, faces in src_face_usage.items():
        for face, idxs in faces.items():
            n = len(idxs)
            for pos, i in enumerate(idxs):
                conn_src_anchor[i] = (face, round((pos + 1) / (n + 1), 4))
    for sid, faces in tgt_face_usage.items():
        for face, idxs in faces.items():
            n = len(idxs)
            for pos, i in enumerate(idxs):
                conn_tgt_anchor[i] = (face, round((pos + 1) / (n + 1), 4))

    # ── Anchor position from box ──────────────────────────────────────────────
    def _anchor_xy(sid, side, offset):
        x, y, w, h = boxes[sid]
        if side == "right":  return x + w, y + h * offset
        if side == "left":   return x,     y + h * offset
        if side == "top":    return x + w * offset, y
        return x + w * offset, y + h   # bottom

    # ── Forward connection waypoints (channel-based, non-overlapping) ─────────
    channels: dict[tuple[int, int], list[int]] = defaultdict(list)
    for i, t in enumerate(forward_trans):
        r0, r1 = rank.get(t["from"], 0), rank.get(t["to"], 0)
        channels[(min(r0, r1), max(r0, r1))].append(i)

    conn_waypoints: dict[int, list[dict]] = {}
    for (r_lo, r_hi), idxs in channels.items():
        lo_nodes = lo.rank_groups.get(r_lo, [])
        hi_nodes = lo.rank_groups.get(r_hi, [])
        if vertical:
            lo_edges = [boxes[n][1] + boxes[n][3] for n in lo_nodes if n in boxes]
            hi_edges = [boxes[n][1]               for n in hi_nodes if n in boxes]
        else:
            lo_edges = [boxes[n][0] + boxes[n][2] for n in lo_nodes if n in boxes]
            hi_edges = [boxes[n][0]               for n in hi_nodes if n in boxes]
        chan_lo = min(lo_edges + hi_edges, default=0)
        chan_hi = max(lo_edges + hi_edges, default=0)

        def _mid(i):
            sa, ta = conn_src_anchor.get(i, (fwd_faces[i][0], 0.5)), conn_tgt_anchor.get(i, (fwd_faces[i][1], 0.5))
            ax, ay = _anchor_xy(forward_trans[i]["from"], sa[0], sa[1])
            ex_, ey_ = _anchor_xy(forward_trans[i]["to"],   ta[0], ta[1])
            return (ax + ex_) / 2 if vertical else (ay + ey_) / 2

        sorted_idxs = sorted(idxs, key=_mid)
        n = len(sorted_idxs)
        step = max((chan_hi - chan_lo) / (n + 1), 20)

        for pos, i in enumerate(sorted_idxs):
            t = forward_trans[i]
            sa = conn_src_anchor.get(i, (fwd_faces[i][0], 0.5))
            ta = conn_tgt_anchor.get(i, (fwd_faces[i][1], 0.5))
            sf, so = sa[0], sa[1]
            tf, to_ = ta[0], ta[1]
            ax, ay = _anchor_xy(t["from"], sf, so)
            ex, ey = _anchor_xy(t["to"],   tf, to_)   # ex/ey avoids shadowing boundary bx/by
            if vertical and abs(ax - ex) < 2:
                conn_waypoints[i] = []
            elif not vertical and abs(ay - ey) < 2:
                conn_waypoints[i] = []
            else:
                track = chan_lo + step * (pos + 1)
                conn_waypoints[i] = (
                    [{"x": round(ax), "y": round(track)}, {"x": round(ex), "y": round(track)}]
                    if vertical else
                    [{"x": round(track), "y": round(ay)}, {"x": round(track), "y": round(ey)}]
                )

    # ── Assemble elements (no port elements) ──────────────────────────────────
    out_elems: list[dict] = []
    annotations: list[dict] = _region_annotations(states_spec, boxes, children_by_parent, container_ids)
    subject_raw = spec.get("subject")
    out_elems.append({
        "id": "boundary", "model_ref": subject_raw or "boundary",
        "symbol": "boundary",
        "layout": {"x": bx, "y": by, "width": bw, "height": bh, "z": 0},
        "compartments": {"attributes": False, "ports": False, "actions": False},
        "style": "boundary.system",
    })
    for sid in all_ids:
        if sid not in boxes:
            continue
        x, y, w, h = boxes[sid]
        d = states_spec[sid]
        sym = ("initial_state" if d.get("initial")
               else "final_state" if d.get("final")
               else "state_usage")
        elem: dict[str, Any] = {
            "id": sid, "symbol": sym,
            "layout": {"x": x, "y": y, "width": w, "height": h,
                       "z": (4 + _container_depth(sid)) if sid in container_ids else 10},
        }
        if sym == "state_usage" or d.get("model_ref"):
            elem["model_ref"] = d.get("model_ref", sid)
        if sym == "state_usage":
            elem["label"] = d.get("label", sid)
            elem["style"] = d.get(
                "style",
                "state.composite" if sid in container_ids else "state.default",
            )
        else:
            elem["style"] = sym
        out_elems.append(elem)

    # ── Assemble connections ───────────────────────────────────────────────────
    out_conns: list[dict] = []
    conn_id_counts: dict[str, int] = defaultdict(int)

    def _unique_conn_id(base: str) -> str:
        conn_id_counts[base] += 1
        if conn_id_counts[base] == 1:
            return base
        return f"{base}-{conn_id_counts[base]}"

    # Forward transitions — connect state boxes directly.
    for i, t in enumerate(forward_trans):
        sa = conn_src_anchor.get(i, (fwd_faces[i][0], 0.5))
        ta = conn_tgt_anchor.get(i, (fwd_faces[i][1], 0.5))
        sf, so = sa[0], sa[1]
        tf, to_ = ta[0], ta[1]
        wps = conn_waypoints.get(i, [])
        tid = _unique_conn_id(t.get("id", f"{t['from']}--{t['to']}"))
        out_conns.append({
            "id": tid, "model_ref": _transition_model_ref(t, tid, subject_raw),
            "source": {"element": t["from"], "anchor": {"side": sf, "offset": round(so, 4)}},
            "target": {"element": t["to"],   "anchor": {"side": tf, "offset": round(to_, 4)}},
            "route": {"kind": "orthogonal", "waypoints": wps},
            "labels": ([{"text": t["label"],
                          "position": {"segment": max(0, len(wps) - 1), "offset": 0.5,
                                       "placement": "centerline"}}]
                       if t.get("label") else []),
            "style": "transition",
        })

    container_pair_positions = _container_pair_positions(container_trans)
    for idx, t in enumerate(container_trans):
        tid = _unique_conn_id(t.get("id", f"{t['from']}--{t['to']}"))
        pair_pos, pair_count = container_pair_positions[idx]
        sf, so, tf, to_, wps = _container_transition_route(
            t["from"], t["to"], boxes, cx_map, cy_map, pair_pos, pair_count
        )
        out_conns.append({
            "id": tid, "model_ref": _transition_model_ref(t, tid, subject_raw),
            "source": {"element": t["from"], "anchor": {"side": sf, "offset": round(so, 4)}},
            "target": {"element": t["to"],   "anchor": {"side": tf, "offset": round(to_, 4)}},
            "route": {"kind": "orthogonal", "waypoints": wps},
            "labels": ([{"text": t["label"],
                          "position": {"segment": max(0, len(wps) - 1), "offset": 0.5,
                                       "placement": "centerline"}}]
                       if t.get("label") else []),
            "style": "transition",
        })

    # Backward transitions — arc above (left-right) or to the right (top-down).
    # Sort shortest rank-span first so the shortest arcs sit closest to the diagram.
    backward_sorted = sorted(
        backward_trans,
        key=lambda t: abs(rank.get(t["from"], 0) - rank.get(t["to"], 0))
    )

    # Spread source offsets: group backward arcs by their source cx so that arcs
    # from states at the SAME x position exit at different horizontal positions
    # and their vertical segments never overlap.
    back_src_by_cx: dict[int, list[int]] = defaultdict(list)
    for idx, t in enumerate(backward_sorted):
        back_src_by_cx[round(cx_map[t["from"]])].append(idx)
    back_src_offset: dict[int, float] = {}
    for cx_val, idxs in back_src_by_cx.items():
        n = len(idxs)
        for pos, idx in enumerate(idxs):
            back_src_offset[idx] = round((pos + 1) / (n + 1), 4)

    # Spread target offsets: group backward arcs by their target cx so that arcs
    # arriving at the SAME state enter at different horizontal positions and their
    # vertical descent segments never overlap.
    back_tgt_by_cx: dict[int, list[int]] = defaultdict(list)
    for idx, t in enumerate(backward_sorted):
        back_tgt_by_cx[round(cx_map[t["to"]])].append(idx)
    back_tgt_offset: dict[int, float] = {}
    for cx_val, idxs in back_tgt_by_cx.items():
        n = len(idxs)
        for pos, idx in enumerate(idxs):
            back_tgt_offset[idx] = round((pos + 1) / (n + 1), 4)

    def _local_backward_mode(t):
        src, tgt = t["from"], t["to"]
        rank_delta = rank.get(src, 0) - rank.get(tgt, 0)
        if rank_delta < 1:
            return None
        sx, sy, sw_, sh_ = boxes[src]
        tx, ty, tw_, th_ = boxes[tgt]
        if vertical:
            if not _ranges_overlap(sx, sx + sw_, tx, tx + tw_):
                return None
            return "right" if sy > ty and not _has_intermediate_box(src, tgt, vertical=True) else None
        if not _ranges_overlap(sy, sy + sh_, ty, ty + th_):
            if sy + sh_ <= ty:
                return "over_top" if sx > tx and rank_delta == 1 else None
            if ty + th_ <= sy:
                return "under_bottom" if sx > tx and rank_delta == 1 else None
            return None
        if sx <= tx:
            return None
        if rank_delta > 1 and states_spec[src].get("parent") == states_spec[tgt].get("parent"):
            return "top_span"
        if rank_delta > 1:
            return "bottom_span"
        if _has_intermediate_box(src, tgt, vertical=False):
            return None
        return "bottom"

    def _ranges_overlap(a0, a1, b0, b1):
        return max(a0, b0) < min(a1, b1)

    def _has_intermediate_box(src, tgt, vertical):
        sx, sy, sw_, sh_ = boxes[src]
        tx, ty, tw_, th_ = boxes[tgt]
        if vertical:
            low, high = sorted((ty + th_, sy))
            cross_lo = min(sx, tx) - BACK_ARC_MARGIN
            cross_hi = max(sx + sw_, tx + tw_) + BACK_ARC_MARGIN
            for sid, (x, y, w, h) in boxes.items():
                if sid in (src, tgt) or sid in container_ids:
                    continue
                if y < high and y + h > low and x < cross_hi and x + w > cross_lo:
                    return True
            return False
        low, high = sorted((tx + tw_, sx))
        cross_lo = min(sy, ty) - BACK_ARC_MARGIN
        cross_hi = max(sy + sh_, ty + th_) + BACK_ARC_MARGIN
        for sid, (x, y, w, h) in boxes.items():
            if sid in (src, tgt) or sid in container_ids:
                continue
            if x < high and x + w > low and y < cross_hi and y + h > cross_lo:
                return True
        return False

    local_back: dict[tuple[str, str], list[tuple[int, dict[str, Any], str]]] = defaultdict(list)
    global_back: list[tuple[int, dict[str, Any]]] = []
    for idx, t in enumerate(backward_sorted):
        mode = _local_backward_mode(t)
        if mode:
            local_back[(t["from"], t["to"])].append((idx, t, mode))
        else:
            global_back.append((idx, t))

    max_local_rows = max((len(members) for members in local_back.values()), default=0)
    local_bottom_targets = {
        t["to"]
        for members in local_back.values()
        for _idx, t, mode in members
        if mode == "bottom"
    }
    top_face_usage: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for members in local_back.values():
        for idx, t, mode in members:
            uses_top = (
                not vertical
                and (
                    mode in ("over_top", "top_span")
                    or (mode == "bottom" and t["from"] in local_bottom_targets)
                )
            )
            if uses_top:
                top_face_usage[t["from"]].append((idx, "src"))
                top_face_usage[t["to"]].append((idx, "tgt"))
    top_endpoint_offset: dict[tuple[int, str], float] = {}
    for endpoints in top_face_usage.values():
        endpoints.sort()
        n = len(endpoints)
        for pos, endpoint in enumerate(endpoints):
            top_endpoint_offset[endpoint] = round((pos + 1) / (n + 1), 4)
    bottom_face_usage: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for members in local_back.values():
        for idx, t, mode in members:
            uses_bottom = (
                not vertical
                and mode in ("bottom", "bottom_span")
                and not (mode == "bottom" and t["from"] in local_bottom_targets)
            )
            if uses_bottom:
                bottom_face_usage[t["from"]].append((idx, "src"))
                bottom_face_usage[t["to"]].append((idx, "tgt"))
    bottom_endpoint_offset: dict[tuple[int, str], float] = {}
    for endpoints in bottom_face_usage.values():
        endpoints.sort()
        n = len(endpoints)
        for pos, endpoint in enumerate(endpoints):
            bottom_endpoint_offset[endpoint] = round((pos + 1) / (n + 1), 4)

    top_lane = 0
    bottom_lane = 0
    for members in local_back.values():
        n = len(members)
        for pos, (idx, t, mode) in enumerate(members):
            tid = _unique_conn_id(t.get("id", f"{t['from']}-back-{t['to']}"))
            soff = round((pos + 1) / (n + 1), 4)
            toff = round((n - pos) / (n + 1), 4)
            if vertical:
                src_right = boxes[t["from"]][0] + boxes[t["from"]][2]
                tgt_right = boxes[t["to"]][0] + boxes[t["to"]][2]
                local_x = max(src_right, tgt_right) + SELF_LOOP_H + pos * BACK_ARC_STEP
                source_y = round(_anchor_xy(t["from"], "right", soff)[1])
                target_y = round(_anchor_xy(t["to"], "right", toff)[1])
                wps = [
                    {"x": round(local_x), "y": source_y},
                    {"x": round(local_x), "y": target_y},
                ]
                _append_back(out_conns, t, tid, subject_raw, t["from"], t["to"],
                             "right", soff, "right", toff, wps)
            elif mode in ("bottom", "bottom_span") and not (mode == "bottom" and t["from"] in local_bottom_targets):
                src_bottom = boxes[t["from"]][1] + boxes[t["from"]][3]
                tgt_bottom = boxes[t["to"]][1] + boxes[t["to"]][3]
                local_y = max(src_bottom, tgt_bottom) + SELF_LOOP_H + bottom_lane * BACK_ARC_STEP
                bottom_lane += 1
                if mode == "bottom_span":
                    soff = bottom_endpoint_offset.get((idx, "src"), soff)
                    toff = bottom_endpoint_offset.get((idx, "tgt"), toff)
                source_x = round(_anchor_xy(t["from"], "bottom", soff)[0])
                target_x = round(_anchor_xy(t["to"], "bottom", toff)[0])
                wps = [
                    {"x": source_x, "y": round(local_y)},
                    {"x": target_x, "y": round(local_y)},
                ]
                _append_back(out_conns, t, tid, subject_raw, t["from"], t["to"],
                             "bottom", soff, "bottom", toff, wps)
            else:
                src_box = boxes[t["from"]]
                tgt_box = boxes[t["to"]]
                if mode in ("over_top", "top_span", "bottom"):
                    local_y = min(src_box[1], tgt_box[1]) - SELF_LOOP_H - top_lane * BACK_ARC_STEP
                    top_lane += 1
                    src_face, tgt_face = "top", "top"
                    soff = top_endpoint_offset.get((idx, "src"), soff)
                    toff = top_endpoint_offset.get((idx, "tgt"), toff)
                else:
                    local_y = max(src_box[1] + src_box[3], tgt_box[1] + tgt_box[3]) + SELF_LOOP_H + pos * BACK_ARC_STEP
                    src_face, tgt_face = "bottom", "bottom"
                source_x = round(_anchor_xy(t["from"], src_face, soff)[0])
                target_x = round(_anchor_xy(t["to"], tgt_face, toff)[0])
                wps = [
                    {"x": source_x, "y": round(local_y)},
                    {"x": target_x, "y": round(local_y)},
                ]
                _append_back(out_conns, t, tid, subject_raw, t["from"], t["to"],
                             src_face, soff, tgt_face, toff, wps)

    local_back_targets = {tgt for _src, tgt in local_back}

    if vertical:
        arc_base = bx + bw + BACK_ARC_MARGIN + max_local_rows * BACK_ARC_STEP
        for lane, (idx, t) in enumerate(global_back):
            tid = _unique_conn_id(t.get("id", f"{t['from']}-back-{t['to']}"))
            soff = back_src_offset.get(idx, 0.5)
            toff = back_tgt_offset.get(idx, 0.5)
            arc_x = arc_base + lane * BACK_ARC_STEP
            wps = [{"x": round(arc_x), "y": round(_anchor_xy(t["from"], "right", soff)[1])},
                   {"x": round(arc_x), "y": round(_anchor_xy(t["to"],   "right", toff)[1])}]
            _append_back(out_conns, t, tid, subject_raw, t["from"], t["to"],
                         "right", soff, "right", toff, wps)
    else:
        max_box_bottom = max(y + h for x, y, w, h in boxes.values())
        arc_base = max_box_bottom + BACK_ARC_MARGIN + max_local_rows * BACK_ARC_STEP
        right_lane_base = max(x + w for x, y, w, h in boxes.values()) + BACK_ARC_MARGIN
        target_order = []
        for idx, t in global_back:
            toff = back_tgt_offset.get(idx, 0.5)
            target_order.append((round(_anchor_xy(t["to"], "bottom", toff)[0]), idx))
        target_order.sort()
        track_index = {
            idx: len(target_order) - position - 1
            for position, (_x, idx) in enumerate(target_order)
        }
        source_order = []
        for idx, t in global_back:
            soff = back_src_offset.get(idx, 0.5)
            source_order.append((round(_anchor_xy(t["from"], "right", soff)[1]), idx))
        source_order.sort()
        lane_index = {
            idx: len(source_order) - position - 1
            for position, (_y, idx) in enumerate(source_order)
        }
        global_local_target_counts: dict[str, int] = defaultdict(int)
        for fallback, (idx, t) in enumerate(global_back):
            tid = _unique_conn_id(t.get("id", f"{t['from']}-back-{t['to']}"))
            soff = back_src_offset.get(idx, 0.5)
            toff = back_tgt_offset.get(idx, 0.5)
            if t["to"] in local_back_targets:
                count = global_local_target_counts[t["to"]]
                toff = min(0.45, 0.2 + count * 0.15)
                global_local_target_counts[t["to"]] += 1
            track = track_index.get(idx, fallback)
            arc_y = arc_base + track * BACK_ARC_STEP
            source_y = round(_anchor_xy(t["from"], "right", soff)[1])
            right_lane = round(right_lane_base + lane_index.get(idx, fallback) * BACK_ARC_STEP)
            target_x = round(_anchor_xy(t["to"], "bottom", toff)[0])
            wps = [
                {"x": right_lane, "y": source_y},
                {"x": right_lane, "y": round(arc_y)},
                {"x": target_x, "y": round(arc_y)},
            ]
            _append_back(out_conns, t, tid, subject_raw, t["from"], t["to"],
                         "right", soff, "bottom", toff, wps)

    # Self-loops — small rectangular notch above the state.
    for t in self_trans:
        src = t["from"]
        tid = _unique_conn_id(t.get("id", f"{src}-self"))
        x, y, w, h = boxes[src]
        loop_y = y - SELF_LOOP_H
        out_conns.append({
            "id": tid, "model_ref": _transition_model_ref(t, tid, subject_raw),
            "source": {"element": src, "anchor": {"side": "top", "offset": 0.3}},
            "target": {"element": src, "anchor": {"side": "top", "offset": 0.7}},
            "route": {"kind": "orthogonal", "waypoints": [
                {"x": round(x + w * 0.3), "y": round(loop_y)},
                {"x": round(x + w * 0.7), "y": round(loop_y)},
            ]},
            "labels": ([{"text": t["label"],
                          "position": {"segment": 1, "offset": 0.5,
                                       "placement": "centerline"}}]
                       if t.get("label") else []),
            "style": "transition",
        })

    # ── Final document ────────────────────────────────────────────────────────
    diagram_id = spec.get("diagram", "state-machine")
    doc: dict[str, Any] = {
        "$schema": "../../schemas/sysmld.schema.json",
        "version": "0.1",
        "mode": "model_based",
        "model_files": spec.get("model_files", []),
        "aliases": aliases,
        "diagram": {
            "id":   diagram_id,
            "kind": spec.get("kind", "StateView"),
            "name": spec.get("name", diagram_id),
            "canvas": {"width": round(canvas_w), "height": round(canvas_h),
                       "background": "#FFFFFF"},
            "frame":       {"visible": True},
            "elements":    out_elems,
            "connections": out_conns,
            "annotations": annotations,
            "styles":      _default_stm_styles(spec.get("styles", {})),
        },
    }
    if subject_raw:
        doc["diagram"]["subject"] = subject_raw
    return doc


def _append_back(out_conns, t, tid, subject_raw, src, tgt,
                  src_face, src_off, tgt_face, tgt_off, wps):
    label_segment = 2 if len(wps) >= 3 else 1
    out_conns.append({
        "id": tid, "model_ref": _transition_model_ref(t, tid, subject_raw),
        "source": {"element": src, "anchor": {"side": src_face, "offset": src_off}},
        "target": {"element": tgt, "anchor": {"side": tgt_face, "offset": tgt_off}},
        "route": {"kind": "orthogonal", "waypoints": wps},
        "labels": ([{"text": t["label"],
                      "position": {"segment": label_segment, "offset": 0.5,
                                   "placement": "centerline"}}]
                   if t.get("label") else []),
        "style": "transition",
    })


def _internal_backward_count(
    container_id: str,
    transitions: list[dict[str, Any]],
    states_spec: dict[str, Any],
    rank: dict[str, int],
) -> int:
    return sum(
        1 for transition in transitions
        if _same_container_scope(transition["from"], transition["to"], container_id, states_spec)
        and transition["from"] != transition["to"]
        and rank.get(transition["from"], 0) > rank.get(transition["to"], 0)
    )


def _separate_external_container_neighbors(
    boxes: dict[str, tuple[int, int, int, int]],
    cx_map: dict[str, float],
    cy_map: dict[str, float],
    states_spec: dict[str, Any],
    transitions: list[dict[str, Any]],
    container_ids: set[str],
    vertical: bool,
) -> tuple[dict[str, tuple[int, int, int, int]], dict[str, float], dict[str, float]]:
    min_gap = BND_PAD

    def _outside(state_id: str, container_id: str) -> bool:
        return state_id != container_id and not _is_descendant_of(state_id, container_id, states_spec)

    def _shift(state_id: str, delta: int):
        x, y, w, h = boxes[state_id]
        if vertical:
            boxes[state_id] = (x, y + delta, w, h)
            cy_map[state_id] = cy_map[state_id] + delta
        else:
            boxes[state_id] = (x + delta, y, w, h)
            cx_map[state_id] = cx_map[state_id] + delta

    changed = True
    while changed:
        changed = False
        for transition in transitions:
            for container_id, peer_id in _container_peer_pairs(transition, container_ids):
                if container_id not in boxes or peer_id not in boxes or not _outside(peer_id, container_id):
                    continue
                cx, cy, cw, ch = boxes[container_id]
                px, py, pw, ph = boxes[peer_id]
                if vertical:
                    if py + ph <= cy:
                        gap = cy - (py + ph)
                        if gap < min_gap:
                            _shift(peer_id, -(min_gap - gap))
                            changed = True
                    elif cy + ch <= py:
                        gap = py - (cy + ch)
                        if gap < min_gap:
                            _shift(peer_id, min_gap - gap)
                            changed = True
                else:
                    if px + pw <= cx:
                        gap = cx - (px + pw)
                        if gap < min_gap:
                            _shift(peer_id, -(min_gap - gap))
                            changed = True
                    elif cx + cw <= px:
                        gap = px - (cx + cw)
                        if gap < min_gap:
                            _shift(peer_id, min_gap - gap)
                            changed = True
    return boxes, cx_map, cy_map


def _container_peer_pairs(transition: dict[str, Any], container_ids: set[str]) -> list[tuple[str, str]]:
    pairs = []
    src = transition["from"]
    tgt = transition["to"]
    if src in container_ids and tgt not in container_ids:
        pairs.append((src, tgt))
    if tgt in container_ids and src not in container_ids:
        pairs.append((tgt, src))
    return pairs


def _same_container_scope(src: str, tgt: str, container_id: str, states_spec: dict[str, Any]) -> bool:
    return (
        _is_descendant_of(src, container_id, states_spec)
        and _is_descendant_of(tgt, container_id, states_spec)
    )


def _is_descendant_of(sid: str, container_id: str, states_spec: dict[str, Any]) -> bool:
    parent = states_spec.get(sid, {}).get("parent")
    seen = {sid}
    while parent and parent in states_spec and parent not in seen:
        if parent == container_id:
            return True
        seen.add(str(parent))
        parent = states_spec[parent].get("parent")
    return False


def _container_pair_positions(container_trans: list[dict[str, Any]]) -> dict[int, tuple[int, int]]:
    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for idx, transition in enumerate(container_trans):
        groups[tuple(sorted((transition["from"], transition["to"])))].append(idx)
    positions: dict[int, tuple[int, int]] = {}
    for idxs in groups.values():
        for pos, idx in enumerate(idxs):
            positions[idx] = (pos, len(idxs))
    return positions


def _container_transition_route(src: str, tgt: str, boxes, cx_map, cy_map, pair_pos: int = 0, pair_count: int = 1):
    sx, sy, sw, sh = boxes[src]
    tx, ty, tw, th = boxes[tgt]
    src_cx, src_cy = cx_map[src], cy_map[src]
    tgt_cx, tgt_cy = cx_map[tgt], cy_map[tgt]
    if abs(src_cx - tgt_cx) >= abs(src_cy - tgt_cy):
        src_side, tgt_side = ("left", "right") if src_cx >= tgt_cx else ("right", "left")
        overlap_top = max(sy, ty)
        overlap_bottom = min(sy + sh, ty + th)
        if overlap_bottom - overlap_top > 20:
            y = overlap_top + ((pair_pos + 1) / (pair_count + 1)) * (overlap_bottom - overlap_top)
            return src_side, (y - sy) / sh, tgt_side, (y - ty) / th, []
        y = min(max(tgt_cy, sy + 12), sy + sh - 12)
        mid_x = (sx if src_side == "left" else sx + sw) + ((tx + tw if tgt_side == "right" else tx) - (sx if src_side == "left" else sx + sw)) / 2
        return src_side, (y - sy) / sh, tgt_side, min(max((y - ty) / th, 0.1), 0.9), [{"x": round(mid_x), "y": round(y)}]
    if src_cy >= tgt_cy:
        src_side, tgt_side = "top", "bottom"
        overlap_left = max(sx, tx)
        overlap_right = min(sx + sw, tx + tw)
        if overlap_right - overlap_left > 20:
            x = overlap_left + ((pair_pos + 1) / (pair_count + 1)) * (overlap_right - overlap_left)
            return src_side, (x - sx) / sw, tgt_side, (x - tx) / tw, []
        x = min(max(tgt_cx, sx + 12), sx + sw - 12)
        return src_side, (x - sx) / sw, tgt_side, (x - tx) / tw, []
    src_side, tgt_side = "bottom", "top"
    overlap_left = max(sx, tx)
    overlap_right = min(sx + sw, tx + tw)
    if overlap_right - overlap_left > 20:
        x = overlap_left + ((pair_pos + 1) / (pair_count + 1)) * (overlap_right - overlap_left)
        return src_side, (x - sx) / sw, tgt_side, (x - tx) / tw, []
    x = min(max(tgt_cx, sx + 12), sx + sw - 12)
    return src_side, (x - sx) / sw, tgt_side, (x - tx) / tw, []


def _region_annotations(
    states_spec: dict[str, Any],
    boxes: dict[str, tuple[int, int, int, int]],
    children_by_parent: dict[str, list[str]],
    container_ids: set[str],
) -> list[dict[str, Any]]:
    annotations: list[dict[str, Any]] = []
    for container_id in sorted(container_ids):
        state = states_spec.get(container_id, {})
        if not state.get("concurrent") and not state.get("regions"):
            continue
        if container_id not in boxes:
            continue
        regions = _ordered_regions(state, children_by_parent.get(container_id, []), states_spec)
        if len(regions) < 2:
            continue
        region_children = {
            region_id: [
                sid for sid in children_by_parent.get(container_id, [])
                if states_spec.get(sid, {}).get("region") == region_id and sid in boxes
            ]
            for region_id, _label in regions
        }
        if not all(region_children.values()):
            continue

        cx, cy, cw, ch = boxes[container_id]
        spread_x = _region_spread(region_children, boxes, axis="x")
        spread_y = _region_spread(region_children, boxes, axis="y")
        orientation = "vertical" if spread_x >= spread_y else "horizontal"
        ordered = sorted(
            regions,
            key=lambda region: _region_center(region_children[region[0]], boxes, axis="x" if orientation == "vertical" else "y"),
        )
        for pos, ((left_id, _left_label), (right_id, right_label)) in enumerate(zip(ordered, ordered[1:]), start=1):
            if orientation == "vertical":
                divider = round((
                    _region_edge(region_children[left_id], boxes, high=True, axis="x")
                    + _region_edge(region_children[right_id], boxes, high=False, axis="x")
                ) / 2)
                annotations.append({
                    "id": f"{container_id}-region-divider-{pos}",
                    "type": "state_region_divider",
                    "x1": divider,
                    "y1": cy + 36,
                    "x2": divider,
                    "y2": cy + ch - 12,
                    "label": right_label,
                    "label_x": divider + 8,
                    "label_y": cy + 52,
                })
            else:
                divider = round((
                    _region_edge(region_children[left_id], boxes, high=True, axis="y")
                    + _region_edge(region_children[right_id], boxes, high=False, axis="y")
                ) / 2)
                annotations.append({
                    "id": f"{container_id}-region-divider-{pos}",
                    "type": "state_region_divider",
                    "x1": cx + 12,
                    "y1": divider,
                    "x2": cx + cw - 12,
                    "y2": divider,
                    "label": right_label,
                    "label_x": cx + 18,
                    "label_y": divider + 16,
                })
    return annotations


def _ordered_regions(state: dict[str, Any], children: list[str], states_spec: dict[str, Any]) -> list[tuple[str, str]]:
    raw_regions = state.get("regions") or []
    regions: list[tuple[str, str]] = []
    for raw in raw_regions:
        if isinstance(raw, dict):
            region_id = str(raw.get("id", raw.get("label", "")))
            label = str(raw.get("label", region_id))
        else:
            region_id = str(raw)
            label = region_id
        if region_id:
            regions.append((region_id, label))
    for child in children:
        region_id = states_spec.get(child, {}).get("region")
        if region_id and not any(existing == region_id for existing, _label in regions):
            regions.append((str(region_id), str(region_id)))
    return regions


def _region_spread(region_children: dict[str, list[str]], boxes: dict[str, tuple[int, int, int, int]], axis: str) -> float:
    centers = [_region_center(children, boxes, axis) for children in region_children.values() if children]
    return max(centers) - min(centers) if centers else 0


def _region_center(children: list[str], boxes: dict[str, tuple[int, int, int, int]], axis: str) -> float:
    if axis == "x":
        values = [boxes[sid][0] + boxes[sid][2] / 2 for sid in children]
    else:
        values = [boxes[sid][1] + boxes[sid][3] / 2 for sid in children]
    return sum(values) / max(len(values), 1)


def _region_edge(children: list[str], boxes: dict[str, tuple[int, int, int, int]], high: bool, axis: str) -> float:
    if axis == "x":
        values = [boxes[sid][0] + (boxes[sid][2] if high else 0) for sid in children]
    else:
        values = [boxes[sid][1] + (boxes[sid][3] if high else 0) for sid in children]
    return max(values) if high else min(values)


def _transition_model_ref(t: dict[str, Any], tid: str, subject_raw: str | None) -> str:
    return t.get("model_ref") or subject_raw or tid


def _default_stm_styles(user_styles: dict) -> dict:
    defaults = {
        "boundary.system": {"fill": "#FFFFFF",  "stroke": "#334155",
                            "stroke_width": 2, "corner_radius": 12},
        "state.default":   {"fill": "#EFF6FF",  "stroke": "#1D4ED8",
                            "stroke_width": 2, "corner_radius": 16},
        "initial_state":   {"fill": "#1E293B",  "stroke": "#1E293B",  "stroke_width": 1},
        "final_state":     {"fill": "#1E293B",  "stroke": "#1E293B",  "stroke_width": 2},
        "transition":      {"stroke": "#1D4ED8", "stroke_width": 1.5,
                            "corner_radius": CORNER_RADIUS, "marker_end": "arrow"},
        "state.composite": {"fill": "#EFF6FF", "stroke": "#1D4ED8",
                            "stroke_width": 2, "corner_radius": 16,
                            "label_position": "top", "container": True},
    }
    defaults.update(user_styles)
    return defaults


def stm_file(input_path: Path, output_path: Path | None = None) -> Path:
    with input_path.open(encoding="utf-8") as fh:
        spec = json.load(fh)
    result = compose_stm(spec)
    target = output_path or input_path.with_suffix(".sysmld")
    with target.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")
    return target
