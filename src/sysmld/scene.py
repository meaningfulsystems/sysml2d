"""Resolved scene graph for SysMLD rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .io import read_json


VIEW_CODES = {
    "DefinitionView": "def",
    "InterconnectionView": "icn",
    "PackageView": "pkg",
    "ConstraintView": "cst",
    "RequirementView": "req",
    "ActionView": "act",
    "StateView": "stv",
    "InteractionView": "int",
    "UseCaseView": "uc",
    "AllocationView": "alloc",
    "FlowView": "flow",
    "AnalysisCaseView": "acase",
    "VerificationCaseView": "vcase",
    "InterfaceView": "intf",
    "GeneralView": "gen",
}

MODE_CODES = {
    "model_based": "mb",
    "sketch": "sk",
}

DEFAULT_STYLES = {
    "boundary":      {"fill": "#FFFFFF", "stroke": "#333333", "stroke_width": 2},
    "part_usage":    {"fill": "#F7F9FC", "stroke": "#334155", "stroke_width": 2},
    "part_definition":{"fill": "#F8FAFC","stroke": "#475569", "stroke_width": 2},
    "port":          {"fill": "#FFFFFF", "stroke": "#334155", "stroke_width": 1},
    "connection":    {"stroke": "#334155", "stroke_width": 2},
    "package":       {"fill": "#F8FAFC", "stroke": "#475569", "stroke_width": 2, "corner_radius": 2},
    "requirement":   {"fill": "#FFF7ED", "stroke": "#C2410C", "stroke_width": 2, "corner_radius": 4},
    "constraint":    {"fill": "#F5F3FF", "stroke": "#6D28D9", "stroke_width": 2, "corner_radius": 4},
    "value_property":{"fill": "#FAFAFA", "stroke": "#525252", "stroke_width": 1.5, "corner_radius": 4},
    "action":        {"fill": "#ECFDF5", "stroke": "#047857", "stroke_width": 2, "corner_radius": 18},
    "decision_node": {"fill": "#FEFCE8", "stroke": "#A16207", "stroke_width": 2},
    "fork_node":     {"fill": "#111827", "stroke": "#111827", "stroke_width": 1},
    "join_node":     {"fill": "#111827", "stroke": "#111827", "stroke_width": 1},
    "activity_final_node": {"fill": "#111827", "stroke": "#111827", "stroke_width": 2},
    "actor":         {"fill": "#FFFFFF", "stroke": "#334155", "stroke_width": 2},
    "use_case":      {"fill": "#EFF6FF", "stroke": "#2563EB", "stroke_width": 2},
    "lifeline":      {"fill": "#FFFFFF", "stroke": "#334155", "stroke_width": 1.5},
    "execution":     {"fill": "#DBEAFE", "stroke": "#1D4ED8", "stroke_width": 1.5},
    "case":          {"fill": "#F0FDFA", "stroke": "#0F766E", "stroke_width": 2, "corner_radius": 4},
    "interface":     {"fill": "#F0F9FF", "stroke": "#0369A1", "stroke_width": 2, "corner_radius": 4},
    "flow_node":     {"fill": "#FDF2F8", "stroke": "#BE185D", "stroke_width": 2, "corner_radius": 4},
    "allocation":    {"fill": "#F8FAFC", "stroke": "#64748B", "stroke_width": 2, "corner_radius": 4},
    "item":          {"fill": "#F1F5F9", "stroke": "#475569", "stroke_width": 1.5, "corner_radius": 4},
    "signal":        {"fill": "#FEF3C7", "stroke": "#B45309", "stroke_width": 1.5, "corner_radius": 4},
    "message":       {"stroke": "#334155", "stroke_width": 1.5, "marker_end": "arrow-dark"},
    "message.return":{"stroke": "#334155", "stroke_width": 1.5, "marker_end": "arrow-dark", "stroke_dasharray": "6 4"},
    "connector.extend": {"stroke": "#334155", "stroke_width": 1.5, "marker_end": "arrow-dark", "stroke_dasharray": "6 4"},
    "connector.include": {"stroke": "#334155", "stroke_width": 1.5, "marker_end": "arrow-dark", "stroke_dasharray": "6 4"},
    "connector.control_flow": {"stroke": "#047857", "stroke_width": 1.8, "marker_end": "arrow-dark"},
    "connector.allocation": {"stroke": "#64748B", "stroke_width": 1.6, "marker_end": "arrow-dark", "stroke_dasharray": "6 4"},
    "connector.flow": {"stroke": "#BE185D", "stroke_width": 1.8, "marker_end": "arrow-dark"},
    "connector.directed": {"stroke": "#334155", "stroke_width": 1.6, "marker_end": "arrow-dark"},
    # State machine symbols
    "state_usage":   {"fill": "#EFF6FF", "stroke": "#1D4ED8", "stroke_width": 2, "corner_radius": 16},
    "initial_state": {"fill": "#1E293B", "stroke": "#1E293B", "stroke_width": 1},
    "final_state":   {"fill": "#1E293B", "stroke": "#1E293B", "stroke_width": 2},
    "transition":    {"stroke": "#1D4ED8", "stroke_width": 1.5, "marker_end": "arrow"},
}


@dataclass
class Box:
    x: float
    y: float
    width: float
    height: float
    z: float = 0

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2


@dataclass
class SceneElement:
    id: str
    symbol: str
    box: Box
    label: str
    style: dict[str, Any]
    owner: str | None = None
    model_ref: str | None = None
    port_side: str | None = None


@dataclass
class SceneConnection:
    id: str
    points: list[tuple[float, float]]
    labels: list[dict[str, Any]]
    style: dict[str, Any]


@dataclass
class Scene:
    id: str
    name: str
    kind: str
    mode: str
    subject: str | None
    width: float
    height: float
    background: str
    header: str
    elements: list[SceneElement] = field(default_factory=list)
    connections: list[SceneConnection] = field(default_factory=list)
    annotations: list[dict[str, Any]] = field(default_factory=list)


def build_scene(path: Path) -> Scene:
    """Load a SysMLD document and resolve it into renderer-ready geometry."""

    data = read_json(path)
    return build_scene_from_data(data)


def build_scene_from_data(data: dict[str, Any]) -> Scene:
    """Resolve raw SysMLD data into scene elements, ports, and connections."""

    diagram = data["diagram"]
    canvas = diagram["canvas"]
    aliases = data.get("aliases", {})
    subject_raw = diagram.get("subject")          # may be an alias key or a qualified name
    subject = _resolve_alias(subject_raw, aliases) # fully resolved qualified name

    # SysML v2 frame header uses "usageName : TypeName" for the subject bracket.
    # If the subject field is an alias key, that key is the usage name (e.g. "toaster");
    # the resolved last segment is the type name (e.g. "Toaster").
    # If it is not an alias, we only have the type name.
    if subject_raw and subject_raw in aliases:
        subject_usage = subject_raw
        subject_type  = subject.split("::")[-1] if subject else None
    else:
        subject_usage = None
        subject_type  = subject.split("::")[-1] if subject else None

    kind = diagram["kind"]
    mode = data["mode"]
    header = _header(kind, mode, diagram["name"], subject_usage, subject_type)
    styles = diagram.get("styles", {})

    elements: dict[str, SceneElement] = {}
    pending_ports: list[dict[str, Any]] = []
    for raw in diagram.get("elements", []):
        if raw.get("symbol") == "port":
            pending_ports.append(raw)
            continue
        layout = raw["layout"]
        symbol = raw["symbol"]
        element = SceneElement(
            id=raw["id"],
            symbol=symbol,
            box=Box(
                x=float(layout["x"]),
                y=float(layout["y"]),
                width=float(layout["width"]),
                height=float(layout["height"]),
                z=float(layout.get("z", 0)),
            ),
            label=_label_for(raw),
            style=_style_for(symbol, raw.get("style"), styles),
            model_ref=_resolve_alias(raw.get("model_ref"), aliases),
        )
        elements[element.id] = element

    for raw in pending_ports:
        owner = elements[raw["owner"]]
        placement = raw["placement"]
        box = _port_box(owner.box, placement["side"], float(placement["offset"]))
        element = SceneElement(
            id=raw["id"],
            symbol="port",
            box=box,
            label=_label_for(raw),
            style=_style_for("port", raw.get("style"), styles),
            owner=raw.get("owner"),
            model_ref=_resolve_alias(raw.get("model_ref"), aliases),
            port_side=placement["side"],
        )
        elements[element.id] = element

    connections = [
        _connection(raw, elements, styles)
        for raw in diagram.get("connections", [])
    ]

    return Scene(
        id=diagram["id"],
        name=diagram["name"],
        kind=kind,
        mode=mode,
        subject=subject,
        width=float(canvas["width"]),
        height=float(canvas["height"]),
        background=canvas.get("background", "#FFFFFF"),
        header=header,
        elements=sorted(elements.values(), key=lambda element: element.box.z),
        connections=connections,
        annotations=diagram.get("annotations", []),
    )


def _resolve_alias(value: str | None, aliases: dict[str, str]) -> str | None:
    if value is None:
        return None
    return aliases.get(value, value)


def _header(
    kind: str,
    mode: str,
    name: str,
    subject_usage: str | None,
    subject_type: str | None,
) -> str:
    """Build the diagram frame header.

    SysML v2 graphical notation (FeatureSpecializationPart) uses
    'usageName : TypeName' for the subject bracket — e.g. [toaster : Toaster].
    When only a type name is available the colon is omitted.
    """
    code      = VIEW_CODES.get(kind, kind)
    mode_code = MODE_CODES.get(mode, mode)
    if subject_usage and subject_type:
        return f"[{code}.{mode_code}] {name} [{subject_usage} : {subject_type}]"
    if subject_type:
        return f"[{code}.{mode_code}] {name} [{subject_type}]"
    return f"[{code}.{mode_code}] {name}"


def _style_for(symbol: str, style_ref: Any, styles: dict[str, Any]) -> dict[str, Any]:
    key = "connection" if symbol == "connection" else symbol
    style = dict(DEFAULT_STYLES.get(key, {}))
    if isinstance(style_ref, str):
        style.update(DEFAULT_STYLES.get(style_ref, {}))
        style.update(styles.get(style_ref, {}))
    elif isinstance(style_ref, dict):
        style.update(style_ref)
    return style


def _label_for(raw: dict[str, Any]) -> str:
    if "label" in raw:
        return str(raw["label"])
    return str(raw.get("model_ref") or raw["id"])


def _port_box(owner: Box, side: str, offset: float) -> Box:
    size = 12
    if side == "left":
        return Box(owner.x - size / 2, owner.y + owner.height * offset - size / 2, size, size, owner.z + 1)
    if side == "right":
        return Box(owner.x + owner.width - size / 2, owner.y + owner.height * offset - size / 2, size, size, owner.z + 1)
    if side == "top":
        return Box(owner.x + owner.width * offset - size / 2, owner.y - size / 2, size, size, owner.z + 1)
    return Box(owner.x + owner.width * offset - size / 2, owner.y + owner.height - size / 2, size, size, owner.z + 1)


def _connection(
    raw: dict[str, Any],
    elements: dict[str, SceneElement],
    styles: dict[str, Any],
) -> SceneConnection:
    source = raw["source"]
    target = raw["target"]
    source_point = _endpoint_point(elements[source["element"]], source["anchor"])
    target_point = _endpoint_point(elements[target["element"]], target["anchor"])
    waypoints = raw.get("route", {}).get("waypoints", [])
    points = [source_point]
    points.extend((float(point["x"]), float(point["y"])) for point in waypoints)
    points.append(target_point)
    return SceneConnection(
        id=raw["id"],
        points=points,
        labels=raw.get("labels", []),
        style=_style_for("connection", raw.get("style"), styles),
    )


def _endpoint_point(element: SceneElement, anchor: dict[str, Any]) -> tuple[float, float]:
    if element.symbol == "lifeline":
        offset = float(anchor["offset"])
        return (element.box.center_x, element.box.y + element.box.height * offset)
    return _anchor_point(element.box, anchor)


def _anchor_point(box: Box, anchor: dict[str, Any]) -> tuple[float, float]:
    side = anchor["side"]
    offset = float(anchor["offset"])
    if side == "left":
        return (box.x, box.y + box.height * offset)
    if side == "right":
        return (box.x + box.width, box.y + box.height * offset)
    if side == "top":
        return (box.x + box.width * offset, box.y)
    return (box.x + box.width * offset, box.y + box.height)
