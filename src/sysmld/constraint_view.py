"""Constraint view composer."""

from pathlib import Path

from .views import view_file


def constraint_file(input_path: Path, output_path: Path | None = None) -> Path:
    return view_file(input_path, output_path, kind="ConstraintView", default_symbol="constraint")
