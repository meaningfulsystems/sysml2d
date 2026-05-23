"""Action view composer."""

from pathlib import Path

from .views import action_file as _action_file


def action_file(input_path: Path, output_path: Path | None = None) -> Path:
    return _action_file(input_path, output_path)
