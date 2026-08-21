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
        sizes = {
            intent.stem: json.loads(intent.with_suffix(".sysmld").read_text(encoding="utf-8"))["diagram"]["canvas"]
            for intent in (
                APOLLO / "apollo-req.json",
                APOLLO / "apollo-stm.json",
                APOLLO / "apollo-bdd.json",
                APOLLO / "apollo-stm-abort.json",
                APOLLO / "apollo-bdd-lm.json",
                APOLLO / "apollo-ibd.json",
                APOLLO / "apollo-alloc.json",
            )
        }
        self.assertLess(sizes["apollo-req"]["width"], 2500)
        self.assertGreater(sizes["apollo-req"]["height"], 200)
        self.assertLess(sizes["apollo-req"]["height"], 900)
        req = json.loads((APOLLO / "apollo-req.json").read_text(encoding="utf-8"))
        self.assertEqual(list(req["nodes"]), ["safety", "land", "talk", "abort", "air", "guide"])
        joined = "\n".join(node["label"] for node in req["nodes"].values())
        land = req["nodes"]["land"]["label"]
        self.assertIn("The Lunar Module shall land", land)
        self.assertIn("two crew on the Moon", land)
        self.assertIn("P66", land)
        self.assertIn("Primary Guidance", land)
        self.assertNotIn("Splash", land)
        self.assertNotIn("195:18:35", joined)
        self.assertNotIn("Hornet", joined)
        air = req["nodes"]["air"]["label"]
        self.assertIn("The Lunar Module shall supply", air)
        self.assertIn("oxygen, water, and lithium", air)
        self.assertNotIn("teaching figure", air)
        self.assertNotIn("required pressure", air)
        self.assertNotIn("cite both", air)
        self.assertNotIn("2800 psi", air)
        self.assertNotIn("3000 psi", air)
        self.assertNotIn("2800 psi vs 3000 psi", joined)
        self.assertNotIn("spsRequirement", req["nodes"])
        self.assertNotIn("dpsRequirement", req["nodes"])
        self.assertNotIn("9,870", joined)
        self.assertNotIn("10,500", joined)
        self.assertNotIn("20,500", joined)
        self.assertNotIn("21,500", joined)
        self.assertNotIn("LMA790", joined)
        self.assertNotRegex(joined, r"(?i)required thrust")
        self.assertNotIn("75:54:28", joined)
        self.assertNotIn("lbf", joined)
        talk = req["nodes"]["talk"]["label"]
        self.assertIn("The stack shall communicate", talk)
        self.assertIn("Unified S-Band", talk)
        self.assertNotIn("stage-to-stage", talk)
        self.assertNotIn("crossfeed", talk)
        self.assertIn("The Range Safety Officer\nshall command UHF destruct", req["nodes"]["safety"]["label"])
        self.assertIn("The Abort Guidance System\nshall provide abort guidance", req["nodes"]["abort"]["label"])
        self.assertIn("landing radar during descent", req["nodes"]["guide"]["label"])
        self.assertIn("rendezvous radar during\nascent", req["nodes"]["guide"]["label"])
        for node in req["nodes"].values():
            self.assertIn("shall", node["label"])
        self.assertLess(sizes["apollo-stm"]["width"], 1600)
        self.assertGreater(sizes["apollo-stm"]["height"], 200)
        self.assertLess(sizes["apollo-stm"]["height"], 1000)
        lunar_canvas = json.loads((APOLLO / "apollo-stm-lunar.sysmld").read_text(encoding="utf-8"))["diagram"]["canvas"]
        and_canvas = json.loads((APOLLO / "apollo-stm-and.sysmld").read_text(encoding="utf-8"))["diagram"]["canvas"]
        self.assertLess(lunar_canvas["width"], 1600)
        self.assertLess(lunar_canvas["height"], 1000)
        self.assertLess(and_canvas["width"], 1800)
        self.assertLess(and_canvas["height"], 800)
        self.assertGreater(and_canvas["width"], and_canvas["height"])
        self.assertLess(sizes["apollo-bdd"]["width"], 2800)
        self.assertGreater(sizes["apollo-bdd"]["height"], 200)
        self.assertLess(sizes["apollo-bdd"]["height"], 800)
        self.assertLess(sizes["apollo-alloc"]["height"], 900)
        self.assertEqual(kinds, set(COMPOSERS))

    def test_apollo_ibds_do_not_cross_boxes(self):
        from sysmld.interconnection_view import compose
        for intent in sorted(APOLLO.glob("apollo-ibd*.json")):
            spec = json.loads(intent.read_text(encoding="utf-8"))
            doc = compose(spec)
            with self.subTest(name=intent.name):
                self.assertEqual(_route_box_hits(doc), [])

    def test_apollo_wrap_and_control_routes_do_not_cross_boxes(self):
        from sysmld.definition_view import compose_tree
        from sysmld.views import action
        from tests.test_action_view import _route_box_hits as action_hits

        for name in ("apollo-bdd.json", "apollo-bdd-lm.json", "apollo-bdd-csm.json"):
            spec = json.loads((APOLLO / name).read_text(encoding="utf-8"))
            doc = compose_tree(spec)
            canvas = doc["diagram"]["canvas"]
            with self.subTest(name=name):
                self.assertEqual(_definition_route_box_hits(doc), [])
                self.assertLess(canvas["width"], 2800)
                self.assertLess(canvas["height"], 2000)

        csm = compose_tree(json.loads((APOLLO / "apollo-bdd-csm.json").read_text(encoding="utf-8")))
        boxes = {element["id"]: element["layout"] for element in csm["diagram"]["elements"]}
        self.assertGreater(boxes["RCS"]["y"], boxes["DSKY"]["y"] + boxes["DSKY"]["height"])
        self.assertGreater(boxes["systemA"]["y"], boxes["RCS"]["y"] + boxes["RCS"]["height"] - 1)
        for grandchild in ("systemA", "systemB"):
            for other in ("probe", "ringLatches", "charger", "inverter1"):
                self.assertFalse(
                    _layouts_overlap(boxes[grandchild], boxes[other]),
                    f"{grandchild} overlaps {other}",
                )

        act = action(json.loads((APOLLO / "apollo-act.json").read_text(encoding="utf-8")))
        self.assertEqual(action_hits(act), [])
        act_boxes = {element["id"]: element["layout"] for element in act["diagram"]["elements"]}
        self.assertLess(act["diagram"]["canvas"]["width"], 1200)
        self.assertAlmostEqual(act_boxes["p66Landing"]["y"], act_boxes["p70Abort"]["y"], delta=1)
        self.assertLess(
            act_boxes["p66Landing"]["x"] + act_boxes["p66Landing"]["width"],
            act_boxes["p70Abort"]["x"],
        )

        bdd = compose_tree(json.loads((APOLLO / "apollo-bdd.json").read_text(encoding="utf-8")))
        bdd_boxes = {element["id"]: element["layout"] for element in bdd["diagram"]["elements"]}
        part_boxes = {
            element["id"]: element
            for element in bdd["diagram"]["elements"]
            if element.get("symbol") != "boundary"
        }
        self.assertGreaterEqual(len(part_boxes), 7)
        self.assertLessEqual(len(part_boxes), 10)
        self.assertNotIn("SIC", bdd_boxes)
        self.assertNotIn("PNGS", bdd_boxes)
        self.assertIn("SaturnV", bdd_boxes)
        self.assertIn("RSO", bdd_boxes)
        self.assertIn("recovery", bdd_boxes)
        self.assertEqual(_definition_route_box_hits(bdd), [])

        from sysmld.views import view
        uc = view(json.loads((APOLLO / "apollo-uc.json").read_text(encoding="utf-8")), kind="UseCaseView")
        uc_boxes = {element["id"]: element["layout"] for element in uc["diagram"]["elements"]}
        self.assertGreater(
            uc_boxes["MCC"]["x"],
            uc_boxes["flyMissionUseCase"]["x"] + uc_boxes["flyMissionUseCase"]["width"],
        )
        self.assertLess(
            uc_boxes["CDR"]["x"] + uc_boxes["CDR"]["width"],
            uc_boxes["flyMissionUseCase"]["x"],
        )

        from sysmld.state_view import compose_stm
        abort_doc = compose_stm(json.loads((APOLLO / "apollo-stm-abort.json").read_text(encoding="utf-8")))
        abort_tracks = {}
        for connection in abort_doc["diagram"]["connections"]:
            target = connection["target"]["element"]
            waypoints = connection["route"].get("waypoints") or []
            if len(waypoints) >= 2 and abs(waypoints[0]["y"] - waypoints[1]["y"]) < 0.6:
                abort_tracks[target] = waypoints[0]["y"]
        self.assertAlmostEqual(abort_tracks["pad"], abort_tracks["SPS"], delta=1)
        self.assertAlmostEqual(abort_tracks["I"], abort_tracks["lunar"], delta=1)
        self.assertAlmostEqual(abort_tracks["II"], abort_tracks["contingencyTLI"], delta=1)
        self.assertAlmostEqual(abort_tracks["III"], abort_tracks["IV"], delta=1)

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
        self.assertNotIn("initial", stm_spec["states"])
        self.assertTrue(stm_spec["states"]["earthCoast"].get("composite"))
        self.assertNotIn("lunarReturn", stm_spec["states"])
        self.assertNotIn("flight", stm_spec["states"])
        self.assertEqual(stm_spec["states"]["TLI"]["parent"], "earthCoast")
        self.assertEqual(stm_spec["states"]["dockEject"]["parent"], "earthCoast")
        earth_top = [
            sid
            for sid, state in stm_spec["states"].items()
            if not state.get("initial") and not state.get("parent")
        ]
        self.assertLessEqual(len(earth_top), 10)
        earth_children = [
            sid
            for sid, state in stm_spec["states"].items()
            if state.get("parent") == "earthCoast" and not state.get("initial")
        ]
        self.assertLessEqual(len(earth_children), 8)
        self.assertEqual(
            set(earth_children),
            {"countdown", "boost", "earthOrbit", "TLI", "dockEject", "translunar", "LOI"},
        )
        self.assertIn("state earthCoast {", text)
        self.assertIn("state lunarReturn {", text)
        self.assertIn("state def Flight", text)
        self.assertIn("state def RangeSafety", text)
        self.assertIn("state csmOrbit", text)
        self.assertIn("state afterUndock", text)
        self.assertIn("state followPNGS", text)
        and_spec = json.loads((APOLLO / "apollo-stm-and.json").read_text(encoding="utf-8"))
        self.assertTrue(and_spec["states"]["flight"].get("concurrent"))
        self.assertEqual(and_spec["states"]["abortMode"]["region"], "clockAbort")
        self.assertEqual(and_spec["states"]["csmOrbit"]["region"], "afterUndock")
        self.assertEqual(and_spec["states"]["rsSafed"]["region"], "rangeSafety")
        self.assertEqual(and_spec["states"]["agsFollow"]["region"], "guidance")
        and_leaves = [
            sid
            for sid, state in and_spec["states"].items()
            if not state.get("initial") and state.get("parent") == "flight"
        ]
        self.assertLessEqual(len(and_leaves), 10)
        hops = {(edge["from"], edge["to"]) for edge in stm_spec["transitions"]}
        earth = [
            "countdown",
            "boost",
            "earthOrbit",
            "TLI",
            "dockEject",
            "translunar",
            "LOI",
        ]
        self.assertEqual(
            [edge["to"] for edge in stm_spec["transitions"] if edge.get("from") in earth[:-1] and edge.get("to") in earth],
            earth[1:],
        )
        self.assertIn(("TLI", "dockEject"), hops)
        self.assertIn(("dockEject", "translunar"), hops)
        self.assertIn(("translunar", "LOI"), hops)
        self.assertNotIn(("TLI", "translunar"), hops)
        self.assertNotIn(("dockEject", "LOI"), hops)
        self.assertNotIn(("translunar", "dockEject"), hops)
        tli_label = stm_spec["states"]["TLI"]["label"]
        self.assertIn("PK 02:44:15", tli_label)
        self.assertIn("A11-FP 2:44:26", tli_label)
        self.assertIn("flown 02:44:16", tli_label)
        self.assertNotIn("02:44:16.2", tli_label)
        loi_label = stm_spec["states"]["LOI"]["label"]
        self.assertIn("75:54:28", loi_label)
        self.assertIn("~075:49:50", loi_label)
        self.assertNotIn("Press Kit", loi_label)
        lunar_spec = json.loads((APOLLO / "apollo-stm-lunar.json").read_text(encoding="utf-8"))
        self.assertNotIn("initial", lunar_spec["states"])
        self.assertTrue(lunar_spec["states"]["lunarInitial"].get("initial"))
        self.assertEqual(lunar_spec["states"]["lunarInitial"].get("parent"), "lunarReturn")
        self.assertTrue(lunar_spec["states"]["lunarReturn"].get("composite"))
        lunar_children = [
            sid
            for sid, state in lunar_spec["states"].items()
            if state.get("parent") == "lunarReturn" and not state.get("initial")
        ]
        self.assertLessEqual(len(lunar_children), 10)
        lunar_hops = {(edge["from"], edge["to"]) for edge in lunar_spec["transitions"]}
        lunar = [
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
            [edge["to"] for edge in lunar_spec["transitions"] if edge.get("from") in lunar[:-1] and edge.get("to") in lunar],
            lunar[1:],
        )
        self.assertIn(("undock", "DOI"), lunar_hops)
        context = json.loads((APOLLO / "apollo-context.json").read_text(encoding="utf-8"))
        context_labels = [node["label"] for node in context["nodes"].values()]
        self.assertIn("Crew", context_labels)
        self.assertIn("Mission Control", context_labels)
        self.assertIn("tracking net", context_labels)
        self.assertIn("Earth", context_labels)
        self.assertIn("Moon", context_labels)
        self.assertTrue(any("Range Safety Officer" in label for label in context_labels))
        joined_labels = "\n".join(context_labels)
        self.assertNotIn("MCC", joined_labels)
        self.assertNotIn("RSO", joined_labels)
        self.assertNotIn("MSFN", joined_labels)
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
        self.assertIn("A11-FP is the only planned source", text)
        self.assertIn("~075:49:50 GET", text)
        self.assertIn("Two LOI-1 numbers only", text)
        self.assertNotIn("A11 PK planned GET:", text)
        self.assertNotIn("flown 75:54:28", text)
        for sent in text.replace(";", ".").split("."):
            if "75:54:28" in sent:
                self.assertNotIn("Press Kit", sent)
                self.assertNotRegex(sent, r"\bPK\b")
        self.assertIn("LM remains in the SLA until dockEject", text)
        self.assertIn("SM 100 lbf per engine (A11 PK p.93)", text)
        self.assertIn("LM 100 lbf per engine (A11 PK p.106)", text)
        self.assertIn("Loaded SM/CM RCS propellant mass UNKNOWN", text)
        self.assertIn("Δv table still UNKNOWN", text)
        self.assertNotIn("per-engine lbf UNKNOWN in press kit", text)
        self.assertIn("The Range Safety Officer shall command UHF destruct from outside Mission Control until that command is safed after Earth orbit.", text)
        self.assertIn("The Lunar Module shall land two crew on the Moon under Primary Guidance program P66.", text)
        self.assertIn("The stack shall communicate with Mission Control on Unified S-Band.", text)
        self.assertIn("The Abort Guidance System shall provide abort guidance without landing the Lunar Module.", text)
        self.assertIn("The Lunar Module shall supply oxygen, water, and lithium hydroxide for life support.", text)
        self.assertIn("The Lunar Module Primary Guidance system shall use landing radar during descent and rendezvous radar during ascent.", text)
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
        self.assertIn("no required thrust", text)
        self.assertIn(
            "9,870 / 1,050–6,300 lbf (PK) vs 10,500 lbf 10:1 (TN D-7143) vs 9,870 / 1,050–6,800 lbf (LMA790)",
            text,
        )
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
        self.assertIn("flown 195:18:35 GET", text)
        self.assertIn("13 nmi from USS Hornet, not from the target", text)
        self.assertIn("~1.7 nmi", text)
        self.assertNotIn("13 nmi from target", text)
        self.assertNotIn("195:18:35 MET", text)
        self.assertNotIn("model does not mark planned or flown", text)
        self.assertIn("CDR 2:48", text)
        self.assertIn("LMP 2:40", text)
        self.assertIn("D-8093 Table I", text)
        self.assertIn("Not the Public Affairs Office (PAO) hatch-to-hatch 2:31:40", text)
        self.assertNotIn("EVA 2:31:40", text)
        self.assertNotIn("duration 2:31:40", text)
        for sent in text.replace(";", ".").split("."):
            if "2:31:40" in sent:
                self.assertRegex(sent, r"(?i)\bnot\b")
        self.assertIn("teaching figure 2800 psi", text)
        self.assertIn("3000 psi D-6724", text)
        self.assertIn("no required pressure", text)
        self.assertNotIn("2800 psi vs 3000 psi", text)
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
        self.assertNotIn("DoDAF", note)
        self.assertNotIn("ninth-grade", note)
        self.assertNotIn("ninth grade", note)
        self.assertNotIn("apollo-stm-and.svg", note)
        self.assertNotIn("concurrency page", note)
        self.assertNotIn("third small page", note)
        self.assertNotIn("lecture", note)
        self.assertNotIn("The class", note)
        self.assertIn("INCOSE shalls", note)
        self.assertIn("four concurrent regions", note)
        abort_spec = json.loads((APOLLO / "apollo-stm-abort.json").read_text(encoding="utf-8"))
        abort_labels = "\n".join(state.get("label", "") for state in abort_spec["states"].values())
        self.assertIn("Pad", abort_labels)
        self.assertIn("Mode I", abort_labels)
        self.assertIn("Mode II", abort_labels)
        self.assertIn("Mode III", abort_labels)
        self.assertIn("Mode IV", abort_labels)
        self.assertIn("Contingency Translunar", abort_labels)
        self.assertIn("Injection", abort_labels)
        self.assertIn("Lunar", abort_labels)
        self.assertIn("Service Propulsion", abort_labels)
        self.assertIn("Launch Escape System", abort_spec["states"]["pad"]["label"])
        self.assertIn("Launch Escape System", abort_spec["states"]["I"]["label"])
        self.assertIn("not Launch Escape System", abort_spec["states"]["II"]["label"])
        self.assertIn("not Launch Escape System", abort_spec["states"]["SPS"]["label"])
        alloc_spec = json.loads((APOLLO / "apollo-alloc.json").read_text(encoding="utf-8"))
        self.assertEqual(alloc_spec["nodes"]["IU"]["label"], "Instrument Unit")
        self.assertEqual(alloc_spec["nodes"]["RSO"]["label"], "Range Safety Officer")
        self.assertEqual(alloc_spec["nodes"]["AGC_CM"]["label"], "Command Module\nguidance computer")
        self.assertEqual(alloc_spec["nodes"]["AGC_LM"]["label"], "Lunar Module\nguidance computer")
        self.assertEqual(alloc_spec["nodes"]["AGS"]["label"], "Abort Guidance System")
        self.assertEqual(alloc_spec["nodes"]["SM"]["label"], "Service Module")
        self.assertEqual(alloc_spec["nodes"]["CM"]["label"], "Command Module")
        self.assertEqual(alloc_spec["nodes"]["descent"]["label"], "Descent stage")
        for node in alloc_spec["nodes"].values():
            self.assertNotEqual(node["label"], "IU")
            self.assertNotEqual(node["label"], "RSO")
            self.assertNotEqual(node["label"], "AGC_CM")
            self.assertNotEqual(node["label"], "AGC_LM")
            self.assertNotEqual(node["label"], "AGS")
            self.assertNotEqual(node["label"], "SM")
            self.assertNotEqual(node["label"], "CM")
        lunar_surface = json.loads((APOLLO / "apollo-stm-lunar.json").read_text(encoding="utf-8"))["states"]["surfaceEVA"]["label"]
        self.assertIn("Extravehicular Activity", lunar_surface)
        self.assertNotEqual(lunar_surface, "Surface EVA")
        right_offsets = {
            (edge["from"], edge["to"]): edge["target_offset"]
            for edge in alloc_spec["edges"]
            if edge["to"] in {"SM", "CM", "descent"}
        }
        self.assertNotEqual(right_offsets[("epsRequirement", "SM")], right_offsets[("rcsRequirement", "SM")])
        self.assertEqual(
            len({
                right_offsets[("epsRequirement", "CM")],
                right_offsets[("dockingRequirement", "CM")],
                right_offsets[("rcsRequirement", "CM")],
            }),
            3,
        )
        self.assertIn(("epsRequirement", "descent"), right_offsets)
        self.assertNotIn("├──", note)
        self.assertNotIn("\n*Saturn V SA-506", note)
        self.assertIn("Stakeholder", note)
        self.assertIn("The serialed hardware", note)
        self.assertIn("Who needs what", note)
        self.assertIn("no required thrust", note)
        self.assertIn("LMA790 (a Grumman Lunar Module document number)", note)
        self.assertIn("9,870 / 1,050–6,800 lbf (LMA790)", note)
        self.assertIn("teaching figure 2800 psi", note)
        self.assertIn("3000 psi D-6724 is the other text", note)
        self.assertIn("no required pressure", note)
        self.assertNotIn("2800 psi vs 3000 psi", note)
        self.assertIn("flown 195:18:35 GET", note)
        self.assertIn("13 nmi from USS *Hornet*, not from the target", note)
        self.assertIn("~1.7 nmi", note)
        self.assertNotIn("13 nmi from target", note)
        self.assertNotIn("195:18:35 MET", note)
        self.assertNotIn("model does not mark planned or flown", note)
        self.assertIn("D-8093 Table I", note)
        self.assertIn("Not the Public Affairs Office (PAO) hatch-to-hatch 2:31:40", note)
        self.assertNotIn("EVA 2:31:40", note)
        self.assertNotIn("duration 2:31:40", note)
        for sent in note.replace(";", ".").split("."):
            if "2:31:40" in sent:
                self.assertRegex(sent, r"(?i)\bnot\b")
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
        system = json.loads((APOLLO / "apollo-bdd.json").read_text(encoding="utf-8"))
        self.assertEqual(system["aliases"]["RSO"], "Apollo11::Apollo11::RSO")
        self.assertEqual(system["aliases"]["recovery"], "Apollo11::Apollo11::recovery")
        self.assertEqual(system["aliases"]["Hornet"], "Apollo11::RecoveryForces::Hornet")
        top_ids = {child["id"] for child in system["roots"][0]["children"]}
        self.assertIn("RSO", top_ids)
        self.assertIn("recovery", top_ids)
        recovery_node = next(child for child in system["roots"][0]["children"] if child["id"] == "recovery")
        self.assertFalse(recovery_node.get("children"))
        labels = {child["id"]: child["label"] for child in system["roots"][0]["children"]}
        self.assertEqual(labels["SaturnV"], "Saturn V")
        self.assertEqual(labels["CSM"], "Command/Service Module")
        self.assertEqual(labels["LM"], "Lunar Module")
        self.assertEqual(labels["RSO"], "Range Safety Officer")
        self.assertEqual(labels["recovery"], "Recovery")
        self.assertGreaterEqual(len(system["roots"][0]["children"]), 6)
        self.assertLessEqual(len(system["roots"][0]["children"]), 8)
        bdd = json.loads((APOLLO / "apollo-bdd-lm.json").read_text(encoding="utf-8"))
        descent_node = bdd["roots"][0]["children"][0]
        ascent_node = bdd["roots"][0]["children"][1]
        self.assertEqual(descent_node["id"], "descent")
        self.assertEqual(ascent_node["id"], "ascent")
        self.assertIn("landingRadar", {child["id"] for child in descent_node["children"]})
        self.assertNotIn("landingRadar", {child["id"] for child in ascent_node["children"]})
        self.assertIn("rendezvousRadar", {child["id"] for child in ascent_node["children"]})
        def _tree_ids(node: dict) -> list[str]:
            ids = [node["id"]]
            for child in node.get("children") or []:
                ids.extend(_tree_ids(child))
            return ids
        lm_ids = _tree_ids(bdd["roots"][0])
        self.assertLessEqual(len(lm_ids), 8)
        self.assertEqual({child["id"] for child in bdd["roots"][0]["children"]}, {"descent", "ascent"})
        self.assertTrue(descent_node.get("children"))
        self.assertTrue(ascent_node.get("children"))
        self.assertNotIn("PNGS", {child["id"] for child in bdd["roots"][0]["children"]})
        self.assertNotIn("AgZn1", lm_ids)
        self.assertNotIn("AEA", lm_ids)
        self.assertNotIn("drogue", lm_ids)


def _definition_route_box_hits(doc: dict) -> list[tuple[str, str]]:
    elements = {element["id"]: element for element in doc["diagram"]["elements"]}
    boxes = {element_id: element["layout"] for element_id, element in elements.items()}
    hits: list[tuple[str, str]] = []
    for connection in doc["diagram"]["connections"]:
        source = connection["source"]
        target = connection["target"]
        points = [
            _element_anchor(elements[source["element"]], source["anchor"]),
            *[(point["x"], point["y"]) for point in connection["route"].get("waypoints", [])],
            _element_anchor(elements[target["element"]], target["anchor"]),
        ]
        for start, end in zip(points, points[1:]):
            for box_id, box in boxes.items():
                if _segment_crosses_interior(start, end, box):
                    hits.append((connection["id"], box_id))
    return hits


def _definition_connection_points(doc: dict, connection: dict) -> list[tuple[float, float]]:
    elements = {element["id"]: element for element in doc["diagram"]["elements"]}
    source = connection["source"]
    target = connection["target"]
    return [
        _element_anchor(elements[source["element"]], source["anchor"]),
        *[(point["x"], point["y"]) for point in connection["route"].get("waypoints", [])],
        _element_anchor(elements[target["element"]], target["anchor"]),
    ]


def _definition_vertical_at(doc: dict, connection: dict, x: float, tol: float = 8) -> bool:
    points = _definition_connection_points(doc, connection)
    for start, end in zip(points, points[1:]):
        if abs(start[0] - end[0]) < 0.6 and abs(start[0] - x) <= tol and abs(start[1] - end[1]) > 8:
            return True
    return False


def _column_centerline_spine(doc: dict, blocker_id: str, stacked_ids: tuple[str, ...]) -> bool:
    elements = {element["id"]: element for element in doc["diagram"]["elements"]}
    blocker = elements[blocker_id]["layout"]
    cx = blocker["x"] + blocker["width"] / 2
    stacked_top = min(elements[node_id]["layout"]["y"] for node_id in stacked_ids)
    col_bottom = max(
        elements[node_id]["layout"]["y"] + elements[node_id]["layout"]["height"]
        for node_id in (blocker_id, *stacked_ids)
    )
    for connection in doc["diagram"]["connections"]:
        ends = {connection["source"]["element"], connection["target"]["element"]}
        if not ends & {blocker_id, *stacked_ids}:
            continue
        points = _definition_connection_points(doc, connection)
        for start, end in zip(points, points[1:]):
            if abs(start[0] - end[0]) >= 0.6 or abs(start[0] - cx) > 8:
                continue
            lo, hi = sorted((start[1], end[1]))
            if connection["target"]["element"] == blocker_id and hi <= blocker["y"] + 1:
                continue
            if hi > stacked_top - 1 or lo >= blocker["y"] + blocker["height"] - 1:
                if lo < col_bottom:
                    return True
    return False


def _element_anchor(element: dict, anchor: dict) -> tuple[float, float]:
    layout = element["layout"]
    side = anchor["side"]
    offset = anchor.get("offset", 0.5)
    if side == "left":
        return (layout["x"], layout["y"] + layout["height"] * offset)
    if side == "right":
        return (layout["x"] + layout["width"], layout["y"] + layout["height"] * offset)
    if side == "top":
        return (layout["x"] + layout["width"] * offset, layout["y"])
    return (layout["x"] + layout["width"] * offset, layout["y"] + layout["height"])


def _layouts_overlap(first: dict, second: dict) -> bool:
    return (
        first["x"] < second["x"] + second["width"] - 1
        and second["x"] < first["x"] + first["width"] - 1
        and first["y"] < second["y"] + second["height"] - 1
        and second["y"] < first["y"] + first["height"] - 1
    )


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
