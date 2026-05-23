import json
import unittest
from pathlib import Path

from sysmld.interconnection_view import compose
from sysmld.layout import _segments_cross


ROOT = Path(__file__).resolve().parents[1]


def _mechanical_spec():
    return {
        "diagram": "toaster-mech-composed-test",
        "kind": "InterconnectionView",
        "name": "Toaster Mechanical Interconnection",
        "model_files": ["toaster.sysml"],
        "direction": "bottom-up",
        "default_w": 160,
        "default_h": 80,
        "nodes": {
            "chassis": {"label": "Chassis", "style": "part.structure"},
            "lever": {"label": "Lever", "style": "part.mechanical"},
            "carriage": {"label": "Carriage", "style": "part.mechanical"},
            "buttons": {"label": "Buttons", "style": "part.mechanical"},
            "crumb-tray": {"label": "Crumb Tray", "style": "part.mechanical"},
            "pcs": {"label": "Power & Control\nSubsystem", "style": "part.control"},
        },
        "edges": [
            {"from": "chassis", "to": "carriage", "label": "guide"},
            {"from": "chassis", "to": "buttons", "label": "mount"},
            {"from": "chassis", "to": "crumb-tray", "label": "guide"},
            {"from": "chassis", "to": "pcs", "label": "mount"},
            {"from": "lever", "to": "carriage", "label": "lift"},
        ],
        "boundary_inputs": [
            {"to": "lever", "label": "lever input"},
            {"to": "buttons", "label": "button press"},
            {"to": "crumb-tray", "label": "pull/remove"},
        ],
        "styles": {
            "boundary.system": {"fill": "#FFFFFF", "stroke": "#333333", "stroke_width": 2},
            "part.mechanical": {"fill": "#E8F5E9", "stroke": "#2E7D32", "stroke_width": 2},
            "part.structure": {"fill": "#F5F5F5", "stroke": "#616161", "stroke_width": 2},
            "part.control": {"fill": "#E3F2FD", "stroke": "#1565C0", "stroke_width": 2},
            "connector.default": {"stroke": "#2E7D32", "stroke_width": 2},
        },
    }


class ComposeTests(unittest.TestCase):
    def test_common_face_ports_follow_peer_geometry(self):
        doc = compose(_mechanical_spec())
        elements = {element["id"]: element for element in doc["diagram"]["elements"]}

        def center_x(node_id):
            layout = elements[node_id]["layout"]
            return layout["x"] + layout["width"] / 2

        chassis_ports = [
            element for element in elements.values()
            if element["symbol"] == "port"
            and element.get("owner") == "chassis"
            and element["id"].startswith("chassis--")
            and element["id"].endswith("--src")
            and element["placement"]["side"] == "top"
        ]
        by_offset = sorted(chassis_ports, key=lambda element: element["placement"]["offset"])
        peer_xs = [
            center_x(element["id"].removeprefix("chassis--").removesuffix("--src"))
            for element in by_offset
        ]

        self.assertEqual(peer_xs, sorted(peer_xs))

    def test_single_diagonal_source_uses_open_side_port(self):
        doc = compose(_mechanical_spec())
        elements = {element["id"]: element for element in doc["diagram"]["elements"]}

        self.assertEqual(elements["lever--carriage--src"]["placement"]["side"], "right")

    def test_toaster_crowded_chassis_fanout_uses_open_side_port(self):
        doc = compose(_mechanical_spec())
        elements = {element["id"]: element for element in doc["diagram"]["elements"]}

        self.assertEqual(elements["chassis--buttons--src"]["placement"]["side"], "left")

    def test_toaster_lift_route_uses_single_elbow(self):
        doc = compose(_mechanical_spec())
        connections = {
            connection["id"]: connection
            for connection in doc["diagram"]["connections"]
        }

        self.assertEqual(len(connections["conn-lever-carriage"]["route"]["waypoints"]), 1)

    def test_composed_routes_do_not_cross_element_interiors(self):
        doc = compose(_mechanical_spec())
        elements = {element["id"]: element for element in doc["diagram"]["elements"]}
        boxes = {
            element["id"]: element["layout"]
            for element in elements.values()
            if element["symbol"] == "part_usage"
        }

        for connection in doc["diagram"]["connections"]:
            points = [
                _port_point(elements, connection["source"]["element"]),
                *[
                    (point["x"], point["y"])
                    for point in connection["route"].get("waypoints", [])
                ],
                _port_point(elements, connection["target"]["element"]),
            ]
            for start, end in zip(points, points[1:]):
                for box in boxes.values():
                    self.assertFalse(
                        _segment_crosses_interior(start, end, box),
                        f"{connection['id']} crosses {box}",
                    )

    def test_toaster_composed_routes_do_not_cross_each_other(self):
        doc = compose(_mechanical_spec())

        self.assertEqual(_route_crossings(doc), [])

    def test_toaster_electrical_routes_do_not_cross_each_other(self):
        spec_path = ROOT / "examples" / "toaster" / "toaster-electrical-icn.json"
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        doc = compose(spec)

        self.assertEqual(_route_crossings(doc), [])
        self.assertEqual(_route_box_hits(doc), [])

    def test_boundary_input_target_labels_are_preserved(self):
        doc = compose({
            "diagram": "boundary-labels",
            "kind": "InterconnectionView",
            "direction": "left-right",
            "label_mode": "port",
            "nodes": {"button": {"label": "Button"}},
            "boundary_inputs": [
                {"to": "button", "label": "Button Input", "target_label": "press"}
            ],
        })
        ports = {
            element["id"]: element
            for element in doc["diagram"]["elements"]
            if element["symbol"] == "port"
        }

        self.assertEqual(ports["button--bnd--tgt"]["label"], "press")

    def test_blender_composed_routes_do_not_cross_each_other(self):
        spec_path = ROOT / "examples" / "blender" / "blender-ibd-composed.json"
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        doc = compose(spec)

        self.assertEqual(_route_crossings(doc), [])

    def test_blender_composed_routes_do_not_cross_element_interiors(self):
        spec_path = ROOT / "examples" / "blender" / "blender-ibd-composed.json"
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        doc = compose(spec)

        self.assertEqual(_route_box_hits(doc), [])

    def test_blender_aligned_connections_stay_straight(self):
        spec_path = ROOT / "examples" / "blender" / "blender-ibd-composed.json"
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        doc = compose(spec)
        connections = {
            connection["id"]: connection
            for connection in doc["diagram"]["connections"]
        }

        self.assertEqual(connections["conn-motorBase-motor"]["route"]["waypoints"], [])
        self.assertEqual(connections["conn-controlPanel-motor"]["route"]["waypoints"], [])
        self.assertEqual(connections["conn-bladeAssembly-driveCoupling"]["route"]["waypoints"], [])

    def test_generated_internal_ports_have_blank_labels(self):
        doc = compose(_mechanical_spec())
        for element in doc["diagram"]["elements"]:
            if element["symbol"] != "port" or element.get("owner") == "boundary":
                continue
            self.assertEqual(element.get("label"), "")

    def test_golden_rank_wrap_compacts_long_chains(self):
        base_spec = {
            "diagram": "long-chain",
            "kind": "InterconnectionView",
            "name": "Long Chain",
            "direction": "top-down",
            "nodes": {f"n{i}": {"label": f"N{i}"} for i in range(8)},
            "edges": [
                {"from": f"n{i}", "to": f"n{i + 1}", "label": "flow"}
                for i in range(7)
            ],
        }
        wrapped = compose({**base_spec, "rank_wrap": "golden"})
        unwrapped = compose(base_spec)

        wrapped_canvas = wrapped["diagram"]["canvas"]
        unwrapped_canvas = unwrapped["diagram"]["canvas"]
        aspect = wrapped_canvas["width"] / wrapped_canvas["height"]

        self.assertGreater(wrapped_canvas["width"], wrapped_canvas["height"])
        self.assertLess(wrapped_canvas["height"], unwrapped_canvas["height"])
        self.assertGreater(aspect, 1.2)
        self.assertLess(aspect, 2.2)


def _port_point(elements, port_id):
    port = elements[port_id]
    owner = elements[port["owner"]]
    layout = owner["layout"]
    side = port["placement"]["side"]
    offset = port["placement"]["offset"]
    x = layout["x"]
    y = layout["y"]
    w = layout["width"]
    h = layout["height"]
    if side == "top":
        return x + w * offset, y
    if side == "bottom":
        return x + w * offset, y + h
    if side == "right":
        return x + w, y + h * offset
    return x, y + h * offset


def _route_crossings(doc):
    elements = {element["id"]: element for element in doc["diagram"]["elements"]}
    segments = []
    for connection in doc["diagram"]["connections"]:
        points = [
            _port_point(elements, connection["source"]["element"]),
            *[
                (point["x"], point["y"])
                for point in connection["route"].get("waypoints", [])
            ],
            _port_point(elements, connection["target"]["element"]),
        ]
        for start, end in zip(points, points[1:]):
            segments.append((connection["id"], start, end))

    crossings = []
    for i, (first_id, first_start, first_end) in enumerate(segments):
        for second_id, second_start, second_end in segments[i + 1:]:
            if first_id == second_id:
                continue
            if {first_start, first_end} & {second_start, second_end}:
                continue
            if _segments_cross(first_start, first_end, second_start, second_end):
                crossings.append((first_id, second_id))
    return crossings


def _route_box_hits(doc):
    elements = {element["id"]: element for element in doc["diagram"]["elements"]}
    boxes = {
        element["id"]: element["layout"]
        for element in elements.values()
        if element["symbol"] == "part_usage"
    }
    hits = []
    for connection in doc["diagram"]["connections"]:
        source_owner = elements[connection["source"]["element"]].get("owner")
        target_owner = elements[connection["target"]["element"]].get("owner")
        points = [
            _port_point(elements, connection["source"]["element"]),
            *[
                (point["x"], point["y"])
                for point in connection["route"].get("waypoints", [])
            ],
            _port_point(elements, connection["target"]["element"]),
        ]
        for start, end in zip(points, points[1:]):
            for box_id, box in boxes.items():
                if box_id in (source_owner, target_owner):
                    continue
                if _segment_crosses_interior(start, end, box):
                    hits.append((connection["id"], box_id))
    return hits


def _segment_crosses_interior(start, end, box):
    x1, y1 = start
    x2, y2 = end
    left = box["x"]
    right = box["x"] + box["width"]
    top = box["y"]
    bottom = box["y"] + box["height"]

    if round(x1) == round(x2):
        x = x1
        if x <= left or x >= right:
            return False
        return max(y1, y2) > top and min(y1, y2) < bottom
    if round(y1) == round(y2):
        y = y1
        if y <= top or y >= bottom:
            return False
        return max(x1, x2) > left and min(x1, x2) < right
    raise AssertionError(f"non-orthogonal segment: {start} -> {end}")


if __name__ == "__main__":
    unittest.main()
