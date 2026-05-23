"""Generic deterministic composers for non-IBD SysMLD views."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .layout import compute as _layout


VIEW_DEFAULT_SYMBOL = {
    "PackageView": "package",
    "RequirementView": "requirement",
    "ConstraintView": "constraint",
    "ActionView": "action",
    "UseCaseView": "use_case",
    "AllocationView": "allocation",
    "FlowView": "flow_node",
    "AnalysisCaseView": "case",
    "VerificationCaseView": "case",
    "InterfaceView": "interface",
    "GeneralView": "part_usage",
}

SYMBOL_SIZE = {
    "actor": (70, 90),
    "use_case": (150, 70),
    "decision_node": (58, 58),
    "fork_node": (90, 12),
    "join_node": (90, 12),
    "initial_state": (20, 20),
    "final_state": (24, 24),
    "activity_final_node": (24, 24),
    "package": (170, 90),
    "requirement": (170, 82),
    "constraint": (160, 76),
    "value_property": (130, 56),
    "case": (170, 76),
}

MARGIN = 72
GROUP_PAD_X = 42
GROUP_PAD_Y = 42
LABEL_CHAR_WIDTH = 7.0
LABEL_LINE_HEIGHT = 15
LABEL_PAD_X = 34
LABEL_PAD_Y = 28
COMPACT_SYMBOLS = {
    "initial_state",
    "final_state",
    "activity_final_node",
    "fork_node",
    "join_node",
}


def view(spec: dict[str, Any], *, kind: str | None = None, default_symbol: str | None = None) -> dict[str, Any]:
    view_kind = kind or spec.get("kind", "GeneralView")
    symbol_default = default_symbol or spec.get("default_symbol") or VIEW_DEFAULT_SYMBOL.get(view_kind, "part_usage")
    direction = spec.get("direction", "left-right")
    default_w = int(spec.get("default_w", 150))
    default_h = int(spec.get("default_h", 70))
    col_gap = int(spec.get("col_gap", 110))
    rank_gap = int(spec.get("rank_gap", 160))
    nodes: dict[str, dict[str, Any]] = spec.get("nodes", {})
    edges: list[dict[str, Any]] = spec.get("edges", [])
    nids = list(nodes)

    boxes = _node_boxes(
        nodes,
        edges,
        nids,
        direction,
        default_w,
        default_h,
        col_gap,
        rank_gap,
        spec.get("rank_wrap"),
    )
    connections = [
        _edge_connection(edge, boxes, nodes=nodes, direction=direction, view_kind=view_kind)
        for edge in edges
        if edge.get("from") in boxes and edge.get("to") in boxes
    ]

    group_boxes = _group_boxes(spec.get("groups", []), boxes)
    bounds = _bounds([*boxes.values(), *group_boxes.values()], connections)
    shift_x = MARGIN - bounds[0]
    shift_y = MARGIN - bounds[1]
    if shift_x or shift_y:
        boxes = {node_id: _shift_box(box, shift_x, shift_y) for node_id, box in boxes.items()}
        group_boxes = {group_id: _shift_box(box, shift_x, shift_y) for group_id, box in group_boxes.items()}
        for connection in connections:
            for point in connection["route"]["waypoints"]:
                point["x"] = _clean(point["x"] + shift_x)
                point["y"] = _clean(point["y"] + shift_y)
    width = _clean(bounds[2] - bounds[0] + MARGIN * 2)
    height = _clean(bounds[3] - bounds[1] + MARGIN * 2)

    elements: list[dict[str, Any]] = []
    for group in spec.get("groups", []):
        group_id = group["id"]
        x, y, w, h = group_boxes[group_id]
        elements.append({
            "id": group_id,
            "model_ref": group.get("model_ref", spec.get("subject", group_id)),
            "symbol": group.get("symbol", "boundary"),
            "layout": {"x": x, "y": y, "width": w, "height": h, "z": group.get("z", 0)},
            "label": group.get("label", group_id),
            "style": group.get("style", "boundary.system"),
        })

    for node_id in nids:
        node = nodes[node_id]
        symbol = node.get("symbol", symbol_default)
        x, y, w, h = boxes[node_id]
        elements.append({
            "id": node_id,
            "model_ref": node.get("model_ref", node_id),
            "symbol": symbol,
            "layout": {"x": x, "y": y, "width": w, "height": h, "z": node.get("z", 10)},
            "label": node.get("label", node_id),
            "style": node.get("style", symbol),
        })

    diagram_id = spec.get("diagram", f"{view_kind.lower()}-view")
    diagram: dict[str, Any] = {
        "id": diagram_id,
        "kind": view_kind,
        "name": spec.get("name", diagram_id),
        "canvas": {"width": width, "height": height, "background": spec.get("background", "#FFFFFF")},
        "frame": {"visible": True},
        "elements": elements,
        "connections": connections,
        "annotations": spec.get("annotations", []),
        "styles": spec.get("styles", {}),
    }
    if spec.get("subject"):
        diagram["subject"] = spec["subject"]
    return {
        "$schema": "../../schemas/sysmld.schema.json",
        "version": "0.1",
        "mode": spec.get("mode", "model_based"),
        "model_files": spec.get("model_files", []),
        "aliases": spec.get("aliases", {}),
        "diagram": diagram,
    }


def interaction(spec: dict[str, Any]) -> dict[str, Any]:
    """Compose a simple sequence-style interaction view."""

    lifelines: dict[str, dict[str, Any]] = spec.get("lifelines", {})
    messages: list[dict[str, Any]] = spec.get("messages", [])
    spacing_x = int(spec.get("spacing_x", 90))
    message_gap = int(spec.get("message_gap", 54))
    top = int(spec.get("top", 70))
    left = int(spec.get("left", 70))
    height = top + 60 + max(1, len(messages)) * message_gap + 50
    elements = []
    centers: dict[str, float] = {}
    cursor_x = left
    lifeline_widths = {
        line_id: max(110, _label_size(str(line.get("label", line_id)))[0] + 12)
        for line_id, line in lifelines.items()
    }
    for line_id, line in lifelines.items():
        width = lifeline_widths[line_id]
        x = cursor_x
        centers[line_id] = x + width / 2
        elements.append({
            "id": line_id,
            "model_ref": line.get("model_ref", line_id),
            "symbol": "lifeline",
            "layout": {"x": x, "y": top, "width": width, "height": height - top - 40, "z": 10},
            "label": line.get("label", line_id),
            "style": line.get("style", "lifeline"),
        })
        cursor_x += width + spacing_x

    connections = []
    for index, message in enumerate(messages):
        src = message["from"]
        tgt = message["to"]
        y = top + 70 + index * message_gap
        source_side = "right" if centers[src] <= centers[tgt] else "left"
        target_side = "left" if source_side == "right" else "right"
        if src == tgt:
            source_side = "right"
            target_side = "right"
            waypoints = [
                {"x": _clean(centers[src] + 70), "y": y},
                {"x": _clean(centers[src] + 70), "y": y + 28},
            ]
            target_offset = (y + 28 - top) / (height - top - 40)
        else:
            waypoints = []
            target_offset = (y - top) / (height - top - 40)
        source_offset = (y - top) / (height - top - 40)
        connections.append({
            "id": message.get("id", f"msg-{index + 1}"),
            "model_ref": message.get("model_ref", message.get("id", src)),
            "source": {"element": src, "anchor": {"side": source_side, "offset": _clean(source_offset)}},
            "target": {"element": tgt, "anchor": {"side": target_side, "offset": _clean(target_offset)}},
            "route": {"kind": "orthogonal", "waypoints": waypoints},
            "labels": [{"text": message.get("label", ""), "position": {"offset": 0.5, "placement": "centerline"}}],
            "style": message.get("style", "message.return" if message.get("return") else "message"),
        })

    width = cursor_x - spacing_x + left if lifelines else left * 2 + 110
    diagram_id = spec.get("diagram", "interaction-view")
    diagram: dict[str, Any] = {
        "id": diagram_id,
        "kind": "InteractionView",
        "name": spec.get("name", diagram_id),
        "canvas": {"width": width, "height": height, "background": spec.get("background", "#FFFFFF")},
        "frame": {"visible": True},
        "elements": elements,
        "connections": connections,
        "annotations": spec.get("annotations", []),
        "styles": spec.get("styles", {}),
    }
    if spec.get("subject"):
        diagram["subject"] = spec["subject"]
    return {
        "$schema": "../../schemas/sysmld.schema.json",
        "version": "0.1",
        "mode": spec.get("mode", "model_based"),
        "model_files": spec.get("model_files", []),
        "aliases": spec.get("aliases", {}),
        "diagram": diagram,
    }


def action(spec: dict[str, Any]) -> dict[str, Any]:
    """Compose an activity/action view with sequence-preserving layout.

    Activity diagrams are behavioral traces, so the primary ordering must be
    the action sequence.  A generic graph layout can make a compact picture
    while scrambling the reading order; this layout keeps adjacent actions
    adjacent, defaults to top-to-bottom portrait flow, and puts loopback flows
    into open channels.
    """

    view_kind = "ActionView"
    symbol_default = spec.get("default_symbol") or VIEW_DEFAULT_SYMBOL[view_kind]
    default_w = int(spec.get("default_w", 150))
    default_h = int(spec.get("default_h", 64))
    direction = spec.get("direction", "top-down")
    col_gap = int(spec.get("col_gap", 90))
    row_gap = int(spec.get("rank_gap", spec.get("row_gap", 96)))
    nodes: dict[str, dict[str, Any]] = spec.get("nodes", {})
    edges: list[dict[str, Any]] = spec.get("edges", [])
    nids = _action_order(nodes, edges)
    boxes, row_bottoms, next_row_tops, bands = _action_boxes(
        nodes,
        nids,
        symbol_default,
        default_w,
        default_h,
        col_gap,
        row_gap,
        direction,
        spec.get("columns"),
        spec.get("rows_per_column"),
    )
    order = {node_id: index for index, node_id in enumerate(nids)}
    loop_counts: dict[int, int] = defaultdict(int)
    connections = [
        _action_edge_connection(edge, boxes, order, bands, row_bottoms, next_row_tops, loop_counts)
        for edge in edges
        if edge.get("from") in boxes and edge.get("to") in boxes
    ]

    group_boxes = _group_boxes(spec.get("groups", []), boxes)
    bounds = _bounds([*boxes.values(), *group_boxes.values()], connections)
    shift_x = MARGIN - bounds[0]
    shift_y = MARGIN - bounds[1]
    if shift_x or shift_y:
        boxes = {node_id: _shift_box(box, shift_x, shift_y) for node_id, box in boxes.items()}
        group_boxes = {group_id: _shift_box(box, shift_x, shift_y) for group_id, box in group_boxes.items()}
        for connection in connections:
            for point in connection["route"]["waypoints"]:
                point["x"] = _clean(point["x"] + shift_x)
                point["y"] = _clean(point["y"] + shift_y)
    width = _clean(bounds[2] - bounds[0] + MARGIN * 2)
    height = _clean(bounds[3] - bounds[1] + MARGIN * 2)

    elements: list[dict[str, Any]] = []
    for group in spec.get("groups", []):
        group_id = group["id"]
        x, y, w, h = group_boxes[group_id]
        elements.append({
            "id": group_id,
            "model_ref": group.get("model_ref", spec.get("subject", group_id)),
            "symbol": group.get("symbol", "boundary"),
            "layout": {"x": x, "y": y, "width": w, "height": h, "z": group.get("z", 0)},
            "label": group.get("label", group_id),
            "style": group.get("style", "boundary.system"),
        })

    for node_id in nids:
        node = nodes[node_id]
        symbol = node.get("symbol", symbol_default)
        x, y, w, h = boxes[node_id]
        elements.append({
            "id": node_id,
            "model_ref": node.get("model_ref", node_id),
            "symbol": symbol,
            "layout": {"x": x, "y": y, "width": w, "height": h, "z": node.get("z", 10)},
            "label": node.get("label", node_id),
            "style": node.get("style", symbol),
        })

    diagram_id = spec.get("diagram", "action-view")
    diagram: dict[str, Any] = {
        "id": diagram_id,
        "kind": view_kind,
        "name": spec.get("name", diagram_id),
        "canvas": {"width": width, "height": height, "background": spec.get("background", "#FFFFFF")},
        "frame": {"visible": True},
        "elements": elements,
        "connections": connections,
        "annotations": spec.get("annotations", []),
        "styles": spec.get("styles", {}),
    }
    if spec.get("subject"):
        diagram["subject"] = spec["subject"]
    return {
        "$schema": "../../schemas/sysmld.schema.json",
        "version": "0.1",
        "mode": spec.get("mode", "model_based"),
        "model_files": spec.get("model_files", []),
        "aliases": spec.get("aliases", {}),
        "diagram": diagram,
    }


def view_file(input_path: Path, output_path: Path | None = None, *, kind: str | None = None, default_symbol: str | None = None) -> Path:
    spec = json.loads(input_path.read_text(encoding="utf-8"))
    result = view(spec, kind=kind, default_symbol=default_symbol)
    target = output_path or input_path.with_suffix(".sysmld")
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return target


def action_file(input_path: Path, output_path: Path | None = None) -> Path:
    spec = json.loads(input_path.read_text(encoding="utf-8"))
    result = action(spec)
    target = output_path or input_path.with_suffix(".sysmld")
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return target


def interaction_file(input_path: Path, output_path: Path | None = None) -> Path:
    spec = json.loads(input_path.read_text(encoding="utf-8"))
    result = interaction(spec)
    target = output_path or input_path.with_suffix(".sysmld")
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return target


def _action_order(nodes: dict[str, dict[str, Any]], edges: list[dict[str, Any]]) -> list[str]:
    nids = list(nodes)
    if all("rank" in nodes[node_id] for node_id in nids):
        return sorted(nids, key=lambda node_id: (int(nodes[node_id].get("rank", 0)), nodes[node_id].get("order", 0), node_id))

    incoming = {node_id: 0 for node_id in nids}
    outgoing: dict[str, list[str]] = {node_id: [] for node_id in nids}
    for edge in edges:
        src = edge.get("from")
        tgt = edge.get("to")
        if src in incoming and tgt in incoming and src != tgt:
            outgoing[src].append(tgt)
            incoming[tgt] += 1
    ready = [node_id for node_id in nids if incoming[node_id] == 0]
    ready.sort(key=nids.index)
    order: list[str] = []
    while ready:
        node_id = ready.pop(0)
        order.append(node_id)
        for target in sorted(outgoing[node_id], key=nids.index):
            incoming[target] -= 1
            if incoming[target] == 0:
                ready.append(target)
        ready.sort(key=nids.index)
    order.extend(node_id for node_id in nids if node_id not in order)
    return order


def _action_column_count(node_count: int, explicit_columns: Any = None, direction: str = "left-right") -> int:
    if explicit_columns:
        return max(1, int(explicit_columns))
    if direction in {"top-down", "bottom-up"}:
        return 1
    if node_count <= 3:
        return node_count
    return min(5, max(2, int((node_count * 1.25) ** 0.5 + 0.999)))


def _action_rows_per_column(node_count: int, columns: int, explicit_rows: Any = None) -> int:
    if explicit_rows:
        return max(1, int(explicit_rows))
    return max(1, (node_count + columns - 1) // columns)


def _action_boxes(
    nodes: dict[str, dict[str, Any]],
    nids: list[str],
    symbol_default: str,
    default_w: int,
    default_h: int,
    col_gap: int,
    row_gap: int,
    direction: str,
    explicit_columns: Any = None,
    explicit_rows: Any = None,
) -> tuple[dict[str, tuple[float, float, float, float]], dict[int, float], dict[int, float], dict[str, int]]:
    columns = _action_column_count(len(nids), explicit_columns, direction)
    rows_per_column = _action_rows_per_column(len(nids), columns, explicit_rows)
    sizes = {
        node_id: _node_size({**nodes[node_id], "symbol": nodes[node_id].get("symbol", symbol_default)}, default_w, default_h)
        for node_id in nids
    }
    cell_positions: dict[str, tuple[int, int]] = {}
    for index, node_id in enumerate(nids):
        if direction in {"top-down", "bottom-up"}:
            col = index // rows_per_column
            row_in_sequence = index % rows_per_column
            row = row_in_sequence if col % 2 == 0 else rows_per_column - 1 - row_in_sequence
        else:
            row = index // columns
            col_in_sequence = index % columns
            col = col_in_sequence if row % 2 == 0 else columns - 1 - col_in_sequence
        cell_positions[node_id] = (row, col)

    row_count = max((row for row, _col in cell_positions.values()), default=0) + 1
    col_widths = [0] * columns
    row_heights = [0] * row_count
    for node_id, (row, col) in cell_positions.items():
        width, height = sizes[node_id]
        col_widths[col] = max(col_widths[col], width)
        row_heights[row] = max(row_heights[row], height)

    x_by_col: list[float] = []
    cursor_x = 0.0
    for width in col_widths:
        x_by_col.append(cursor_x)
        cursor_x += width + col_gap

    y_by_row: list[float] = []
    cursor_y = 0.0
    for height in row_heights:
        y_by_row.append(cursor_y)
        cursor_y += height + row_gap

    boxes: dict[str, tuple[float, float, float, float]] = {}
    for node_id, (row, col) in cell_positions.items():
        width, height = sizes[node_id]
        x = x_by_col[col] + (col_widths[col] - width) / 2
        y = y_by_row[row] + (row_heights[row] - height) / 2
        boxes[node_id] = (_clean(x), _clean(y), width, height)

    row_bottoms = {
        row: y_by_row[row] + row_heights[row]
        for row in range(row_count)
    }
    next_row_tops = {
        row: y_by_row[row + 1]
        for row in range(row_count - 1)
    }
    bands = {
        node_id: cell_positions[node_id][0]
        for node_id in nids
    }
    return boxes, row_bottoms, next_row_tops, bands


def _action_edge_connection(
    edge: dict[str, Any],
    boxes: dict[str, tuple[float, float, float, float]],
    order: dict[str, int],
    rows: dict[str, int],
    row_bottoms: dict[int, float],
    next_row_tops: dict[int, float],
    loop_counts: dict[int, int],
) -> dict[str, Any]:
    src = edge["from"]
    tgt = edge["to"]
    if order[tgt] < order[src]:
        source_side, target_side, waypoints = _action_loop_route(edge, boxes, rows, row_bottoms, next_row_tops, loop_counts)
    else:
        source_side, target_side = _sides(boxes[src], boxes[tgt], edge)
        source_point = _anchor_point(boxes[src], source_side)
        target_point = _anchor_point(boxes[tgt], target_side)
        waypoints = edge.get("waypoints")
        if waypoints is None:
            waypoints = _orthogonal_waypoints(source_point, target_point, source_side, target_side)

    labels = []
    if edge.get("label", ""):
        labels.append({"text": edge["label"], "position": {"offset": 0.5, "placement": "centerline"}})
    return {
        "id": edge.get("id", f"conn-{src}-{tgt}"),
        "model_ref": edge.get("model_ref", src),
        "source": {"element": src, "anchor": {"side": source_side, "offset": _clean(float(edge.get("source_offset", 0.5)))}},
        "target": {"element": tgt, "anchor": {"side": target_side, "offset": _clean(float(edge.get("target_offset", 0.5)))}},
        "route": {"kind": "orthogonal", "waypoints": waypoints},
        "labels": labels,
        "style": edge.get("style", "connector.control_flow"),
    }


def _action_loop_route(
    edge: dict[str, Any],
    boxes: dict[str, tuple[float, float, float, float]],
    rows: dict[str, int],
    row_bottoms: dict[int, float],
    next_row_tops: dict[int, float],
    loop_counts: dict[int, int],
) -> tuple[str, str, list[dict[str, float]]]:
    src = edge["from"]
    tgt = edge["to"]
    source_row = rows[src]
    target_row = rows[tgt]
    if source_row == target_row:
        source_side = edge.get("source_side", "bottom")
        target_side = edge.get("target_side", "bottom")
        loop_counts[source_row] += 1
        lower_limit = next_row_tops.get(source_row)
        base_y = row_bottoms[source_row] + 28 * loop_counts[source_row]
        if lower_limit is not None:
            base_y = min(base_y, lower_limit - 24)
        source_point = _anchor_point(boxes[src], source_side)
        target_point = _anchor_point(boxes[tgt], target_side)
        return source_side, target_side, [
            {"x": _clean(source_point[0]), "y": _clean(base_y)},
            {"x": _clean(target_point[0]), "y": _clean(base_y)},
        ]

    left = min(box[0] for box in boxes.values())
    right = max(box[0] + box[2] for box in boxes.values())
    src_center = _center(boxes[src])[0]
    tgt_center = _center(boxes[tgt])[0]
    use_right = src_center >= tgt_center
    default_side = "right" if use_right else "left"
    source_side = edge.get("source_side") if edge.get("source_side") in {"left", "right"} else default_side
    target_side = edge.get("target_side") if edge.get("target_side") in {"left", "right"} else default_side
    lane_x = (right + 44) if use_right else (left - 44)
    source_point = _anchor_point(boxes[src], source_side)
    target_point = _anchor_point(boxes[tgt], target_side)
    return source_side, target_side, [
        {"x": _clean(lane_x), "y": _clean(source_point[1])},
        {"x": _clean(lane_x), "y": _clean(target_point[1])},
    ]


def _node_boxes(
    nodes: dict[str, dict[str, Any]],
    edges: list[dict[str, Any]],
    nids: list[str],
    direction: str,
    default_w: int,
    default_h: int,
    col_gap: int,
    rank_gap: int,
    rank_wrap: str | None = None,
) -> dict[str, tuple[float, float, float, float]]:
    fixed_ranks = all("rank" in nodes[node_id] for node_id in nids) and not rank_wrap
    sizes = {node_id: _node_size(nodes[node_id], default_w, default_h) for node_id in nids}
    if fixed_ranks:
        rank_groups: dict[int, list[str]] = defaultdict(list)
        for node_id in nids:
            rank_groups[int(nodes[node_id]["rank"])].append(node_id)
        for group in rank_groups.values():
            group.sort(key=lambda node_id: (nodes[node_id].get("order", 0), node_id))
        boxes = {}
        vertical = direction in {"top-down", "bottom-up"}
        primary_by_rank: dict[int, float] = {}
        cursor = 0.0
        for rank in sorted(rank_groups):
            primary_by_rank[rank] = cursor
            max_primary = max(sizes[node_id][1 if vertical else 0] for node_id in rank_groups[rank])
            cursor += max_primary + rank_gap
        for rank in sorted(rank_groups):
            group = rank_groups[rank]
            total_cross = sum(sizes[node_id][0 if vertical else 1] for node_id in group) + col_gap * max(0, len(group) - 1)
            cross = -total_cross / 2
            for node_id in group:
                w, h = sizes[node_id]
                if vertical:
                    x = cross
                    y = primary_by_rank[rank]
                    cross += w + col_gap
                else:
                    x = primary_by_rank[rank]
                    y = cross
                    cross += h + col_gap
                boxes[node_id] = (x, y, w, h)
        return boxes

    avg_w = sum(width for width, _height in sizes.values()) / max(len(sizes), 1)
    avg_h = sum(height for _width, height in sizes.values()) / max(len(sizes), 1)
    layout = _layout(
        nids,
        edges,
        direction,
        col_gap=int(col_gap + avg_w),
        rank_gap=int(rank_gap + avg_h),
        margin=max(default_w, default_h),
        rank_wrap=rank_wrap,
    )
    return {
        node_id: (
            layout.cx[node_id] - sizes[node_id][0] / 2,
            layout.cy[node_id] - sizes[node_id][1] / 2,
            sizes[node_id][0],
            sizes[node_id][1],
        )
        for node_id in nids
    }


def _node_size(node: dict[str, Any], default_w: int, default_h: int) -> tuple[int, int]:
    symbol_w, symbol_h = SYMBOL_SIZE.get(node.get("symbol", ""), (default_w, default_h))
    explicit_w = int(node["w"]) if "w" in node else None
    explicit_h = int(node["h"]) if "h" in node else None
    label_w, label_h = _label_size(str(node.get("label", node.get("id", ""))))
    if node.get("symbol") in COMPACT_SYMBOLS:
        return explicit_w or symbol_w, explicit_h or symbol_h
    if node.get("symbol") in SYMBOL_SIZE:
        width = max(explicit_w or symbol_w, label_w)
        height = max(explicit_h or symbol_h, label_h)
        return width, height
    width = max(explicit_w or default_w, symbol_w, label_w)
    height = max(explicit_h or default_h, symbol_h, label_h)
    return width, height


def _label_size(label: str) -> tuple[int, int]:
    lines = str(label).splitlines() or [""]
    longest = max((len(line) for line in lines), default=0)
    return (
        int(longest * LABEL_CHAR_WIDTH + LABEL_PAD_X),
        int(len(lines) * LABEL_LINE_HEIGHT + LABEL_PAD_Y),
    )


def _edge_connection(
    edge: dict[str, Any],
    boxes: dict[str, tuple[float, float, float, float]],
    *,
    nodes: dict[str, dict[str, Any]] | None = None,
    direction: str | None = None,
    view_kind: str = "GeneralView",
) -> dict[str, Any]:
    src = edge["from"]
    tgt = edge["to"]
    source_side, target_side = _rank_sides(edge, nodes, direction) or _sides(boxes[src], boxes[tgt], edge)
    source_offset = float(edge.get("source_offset", 0.5))
    target_offset = float(edge.get("target_offset", 0.5))
    source_point = _anchor_point(boxes[src], source_side, source_offset)
    target_point = _anchor_point(boxes[tgt], target_side, target_offset)
    waypoints = edge.get("waypoints")
    if waypoints is None:
        if view_kind == "ConstraintView" and str(edge.get("label", "")).lower() == "bind":
            waypoints = []
        else:
            waypoints = _orthogonal_waypoints_avoiding_boxes(source_point, target_point, source_side, target_side, boxes, src, tgt)
    labels = []
    if edge.get("label", ""):
        labels.append({"text": edge["label"], "position": {"offset": 0.5, "placement": "centerline"}})
    return {
        "id": edge.get("id", f"conn-{src}-{tgt}"),
        "model_ref": edge.get("model_ref", src),
        "source": {"element": src, "anchor": {"side": source_side, "offset": _clean(source_offset)}},
        "target": {"element": tgt, "anchor": {"side": target_side, "offset": _clean(target_offset)}},
        "route": {"kind": _default_route_kind(view_kind, edge), "waypoints": waypoints},
        "labels": labels,
        "style": edge.get("style", _default_edge_style(view_kind, edge)),
    }


def _default_edge_style(view_kind: str, edge: dict[str, Any]) -> str:
    if view_kind == "AllocationView":
        return "connector.allocation"
    if view_kind == "FlowView":
        return "connector.flow"
    if view_kind == "GeneralView":
        return "connector.directed"
    if view_kind == "ConstraintView" and str(edge.get("label", "")).lower() != "bind":
        return "connector.directed"
    return "connector.default"


def _default_route_kind(view_kind: str, edge: dict[str, Any]) -> str:
    if view_kind == "ConstraintView" and str(edge.get("label", "")).lower() == "bind":
        return "polyline"
    return "orthogonal"


def _rank_sides(
    edge: dict[str, Any],
    nodes: dict[str, dict[str, Any]] | None,
    direction: str | None,
) -> tuple[str, str] | None:
    if edge.get("source_side") and edge.get("target_side"):
        return None
    if not nodes or edge.get("from") not in nodes or edge.get("to") not in nodes:
        return None
    source = nodes[edge["from"]]
    target = nodes[edge["to"]]
    if "rank" not in source or "rank" not in target:
        return None
    source_rank = int(source["rank"])
    target_rank = int(target["rank"])
    if source_rank == target_rank:
        return None
    if direction in {"top-down", "bottom-up"}:
        forward = target_rank > source_rank
        if direction == "bottom-up":
            forward = not forward
        return ("bottom", "top") if forward else ("top", "bottom")
    if direction in {"left-right", "right-left"}:
        forward = target_rank > source_rank
        if direction == "right-left":
            forward = not forward
        return ("right", "left") if forward else ("left", "right")
    return None


def _sides(
    src_box: tuple[float, float, float, float],
    tgt_box: tuple[float, float, float, float],
    edge: dict[str, Any],
) -> tuple[str, str]:
    if edge.get("source_side") and edge.get("target_side"):
        return edge["source_side"], edge["target_side"]
    sx, sy = _center(src_box)
    tx, ty = _center(tgt_box)
    if abs(tx - sx) >= abs(ty - sy):
        return ("right", "left") if tx >= sx else ("left", "right")
    return ("bottom", "top") if ty >= sy else ("top", "bottom")


def _orthogonal_waypoints(
    src: tuple[float, float],
    tgt: tuple[float, float],
    source_side: str,
    target_side: str,
) -> list[dict[str, float]]:
    sx, sy = src
    tx, ty = tgt
    if source_side in {"left", "right"} and target_side in {"left", "right"}:
        if abs(sy - ty) < 1:
            return []
        mid_x = (sx + tx) / 2
        return [{"x": _clean(mid_x), "y": _clean(sy)}, {"x": _clean(mid_x), "y": _clean(ty)}]
    if source_side in {"top", "bottom"} and target_side in {"top", "bottom"}:
        if abs(sx - tx) < 1:
            return []
        mid_y = (sy + ty) / 2
        return [{"x": _clean(sx), "y": _clean(mid_y)}, {"x": _clean(tx), "y": _clean(mid_y)}]
    elbow = (tx, sy) if source_side in {"left", "right"} else (sx, ty)
    return [{"x": _clean(elbow[0]), "y": _clean(elbow[1])}]


def _orthogonal_waypoints_avoiding_boxes(
    src: tuple[float, float],
    tgt: tuple[float, float],
    source_side: str,
    target_side: str,
    boxes: dict[str, tuple[float, float, float, float]],
    source_id: str,
    target_id: str,
) -> list[dict[str, float]]:
    sx, sy = src
    tx, ty = tgt
    obstacles = {
        node_id: box
        for node_id, box in boxes.items()
        if node_id not in {source_id, target_id}
    }
    if source_side in {"left", "right"} and target_side in {"left", "right"}:
        if abs(sy - ty) < 1:
            if not _route_crosses_obstacle([src, tgt], obstacles):
                return []
            for lane_y in _detour_candidates("y", sy, obstacles):
                points = [(sx, lane_y), (tx, lane_y)]
                if not _route_crosses_obstacle([src, *points, tgt], obstacles):
                    return _clean_waypoints(points)
            return []
        for lane_x in _lane_candidates("x", sx, tx, obstacles):
            points = [(lane_x, sy), (lane_x, ty)]
            if not _route_crosses_obstacle([src, *points, tgt], obstacles):
                return _clean_waypoints(points)
    elif source_side in {"top", "bottom"} and target_side in {"top", "bottom"}:
        if abs(sx - tx) < 1:
            if not _route_crosses_obstacle([src, tgt], obstacles):
                return []
            for lane_x in _detour_candidates("x", sx, obstacles):
                points = [(lane_x, sy), (lane_x, ty)]
                if not _route_crosses_obstacle([src, *points, tgt], obstacles):
                    return _clean_waypoints(points)
            return []
        for lane_y in _lane_candidates("y", sy, ty, obstacles):
            points = [(sx, lane_y), (tx, lane_y)]
            if not _route_crosses_obstacle([src, *points, tgt], obstacles):
                return _clean_waypoints(points)
    else:
        preferred = (tx, sy) if source_side in {"left", "right"} else (sx, ty)
        alternate = (sx, ty) if source_side in {"left", "right"} else (tx, sy)
        candidates = [preferred, alternate]
        candidates.sort(key=lambda point: abs(point[0] - preferred[0]) + abs(point[1] - preferred[1]))
        for elbow in candidates:
            if not _route_crosses_obstacle([src, elbow, tgt], obstacles):
                return _clean_waypoints([elbow])
    return _orthogonal_waypoints(src, tgt, source_side, target_side)


def _detour_candidates(
    axis: str,
    center: float,
    boxes: dict[str, tuple[float, float, float, float]],
) -> list[float]:
    extents = []
    for box in boxes.values():
        x, y, w, h = box
        extents.append((x, x + w) if axis == "x" else (y, y + h))
    if not extents:
        return [center + 56, center - 56]
    low = min(first for first, _second in extents)
    high = max(second for _first, second in extents)
    candidates = [high + 44, low - 44, center + 56, center - 56, center + 96, center - 96]
    unique = []
    seen = set()
    for value in candidates:
        key = round(value, 3)
        if key not in seen:
            unique.append(value)
            seen.add(key)
    return unique


def _lane_candidates(
    axis: str,
    start: float,
    end: float,
    boxes: dict[str, tuple[float, float, float, float]],
) -> list[float]:
    low, high = sorted((start, end))
    midpoint = (start + end) / 2
    direction = 1 if end >= start else -1
    candidates = [
        midpoint,
        start + direction * 56,
        end - direction * 56,
        start + direction * 84,
        end - direction * 84,
    ]
    intervals = []
    for box in boxes.values():
        x, y, w, h = box
        intervals.append((x, x + w) if axis == "x" else (y, y + h))
    stops = sorted({low, high, *[value for interval in intervals for value in interval]})
    for first, second in zip(stops, stops[1:]):
        if second <= low or first >= high:
            continue
        gap_low = max(first, low)
        gap_high = min(second, high)
        if gap_high - gap_low >= 28:
            candidates.append((gap_low + gap_high) / 2)

    unique = []
    seen = set()
    for value in candidates:
        if value <= low + 8 or value >= high - 8:
            continue
        key = round(value, 3)
        if key not in seen:
            unique.append(value)
            seen.add(key)
    unique.sort(key=lambda value: (abs(value - (start + direction * 56)), abs(value - midpoint), value))
    return unique


def _route_crosses_obstacle(
    points: list[tuple[float, float]],
    obstacles: dict[str, tuple[float, float, float, float]],
) -> bool:
    for start, end in zip(points, points[1:]):
        for box in obstacles.values():
            if _segment_crosses_box_interior(start, end, box):
                return True
    return False


def _segment_crosses_box_interior(
    start: tuple[float, float],
    end: tuple[float, float],
    box: tuple[float, float, float, float],
) -> bool:
    x1, y1 = start
    x2, y2 = end
    left, top, width, height = box
    right = left + width
    bottom = top + height
    if round(x1) == round(x2):
        if x1 <= left or x1 >= right:
            return False
        return max(y1, y2) > top and min(y1, y2) < bottom
    if round(y1) == round(y2):
        if y1 <= top or y1 >= bottom:
            return False
        return max(x1, x2) > left and min(x1, x2) < right
    return True


def _group_boxes(groups: list[dict[str, Any]], boxes: dict[str, tuple[float, float, float, float]]) -> dict[str, tuple[float, float, float, float]]:
    output = {}
    for group in groups:
        members = [boxes[member] for member in group.get("members", []) if member in boxes]
        if not members:
            continue
        left = min(box[0] for box in members) - group.get("pad_x", GROUP_PAD_X)
        top = min(box[1] for box in members) - group.get("pad_y", GROUP_PAD_Y)
        right = max(box[0] + box[2] for box in members) + group.get("pad_x", GROUP_PAD_X)
        bottom = max(box[1] + box[3] for box in members) + group.get("pad_y", GROUP_PAD_Y)
        output[group["id"]] = (left, top, right - left, bottom - top)
    return output


def _clean_waypoints(points: list[tuple[float, float]]) -> list[dict[str, float]]:
    return [{"x": _clean(x), "y": _clean(y)} for x, y in points]


def _bounds(
    boxes: list[tuple[float, float, float, float]],
    connections: list[dict[str, Any]],
) -> tuple[float, float, float, float]:
    xs = [box[0] for box in boxes] or [0]
    ys = [box[1] for box in boxes] or [0]
    x2 = [box[0] + box[2] for box in boxes] or [1]
    y2 = [box[1] + box[3] for box in boxes] or [1]
    for connection in connections:
        for point in connection["route"]["waypoints"]:
            xs.append(point["x"])
            ys.append(point["y"])
            x2.append(point["x"])
            y2.append(point["y"])
    return min(xs), min(ys), max(x2), max(y2)


def _anchor_point(box: tuple[float, float, float, float], side: str, offset: float = 0.5) -> tuple[float, float]:
    x, y, w, h = box
    if side == "left":
        return x, y + h * offset
    if side == "right":
        return x + w, y + h * offset
    if side == "top":
        return x + w * offset, y
    return x + w * offset, y + h


def _center(box: tuple[float, float, float, float]) -> tuple[float, float]:
    return box[0] + box[2] / 2, box[1] + box[3] / 2


def _shift_box(box: tuple[float, float, float, float], dx: float, dy: float) -> tuple[float, float, float, float]:
    return _clean(box[0] + dx), _clean(box[1] + dy), box[2], box[3]


def _clean(value: float) -> float:
    rounded = round(value, 3)
    return int(rounded) if float(rounded).is_integer() else rounded
