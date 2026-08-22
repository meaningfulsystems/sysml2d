# Changelog

All notable changes to SysMLD are documented here.

## Unreleased

### Added

- Shared orthogonal autorouting helpers (`src/sysmld/routing.py`): unique channel tracks for adjacent-rank edges, outside rails for skip-rank edges, and renderer hop-overs as small half-circle arcs where later connections cross earlier ones
- `examples/e-bike/` — a street-legal class e-bike model with intents, `.sysmld`, and SVG for all 15 view kinds plus an operating-context general view
- Adoption pack: [AGENTS.md](AGENTS.md), four installable skills (`bootstrap-project`, `author-model`, `compose-views`, `vision-review`), and [templates/new-project/](templates/new-project/) (copy-this `.sysml` + IBD + STM)
- `examples/apollo/` — Apollo 11 / Block II (AS-506) whole-stack model: ground/crew, vehicles, two AGCs, AGS, IU LVDC, USB, mission + abort STMs. Sourced numbers only; UNKNOWN marked
- Apollo morning delta: SM three fuel cells; CM AgZn + charger + two 117 V 400 Hz inverters; LM six AgZn + ECA; AGS AEA/ASA/DEDA (TN-7990); CM probe / LM drogue / 12 latches; SM/LM RCS 100 lbf (PK p.93 / p.106), CM 93 lbf; loaded SM/CM RCS propellant mass UNKNOWN
- Apollo Press Kit p.109 tank loads filled; A11 ropes Comanche 055 + Luminary 1A LMY99/1; CMC ENTRY vs LGC LANDING split; SPS/DPS cited as PK vs TN conflicts. SPS loaded mass and CSM lunar Δv stay UNKNOWN

### Changed

- Shared router refuses any orthogonal path through a node or part rectangle; hop-overs stay line-on-line only. Interconnection views (e-bike, toaster, blender) detour around boxes
- State-machine long skip-rank returns can step off the top rail; interaction canvases no longer reserve a blank trailing message row
- Generic view routing now keeps fan-out/fan-in on separated tracks, snaps exclusive 1:1 pairs to a straight line, and places association rails outside system-boundary groups
- Crossing hop-overs are drawn at true interior crossings, including near route corners (still skipped at shared connection endpoints)
- Connection labels on generic, action, and requirement views sit beside the line instead of on the centerline
- Toaster, blender, and e-bike example artifacts regenerated from the composers
- README / CONTRIBUTING test counts updated for the new routing and e-bike coverage
- E-bike review: EPAC cadence PAS only (throttle removed from RideControl, HumanInterface, and RiderInterface), Tour-mode 500 Wh / 60 km bind, BMS inside BatteryPack, EN 15194 5 m / 2 m plus 50 ms inhibit, fail-silent allocated beyond brakes, `lockBikeUseCase` removed, rear geared hub (no regen), StVZO / ISO 6742 lighting
- E-bike addendum: RideControl state `walk` (≤ 6 km/h, not throttle); Tour binds `usableWh` + `energyPerKm`; energyBalance is pack-only; ports live on child parts only

## [0.1.0] — 2026-05-22

First public release.

### Added

- **15 SysML v2 view composers** — all deterministic, same inputs always produce identical output:
  - `sysmld interconnection` — InterconnectionView (IBD) with Sugiyama layout, non-overlapping orthogonal routing, and port placement
  - `sysmld definition` — DefinitionView (BDD) tree with configurable direction and depth
  - `sysmld state` — StateView state machine with forward transition routing, backward arc separation, and composite state support
  - `sysmld requirement` — RequirementView with custom hierarchy tree layout
  - `sysmld action` — ActionView activity diagrams with decision nodes and control flow
  - `sysmld interaction` — InteractionView sequence diagrams with lifelines and message arrows
  - `sysmld usecase` — UseCaseView with actor stick figures and ellipse use cases
  - `sysmld package` — PackageView namespace organization
  - `sysmld constraint` — ConstraintView parametric diagrams
  - `sysmld allocation` — AllocationView requirement-to-component allocations
  - `sysmld flow` — FlowView item and energy flows
  - `sysmld analysis` — AnalysisCaseView
  - `sysmld verification` — VerificationCaseView
  - `sysmld interface` — InterfaceView
  - `sysmld general` — GeneralView for mixed-element context diagrams
- **Topology debug graph** — `sysmld graph` and `sysmld interconnection --graph` write a crossing-minimized spider-web SVG and position JSON for layout debugging
- **SVG renderer** with 20+ symbol types: parts, ports, boundary boxes, state machine nodes, activity control nodes (decision diamond, fork/join bars, initial/final), actor stick figures, use case ellipses, lifelines, package tabs, and more
- **SysML v2 frame header** compliant with the OMG graphical notation: `[view.mode] name [usage : Type]`
- **Shared Sugiyama layout engine** used by all composers for crossing-minimized rank assignment and barycenter ordering
- **JSON Schema** (`schemas/sysmld.schema.json`) as the authoritative contract for `.sysmld` document shape
- **Strict model-reference validation** against `.sysml` source files (`sysmld validate --strict`)
- **Lint validation** mode for quality warnings
- **Complete toaster and blender appliance examples** across all 15 view types with full SysML v2 model files, intent files, generated `.sysmld`, and rendered `.svg`
- **Skills folder** with prompt templates for AI-assisted model and diagram generation
- **66 tests** covering all composers, validators, layout engine, and renderer

### Architecture

- `.sysml` / `.json` / `.sysmld` / `.svg` pipeline — model semantics and diagram layout are fully separated
- All view-specific modules follow the `*_view.py` naming convention (e.g. `interconnection_view.py`, `state_view.py`)
- CLI commands use full view type names as primary (`sysmld interconnection`, `sysmld definition`, `sysmld state`, `sysmld requirement`); short forms (`compose`, `bdd`, `stm`, `req`) accepted as aliases
- No external dependencies beyond the Python standard library
- Schema is the authoritative contract; specification Markdown explains intent
