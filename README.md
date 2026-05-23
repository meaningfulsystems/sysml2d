# SysMLD

SysMLD is a lightweight diagram/view format and deterministic rendering toolkit for [SysML v2](https://www.omg.org/spec/SysML) models.

## The Most Advanced System Modeling Language, Made Accessible

SysML v2 is the most powerful systems modeling language ever standardized. Developed by the Object Management Group with input from NASA, Boeing, Airbus, NIST, and leading defense and aerospace organizations, it defines a precise, formally grounded language for describing the structure, behavior, requirements, constraints, interfaces, allocations, and flows of complex engineered systems. It has a rigorous abstract syntax, a clean textual notation, and a graphical notation covering 15 diagram types. It handles everything from simple block diagrams to executable parametric models and formal verification cases.

The problem has never been the language. The problem has been the tooling.

Most SysML v2 tools require a commercial license, run a proprietary model server, store models in a binary or opaque format, and keep diagrams locked inside a desktop application. That is a barrier for smaller teams, for open-source projects, for organizations that need to share models across tool boundaries, and for AI agents that cannot open a GUI.

SysMLD is built on a different premise: **the full power of SysML v2, in plain text files, version-controlled alongside everything else.**

## Human-AI Collaboration on System Models

Traditional MBSE tools lock your models and diagrams inside proprietary formats. That makes it hard to review changes, impossible to diff meaningfully, and difficult for AI agents to help — because they cannot read, write, or reason about what they cannot see as text.

SysMLD is built around a different premise: **everything is text, everything is versioned, and everything is readable by both humans and AI.**

```
your-system/
  model.sysml          ← SysML v2 model — text, diffable, reviewable
  ibd-intent.json      ← compact diagram request — 30 lines, AI-writable
  ibd.sysmld           ← generated layout — explicit, stable, versioned
  ibd.svg              ← rendered output — reviewable in any browser or PR
```

Every file in this pipeline is plain text stored in a normal git repository. That has real consequences:

**Pull requests become meaningful.** When a system engineer adds a new subsystem, the diff shows exactly which model elements changed and which diagram layouts were updated. Reviewers can see the intent, the layout, and the rendering all in one PR — without opening a separate tool.

**AI agents can do real work on your models.** An AI can read a `.sysml` file, understand the architecture, propose changes, generate a diagram intent file, and commit everything in a single session. The model and its views stay in sync because they live in the same repository and the composer is deterministic — the same intent always produces the same layout.

**Diagrams never go stale.** Because layouts are generated from intent files, regenerating all diagrams for a project is a single script. Update the model, run the composers, commit. No manual diagram redrawing, no out-of-date screenshots in the documentation folder.

**The whole team can contribute.** Systems engineers write `.sysml`. Product managers review SVG diagrams in a browser. AI agents draft models and intent files. All of it version-controlled together, with no tool installation required to view the results.

**Open source means the workflow is yours.** SysMLD is a pure Python library with no external dependencies beyond the standard library (PNG export optionally uses cairosvg). You can run it in CI, in a container, on a developer laptop, or inside an AI agent's tool environment. The format is documented, the schema is published, and everything is forkable and extensible.

**The modeler stays in control.** The SysML v2 standard includes a REST API for model interchange, and commercial repositories expose models through that API layer. That approach works well for large enterprise tool ecosystems — but it also means your model lives on a server, accessed through an API, managed by a platform. SysMLD takes the opposite position: the model is a file you own, stored where you choose, versioned how you choose, and readable without any running service. There are no API keys to manage, no repository subscriptions, and no dependency on a vendor's uptime. The `.sysml` textual notation is the interoperability layer — any tool that speaks SysML v2 text can read it, and any tool that produces SysML v2 text can feed into SysMLD's composers and validators. You get the benefits of a standard without giving up ownership of your own work.

This is the core idea that inspired the [MSML project](https://github.com/meaningfulsystems/msml) and drove the design of SysMLD: when models, diagrams, and their history live together as text in a repository, human-AI collaboration on systems engineering becomes a natural workflow rather than a workaround.

---

- `.sysml` files hold SysML v2 model content.
- `.json` intent files describe compact view requests for the composers.
- `.sysmld` files hold explicit diagram layout and rendering instructions.
- `.svg` files are generated renderings — commit them, share them, embed them in documentation.

## Examples

**Blender internal block diagram** — generated by `sysmld interconnection`:

![Blender Internal Block Diagram](examples/blender/blender-ibd-composed.svg)

**Toaster control state machine** — generated by `sysmld state`:

![Toaster Control State Machine](examples/toaster/toaster-stm.svg)

See the full [toaster](examples/toaster) and [blender](examples/blender) example sets for all 15 supported view types.

## Quick Start

```bash
git clone https://github.com/meaningfulsystems/sysml2d.git
cd sysml2d
python -m pip install -e .
```

Then see [QUICKSTART.md](QUICKSTART.md) for a step-by-step guide to creating your first model and diagram.

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

**Notation note:** Views marked ✅ produce diagrams that closely follow the SysML v2 OMG graphical notation specification. Views marked ⚠️ produce pragmatic overview diagrams that correctly reference SysML v2 model elements but use simplified relationship notation.

The composers are deterministic. Given the same model and intent file, they always produce the same `.sysmld` output.

**Backward-compatible aliases:** `sysmld compose` (→ `interconnection`), `sysmld bdd` / `sysmld tree` (→ `definition`), `sysmld stm` (→ `state`), `sysmld req` (→ `requirement`) are all still accepted.

## Install

Requires Python 3.11 or newer.

```bash
pip install -e .
```

## Command Line

```bash
sysmld interconnection examples/toaster/toaster-mech-composed.json
sysmld definition      examples/toaster/toaster-bdd.json
sysmld state           examples/toaster/toaster-stm.json
sysmld requirement     examples/toaster/toaster-req.json
sysmld action          examples/toaster/toaster-act.json
sysmld render          examples/toaster/toaster-mech-composed.sysmld
sysmld validate        examples/toaster/toaster-mech-composed.sysmld --strict
```

Add `--graph` to see the crossing-minimized topology before full layout:

```bash
sysmld interconnection examples/toaster/toaster-mech-composed.json --graph
```

PNG output is also supported (requires `pip install cairosvg`):

```bash
sysmld render examples/toaster/toaster-stm.sysmld --png        # PNG only
sysmld render examples/toaster/toaster-stm.sysmld --all        # SVG + PNG
sysmld render examples/toaster/toaster-stm.sysmld --png --scale 3.0  # higher resolution
```

## Repository Layout

```text
src/sysmld/              Python package — view composers, layout engine, renderer, validator
schemas/                 SysMLD JSON Schema (authoritative for .sysmld document shape)
examples/toaster/        Toaster appliance model and all diagram examples
examples/blender/        Blender appliance model and all diagram examples
skills/                  Prompt templates for AI-assisted modeling
tests/                   Unit and regression tests (66 tests)
sysmld-specification.md  Human-readable SysMLD specification
QUICKSTART.md            Step-by-step guide for new users
```

## Development

```bash
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code conventions, and pull request guidelines.

## License

SysMLD is released under the MIT License. See [LICENSE](LICENSE).
