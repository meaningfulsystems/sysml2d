"""SVG renderer for SysMLD scenes."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import NamedTuple

from .scene import Scene, SceneElement, build_scene
from .validate import validate_file


FRAME_HEIGHT = 38
PADDING = 2
DEFAULT_LABEL_OFFSET = 10
LABEL_PADDING_X = 4
LABEL_PADDING_Y = 3
TEXT_CHAR_WIDTH = 6.2
SMALL_TEXT_HEIGHT = 11
LABEL_STAGGER = SMALL_TEXT_HEIGHT + LABEL_PADDING_Y * 2


class Bounds(NamedTuple):
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height


def render_svg(path: Path, output_path: Path | None = None, strict: bool = True) -> Path:
    """Validate and render a SysMLD document to an SVG file."""

    if strict:
        report = validate_file(path, strict=True)
        if report.errors:
            messages = "; ".join(f"{finding.code}: {finding.message}" for finding in report.findings)
            raise ValueError(f"Cannot render strict-invalid diagram: {messages}")
    scene = build_scene(path)
    target = output_path or path.with_suffix(".svg")
    target.write_text(scene_to_svg(scene), encoding="utf-8")
    return target


def render_png(path: Path, output_path: Path | None = None, strict: bool = True, scale: float = 2.0) -> Path:
    """Validate and render a SysMLD document to a PNG file.

    Builds the scene graph once, converts via the SVG representation using
    cairosvg.  Requires: pip install cairosvg

    scale=2.0 produces a 2× retina-quality image suitable for sharing on
    LinkedIn and other social platforms.
    """
    try:
        import cairosvg
    except ImportError:
        raise ImportError(
            "PNG rendering requires cairosvg. Install it with: pip install cairosvg"
        )

    if strict:
        report = validate_file(path, strict=True)
        if report.errors:
            messages = "; ".join(f"{finding.code}: {finding.message}" for finding in report.findings)
            raise ValueError(f"Cannot render strict-invalid diagram: {messages}")

    scene = build_scene(path)
    svg_text = scene_to_svg(scene)
    target = output_path or path.with_suffix(".png")
    cairosvg.svg2png(bytestring=svg_text.encode("utf-8"), write_to=str(target), scale=scale)
    return target


def scene_to_svg(scene: Scene) -> str:
    """Convert a resolved scene graph to an SVG document string."""

    width = scene.width + PADDING * 2
    height = scene.height + FRAME_HEIGHT + PADDING * 2
    body: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height:g}" viewBox="0 0 {width:g} {height:g}">',
        "<defs>",
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111827}.label{font-size:13px}.small{font-size:11px}.header{font-size:14px;font-weight:600}</style>',
        '<marker id="arrow" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">'
        '<polygon points="0 0,8 3,0 6" fill="#1D4ED8"/></marker>',
        '<marker id="arrow-dark" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">'
        '<polygon points="0 0,8 3,0 6" fill="#334155"/></marker>',
        '<marker id="composition" markerWidth="12" markerHeight="12" refX="0" refY="6" orient="auto" markerUnits="strokeWidth">'
        '<polygon points="0 6,6 0,12 6,6 12" fill="#111827" stroke="#111827"/></marker>',
        "</defs>",
        f'<rect x="0" y="0" width="{width:g}" height="{height:g}" fill="{escape(scene.background)}"/>',
    ]
    body.extend(_frame(scene))
    body.append(f'<g transform="translate({PADDING:g},{FRAME_HEIGHT + PADDING:g})">')
    label_bounds = Bounds(0, 0, scene.width, scene.height)
    occupied = _initial_label_obstacles(scene.elements)
    route_segments = [
        segment
        for connection in scene.connections
        for segment in zip(connection.points, connection.points[1:])
    ]
    close_packed_ports = _close_packed_port_ids(scene.elements)
    for element in scene.elements:
        body.extend(_element(element))
    for annotation in scene.annotations:
        body.extend(_annotation(annotation))
    for connection in scene.connections:
        body.extend(_connection(connection.points, connection.style))
    for element in scene.elements:
        body.extend(_placed_port_label(element, occupied, route_segments, element.id in close_packed_ports, label_bounds))
    route_segments_by_connection = {
        connection.id: list(zip(connection.points, connection.points[1:]))
        for connection in scene.connections
    }
    for connection in scene.connections:
        other_route_segments = [
            segment
            for other_id, segments in route_segments_by_connection.items()
            if other_id != connection.id
            for segment in segments
        ]
        body.extend(_connection_labels(connection.points, connection.labels, connection.style, occupied, other_route_segments, label_bounds))
    body.append("</g>")
    body.append("</svg>")
    return "\n".join(body) + "\n"


def _frame(scene: Scene) -> list[str]:
    width = scene.width + PADDING * 2
    height = scene.height + PADDING
    header = escape(scene.header)
    tab_width = max(220, len(scene.header) * 8 + 24)
    return [
        f'<rect x="{PADDING:g}" y="{FRAME_HEIGHT:g}" width="{scene.width:g}" height="{scene.height:g}" fill="none" stroke="#333333" stroke-width="2"/>',
        f'<path d="M {PADDING:g} 1 H {tab_width:g} L {tab_width + 16:g} {FRAME_HEIGHT:g} H {PADDING:g} Z" fill="#FFFFFF" stroke="#333333" stroke-width="2"/>',
        f'<text class="header" x="{PADDING + 10:g}" y="24">{header}</text>',
        f'<rect x="{PADDING:g}" y="{FRAME_HEIGHT:g}" width="{width - PADDING * 2:g}" height="{height:g}" fill="none" stroke="#333333" stroke-width="0"/>',
    ]


def _element(element: SceneElement) -> list[str]:
    box = element.box
    style = element.style
    fill = escape(str(style.get("fill", "#F7F9FC")))
    stroke = escape(str(style.get("stroke", "#334155")))
    stroke_width = float(style.get("stroke_width", 2))
    corner_radius = float(style.get("corner_radius", 4))
    if element.symbol == "port":
        return [
            f'<rect id="{escape(element.id)}" x="{box.x:g}" y="{box.y:g}" width="{box.width:g}" height="{box.height:g}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width:g}"/>',
        ]
    if element.symbol == "boundary":
        boundary_radius = float(style.get("corner_radius", 0))
        return [
            f'<rect id="{escape(element.id)}" x="{box.x:g}" y="{box.y:g}" width="{box.width:g}" height="{box.height:g}" rx="{boundary_radius:g}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width:g}"/>',
            _text("label", element.label, box.x + 10, box.y + 22),
        ]
    if element.symbol == "initial_state":
        r = min(box.width, box.height) / 2
        cx, cy = box.center_x, box.center_y
        return [f'<circle id="{escape(element.id)}" cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width:g}"/>']
    if element.symbol == "final_state":
        r_outer = min(box.width, box.height) / 2
        r_inner = r_outer * 0.55
        cx, cy = box.center_x, box.center_y
        return [
            f'<circle cx="{cx:g}" cy="{cy:g}" r="{r_outer:g}" fill="none" stroke="{stroke}" stroke-width="{stroke_width:g}"/>',
            f'<circle id="{escape(element.id)}" cx="{cx:g}" cy="{cy:g}" r="{r_inner:g}" fill="{fill}" stroke="none"/>',
        ]
    if element.symbol == "activity_final_node":
        r_outer = min(box.width, box.height) / 2
        r_inner = r_outer * 0.55
        cx, cy = box.center_x, box.center_y
        return [
            f'<circle cx="{cx:g}" cy="{cy:g}" r="{r_outer:g}" fill="none" stroke="{stroke}" stroke-width="{stroke_width:g}"/>',
            f'<circle id="{escape(element.id)}" cx="{cx:g}" cy="{cy:g}" r="{r_inner:g}" fill="{fill}" stroke="none"/>',
        ]
    if element.symbol == "decision_node":
        cx, cy = box.center_x, box.center_y
        points = f"{cx:g},{box.y:g} {box.x + box.width:g},{cy:g} {cx:g},{box.y + box.height:g} {box.x:g},{cy:g}"
        return [
            f'<polygon id="{escape(element.id)}" points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width:g}"/>',
            _text("small", element.label, cx, cy + 4, anchor="middle") if element.label else "",
        ]
    if element.symbol in {"fork_node", "join_node"}:
        return [
            f'<rect id="{escape(element.id)}" x="{box.x:g}" y="{box.y:g}" width="{box.width:g}" height="{box.height:g}" rx="1" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width:g}"/>',
        ]
    if element.symbol == "actor":
        cx = box.center_x
        head_r = min(box.width, box.height) * 0.16
        head_cy = box.y + head_r + 4
        body_top = head_cy + head_r
        body_bottom = box.y + box.height * 0.62
        arm_y = box.y + box.height * 0.38
        leg_y = box.y + box.height - 4
        return [
            f'<circle id="{escape(element.id)}" cx="{cx:g}" cy="{head_cy:g}" r="{head_r:g}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width:g}"/>',
            f'<line x1="{cx:g}" y1="{body_top:g}" x2="{cx:g}" y2="{body_bottom:g}" stroke="{stroke}" stroke-width="{stroke_width:g}" stroke-linecap="round"/>',
            f'<line x1="{box.x + 8:g}" y1="{arm_y:g}" x2="{box.x + box.width - 8:g}" y2="{arm_y:g}" stroke="{stroke}" stroke-width="{stroke_width:g}" stroke-linecap="round"/>',
            f'<line x1="{cx:g}" y1="{body_bottom:g}" x2="{box.x + 10:g}" y2="{leg_y:g}" stroke="{stroke}" stroke-width="{stroke_width:g}" stroke-linecap="round"/>',
            f'<line x1="{cx:g}" y1="{body_bottom:g}" x2="{box.x + box.width - 10:g}" y2="{leg_y:g}" stroke="{stroke}" stroke-width="{stroke_width:g}" stroke-linecap="round"/>',
            _text("small", element.label, cx, box.y + box.height + 14, anchor="middle"),
        ]
    if element.symbol == "use_case":
        return [
            f'<ellipse id="{escape(element.id)}" cx="{box.center_x:g}" cy="{box.center_y:g}" rx="{box.width / 2:g}" ry="{box.height / 2:g}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width:g}"/>',
            _text("label", element.label, box.center_x, box.center_y, anchor="middle"),
        ]
    if element.symbol == "package":
        tab_w = min(max(len(element.label) * 7 + 20, 68), box.width * 0.65)
        tab_h = 20
        return [
            f'<path id="{escape(element.id)}" d="M {box.x:g},{box.y + tab_h:g} V {box.y:g} H {box.x + tab_w:g} L {box.x + tab_w + 12:g},{box.y + tab_h:g} H {box.x + box.width:g} V {box.y + box.height:g} H {box.x:g} Z" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width:g}"/>',
            _text("small", element.label, box.x + 10, box.y + 15),
        ]
    if element.symbol == "lifeline":
        header_h = 34
        cx = box.center_x
        return [
            f'<rect id="{escape(element.id)}" x="{box.x:g}" y="{box.y:g}" width="{box.width:g}" height="{header_h:g}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width:g}"/>',
            _text("small", element.label, cx, box.y + 21, anchor="middle"),
            f'<line x1="{cx:g}" y1="{box.y + header_h:g}" x2="{cx:g}" y2="{box.y + box.height:g}" stroke="{stroke}" stroke-width="1.2" stroke-dasharray="5 5"/>',
        ]
    return [
        f'<rect id="{escape(element.id)}" x="{box.x:g}" y="{box.y:g}" width="{box.width:g}" height="{box.height:g}" rx="{corner_radius:g}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width:g}"/>',
        _state_label(element),
    ]


def _state_label(element: SceneElement) -> str:
    box = element.box
    if element.style.get("label_position") == "top":
        return _text("label", element.label, box.x + 12, box.y + 24)
    return _text("label", element.label, box.center_x, box.center_y, anchor="middle")


def _annotation(annotation: dict) -> list[str]:
    if annotation.get("type") != "state_region_divider":
        return []
    x1 = float(annotation.get("x1", 0))
    y1 = float(annotation.get("y1", 0))
    x2 = float(annotation.get("x2", x1))
    y2 = float(annotation.get("y2", y1))
    output = [
        f'<line id="{escape(str(annotation["id"]))}" x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="#64748B" stroke-width="1.5" stroke-dasharray="6 5"/>'
    ]
    label = str(annotation.get("label", ""))
    if label:
        output.append(_text("small", label, float(annotation.get("label_x", x1 + 8)), float(annotation.get("label_y", y1 + 16))))
    return output


def _text(class_name: str, value: str, x: float, y: float, anchor: str | None = None) -> str:
    lines = str(value).splitlines() or [""]
    line_height = 15 if class_name == "label" else 12
    first_y = y - (len(lines) - 1) * line_height / 2
    anchor_attr = f' text-anchor="{anchor}"' if anchor else ""
    if len(lines) == 1:
        return f'<text class="{class_name}"{anchor_attr} x="{x:g}" y="{y:g}">{escape(lines[0])}</text>'
    tspans = [
        f'<tspan x="{x:g}" y="{first_y:g}">{escape(lines[0])}</tspan>'
    ]
    for index, line in enumerate(lines[1:], start=1):
        tspans.append(f'<tspan x="{x:g}" dy="{line_height:g}">{escape(line)}</tspan>')
    return f'<text class="{class_name}"{anchor_attr}>{"".join(tspans)}</text>'


def _placed_port_label(
    element: SceneElement,
    occupied: list[Bounds],
    route_segments: list[tuple[tuple[float, float], tuple[float, float]]],
    close_packed: bool = False,
    label_bounds: Bounds | None = None,
) -> list[str]:
    if element.symbol != "port" or not element.label.strip():
        return []
    x, y, anchor, bounds = _best_port_label_candidate(element, occupied, route_segments, close_packed, label_bounds)
    occupied.append(bounds)
    anchor_attr = f' text-anchor="{anchor}"' if anchor else ""
    return [f'<text class="small"{anchor_attr} x="{x:g}" y="{y:g}">{escape(element.label)}</text>']


def _best_port_label_candidate(
    element: SceneElement,
    occupied: list[Bounds],
    route_segments: list[tuple[tuple[float, float], tuple[float, float]]],
    close_packed: bool = False,
    label_bounds: Bounds | None = None,
) -> tuple[float, float, str, Bounds]:
    candidates = _port_label_candidates(element)
    external_port = element.owner == "boundary"
    checked_route_segments = [] if close_packed and not external_port else route_segments
    return min(
        candidates,
        key=lambda candidate: _label_penalty(
            candidate[3],
            occupied,
            checked_route_segments,
            label_bounds,
            strict_no_fly=external_port,
        ),
    )


def _close_packed_port_ids(elements: list[SceneElement]) -> set[str]:
    groups: dict[tuple[str | None, str | None], list[SceneElement]] = {}
    for element in elements:
        if element.symbol == "port" and element.label.strip():
            groups.setdefault((element.owner, element.port_side), []).append(element)

    close_packed: set[str] = set()
    for (_owner, side), ports in groups.items():
        if len(ports) < 2:
            continue
        if side in ("top", "bottom"):
            ports.sort(key=lambda port: port.box.center_x)
            for left, right in zip(ports, ports[1:]):
                left_width = _text_bounds(left.label, 0, 0, "middle").width
                right_width = _text_bounds(right.label, 0, 0, "middle").width
                min_gap = (left_width + right_width) / 2
                if right.box.center_x - left.box.center_x < min_gap:
                    close_packed.update((left.id, right.id))
        else:
            ports.sort(key=lambda port: port.box.center_y)
            min_gap = SMALL_TEXT_HEIGHT + LABEL_PADDING_Y * 2
            for upper, lower in zip(ports, ports[1:]):
                if lower.box.center_y - upper.box.center_y < min_gap:
                    close_packed.update((upper.id, lower.id))
    return close_packed


def _port_label_candidates(element: SceneElement) -> list[tuple[float, float, str, Bounds]]:
    box = element.box
    text = element.label
    side = element.port_side
    gap = DEFAULT_LABEL_OFFSET

    if side == "left":
        specs = [
            (box.x - gap, box.center_y + SMALL_TEXT_HEIGHT / 2 - 1, "end"),
            (box.x - gap, box.y - gap, "end"),
            (box.x - gap, box.y + box.height + gap + SMALL_TEXT_HEIGHT, "end"),
            (box.x + box.width + gap, box.center_y + SMALL_TEXT_HEIGHT / 2 - 1, ""),
            (box.x + box.width + gap, box.y - gap, ""),
            (box.x + box.width + gap, box.y + box.height + gap + SMALL_TEXT_HEIGHT, ""),
        ]
    elif side == "right":
        specs = [
            (box.x + box.width + gap, box.center_y + SMALL_TEXT_HEIGHT / 2 - 1, ""),
            (box.x + box.width + gap, box.y - gap, ""),
            (box.x + box.width + gap, box.y + box.height + gap + SMALL_TEXT_HEIGHT, ""),
            (box.x - gap, box.center_y + SMALL_TEXT_HEIGHT / 2 - 1, "end"),
            (box.x - gap, box.y - gap, "end"),
            (box.x - gap, box.y + box.height + gap + SMALL_TEXT_HEIGHT, "end"),
        ]
    elif side == "top":
        y0 = box.y - gap
        specs = [
            (box.center_x, y0, "middle"),
            (box.center_x, y0 - LABEL_STAGGER, "middle"),
            (box.center_x, y0 - LABEL_STAGGER * 2, "middle"),
            (box.x - gap, y0, "end"),
            (box.x + box.width + gap, y0, ""),
            (box.center_x, box.y + box.height + gap + SMALL_TEXT_HEIGHT, "middle"),
        ]
    else:
        y0 = box.y + box.height + gap + SMALL_TEXT_HEIGHT
        specs = [
            (box.center_x, y0, "middle"),
            (box.center_x, y0 + LABEL_STAGGER, "middle"),
            (box.center_x, y0 + LABEL_STAGGER * 2, "middle"),
            (box.x - gap, y0, "end"),
            (box.x + box.width + gap, y0, ""),
            (box.center_x, box.y - gap, "middle"),
        ]
    return [(x, y, anchor, _text_bounds(text, x, y, anchor)) for x, y, anchor in specs]


def _connection(points: list[tuple[float, float]], style: dict) -> list[str]:
    stroke = escape(str(style.get("stroke", "#334155")))
    stroke_width = float(style.get("stroke_width", 2))
    corner_radius = float(style.get("corner_radius", 0))
    path_data = _connection_path(points, corner_radius)
    marker_start = style.get("marker_start", "")
    marker = style.get("marker_end", "")
    marker_start_attr = f' marker-start="url(#{marker_start})"' if marker_start else ""
    marker_attr = f' marker-end="url(#{marker})"' if marker else ""
    dasharray = style.get("stroke_dasharray", style.get("stroke-dasharray", ""))
    dash_attr = f' stroke-dasharray="{escape(str(dasharray))}"' if dasharray else ""
    return [
        f'<path d="{path_data}" fill="none" stroke="{stroke}" stroke-width="{stroke_width:g}" stroke-linejoin="round" stroke-linecap="round"{dash_attr}{marker_start_attr}{marker_attr}/>'
    ]


def _connection_path(points: list[tuple[float, float]], corner_radius: float) -> str:
    if not points:
        return ""
    if len(points) == 1:
        return f"M {_point(points[0])}"

    commands = [f"M {_point(points[0])}"]
    if corner_radius <= 0 or len(points) == 2:
        commands.extend(f"L {_point(point)}" for point in points[1:])
        return " ".join(commands)

    for index in range(1, len(points) - 1):
        previous = points[index - 1]
        current = points[index]
        following = points[index + 1]
        rounded = _rounded_corner(previous, current, following, corner_radius)
        if rounded is None:
            commands.append(f"L {_point(current)}")
            continue
        before, after = rounded
        commands.append(f"L {_point(before)}")
        commands.append(f"Q {_point(current)} {_point(after)}")
    commands.append(f"L {_point(points[-1])}")
    return " ".join(commands)


def _rounded_corner(
    previous: tuple[float, float],
    current: tuple[float, float],
    following: tuple[float, float],
    radius: float,
) -> tuple[tuple[float, float], tuple[float, float]] | None:
    incoming = (current[0] - previous[0], current[1] - previous[1])
    outgoing = (following[0] - current[0], following[1] - current[1])
    incoming_length = (incoming[0] ** 2 + incoming[1] ** 2) ** 0.5
    outgoing_length = (outgoing[0] ** 2 + outgoing[1] ** 2) ** 0.5
    if incoming_length == 0 or outgoing_length == 0:
        return None

    incoming_unit = (incoming[0] / incoming_length, incoming[1] / incoming_length)
    outgoing_unit = (outgoing[0] / outgoing_length, outgoing[1] / outgoing_length)
    if abs(incoming_unit[0] - outgoing_unit[0]) < 1e-9 and abs(incoming_unit[1] - outgoing_unit[1]) < 1e-9:
        return None

    actual_radius = min(radius, incoming_length / 2, outgoing_length / 2)
    before = (
        current[0] - incoming_unit[0] * actual_radius,
        current[1] - incoming_unit[1] * actual_radius,
    )
    after = (
        current[0] + outgoing_unit[0] * actual_radius,
        current[1] + outgoing_unit[1] * actual_radius,
    )
    return before, after


def _point(point: tuple[float, float]) -> str:
    return f"{point[0]:g},{point[1]:g}"


def _connection_labels(
    points: list[tuple[float, float]],
    labels: list[dict],
    style: dict,
    occupied: list[Bounds] | None = None,
    route_segments: list[tuple[tuple[float, float], tuple[float, float]]] | None = None,
    label_bounds: Bounds | None = None,
) -> list[str]:
    output: list[str] = []
    occupied = occupied if occupied is not None else []
    route_segments = route_segments or []
    for label in labels:
        position = label.get("position", {})
        text = str(label.get("text", ""))
        if not text:
            continue
        if _uses_explicit_label_position(position):
            candidate = _explicit_label_candidate(points, position, style, text)
            if candidate is None:
                continue
        else:
            candidate = _best_label_candidate(
                points,
                position,
                style,
                text,
                occupied,
                route_segments,
                label_bounds,
            )

        x, y, anchor, bounds = candidate
        occupied.append(bounds)
        anchor_attr = f' text-anchor="{anchor}"' if anchor else ""
        output.append(f'<text class="small"{anchor_attr} x="{x:g}" y="{y:g}">{escape(text)}</text>')
    return output


def _uses_explicit_label_position(position: dict) -> bool:
    return "dx" in position or "dy" in position or "x" in position or "y" in position


def _explicit_label_candidate(
    points: list[tuple[float, float]],
    position: dict,
    style: dict,
    text: str,
) -> tuple[float, float, str, Bounds] | None:
    if "x" in position and "y" in position:
        x = float(position["x"])
        y = float(position["y"])
        anchor = position.get("text_anchor", "middle")
        return x, y, anchor, _text_bounds(text, x, y, anchor)

    segment = int(position.get("segment", 0))
    if segment < 0 or segment >= len(points) - 1:
        return None
    offset = float(position.get("offset", 0.5))
    start = points[segment]
    end = points[segment + 1]
    if "dx" in position or "dy" in position:
        dx = float(position.get("dx", 0))
        dy = float(position.get("dy", 0))
    else:
        dx, dy = _default_label_offset(start, end, float(style.get("label_offset", DEFAULT_LABEL_OFFSET)))
    x = start[0] + (end[0] - start[0]) * offset + dx
    y = start[1] + (end[1] - start[1]) * offset + dy
    anchor = position.get("text_anchor", "")
    return x, y, anchor, _text_bounds(text, x, y, anchor)


def _best_label_candidate(
    points: list[tuple[float, float]],
    position: dict,
    style: dict,
    text: str,
    occupied: list[Bounds],
    route_segments: list[tuple[tuple[float, float], tuple[float, float]]],
    label_bounds: Bounds | None = None,
) -> tuple[float, float, str, Bounds]:
    candidates = _label_candidates(points, position, style, text)
    return min(
        candidates,
        key=lambda candidate: _label_penalty(candidate[3], occupied, route_segments, label_bounds),
    )


def _label_candidates(
    points: list[tuple[float, float]],
    position: dict,
    style: dict,
    text: str,
) -> list[tuple[float, float, str, Bounds]]:
    preferred_segment = int(position.get("segment", -1))
    preferred_offset = float(position.get("offset", 0.5))
    label_offset = float(style.get("label_offset", DEFAULT_LABEL_OFFSET))
    centerline = position.get("placement") == "centerline"
    segment_indices = list(range(max(0, len(points) - 1)))
    if 0 <= preferred_segment < len(points) - 1:
        segment_indices.sort(key=lambda idx: (idx != preferred_segment, idx))
    else:
        segment_indices.sort(key=lambda idx: (-_segment_length(points[idx], points[idx + 1]), idx))

    offsets = _ordered_offsets(preferred_offset)
    candidates: list[tuple[float, float, str, Bounds]] = []
    for segment in segment_indices:
        start = points[segment]
        end = points[segment + 1]
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        for offset in offsets:
            if centerline:
                x = start[0] + dx * offset
                y = start[1] + dy * offset + _centerline_text_dy()
                candidates.append((x, y, "middle", _text_bounds(text, x, y, "middle")))
        if abs(dx) >= abs(dy):
            sides = [(0, -label_offset, "middle"), (0, label_offset + SMALL_TEXT_HEIGHT, "middle")]
        else:
            sides = [(label_offset, 0, ""), (-label_offset, 0, "end")]
        for offset in offsets:
            base_x = start[0] + dx * offset
            base_y = start[1] + dy * offset
            for side_dx, side_dy, anchor in sides:
                x = base_x + side_dx
                y = base_y + side_dy
                candidates.append((x, y, anchor, _text_bounds(text, x, y, anchor)))
    return candidates


def _centerline_text_dy() -> float:
    return (SMALL_TEXT_HEIGHT - 1 + LABEL_PADDING_Y * 2) / 2


def _ordered_offsets(preferred: float) -> list[float]:
    base = [preferred, 0.5, 0.35, 0.65, 0.2, 0.8]
    output: list[float] = []
    for value in base:
        clipped = max(0.08, min(0.92, value))
        if not any(abs(existing - clipped) < 0.01 for existing in output):
            output.append(clipped)
    return output


def _label_penalty(
    bounds: Bounds,
    occupied: list[Bounds],
    route_segments: list[tuple[tuple[float, float], tuple[float, float]]],
    label_bounds: Bounds | None = None,
    strict_no_fly: bool = False,
) -> tuple[float, ...]:
    area_overlap = sum(_overlap_area(bounds, obstacle) for obstacle in occupied)
    route_hits = sum(1 for start, end in route_segments if _segment_intersects_bounds(start, end, bounds))
    overflow = _bounds_overflow(bounds, label_bounds)
    if strict_no_fly:
        no_fly_hits = (1 if area_overlap > 0 else 0) + route_hits
        return (overflow, no_fly_hits, area_overlap, route_hits)
    return (overflow, area_overlap, route_hits)


def _bounds_overflow(bounds: Bounds, label_bounds: Bounds | None) -> float:
    if label_bounds is None:
        return max(0.0, -bounds.x) + max(0.0, -bounds.y)
    return (
        max(0.0, label_bounds.x - bounds.x)
        + max(0.0, label_bounds.y - bounds.y)
        + max(0.0, bounds.right - label_bounds.right)
        + max(0.0, bounds.bottom - label_bounds.bottom)
    )


def _initial_label_obstacles(elements: list[SceneElement]) -> list[Bounds]:
    obstacles: list[Bounds] = []
    for element in elements:
        if element.symbol == "boundary":
            if element.label:
                obstacles.append(_text_bounds(element.label, element.box.x + 10, element.box.y + 22, ""))
            continue
        if element.style.get("container"):
            if element.label:
                obstacles.append(_text_bounds(element.label, element.box.x + 12, element.box.y + 24, ""))
            continue
        obstacles.append(_box_bounds(element.box, pad=6))
        if element.label and element.symbol != "port":
            obstacles.append(_text_bounds(element.label, element.box.center_x, element.box.center_y, "middle"))
    return obstacles


def _box_bounds(box, pad: float = 0) -> Bounds:
    return Bounds(box.x - pad, box.y - pad, box.width + pad * 2, box.height + pad * 2)


def _text_bounds(text: str, x: float, y: float, anchor: str) -> Bounds:
    lines = str(text).splitlines() or [""]
    width = max(len(line) for line in lines) * TEXT_CHAR_WIDTH + LABEL_PADDING_X * 2
    height = len(lines) * SMALL_TEXT_HEIGHT + LABEL_PADDING_Y * 2
    if anchor == "middle":
        left = x - width / 2
    elif anchor == "end":
        left = x - width
    else:
        left = x
    top = y - SMALL_TEXT_HEIGHT + 1 - LABEL_PADDING_Y
    return Bounds(left, top, width, height)


def _overlap_area(a: Bounds, b: Bounds) -> float:
    x_overlap = max(0.0, min(a.right, b.right) - max(a.x, b.x))
    y_overlap = max(0.0, min(a.bottom, b.bottom) - max(a.y, b.y))
    return x_overlap * y_overlap


def _segment_intersects_bounds(
    start: tuple[float, float],
    end: tuple[float, float],
    bounds: Bounds,
) -> bool:
    x1, y1 = start
    x2, y2 = end
    if round(x1) == round(x2):
        x = x1
        return bounds.x <= x <= bounds.right and max(y1, y2) >= bounds.y and min(y1, y2) <= bounds.bottom
    if round(y1) == round(y2):
        y = y1
        return bounds.y <= y <= bounds.bottom and max(x1, x2) >= bounds.x and min(x1, x2) <= bounds.right
    return False


def _segment_length(start: tuple[float, float], end: tuple[float, float]) -> float:
    return ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5


def _default_label_offset(
    start: tuple[float, float],
    end: tuple[float, float],
    distance: float,
) -> tuple[float, float]:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = (dx**2 + dy**2) ** 0.5
    if length == 0:
        return (0, -distance)
    if abs(dx) >= abs(dy):
        return (0, -distance)
    return (distance, 0)
