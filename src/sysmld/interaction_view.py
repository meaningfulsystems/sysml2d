"""Interaction view composer."""

from pathlib import Path

from .views import interaction_file


def sequence_file(input_path: Path, output_path: Path | None = None) -> Path:
    return interaction_file(input_path, output_path)
