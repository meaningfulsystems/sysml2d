# Contributing to SysMLD

Thank you for your interest in contributing. This document covers development setup, code conventions, and how to submit changes.

## Development Setup

Requires Python 3.11 or newer.

```bash
git clone https://github.com/meaningfulsystems/sysml2d
cd sysml2d
python -m pip install -e .
python -m pip install pytest
pytest
```

All 66 tests should pass on a clean checkout.

## Project Structure

```text
src/sysmld/
  layout.py                Shared Sugiyama layout engine (used by all composers)
  views.py                 Generic shared view layout engine (called by thin wrappers)
  interconnection_view.py  InterconnectionView (IBD) composer
  definition_view.py       DefinitionView (BDD) tree composer
  state_view.py            StateView state machine composer
  requirement_view.py      RequirementView composer (custom tree layout)
  action_view.py           ActionView composer
  interaction_view.py      InteractionView sequence diagram composer
  use_case_view.py         UseCaseView composer
  case_view.py             AnalysisCaseView + VerificationCaseView composers
  package_view.py          PackageView composer
  constraint_view.py       ConstraintView composer
  allocation_view.py       AllocationView composer
  flow_view.py             FlowView composer
  interface_view.py        InterfaceView composer
  general_view.py          GeneralView composer
  graph.py                 Topology-only SVG debug output (sysmld graph)
  render_svg.py            SVG renderer (all symbol types)
  scene.py                 Scene graph (intermediate between .sysmld and renderer)
  validate.py              Schema and strict model-reference validation
  cli.py                   Command-line entry points
  io.py                    JSON I/O and path resolution
  model_index.py           Minimal SysML textual reference scanner

tests/
  test_interconnection_view.py  InterconnectionView composer tests
  test_definition_view.py       DefinitionView tree composer tests
  test_state_view.py            StateView state machine composer tests
  test_action_view.py           ActionView composer tests
  test_requirement_view.py      RequirementView composer tests
  test_layout.py                Shared layout engine tests
  test_render_svg.py            SVG renderer tests
  test_validate.py              Validator tests
  test_cli.py                   CLI command coverage tests
```

Each view type has a dedicated `*_view.py` module in `src/sysmld/` and a corresponding `test_*_view.py` in `tests/`. Thin wrappers (most views) call `views.py`. Full composers (`interconnection_view.py`, `state_view.py`, `definition_view.py`, `requirement_view.py`) contain view-specific layout logic.

## Adding a New View Type

1. Add the view kind name to `VIEW_KINDS` in `validate.py`.
2. Add the view kind to the symbol enum in `schemas/sysmld.schema.json` if new symbols are needed.
3. Add default styles for new symbols in `scene.py` `DEFAULT_STYLES`.
4. Add rendering for new symbols in `render_svg.py` `_element()`.
5. Create `src/sysmld/my_view.py` (use the full view type name, snake_case, with `_view` suffix):
   ```python
   from pathlib import Path
   from .views import view_file
   def my_view_file(input_path: Path, output_path: Path | None = None) -> Path:
       return view_file(input_path, output_path, kind="MyView", default_symbol="my_symbol")
   ```
6. Import and register the command in `cli.py`.
7. Add `tests/test_my_view.py` with at least one test.

## Code Conventions

- **No external dependencies** beyond the Python standard library for the core package. The renderer, composer, layout engine, and validator are all pure Python.
- **Determinism first.** Every composer must produce identical output for identical inputs. No random seeds, no timestamp-based identifiers, no floating-point non-determinism in layout.
- **File naming.** View-specific Python modules use the pattern `{view_type}_view.py` (e.g., `state_view.py`, `interconnection_view.py`). Test files mirror this: `test_{view_type}_view.py`.
- **No comments** except for non-obvious constraints or workarounds. Well-named identifiers should be self-documenting.
- **Types.** Use `from __future__ import annotations` and type hints throughout. Functions must be typed.
- **`_clean(value)`** in `views.py` rounds floats to clean integers/decimals for readable JSON output. Use it for all coordinate values going into `.sysmld`.

## Running Tests

```bash
pytest                                        # all tests
pytest tests/test_state_view.py              # state machine view tests
pytest tests/test_interconnection_view.py    # interconnection view tests
pytest -k "interconnection"                 # by keyword
```

The test suite includes:
- Schema validation and strict model-reference validation
- CLI command smoke tests (all commands produce valid output)
- Deterministic layout (same input → same output)
- Renderer symbol coverage
- Regression tests for toaster and blender examples

## Pull Requests

- Run `pytest` locally before submitting. All tests must pass.
- Keep changes focused. Fix one thing per PR.
- If you add a new view type or symbol, include at least one example file.
- If you change the `.sysmld` format or JSON schema, update `sysmld-specification.md` to match.
- The JSON schema in `schemas/sysmld.schema.json` is the authoritative contract. If the spec and schema conflict, the schema wins.

## Reporting Issues

Open a GitHub issue with:
- The `.json` intent file or `.sysmld` file that triggers the problem
- The command you ran
- The actual output vs. expected output
- Your Python version and operating system
