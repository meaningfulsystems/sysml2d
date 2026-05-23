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
        self.assertEqual(second_row_bus_y, first_row_bus_y)

        second_row_label = connections["conn-root-child-4"]["labels"][0]["position"]
        self.assertGreater(second_row_label["offset"], 0.9)

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


if __name__ == "__main__":
    unittest.main()
