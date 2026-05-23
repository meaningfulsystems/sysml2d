"""Validation for SysMLD documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .io import read_json, resolve_path
from .model_index import build_model_index


VIEW_KINDS = {
    "DefinitionView",
    "InterconnectionView",
    "PackageView",
    "ConstraintView",
    "RequirementView",
    "ActionView",
    "StateView",
    "InteractionView",
    "UseCaseView",
    "AllocationView",
    "FlowView",
    "AnalysisCaseView",
    "VerificationCaseView",
    "InterfaceView",
    "GeneralView",
}

SIDES = {"top", "right", "bottom", "left"}


@dataclass
class Finding:
    code: str
    message: str
    severity: str = "error"


@dataclass
class ValidationReport:
    findings: list[Finding] = field(default_factory=list)

    @property
    def errors(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    def error(self, code: str, message: str) -> None:
        self.findings.append(Finding(code=code, message=message))

    def warn(self, code: str, message: str) -> None:
        self.findings.append(Finding(code=code, message=message, severity="warning"))


def validate_file(path: Path, strict: bool = False, lint: bool = False) -> ValidationReport:
    """Validate a SysMLD document and return all findings."""

    report = ValidationReport()
    try:
        data = read_json(path)
    except Exception as exc:
        report.error("SYSMLD-SCHEMA-001", str(exc))
        return report
    validate_schema_shape(data, report)
    if strict and report.errors == 0:
        validate_strict(path, data, report)
    if lint and report.errors == 0:
        validate_lint(data, report)
    return report


def validate_schema_shape(data: dict[str, Any], report: ValidationReport) -> None:
    required = ["version", "mode", "diagram"]
    for key in required:
        if key not in data:
            report.error("SYSMLD-SCHEMA-002", f"missing required field: {key}")
    if data.get("version") != "0.1":
        report.error("SYSMLD-SCHEMA-003", "version must be '0.1'")
    if data.get("mode") not in {"model_based", "sketch"}:
        report.error("SYSMLD-SCHEMA-003", "mode must be model_based or sketch")
    diagram = data.get("diagram")
    if not isinstance(diagram, dict):
        report.error("SYSMLD-SCHEMA-002", "diagram must be an object")
        return
    for key in ["id", "kind", "name", "canvas", "elements", "connections"]:
        if key not in diagram:
            report.error("SYSMLD-SCHEMA-002", f"diagram missing required field: {key}")
    if diagram.get("kind") not in VIEW_KINDS:
        report.error("SYSMLD-SCHEMA-003", f"invalid diagram kind: {diagram.get('kind')}")
    _validate_canvas(diagram.get("canvas"), report)
    _validate_elements(diagram.get("elements", []), report)
    _validate_connections(diagram.get("connections", []), report)


def _validate_canvas(canvas: Any, report: ValidationReport) -> None:
    if not isinstance(canvas, dict):
        report.error("SYSMLD-SCHEMA-002", "canvas must be an object")
        return
    for key in ["width", "height"]:
        value = canvas.get(key)
        if not isinstance(value, (int, float)) or value <= 0:
            report.error("SYSMLD-SCHEMA-004", f"canvas.{key} must be positive")


def _validate_elements(elements: Any, report: ValidationReport) -> None:
    if not isinstance(elements, list):
        report.error("SYSMLD-SCHEMA-002", "elements must be an array")
        return
    for element in elements:
        if not isinstance(element, dict):
            report.error("SYSMLD-SCHEMA-002", "element must be an object")
            continue
        for key in ["id", "symbol"]:
            if key not in element:
                report.error("SYSMLD-SCHEMA-002", f"element missing required field: {key}")
        sym = element.get("symbol")
        if sym == "port":
            _validate_placement(element.get("placement"), report)
        elif sym in ("initial_state", "final_state"):
            # Small pseudostate nodes — layout is required but may be auto-sized.
            _validate_layout(element.get("layout"), report)
        else:
            _validate_layout(element.get("layout"), report)


def _validate_layout(layout: Any, report: ValidationReport) -> None:
    if not isinstance(layout, dict):
        report.error("SYSMLD-SCHEMA-002", "non-port element missing layout")
        return
    for key in ["x", "y", "width", "height"]:
        if key not in layout:
            report.error("SYSMLD-SCHEMA-002", f"layout missing required field: {key}")
    for key in ["width", "height"]:
        value = layout.get(key)
        if not isinstance(value, (int, float)) or value <= 0:
            report.error("SYSMLD-SCHEMA-004", f"layout.{key} must be positive")


def _validate_placement(placement: Any, report: ValidationReport) -> None:
    if not isinstance(placement, dict):
        report.error("SYSMLD-SCHEMA-002", "port missing placement")
        return
    if placement.get("side") not in SIDES:
        report.error("SYSMLD-SCHEMA-003", f"invalid side: {placement.get('side')}")
    offset = placement.get("offset")
    if not isinstance(offset, (int, float)) or offset < 0 or offset > 1:
        report.error("SYSMLD-SCHEMA-004", "placement.offset must be between 0 and 1")


def _validate_connections(connections: Any, report: ValidationReport) -> None:
    if not isinstance(connections, list):
        report.error("SYSMLD-SCHEMA-002", "connections must be an array")
        return
    for connection in connections:
        if not isinstance(connection, dict):
            report.error("SYSMLD-SCHEMA-002", "connection must be an object")
            continue
        for key in ["id", "model_ref", "source", "target"]:
            if key not in connection:
                report.error("SYSMLD-SCHEMA-002", f"connection missing required field: {key}")
        for endpoint_name in ["source", "target"]:
            endpoint = connection.get(endpoint_name)
            if not isinstance(endpoint, dict) or "element" not in endpoint:
                report.error("SYSMLD-SCHEMA-002", f"connection.{endpoint_name} missing element")
                continue
            _validate_placement(endpoint.get("anchor"), report)


def validate_strict(path: Path, data: dict[str, Any], report: ValidationReport) -> None:
    mode = data["mode"]
    model_files = data.get("model_files", [])
    if mode == "model_based" and not model_files:
        report.error("SYSMLD-REF-003", "model_based diagrams require model_files")
        return
    if mode == "sketch" and model_files:
        report.error("SYSMLD-REF-003", "sketch diagrams must not declare model_files")
        return

    diagram = data["diagram"]
    elements = diagram.get("elements", [])
    connections = diagram.get("connections", [])
    element_ids = _validate_unique_ids(elements, "element", report)
    _validate_unique_ids(connections, "connection", report)
    for element in elements:
        owner = element.get("owner")
        if owner and owner not in element_ids:
            report.error("SYSMLD-VIEW-002", f"owner not found: {owner}")
    for connection in connections:
        for endpoint_name in ["source", "target"]:
            endpoint = connection.get(endpoint_name, {})
            element_id = endpoint.get("element")
            if element_id not in element_ids:
                report.error("SYSMLD-VIEW-002", f"endpoint element not found: {element_id}")

    if mode == "model_based":
        paths = [resolve_path(path, model_file) for model_file in model_files]
        for model_path in paths:
            if not model_path.exists():
                report.error("SYSMLD-REF-003", f"model file not found: {model_path}")
        if report.errors:
            return
        index = build_model_index(paths)
        aliases = data.get("aliases", {})
        refs = _collect_model_refs(data)
        for ref in refs:
            resolved = aliases.get(ref, ref)
            if ref in aliases and not resolved:
                report.error("SYSMLD-REF-001", f"alias resolves to empty value: {ref}")
            if not index.has(resolved):
                report.error("SYSMLD-REF-002", f"unresolved model reference: {ref} -> {resolved}")


def _validate_unique_ids(items: list[dict[str, Any]], label: str, report: ValidationReport) -> set[str]:
    seen: set[str] = set()
    for item in items:
        item_id = item.get("id")
        if not item_id:
            continue
        if item_id in seen:
            report.error("SYSMLD-VIEW-001", f"duplicate {label} id: {item_id}")
        seen.add(item_id)
    return seen


def _collect_model_refs(data: dict[str, Any]) -> set[str]:
    refs: set[str] = set()
    diagram = data["diagram"]
    if diagram.get("subject"):
        refs.add(diagram["subject"])
    for element in diagram.get("elements", []):
        if element.get("model_ref"):
            refs.add(element["model_ref"])
    for connection in diagram.get("connections", []):
        if connection.get("model_ref"):
            refs.add(connection["model_ref"])
    return refs


def validate_lint(data: dict[str, Any], report: ValidationReport) -> None:
    styles = data["diagram"].get("styles", {})
    if isinstance(styles, dict):
        used_styles = set()
        for element in data["diagram"].get("elements", []):
            if isinstance(element.get("style"), str):
                used_styles.add(element["style"])
        for connection in data["diagram"].get("connections", []):
            if isinstance(connection.get("style"), str):
                used_styles.add(connection["style"])
        for style_name in sorted(set(styles) - used_styles):
            report.warn("SYSMLD-LINT-002", f"unused style: {style_name}")
