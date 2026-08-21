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

LOCKED = (
    "package SaturnV",
    "package CSM",
    "package LM",
    "package Crew",
    "package Ground",
    "part SIC : SIC",
    "part SII : SII",
    "part SIVB : SIVB",
    "part IU : IU",
    "part LVDC : LVDC",
    "part ST124 : ST124",
    "part FCC : FCC",
    "part SLA : SLA",
    "part LES : LES",
    "part CM : CM",
    "part SM : SM",
    "part SCS : SCS",
    "part AGC_CM : AGC_CM",
    "part AGC_LM : AGC_LM",
    "part IMU : IMU",
    "part DSKY : DSKY",
    "part SPS : SPS",
    "part RCS : RCS",
    "part ECLSS : ECLSS",
    "part descent : descent",
    "part ascent : ascent",
    "part PNGS : PNGS",
    "part AGS : AGS",
    "part DPS : DPS",
    "part APS : APS",
    "part landingRadar : landingRadar",
    "part rendezvousRadar : rendezvousRadar",
    "part CDR : CDR",
    "part CMP : CMP",
    "part LMP : LMP",
    "part A7L : A7L",
    "part PLSS : PLSS",
    "part KSC_LCC : KSC_LCC",
    "part MCC : MCC",
    "part MOCR2 : MOCR",
    "part Hornet : Hornet",
    "part RTCC : RTCC",
    "part Goldstone : Goldstone",
    "part Madrid : Madrid",
    "part Honeysuckle : Honeysuckle",
    "part NASCOM : NASCOM",
    "state TLI",
    "state LOI",
    "state DOI",
    "state TEI",
    "state dockEject",
    "state surfaceEVA",
    "state pad",
    "state contingencyTLI",
    "state lunar",
    "part AEA : AEA",
    "part ASA : ASA",
    "part DEDA : DEDA",
    "part FC1 : FC",
    "part charger : charger",
    "part ECA : ECA",
    "part probe : probe",
    "part drogue : drogue",
    "part ringLatches : ringLatches",
    "part quadA : quad",
    "part systemA : RCSSystem",
    "state soft",
    "state hard",
    "state hardwareOff",
    "part Comanche055 : Rope",
    "part Luminary1A : Rope",
    "state def CMC_Entry",
    "state def LGC_Landing",
    "state execOverflow",
)


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

    def test_apollo_locked_msml_names(self):
        text = (APOLLO / "apollo.sysml").read_text(encoding="utf-8")
        for token in LOCKED:
            with self.subTest(token=token):
                self.assertIn(token, text)
        self.assertIn("part USB : USB", text)
        self.assertNotIn("part cmc : CMC", text)
        self.assertNotIn("part lgc : LGC", text)
        self.assertNotIn("part vanguard", text)
        stm_spec = json.loads((APOLLO / "apollo-stm.json").read_text(encoding="utf-8"))
        self.assertIn("dockEject", stm_spec["states"])
        self.assertEqual(stm_spec["states"]["dockEject"]["label"], "dock/eject")
        hops = {(edge["from"], edge["to"]) for edge in stm_spec["transitions"]}
        mission = [
            "countdown",
            "boost",
            "earthOrbit",
            "TLI",
            "dockEject",
            "translunar",
            "LOI",
            "undock",
            "DOI",
            "descent",
            "surfaceEVA",
            "ascent",
            "rendezvous",
            "TEI",
            "entry",
            "recovery",
        ]
        self.assertEqual(
            [edge["to"] for edge in stm_spec["transitions"] if edge.get("from") in mission[:-1] and edge.get("to") in mission],
            mission[1:],
        )
        self.assertIn(("TLI", "dockEject"), hops)
        self.assertIn(("dockEject", "translunar"), hops)
        self.assertIn(("translunar", "LOI"), hops)
        self.assertNotIn(("TLI", "translunar"), hops)
        self.assertNotIn(("dockEject", "LOI"), hops)
        self.assertNotIn(("translunar", "dockEject"), hops)
        tli_i = text.find("state TLI")
        dock_i = text.find("state dockEject")
        coast_i = text.find("state translunar")
        loi_i = text.find("state LOI")
        self.assertTrue(tli_i < dock_i < coast_i < loi_i)
        self.assertIn("CMP-owned", text)
        self.assertIn("02:44:15 GET", text)
        self.assertIn("2:44:26 GET", text)
        self.assertIn("02:44:16 GET (MSC-00171)", text)
        self.assertNotIn("02:44:16.2", text)
        self.assertIn("75:54:28 GET", text)
        self.assertIn("A11-FP is the control source", text)
        self.assertIn("Apollo 11 Flight Plan", text)
        self.assertIn("~075:49:50 GET", text)
        self.assertIn("Press Kit may print the same string", text)
        self.assertIn("Two LOI-1 numbers only", text)
        self.assertNotIn("A11 PK planned GET:", text)
        self.assertNotIn("flown 75:54:28", text)
        self.assertIn("LM remains in the SLA until dockEject", text)
        self.assertIn("SM 100 lbf per engine (A11 PK p.93)", text)
        self.assertIn("LM 100 lbf per engine (A11 PK p.106)", text)
        self.assertIn("Loaded SM/CM RCS propellant mass UNKNOWN", text)
        self.assertIn("Δv table still UNKNOWN", text)
        self.assertNotIn("per-engine lbf UNKNOWN in press kit", text)
        self.assertIn("Not a landing computer", text)
        self.assertIn("4096 × 18-bit", text)
        self.assertIn("two × six 93 lbf", text)
        self.assertIn("117 V 400 Hz", text)
        self.assertIn("5,022,674 fueled", text)
        self.assertIn("1,059,171", text)
        self.assertIn("260,523", text)
        self.assertIn("4,306 lb", text)
        self.assertIn("12,250", text)
        self.assertIn("51,243", text)
        self.assertIn("7,653,854 lbf", text)
        self.assertIn("SPS loaded mass UNKNOWN", text)
        self.assertIn("CSM lunar Δv UNKNOWN", text)
        self.assertNotIn("Stage tank loads and Δv table UNKNOWN", text)
        self.assertNotIn("A11 rope IDs UNKNOWN", text)
        self.assertIn("Comanche 055", text)
        self.assertIn("Luminary 1A LMY99/1", text)
        self.assertIn("A11 AGS flight-program name UNKNOWN", text)
        self.assertIn("AGS ≠ DSKY", text)
        self.assertIn("AGS display is DEDA", text)
        self.assertIn("D-7720 April 1967 plan baseline", text)
        self.assertIn("IU physically is LVDC + ST-124 + Flight Control Computer (FCC)", text)
        self.assertIn("Eight panels: four jettison, four stay", text)
        self.assertNotIn("Four petals", text)
        self.assertIn("2800 kcal/man/day CM", text)
        self.assertIn("3200 kcal/man/day LM", text)
        self.assertIn("A11 actual intake UNKNOWN", text)
        self.assertNotIn("2200±300", text)
        self.assertNotIn("NAS 9-8927", text)
        self.assertIn("CMC P61–P67 = ENTRY", text)
        self.assertIn("LGC P63–P68 = LANDING", text)
        self.assertIn("1201/1202 is exec overflow, not an abort", text)
        self.assertIn("CM 5.85 cm/s/pulse", text)
        self.assertIn("82.03125", text)
        self.assertIn("No digital AGC↔LVDC", text)
        self.assertIn("20,500 lbf (PK) vs 21,500 lbf (TN D-7375)", text)
        self.assertIn("9,870 / 1,050–6,300 lbf (PK) vs 10,500 lbf 10:1 (TN D-7143)", text)
        self.assertIn("A11 MCC is MOCR 2", text)
        self.assertIn("Mission Rule 1-21", text)
        self.assertIn("296.8", text)
        self.assertIn("259.7", text)
        self.assertIn("243.0", text)
        self.assertIn("S-IC-6", text)
        self.assertIn("S-II-6", text)
        self.assertIn("S-IVB-6N", text)
        self.assertIn("IU-6", text)
        self.assertIn("SLA-14", text)
        self.assertIn("No stage-to-stage electrical power", text)
        self.assertIn("No CSM–LM propellant crossfeed", text)
        self.assertIn("A11 SM cryo is 2+2", text)
        self.assertIn("1.5° cant", text)
        self.assertIn("195:18:35", text)
        self.assertIn("13 nmi", text)
        self.assertIn("CDR 2:48", text)
        self.assertIn("LMP 2:40", text)
        self.assertIn("2800 psi vs 3000 psi", text)
        self.assertIn("part Comanche055 : Rope", text)
        self.assertIn("part Luminary1A : Rope", text)
        descent = _sysml_block(text, "part def descent")
        ascent = _sysml_block(text, "part def ascent")
        pngs = _sysml_block(text, "part def PNGS")
        lm = _sysml_block(text, "part def LM")
        self.assertIn("part landingRadar : landingRadar", descent)
        self.assertNotIn("part landingRadar : landingRadar", ascent)
        self.assertNotIn("part landingRadar : landingRadar", pngs)
        self.assertIn("part rendezvousRadar : rendezvousRadar", ascent)
        self.assertNotIn("part rendezvousRadar : rendezvousRadar", pngs)
        self.assertIn("PNGSToRendezvousRadar connect PNGS to rendezvousRadar", ascent)
        self.assertIn("connect ascent.PNGS to descent.landingRadar", lm)
        self.assertNotIn("IMUToLandingRadar", text)
        self.assertNotIn("IMUToRendezvousRadar", text)
        self.assertNotIn("PNGSToLandingRadar connect PNGS to landingRadar", text)
        note = (APOLLO / "apollo-architecture-summary.md").read_text(encoding="utf-8")
        self.assertIn("descent → DPS, AgZn1–4, ECA, landingRadar", note)
        self.assertIn("PNGS → IMU", note)
        self.assertNotIn("PNGS → IMU, rendezvousRadar", note)
        self.assertNotIn("PNGS → IMU, landingRadar, rendezvousRadar", note)
        self.assertIn("IU → LVDC, ST-124, FCC", note)
        self.assertIn("8 panels (4 jettison / 4 stay)", note)
        self.assertNotIn("four petals", note)
        self.assertIn("Stakeholder", note)
        self.assertIn("The serialed hardware", note)
        self.assertIn("Who needs what", note)
        self.assertNotIn("| Physical-subsystem |", note)
        iu = _sysml_block(text, "part def IU")
        sla = _sysml_block(text, "part def SLA")
        self.assertIn("part ST124 : ST124", iu)
        self.assertIn("part FCC : FCC", iu)
        self.assertIn("part LVDC : LVDC", iu)
        self.assertIn("Eight panels: four jettison, four stay", sla)
        ibd = json.loads((APOLLO / "apollo-ibd-lm.json").read_text(encoding="utf-8"))
        self.assertEqual(ibd["aliases"]["landingRadar"], "Apollo11::LM::descent::landingRadar")
        self.assertEqual(ibd["aliases"]["rendezvousRadar"], "Apollo11::LM::ascent::rendezvousRadar")
        self.assertEqual(ibd["aliases"]["PNGS--rendezvousRadar--tgt"], "Apollo11::LM::ascent::rendezvousRadar")
        self.assertEqual(ibd["aliases"]["conn-PNGS-rendezvousRadar"], "Apollo11::LM::ascent::PNGSToRendezvousRadar")
        self.assertEqual(ibd["aliases"]["PNGS--landingRadar--tgt"], "Apollo11::LM::descent::landingRadar")
        bdd = json.loads((APOLLO / "apollo-bdd-lm.json").read_text(encoding="utf-8"))
        descent_node = bdd["roots"][0]["children"][0]
        ascent_node = bdd["roots"][0]["children"][1]
        self.assertEqual(descent_node["id"], "descent")
        self.assertEqual(ascent_node["id"], "ascent")
        self.assertIn("landingRadar", {child["id"] for child in descent_node["children"]})
        self.assertNotIn("landingRadar", {child["id"] for child in ascent_node["children"]})
        self.assertIn("rendezvousRadar", {child["id"] for child in ascent_node["children"]})


def _sysml_block(text: str, header: str) -> str:
    start = text.find(header)
    if start < 0:
        raise AssertionError(f"missing {header}")
    brace = text.find("{", start)
    if brace < 0:
        raise AssertionError(f"missing body for {header}")
    depth = 0
    for index, char in enumerate(text[brace:], start=brace):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[brace : index + 1]
    raise AssertionError(f"unclosed {header}")


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
