"""Requirement view composer."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .views import MARGIN, _bounds, _clean, _node_size, _shift_box


PRIMARY_EDGE_LABELS = {"derive", "refine", "satisfy", "verify", "trace"}


def requirement(spec: dict[str, Any]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = spec.get("nodes", {})
    edges: list[dict[str, Any]] = spec.get("edges", [])
    default_w = int(spec.get("default_w", 250))
    default_h = int(spec.get("default_h", 124))
    sibling_gap = int(spec.get("sibling_gap", 72))
    rank_gap = int(spec.get("rank_gap", 110))
    nids = sorted(nodes, key=lambda node_id: (nodes[node_id].get("rank", 0), nodes[node_id].get("order", 0), node_id))
    sizes = {
        node_id: _node_size({**nodes[node_id], "symbol": nodes[node_id].get("symbol", "requirement")}, default_w, default_h)
        for node_id in nids
    }
    children, parent = _requirement_tree(nids, nodes, edges)
    roots = [node_id for node_id in nids if node_id not in parent]
    if not roots:
        roots = nids[:1]

    subtree_widths: dict[str, float] = {}
    for root in roots:
        _subtree_width(root, children, sizes, sibling_gap, subtree_widths)

    positions: dict[str, tuple[float, int]] = {}
    cursor = 0.0
    for root in roots:
        width = subtree_widths[root]
        _place_tree(root, cursor + width / 2, 0, children, sizes, sibling_gap, rank_gap, subtree_widths, positions)
        cursor += width + sibling_gap
    for node_id in nids:
        if node_id not in positions:
            width = subtree_widths.get(node_id, sizes[node_id][0])
            _place_tree(node_id, cursor + width / 2, 0, children, sizes, sibling_gap, rank_gap, subtree_widths, positions)
            cursor += width + sibling_gap

    boxes = {
        node_id: (
            _clean(cx - sizes[node_id][0] / 2),
            _clean(depth * (sizes[node_id][1] + rank_gap)),
            sizes[node_id][0],
            sizes[node_id][1],
        )
        for node_id, (cx, depth) in positions.items()
    }
    source_slots, target_slots = _edge_slots(edges, boxes)
    connections = [
        _requirement_connection(edge, boxes, source_slots, target_slots)
        for index, edge in enumerate(edges)
        if edge.get("from") in boxes and edge.get("to") in boxes
    ]

    bounds = _bounds(list(boxes.values()), connections)
    shift_x = MARGIN - bounds[0]
    shift_y = MARGIN - bounds[1]
    if shift_x or shift_y:
        boxes = {node_id: _shift_box(box, shift_x, shift_y) for node_id, box in boxes.items()}
        for connection in connections:
            for point in connection["route"]["waypoints"]:
                point["x"] = _clean(point["x"] + shift_x)
                point["y"] = _clean(point["y"] + shift_y)
    width = _clean(bounds[2] - bounds[0] + MARGIN * 2)
    height = _clean(bounds[3] - bounds[1] + MARGIN * 2)

    elements = []
    for node_id in nids:
        node = nodes[node_id]
        x, y, w, h = boxes[node_id]
        elements.append({
            "id": node_id,
            "model_ref": node.get("model_ref", node_id),
            "symbol": node.get("symbol", "requirement"),
            "layout": {"x": x, "y": y, "width": w, "height": h, "z": node.get("z", 10)},
            "label": node.get("label", node_id),
            "style": node.get("style", "requirement"),
        })

    diagram_id = spec.get("diagram", "requirement-view")
    diagram: dict[str, Any] = {
        "id": diagram_id,
        "kind": "RequirementView",
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


def requirement_file(input_path: Path, output_path: Path | None = None) -> Path:
    spec = json.loads(input_path.read_text(encoding="utf-8"))
    result = requirement(spec)
    target = output_path or input_path.with_suffix(".sysmld")
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return target


def _requirement_tree(
    nids: list[str],
    nodes: dict[str, dict[str, Any]],
    edges: list[dict[str, Any]],
) -> tuple[dict[str, list[str]], dict[str, str]]:
    parent: dict[str, str] = {}
    children: dict[str, list[str]] = defaultdict(list)
    incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, edge in enumerate(edges):
        src = edge.get("from")
        tgt = edge.get("to")
        if src in nodes and tgt in nodes and src != tgt:
            incoming[tgt].append({**edge, "_index": index})

    for node_id in nids:
        candidates = incoming.get(node_id, [])
        if not candidates:
            continue
        candidates.sort(key=lambda edge: (_edge_priority(edge), edge["_index"]))
        selected = candidates[0]
        parent[node_id] = selected["from"]
        children[selected["from"]].append(node_id)

    for child_list in children.values():
        child_list.sort(key=lambda node_id: (nodes[node_id].get("rank", 0), nodes[node_id].get("order", 0), node_id))
    return dict(children), parent


def _edge_priority(edge: dict[str, Any]) -> int:
    label = str(edge.get("label", "")).lower()
    if label == "derive":
        return 0
    if label == "refine":
        return 1
    if label in PRIMARY_EDGE_LABELS:
        return 2
    return 3


def _subtree_width(
    node_id: str,
    children: dict[str, list[str]],
    sizes: dict[str, tuple[int, int]],
    sibling_gap: int,
    widths: dict[str, float],
) -> float:
    child_ids = children.get(node_id, [])
    if not child_ids:
        widths[node_id] = sizes[node_id][0]
        return widths[node_id]
    child_widths = [
        _subtree_width(child_id, children, sizes, sibling_gap, widths)
        for child_id in child_ids
    ]
    widths[node_id] = max(sizes[node_id][0], sum(child_widths) + sibling_gap * (len(child_widths) - 1))
    return widths[node_id]


def _place_tree(
    node_id: str,
    center_x: float,
    depth: int,
    children: dict[str, list[str]],
    sizes: dict[str, tuple[int, int]],
    sibling_gap: int,
    rank_gap: int,
    widths: dict[str, float],
    positions: dict[str, tuple[float, int]],
) -> None:
    positions[node_id] = (center_x, depth)
    child_ids = children.get(node_id, [])
    if not child_ids:
        return
    total_width = sum(widths[child_id] for child_id in child_ids) + sibling_gap * (len(child_ids) - 1)
    cursor = center_x - total_width / 2
    for child_id in child_ids:
        child_width = widths[child_id]
        _place_tree(
            child_id,
            cursor + child_width / 2,
            depth + 1,
            children,
            sizes,
            sibling_gap,
            rank_gap,
            widths,
            positions,
        )
        cursor += child_width + sibling_gap


def _requirement_connection(
    edge: dict[str, Any],
    boxes: dict[str, tuple[float, float, float, float]],
    source_slots: dict[int, tuple[int, int]],
    target_slots: dict[int, tuple[int, int]],
) -> dict[str, Any]:
    src = edge["from"]
    tgt = edge["to"]
    edge_key = id(edge)
    source_side = edge.get("source_side", "bottom")
    target_side = edge.get("target_side", "top")
    source_offset = float(edge.get("source_offset", _slot_offset(*source_slots.get(edge_key, (0, 1)))))
    target_offset = float(edge.get("target_offset", _slot_offset(*target_slots.get(edge_key, (0, 1)))))
    source = _anchor_point(boxes[src], source_side, source_offset)
    target = _anchor_point(boxes[tgt], target_side, target_offset)
    waypoints: list[dict[str, float]] = []
    labels = []
    if edge.get("label", ""):
        labels.append({"text": edge["label"], "position": {"offset": 0.5, "placement": "centerline"}})
    return {
        "id": edge.get("id", f"conn-{src}-{tgt}"),
        "model_ref": edge.get("model_ref", src),
        "source": {"element": src, "anchor": {"side": source_side, "offset": _clean(source_offset)}},
        "target": {"element": tgt, "anchor": {"side": target_side, "offset": _clean(target_offset)}},
        "route": {"kind": "polyline", "waypoints": waypoints},
        "labels": labels,
        "style": edge.get("style", "connector.default"),
    }


def _edge_slots(
    edges: list[dict[str, Any]],
    boxes: dict[str, tuple[float, float, float, float]],
) -> tuple[dict[int, tuple[int, int]], dict[int, tuple[int, int]]]:
    outgoing: dict[str, list[dict[str, Any]]] = defaultdict(list)
    incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        if edge.get("from") in boxes and edge.get("to") in boxes:
            outgoing[edge["from"]].append(edge)
            incoming[edge["to"]].append(edge)

    source_slots: dict[int, tuple[int, int]] = {}
    for edge_list in outgoing.values():
        edge_list.sort(key=lambda edge: (_center_x(boxes[edge["to"]]), edge.get("label", ""), edge["to"]))
        total = len(edge_list)
        for index, edge in enumerate(edge_list):
            source_slots[id(edge)] = (index, total)

    target_slots: dict[int, tuple[int, int]] = {}
    for edge_list in incoming.values():
        edge_list.sort(key=lambda edge: (_center_x(boxes[edge["from"]]), edge.get("label", ""), edge["from"]))
        total = len(edge_list)
        for index, edge in enumerate(edge_list):
            target_slots[id(edge)] = (index, total)
    return source_slots, target_slots


def _slot_offset(index: int, total: int) -> float:
    if total <= 1:
        return 0.5
    return (index + 1) / (total + 1)


def _center_x(box: tuple[float, float, float, float]) -> float:
    return box[0] + box[2] / 2


def _anchor_point(box: tuple[float, float, float, float], side: str, offset: float = 0.5) -> tuple[float, float]:
    x, y, w, h = box
    if side == "left":
        return x, y + h * offset
    if side == "right":
        return x + w, y + h * offset
    if side == "top":
        return x + w * offset, y
    return x + w * offset, y + h
