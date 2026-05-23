"""Case view composers."""

from pathlib import Path

from .views import view_file


def analysis_file(input_path: Path, output_path: Path | None = None) -> Path:
    return view_file(input_path, output_path, kind="AnalysisCaseView", default_symbol="case")


def verification_file(input_path: Path, output_path: Path | None = None) -> Path:
    return view_file(input_path, output_path, kind="VerificationCaseView", default_symbol="case")
