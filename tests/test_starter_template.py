from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sysmld.interconnection_view import compose_file
from sysmld.render_svg import scene_to_svg
from sysmld.scene import build_scene
from sysmld.state_view import stm_file
from sysmld.validate import validate_file


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "template" / "new-project"


class StarterTemplateTests(unittest.TestCase):
    def test_starter_ibd_and_stm_compose_validate_and_clear_boxes(self):
        with TemporaryDirectory() as tmp:
            dest = Path(tmp) / "new-project"
            shutil.copytree(TEMPLATE, dest)
            ibd = dest / "starter-ibd.json"
            stm = dest / "starter-stm.json"
            ibd_out = compose_file(ibd)
            stm_out = stm_file(stm)

            for path in (ibd_out, stm_out):
                report = validate_file(path, strict=True)
                self.assertEqual(
                    report.errors,
                    0,
                    [finding.message for finding in report.findings],
                )
                svg = scene_to_svg(build_scene(path))
                self.assertIn("<svg", svg)
                self.assertIn("<path", svg)

            doc = json.loads(ibd_out.read_text(encoding="utf-8"))
            self.assertEqual(doc["diagram"]["kind"], "InterconnectionView")
            self.assertEqual(_route_box_hits(doc), [])


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
            *[
                (point["x"], point["y"])
                for point in connection["route"].get("waypoints", [])
            ],
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
        x = x1
        if x <= left or x >= right:
            return False
        lo, hi = sorted((y1, y2))
        return lo < bottom and hi > top
    if round(y1) == round(y2):
        y = y1
        if y <= top or y >= bottom:
            return False
        lo, hi = sorted((x1, x2))
        return lo < right and hi > left
    return False


if __name__ == "__main__":
    unittest.main()
