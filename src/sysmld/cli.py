"""Command-line interface for SysMLD."""

from __future__ import annotations

import argparse
from pathlib import Path

from .action_view import action_file
from .allocation_view import allocation_file
from .case_view import analysis_file, verification_file
from .interconnection_view import compose_file
from .constraint_view import constraint_file
from .flow_view import flow_file
from .general_view import general_file
from .graph import graph_file
from .interaction_view import sequence_file
from .interface_view import interface_file
from .package_view import package_file
from .render_svg import render_png, render_svg
from .requirement_view import requirement_file
from .state_view import stm_file
from .definition_view import tree_file
from .use_case_view import usecase_file
from .validate import validate_file


def main() -> int:
    """Run the SysMLD command-line interface."""

    parser = argparse.ArgumentParser(prog="sysmld")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ── Topology debug ────────────────────────────────────────────────────────
    graph_parser = subparsers.add_parser(
        "graph",
        help="Render a topology-only SVG and position JSON from an intent file",
    )
    graph_parser.add_argument("path", help="Layout intent JSON file")
    graph_parser.add_argument("--output", "-o", help="Output SVG path (default: <input>.graph.svg)")
    graph_parser.add_argument("--direction", choices=["top-down", "bottom-up", "left-right", "right-left"])

    # ── InterconnectionView ───────────────────────────────────────────────────
    icn_parser = subparsers.add_parser(
        "interconnection",
        aliases=["compose", "ibd"],
        help="Generate an InterconnectionView .sysmld from an intent file",
    )
    icn_parser.add_argument("path", help="Intent JSON file")
    icn_parser.add_argument("--output", "-o", help="Output .sysmld path")
    icn_parser.add_argument("--graph", action="store_true",
                            help="Also write topology graph sidecars")
    icn_parser.add_argument("--graph-output",
                            help="Output graph SVG path (default: <input>.graph.svg)")

    # ── DefinitionView ────────────────────────────────────────────────────────
    def_parser = subparsers.add_parser(
        "definition",
        aliases=["bdd", "tree"],
        help="Generate a DefinitionView tree .sysmld from an intent file",
    )
    def_parser.add_argument("path", help="Tree intent JSON file")
    def_parser.add_argument("--output", "-o", help="Output .sysmld path")

    # ── StateView ─────────────────────────────────────────────────────────────
    stm_parser = subparsers.add_parser(
        "state",
        aliases=["stm"],
        help="Generate a StateView .sysmld from a state machine intent file",
    )
    stm_parser.add_argument("path", help="State machine intent JSON file")
    stm_parser.add_argument("--output", "-o", help="Output .sysmld path")

    # ── All other view types (generic layout engine) ──────────────────────────
    view_commands = {
        "package":      ("Generate a PackageView .sysmld",           package_file),
        "requirement":  ("Generate a RequirementView .sysmld",        requirement_file),
        "constraint":   ("Generate a ConstraintView .sysmld",         constraint_file),
        "action":       ("Generate an ActionView .sysmld",            action_file),
        "interaction":  ("Generate an InteractionView .sysmld",       sequence_file),
        "usecase":      ("Generate a UseCaseView .sysmld",            usecase_file),
        "allocation":   ("Generate an AllocationView .sysmld",        allocation_file),
        "flow":         ("Generate a FlowView .sysmld",               flow_file),
        "analysis":     ("Generate an AnalysisCaseView .sysmld",      analysis_file),
        "verification": ("Generate a VerificationCaseView .sysmld",   verification_file),
        "interface":    ("Generate an InterfaceView .sysmld",         interface_file),
        "general":      ("Generate a GeneralView .sysmld",            general_file),
    }
    # Short aliases kept for backward compatibility
    view_aliases = {
        "req": "requirement",
    }
    for command, (help_text, _handler) in view_commands.items():
        view_parser = subparsers.add_parser(command, help=help_text)
        view_parser.add_argument("path", help="View intent JSON file")
        view_parser.add_argument("--output", "-o", help="Output .sysmld path")
    for alias, primary in view_aliases.items():
        help_text, _handler = view_commands[primary]
        view_parser = subparsers.add_parser(alias, help=f"Alias for sysmld {primary}")
        view_parser.add_argument("path", help="View intent JSON file")
        view_parser.add_argument("--output", "-o", help="Output .sysmld path")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("path")
    validate_parser.add_argument("--schema", action="store_true")
    validate_parser.add_argument("--strict", action="store_true")
    validate_parser.add_argument("--lint", action="store_true")

    render_parser = subparsers.add_parser("render")
    render_parser.add_argument("path")
    render_parser.add_argument("--svg", action="store_true", help="Render to SVG (default)")
    render_parser.add_argument("--png", action="store_true", help="Render to PNG (requires cairosvg)")
    render_parser.add_argument("--all", action="store_true", help="Render to both SVG and PNG")
    render_parser.add_argument("--scale", type=float, default=2.0, help="PNG scale factor (default: 2.0 for retina quality)")
    render_parser.add_argument("--output")
    render_parser.add_argument("--no-strict", action="store_true")

    args = parser.parse_args()

    if args.command == "graph":
        output = Path(args.output) if args.output else None
        svg_path, json_path = graph_file(Path(args.path), output,
                                         getattr(args, "direction", None))
        print(f"SVG:  {svg_path}")
        print(f"JSON: {json_path}")
        return 0

    if args.command in {"interconnection", "compose", "ibd"}:
        output = Path(args.output) if args.output else None
        input_path = Path(args.path)
        target = compose_file(input_path, output)
        print(target)
        if getattr(args, "graph", False):
            graph_output = Path(args.graph_output) if getattr(args, "graph_output", None) else None
            svg_path, json_path = graph_file(input_path, graph_output)
            print(f"SVG:  {svg_path}")
            print(f"JSON: {json_path}")
        return 0

    if args.command in {"definition", "bdd", "tree"}:
        output = Path(args.output) if args.output else None
        target = tree_file(Path(args.path), output)
        print(target)
        return 0

    if args.command in {"state", "stm"}:
        output = Path(args.output) if args.output else None
        target = stm_file(Path(args.path), output)
        print(target)
        return 0

    # Resolve alias to primary command name
    canonical = view_aliases.get(args.command, args.command)
    if canonical in view_commands:
        output = Path(args.output) if args.output else None
        target = view_commands[canonical][1](Path(args.path), output)
        print(target)
        return 0

    if args.command == "validate":
        report = validate_file(Path(args.path), strict=args.strict or args.lint, lint=args.lint)
        for finding in report.findings:
            print(f"{finding.severity.upper()} {finding.code}: {finding.message}")
        print(f"{report.errors} errors, {len(report.findings) - report.errors} warnings")
        return 1 if report.errors else 0

    if args.command == "render":
        do_svg = args.svg or args.all or (not args.png)
        do_png = args.png or args.all
        output = Path(args.output) if args.output else None
        strict = not args.no_strict
        if do_svg:
            target = render_svg(Path(args.path), output_path=output, strict=strict)
            print(target)
        if do_png:
            png_output = output.with_suffix(".png") if output else None
            target = render_png(Path(args.path), output_path=png_output, strict=strict, scale=args.scale)
            print(target)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
