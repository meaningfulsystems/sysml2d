"""Flow view composer."""

from pathlib import Path

from .views import view_file


def flow_file(input_path: Path, output_path: Path | None = None) -> Path:
    return view_file(input_path, output_path, kind="FlowView", default_symbol="flow_node")
