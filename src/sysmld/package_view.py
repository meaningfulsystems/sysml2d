"""Package view composer."""

from pathlib import Path

from .views import view_file


def package_file(input_path: Path, output_path: Path | None = None) -> Path:
    return view_file(input_path, output_path, kind="PackageView", default_symbol="package")
