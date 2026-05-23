import json
from pathlib import Path
import unittest

from sysmld.layout import _segments_cross
from sysmld.requirement_view import requirement


ROOT = Path(__file__).resolve().parents[1]


class RequirementComposerTests(unittest.TestCase):
    def test_requirement_examples_have_no_route_crossings_or_box_hits(self):
        for path in [
            ROOT / "examples/toaster/toaster-req.json",
            ROOT / "examples/blender/blender-req.json",
        ]:
            with self.subTest(path=path.name):
                spec = json.loads(path.read_text(encoding="utf-8"))
                doc = requirement(spec)

                self.assertEqual(_route_crossings(doc), [])
                self.assertEqual(_route_box_hits(doc), [])

    def test_requirement_routes_use_polyline_dependency_lines(self):
        spec = json.loads((ROOT / "examples/toaster/toaster-req.json").read_text(encoding="utf-8"))
        doc = requirement(spec)

        self.assertTrue(doc["diagram"]["connections"])
        for connection in doc["diagram"]["connections"]:
            self.assertEqual(connection["route"]["kind"], "polyline")
            self.assertEqual(connection["route"]["waypoints"], [])


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


def _route_box_hits(doc):
    elements, segments = _route_segments(doc)
    boxes = {
        element["id"]: element["layout"]
        for element in elements.values()
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
            if _segment_hits_box(start, end, box):
                hits.append((connection_id, box_id))
    return hits


def _segment_hits_box(start, end, box):
    x1, y1 = start
    x2, y2 = end
    left = box["x"]
    right = box["x"] + box["width"]
    top = box["y"]
    bottom = box["y"] + box["height"]
    dx = x2 - x1
    dy = y2 - y1
    t0 = 0.0
    t1 = 1.0
    for p, q in [
        (-dx, x1 - left),
        (dx, right - x1),
        (-dy, y1 - top),
        (dy, bottom - y1),
    ]:
        if p == 0:
            if q <= 0:
                return False
            continue
        r = q / p
        if p < 0:
            t0 = max(t0, r)
        else:
            t1 = min(t1, r)
        if t0 >= t1:
            return False
    return t0 < 1 and t1 > 0


if __name__ == "__main__":
    unittest.main()
