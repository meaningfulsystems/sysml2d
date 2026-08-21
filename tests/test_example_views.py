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

    def test_ebike_review_bindings_locked_with_msml(self):
        model = (ROOT / "examples/e-bike/e-bike.sysml").read_text(encoding="utf-8")
        self.assertIn("part bms : BMS", model)
        self.assertIn("part def BatteryPack", model)
        self.assertIn("allocation allocateChargeToBms", model)
        self.assertNotIn("lockBikeUseCase", model)
        self.assertIn("accept cadencePedal", model)
        self.assertNotIn("accept throttle", model.lower())
        self.assertIn("Tour-mode scenario only", model)
        self.assertIn("usableWh 500 Wh / energyPerKm ~8.3 Wh/km", model)
        self.assertIn("Not Eco / PAS-1", model)
        self.assertIn("within 50 ms", model)
        self.assertIn("en15194DistanceRequirement", model)
        self.assertIn("EN 15194:2017 clause 4.2.13", model)
        self.assertIn("Power management", model)
        self.assertIn("not vehicle brake distance", model)
        self.assertIn("within 2 m after pedaling stops", model)
        self.assertIn("relax the cut-off from 2 m to 5 m", model)
        self.assertIn("no certified throttle", model)
        self.assertIn("25 km/h", model)
        self.assertIn("Rear geared hub. No regenerative braking.", model)
        self.assertIn("EU continuous rating 250 W", model)
        self.assertIn("Hub peak torque 40 N·m", model)
        self.assertIn("not continuous", model)
        self.assertIn("does not sit with 250 W at 25 km/h", model)
        self.assertIn("regen none", model)
        self.assertIn("attribute continuousPower", model)
        self.assertIn("attribute wheelTorque", model)
        self.assertNotIn("peakPower 250 W", model)
        self.assertIn("connection chargerToBms", model)
        self.assertNotIn("chargerToBattery", model)
        self.assertNotIn("connect batteryPack.bms.chargerIn to batteryPack.powerOut", model)
        self.assertIn("Cadence PAS, walk assist, and display. No throttle.", model)
        self.assertIn("state walk", model)
        self.assertNotIn("state walkAssist", model)
        self.assertIn("attribute energyPerKm", model)
        self.assertIn("attribute usableWh", model)
        self.assertIn("accept walkButton", model)
        self.assertIn("6 km/h", model)
        self.assertIn("Walk assist is not a throttle", model)
        self.assertIn("Do not add rider watts to pack energy", model)
        self.assertNotIn("port riderCommandIn", model)
        self.assertNotIn("port frameBatteryMountOut", model)
        self.assertIn("port batteryMountOut", model)
        self.assertIn("port chargerIn", model)
        self.assertIn("part cadenceSensor : CadenceSensor", model)
        self.assertIn("part wheelSpeedSensor : WheelSpeedSensor", model)
        self.assertIn("allocateSafetyToWheelSpeed", model)
        self.assertIn("allocateAssistToWheelSpeed", model)
        self.assertIn("cadence-only cannot enforce 25 km/h", model)
        self.assertIn("250 W", model)
        self.assertIn("StVZO / ISO 6742", model)
        self.assertNotIn("UN ECE R113.", model.replace("Not UN ECE R113.", ""))
        self.assertIn("allocateSafetyToBrakes", model)
        self.assertIn("allocateSafetyToController", model)
        self.assertIn("allocateSafetyToSensors", model)
        self.assertIn("allocateSafetyToBms", model)
        self.assertIn("allocateDistanceToController", model)
        self.assertIn("allocateDistanceToCadence", model)
        self.assertIn("allocateDistanceToWheelSpeed", model)
        self.assertIn("motor-assist cut-off after pedaling stops", model)
        self.assertNotIn("tighter than the EN 15194 distance test", model)
        for name in (
            "frame",
            "batteryPack",
            "motorController",
            "hubMotor",
            "humanInterface",
            "brakeSystem",
            "cadenceSensor",
        ):
            self.assertIn(f"part {name} :", model)

        intf = json.loads((ROOT / "examples/e-bike/e-bike-intf.json").read_text(encoding="utf-8"))
        self.assertNotIn("ThrottleCommand", intf["nodes"])
        self.assertFalse(any(edge.get("to") == "ThrottleCommand" for edge in intf["edges"]))

        alloc = json.loads((ROOT / "examples/e-bike/e-bike-alloc.json").read_text(encoding="utf-8"))
        safety_targets = {
            edge["to"]
            for edge in alloc["edges"]
            if edge.get("from") == "rideSafetyRequirement"
        }
        self.assertEqual(
            safety_targets,
            {"brakeSystem", "motorController", "cadenceSensor", "wheelSpeedSensor", "bms"},
        )
        assist_targets = {
            edge["to"]
            for edge in alloc["edges"]
            if edge.get("from") == "assistLimitRequirement"
        }
        self.assertIn("wheelSpeedSensor", assist_targets)
        self.assertIn("motorController", assist_targets)
        distance_targets = {
            edge["to"]
            for edge in alloc["edges"]
            if edge.get("from") == "en15194DistanceRequirement"
        }
        self.assertEqual(
            distance_targets,
            {"motorController", "cadenceSensor", "wheelSpeedSensor"},
        )
        self.assertNotIn("brakeSystem", distance_targets)
        charge_edges = [edge for edge in alloc["edges"] if edge.get("model_ref") == "allocateChargeToBms"]
        self.assertEqual(len(charge_edges), 1)
        self.assertEqual(charge_edges[0]["to"], "bms")

        cst = json.loads((ROOT / "examples/e-bike/e-bike-cst.json").read_text(encoding="utf-8"))
        self.assertFalse(
            any(edge.get("from") == "riderPower" and edge.get("to") == "energyBalance" for edge in cst["edges"])
        )
        self.assertTrue(
            any(edge.get("from") == "packEnergy" and edge.get("to") == "energyBalance" for edge in cst["edges"])
        )
        self.assertTrue(
            any(edge.get("from") == "riderPower" and edge.get("to") == "riderInputBalance" for edge in cst["edges"])
        )
        self.assertTrue(
            any(edge.get("from") == "usableWh" and edge.get("to") == "tourRangeBind" for edge in cst["edges"])
        )
        self.assertTrue(
            any(edge.get("from") == "energyPerKm" and edge.get("to") == "tourRangeBind" for edge in cst["edges"])
        )
        self.assertTrue(
            any(edge.get("from") == "energyBalance" and edge.get("to") == "usableWh" for edge in cst["edges"])
        )

        ibd = json.loads((ROOT / "examples/e-bike/e-bike-ibd.json").read_text(encoding="utf-8"))
        self.assertEqual(ibd["aliases"]["frame--batteryPack--src"], "ElectricBike::Frame::batteryMountOut")
        self.assertEqual(ibd["aliases"]["bms--bnd--tgt"], "ElectricBike::BMS::chargerIn")
        self.assertEqual(ibd["aliases"]["conn-bnd-bms"], "ElectricBike::ElectricBike::chargerToBms")
        self.assertEqual(ibd["aliases"]["conn-bms-batteryPack"], "ElectricBike::BatteryPack::bmsToPackPower")
        flow = json.loads((ROOT / "examples/e-bike/e-bike-flow.json").read_text(encoding="utf-8"))
        charge_from = {edge["to"] for edge in flow["edges"] if edge.get("from") == "charger"}
        self.assertEqual(charge_from, {"bms"})
        self.assertTrue(any(edge.get("from") == "bms" and edge.get("to") == "batteryPack" for edge in flow["edges"]))
        self.assertFalse(any(edge.get("from") == "charger" and edge.get("to") == "batteryPack" for edge in flow["edges"]))
        self.assertIn("bms", ibd["nodes"])
        self.assertIn("cadenceSensor", ibd["nodes"])
        self.assertIn("wheelSpeedSensor", ibd["nodes"])
        self.assertNotIn("ElectricBike::ElectricBike::frameBatteryMountOut", ibd["aliases"].values())
        parent_body = model[model.index("part def ElectricBike {") : model.index("part def Frame")]
        self.assertNotIn("port ", parent_body)
        for key, value in ibd["aliases"].items():
            if "--src" in key or "--tgt" in key or key.startswith("bnd--"):
                self.assertNotIn("ElectricBike::ElectricBike::", value)

        uc = json.loads((ROOT / "examples/e-bike/e-bike-uc.json").read_text(encoding="utf-8"))
        charger_tos = {edge["to"] for edge in uc["edges"] if edge.get("from") == "charger"}
        rider_tos = {edge["to"] for edge in uc["edges"] if edge.get("from") == "rider"}
        self.assertEqual(charger_tos, {"chargeBikeUseCase"})
        self.assertEqual(rider_tos, {"rideBikeUseCase", "adjustAssistUseCase"})
        self.assertTrue(
            any(
                edge.get("from") == "rideBikeUseCase" and edge.get("to") == "adjustAssistUseCase"
                for edge in uc["edges"]
            )
        )
        self.assertFalse(
            any(edge.get("from") == "charger" and edge.get("to") == "adjustAssistUseCase" for edge in uc["edges"])
        )

        interaction = json.loads((ROOT / "examples/e-bike/e-bike-int.json").read_text(encoding="utf-8"))
        self.assertEqual(interaction["lifelines"]["hubMotor"]["label"], "Rear Geared Hub")

        stm = json.loads((ROOT / "examples/e-bike/e-bike-stm.json").read_text(encoding="utf-8"))
        hops = {(edge["from"], edge["to"]) for edge in stm["transitions"]}
        self.assertIn(("fault", "off"), hops)
        self.assertNotIn(("fault", "standby"), hops)
        self.assertIn(("off", "charging"), hops)
        self.assertNotIn(("standby", "charging"), hops)
        self.assertNotIn(("standby", "fault"), hops)
        self.assertTrue(stm["states"]["walk"]["label"].startswith("walk"))
        self.assertIn("do / <= 6 km/h", stm["states"]["walk"]["label"])
        self.assertIn("from Off only", stm["states"]["charging"]["label"])
        self.assertIn("resetFault is Fault→Off", model)
        self.assertIn("Charging only from Off", model)

        bdd = json.loads((ROOT / "examples/e-bike/e-bike-bdd.json").read_text(encoding="utf-8"))
        children = bdd["roots"][0]["children"]
        hub = next(child for child in children if child["id"] == "hubMotor")
        self.assertIn("Rear Geared Hub", hub["label"])
        self.assertIn("250 W cont. (EU)", hub["label"])
        self.assertIn("40 N·m peak", hub["label"])
        self.assertIn("regen none", hub["label"])
        self.assertIn("250 W cont. (EU)", ibd["nodes"]["hubMotor"]["label"])
        self.assertIn("40 N·m peak", ibd["nodes"]["hubMotor"]["label"])
        self.assertIn("regen none", ibd["nodes"]["hubMotor"]["label"])
        pack = next(child for child in children if child["id"] == "batteryPack")
        self.assertEqual(pack["children"][0]["id"], "bms")

    def test_architecture_notes_are_simplified_magicgrid_walkthroughs(self):
        notes = {
            "toaster": ROOT / "examples/toaster/toaster-architecture-summary.md",
            "blender": ROOT / "examples/blender/blender-architecture-summary.md",
            "e-bike": ROOT / "examples/e-bike/e-bike-architecture-summary.md",
            "apollo": ROOT / "examples/apollo/apollo-architecture-summary.md",
        }
        for name, path in notes.items():
            text = path.read_text(encoding="utf-8")
            with self.subTest(name=name):
                self.assertIn("simplified MagicGrid", text)
                self.assertIn("Department of Defense Architecture Framework (DoDAF)", text)
                self.assertIn("example model, not a certifiable", text)
                self.assertNotIn("Grok", text)
                self.assertNotIn("we locked", text)
                self.assertNotIn("HOS", text)
                self.assertNotIn("2200±300", text)
        toaster = notes["toaster"].read_text(encoding="utf-8")
        self.assertIn("±5%", toaster)
        self.assertIn("at least three", toaster)
        self.assertIn("no more than 10 N", toaster)
        self.assertIn("at least 10,000", toaster)
        self.assertIn("heaterToCarriage", toaster)
        self.assertIn("heat to the carriage", toaster)
        self.assertNotIn("heat to bread", toaster.lower())
        self.assertNotIn("include/extend", toaster)
        self.assertNotIn("include or extend", toaster)
        self.assertIn("Error is event names only", toaster)
        self.assertIn("no equations and no results", toaster)
        self.assertNotIn("uses heatEnergyBalance against browning", toaster)
        self.assertNotIn("named constraint `heatEnergyBalance`", toaster)
        self.assertNotIn("named constraint `electricalPowerLimit`", toaster)
        blender = notes["blender"].read_text(encoding="utf-8")
        self.assertIn("within 50 ms", blender)
        self.assertIn("MainsSupply", blender)
        self.assertIn("ElectricalEnergy", blender)
        self.assertIn("mainsPowerFlow", blender)
        self.assertIn("There is **no** `PowerPort`", blender)
        self.assertNotIn("include/extend", blender)
        self.assertNotIn("include or extend", blender)
        self.assertNotIn("interlock geometry", blender)
        self.assertIn("No interlock part", blender)
        self.assertIn("Error is event names only", blender)
        self.assertNotIn("motor-stop", blender)
        self.assertIn("no equations and no results", blender)
        self.assertNotIn("named constraint `torqueSpeedLoadEstimate`", blender)
        self.assertNotIn("named constraint `smoothnessThresholdEstimate`", blender)
        self.assertNotIn("uses torqueSpeedLoadEstimate against", blender)
        self.assertNotIn("uses smoothnessThresholdEstimate against", blender)
        ebike = notes["e-bike"].read_text(encoding="utf-8")
        self.assertIn("EN 15194:2017 clause 4.2.13", ebike)
        self.assertIn("250 W is the European Union (EU) continuous rating", ebike)
        self.assertIn("charger → `bms.chargerIn`", ebike)
        self.assertIn("UL 2849 cited; not a certification shall", ebike)
        self.assertIn("Ride Bike **includes** Adjust Assist", ebike)
        self.assertNotIn("every actor, include/extend", ebike)
        apollo = notes["apollo"].read_text(encoding="utf-8")
        self.assertNotIn("All Viewpoint 1", apollo)
        self.assertNotIn("DoDAF overview card", apollo)
        self.assertNotIn("MagicGrid layer:", apollo)
        self.assertNotIn("This note teaches", apollo)
        self.assertNotIn("This note uses", apollo)
        self.assertNotIn("The block below is an AV-1", apollo)
        self.assertIn("NPR 7123.1", apollo)
        self.assertNotIn("NPR 7123 stakeholder expectations", apollo)
        self.assertNotIn("NPR 7123 product verification", apollo)
        self.assertNotIn("NPR 7123 technical requirements", apollo)
        self.assertNotIn("NPR 7123 logical decomposition at system grain", apollo)
        self.assertNotIn("NPR 7123 design solution", apollo)
        self.assertIn("Who needs what", apollo)
        self.assertIn("The shalls", apollo)
        self.assertIn("What the design does in time", apollo)
        self.assertIn("The serialed hardware", apollo)
        self.assertIn("Named checks", apollo)
        self.assertNotIn("| Physical-subsystem |", apollo)
        self.assertNotIn("| Use Cases |", apollo)
        self.assertNotIn("| Functional |", apollo)
        self.assertNotIn("every actor, include/extend", apollo)
        self.assertNotIn("planned GET (A11 Press Kit)", apollo)
        self.assertIn("D-7720 April 1967 plan baseline", apollo)
        self.assertIn("descent → DPS, AgZn1–4, ECA, landingRadar", apollo)
        self.assertIn("PNGS → IMU", apollo)
        self.assertNotIn("PNGS → IMU, rendezvousRadar", apollo)
        self.assertIn("8 panels (4 jettison / 4 stay)", apollo)
        self.assertNotIn("four petals", apollo)
        self.assertIn("ST-124", apollo)
        self.assertIn("Flight Control Computer (FCC)", apollo)
        self.assertIn("PGNCS", apollo)
        self.assertIn("A11-FP is the **only planned source**", apollo)
        self.assertNotIn("Apollo 11 Flight Plan", apollo)
        self.assertIn("MSC-00171", apollo)
        self.assertIn("~075:49:50 GET", apollo)
        self.assertIn("2:44:26 GET", apollo)
        self.assertNotIn("02:44:16.2", apollo)
        self.assertNotIn("flown 75:54:28", apollo.lower())
        self.assertIn("**Includes** Lunar EVA", apollo)
        for sent in apollo.replace(";", ".").split("."):
            if "75:54:28" in sent:
                self.assertNotIn("Press Kit", sent)
                self.assertNotRegex(sent, r"\bPK\b")

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
