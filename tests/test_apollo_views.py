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
APOLLO = ROOT / "examples/apollo"

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


class ApolloViewTests(unittest.TestCase):
    def test_apollo_intents_compose_validate_and_render(self):
        intents = sorted(APOLLO.glob("apollo-*.json"))
        self.assertGreaterEqual(len(intents), 15)
        kinds = set()
        for intent in intents:
            spec = json.loads(intent.read_text(encoding="utf-8"))
            kind = spec["kind"]
            kinds.add(kind)
            with self.subTest(name=intent.name):
                committed = intent.with_suffix(".sysmld")
                COMPOSERS[kind](intent, committed)
                report = validate_file(committed, strict=True)
                self.assertEqual(report.errors, 0, [f.message for f in report.findings])
                svg = scene_to_svg(build_scene(committed))
                self.assertIn("<svg", svg)
        self.assertEqual(kinds, set(COMPOSERS))

    def test_apollo_ibds_do_not_cross_boxes(self):
        from sysmld.interconnection_view import compose
        for intent in sorted(APOLLO.glob("apollo-ibd*.json")):
            spec = json.loads(intent.read_text(encoding="utf-8"))
            doc = compose(spec)
            with self.subTest(name=intent.name):
                self.assertEqual(_route_box_hits(doc), [])

    def test_apollo_does_not_collapse_agcs(self):
        text = (APOLLO / "apollo.sysml").read_text(encoding="utf-8")
        self.assertIn("part cmc : CMC", text)
        self.assertIn("part lgc : LGC", text)
        self.assertIn("part ags : AGS", text)
        self.assertIn("part lvdc : LVDC", text)
        self.assertIn("part ems : EMS", text)
        self.assertIn("part cmDsky1 : DSKY", text)
        self.assertIn("part cmDsky2 : DSKY", text)
        self.assertIn("part lmDsky : DSKY", text)

    def test_apollo_keeps_inner_machines_and_a11_flags(self):
        text = (APOLLO / "apollo.sysml").read_text(encoding="utf-8")
        self.assertIn("part scs : SCS", text)
        self.assertIn("part pngs : PNGS", text)
        self.assertIn("state def ScsMode", text)
        self.assertIn("state def AgsMode", text)
        self.assertIn("state def LgcMajorMode", text)
        self.assertIn("state def CmcMajorMode", text)
        self.assertIn("requirement a11AtypicalRequirement", text)
        self.assertIn("requirement scsRequirement", text)
        self.assertIn("requirement pngsRequirement", text)
        self.assertNotIn("part pngs : AGS", text)
        self.assertNotIn("part scs : CMC", text)
        self.assertIn("part def SaturnV", text)
        self.assertIn("part def CSM", text)
        self.assertIn("part def LM", text)
        self.assertIn("part cmRcs : CMRCS", text)
        self.assertIn("part smRcsA : SMRCSQuad", text)
        self.assertIn("part lmRcs : LMRCS", text)
        self.assertIn("part oxygenLoop : OxygenLoop", text)
        self.assertIn("part erasable : ErasableMemory", text)
        self.assertIn("state def EclssMode", text)


def _route_box_hits(doc: dict) -> list[tuple[str, str]]:
    elements = {element["id"]: element for element in doc["diagram"]["elements"]}
    boxes = {
        element["id"]: element["layout"]
        for element in elements.values()
        if element["symbol"] == "part_usage"
    }
    hits: list[tuple[str, str]] = []
    for connection in doc["diagram"]["connections"]:
        source_owner = elements[connection["source"]["element"]].get("owner")
        target_owner = elements[connection["target"]["element"]].get("owner")
        points = [
            _port_point(elements, connection["source"]["element"]),
            *[(point["x"], point["y"]) for point in connection["route"].get("waypoints", [])],
            _port_point(elements, connection["target"]["element"]),
        ]
        for start, end in zip(points, points[1:]):
            for box_id, box in boxes.items():
                if box_id in (source_owner, target_owner):
                    continue
                if _segment_crosses_interior(start, end, box):
                    hits.append((connection["id"], box_id))
    return hits


def _port_point(elements: dict, port_id: str) -> tuple[float, float]:
    port = elements[port_id]
    owner = elements[port["owner"]]
    layout = owner["layout"]
    side = port["placement"]["side"]
    offset = port["placement"]["offset"]
    if side == "left":
        return (layout["x"], layout["y"] + layout["height"] * offset)
    if side == "right":
        return (layout["x"] + layout["width"], layout["y"] + layout["height"] * offset)
    if side == "top":
        return (layout["x"] + layout["width"] * offset, layout["y"])
    return (layout["x"] + layout["width"] * offset, layout["y"] + layout["height"])


def _segment_crosses_interior(start: tuple[float, float], end: tuple[float, float], box: dict) -> bool:
    x1, y1 = start
    x2, y2 = end
    left = box["x"]
    right = box["x"] + box["width"]
    top = box["y"]
    bottom = box["y"] + box["height"]
    if round(x1) == round(x2):
        if x1 <= left or x1 >= right:
            return False
        lo, hi = sorted((y1, y2))
        return lo < bottom and hi > top
    if round(y1) == round(y2):
        if y1 <= top or y1 >= bottom:
            return False
        lo, hi = sorted((x1, x2))
        return lo < right and hi > left
    return False


if __name__ == "__main__":
    unittest.main()
