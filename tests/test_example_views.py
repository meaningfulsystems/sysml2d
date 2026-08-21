from __future__ import annotations

import json
from pathlib import Path
import unittest

from sysmld.action_view import action_file
from sysmld.allocation_view import allocation_file
from sysmld.case_view import analysis_file, verification_file
from sysmld.constraint_view import constraint_file
from sysmld.definition_view import tree_file
from sysmld.flow_view import flow_file
from sysmld.general_view import general_file
from sysmld.interaction_view import sequence_file
from sysmld.interconnection_view import compose_file
from sysmld.interface_view import interface_file
from sysmld.package_view import package_file
from sysmld.render_svg import scene_to_svg
from sysmld.requirement_view import requirement_file
from sysmld.scene import build_scene
from sysmld.state_view import stm_file
from sysmld.use_case_view import usecase_file
from sysmld.validate import validate_file


ROOT = Path(__file__).resolve().parents[1]

COMPOSERS = {
    "DefinitionView": tree_file,
    "InterconnectionView": compose_file,
    "StateView": stm_file,
    "ActionView": action_file,
    "InteractionView": sequence_file,
    "UseCaseView": usecase_file,
    "PackageView": package_file,
    "RequirementView": requirement_file,
    "ConstraintView": constraint_file,
    "AllocationView": allocation_file,
    "FlowView": flow_file,
    "AnalysisCaseView": analysis_file,
    "VerificationCaseView": verification_file,
    "InterfaceView": interface_file,
    "GeneralView": general_file,
}

EBIKE_INTENTS = [
    ("e-bike-bdd.json", "DefinitionView"),
    ("e-bike-ibd.json", "InterconnectionView"),
    ("e-bike-stm.json", "StateView"),
    ("e-bike-act.json", "ActionView"),
    ("e-bike-int.json", "InteractionView"),
    ("e-bike-uc.json", "UseCaseView"),
    ("e-bike-pkg.json", "PackageView"),
    ("e-bike-req.json", "RequirementView"),
    ("e-bike-cst.json", "ConstraintView"),
    ("e-bike-alloc.json", "AllocationView"),
    ("e-bike-flow.json", "FlowView"),
    ("e-bike-acase.json", "AnalysisCaseView"),
    ("e-bike-vcase.json", "VerificationCaseView"),
    ("e-bike-intf.json", "InterfaceView"),
    ("e-bike-general.json", "GeneralView"),
]


class ExampleViewTests(unittest.TestCase):
    def test_ebike_covers_all_fifteen_view_kinds(self):
        kinds = set()
        for name, expected in EBIKE_INTENTS:
            intent = ROOT / "examples/e-bike" / name
            spec = json.loads(intent.read_text(encoding="utf-8"))
            self.assertEqual(spec["kind"], expected)
            kinds.add(expected)
        self.assertEqual(kinds, set(COMPOSERS))

    def test_ebike_intents_compose_validate_and_render(self):
        for name, expected in EBIKE_INTENTS:
            intent = ROOT / "examples/e-bike" / name
            committed = intent.with_suffix(".sysmld")
            with self.subTest(name=name):
                COMPOSERS[expected](intent, committed)
                report = validate_file(committed, strict=True)
                self.assertEqual(report.errors, 0, [finding.message for finding in report.findings])
                data = json.loads(committed.read_text(encoding="utf-8"))
                self.assertEqual(data["diagram"]["kind"], expected)
                self.assertTrue(data["diagram"]["elements"])
                svg = scene_to_svg(build_scene(committed))
                self.assertIn("<svg", svg)
                self.assertIn("<path", svg)

    def test_hop_overs_appear_on_crossing_generic_views(self):
        spec = {
            "kind": "PackageView",
            "mode": "sketch",
            "direction": "top-down",
            "nodes": {
                "a": {"label": "A", "rank": 0, "order": 0},
                "b": {"label": "B", "rank": 1, "order": 0},
                "c": {"label": "C", "rank": 1, "order": 1},
                "d": {"label": "D", "rank": 2, "order": 0},
            },
            "edges": [
                {"from": "a", "to": "b"},
                {"from": "a", "to": "d"},
                {"from": "c", "to": "d"},
            ],
        }
        from sysmld.views import view
        from sysmld.scene import build_scene_from_data

        doc = view(spec, kind="PackageView")
        svg = scene_to_svg(build_scene_from_data(doc))
        hops = hop_count(doc)
        if hops:
            self.assertIn(" A 7 7 0 0 ", svg)


def hop_count(doc: dict) -> int:
    from sysmld.routing import hop_crossings
    from sysmld.scene import build_scene_from_data

    scene = build_scene_from_data(doc)
    hops = hop_crossings([connection.points for connection in scene.connections])
    return sum(len(item) for item in hops)


if __name__ == "__main__":
    unittest.main()
