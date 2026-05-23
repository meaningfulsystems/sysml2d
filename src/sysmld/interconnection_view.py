"""
sysmld compose — generate a complete .sysmld from a layout intent file.

Uses the same Sugiyama layout engine as `sysmld graph`, so the node
ordering and rank positions always match the topology SVG.

Input format (intent.json):

{
  "diagram":     "my-diagram-id",
  "kind":        "InterconnectionView",
  "name":        "Human-Readable Name",
  "subject":     "alias-or-qname",          (optional)
  "model_files": ["model.sysml"],
  "aliases":     { ... },                   (optional, passed through)
  "direction":   "top-down",               (top-down | bottom-up | left-right | right-left)
  "default_w":   160,
  "default_h":   80,
  "col_gap":     60,                        (gap between boxes in same rank)
  "rank_gap":    160,                       (gap between ranks)
  "nodes": {
    "id": { "label": "...", "style": "part.mechanical", "w": 200, "h": 90 }
  },
  "edges": [
    { "from": "a", "to": "b", "label": "signal", "style": "connector.signal" }
  ],
  "boundary_inputs": [
    { "to": "a", "label": "user input" }
  ],
  "styles": { ... }
}
"""

from __future__ import annotations

import json
from itertools import permutations
from collections import defaultdict
from pathlib import Path
from typing import Any

from .layout import compute as _layout
from .layout import _segments_cross

OPP = {"top": "bottom", "bottom": "top", "left": "right", "right": "left"}

# Canvas margin around the boundary box.
CANVAS_MARGIN = 40
# Padding from boundary wall to nearest element centre.
BND_PAD = 60
# Minimum free space between a routed line and an element box.
ROUTE_CLEARANCE = 24
# Minimum distance between parallel channel tracks.
TRACK_GAP = 28
# Distance a side-mounted route steps away from its element before turning.
PORT_STUB = 28


def compose(spec: dict[str, Any]) -> dict[str, Any]:
    direction = spec.get("direction", "top-down")
    dw        = int(spec.get("default_w", 160))
    dh        = int(spec.get("default_h", 80))
    # Gap between box edges (not centres) within a rank and between ranks.
    col_gap   = int(spec.get("col_gap",  60))
    rank_gap  = int(spec.get("rank_gap", 160))
    route_clearance = int(spec.get("route_clearance", ROUTE_CLEARANCE))
    track_gap = int(spec.get("track_gap", TRACK_GAP))
    port_stub = int(spec.get("port_stub", PORT_STUB))
    rank_wrap = spec.get("rank_wrap")
    target_aspect = float(spec.get("target_aspect", 1.618))
    nodes     = spec.get("nodes", {})
    edges     = spec.get("edges", [])
    binputs   = spec.get("boundary_inputs", [])
    label_mode = spec.get("label_mode", "connection")
    nids      = list(nodes.keys())

    def nw(n): return max(int(nodes[n].get("w", dw)), _label_width(str(nodes[n].get("label", n))))
    def nh(n): return max(int(nodes[n].get("h", dh)), _label_height(str(nodes[n].get("label", n))))

    # ── layout via shared engine ───────────────────────────────────────────
    # col_gap and rank_gap here are centre-to-centre distances, so add the
    # average box dimension to convert from edge-gap to centre-gap.
    avg_w = sum(nw(n) for n in nids) / max(len(nids), 1)
    avg_h = sum(nh(n) for n in nids) / max(len(nids), 1)
    lo = _layout(
        nids, edges, direction,
        col_gap  = col_gap  + (avg_w if lo_vertical(direction) else avg_h),
        rank_gap = rank_gap + (avg_h if lo_vertical(direction) else avg_w),
        margin   = CANVAS_MARGIN + BND_PAD + max(dw, dh) // 2,
        rank_wrap=rank_wrap,
        target_aspect=target_aspect,
    )
    max_channel = _max_adjacent_channel_members(edges, lo.rank)
    if rank_wrap:
        min_rank_gap = (2 * route_clearance) + (2 * track_gap)
    else:
        min_rank_gap = (2 * route_clearance) + ((max_channel + 1) * track_gap)
    if rank_gap < min_rank_gap:
        rank_gap = min_rank_gap
        lo = _layout(
            nids, edges, direction,
            col_gap  = col_gap  + (avg_w if lo_vertical(direction) else avg_h),
            rank_gap = rank_gap + (avg_h if lo_vertical(direction) else avg_w),
            margin   = CANVAS_MARGIN + BND_PAD + max(dw, dh) // 2,
            rank_wrap=rank_wrap,
            target_aspect=target_aspect,
        )

    rank_groups = lo.rank_groups
    cx_map      = lo.cx
    cy_map      = lo.cy
    vertical    = lo.vertical

    # ── element bounding boxes ────────────────────────────────────────────
    boxes: dict[str, tuple[int, int, int, int]] = {}
    for n in nids:
        w, h  = nw(n), nh(n)
        boxes[n] = (round(cx_map[n] - w/2), round(cy_map[n] - h/2), w, h)

    # ── boundary size ─────────────────────────────────────────────────────
    all_x  = [x        for x, y, w, h in boxes.values()]
    all_y  = [y        for x, y, w, h in boxes.values()]
    all_x2 = [x + w    for x, y, w, h in boxes.values()]
    all_y2 = [y + h    for x, y, w, h in boxes.values()]

    bx = min(all_x)  - BND_PAD
    by = min(all_y)  - BND_PAD
    bw = max(all_x2) - bx + BND_PAD
    bh = max(all_y2) - by + BND_PAD

    canvas_w = bx + bw + CANVAS_MARGIN
    canvas_h = by + bh + CANVAS_MARGIN

    # ── port assignment ───────────────────────────────────────────────────
    edge_degree: dict[str, int] = defaultdict(int)
    for e in edges:
        if e.get("from") in boxes and e.get("to") in boxes:
            edge_degree[e["from"]] += 1
            edge_degree[e["to"]] += 1

    def open_horizontal_face(nid: str) -> str:
        left_clear = horizontal_clearance(nid, "left")
        right_clear = horizontal_clearance(nid, "right")
        return "right" if right_clear >= left_clear else "left"

    def horizontal_clearance(nid: str, side: str) -> float:
        x, y, w, h = boxes[nid]
        left_limit = bx
        right_limit = bx + bw
        for other, (ox, oy, ow, oh) in boxes.items():
            if other == nid or not _ranges_overlap(y, y + h, oy, oy + oh):
                continue
            if ox + ow <= x:
                left_limit = max(left_limit, ox + ow)
            elif ox >= x + w:
                right_limit = min(right_limit, ox)
        left_clear = x - left_limit
        right_clear = right_limit - (x + w)
        return right_clear if side == "right" else left_clear

    def horizontal_face_toward(nid: str, peer: str) -> str:
        nx, _ny = _box_center(boxes[nid])
        px, _py = _box_center(boxes[peer])
        toward = "right" if px >= nx else "left"
        if horizontal_clearance(nid, toward) >= port_stub * 2:
            return toward
        return open_horizontal_face(nid)

    def open_vertical_face(nid: str) -> str:
        x, y, w, h = boxes[nid]
        top_limit = by
        bottom_limit = by + bh
        for other, (ox, oy, ow, oh) in boxes.items():
            if other == nid or not _ranges_overlap(x, x + w, ox, ox + ow):
                continue
            if oy + oh <= y:
                top_limit = max(top_limit, oy + oh)
            elif oy >= y + h:
                bottom_limit = min(bottom_limit, oy)
        top_clear = y - top_limit
        bottom_clear = bottom_limit - (y + h)
        return "bottom" if bottom_clear >= top_clear else "top"

    def exit_faces(edge: dict[str, Any]) -> tuple[str, str]:
        src, tgt = edge["from"], edge["to"]
        src_override = edge.get("source_side")
        tgt_override = edge.get("target_side")
        if vertical:
            if cy_map[src] < cy_map[tgt]:
                sf, tf = "bottom", "top"
            elif cy_map[src] > cy_map[tgt]:
                sf, tf = "top", "bottom"
            else:
                sf, tf = ("right", "left") if cx_map[src] < cx_map[tgt] else ("left", "right")
                if _same_row_blocked(src, tgt, boxes):
                    same_row_face = "bottom" if cy_map[src] >= by + bh / 2 else "top"
                    sf = tf = same_row_face

            diagonal = abs(cx_map[src] - cx_map[tgt]) > min(nw(src), nw(tgt)) * 0.75
            rank_span = abs(lo.rank.get(src, 0) - lo.rank.get(tgt, 0))
            if (
                cy_map[src] != cy_map[tgt]
                and sf in ("top", "bottom")
                and tf in ("top", "bottom")
                and _vertical_corridor_blocked(src, tgt, boxes)
            ):
                side = horizontal_face_toward(src, tgt)
                if horizontal_clearance(tgt, side) >= port_stub * 2:
                    sf = tf = side
            if cy_map[src] != cy_map[tgt] and diagonal and rank_span > 1:
                toward_target = "right" if cx_map[tgt] >= cx_map[src] else "left"
                sf = toward_target if open_horizontal_face(src) == toward_target else open_horizontal_face(src)
            if (
                cy_map[src] != cy_map[tgt]
                and diagonal
                and edge_degree[src] > 2
                and sf in ("top", "bottom")
                and not rank_wrap
            ):
                side = horizontal_face_toward(src, tgt)
                if horizontal_clearance(src, side) >= max(col_gap * 1.5, port_stub * 2):
                    sf = side
            if cy_map[src] != cy_map[tgt] and diagonal and edge_degree[src] == 1:
                sf = open_horizontal_face(src)
        else:
            if cx_map[src] < cx_map[tgt]:
                sf, tf = "right", "left"
            elif cx_map[src] > cx_map[tgt]:
                sf, tf = "left", "right"
            else:
                sf, tf = ("bottom", "top") if cy_map[src] < cy_map[tgt] else ("top", "bottom")

            diagonal = abs(cy_map[src] - cy_map[tgt]) > min(nh(src), nh(tgt)) * 0.75
            if cx_map[src] != cx_map[tgt] and diagonal and edge_degree[src] == 1:
                sf = open_vertical_face(src)

        if src_override in OPP:
            sf = src_override
        if tgt_override in OPP:
            tf = tgt_override
        return sf, tf

    # Boundary input face: nearest boundary wall to the target node.
    def bnd_face_for(tgt: str) -> str:
        tx, ty = cx_map[tgt], cy_map[tgt]
        if vertical:
            return "top" if ty - by <= (by + bh - ty) else "bottom"
        else:
            return "left" if tx - bx <= (bx + bw - tx) else "right"

    face_ports: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    port_peer: dict[str, str] = {}
    conn_entries = []
    for e in edges:
        s, t = e["from"], e["to"]
        if s not in boxes or t not in boxes:
            continue
        sf, tf = exit_faces(e)
        sp, tp = f"{s}--{t}--src", f"{s}--{t}--tgt"
        port_peer[sp] = t
        port_peer[tp] = s
        face_ports[s][sf].append(sp)
        face_ports[t][tf].append(tp)
        conn_entries.append((e, sp, sf, tp, tf))

    bnd_entries = []
    bnd_target_labels: dict[str, str] = {}
    for bi in binputs:
        tgt = bi["to"]
        if tgt not in boxes:
            continue
        bf  = bnd_face_for(tgt)
        tf  = bf        # element receives on the face that faces the boundary
        bp  = f"bnd--{tgt}"
        tp  = f"{tgt}--bnd--tgt"
        port_peer[bp] = tgt
        port_peer[tp] = "boundary"
        face_ports[tgt][tf].append(tp)
        if label_mode in ("port", "both"):
            bnd_target_labels[tp] = str(bi.get("target_label", bi.get("label", "")))
        bnd_entries.append((bi, bp, tp, tgt, bf))

    # Port offsets: centred when alone, evenly distributed when multiple.
    # For ports sharing a face, assign offsets in peer-geometric order.
    # This keeps fan-outs/fan-ins monotonic and avoids crossings that happen
    # when a common node's ports are simply assigned in input order.
    port_place: dict[str, tuple[str, float]] = {}
    for nid, faces in face_ports.items():
        for face, pids in faces.items():
            pids.sort(key=lambda pid, _nid=nid, _face=face: _port_sort_key(_nid, _face, pid, port_peer, boxes))
            n = len(pids)
            centered_pid = _center_aligned_port(nid, face, pids, port_peer, boxes)
            if centered_pid:
                center_index = pids.index(centered_pid)
                left_slots = _spread_offsets(center_index, 0, 0.5)
                right_slots = _spread_offsets(n - center_index - 1, 0.5, 1)
                for i, pid in enumerate(pids):
                    if pid == centered_pid:
                        offset = 0.5
                    elif i < center_index:
                        offset = left_slots[i]
                    else:
                        offset = right_slots[i - center_index - 1]
                    port_place[pid] = (face, round(offset, 4))
            else:
                for i, pid in enumerate(pids):
                    port_place[pid] = (face, round((i + 1) / (n + 1), 4))

    # ── connection routing with non-overlapping tracks ────────────────────
    # Group connections by the channel they cross (pair of adjacent ranks).
    # Within each channel assign each connection a unique track position so
    # their horizontal (landscape) or vertical (portrait) mid-segments never
    # overlap.  Sort connections by cross-axis midpoint first to minimise
    # crossing among the tracks themselves.
    lo_rank = lo.rank
    channels: dict[tuple[int, int, bool, str], list[tuple]] = defaultdict(list)
    for e, sp, sf, tp_, tf in conn_entries:
        sr, tr = lo_rank.get(e["from"], 0), lo_rank.get(e["to"], 0)
        route_vertical = _route_vertical(sf, tf)
        band = _route_band(sr, tr, route_vertical, sf, tf)
        key = (min(sr, tr), max(sr, tr), route_vertical, band)
        channels[key].append((e, sp, sf, tp_, tf))

    def _port_xy(node: str, port_id: str, side: str) -> tuple[float, float]:
        """Return the absolute (x, y) anchor point for a specific port."""
        x, y, w, h = boxes[node]
        _, off = port_place.get(port_id, (side, 0.5))
        if side == "top":    return x + w * off, y
        if side == "bottom": return x + w * off, y + h
        if side == "right":  return x + w,       y + h * off
        return x, y + h * off   # left

    conn_waypoints: dict[str, list[dict]] = {}

    for (r_lo, r_hi, route_vertical, band), members in channels.items():
        chan_lo, chan_hi = _channel_gap(
            r_lo, r_hi, lo.rank_groups, boxes, route_vertical, route_clearance, track_gap, len(members), band
        )

        # Sort by the cross-axis midpoint of actual port positions.
        def _sort_key(m, _v=route_vertical):
            _, sp_, sf_, tp_2, tf_ = m
            # Extract node names from port ids: "src--tgt--src" → src node
            src_node = sp_.split("--")[0]
            tgt_node = tp_2.split("--")[1]
            ax_, ay_ = _port_xy(src_node, sp_, sf_)
            bx_, by_ = _port_xy(tgt_node, tp_2, tf_)
            return ((ax_ + bx_) / 2) if _v else ((ay_ + by_) / 2)
        members.sort(key=_sort_key)

        n = len(members)
        step = (chan_hi - chan_lo) / (n + 1)
        avg_delta = 0.0
        for _, sp_, sf_, tp_2, tf_ in members:
            src_node = sp_.split("--")[0]
            tgt_node = tp_2.split("--")[1]
            ax_, ay_ = _port_xy(src_node, sp_, sf_)
            bx_2, by_2 = _port_xy(tgt_node, tp_2, tf_)
            avg_delta += (by_2 - ay_) if route_vertical else (bx_2 - ax_)
        avg_delta = avg_delta / max(n, 1)
        rank_span = r_hi - r_lo
        source_near_hi = avg_delta < 0 if route_vertical else avg_delta < 0
        if band in ("bottom", "right"):
            edge_step = min(track_gap, max((chan_hi - chan_lo) / (n + 1), 1))
            tracks = [chan_lo + edge_step * i for i in range(n)]
        elif band in ("top", "left"):
            edge_step = min(track_gap, max((chan_hi - chan_lo) / (n + 1), 1))
            tracks = [chan_hi - edge_step * i for i in range(n)]
        elif rank_span > 1:
            edge_step = min(track_gap, max((chan_hi - chan_lo) / (n + 1), 1))
            if source_near_hi:
                tracks = [chan_hi - edge_step * (i + 1) for i in range(n)]
            else:
                tracks = [chan_lo + edge_step * (i + 1) for i in range(n)]
        else:
            tracks = [chan_lo + step * (i + 1) for i in range(n)]

        def _route_for(member, track):
            e, sp, sf, tp_, tf = member
            conn_id = f"conn-{e['from']}-{e['to']}"
            src_node = sp.split("--")[0]
            tgt_node = tp_.split("--")[1]
            ax, ay = _port_xy(src_node, sp,  sf)
            bx_, by_ = _port_xy(tgt_node, tp_, tf)

            if route_vertical and sf in ("top", "bottom") and tf in ("top", "bottom") and abs(ax - bx_) < 2:
                waypoints = []
            elif not route_vertical and sf in ("left", "right") and tf in ("left", "right") and abs(ay - by_) < 2:
                waypoints = []
            elif elbow := _mixed_elbow_waypoints(
                ax, ay, bx_, by_, sf, tf, src_node, tgt_node, boxes
            ):
                waypoints = elbow
            elif route_vertical:
                waypoints = _vertical_waypoints(ax, ay, bx_, by_, sf, tf, track, port_stub)
            else:
                waypoints = _horizontal_waypoints(ax, ay, bx_, by_, sf, tf, track, port_stub)

            points = [(ax, ay), *[(point["x"], point["y"]) for point in waypoints], (bx_, by_)]
            return conn_id, waypoints, points

        def _assignment_score(assigned_tracks):
            routed = [_route_for(member, track) for member, track in zip(members, assigned_tracks)]
            crossings = _route_crossing_count(routed)
            length = sum(_route_length(points) for _, _, points in routed)
            displacement = sum(abs(track - tracks[i]) for i, track in enumerate(assigned_tracks))
            return (crossings, round(length, 3), round(displacement, 3), tuple(round(track, 3) for track in assigned_tracks))

        best_tracks = tuple(tracks)
        best_score = _assignment_score(best_tracks)
        if n <= 6:
            for candidate_tracks in permutations(tracks):
                score = _assignment_score(candidate_tracks)
                if score < best_score:
                    best_score = score
                    best_tracks = candidate_tracks

        for member, track in zip(members, best_tracks):
            conn_id, waypoints, _points = _route_for(member, track)
            conn_waypoints[conn_id] = waypoints

    # ── route-aware canvas normalization ──────────────────────────────────
    # Compute the final extents from boxes and routed points, then shift the
    # whole diagram to a consistent canvas margin. This keeps outside-band
    # routes away from the boundary without preserving stale layout whitespace.
    extent_x = [x for x, _y, _w, _h in boxes.values()]
    extent_y = [y for _x, y, _w, _h in boxes.values()]
    extent_x2 = [x + w for x, _y, w, _h in boxes.values()]
    extent_y2 = [y + h for _x, y, _w, h in boxes.values()]

    def _port_xy_for_place(node: str, port_id: str, side: str) -> tuple[float, float]:
        x, y, w, h = boxes[node]
        _, off = port_place.get(port_id, (side, 0.5))
        if side == "top":    return x + w * off, y
        if side == "bottom": return x + w * off, y + h
        if side == "right":  return x + w,       y + h * off
        return x, y + h * off

    for e, sp, sf, tp, tf in conn_entries:
        conn_id = f"conn-{e['from']}-{e['to']}"
        points = [
            _port_xy_for_place(sp.split("--")[0], sp, sf),
            *[(point["x"], point["y"]) for point in conn_waypoints.get(conn_id, [])],
            _port_xy_for_place(tp.split("--")[1], tp, tf),
        ]
        for px, py in points:
            extent_x.append(px)
            extent_y.append(py)
            extent_x2.append(px)
            extent_y2.append(py)

    boundary_pad = int(spec.get("boundary_pad", max(route_clearance + 12, 36)))
    raw_bx = min(extent_x) - boundary_pad
    raw_by = min(extent_y) - boundary_pad
    raw_br = max(extent_x2) + boundary_pad
    raw_bb = max(extent_y2) + boundary_pad
    shift_x = CANVAS_MARGIN - raw_bx
    shift_y = CANVAS_MARGIN - raw_by

    if shift_x or shift_y:
        for nid, (x, y, w, h) in list(boxes.items()):
            boxes[nid] = (round(x + shift_x), round(y + shift_y), w, h)
        for waypoints in conn_waypoints.values():
            for point in waypoints:
                point["x"] = _clean_number(point["x"] + shift_x)
                point["y"] = _clean_number(point["y"] + shift_y)

    bx = CANVAS_MARGIN
    by = CANVAS_MARGIN
    bw = raw_br - raw_bx
    bh = raw_bb - raw_by
    canvas_w = bx + bw + CANVAS_MARGIN
    canvas_h = by + bh + CANVAS_MARGIN

    # ── boundary port offsets aligned to target ───────────────────────────
    bnd_port_place: dict[str, tuple[str, float]] = {}
    for bi, bp, tp, tgt, bf in bnd_entries:
        tside, toff = port_place.get(tp, (bf, 0.5))
        tx_b, ty_b, tw, th = boxes[tgt]
        if tside in ("top", "bottom"):
            abs_pos = tx_b + tw * toff
            off = (abs_pos - bx) / bw
        else:
            abs_pos = ty_b + th * toff
            off = (abs_pos - by) / bh
        bnd_port_place[bp] = (bf, round(max(0.02, min(0.98, off)), 4))

    # ── assemble .sysmld ───────────────────────────────────────────────────
    out_elems: list[dict] = []

    out_elems.append({
        "id": "boundary",
        "model_ref": spec.get("subject", "boundary"),
        "symbol": "boundary",
        "layout": {"x": round(bx), "y": round(by),
                   "width": round(bw), "height": round(bh), "z": 0},
        "compartments": {"attributes": False, "ports": False, "actions": False},
        "style": "boundary.system",
    })

    for nid in nids:
        x, y, w, h = boxes[nid]
        d = nodes[nid]
        out_elems.append({
            "id": nid, "model_ref": nid, "symbol": "part_usage",
            "layout": {"x": x, "y": y, "width": w, "height": h, "z": 10},
            "label": d.get("label", nid),
            "compartments": {"attributes": False, "ports": True, "actions": False},
            "style": d.get("style", "part.default"),
        })

    seen: set[str] = set()
    for nid in nids:
        for face, pids in face_ports.get(nid, {}).items():
            for pid in pids:
                if pid in seen: continue
                seen.add(pid)
                side, offset = port_place.get(pid, (face, 0.5))
                out_elems.append({
                    "id": pid, "model_ref": pid, "symbol": "port",
                    "owner": nid,
                    "placement": {"side": side, "offset": offset},
                    "label": bnd_target_labels.get(pid, _generated_port_label(pid, conn_entries, label_mode)),
                })

    for bi, bp, tp, tgt, bf in bnd_entries:
        bside, boffset = bnd_port_place.get(bp, (bf, 0.5))
        out_elems.append({
            "id": bp, "model_ref": bp, "symbol": "port",
            "owner": "boundary",
            "placement": {"side": bside, "offset": boffset},
            "label": bi.get("label", ""),
        })
        if tp not in seen:
            tside, toff = port_place.get(tp, (bf, 0.5))
            out_elems.append({
                "id": tp, "model_ref": tp, "symbol": "port",
                "owner": tgt,
                "placement": {"side": tside, "offset": toff},
                "label": bi.get("target_label", bi.get("label", "")) if label_mode in ("port", "both") else "",
            })

    out_conns: list[dict] = []
    for e, sp, sf, tp, tf in conn_entries:
        conn_id = f"conn-{e['from']}-{e['to']}"
        wps = conn_waypoints.get(conn_id, [])
        labels = []
        if label_mode in ("connection", "both"):
            labels = [{"text": e.get("label", ""), "position": {"offset": 0.5}}]
        out_conns.append({
            "id": conn_id, "model_ref": e.get("model_ref", conn_id),
            "source": {"element": sp, "anchor": {"side": sf, "offset": 0.5}},
            "target": {"element": tp, "anchor": {"side": tf, "offset": 0.5}},
            "route": {"kind": "orthogonal", "waypoints": wps},
            "labels": labels,
            "style": e.get("style", "connector.default"),
        })

    for bi, bp, tp, tgt, bf in bnd_entries:
        conn_id   = f"conn-bnd-{tgt}"
        src_anchor = OPP[bf]
        tside, _  = port_place.get(tp, (bf, 0.5))
        out_conns.append({
            "id": conn_id, "model_ref": bi.get("model_ref", conn_id),
            "source": {"element": bp, "anchor": {"side": src_anchor, "offset": 0.5}},
            "target": {"element": tp, "anchor": {"side": tside,      "offset": 0.5}},
            "route": {"kind": "orthogonal", "waypoints": []},
            "labels": [],
            "style": bi.get("style", "connector.default"),
        })

    diagram_id = spec.get("diagram", "diagram")
    doc: dict[str, Any] = {
        "$schema": "../../schemas/sysmld.schema.json",
        "version": "0.1",
        "mode": "model_based",
        "model_files": spec.get("model_files", []),
        "aliases": spec.get("aliases", {}),
        "diagram": {
            "id":   diagram_id,
            "kind": spec.get("kind", "InterconnectionView"),
            "name": spec.get("name", diagram_id),
            "canvas": {"width": round(canvas_w), "height": round(canvas_h),
                       "background": "#FFFFFF"},
            "frame":       {"visible": True},
            "elements":    out_elems,
            "connections": out_conns,
            "annotations": [],
            "styles":      spec.get("styles", {}),
        },
    }
    if spec.get("subject"):
        doc["diagram"]["subject"] = spec["subject"]
    return doc


def lo_vertical(direction: str) -> bool:
    return direction in ("top-down", "bottom-up")


def _route_crossing_count(routed: list[tuple[str, list[dict], list[tuple[float, float]]]]) -> int:
    segments = [
        (conn_id, start, end)
        for conn_id, _waypoints, points in routed
        for start, end in zip(points, points[1:])
    ]
    count = 0
    for i, (first_id, first_start, first_end) in enumerate(segments):
        for second_id, second_start, second_end in segments[i + 1:]:
            if first_id == second_id:
                continue
            if {first_start, first_end} & {second_start, second_end}:
                continue
            if _segments_cross(first_start, first_end, second_start, second_end):
                count += 1
    return count


def _route_length(points: list[tuple[float, float]]) -> float:
    return sum(
        abs(end[0] - start[0]) + abs(end[1] - start[1])
        for start, end in zip(points, points[1:])
    )


def _mixed_elbow_waypoints(
    ax: float,
    ay: float,
    bx: float,
    by: float,
    source_side: str,
    target_side: str,
    source_node: str,
    target_node: str,
    boxes: dict[str, tuple[int, int, int, int]],
) -> list[dict[str, float]] | None:
    source_horizontal = source_side in ("left", "right")
    target_horizontal = target_side in ("left", "right")
    if source_horizontal == target_horizontal:
        return None

    elbow = (bx, ay) if source_horizontal else (ax, by)
    points = [(ax, ay), elbow, (bx, by)]
    if _route_crosses_box(points, source_node, target_node, boxes):
        return None
    return _clean_waypoints([elbow])


def _route_crosses_box(
    points: list[tuple[float, float]],
    source_node: str,
    target_node: str,
    boxes: dict[str, tuple[int, int, int, int]],
) -> bool:
    for start, end in zip(points, points[1:]):
        for node_id, box in boxes.items():
            if node_id in (source_node, target_node):
                continue
            if _segment_crosses_box_interior(start, end, box):
                return True
    return False


def _segment_crosses_box_interior(
    start: tuple[float, float],
    end: tuple[float, float],
    box: tuple[int, int, int, int],
) -> bool:
    x1, y1 = start
    x2, y2 = end
    left, top, width, height = box
    right = left + width
    bottom = top + height
    if round(x1, 3) == round(x2, 3):
        return left < x1 < right and max(y1, y2) > top and min(y1, y2) < bottom
    if round(y1, 3) == round(y2, 3):
        return top < y1 < bottom and max(x1, x2) > left and min(x1, x2) < right
    return False


def _spread_offsets(count: int, start: float, end: float) -> list[float]:
    if count <= 0:
        return []
    step = (end - start) / (count + 1)
    return [start + step * (i + 1) for i in range(count)]


def _center_aligned_port(
    node_id: str,
    face: str,
    port_ids: list[str],
    port_peer: dict[str, str],
    boxes: dict[str, tuple[int, int, int, int]],
) -> str | None:
    aligned: list[tuple[float, str]] = []
    node_x, node_y, node_w, node_h = boxes[node_id]
    for port_id in port_ids:
        peer = port_peer.get(port_id)
        if peer not in boxes:
            continue
        peer_x, peer_y = _box_center(boxes[peer])
        if face in ("top", "bottom"):
            projected = (peer_x - node_x) / node_w
        else:
            projected = (peer_y - node_y) / node_h
        distance = abs(projected - 0.5)
        if distance <= 0.08:
            aligned.append((distance, port_id))
    if len(aligned) != 1:
        return None
    return min(aligned)[1]


def _generated_port_label(port_id: str, conn_entries: list[tuple], label_mode: str) -> str:
    if label_mode not in ("port", "both"):
        return ""
    for edge, source_port, _source_face, target_port, _target_face in conn_entries:
        if port_id == source_port:
            return str(edge.get("source_label", edge.get("label", "")))
        if port_id == target_port:
            return str(edge.get("target_label", edge.get("label", "")))
    return ""


def _route_vertical(source_side: str, target_side: str) -> bool:
    return not (source_side in ("left", "right") and target_side in ("left", "right"))


def _ranges_overlap(a1: float, a2: float, b1: float, b2: float) -> bool:
    return max(a1, b1) < min(a2, b2)


def _same_row_blocked(
    src: str,
    tgt: str,
    boxes: dict[str, tuple[int, int, int, int]],
) -> bool:
    sx, sy, sw, sh = boxes[src]
    tx, ty, tw, th = boxes[tgt]
    if not _ranges_overlap(sy, sy + sh, ty, ty + th):
        return False

    left = min(sx + sw, tx + tw)
    right = max(sx, tx)
    if left >= right:
        return False

    row_top = max(sy, ty)
    row_bottom = min(sy + sh, ty + th)
    for node, (ox, oy, ow, oh) in boxes.items():
        if node in (src, tgt):
            continue
        if ox < right and ox + ow > left and _ranges_overlap(oy, oy + oh, row_top, row_bottom):
            return True
    return False


def _vertical_corridor_blocked(
    src: str,
    tgt: str,
    boxes: dict[str, tuple[int, int, int, int]],
) -> bool:
    sx, sy, sw, sh = boxes[src]
    tx, ty, tw, th = boxes[tgt]
    src_cx = sx + sw / 2
    tgt_cx = tx + tw / 2
    if abs(src_cx - tgt_cx) > min(sw, tw) * 0.35:
        return False

    line_x = (src_cx + tgt_cx) / 2
    top = min(sy + sh, ty + th)
    bottom = max(sy, ty)
    if top >= bottom:
        return False

    for node, (ox, oy, ow, oh) in boxes.items():
        if node in (src, tgt):
            continue
        if ox < line_x < ox + ow and max(oy, top) < min(oy + oh, bottom):
            return True
    return False


def _route_band(
    source_rank: int,
    target_rank: int,
    route_vertical: bool,
    source_side: str,
    target_side: str,
) -> str:
    if route_vertical and source_side == target_side and source_side in ("top", "bottom"):
        return source_side
    if not route_vertical and source_side == target_side and source_side in ("left", "right"):
        return source_side
    if source_rank != target_rank:
        return "between"
    return "between"


def _max_adjacent_channel_members(edges: list[dict[str, Any]], rank: dict[str, int]) -> int:
    counts: dict[tuple[int, int], int] = defaultdict(int)
    for edge in edges:
        src = edge.get("from")
        tgt = edge.get("to")
        if src not in rank or tgt not in rank:
            continue
        r1, r2 = sorted((rank[src], rank[tgt]))
        if r1 == r2:
            counts[(r1, r2)] += 1
            continue
        for r in range(r1, r2):
            counts[(r, r + 1)] += 1
    return max(counts.values(), default=1)


def _channel_gap(
    r1: int,
    r2: int,
    rank_groups: dict[int, list[str]],
    boxes: dict[str, tuple[int, int, int, int]],
    vertical: bool,
    clearance: int,
    track_gap: int,
    member_count: int,
    band: str,
) -> tuple[float, float]:
    group1 = [n for n in rank_groups.get(r1, []) if n in boxes]
    group2 = [n for n in rank_groups.get(r2, []) if n in boxes]
    if not group1 or not group2:
        return 0, 0

    if band in ("top", "bottom") and vertical:
        span = max(clearance, track_gap * (member_count + 1))
        group = list(dict.fromkeys(group1 + group2))
        if band == "top":
            gap_hi = min(boxes[n][1] for n in group) - clearance
            return gap_hi - span, gap_hi
        gap_lo = max(boxes[n][1] + boxes[n][3] for n in group) + clearance
        return gap_lo, gap_lo + span

    if band in ("left", "right") and not vertical:
        span = max(clearance, track_gap * (member_count + 1))
        group = list(dict.fromkeys(group1 + group2))
        if band == "left":
            gap_hi = min(boxes[n][0] for n in group) - clearance
            return gap_hi - span, gap_hi
        gap_lo = max(boxes[n][0] + boxes[n][2] for n in group) + clearance
        return gap_lo, gap_lo + span

    if r1 == r2:
        span = max(clearance, track_gap * (member_count + 1))
        group = group1
        if vertical:
            if band == "top":
                gap_hi = min(boxes[n][1] for n in group) - clearance
                return gap_hi - span, gap_hi
            gap_lo = max(boxes[n][1] + boxes[n][3] for n in group) + clearance
            return gap_lo, gap_lo + span

        if band == "left":
            gap_hi = min(boxes[n][0] for n in group) - clearance
            return gap_hi - span, gap_hi
        gap_lo = max(boxes[n][0] + boxes[n][2] for n in group) + clearance
        return gap_lo, gap_lo + span

    if vertical:
        c1 = sum(boxes[n][1] + boxes[n][3] / 2 for n in group1) / len(group1)
        c2 = sum(boxes[n][1] + boxes[n][3] / 2 for n in group2) / len(group2)
        upper, lower = (group1, group2) if c1 < c2 else (group2, group1)
        gap_lo = max(boxes[n][1] + boxes[n][3] for n in upper) + clearance
        gap_hi = min(boxes[n][1] for n in lower) - clearance
    else:
        c1 = sum(boxes[n][0] + boxes[n][2] / 2 for n in group1) / len(group1)
        c2 = sum(boxes[n][0] + boxes[n][2] / 2 for n in group2) / len(group2)
        left, right = (group1, group2) if c1 < c2 else (group2, group1)
        gap_lo = max(boxes[n][0] + boxes[n][2] for n in left) + clearance
        gap_hi = min(boxes[n][0] for n in right) - clearance

    if gap_hi <= gap_lo:
        mid = (gap_lo + gap_hi) / 2
        return mid, mid
    return gap_lo, gap_hi


def _vertical_waypoints(
    ax: float,
    ay: float,
    bx: float,
    by: float,
    source_side: str,
    target_side: str,
    track_y: float,
    port_stub: int,
) -> list[dict[str, int]]:
    points: list[tuple[float, float]] = []
    if source_side == "left":
        sx = ax - port_stub
        points.extend([(sx, ay), (sx, track_y)])
    elif source_side == "right":
        sx = ax + port_stub
        points.extend([(sx, ay), (sx, track_y)])
    else:
        points.append((ax, track_y))

    if target_side == "left":
        tx = bx - port_stub
        points.extend([(tx, track_y), (tx, by)])
    elif target_side == "right":
        tx = bx + port_stub
        points.extend([(tx, track_y), (tx, by)])
    else:
        points.append((bx, track_y))
    return _clean_waypoints(points)


def _horizontal_waypoints(
    ax: float,
    ay: float,
    bx: float,
    by: float,
    source_side: str,
    target_side: str,
    track_x: float,
    port_stub: int,
) -> list[dict[str, int]]:
    points: list[tuple[float, float]] = []
    if source_side == "top":
        sy = ay - port_stub
        points.extend([(ax, sy), (track_x, sy)])
    elif source_side == "bottom":
        sy = ay + port_stub
        points.extend([(ax, sy), (track_x, sy)])
    else:
        points.append((track_x, ay))

    if target_side == "top":
        ty = by - port_stub
        points.extend([(track_x, ty), (bx, ty)])
    elif target_side == "bottom":
        ty = by + port_stub
        points.extend([(track_x, ty), (bx, ty)])
    else:
        points.append((track_x, by))
    return _clean_waypoints(points)


def _clean_waypoints(points: list[tuple[float, float]]) -> list[dict[str, float]]:
    rounded = [(_clean_number(x), _clean_number(y)) for x, y in points]
    deduped: list[tuple[float, float]] = []
    for point in rounded:
        if not deduped or deduped[-1] != point:
            deduped.append(point)

    cleaned: list[tuple[float, float]] = []
    for point in deduped:
        if len(cleaned) >= 2:
            a = cleaned[-2]
            b = cleaned[-1]
            c = point
            if (a[0] == b[0] == c[0]) or (a[1] == b[1] == c[1]):
                cleaned[-1] = c
                continue
        cleaned.append(point)
    return [{"x": x, "y": y} for x, y in cleaned]


def _clean_number(value: float) -> float:
    rounded = round(value, 3)
    return int(rounded) if float(rounded).is_integer() else rounded


def _box_center(box: tuple[int, int, int, int]) -> tuple[float, float]:
    x, y, w, h = box
    return x + w / 2, y + h / 2


def _port_sort_key(
    node_id: str,
    face: str,
    port_id: str,
    port_peer: dict[str, str],
    boxes: dict[str, tuple[int, int, int, int]],
) -> tuple[float, float, str]:
    peer = port_peer.get(port_id)
    if peer in boxes:
        peer_x, peer_y = _box_center(boxes[peer])
        node_x, node_y = _box_center(boxes[node_id])
        if face in ("top", "bottom"):
            if face == "top":
                return (peer_x, -peer_y, port_id)
            return (peer_x, peer_y, port_id)
        return (peer_y, peer_x, port_id)

    node_x, node_y = _box_center(boxes[node_id])
    return (node_x if face in ("top", "bottom") else node_y, 0, port_id)


def _label_width(label: str) -> int:
    longest = max((len(line) for line in str(label).splitlines()), default=1)
    return longest * 7 + 34


def _label_height(label: str) -> int:
    line_count = len(str(label).splitlines()) or 1
    return line_count * 15 + 28


def compose_file(input_path: Path, output_path: Path | None = None) -> Path:
    with input_path.open(encoding="utf-8") as fh:
        spec = json.load(fh)
    result = compose(spec)
    target = output_path or input_path.with_suffix(".sysmld")
    with target.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")
    return target
