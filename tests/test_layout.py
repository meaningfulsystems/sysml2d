import unittest

from sysmld.layout import _edge_crossings, compute


class LayoutTests(unittest.TestCase):
    def test_wrapped_layout_reduces_blender_graph_crossings(self):
        nodes = [
            "tamper",
            "lid",
            "container",
            "bladeAssembly",
            "driveCoupling",
            "smoothnessSensor",
            "motorBase",
            "motor",
            "controlPanel",
        ]
        edges = [
            {"from": "tamper", "to": "lid"},
            {"from": "lid", "to": "container"},
            {"from": "container", "to": "bladeAssembly"},
            {"from": "container", "to": "motorBase"},
            {"from": "motorBase", "to": "motor"},
            {"from": "motorBase", "to": "controlPanel"},
            {"from": "motorBase", "to": "driveCoupling"},
            {"from": "bladeAssembly", "to": "driveCoupling"},
            {"from": "driveCoupling", "to": "motor"},
            {"from": "driveCoupling", "to": "smoothnessSensor"},
            {"from": "smoothnessSensor", "to": "controlPanel"},
            {"from": "controlPanel", "to": "motor"},
        ]

        layout = compute(
            nodes,
            edges,
            "top-down",
            col_gap=120,
            rank_gap=160,
            margin=80,
            rank_wrap="golden",
        )

        self.assertEqual(_edge_crossings(edges, layout.cx, layout.cy), 0)


if __name__ == "__main__":
    unittest.main()
