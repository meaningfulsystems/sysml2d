from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from sysmld.validate import validate_file


ROOT = Path(__file__).resolve().parents[1]
TOASTER = ROOT / "examples/toaster/toaster-electrical-icn.sysmld"
TOASTER_ELECTRICAL = ROOT / "examples/toaster/toaster-electrical-icn.sysmld"
TOASTER_ELECTRICAL_MANUAL = ROOT / "examples/toaster/manual/toaster-electrical-icn.sysmld"
TOASTER_MECHANICAL = ROOT / "examples/toaster/manual/toaster-mechanical-icn.sysmld"
TOASTER_BDD = ROOT / "examples/toaster/toaster-bdd.sysmld"
BLENDER_COMPOSED = ROOT / "examples/blender/blender-ibd-composed.sysmld"
BLENDER_BDD = ROOT / "examples/blender/blender-bdd.sysmld"
TOASTER_STM = ROOT / "examples/toaster/toaster-stm.sysmld"
BLENDER_STM = ROOT / "examples/blender/blender-stm.sysmld"
EXAMPLE_SYSMLD = [
    *sorted((ROOT / "examples/toaster").glob("*.sysmld")),
    *sorted((ROOT / "examples/toaster/manual").glob("*.sysmld")),
    *sorted((ROOT / "examples/blender").glob("*.sysmld")),
]


class ValidateTests(unittest.TestCase):
    def test_toaster_strict_validates(self):
        for path in [TOASTER_ELECTRICAL, TOASTER_ELECTRICAL_MANUAL, TOASTER_MECHANICAL, TOASTER_BDD, TOASTER_STM]:
            with self.subTest(path=path.name):
                report = validate_file(path, strict=True)
                self.assertEqual(report.errors, 0, [f.message for f in report.findings])

    def test_blender_composed_strict_validates(self):
        for path in [BLENDER_COMPOSED, BLENDER_BDD, BLENDER_STM]:
            with self.subTest(path=path.name):
                report = validate_file(path, strict=True)
                self.assertEqual(report.errors, 0, [f.message for f in report.findings])

    def test_all_example_sysmld_strict_validates(self):
        for path in EXAMPLE_SYSMLD:
            with self.subTest(path=path.relative_to(ROOT)):
                report = validate_file(path, strict=True)
                self.assertEqual(report.errors, 0, [f.message for f in report.findings])

    def test_unresolved_alias_fails_strict_validation(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "bad.sysmld"
            data = json.loads(TOASTER.read_text(encoding="utf-8"))
            data["diagram"]["elements"][1]["model_ref"] = "missingAlias"
            target.write_text(json.dumps(data), encoding="utf-8")
            (Path(tmp) / "toaster.sysml").write_text(
                (ROOT / "examples/toaster/toaster.sysml").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            report = validate_file(target, strict=True)
        self.assertGreater(report.errors, 0)
        self.assertTrue(any(f.code == "SYSMLD-REF-002" for f in report.findings))

    def test_sketch_with_model_files_fails_strict_validation(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "sketch.sysmld"
            data = json.loads(TOASTER.read_text(encoding="utf-8"))
            data["mode"] = "sketch"
            target.write_text(json.dumps(data), encoding="utf-8")
            report = validate_file(target, strict=True)
        self.assertGreater(report.errors, 0)
        self.assertTrue(any(f.code == "SYSMLD-REF-003" for f in report.findings))

    def test_missing_endpoint_fails_strict_validation(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "bad-endpoint.sysmld"
            data = json.loads(TOASTER.read_text(encoding="utf-8"))
            data["diagram"]["connections"][0]["target"]["element"] = "missing-port"
            target.write_text(json.dumps(data), encoding="utf-8")
            (Path(tmp) / "toaster.sysml").write_text(
                (ROOT / "examples/toaster/toaster.sysml").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            report = validate_file(target, strict=True)
        self.assertGreater(report.errors, 0)
        self.assertTrue(any(f.code == "SYSMLD-VIEW-002" for f in report.findings))


if __name__ == "__main__":
    unittest.main()
