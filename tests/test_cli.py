from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from sysmld.cli import main


class CliTests(unittest.TestCase):
    def test_compose_graph_sidecars_are_opt_in(self):
        with TemporaryDirectory() as tmp:
            intent = Path(tmp) / "sample.json"
            intent.write_text(
                json.dumps({
                    "diagram": "sample",
                    "kind": "InterconnectionView",
                    "direction": "left-right",
                    "nodes": {
                        "a": {"label": "A"},
                        "b": {"label": "B"},
                    },
                    "edges": [
                        {"from": "a", "to": "b", "label": "flow"},
                    ],
                }),
                encoding="utf-8",
            )

            with patch("sys.argv", ["sysmld", "compose", str(intent)]), redirect_stdout(StringIO()):
                self.assertEqual(main(), 0)

            self.assertTrue((Path(tmp) / "sample.sysmld").exists())
            self.assertFalse((Path(tmp) / "sample.graph.svg").exists())
            self.assertFalse((Path(tmp) / "sample.graph.json").exists())

            with patch("sys.argv", ["sysmld", "compose", str(intent), "--graph"]), redirect_stdout(StringIO()):
                self.assertEqual(main(), 0)

            self.assertTrue((Path(tmp) / "sample.graph.svg").exists())
            self.assertTrue((Path(tmp) / "sample.graph.json").exists())

    def test_bdd_alias_generates_tree_sysmld(self):
        with TemporaryDirectory() as tmp:
            intent = Path(tmp) / "sample-bdd.json"
            intent.write_text(
                json.dumps({
                    "diagram": "sample-bdd",
                    "kind": "DefinitionView",
                    "name": "Sample BDD",
                    "roots": [{"id": "root"}],
                }),
                encoding="utf-8",
            )

            with patch("sys.argv", ["sysmld", "bdd", str(intent)]), redirect_stdout(StringIO()):
                self.assertEqual(main(), 0)

            self.assertTrue((Path(tmp) / "sample-bdd.sysmld").exists())

    def test_view_commands_generate_sysmld(self):
        commands = [
            ("package", "PackageView", "package", "pkgA"),
            ("req", "RequirementView", "requirement", "reqA"),
            ("constraint", "ConstraintView", "constraint", "constraintA"),
            ("action", "ActionView", "action", "actionA"),
            ("usecase", "UseCaseView", "use_case", "useCaseA"),
            ("allocation", "AllocationView", "allocation", "allocationA"),
            ("flow", "FlowView", "flow_node", "flowA"),
            ("analysis", "AnalysisCaseView", "case", "analysisA"),
            ("verification", "VerificationCaseView", "case", "verificationA"),
            ("interface", "InterfaceView", "interface", "interfaceA"),
            ("general", "GeneralView", "part_usage", "nodeA"),
        ]
        with TemporaryDirectory() as tmp:
            for command, kind, symbol, node_id in commands:
                intent = Path(tmp) / f"{command}.json"
                intent.write_text(
                    json.dumps({
                        "diagram": command,
                        "kind": kind,
                        "mode": "sketch",
                        "nodes": {
                            node_id: {"label": node_id, "symbol": symbol},
                        },
                        "edges": [],
                    }),
                    encoding="utf-8",
                )

                with patch("sys.argv", ["sysmld", command, str(intent)]), redirect_stdout(StringIO()):
                    self.assertEqual(main(), 0)

                self.assertTrue(intent.with_suffix(".sysmld").exists())

    def test_interaction_command_generates_sysmld(self):
        with TemporaryDirectory() as tmp:
            intent = Path(tmp) / "interaction.json"
            intent.write_text(
                json.dumps({
                    "diagram": "interaction",
                    "mode": "sketch",
                    "lifelines": {
                        "a": {"label": "A"},
                        "b": {"label": "B"},
                    },
                    "messages": [
                        {"id": "m1", "from": "a", "to": "b", "label": "call"},
                    ],
                }),
                encoding="utf-8",
            )

            with patch("sys.argv", ["sysmld", "interaction", str(intent)]), redirect_stdout(StringIO()):
                self.assertEqual(main(), 0)

            self.assertTrue(intent.with_suffix(".sysmld").exists())

    def test_generic_view_sizes_boxes_for_multiline_labels(self):
        with TemporaryDirectory() as tmp:
            intent = Path(tmp) / "req.json"
            intent.write_text(
                json.dumps({
                    "diagram": "req",
                    "kind": "RequirementView",
                    "mode": "sketch",
                    "nodes": {
                        "r1": {"label": "REQ-1\nThis requirement text\nuses multiple lines"},
                    },
                    "edges": [],
                }),
                encoding="utf-8",
            )

            with patch("sys.argv", ["sysmld", "req", str(intent)]), redirect_stdout(StringIO()):
                self.assertEqual(main(), 0)

            data = json.loads(intent.with_suffix(".sysmld").read_text(encoding="utf-8"))
            element = data["diagram"]["elements"][0]
            self.assertGreaterEqual(element["layout"]["height"], 73)
            self.assertGreaterEqual(element["layout"]["width"], 177)


if __name__ == "__main__":
    unittest.main()
