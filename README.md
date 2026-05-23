# SysMLD

SysMLD is a lightweight diagram/view format and deterministic rendering toolkit for SysML v2 models.

**Why SysMLD?** Most MBSE tools bundle model semantics and diagram layout together, making it hard to keep diagrams in sync with models or to generate diagrams automatically. SysMLD separates the two: a `.sysml` file holds the model, and a `.sysmld` file holds the diagram layout. Composers generate the layout deterministically from a compact JSON intent file — the same inputs always produce the same diagram.

- `.sysml` files hold SysML v2 model content.
- `.json` intent files describe compact view requests for the composers.
- `.sysmld` files hold explicit diagram layout and rendering instructions.
- `.svg` files are generated renderings.

## Quick Start

**1. Write a SysML v2 model** (or use an existing one):

```sysml
package Toaster {
    part def Toaster {
        part lever : Lever;
        part heater : HeatingElement;
        connection leverToHeater connect lever to heater;
    }
    part def Lever;
    part def HeatingElement;
}
```

**2. Write a compact intent file** describing what diagram you want:

```json
{
  "diagram": "toaster-ibd",
  "kind": "InterconnectionView",
  "name": "Toaster Internals",
  "subject": "toaster",
  "model_files": ["toaster.sysml"],
  "direction": "left-right",
  "nodes": {
    "lever":  { "label": "Lever",          "style": "part.mechanical" },
    "heater": { "label": "Heating Element", "style": "part.thermal" }
  },
  "edges": [
    { "from": "lever", "to": "heater", "label": "control" }
  ]
}
```

**3. Compose and render:**

```bash
sysmld interconnection toaster-intent.json
sysmld render toaster-ibd.sysmld
```

This produces `toaster-ibd.svg` — a validated, model-backed diagram with stable element IDs and repeatable layout.

See [examples/toaster](examples/toaster) and [examples/blender](examples/blender) for complete working examples covering all 15 supported view types.

## Supported Views

SysMLD supports these SysML v2 view kinds:

| View kind | Code | Composer command | Notation |
| --- | --- | --- | --- |
| `DefinitionView` | `def` | `sysmld definition` | ✅ Close to SysML v2 standard |
| `InterconnectionView` | `icn` | `sysmld interconnection` | ✅ Close to SysML v2 standard |
| `StateView` | `stv` | `sysmld state` | ✅ Close to SysML v2 standard |
| `ActionView` | `act` | `sysmld action` | ✅ Close to SysML v2 standard |
| `InteractionView` | `int` | `sysmld interaction` | ✅ Close to SysML v2 standard |
| `UseCaseView` | `uc` | `sysmld usecase` | ✅ Close to SysML v2 standard |
| `PackageView` | `pkg` | `sysmld package` | ⚠️ Pragmatic overview diagram |
| `RequirementView` | `req` | `sysmld requirement` | ⚠️ Pragmatic overview diagram |
| `ConstraintView` | `cst` | `sysmld constraint` | ⚠️ Pragmatic overview diagram |
| `AllocationView` | `alloc` | `sysmld allocation` | ⚠️ Pragmatic overview diagram |
| `FlowView` | `flow` | `sysmld flow` | ⚠️ Pragmatic overview diagram |
| `AnalysisCaseView` | `acase` | `sysmld analysis` | ⚠️ Pragmatic overview diagram |
| `VerificationCaseView` | `vcase` | `sysmld verification` | ⚠️ Pragmatic overview diagram |
| `InterfaceView` | `intf` | `sysmld interface` | ⚠️ Pragmatic overview diagram |
| `GeneralView` | `gen` | `sysmld general` | ⚠️ User-defined |

**Notation note:** Views marked ✅ produce diagrams that closely follow the SysML v2 OMG graphical notation specification. Views marked ⚠️ produce pragmatic overview diagrams that correctly reference SysML v2 model elements but use simplified relationship notation. They are suitable for documentation and model understanding but are not strict OMG graphical notation implementations.

The composers are deterministic. Given the same model and intent file, they always produce the same `.sysmld` output.

**Backward-compatible aliases:** `sysmld compose` (→ `interconnection`), `sysmld bdd` / `sysmld tree` (→ `definition`), `sysmld stm` (→ `state`), `sysmld req` (→ `requirement`), `sysmld ibd` (→ `interconnection`) are all still accepted.

## Install

Requires Python 3.11 or newer.

```bash
python -m pip install -e .
```

For development, install the test runner:

```bash
python -m pip install pytest
```

## Command Line

Generate a `.sysmld` diagram from an intent file:

```bash
sysmld interconnection examples/toaster/toaster-mech-composed.json
sysmld definition      examples/toaster/toaster-bdd.json
sysmld state           examples/toaster/toaster-stm.json
sysmld requirement     examples/toaster/toaster-req.json
sysmld action          examples/toaster/toaster-act.json
```

Render a `.sysmld` file to SVG:

```bash
sysmld render examples/toaster/toaster-mech-composed.sysmld
```

Validate a `.sysmld` file:

```bash
sysmld validate examples/toaster/toaster-mech-composed.sysmld --strict
```

Show the crossing-minimized topology graph for an interconnection intent file:

```bash
sysmld interconnection examples/toaster/toaster-mech-composed.json --graph
```

**Note:** SVG is the primary output format in v0.1. PNG rendering is not yet implemented.

## Examples

The [examples/toaster](examples/toaster) and [examples/blender](examples/blender) folders contain complete model-backed example sets covering all 15 view types:

- SysML v2 model files (`.sysml`)
- Compact composer intent files (`.json`)
- Generated diagram layout files (`.sysmld`)
- Rendered SVG diagrams (`.svg`)
- Hand-tuned manual reference diagrams under `manual/`

## Repository Layout

```text
src/sysmld/              Python package — view composers, layout engine, renderer, validator
schemas/                 SysMLD JSON Schema (authoritative for .sysmld document shape)
examples/toaster/        Toaster appliance model and all diagram examples
examples/blender/        Blender appliance model and all diagram examples
tests/                   Unit and regression tests (66 tests)
sysmld-specification.md  Human-readable SysMLD specification
```

## Development

Run the tests before submitting changes:

```bash
pytest
```

The tests cover schema validation, strict model-reference validation, CLI command coverage, deterministic layout behavior, renderer symbols, and regression coverage for all toaster and blender examples.

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code conventions, and pull request guidelines.

## License

SysMLD is released under the MIT License. See [LICENSE](LICENSE).
