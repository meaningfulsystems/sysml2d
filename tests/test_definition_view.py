import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from sysmld.definition_view import compose_tree, tree_file


ROOT = Path(__file__).resolve().parents[1]


class TreeComposerTests(unittest.TestCase):
    def test_tree_layout_handles_multiple_depths_deterministically(self):
        doc = compose_tree({
            "diagram": "deep-tree",
            "kind": "DefinitionView",
            "name": "Deep Tree",
            "model_files": ["model.sysml"],
            "roots": [
                {
                    "id": "root",
                    "children": [
                        {"id": "left", "children": [{"id": "leaf"}]},
                        {"id": "right"},
                    ],
                }
            ],
        })
        elements = {
            element["id"]: element
            for element in doc["diagram"]["elements"]
        }

        self.assertEqual(doc["diagram"]["kind"], "DefinitionView")
        self.assertLess(elements["root"]["layout"]["y"], elements["left"]["layout"]["y"])
        self.assertLess(elements["left"]["layout"]["y"], elements["leaf"]["layout"]["y"])
        self.assertLess(elements["left"]["layout"]["x"], elements["right"]["layout"]["x"])
        self.assertEqual(
            [connection["id"] for connection in doc["diagram"]["connections"]],
            ["conn-root-left", "conn-root-right", "conn-left-leaf"],
        )

    def test_wide_sibling_layer_wraps_into_staggered_rows(self):
        doc = compose_tree({
            "diagram": "wide-tree",
            "kind": "DefinitionView",
            "name": "Wide Tree",
            "max_siblings_per_row": 6,
            "roots": [
                {
                    "id": "root",
                    "children": [{"id": f"child-{index}"} for index in range(8)],
                }
            ],
        })
        elements = {
            element["id"]: element
            for element in doc["diagram"]["elements"]
        }
        first_row_y = elements["child-0"]["layout"]["y"]
        second_row_y = elements["child-4"]["layout"]["y"]
        first_gap_left = elements["child-0"]["layout"]["x"] + elements["child-0"]["layout"]["width"]
        first_gap_right = elements["child-1"]["layout"]["x"]
        second_center = elements["child-4"]["layout"]["x"] + elements["child-4"]["layout"]["width"] / 2

        self.assertGreater(second_row_y, first_row_y)
        self.assertLess(first_gap_left, second_center)
        self.assertLess(second_center, first_gap_right)

        connections = {
            connection["id"]: connection
            for connection in doc["diagram"]["connections"]
        }
        first_row_bus_y = connections["conn-root-child-0"]["route"]["waypoints"][0]["y"]
        second_row_bus_y = connections["conn-root-child-4"]["route"]["waypoints"][0]["y"]
        self.assertGreater(second_row_bus_y, first_row_bus_y)

        second_row_label = connections["conn-root-child-4"]["labels"][0]["position"]
        self.assertGreater(second_row_label["offset"], 0.9)

    def test_stacked_column_wrap_does_not_rejoin_blocker_centerline(self):
        spec = {
            "diagram": "spine-tree",
            "kind": "DefinitionView",
            "name": "Spine Tree",
            "route_around_boxes": True,
            "break_column_spines": True,
            "max_siblings_per_row": 1,
            "default_w": 80,
            "default_h": 40,
            "rank_gap": 40,
            "row_gap": 16,
            "roots": [
                {
                    "id": "root",
                    "w": 80,
                    "children": [
                        {"id": "blocker", "w": 80},
                        {
                            "id": "mid",
                            "w": 80,
                            "children": [{"id": "leaf", "w": 80}],
                        },
                    ],
                }
            ],
        }
        doc = compose_tree(spec)
        boxes = {element["id"]: element["layout"] for element in doc["diagram"]["elements"]}
        connections = {connection["id"]: connection for connection in doc["diagram"]["connections"]}
        self.assertEqual(connections["conn-root-mid"]["target"]["anchor"]["side"], "left")
        self.assertEqual(connections["conn-mid-leaf"]["target"]["anchor"]["side"], "left")
        self.assertEqual(_definition_box_hits(doc), [])
        self.assertFalse(
            _rejoins_stacked_centerline(doc, "blocker", ("mid", "leaf")),
            "wrap rejoined the blocker/mid/leaf centerline",
        )
        blocker_left = boxes["blocker"]["x"]
        col_top = boxes["blocker"]["y"]
        col_bottom = boxes["leaf"]["y"] + boxes["leaf"]["height"]
        for conn_id in ("conn-root-mid", "conn-mid-leaf"):
            points = _connection_points(doc, connections[conn_id])
            for start, end in zip(points, points[1:]):
                if abs(start[0] - end[0]) >= 0.6:
                    continue
                lo, hi = sorted((start[1], end[1]))
                if hi < col_top or lo > col_bottom:
                    continue
                self.assertLess(start[0], blocker_left, f"{conn_id} vertical at {start[0]} is not left of blocker")

        unchanged = compose_tree({**spec, "break_column_spines": False})
        self.assertTrue(
            _rejoins_stacked_centerline(unchanged, "blocker", ("mid", "leaf")),
            "centerline-rejoin detector must fail the old top-entry spine",
        )

    def test_later_wrap_routes_around_first_row_boxes(self):
        doc = compose_tree({
            "diagram": "around-tree",
            "kind": "DefinitionView",
            "name": "Around Tree",
            "route_around_boxes": True,
            "max_siblings_per_row": 1,
            "default_w": 80,
            "default_h": 40,
            "rank_gap": 40,
            "row_gap": 16,
            "roots": [
                {
                    "id": "root",
                    "w": 80,
                    "children": [
                        {"id": "blocker", "w": 200},
                        {"id": "tail", "w": 80},
                    ],
                }
            ],
        })
        hits = _definition_box_hits(doc)
        self.assertEqual(hits, [])
        self.assertNotIn(("conn-root-tail", "blocker"), hits)
        connections = {connection["id"]: connection for connection in doc["diagram"]["connections"]}
        wrap = connections["conn-root-tail"]["route"]["waypoints"]
        self.assertGreaterEqual(len(wrap), 2)
        blocker = next(element["layout"] for element in doc["diagram"]["elements"] if element["id"] == "blocker")
        rail_x = wrap[1]["x"]
        self.assertTrue(
            rail_x <= blocker["x"] or rail_x >= blocker["x"] + blocker["width"],
            f"wrap rail {rail_x} still crosses blocker",
        )

    def test_wrapped_rows_with_grandchildren_do_not_overlap(self):
        doc = compose_tree({
            "diagram": "stacked-tree",
            "kind": "DefinitionView",
            "name": "Stacked Tree",
            "max_siblings_per_row": 2,
            "default_w": 80,
            "default_h": 40,
            "rank_gap": 40,
            "row_gap": 16,
            "roots": [
                {
                    "id": "root",
                    "children": [
                        {"id": "left", "children": [{"id": "left-a"}, {"id": "left-b"}]},
                        {"id": "right", "children": [{"id": "right-a"}]},
                        {"id": "tail", "children": [{"id": "tail-a"}]},
                    ],
                }
            ],
        })
        boxes = {
            element["id"]: element["layout"]
            for element in doc["diagram"]["elements"]
        }
        self.assertLess(boxes["left"]["y"] + boxes["left"]["height"], boxes["tail"]["y"])
        ids = list(boxes)
        for index, first in enumerate(ids):
            a = boxes[first]
            for second in ids[index + 1:]:
                b = boxes[second]
                overlap = (
                    a["x"] < b["x"] + b["width"] - 1
                    and b["x"] < a["x"] + a["width"] - 1
                    and a["y"] < b["y"] + b["height"] - 1
                    and b["y"] < a["y"] + a["height"] - 1
                )
                self.assertFalse(overlap, f"{first} overlaps {second}")

    def test_tree_connections_use_part_refs_and_multiplicity_labels(self):
        doc = compose_tree({
            "diagram": "parts",
            "kind": "DefinitionView",
            "name": "Parts",
            "roots": [
                {
                    "id": "whole",
                    "children": [
                        {
                            "id": "part",
                            "model_ref": "partDef",
                            "part_ref": "partUsage",
                            "multiplicity": "0..1",
                        }
                    ],
                }
            ],
        })
        connection = doc["diagram"]["connections"][0]

        self.assertEqual(connection["model_ref"], "partUsage")
        self.assertEqual(connection["labels"][0]["text"], "0..1")
        self.assertEqual(connection["labels"][0]["position"]["dx"], 10)

    def test_tree_file_writes_sysmld(self):
        with TemporaryDirectory() as tmp:
            intent = Path(tmp) / "tree.json"
            intent.write_text(
                json.dumps({
                    "diagram": "sample-bdd",
                    "kind": "DefinitionView",
                    "name": "Sample BDD",
                    "roots": [{"id": "root"}],
                }),
                encoding="utf-8",
            )

            output = tree_file(intent)

            self.assertEqual(output, intent.with_suffix(".sysmld"))
            self.assertTrue(output.exists())

    def test_example_bdds_are_definition_trees(self):
        for path in [
            ROOT / "examples/toaster/toaster-bdd.json",
            ROOT / "examples/blender/blender-bdd.json",
        ]:
            with self.subTest(path=path.name):
                spec = json.loads(path.read_text(encoding="utf-8"))
                doc = compose_tree(spec)
                self.assertEqual(doc["diagram"]["kind"], "DefinitionView")
                self.assertTrue(all(element["symbol"] == "part_definition" for element in doc["diagram"]["elements"]))


def _connection_points(doc, connection):
    elements = {element["id"]: element for element in doc["diagram"]["elements"]}
    source = connection["source"]
    target = connection["target"]
    return [
        _anchor(elements[source["element"]], source["anchor"]["side"]),
        *[(point["x"], point["y"]) for point in connection["route"].get("waypoints", [])],
        _anchor(elements[target["element"]], target["anchor"]["side"]),
    ]


def _is_vertical_run(doc, connection, x, tol=8):
    points = _connection_points(doc, connection)
    for start, end in zip(points, points[1:]):
        if abs(start[0] - end[0]) < 0.6 and abs(start[0] - x) <= tol and abs(start[1] - end[1]) > 8:
            return True
    return False


def _rejoins_stacked_centerline(doc, blocker_id, stacked_ids):
    """True when a vertical bus sits on the shared centerline through a stacked column.

    Interior-only hits miss a jog that rides the gaps and then re-enters the spine.
    """
    elements = {element["id"]: element for element in doc["diagram"]["elements"]}
    blocker = elements[blocker_id]["layout"]
    column = [blocker, *[elements[node_id]["layout"] for node_id in stacked_ids]]
    cx = blocker["x"] + blocker["width"] / 2
    col_top = min(box["y"] for box in column)
    col_bottom = max(box["y"] + box["height"] for box in column)
    stacked_top = min(elements[node_id]["layout"]["y"] for node_id in stacked_ids)
    for connection in doc["diagram"]["connections"]:
        ends = {connection["source"]["element"], connection["target"]["element"]}
        if not ends & {blocker_id, *stacked_ids}:
            continue
        points = _connection_points(doc, connection)
        for start, end in zip(points, points[1:]):
            if abs(start[0] - end[0]) >= 0.6:
                continue
            if abs(start[0] - cx) > 8:
                continue
            lo, hi = sorted((start[1], end[1]))
            if hi < col_top or lo > col_bottom:
                continue
            # First-row stub that only arrives at the blocker top may stay.
            if ends == {"root", blocker_id} and hi <= blocker["y"] + 1:
                continue
            if connection["target"]["element"] == blocker_id and hi <= blocker["y"] + 1:
                continue
            # A vertical on the centerline that reaches the stacked boxes or the
            # gap under the blocker is a rejoin / spine.
            if hi > stacked_top - 1 or lo >= blocker["y"] + blocker["height"] - 1:
                return True
    return False


def _definition_box_hits(doc):
    elements = {element["id"]: element for element in doc["diagram"]["elements"]}
    boxes = {element_id: element["layout"] for element_id, element in elements.items()}
    hits = []
    for connection in doc["diagram"]["connections"]:
        source = connection["source"]
        target = connection["target"]
        points = [
            _anchor(elements[source["element"]], source["anchor"]["side"]),
            *[(point["x"], point["y"]) for point in connection["route"].get("waypoints", [])],
            _anchor(elements[target["element"]], target["anchor"]["side"]),
        ]
        own = {source["element"], target["element"]}
        for start, end in zip(points, points[1:]):
            for box_id, box in boxes.items():
                if box_id in own:
                    continue
                if _segment_hits(start, end, box):
                    hits.append((connection["id"], box_id))
    return hits


def _anchor(element, side):
    layout = element["layout"]
    if side == "top":
        return layout["x"] + layout["width"] / 2, layout["y"]
    if side == "bottom":
        return layout["x"] + layout["width"] / 2, layout["y"] + layout["height"]
    if side == "left":
        return layout["x"], layout["y"] + layout["height"] / 2
    return layout["x"] + layout["width"], layout["y"] + layout["height"] / 2


def _segment_hits(start, end, box):
    x1, y1 = start
    x2, y2 = end
    left, right = box["x"], box["x"] + box["width"]
    top, bottom = box["y"], box["y"] + box["height"]
    if round(x1, 3) == round(x2, 3):
        return left < x1 < right and max(y1, y2) > top and min(y1, y2) < bottom
    if round(y1, 3) == round(y2, 3):
        return top < y1 < bottom and max(x1, x2) > left and min(x1, x2) < right
    return False


if __name__ == "__main__":
    unittest.main()
