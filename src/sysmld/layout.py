"""
Shared Sugiyama layout engine used by both `graph` and `compose`.

Takes nodes and edges, returns rank assignments, within-rank ordering,
and node centre positions.  The same computation drives the topology SVG
and the full .sysmld, so they always agree on which node goes where.
"""

from __future__ import annotations

import math
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LayoutResult:
    rank:          dict[str, int]           # node_id → rank number (sources = 0)
    pos_in_rank:   dict[str, int]           # node_id → position within its rank (0-based)
    rank_groups:   dict[int, list[str]]     # rank → ordered list of node_ids
    cx:            dict[str, float]         # node centre x
    cy:            dict[str, float]         # node centre y
    canvas_w:      float
    canvas_h:      float
    n_ranks:       int
    flip:          bool                     # True for bottom-up / right-left
    vertical:      bool                     # True for top-down / bottom-up


def compute(
    nids:      list[str],
    edges:     list[dict[str, Any]],
    direction: str  = "top-down",
    col_gap:   int  = 120,   # centre-to-centre within a rank
    rank_gap:  int  = 160,   # centre-to-centre between ranks
    margin:    int  = 80,    # canvas edge → nearest node centre
    rank_wrap: str | None = None,
    target_aspect: float = 1.618,
) -> LayoutResult:
    """Run Sugiyama layout and return a LayoutResult."""

    # ── 1. Rank assignment (longest-path, sources = rank 0) ───────────────
    adj:      dict[str, set[str]] = defaultdict(set)
    in_count: dict[str, int]      = {n: 0 for n in nids}
    for e in edges:
        s, t = e["from"], e["to"]
        if s in in_count and t in in_count and s != t:
            adj[s].add(t)
            in_count[t] += 1

    rank: dict[str, int] = {n: 0 for n in nids}
    queue: deque[str] = deque(n for n in sorted(nids) if in_count[n] == 0)
    while queue:
        n = queue.popleft()
        for nbr in sorted(adj[n]):
            rank[nbr] = max(rank[nbr], rank[n] + 1)
            in_count[nbr] -= 1
            if in_count[nbr] == 0:
                queue.append(nbr)

    # ── 2. Within-rank ordering (barycenter, always rank-0-first) ─────────
    # Do NOT flip rank numbers before this step — barycenter needs
    # predecessors positioned first, which means processing rank 0 first.
    rank_groups: dict[int, list[str]] = defaultdict(list)
    for n in nids:
        rank_groups[rank[n]].append(n)

    preds: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        if e["from"] in rank and e["to"] in rank:
            preds[e["to"]].append(e["from"])

    pos_in_rank: dict[str, int] = {}
    for r in sorted(rank_groups):
        grp = rank_groups[r]
        if r == 0:
            grp.sort()
        else:
            def _bary(n: str, _p=preds, _pos=pos_in_rank) -> float:
                ps = [_pos[p] for p in _p[n] if p in _pos]
                return sum(ps) / len(ps) if ps else 0.0
            grp.sort(key=_bary)
        rank_groups[r] = grp
        for i, n in enumerate(grp):
            pos_in_rank[n] = i

    # ── 3. Coordinate assignment ───────────────────────────────────────────
    all_ranks   = sorted(rank_groups)
    n_ranks     = len(all_ranks)
    vertical    = direction in ("top-down", "bottom-up")
    flip        = direction in ("bottom-up", "right-left")
    max_per     = max((len(g) for g in rank_groups.values()), default=1)

    wrapped = rank_wrap in ("golden", "snake") and vertical and n_ranks > 3

    if wrapped:
        rows_per_col = _wrapped_rows_per_col(
            n_ranks,
            max_per,
            col_gap,
            rank_gap,
            margin,
            target_aspect,
        )
        n_cols = (n_ranks + rows_per_col - 1) // rows_per_col
        fold_gap = _fold_gap(col_gap, rank_gap, max_per)
        canvas_w = margin * 2 + (n_cols - 1) * fold_gap + (max_per - 1) * col_gap
        canvas_h = margin * 2 + (rows_per_col - 1) * rank_gap
    elif vertical:
        canvas_w = margin * 2 + (max_per - 1) * col_gap
        canvas_h = margin * 2 + (n_ranks  - 1) * rank_gap
    else:
        canvas_h = margin * 2 + (max_per - 1) * col_gap
        canvas_w = margin * 2 + (n_ranks  - 1) * rank_gap

    cx_map: dict[str, float] = {}
    cy_map: dict[str, float] = {}

    for ri, r in enumerate(all_ranks):
        grp   = rank_groups[r]
        n_grp = len(grp)

        if wrapped:
            rank_idx = (n_ranks - 1 - ri) if flip else ri
            col_idx = rank_idx // rows_per_col
            row_in_col = rank_idx % rows_per_col
            if col_idx % 2 == 1:
                row_in_col = rows_per_col - 1 - row_in_col
            primary = margin + row_in_col * rank_gap
            if n_grp > 1 and col_idx + n_grp - 1 < n_cols:
                cross_step = fold_gap
                cross_start = margin + col_idx * fold_gap
            else:
                cross_step = col_gap
                total_cross = (n_grp - 1) * col_gap
                cross_start = margin + col_idx * fold_gap - total_cross / 2
        else:
            # Primary axis: flip direction for bottom-up / right-left.
            rank_idx = (n_ranks - 1 - ri) if flip else ri
            primary  = margin + rank_idx * rank_gap

            # Cross axis: centre the group within the canvas.
            cross_step = col_gap
            total_cross = (n_grp - 1) * col_gap
            cross_start = ((canvas_w if vertical else canvas_h) - total_cross) / 2

        for i, n in enumerate(grp):
            cross = cross_start + i * cross_step
            if vertical:
                cx_map[n] = cross
                cy_map[n] = primary
            else:
                cx_map[n] = primary
                cy_map[n] = cross

    if wrapped:
        _reduce_wrapped_crossings(
            nids,
            edges,
            rank_groups,
            cx_map,
            cy_map,
            col_gap,
            rank_gap,
            margin,
            target_aspect,
            vertical,
        )
        min_x = min(cx_map.values(), default=margin)
        min_y = min(cy_map.values(), default=margin)
        dx = margin - min_x if min_x < margin else 0
        dy = margin - min_y if min_y < margin else 0
        if dx or dy:
            for n in nids:
                cx_map[n] += dx
                cy_map[n] += dy
        canvas_w = max(cx_map.values(), default=margin) + margin
        canvas_h = max(cy_map.values(), default=margin) + margin

    return LayoutResult(
        rank=rank,
        pos_in_rank=pos_in_rank,
        rank_groups=dict(rank_groups),
        cx=cx_map,
        cy=cy_map,
        canvas_w=canvas_w,
        canvas_h=canvas_h,
        n_ranks=n_ranks,
        flip=flip,
        vertical=vertical,
    )


def _wrapped_rows_per_col(
    n_ranks: int,
    max_per: int,
    col_gap: int,
    rank_gap: int,
    margin: int,
    target_aspect: float,
) -> int:
    best_rows = n_ranks
    best_score = float("inf")
    for rows in range(2, n_ranks + 1):
        cols = (n_ranks + rows - 1) // rows
        fold_gap = _fold_gap(col_gap, rank_gap, max_per)
        width = margin * 2 + (cols - 1) * fold_gap + (max_per - 1) * col_gap
        height = margin * 2 + (rows - 1) * rank_gap
        aspect = width / max(height, 1)
        score = abs(math.log(aspect / target_aspect))
        if aspect > target_aspect:
            score *= 2
        if score < best_score:
            best_score = score
            best_rows = rows
    return best_rows


def _fold_gap(col_gap: int, rank_gap: int, max_per: int) -> float:
    return max(col_gap * max(1.25, max_per - 0.75), rank_gap * 1.2)


def _reduce_wrapped_crossings(
    nids: list[str],
    edges: list[dict[str, Any]],
    rank_groups: dict[int, list[str]],
    cx: dict[str, float],
    cy: dict[str, float],
    col_gap: int,
    rank_gap: int,
    margin: int,
    target_aspect: float,
    vertical: bool,
) -> None:
    if not vertical:
        return

    original = {n: (cx[n], cy[n]) for n in nids}
    shifts = {r: 0.0 for r in rank_groups}
    candidate_step = min(col_gap, rank_gap)
    candidates = [i * candidate_step for i in (-1, 0, 1)]

    def apply_shift(rank_id: int, value: float) -> None:
        delta = value - shifts[rank_id]
        if delta == 0:
            return
        for n in rank_groups[rank_id]:
            cx[n] += delta
        shifts[rank_id] = value

    rank_ids = sorted(rank_groups)
    if len(rank_ids) <= 9:
        best_values = tuple(shifts[r] for r in rank_ids)
        best_score = _layout_score(
            nids,
            edges,
            rank_groups,
            cx,
            cy,
            original,
            shifts,
            col_gap,
            rank_gap,
            margin,
            target_aspect,
        )

        def visit(index: int) -> None:
            nonlocal best_score, best_values
            if index == len(rank_ids):
                score = _layout_score(
                    nids,
                    edges,
                    rank_groups,
                    cx,
                    cy,
                    original,
                    shifts,
                    col_gap,
                    rank_gap,
                    margin,
                    target_aspect,
                )
                if score < best_score:
                    best_score = score
                    best_values = tuple(shifts[r] for r in rank_ids)
                return

            rank_id = rank_ids[index]
            current = shifts[rank_id]
            for candidate in candidates:
                apply_shift(rank_id, candidate)
                visit(index + 1)
            apply_shift(rank_id, current)

        visit(0)
        for rank_id, value in zip(rank_ids, best_values):
            apply_shift(rank_id, value)
        return

    for _pass in range(3):
        changed = False
        for rank_id in rank_ids:
            current = shifts[rank_id]
            best_shift = current
            best_score = _layout_score(
                nids,
                edges,
                rank_groups,
                cx,
                cy,
                original,
                shifts,
                col_gap,
                rank_gap,
                margin,
                target_aspect,
            )
            for candidate in candidates:
                apply_shift(rank_id, candidate)
                score = _layout_score(
                    nids,
                    edges,
                    rank_groups,
                    cx,
                    cy,
                    original,
                    shifts,
                    col_gap,
                    rank_gap,
                    margin,
                    target_aspect,
                )
                if score < best_score:
                    best_score = score
                    best_shift = candidate
            apply_shift(rank_id, best_shift)
            changed = changed or best_shift != current
        if not changed:
            break


def _layout_score(
    nids: list[str],
    edges: list[dict[str, Any]],
    rank_groups: dict[int, list[str]],
    cx: dict[str, float],
    cy: dict[str, float],
    original: dict[str, tuple[float, float]],
    shifts: dict[int, float],
    col_gap: int,
    rank_gap: int,
    margin: int,
    target_aspect: float,
) -> tuple[int, int, int, float, float, float, float, float]:
    crossings = _edge_crossings(edges, cx, cy)
    close_pairs = _close_node_pairs(nids, cx, cy, col_gap, rank_gap)
    min_x = min(cx.values())
    min_y = min(cy.values())
    width = max(cx.values()) - min_x + 2 * margin
    height = max(cy.values()) - min_y + 2 * margin
    aspect = width / max(height, 1)
    aspect_error = abs(math.log(aspect / target_aspect))
    aspect_bucket = round(aspect_error / 0.05)
    dx = margin - min_x if min_x < margin else 0
    dy = margin - min_y if min_y < margin else 0
    displacement = sum(
        abs((cx[n] + dx) - original[n][0]) + abs((cy[n] + dy) - original[n][1])
        for n in nids
    )
    max_shift = max((abs(shift) for shift in shifts.values()), default=0)
    moved_multi = sum(
        abs(shifts.get(rank_id, 0)) * len(group)
        for rank_id, group in rank_groups.items()
        if len(group) > 1
    )
    area = width * height
    return (
        crossings,
        close_pairs,
        displacement,
        max_shift,
        moved_multi,
        aspect_bucket,
        round(aspect_error, 6),
        area,
    )


def _edge_crossings(edges: list[dict[str, Any]], cx: dict[str, float], cy: dict[str, float]) -> int:
    valid_edges = [
        (edge["from"], edge["to"])
        for edge in edges
        if edge.get("from") in cx and edge.get("to") in cx
    ]
    count = 0
    for i, (a, b) in enumerate(valid_edges):
        p1 = (cx[a], cy[a])
        p2 = (cx[b], cy[b])
        for c, d in valid_edges[i + 1:]:
            if len({a, b, c, d}) < 4:
                continue
            q1 = (cx[c], cy[c])
            q2 = (cx[d], cy[d])
            if _segments_cross(p1, p2, q1, q2):
                count += 1
    return count


def _close_node_pairs(
    nids: list[str],
    cx: dict[str, float],
    cy: dict[str, float],
    col_gap: int,
    rank_gap: int,
) -> int:
    count = 0
    for i, a in enumerate(nids):
        for b in nids[i + 1:]:
            if abs(cy[a] - cy[b]) < rank_gap * 0.25 and abs(cx[a] - cx[b]) < col_gap * 0.8:
                count += 1
    return count


def _segments_cross(
    p1: tuple[float, float],
    p2: tuple[float, float],
    q1: tuple[float, float],
    q2: tuple[float, float],
) -> bool:
    def orient(a, b, c) -> float:
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    o1 = orient(p1, p2, q1)
    o2 = orient(p1, p2, q2)
    o3 = orient(q1, q2, p1)
    o4 = orient(q1, q2, p2)
    return (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)
