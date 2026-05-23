from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from sysmld.render_svg import (
    Bounds,
    _best_port_label_candidate,
    _close_packed_port_ids,
    _connection_labels,
    _initial_label_obstacles,
    _overlap_area,
    _text_bounds,
    render_svg,
    scene_to_svg,
)
from sysmld.render_svg import _placed_port_label
from sysmld.scene import Box, SceneElement, build_scene


ROOT = Path(__file__).resolve().parents[1]
TOASTER = ROOT / "examples/toaster/toaster-electrical-icn.sysmld"
TOASTER_ELECTRICAL = ROOT / "examples/toaster/toaster-electrical-icn.sysmld"
TOASTER_MECHANICAL = ROOT / "examples/toaster/manual/toaster-mechanical-icn.sysmld"
TOASTER_MECH_COMPOSED = ROOT / "examples/toaster/toaster-mech-composed.sysmld"
TOASTER_BDD = ROOT / "examples/toaster/toaster-bdd.sysmld"
BLENDER_COMPOSED = ROOT / "examples/blender/blender-ibd-composed.sysmld"
BLENDER_BDD = ROOT / "examples/blender/blender-bdd.sysmld"
TOASTER_STM = ROOT / "examples/toaster/toaster-stm.sysmld"
BLENDER_STM = ROOT / "examples/blender/blender-stm.sysmld"
TOASTER_INTERACTION = ROOT / "examples/toaster/toaster-int.sysmld"


class RenderSvgTests(unittest.TestCase):
    def test_scene_has_expected_header_and_ports(self):
        scene = build_scene(TOASTER)
        self.assertEqual(scene.header, "[icn.mb] Toaster Electrical Interconnection [toaster : Toaster]")
        self.assertIn("lever--power-control-subsystem--src", {element.id for element in scene.elements})
        self.assertIn("buttons", {element.id for element in scene.elements})
        self.assertIn("power-cord", {element.id for element in scene.elements})
        self.assertEqual(len(scene.connections), 6)

    def test_svg_contains_frame_header_and_connections(self):
        scene = build_scene(TOASTER)
        svg = scene_to_svg(scene)
        self.assertIn("[icn.mb] Toaster Electrical Interconnection [toaster : Toaster]", svg)
        self.assertIn("<path", svg)
        self.assertIn("<tspan", svg)
        self.assertIn(" Q ", svg)
        self.assertIn("heat command", svg)

    def test_render_svg_writes_file(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "toaster.svg"
            result = render_svg(TOASTER, output_path=target)
            self.assertEqual(result, target)
            self.assertTrue(target.exists())
            self.assertIn("<svg", target.read_text(encoding="utf-8"))

    def test_split_views_render_expected_content(self):
        electrical_svg = scene_to_svg(build_scene(TOASTER_ELECTRICAL))
        mechanical_svg = scene_to_svg(build_scene(TOASTER_MECHANICAL))
        self.assertIn("Toaster Electrical Interconnection", electrical_svg)
        self.assertIn("Mains Power", electrical_svg)
        self.assertIn("Power Cord", electrical_svg)
        self.assertIn("press", electrical_svg)
        self.assertIn("in", electrical_svg)
        self.assertIn("line power", electrical_svg)
        self.assertIn("button control", electrical_svg)
        self.assertIn("heat command", electrical_svg)
        self.assertIn("Toaster Mechanical Interconnection", mechanical_svg)
        self.assertIn("Buttons", mechanical_svg)
        self.assertIn("button press", mechanical_svg)
        self.assertIn("Crumb Tray", mechanical_svg)
        self.assertIn("pull/remove", mechanical_svg)
        self.assertIn("lift", mechanical_svg)

    def test_blender_composed_renders_expected_content(self):
        blender_svg = scene_to_svg(build_scene(BLENDER_COMPOSED))
        self.assertIn("Blender Internal Structure", blender_svg)
        self.assertIn("Tamper", blender_svg)
        self.assertIn("Container", blender_svg)
        self.assertIn("Drive Coupling", blender_svg)
        self.assertIn("Control Panel", blender_svg)
        self.assertIn("vibration/load", blender_svg)

    def test_definition_trees_render_expected_content(self):
        toaster_svg = scene_to_svg(build_scene(TOASTER_BDD))
        blender_svg = scene_to_svg(build_scene(BLENDER_BDD))

        self.assertIn("[def.mb] Toaster Definition Tree [Toaster]", toaster_svg)
        self.assertIn("Power &amp; Control", toaster_svg)
        self.assertIn("Crumb Tray", toaster_svg)
        self.assertIn('marker-start="url(#composition)"', toaster_svg)
        self.assertIn(">0..1<", toaster_svg)
        self.assertIn("[def.mb] Blender Definition Tree [Blender]", blender_svg)
        self.assertIn("Blade Assembly", blender_svg)
        self.assertIn("Smoothness", blender_svg)

    def test_state_machines_render_expected_content(self):
        toaster_svg = scene_to_svg(build_scene(TOASTER_STM))
        blender_svg = scene_to_svg(build_scene(BLENDER_STM))

        self.assertIn("[stv.mb] Toaster Control State Machine [toasterControl : ToasterControl]", toaster_svg)
        self.assertIn("Heating", toaster_svg)
        self.assertIn("carriage up", toaster_svg)
        self.assertIn("[stv.mb] Blender Control State Machine [blenderControl : BlenderControl]", blender_svg)
        self.assertIn("Powered", blender_svg)
        self.assertIn("smoothness signal [smooth] / stop", blender_svg)

    def test_interaction_messages_anchor_on_lifeline_centers(self):
        scene = build_scene(TOASTER_INTERACTION)
        centers = {
            element.id: element.box.center_x
            for element in scene.elements
            if element.symbol == "lifeline"
        }
        messages = {connection.id: connection for connection in scene.connections}

        self.assertLess(scene.width, 1200)
        self.assertEqual(messages["msgLowerLever"].points[0][0], centers["user"])
        self.assertEqual(messages["msgLowerLever"].points[-1][0], centers["lever"])
        self.assertEqual(messages["msgControl"].points[0][0], centers["lever"])
        self.assertEqual(messages["msgControl"].points[-1][0], centers["powerAndControlSubsystem"])
        self.assertEqual(messages["msgPresent"].points[0][0], centers["carriage"])
        self.assertEqual(messages["msgPresent"].points[-1][0], centers["user"])

    def test_new_view_symbols_render_expected_shapes(self):
        usecase_svg = scene_to_svg(build_scene(ROOT / "examples/toaster/toaster-uc.sysmld"))
        action_svg = scene_to_svg(build_scene(ROOT / "examples/blender/blender-act.sysmld"))
        interaction_svg = scene_to_svg(build_scene(ROOT / "examples/blender/blender-int.sysmld"))
        package_svg = scene_to_svg(build_scene(ROOT / "examples/toaster/toaster-pkg.sysmld"))

        self.assertIn("<ellipse", usecase_svg)
        self.assertIn("Toast Bread", usecase_svg)
        self.assertIn("<polygon", action_svg)
        self.assertIn("smooth?", action_svg)
        self.assertIn('marker-end="url(#arrow-dark)"', action_svg)
        self.assertIn("stroke-dasharray=\"5 5\"", interaction_svg)
        self.assertIn("Smoothness Sensor", interaction_svg)
        self.assertIn("Toaster Model", package_svg)

    def test_relationship_styles_render_dashed(self):
        usecase_svg = scene_to_svg(build_scene(ROOT / "examples/toaster/toaster-uc.sysmld"))
        interaction_svg = scene_to_svg(build_scene(ROOT / "examples/blender/blender-int.sysmld"))
        allocation_svg = scene_to_svg(build_scene(ROOT / "examples/toaster/toaster-alloc.sysmld"))
        flow_svg = scene_to_svg(build_scene(ROOT / "examples/toaster/toaster-flow.sysmld"))
        general_svg = scene_to_svg(build_scene(ROOT / "examples/toaster/toaster-general.sysmld"))

        self.assertIn('stroke-dasharray="6 4"', usecase_svg)
        self.assertIn('marker-end="url(#arrow-dark)"', interaction_svg)
        self.assertIn('stroke-dasharray="6 4"', allocation_svg)
        self.assertIn('marker-end="url(#arrow-dark)"', allocation_svg)
        self.assertIn('marker-end="url(#arrow-dark)"', flow_svg)
        self.assertIn('marker-end="url(#arrow-dark)"', general_svg)

    def test_auto_connection_label_avoids_occupied_bounds(self):
        occupied = [Bounds(45, 75, 50, 20)]
        labels = [{"text": "mount", "position": {"offset": 0.5}}]

        svg_nodes = _connection_labels(
            [(0, 100), (140, 100)],
            labels,
            {"label_offset": 10},
            occupied,
            [],
        )

        self.assertEqual(len(svg_nodes), 1)
        self.assertEqual(_overlap_area(occupied[-1], Bounds(45, 75, 50, 20)), 0)

    def test_auto_connection_labels_do_not_overlap_each_other(self):
        occupied = []
        labels = [{"text": "guide", "position": {"offset": 0.5}}]
        points = [(0, 100), (140, 100)]

        _connection_labels(points, labels, {"label_offset": 10}, occupied, [])
        _connection_labels(points, labels, {"label_offset": 10}, occupied, [])

        self.assertEqual(_overlap_area(occupied[0], occupied[1]), 0)

    def test_centerline_connection_label_prefers_connector_center(self):
        occupied = []
        labels = [{"text": "event", "position": {"offset": 0.5, "placement": "centerline"}}]

        svg_nodes = _connection_labels(
            [(0, 100), (140, 100)],
            labels,
            {"label_offset": 10},
            occupied,
            [],
        )

        self.assertIn('x="70" y="108"', svg_nodes[0])

    def test_centerline_connection_label_moves_on_collision(self):
        occupied = [Bounds(45, 95, 50, 20)]
        labels = [{"text": "event", "position": {"offset": 0.5, "placement": "centerline"}}]

        svg_nodes = _connection_labels(
            [(0, 100), (140, 100)],
            labels,
            {"label_offset": 10},
            occupied,
            [],
        )

        self.assertNotIn('x="70" y="108"', svg_nodes[0])
        self.assertEqual(_overlap_area(occupied[-1], Bounds(45, 95, 50, 20)), 0)

    def test_auto_port_labels_do_not_overlap_each_other(self):
        occupied = []
        route_segments = [((56, 80), (56, 10)), ((64, 80), (64, 10))]
        first = SceneElement(
            id="p1",
            symbol="port",
            box=Box(50, 50, 12, 12),
            label="guide",
            style={},
            owner="a",
            port_side="top",
        )
        second = SceneElement(
            id="p2",
            symbol="port",
            box=Box(58, 50, 12, 12),
            label="mount",
            style={},
            owner="a",
            port_side="top",
        )

        first_label = _placed_port_label(first, occupied, route_segments, close_packed=True)[0]
        second_label = _placed_port_label(second, occupied, route_segments, close_packed=True)[0]

        self.assertEqual(_overlap_area(occupied[0], occupied[1]), 0)
        self.assertIn('text-anchor="middle"', first_label)
        self.assertIn('x="56"', first_label)
        self.assertIn('text-anchor="middle"', second_label)
        self.assertIn('x="64"', second_label)
        self.assertNotIn('y="40"', second_label)

    def test_non_close_packed_port_label_uses_whitespace_around_route(self):
        occupied = []
        route_segments = [((56, 80), (56, 10))]
        port = SceneElement(
            id="p1",
            symbol="port",
            box=Box(50, 50, 12, 12),
            label="guide",
            style={},
            owner="a",
            port_side="top",
        )

        label = _placed_port_label(port, occupied, route_segments, close_packed=False)[0]

        self.assertNotIn('x="56"', label)

    def test_boundary_port_label_stays_inside_frame(self):
        occupied = []
        port = SceneElement(
            id="bnd--buttons",
            symbol="port",
            box=Box(34, 106, 12, 12),
            label="Button Input",
            style={},
            owner="boundary",
            port_side="left",
        )

        _x, _y, _anchor, bounds = _best_port_label_candidate(
            port,
            occupied,
            [],
            close_packed=False,
            label_bounds=Bounds(0, 0, 999, 522),
        )

        self.assertGreaterEqual(bounds.x, 0)
        self.assertGreaterEqual(bounds.y, 0)
        self.assertLessEqual(bounds.right, 999)
        self.assertLessEqual(bounds.bottom, 522)

    def test_boundary_port_label_avoids_connection_no_fly_zone(self):
        occupied = []
        route_segments = [((56, 110), (160, 110))]
        port = SceneElement(
            id="bnd--buttons",
            symbol="port",
            box=Box(34, 106, 12, 12),
            label="Button Input",
            style={},
            owner="boundary",
            port_side="left",
        )

        _x, _y, _anchor, bounds = _best_port_label_candidate(
            port,
            occupied,
            route_segments,
            close_packed=False,
            label_bounds=Bounds(0, 0, 999, 522),
        )

        self.assertFalse(bounds.y <= 110 <= bounds.bottom and bounds.x <= 56 <= bounds.right)

    def test_port_label_avoids_boundary_title_text(self):
        scene = build_scene(TOASTER_MECH_COMPOSED)
        occupied = _initial_label_obstacles(scene.elements)
        route_segments = [
            segment
            for connection in scene.connections
            for segment in zip(connection.points, connection.points[1:])
        ]
        close_packed_ports = _close_packed_port_ids(scene.elements)
        port = next(element for element in scene.elements if element.id == "buttons--bnd--tgt")
        boundary = next(element for element in scene.elements if element.id == "boundary")
        boundary_label = _text_bounds(boundary.label, boundary.box.x + 10, boundary.box.y + 22, "")

        _x, _y, _anchor, bounds = _best_port_label_candidate(
            port,
            occupied,
            route_segments,
            port.id in close_packed_ports,
            Bounds(0, 0, scene.width, scene.height),
        )

        self.assertEqual(_overlap_area(bounds, boundary_label), 0)

    def test_close_packed_boundary_port_label_still_avoids_connection_no_fly_zone(self):
        occupied = []
        route_segments = [((156, 40), (156, 4))]
        port = SceneElement(
            id="bnd--buttons",
            symbol="port",
            box=Box(150, 34, 12, 12),
            label="button press",
            style={},
            owner="boundary",
            port_side="top",
        )

        _x, _y, _anchor, bounds = _best_port_label_candidate(
            port,
            occupied,
            route_segments,
            close_packed=True,
            label_bounds=Bounds(0, 0, 972, 528),
        )

        self.assertFalse(bounds.x <= 156 <= bounds.right and bounds.y <= 40 <= bounds.bottom)

    def test_close_packed_detection_uses_label_width(self):
        ports = [
            SceneElement("p1", "port", Box(50, 50, 12, 12), "guide", {}, owner="a", port_side="top"),
            SceneElement("p2", "port", Box(82, 50, 12, 12), "mount", {}, owner="a", port_side="top"),
            SceneElement("p3", "port", Box(170, 50, 12, 12), "lift", {}, owner="a", port_side="top"),
        ]

        self.assertEqual(_close_packed_port_ids(ports), {"p1", "p2"})


if __name__ == "__main__":
    unittest.main()
