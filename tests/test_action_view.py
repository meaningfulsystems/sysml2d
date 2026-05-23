import json
from pathlib import Path
import unittest

from sysmld.views import action
from sysmld.layout import _segments_cross
from tests.test_interconnection_view import _segment_crosses_interior


ROOT = Path(__file__).resolve().parents[1]


class ActionComposerTests(unittest.TestCase):
    def test_activity_layout_defaults_to_portrait_top_down_flow(self):
        spec = json.loads((ROOT / "examples/toaster/toaster-act.json").read_text(encoding="utf-8"))
        doc = action(spec)
        elements = {element["id"]: element for element in doc["diagram"]["elements"]}
        canvas = doc["diagram"]["canvas"]

        self.assertLessEqual(elements["toastStart"]["layout"]["width"], 24)
        self.assertEqual(elements["toastStart"]["layout"]["height"], 20)
        self.assertLess(canvas["width"], canvas["height"])
        ordered = [
            "toastStart",
            "insertBread",
            "lowerLever",
            "latchCarriage",
            "energizeHeater",
            "monitorToastTimer",
            "toastDecision",
            "releaseCarriage",
            "presentToast",
            "toastEnd",
        ]
        y_positions = [elements[node_id]["layout"]["y"] for node_id in ordered]
        self.assertEqual(y_positions, sorted(y_positions))
        x_centers = [
            elements[node_id]["layout"]["x"] + elements[node_id]["layout"]["width"] / 2
            for node_id in ordered
        ]
        self.assertLess(max(x_centers) - min(x_centers), 1)

    def test_activity_routes_do_not_cross_action_boxes_or_each_other(self):
        for path in [
            ROOT / "examples/toaster/toaster-act.json",
            ROOT / "examples/blender/blender-act.json",
        ]:
            with self.subTest(path=path.name):
                spec = json.loads(path.read_text(encoding="utf-8"))
                doc = action(spec)
                self.assertEqual(_route_box_hits(doc), [])
                self.assertEqual(_route_crossings(doc), [])

    def test_backward_activity_loop_uses_side_channel(self):
        spec = json.loads((ROOT / "examples/blender/blender-act.json").read_text(encoding="utf-8"))
        doc = action(spec)
        connections = {connection["id"]: connection for connection in doc["diagram"]["connections"]}
        loop = connections["conn-smoothEnough-spinBladeAssembly"]

        self.assertEqual(loop["source"]["anchor"]["side"], "right")
        self.assertEqual(loop["target"]["anchor"]["side"], "right")
        self.assertEqual(len(loop["route"]["waypoints"]), 2)

    def test_activity_edges_default_to_control_flow_arrows(self):
        spec = json.loads((ROOT / "examples/toaster/toaster-act.json").read_text(encoding="utf-8"))
        doc = action(spec)

        self.assertTrue(doc["diagram"]["connections"])
        for connection in doc["diagram"]["connections"]:
            self.assertEqual(connection["style"], "connector.control_flow")


def _anchor_point(elements, endpoint):
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
    elements = {element["id"]: element for element in doc["diagram"]["elements"]}
    segments = []
    for connection in doc["diagram"]["connections"]:
        points = [
            _anchor_point(elements, connection["source"]),
            *[
                (point["x"], point["y"])
                for point in connection["route"].get("waypoints", [])
            ],
            _anchor_point(elements, connection["target"]),
        ]
        for start, end in zip(points, points[1:]):
            segments.append((connection["id"], start, end))
    return elements, segments


def _route_box_hits(doc):
    elements, segments = _route_segments(doc)
    boxes = {
        element["id"]: element["layout"]
        for element in elements.values()
        if element["symbol"] not in {"initial_state", "activity_final_node"}
    }
    connections = {connection["id"]: connection for connection in doc["diagram"]["connections"]}
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


def _route_crossings(doc):
    _elements, segments = _route_segments(doc)
    crossings = []
    for index, (first_id, first_start, first_end) in enumerate(segments):
        for second_id, second_start, second_end in segments[index + 1:]:
            if first_id == second_id:
                continue
            if {first_start, first_end} & {second_start, second_end}:
                continue
            if _segments_cross(first_start, first_end, second_start, second_end):
                crossings.append((first_id, second_id))
    return crossings


if __name__ == "__main__":
    unittest.main()
