"""Deterministic orthogonal routing helpers and crossing hop-overs."""

from __future__ import annotations

from collections import defaultdict
from heapq import heappop, heappush
from typing import Any


HOP_RADIUS = 7.0
HOP_CLEAR = 10.0
TRACK_PAD = 16.0
RAIL_PAD = 40.0
RAIL_GAP = 18.0
ALIGN_SNAP = 14.0
BOX_CLEAR = 16.0


def clean(value: float) -> float:
    rounded = round(value, 3)
    return int(rounded) if float(rounded).is_integer() else rounded


def orthogonal_intersection(
    a1: tuple[float, float],
    a2: tuple[float, float],
    b1: tuple[float, float],
    b2: tuple[float, float],
) -> tuple[float, float] | None:
    ax1, ay1 = a1
    ax2, ay2 = a2
    bx1, by1 = b1
    bx2, by2 = b2
    a_horiz = abs(ay1 - ay2) < 0.6 and abs(ax1 - ax2) >= 0.6
    a_vert = abs(ax1 - ax2) < 0.6 and abs(ay1 - ay2) >= 0.6
    b_horiz = abs(by1 - by2) < 0.6 and abs(bx1 - bx2) >= 0.6
    b_vert = abs(bx1 - bx2) < 0.6 and abs(by1 - by2) >= 0.6
    if a_horiz and b_vert:
        x, y = bx1, ay1
        if _strict_between(x, ax1, ax2) and _strict_between(y, by1, by2):
            return (x, y)
        return None
    if a_vert and b_horiz:
        x, y = ax1, by1
        if _strict_between(y, ay1, ay2) and _strict_between(x, bx1, bx2):
            return (x, y)
        return None
    return None


def hop_crossings(
    paths: list[list[tuple[float, float]]],
    radius: float = HOP_RADIUS,
) -> list[list[tuple[int, float, float]]]:
    """Later paths hop over earlier ones. Returns (segment_index, x, y) per path."""

    result: list[list[tuple[int, float, float]]] = [[] for _ in paths]
    for index, path in enumerate(paths):
        hops: list[tuple[int, float, float]] = []
        path_ends = (path[0], path[-1])
        for seg_index, (start, end) in enumerate(zip(path, path[1:])):
            if _dist(start, end) < radius * 2:
                continue
            for earlier in paths[:index]:
                earlier_ends = (earlier[0], earlier[-1])
                for other_start, other_end in zip(earlier, earlier[1:]):
                    hit = orthogonal_intersection(start, end, other_start, other_end)
                    if hit is None:
                        continue
                    if _near_end(hit, path_ends) or _near_end(hit, earlier_ends):
                        continue
                    hops.append((seg_index, hit[0], hit[1]))
        hops.sort(key=lambda item: (item[0], item[1], item[2]))
        unique: list[tuple[int, float, float]] = []
        seen: set[tuple[int, float, float]] = set()
        last_by_seg: dict[int, tuple[float, float]] = {}
        for hop in hops:
            key = (hop[0], round(hop[1], 2), round(hop[2], 2))
            if key in seen:
                continue
            previous = last_by_seg.get(hop[0])
            if previous and _dist(previous, (hop[1], hop[2])) < radius * 2:
                continue
            seen.add(key)
            last_by_seg[hop[0]] = (hop[1], hop[2])
            unique.append(hop)
        result[index] = unique
    return result


def hop_arc(
    start: tuple[float, float],
    end: tuple[float, float],
    hop: tuple[float, float],
    radius: float = HOP_RADIUS,
) -> tuple[tuple[float, float], tuple[float, float], int] | None:
    """Return (before, after, sweep) for a semicircle hop, or None if too tight."""

    hx, hy = hop
    if _dist(start, hop) < radius + 1 or _dist(end, hop) < radius + 1:
        return None
    if abs(end[1] - start[1]) < abs(end[0] - start[0]):
        going_right = end[0] >= start[0]
        before = (hx - radius, hy) if going_right else (hx + radius, hy)
        after = (hx + radius, hy) if going_right else (hx - radius, hy)
        sweep = 0 if going_right else 1
    else:
        going_down = end[1] >= start[1]
        before = (hx, hy - radius) if going_down else (hx, hy + radius)
        after = (hx, hy + radius) if going_down else (hx, hy - radius)
        sweep = 1 if going_down else 0
    return before, after, sweep


def rank_route_assignments(
    edges: list[dict[str, Any]],
    boxes: dict[str, tuple[float, float, float, float]],
    nodes: dict[str, dict[str, Any]],
    direction: str,
    member_bounds: dict[str, tuple[float, float, float, float]] | None = None,
) -> list[tuple[str, float] | None]:
    """Assign a channel track or side rail to each ranked edge."""

    assignments: list[tuple[str, float] | None] = [None] * len(edges)
    channels: dict[tuple[str, int, int], list[int]] = defaultdict(list)
    for index, edge in enumerate(edges):
        src = edge.get("from")
        tgt = edge.get("to")
        if src not in nodes or tgt not in nodes or src not in boxes or tgt not in boxes:
            continue
        if "rank" not in nodes[src] or "rank" not in nodes[tgt]:
            continue
        source_rank = int(nodes[src]["rank"])
        target_rank = int(nodes[tgt]["rank"])
        if source_rank == target_rank:
            continue
        low, high = sorted((source_rank, target_rank))
        kind = "channel" if high - low == 1 else "rail"
        channels[(kind, low, high)].append(index)

    vertical = direction in {"top-down", "bottom-up"}
    groups = member_bounds or {}
    for (kind, _low, _high), indexes in channels.items():
        if kind == "channel":
            _assign_channel(assignments, indexes, edges, boxes, vertical, groups)
        else:
            _assign_rails(assignments, indexes, edges, boxes, vertical)
    return assignments


def _assign_channel(
    assignments: list[tuple[str, float] | None],
    indexes: list[int],
    edges: list[dict[str, Any]],
    boxes: dict[str, tuple[float, float, float, float]],
    vertical: bool,
    member_bounds: dict[str, tuple[float, float, float, float]],
) -> None:
    routed = [
        index
        for index in indexes
        if _shares_endpoint(index, indexes, edges) or not _centers_aligned(edges[index], boxes, vertical)
    ]
    if not routed:
        return

    lows: list[float] = []
    highs: list[float] = []
    for index in routed:
        low, high = _channel_span(edges[index], boxes, vertical, member_bounds)
        lows.append(low)
        highs.append(high)
    gap_lo = max(lows) + TRACK_PAD
    gap_hi = min(highs) - TRACK_PAD
    if gap_hi - gap_lo < 8:
        return

    def sort_key(index: int) -> tuple[float, int]:
        source = boxes[edges[index]["from"]]
        target = boxes[edges[index]["to"]]
        if vertical:
            mid = (_center(source)[0] + _center(target)[0]) / 2
        else:
            mid = (_center(source)[1] + _center(target)[1]) / 2
        return (mid, index)

    ordered = sorted(routed, key=sort_key)
    span = gap_hi - gap_lo
    sources = {edges[index]["from"] for index in ordered}
    targets = {edges[index]["to"] for index in ordered}
    if len(sources) == 1 and len(targets) > 1:
        track = clean(gap_lo + min(20.0, span / 4))
        for index in ordered:
            assignments[index] = ("channel", clean(track))
        return
    count = len(ordered)
    for slot, index in enumerate(ordered):
        assignments[index] = ("channel", clean(gap_lo + span * (slot + 1) / (count + 1)))


def _assign_rails(
    assignments: list[tuple[str, float] | None],
    indexes: list[int],
    edges: list[dict[str, Any]],
    boxes: dict[str, tuple[float, float, float, float]],
    vertical: bool,
) -> None:
    if vertical:
        right = max(box[0] + box[2] for box in boxes.values())
        rail0 = right + RAIL_PAD
    else:
        bottom = max(box[1] + box[3] for box in boxes.values())
        rail0 = bottom + RAIL_PAD

    def sort_key(index: int) -> tuple[float, int]:
        source = boxes[edges[index]["from"]]
        target = boxes[edges[index]["to"]]
        if vertical:
            mid = (_center(source)[1] + _center(target)[1]) / 2
        else:
            mid = (_center(source)[0] + _center(target)[0]) / 2
        return (mid, index)

    for slot, index in enumerate(sorted(indexes, key=sort_key)):
        assignments[index] = ("rail", clean(rail0 + slot * RAIL_GAP))


def _center(box: tuple[float, float, float, float]) -> tuple[float, float]:
    return box[0] + box[2] / 2, box[1] + box[3] / 2


def _channel_span(
    edge: dict[str, Any],
    boxes: dict[str, tuple[float, float, float, float]],
    vertical: bool,
    member_bounds: dict[str, tuple[float, float, float, float]],
) -> tuple[float, float]:
    src = edge["from"]
    tgt = edge["to"]
    source = boxes[src]
    target = boxes[tgt]
    if vertical:
        if _center(source)[1] <= _center(target)[1]:
            low, high = source[1] + source[3], target[1]
            if src in member_bounds:
                group = member_bounds[src]
                low = max(low, group[1] + group[3])
            if tgt in member_bounds:
                high = min(high, member_bounds[tgt][1])
        else:
            low, high = target[1] + target[3], source[1]
            if tgt in member_bounds:
                group = member_bounds[tgt]
                low = max(low, group[1] + group[3])
            if src in member_bounds:
                high = min(high, member_bounds[src][1])
        return low, high
    if _center(source)[0] <= _center(target)[0]:
        low, high = source[0] + source[2], target[0]
        if src in member_bounds:
            group = member_bounds[src]
            low = max(low, group[0] + group[2])
        if tgt in member_bounds:
            high = min(high, member_bounds[tgt][0])
    else:
        low, high = target[0] + target[2], source[0]
        if tgt in member_bounds:
            group = member_bounds[tgt]
            low = max(low, group[0] + group[2])
        if src in member_bounds:
            high = min(high, member_bounds[src][0])
    return low, high


def _centers_aligned(edge: dict[str, Any], boxes: dict[str, tuple[float, float, float, float]], vertical: bool) -> bool:
    source = _center(boxes[edge["from"]])
    target = _center(boxes[edge["to"]])
    delta = abs(source[0] - target[0]) if vertical else abs(source[1] - target[1])
    return delta < ALIGN_SNAP


def _shares_endpoint(index: int, indexes: list[int], edges: list[dict[str, Any]]) -> bool:
    source = edges[index]["from"]
    target = edges[index]["to"]
    return any(
        other != index and (edges[other]["from"] == source or edges[other]["to"] == target)
        for other in indexes
    )


def _near_end(hit: tuple[float, float], ends: tuple[tuple[float, float], tuple[float, float]]) -> bool:
    return _dist(hit, ends[0]) < HOP_CLEAR or _dist(hit, ends[1]) < HOP_CLEAR


def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def _strict_between(value: float, start: float, end: float) -> bool:
    low, high = (start, end) if start <= end else (end, start)
    return low + 0.6 < value < high - 0.6


def segment_crosses_box_interior(
    start: tuple[float, float],
    end: tuple[float, float],
    box: tuple[float, float, float, float],
) -> bool:
    """True when an orthogonal segment passes through a rectangle interior."""

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


def path_crosses_boxes(
    points: list[tuple[float, float]],
    boxes: dict[str, tuple[float, float, float, float]],
    ignore: set[str] | None = None,
) -> bool:
    skip = ignore or set()
    for start, end in zip(points, points[1:]):
        for node_id, box in boxes.items():
            if node_id in skip:
                continue
            if segment_crosses_box_interior(start, end, box):
                return True
    return False


def orthogonal_path_avoiding_boxes(
    start: tuple[float, float],
    end: tuple[float, float],
    boxes: dict[str, tuple[float, float, float, float]],
    *,
    ignore: set[str] | None = None,
    clearance: float = BOX_CLEAR,
    preferred: list[tuple[float, float]] | None = None,
) -> list[tuple[float, float]]:
    """Return intermediate orthogonal points from start to end that miss box interiors.

    Hop-overs are never used here. If `preferred` (a full path including the
    endpoints) is already clear, its intermediate points are returned unchanged.
    """

    skip = ignore or set()
    if preferred is None:
        preferred = [start, end]
    if not path_crosses_boxes(preferred, boxes, skip):
        return list(preferred[1:-1])

    obstacles = [box for node_id, box in boxes.items() if node_id not in skip]
    found = _grid_path(start, end, obstacles, clearance)
    if found is None:
        found = _grid_path(start, end, list(boxes.values()), clearance)
    if found is None:
        return list(preferred[1:-1])
    return found[1:-1]


def _grid_path(
    start: tuple[float, float],
    end: tuple[float, float],
    obstacles: list[tuple[float, float, float, float]],
    clearance: float,
) -> list[tuple[float, float]] | None:
    start_n = (clean(start[0]), clean(start[1]))
    end_n = (clean(end[0]), clean(end[1]))
    xs = {start_n[0], end_n[0]}
    ys = {start_n[1], end_n[1]}
    for x, y, width, height in obstacles:
        xs.add(clean(x - clearance))
        xs.add(clean(x + width + clearance))
        ys.add(clean(y - clearance))
        ys.add(clean(y + height + clearance))
    xs_list = sorted(xs)
    ys_list = sorted(ys)

    def inside(point: tuple[float, float]) -> bool:
        px, py = point
        for x, y, width, height in obstacles:
            if x < px < x + width and y < py < y + height:
                return True
        return False

    def blocked(first: tuple[float, float], second: tuple[float, float]) -> bool:
        return any(segment_crosses_box_interior(first, second, box) for box in obstacles)

    nodes = {(x, y) for x in xs_list for y in ys_list if not inside((x, y))}
    nodes.add(start_n)
    nodes.add(end_n)
    x_index = {value: index for index, value in enumerate(xs_list)}
    y_index = {value: index for index, value in enumerate(ys_list)}

    def neighbors(point: tuple[float, float]) -> list[tuple[float, float]]:
        x, y = point
        result: list[tuple[float, float]] = []
        if x in x_index:
            index = x_index[x]
            for other in (index - 1, index + 1):
                if 0 <= other < len(xs_list):
                    nxt = (xs_list[other], y)
                    if nxt in nodes and not blocked(point, nxt):
                        result.append(nxt)
        if y in y_index:
            index = y_index[y]
            for other in (index - 1, index + 1):
                if 0 <= other < len(ys_list):
                    nxt = (x, ys_list[other])
                    if nxt in nodes and not blocked(point, nxt):
                        result.append(nxt)
        result.sort()
        return result

    infinite = (10**12, 10**12)
    best: dict[tuple[float, float], tuple[float, int]] = {start_n: (0.0, 0)}
    came: dict[tuple[float, float], tuple[float, float]] = {}
    incoming: dict[tuple[float, float], tuple[float, float] | None] = {start_n: None}
    heap: list[tuple[float, int, float, float]] = [(0.0, 0, start_n[0], start_n[1])]
    while heap:
        length, bends, x, y = heappop(heap)
        point = (x, y)
        if best.get(point) != (length, bends):
            continue
        if point == end_n:
            break
        previous_dir = incoming[point]
        for nxt in neighbors(point):
            step = abs(nxt[0] - x) + abs(nxt[1] - y)
            direction = (nxt[0] - x, nxt[1] - y)
            next_bends = bends if previous_dir in (None, direction) else bends + 1
            score = (length + step, next_bends)
            if score < best.get(nxt, infinite):
                best[nxt] = score
                came[nxt] = point
                incoming[nxt] = direction
                heappush(heap, (score[0], score[1], nxt[0], nxt[1]))

    if end_n not in came and end_n != start_n:
        return None
    path = [end_n]
    cursor = end_n
    while cursor != start_n:
        cursor = came[cursor]
        path.append(cursor)
    path.reverse()
    return _compress_collinear(path)


def _compress_collinear(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    cleaned: list[tuple[float, float]] = []
    for point in points:
        if cleaned and cleaned[-1] == point:
            continue
        if len(cleaned) >= 2:
            first = cleaned[-2]
            mid = cleaned[-1]
            if (first[0] == mid[0] == point[0]) or (first[1] == mid[1] == point[1]):
                cleaned[-1] = point
                continue
        cleaned.append(point)
    return cleaned
