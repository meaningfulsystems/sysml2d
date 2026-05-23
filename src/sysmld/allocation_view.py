"""Allocation view composer."""

from pathlib import Path

from .views import view_file


def allocation_file(input_path: Path, output_path: Path | None = None) -> Path:
    return view_file(input_path, output_path, kind="AllocationView", default_symbol="allocation")
