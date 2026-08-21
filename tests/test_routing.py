from __future__ import annotations

import unittest

from sysmld.render_svg import _connection_path
from sysmld.routing import (
    hop_crossings,
    orthogonal_intersection,
    orthogonal_path_avoiding_boxes,
    path_crosses_boxes,
    rank_route_assignments,
)
from sysmld.views import view


class RoutingTests(unittest.TestCase):
    def test_orthogonal_intersection_finds_interior_crossing(self):
        hit = orthogonal_intersection((0, 10), (20, 10), (8, 0), (8, 20))
        self.assertEqual(hit, (8, 10))

    def test_orthogonal_intersection_ignores_shared_endpoints(self):
        self.assertIsNone(orthogonal_intersection((0, 10), (10, 10), (10, 10), (10, 20)))

    def test_later_path_hops_over_earlier_path(self):
        hops = hop_crossings([
            [(0, 20), (60, 20)],
            [(30, 0), (30, 50)],
        ])
        self.assertEqual(hops[0], [])
        self.assertEqual(hops[1], [(0, 30.0, 20.0)])

    def test_hop_near_corner_when_far_from_path_ends(self):
        hops = hop_crossings([
            [(0, 20), (80, 20)],
            [(70, 0), (20, 12), (20, 50)],
        ])
        self.assertEqual(hops[1], [(1, 20.0, 20.0)])

    def test_connection_path_inserts_hop_arc(self):
        path = _connection_path(
            [(30, 0), (30, 50)],
            0,
            [(0, 30.0, 20.0)],
        )
        self.assertIn(" A 7 7 0 0 ", path)
        self.assertIn("30,13", path)

    def test_ranked_channel_tracks_separate_parallel_edges(self):
        spec = {
            "kind": "VerificationCaseView",
            "mode": "sketch",
            "direction": "left-right",
            "nodes": {
                "caseA": {"label": "Case A", "rank": 0, "order": 0},
                "caseB": {"label": "Case B", "rank": 0, "order": 1},
                "reqA": {"label": "Req A", "symbol": "requirement", "rank": 1, "order": 0},
                "reqB": {"label": "Req B", "symbol": "requirement", "rank": 1, "order": 1},
            },
            "edges": [
                {"from": "caseA", "to": "reqA", "label": "verifies"},
                {"from": "caseA", "to": "reqB", "label": "verifies"},
                {"from": "caseB", "to": "reqB", "label": "verifies"},
            ],
        }
        nodes = spec["nodes"]
        boxes = {
            "caseA": (0, 0, 80, 40),
            "caseB": (0, 80, 80, 40),
            "reqA": (200, 0, 80, 40),
            "reqB": (200, 80, 80, 40),
        }
        assignments = rank_route_assignments(spec["edges"], boxes, nodes, "left-right")
        tracks = [item[1] for item in assignments if item and item[0] == "channel"]
        self.assertEqual(len(set(tracks)), 3)

        doc = view(spec, kind="VerificationCaseView")
        crossing = next(
            connection
            for connection in doc["diagram"]["connections"]
            if connection["source"]["element"] == "caseA" and connection["target"]["element"] == "reqB"
        )
        self.assertTrue(crossing["route"]["waypoints"])

    def test_skip_rank_edges_use_outside_rail(self):
        spec = {
            "kind": "PackageView",
            "mode": "sketch",
            "direction": "top-down",
            "nodes": {
                "root": {"label": "Model", "rank": 0, "order": 0},
                "mid": {"label": "Structure", "rank": 1, "order": 0},
                "leaf": {"label": "Analysis", "rank": 2, "order": 0},
            },
            "edges": [
                {"from": "root", "to": "mid", "label": "contains"},
                {"from": "root", "to": "leaf", "label": "contains"},
            ],
        }
        doc = view(spec, kind="PackageView")
        skip = next(
            connection
            for connection in doc["diagram"]["connections"]
            if connection["id"] == "conn-root-leaf"
        )
        boxes = {element["id"]: element["layout"] for element in doc["diagram"]["elements"]}
        rail_x = skip["route"]["waypoints"][0]["x"]
        self.assertGreater(rail_x, boxes["mid"]["x"] + boxes["mid"]["width"])

    def test_aligned_exclusive_edges_stay_straight(self):
        spec = {
            "kind": "AnalysisCaseView",
            "mode": "sketch",
            "direction": "left-right",
            "nodes": {
                "caseA": {"label": "Case A", "rank": 0, "order": 0},
                "caseB": {"label": "Case B", "rank": 0, "order": 1},
                "methodA": {"label": "Method A", "symbol": "constraint", "rank": 1, "order": 0},
                "methodB": {"label": "Method B", "symbol": "constraint", "rank": 1, "order": 1},
            },
            "edges": [
                {"from": "caseA", "to": "methodA", "label": "method"},
                {"from": "caseB", "to": "methodB", "label": "method"},
            ],
        }
        doc = view(spec, kind="AnalysisCaseView")
        for connection in doc["diagram"]["connections"]:
            self.assertEqual(connection["route"]["waypoints"], [])

    def test_preferred_clear_path_is_unchanged(self):
        start = (0.0, 10.0)
        end = (80.0, 10.0)
        boxes = {"block": (20.0, 30.0, 20.0, 20.0)}
        preferred = [start, end]
        self.assertEqual(
            orthogonal_path_avoiding_boxes(start, end, boxes, preferred=preferred),
            [],
        )

    def test_route_goes_around_box_not_through_it(self):
        start = (0.0, 50.0)
        end = (200.0, 50.0)
        boxes = {"mid": (80.0, 20.0, 40.0, 60.0)}
        preferred = [start, end]
        self.assertTrue(path_crosses_boxes(preferred, boxes))
        waypoints = orthogonal_path_avoiding_boxes(
            start, end, boxes, preferred=preferred, clearance=8.0
        )
        full = [start, *waypoints, end]
        self.assertTrue(waypoints)
        self.assertFalse(path_crosses_boxes(full, boxes))
        for start_pt, end_pt in zip(full, full[1:]):
            self.assertTrue(
                round(start_pt[0], 3) == round(end_pt[0], 3)
                or round(start_pt[1], 3) == round(end_pt[1], 3)
            )

    def test_use_case_channels_stay_outside_system_boundary(self):
        spec = {
            "kind": "UseCaseView",
            "mode": "sketch",
            "direction": "left-right",
            "col_gap": 180,
            "nodes": {
                "actor": {"label": "Rider", "symbol": "actor", "rank": 0, "order": 0},
                "ride": {"label": "Ride", "rank": 1, "order": 0},
                "charge": {"label": "Charge", "rank": 1, "order": 1},
            },
            "groups": [
                {"id": "bike", "label": "Bike", "members": ["ride", "charge"], "pad_x": 70, "pad_y": 40}
            ],
            "edges": [
                {"from": "actor", "to": "ride"},
                {"from": "actor", "to": "charge"},
            ],
        }
        doc = view(spec, kind="UseCaseView")
        boxes = {element["id"]: element["layout"] for element in doc["diagram"]["elements"]}
        group_left = boxes["bike"]["x"]
        for connection in doc["diagram"]["connections"]:
            for point in connection["route"]["waypoints"]:
                self.assertLess(point["x"], group_left)


if __name__ == "__main__":
    unittest.main()
