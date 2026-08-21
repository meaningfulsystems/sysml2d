"""Generate DefinitionView tree diagrams from a compact tree intent file."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

from .routing import orthogonal_path_avoiding_boxes, path_crosses_boxes, segment_crosses_box_interior


CANVAS_MARGIN = 40
DEFAULT_NODE_W = 170
DEFAULT_NODE_H = 72
DEFAULT_SIBLING_GAP = 48
DEFAULT_RANK_GAP = 100
DEFAULT_ROW_GAP = 28
DEFAULT_MAX_SIBLINGS_PER_ROW = 6


@dataclass
class TreeNode:
    id: str
    label: str
    model_ref: str
    part_ref: str | None
    multiplicity: str
    style: str
    width: int
    height: int
    max_siblings_per_row: int | None = None
    children: list["TreeNode"] = field(default_factory=list)


def compose_tree(spec: dict[str, Any]) -> dict[str, Any]:
    direction = spec.get("direction", "top-down")
    if direction not in {"top-down", "bottom-up", "left-right", "right-left"}:
        raise ValueError(f"unsupported tree direction: {direction}")

    default_w = int(spec.get("default_w", DEFAULT_NODE_W))
    default_h = int(spec.get("default_h", DEFAULT_NODE_H))
    sibling_gap = int(spec.get("sibling_gap", DEFAULT_SIBLING_GAP))
    rank_gap = int(spec.get("rank_gap", DEFAULT_RANK_GAP))
    row_gap = int(spec.get("row_gap", DEFAULT_ROW_GAP))
    max_siblings_per_row = int(spec.get("max_siblings_per_row", DEFAULT_MAX_SIBLINGS_PER_ROW))
    roots = [_read_node(raw, default_w, default_h, spec.get("node_style", "part.definition")) for raw in spec.get("roots", [])]
    if not roots:
        raise ValueError("tree intent requires at least one root")

    node_order: list[TreeNode] = []
    _flatten_roots(roots, node_order)
    _validate_unique_node_ids(node_order)

    subtree_widths: dict[str, float] = {}
    for root in roots:
        _subtree_width(root, sibling_gap, max_siblings_per_row, subtree_widths)

    positions: dict[str, tuple[float, float]] = {}
    cursor = 0.0
    for root in roots:
        width = subtree_widths[root.id]
        _place(
            root,
            cursor + width / 2,
            0,
            sibling_gap,
            rank_gap,
            row_gap,
            max_siblings_per_row,
            subtree_widths,
            positions,
        )
        cursor += width + sibling_gap

    boxes = _oriented_boxes(node_order, positions, direction)
    min_x = min(x for x, _y, _w, _h in boxes.values())
    min_y = min(y for _x, y, _w, _h in boxes.values())
    if min_x != CANVAS_MARGIN or min_y != CANVAS_MARGIN:
        shift_x = CANVAS_MARGIN - min_x
        shift_y = CANVAS_MARGIN - min_y
        boxes = {
            node_id: (round(x + shift_x), round(y + shift_y), w, h)
            for node_id, (x, y, w, h) in boxes.items()
        }

    avoid_boxes = bool(spec.get("route_around_boxes"))
    break_column_spines = bool(spec.get("break_column_spines"))
    parent_of = {child.id: parent for parent in node_order for child in parent.children}
    connections = []
    for parent in node_order:
        for child in parent.children:
            connections.append(_connection(
                parent,
                child,
                boxes,
                direction,
                avoid_boxes=avoid_boxes,
                break_column_spines=break_column_spines,
                parent_of=parent_of,
            ))

    boxes, connections, canvas_w, canvas_h = _fit_canvas(boxes, connections)

    elements = []
    for node in node_order:
        x, y, w, h = boxes[node.id]
        elements.append({
            "id": node.id,
            "model_ref": node.model_ref,
            "symbol": "part_definition",
            "layout": {"x": x, "y": y, "width": w, "height": h, "z": 10},
            "label": node.label,
            "compartments": {"attributes": False, "ports": False, "actions": False},
            "style": node.style,
        })

    diagram_id = spec.get("diagram", "definition-tree")
    doc: dict[str, Any] = {
        "$schema": "../../schemas/sysmld.schema.json",
        "version": "0.1",
        "mode": "model_based",
        "model_files": spec.get("model_files", []),
        "aliases": spec.get("aliases", {}),
        "diagram": {
            "id": diagram_id,
            "kind": spec.get("kind", "DefinitionView"),
            "name": spec.get("name", diagram_id),
            "canvas": {
                "width": round(canvas_w),
                "height": round(canvas_h),
                "background": "#FFFFFF",
            },
            "frame": {"visible": True},
            "elements": elements,
            "connections": connections,
            "annotations": [],
            "styles": spec.get("styles", {}),
        },
    }
    if spec.get("subject"):
        doc["diagram"]["subject"] = spec["subject"]
    return doc


def tree_file(input_path: Path, output_path: Path | None = None) -> Path:
    with input_path.open(encoding="utf-8") as fh:
        spec = json.load(fh)
    result = compose_tree(spec)
    target = output_path or input_path.with_suffix(".sysmld")
    with target.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")
    return target


def _read_node(raw: dict[str, Any], default_w: int, default_h: int, default_style: str) -> TreeNode:
    node_id = str(raw["id"])
    label = str(raw.get("label", node_id))
    width = int(raw.get("w", max(default_w, _label_width(label))))
    height = int(raw.get("h", max(default_h, _label_height(label))))
    return TreeNode(
        id=node_id,
        label=label,
        model_ref=str(raw.get("model_ref", node_id)),
        part_ref=str(raw["part_ref"]) if "part_ref" in raw else None,
        multiplicity=str(raw.get("multiplicity", "1")),
        style=str(raw.get("style", default_style)),
        width=width,
        height=height,
        max_siblings_per_row=int(raw["max_siblings_per_row"]) if "max_siblings_per_row" in raw else None,
        children=[
            _read_node(child, default_w, default_h, default_style)
            for child in raw.get("children", [])
        ],
    )


def _label_width(label: str) -> int:
    longest = max((len(line) for line in str(label).splitlines()), default=1)
    return longest * 8 + 36


def _label_height(label: str) -> int:
    line_count = len(str(label).splitlines()) or 1
    return line_count * 15 + 28


def _flatten_roots(roots: list[TreeNode], output: list[TreeNode]) -> None:
    for root in roots:
        output.append(root)
        _flatten_roots(root.children, output)


def _validate_unique_node_ids(nodes: list[TreeNode]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for node in nodes:
        if node.id in seen:
            duplicates.add(node.id)
        seen.add(node.id)
    if duplicates:
        raise ValueError(f"duplicate tree node id(s): {', '.join(sorted(duplicates))}")


def _subtree_width(
    node: TreeNode,
    sibling_gap: int,
    max_siblings_per_row: int,
    widths: dict[str, float],
) -> float:
    if not node.children:
        widths[node.id] = node.width
        return node.width
    for child in node.children:
        _subtree_width(child, sibling_gap, max_siblings_per_row, widths)
    rows = _child_rows(node.children, _effective_max(node, max_siblings_per_row))
    if _later_wrap_needs_stack(rows):
        row_widths = [_row_base_width(row, sibling_gap, widths) for row in rows]
    else:
        row_widths = [_row_width(row, sibling_gap, widths, row_index, rows) for row_index, row in enumerate(rows)]
    widths[node.id] = max(node.width, *row_widths)
    return widths[node.id]


def _place(
    node: TreeNode,
    center_x: float,
    depth: int,
    sibling_gap: int,
    rank_gap: int,
    row_gap: int,
    max_siblings_per_row: int,
    subtree_widths: dict[str, float],
    positions: dict[str, tuple[float, float]],
) -> None:
    positions[node.id] = (center_x, depth * (node.height + rank_gap))
    if not node.children:
        return
    child_limit = _effective_max(node, max_siblings_per_row)
    rows = _child_rows(node.children, child_limit)
    row_step = node.height + row_gap
    stack_rows = _later_wrap_needs_stack(rows)
    next_depth = depth + 1
    for row_index, row in enumerate(rows):
        row_width = _row_base_width(row, sibling_gap, subtree_widths)
        stagger = 0 if stack_rows else _row_stagger(row, sibling_gap, subtree_widths, row_index, rows)
        cursor = center_x - row_width / 2 + stagger
        if stack_rows:
            row_depth = next_depth
        else:
            row_depth = depth + 1 + (row_index * row_step / (node.height + rank_gap))
        for child in row:
            child_width = subtree_widths[child.id]
            _place(
                child,
                cursor + child_width / 2,
                row_depth,
                sibling_gap,
                rank_gap,
                row_gap,
                max_siblings_per_row,
                subtree_widths,
                positions,
            )
            cursor += child_width + sibling_gap
        if stack_rows:
            next_depth = row_depth + max(
                _placed_depth(child, max_siblings_per_row) for child in row
            )


def _effective_max(node: TreeNode, default: int) -> int:
    if node.max_siblings_per_row is None:
        return default
    return node.max_siblings_per_row


def _placed_depth(node: TreeNode, max_siblings_per_row: int) -> int:
    if not node.children:
        return 1
    rows = _child_rows(node.children, _effective_max(node, max_siblings_per_row))
    if _later_wrap_needs_stack(rows):
        return 1 + sum(
            max(_placed_depth(child, max_siblings_per_row) for child in row)
            for row in rows
        )
    return 1 + max(_placed_depth(child, max_siblings_per_row) for child in node.children)


def _later_wrap_needs_stack(rows: list[list[TreeNode]]) -> bool:
    return any(any(child.children for child in row) for row in rows[1:])


def _child_rows(children: list[TreeNode], max_siblings_per_row: int) -> list[list[TreeNode]]:
    if not children:
        return []
    if len(children) <= max_siblings_per_row:
        return [children]
    row_count = (len(children) + max_siblings_per_row - 1) // max_siblings_per_row
    row_size = (len(children) + row_count - 1) // row_count
    rows = []
    for start in range(0, len(children), row_size):
        rows.append(children[start:start + row_size])
    return rows


def _row_width(
    row: list[TreeNode],
    sibling_gap: int,
    subtree_widths: dict[str, float],
    row_index: int,
    rows: list[list[TreeNode]],
) -> float:
    width = _row_base_width(row, sibling_gap, subtree_widths)
    return width + abs(_row_stagger(row, sibling_gap, subtree_widths, row_index, rows)) * 2


def _row_base_width(
    row: list[TreeNode],
    sibling_gap: int,
    subtree_widths: dict[str, float],
) -> float:
    if not row:
        return 0
    width = sum(subtree_widths[child.id] for child in row)
    width += sibling_gap * (len(row) - 1)
    return width


def _row_stagger(
    row: list[TreeNode],
    sibling_gap: int,
    subtree_widths: dict[str, float],
    row_index: int,
    rows: list[list[TreeNode]],
) -> float:
    if row_index % 2 == 0 or not row:
        return 0
    previous_row = rows[row_index - 1]
    if len(row) < len(previous_row):
        return 0
    average_width = sum(subtree_widths[child.id] for child in row) / len(row)
    return (average_width + sibling_gap) / 2


def _oriented_boxes(
    nodes: list[TreeNode],
    positions: dict[str, tuple[float, float]],
    direction: str,
) -> dict[str, tuple[int, int, int, int]]:
    boxes: dict[str, tuple[int, int, int, int]] = {}
    for node in nodes:
        cx, depth_pos = positions[node.id]
        if direction in {"top-down", "bottom-up"}:
            x = cx - node.width / 2
            y = depth_pos
            boxes[node.id] = (round(x), round(y), node.width, node.height)
        else:
            x = depth_pos
            y = cx - node.height / 2
            boxes[node.id] = (round(x), round(y), node.width, node.height)

    if direction == "bottom-up":
        max_bottom = max(y + h for _x, y, _w, h in boxes.values())
        boxes = {
            node_id: (x, round(max_bottom - (y + h)), w, h)
            for node_id, (x, y, w, h) in boxes.items()
        }
    elif direction == "right-left":
        max_right = max(x + w for x, _y, w, _h in boxes.values())
        boxes = {
            node_id: (round(max_right - (x + w)), y, w, h)
            for node_id, (x, y, w, h) in boxes.items()
        }
    return boxes


def _connection(
    parent: TreeNode,
    child: TreeNode,
    boxes: dict[str, tuple[int, int, int, int]],
    direction: str,
    avoid_boxes: bool = False,
    break_column_spines: bool = False,
    parent_of: dict[str, TreeNode] | None = None,
) -> dict[str, Any]:
    source_side, target_side = {
        "top-down": ("bottom", "top"),
        "bottom-up": ("top", "bottom"),
        "left-right": ("right", "left"),
        "right-left": ("left", "right"),
    }[direction]
    primary_target = _primary_child_anchor(parent, boxes, "top" if direction == "top-down" else target_side, direction)
    first_row_boxes = _first_row_child_boxes(parent, boxes, primary_target, direction)
    later_row = _is_later_row(boxes[child.id], primary_target, direction)
    side_rail = False
    if avoid_boxes and break_column_spines and direction == "top-down":
        if later_row and _stacked_under_first_row(boxes[child.id], first_row_boxes):
            target_side = "left" if _center_x(boxes[child.id]) <= _center_x(boxes[parent.id]) else "right"
            side_rail = True
        elif _has_sibling_blocker_above(parent, boxes, parent_of or {}):
            if abs(_center_x(boxes[parent.id]) - _center_x(boxes[child.id])) <= 8:
                source_side = "left"
                target_side = "left"
                side_rail = True
            else:
                source_side = "left" if _center_x(boxes[child.id]) < _center_x(boxes[parent.id]) else "right"
    source_point = _anchor_point(boxes[parent.id], source_side)
    target_point = _anchor_point(boxes[child.id], target_side)
    if side_rail and later_row:
        waypoints = _side_enter_around_first_row(
            source_point, target_point, first_row_boxes, target_side
        )
    elif side_rail:
        waypoints = _column_side_rail(
            source_point,
            target_point,
            boxes[parent.id],
            boxes[child.id],
            boxes,
            {parent.id, child.id},
        )
    else:
        waypoints = _tree_waypoints(
            source_point,
            target_point,
            direction,
            primary_target,
            child_box=boxes[child.id],
            parent_box=boxes[parent.id],
            first_row_boxes=first_row_boxes if avoid_boxes else None,
        )
    if avoid_boxes:
        points = [source_point, *[(point["x"], point["y"]) for point in waypoints], target_point]
        ignore = {parent.id, child.id}
        if path_crosses_boxes(points, boxes, ignore):
            avoided = orthogonal_path_avoiding_boxes(
                source_point,
                target_point,
                boxes,
                ignore=ignore,
                preferred=points,
            )
            waypoints = _clean_waypoints(avoided)
    labels = []
    if child.multiplicity:
        labels.append({
            "text": child.multiplicity,
            "position": _multiplicity_label_position(direction, len(waypoints), source_point, target_point),
        })
    return {
        "id": f"conn-{parent.id}-{child.id}",
        "model_ref": child.part_ref or child.model_ref,
        "source": {"element": parent.id, "anchor": {"side": source_side, "offset": 0.5}},
        "target": {"element": child.id, "anchor": {"side": target_side, "offset": 0.5}},
        "route": {"kind": "orthogonal", "waypoints": waypoints},
        "labels": labels,
        "style": "connector.definition",
    }


def _anchor_point(box: tuple[int, int, int, int], side: str) -> tuple[float, float]:
    x, y, w, h = box
    if side == "top":
        return x + w / 2, y
    if side == "bottom":
        return x + w / 2, y + h
    if side == "left":
        return x, y + h / 2
    return x + w, y + h / 2


def _multiplicity_label_position(
    direction: str,
    segment: int,
    source_point: tuple[float, float],
    target_point: tuple[float, float],
) -> dict[str, float]:
    if direction in {"top-down", "bottom-up"}:
        offset = 0.94 if abs(target_point[1] - source_point[1]) > 120 else 0.82
        return {"segment": segment, "offset": offset, "dx": 10, "dy": -4}
    return {"segment": segment, "offset": 0.82, "dx": 0, "dy": -8}


def _primary_child_anchor(
    parent: TreeNode,
    boxes: dict[str, tuple[int, int, int, int]],
    target_side: str,
    direction: str,
) -> tuple[float, float] | None:
    anchors = [
        _anchor_point(boxes[child.id], target_side)
        for child in parent.children
        if child.id in boxes
    ]
    if not anchors:
        return None
    if direction == "top-down":
        return min(anchors, key=lambda point: point[1])
    if direction == "bottom-up":
        return max(anchors, key=lambda point: point[1])
    if direction == "left-right":
        return min(anchors, key=lambda point: point[0])
    return max(anchors, key=lambda point: point[0])


def _first_row_child_boxes(
    parent: TreeNode,
    boxes: dict[str, tuple[int, int, int, int]],
    primary_target: tuple[float, float] | None,
    direction: str,
) -> list[tuple[int, int, int, int]]:
    if primary_target is None:
        return []
    found: list[tuple[int, int, int, int]] = []
    for child in parent.children:
        if child.id not in boxes:
            continue
        anchor = _anchor_point(
            boxes[child.id],
            "top" if direction == "top-down" else
            "bottom" if direction == "bottom-up" else
            "left" if direction == "left-right" else
            "right",
        )
        if direction in {"top-down", "bottom-up"}:
            if abs(anchor[1] - primary_target[1]) <= 20:
                found.append(boxes[child.id])
        elif abs(anchor[0] - primary_target[0]) <= 20:
            found.append(boxes[child.id])
    return found


def _center_x(box: tuple[int, int, int, int]) -> float:
    return box[0] + box[2] / 2


def _is_later_row(
    child_box: tuple[int, int, int, int],
    primary_target: tuple[float, float] | None,
    direction: str,
) -> bool:
    if primary_target is None:
        return False
    if direction in {"top-down", "bottom-up"}:
        return abs(_anchor_point(child_box, "top" if direction == "top-down" else "bottom")[1] - primary_target[1]) > 20
    return abs(_anchor_point(child_box, "left" if direction == "left-right" else "right")[0] - primary_target[0]) > 20


def _stacked_under_first_row(
    child_box: tuple[int, int, int, int],
    first_row_boxes: list[tuple[int, int, int, int]],
    tol: float = 8,
) -> bool:
    cx = _center_x(child_box)
    return any(abs(_center_x(box) - cx) <= tol for box in first_row_boxes)


def _has_sibling_blocker_above(
    parent: TreeNode,
    boxes: dict[str, tuple[int, int, int, int]],
    parent_of: dict[str, TreeNode],
    tol: float = 8,
) -> bool:
    owner = parent_of.get(parent.id)
    if owner is None or parent.id not in boxes:
        return False
    parent_top = boxes[parent.id][1]
    parent_cx = _center_x(boxes[parent.id])
    for sibling in owner.children:
        if sibling.id == parent.id or sibling.id not in boxes:
            continue
        box = boxes[sibling.id]
        if abs(_center_x(box) - parent_cx) > tol:
            continue
        if box[1] + box[3] <= parent_top + 1:
            return True
    return False


def _side_enter_around_first_row(
    source: tuple[float, float],
    target: tuple[float, float],
    first_row_boxes: list[tuple[int, int, int, int]],
    target_side: str,
) -> list[dict[str, float]]:
    gutter = 28
    if first_row_boxes:
        left = min(box[0] for box in first_row_boxes) - gutter
        right = max(box[0] + box[2] for box in first_row_boxes) + gutter
    else:
        left = min(source[0], target[0]) - gutter
        right = max(source[0], target[0]) + gutter
    side_x = left if target_side == "left" else right
    stub = min(28, max(16, abs(target[1] - source[1]) * 0.2))
    mid_y = source[1] + stub if target[1] >= source[1] else source[1] - stub
    return _clean_waypoints([
        (source[0], mid_y),
        (side_x, mid_y),
        (side_x, target[1]),
    ])


def _column_side_rail(
    source: tuple[float, float],
    target: tuple[float, float],
    parent_box: tuple[int, int, int, int],
    child_box: tuple[int, int, int, int],
    boxes: dict[str, tuple[int, int, int, int]] | None = None,
    ignore: set[str] | None = None,
) -> list[dict[str, float]]:
    col_left = min(parent_box[0], child_box[0])
    rail_x = col_left - 28
    skip = ignore or set()
    obstacles = [
        box
        for node_id, box in (boxes or {}).items()
        if node_id not in skip
    ]
    if obstacles and any(
        segment_crosses_box_interior((rail_x, source[1]), (rail_x, target[1]), box)
        for box in obstacles
    ):
        rail_x = col_left - 12
    return _clean_waypoints([
        (rail_x, source[1]),
        (rail_x, target[1]),
    ])


def _around_first_row_waypoints(
    source: tuple[float, float],
    target: tuple[float, float],
    direction: str,
    first_row_boxes: list[tuple[int, int, int, int]],
    stub: float,
    bus: float,
) -> list[dict[str, float]] | None:
    if not first_row_boxes:
        return None
    gutter = 28
    if direction in {"top-down", "bottom-up"}:
        left = min(box[0] for box in first_row_boxes) - gutter
        right = max(box[0] + box[2] for box in first_row_boxes) + gutter
        side_x = left if target[0] <= source[0] else right
        mid_y = source[1] + stub if direction == "top-down" else source[1] - stub
        return _clean_waypoints([
            (source[0], mid_y),
            (side_x, mid_y),
            (side_x, bus),
            (target[0], bus),
        ])
    top = min(box[1] for box in first_row_boxes) - gutter
    bottom = max(box[1] + box[3] for box in first_row_boxes) + gutter
    side_y = top if target[1] <= source[1] else bottom
    mid_x = source[0] + stub if direction == "left-right" else source[0] - stub
    return _clean_waypoints([
        (mid_x, source[1]),
        (mid_x, side_y),
        (bus, side_y),
        (bus, target[1]),
    ])


def _tree_waypoints(
    source: tuple[float, float],
    target: tuple[float, float],
    direction: str,
    primary_target: tuple[float, float] | None = None,
    child_box: tuple[int, int, int, int] | None = None,
    parent_box: tuple[int, int, int, int] | None = None,
    first_row_boxes: list[tuple[int, int, int, int]] | None = None,
) -> list[dict[str, float]]:
    if direction in {"top-down", "bottom-up"}:
        first_row = primary_target or target
        later_row = child_box is not None and abs(target[1] - first_row[1]) > 20
        bus_y = (source[1] + first_row[1]) / 2
        if later_row:
            gap = (target[1] - source[1]) if direction == "top-down" else (source[1] - target[1])
            stub = min(28, max(16, abs(gap) * 0.2))
            bus_y = target[1] - stub if direction == "top-down" else target[1] + stub
            around = _around_first_row_waypoints(
                source, target, direction, first_row_boxes or [], stub, bus_y
            )
            if around:
                return around
            stacked_later = abs(target[1] - first_row[1]) > 100
            if stacked_later and parent_box is not None:
                px, _py, pw, _ph = parent_box
                down = direction == "top-down"
                side_x = px - 36 if target[0] <= source[0] else px + pw + 36
                mid_y = source[1] + stub if down else source[1] - stub
                return _clean_waypoints([
                    (source[0], mid_y),
                    (side_x, mid_y),
                    (side_x, bus_y),
                    (target[0], bus_y),
                ])
        if source[0] == target[0]:
            return [] if not later_row and target[1] == first_row[1] else _clean_waypoints([(source[0], bus_y)])
        return _clean_waypoints([(source[0], bus_y), (target[0], bus_y)])
    first_row = primary_target or target
    later_row = child_box is not None and abs(target[0] - first_row[0]) > 20
    bus_x = (source[0] + first_row[0]) / 2
    if later_row:
        gap = (target[0] - source[0]) if direction == "left-right" else (source[0] - target[0])
        stub = min(28, max(16, abs(gap) * 0.2))
        bus_x = target[0] - stub if direction == "left-right" else target[0] + stub
        around = _around_first_row_waypoints(
            source, target, direction, first_row_boxes or [], stub, bus_x
        )
        if around:
            return around
    if source[1] == target[1]:
        return [] if not later_row and target[0] == first_row[0] else _clean_waypoints([(bus_x, source[1])])
    return _clean_waypoints([(bus_x, source[1]), (bus_x, target[1])])


def _fit_canvas(
    boxes: dict[str, tuple[int, int, int, int]],
    connections: list[dict[str, Any]],
) -> tuple[dict[str, tuple[int, int, int, int]], list[dict[str, Any]], float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for x, y, width, height in boxes.values():
        xs.extend((x, x + width))
        ys.extend((y, y + height))
    for connection in connections:
        for point in connection["route"]["waypoints"]:
            xs.append(float(point["x"]))
            ys.append(float(point["y"]))
    min_x = min(xs)
    min_y = min(ys)
    shift_x = CANVAS_MARGIN - min_x if min_x < CANVAS_MARGIN else 0
    shift_y = CANVAS_MARGIN - min_y if min_y < CANVAS_MARGIN else 0
    if shift_x or shift_y:
        boxes = {
            node_id: (round(x + shift_x), round(y + shift_y), width, height)
            for node_id, (x, y, width, height) in boxes.items()
        }
        for connection in connections:
            for point in connection["route"]["waypoints"]:
                point["x"] = _clean_number(point["x"] + shift_x)
                point["y"] = _clean_number(point["y"] + shift_y)
        xs = [value + shift_x for value in xs]
        ys = [value + shift_y for value in ys]
    return boxes, connections, max(xs) + CANVAS_MARGIN, max(ys) + CANVAS_MARGIN


def _clean_waypoints(points: list[tuple[float, float]]) -> list[dict[str, float]]:
    return [{"x": _clean_number(x), "y": _clean_number(y)} for x, y in points]


def _clean_number(value: float) -> float:
    rounded = round(value, 3)
    return int(rounded) if float(rounded).is_integer() else rounded
