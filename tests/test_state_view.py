import json
from pathlib import Path
import unittest

from sysmld.layout import _segments_cross
from sysmld.state_view import compose_stm
from tests.test_interconnection_view import _segment_crosses_interior


ROOT = Path(__file__).resolve().parents[1]


class StateMachineComposerTests(unittest.TestCase):
    def test_resettable_error_and_done_states_are_not_final_nodes(self):
        spec = json.loads((ROOT / "examples/toaster/toaster-stm.json").read_text(encoding="utf-8"))
        doc = compose_stm(spec)
        elements = {
            element["id"]: element
            for element in doc["diagram"]["elements"]
        }

        self.assertEqual(elements["error"]["symbol"], "state_usage")
        self.assertEqual(elements["done"]["symbol"], "state_usage")

    def test_stm_routes_do_not_overlap_or_cross_state_boxes(self):
        for path in [
            ROOT / "examples/toaster/toaster-stm.json",
            ROOT / "examples/blender/blender-stm.json",
        ]:
            with self.subTest(path=path.name):
                spec = json.loads(path.read_text(encoding="utf-8"))
                doc = compose_stm(spec)
                self.assertEqual(_route_overlaps(doc), [])
                self.assertEqual(_route_crossings(doc), [])
                self.assertEqual(_route_box_hits(doc), [])

    def test_unlabeled_initial_transition_uses_subject_model_ref(self):
        spec = json.loads((ROOT / "examples/toaster/toaster-stm.json").read_text(encoding="utf-8"))
        doc = compose_stm(spec)
        initial_transition = next(
            connection
            for connection in doc["diagram"]["connections"]
            if connection["id"] == "initial--idle"
        )

        self.assertEqual(initial_transition["model_ref"], "toasterControl")

    def test_adjacent_backward_transitions_route_locally(self):
        spec = json.loads((ROOT / "examples/toaster/toaster-stm.json").read_text(encoding="utf-8"))
        doc = compose_stm(spec)
        elements = {
            element["id"]: element
            for element in doc["diagram"]["elements"]
        }
        connections = {
            connection["id"]: connection
            for connection in doc["diagram"]["connections"]
        }
        heating = elements["heating"]["layout"]
        idle = elements["idle"]["layout"]
        local_routes = [connections["heating-back-idle"]]

        for connection in local_routes:
            self.assertEqual(connection["source"]["anchor"]["side"], "bottom")
            self.assertEqual(connection["target"]["anchor"]["side"], "bottom")
            self.assertEqual(len(connection["route"]["waypoints"]), 2)
            max_route_x = max(point["x"] for point in connection["route"]["waypoints"])
            self.assertLess(max_route_x, heating["x"] + heating["width"])
            self.assertGreater(max_route_x, idle["x"] + idle["width"])

    def test_composite_state_wraps_child_states(self):
        spec = json.loads((ROOT / "examples/blender/blender-stm.json").read_text(encoding="utf-8"))
        doc = compose_stm(spec)
        elements = {
            element["id"]: element
            for element in doc["diagram"]["elements"]
        }
        powered = elements["powered"]["layout"]

        for child_id in ["poweredInitial", "ready", "blending", "error"]:
            child = elements[child_id]["layout"]
            self.assertGreater(child["x"], powered["x"])
            self.assertGreater(child["y"], powered["y"])
            self.assertLess(child["x"] + child["width"], powered["x"] + powered["width"])
            self.assertLess(child["y"] + child["height"], powered["y"] + powered["height"])

        off = elements["off"]["layout"]
        self.assertLess(off["x"] + off["width"], powered["x"])
        self.assertGreaterEqual(powered["x"] - (off["x"] + off["width"]), 50)

    def test_composite_power_off_uses_container_endpoint(self):
        spec = json.loads((ROOT / "examples/blender/blender-stm.json").read_text(encoding="utf-8"))
        doc = compose_stm(spec)
        connections = {
            connection["id"]: connection
            for connection in doc["diagram"]["connections"]
        }

        self.assertIn("off--powered", connections)
        self.assertEqual(connections["off--powered"]["source"]["element"], "off")
        self.assertEqual(connections["off--powered"]["target"]["element"], "powered")
        self.assertIn("poweredInitial--ready", connections)
        self.assertIn("powered--off", connections)
        self.assertEqual(connections["powered--off"]["source"]["element"], "powered")
        self.assertEqual(connections["powered--off"]["target"]["element"], "off")
        self.assertNotIn("off--ready", connections)
        self.assertNotIn("ready-back-off", connections)
        self.assertNotIn("blending-back-off", connections)

    def test_internal_composite_routes_stay_inside_container(self):
        spec = json.loads((ROOT / "examples/blender/blender-stm.json").read_text(encoding="utf-8"))
        doc = compose_stm(spec)
        elements = {
            element["id"]: element
            for element in doc["diagram"]["elements"]
        }
        powered = elements["powered"]["layout"]
        connections = [
            connection
            for connection in doc["diagram"]["connections"]
            if connection["source"]["element"] in {"ready", "blending", "error"}
            and connection["target"]["element"] in {"ready", "blending", "error"}
        ]

        for connection in connections:
            points = [
                _port_point(elements, connection["source"]),
                *[
                    (point["x"], point["y"])
                    for point in connection["route"].get("waypoints", [])
                ],
                _port_point(elements, connection["target"]),
            ]
            for x, y in points:
                self.assertGreaterEqual(x, powered["x"])
                self.assertGreaterEqual(y, powered["y"])
                self.assertLessEqual(x, powered["x"] + powered["width"])
                self.assertLessEqual(y, powered["y"] + powered["height"])

    def test_nested_composite_states_wrap_recursively(self):
        doc = compose_stm({
            "diagram": "nested-stm",
            "kind": "StateView",
            "subject": "controller",
            "states": {
                "off": {"label": "Off"},
                "powered": {"label": "Powered", "composite": True},
                "operating": {"label": "Operating", "parent": "powered", "composite": True},
                "running": {"label": "Running", "parent": "operating"},
            },
            "transitions": [
                {"from": "off", "to": "running", "label": "power on"},
            ],
        })
        elements = {
            element["id"]: element
            for element in doc["diagram"]["elements"]
        }

        self.assert_box_contains(elements["powered"]["layout"], elements["operating"]["layout"])
        self.assert_box_contains(elements["operating"]["layout"], elements["running"]["layout"])
        self.assertLess(elements["off"]["layout"]["x"] + elements["off"]["layout"]["width"], elements["powered"]["layout"]["x"])

    def test_concurrent_composite_states_emit_region_dividers(self):
        doc = compose_stm({
            "diagram": "concurrent-stm",
            "kind": "StateView",
            "subject": "controller",
            "states": {
                "powered": {
                    "label": "Powered",
                    "composite": True,
                    "concurrent": True,
                    "regions": [
                        {"id": "drive", "label": "Drive Control"},
                        {"id": "monitoring", "label": "Monitoring"},
                    ],
                },
                "runMotor": {"label": "Run Motor", "parent": "powered", "region": "drive"},
                "senseLoad": {"label": "Sense Load", "parent": "powered", "region": "monitoring"},
            },
            "transitions": [],
        })
        annotations = doc["diagram"]["annotations"]

        self.assertEqual(len(annotations), 1)
        self.assertEqual(annotations[0]["type"], "state_region_divider")
        self.assertEqual(annotations[0]["label"], "Monitoring")

    def assert_box_contains(self, outer, inner):
        self.assertGreater(inner["x"], outer["x"])
        self.assertGreater(inner["y"], outer["y"])
        self.assertLess(inner["x"] + inner["width"], outer["x"] + outer["width"])
        self.assertLess(inner["y"] + inner["height"], outer["y"] + outer["height"])


def _port_point(elements, endpoint):
    element = elements[endpoint["element"]]
    layout = element["layout"]
    side = endpoint["anchor"]["side"]
    offset = endpoint["anchor"]["offset"]
    x = layout["x"]
    y = layout["y"]
    w = layout["width"]
    h = layout["height"]
    if side == "left":
        return x, y + h * offset
    if side == "right":
        return x + w, y + h * offset
    if side == "top":
        return x + w * offset, y
    return x + w * offset, y + h


def _route_segments(doc):
    elements = {
        element["id"]: element
        for element in doc["diagram"]["elements"]
    }
    segments = []
    for connection in doc["diagram"]["connections"]:
        points = [
            _port_point(elements, connection["source"]),
            *[
                (point["x"], point["y"])
                for point in connection["route"].get("waypoints", [])
            ],
            _port_point(elements, connection["target"]),
        ]
        for start, end in zip(points, points[1:]):
            segments.append((connection["id"], start, end))
    return elements, segments


def _route_overlaps(doc):
    _elements, segments = _route_segments(doc)
    overlaps = []
    for i, (first_id, first_start, first_end) in enumerate(segments):
        for second_id, second_start, second_end in segments[i + 1:]:
            if first_id == second_id:
                continue
            if _collinear_overlap(first_start, first_end, second_start, second_end):
                overlaps.append((first_id, second_id))
    return overlaps


def _route_crossings(doc):
    _elements, segments = _route_segments(doc)
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


def _collinear_overlap(a, b, c, d):
    if a[0] == b[0] == c[0] == d[0]:
        return max(min(a[1], b[1]), min(c[1], d[1])) < min(max(a[1], b[1]), max(c[1], d[1]))
    if a[1] == b[1] == c[1] == d[1]:
        return max(min(a[0], b[0]), min(c[0], d[0])) < min(max(a[0], b[0]), max(c[0], d[0]))
    return False


def _route_box_hits(doc):
    elements, segments = _route_segments(doc)
    boxes = {
        element["id"]: element["layout"]
        for element in elements.values()
        if element["symbol"] != "boundary"
        and element.get("style") != "state.composite"
    }
    connections = {
        connection["id"]: connection
        for connection in doc["diagram"]["connections"]
    }
    hits = []
    for connection_id, start, end in segments:
        own = {
            connections[connection_id]["source"]["element"],
            connections[connection_id]["target"]["element"],
        }
        for box_id, box in boxes.items():
            if box_id in own:
                continue
            if _segment_crosses_interior(start, end, box):
                hits.append((connection_id, box_id))
    return hits


if __name__ == "__main__":
    unittest.main()
