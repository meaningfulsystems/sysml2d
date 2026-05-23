"""Generate DefinitionView tree diagrams from a compact tree intent file."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


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

    max_x = max(x + w for x, _y, w, _h in boxes.values())
    max_y = max(y + h for _x, y, _w, h in boxes.values())
    canvas_w = max_x + CANVAS_MARGIN
    canvas_h = max_y + CANVAS_MARGIN

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

    connections = []
    for parent in node_order:
        for child in parent.children:
            connections.append(_connection(parent, child, boxes, direction))

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
    rows = _child_rows(node.children, max_siblings_per_row)
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
    rows = _child_rows(node.children, max_siblings_per_row)
    row_step = node.height + row_gap
    for row_index, row in enumerate(rows):
        row_width = _row_base_width(row, sibling_gap, subtree_widths)
        cursor = center_x - row_width / 2 + _row_stagger(row, sibling_gap, subtree_widths, row_index, rows)
        for child in row:
            child_width = subtree_widths[child.id]
            child_depth = depth + 1 + (row_index * row_step / (node.height + rank_gap))
            _place(
                child,
                cursor + child_width / 2,
                child_depth,
                sibling_gap,
                rank_gap,
                row_gap,
                max_siblings_per_row,
                subtree_widths,
                positions,
            )
            cursor += child_width + sibling_gap


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
) -> dict[str, Any]:
    source_side, target_side = {
        "top-down": ("bottom", "top"),
        "bottom-up": ("top", "bottom"),
        "left-right": ("right", "left"),
        "right-left": ("left", "right"),
    }[direction]
    source_point = _anchor_point(boxes[parent.id], source_side)
    target_point = _anchor_point(boxes[child.id], target_side)
    primary_target = _primary_child_anchor(parent, boxes, target_side, direction)
    waypoints = _tree_waypoints(source_point, target_point, direction, primary_target)
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


def _tree_waypoints(
    source: tuple[float, float],
    target: tuple[float, float],
    direction: str,
    primary_target: tuple[float, float] | None = None,
) -> list[dict[str, float]]:
    if direction in {"top-down", "bottom-up"}:
        bus_target = primary_target or target
        mid_y = (source[1] + bus_target[1]) / 2
        if source[0] == target[0]:
            return [] if target[1] == bus_target[1] else _clean_waypoints([(source[0], mid_y)])
        return _clean_waypoints([(source[0], mid_y), (target[0], mid_y)])
    bus_target = primary_target or target
    mid_x = (source[0] + bus_target[0]) / 2
    if source[1] == target[1]:
        return [] if target[0] == bus_target[0] else _clean_waypoints([(mid_x, source[1])])
    return _clean_waypoints([(mid_x, source[1]), (mid_x, target[1])])


def _clean_waypoints(points: list[tuple[float, float]]) -> list[dict[str, float]]:
    return [{"x": _clean_number(x), "y": _clean_number(y)} for x, y in points]


def _clean_number(value: float) -> float:
    rounded = round(value, 3)
    return int(rounded) if float(rounded).is_integer() else rounded
