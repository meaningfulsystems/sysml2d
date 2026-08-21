---
name: compose-views
description: Write intent JSON and run the matching sysmld command for any of the 15 view kinds. Use when adding or regenerating a diagram from a model.
---

# Compose SysMLD views

Do **not** add a skill per view kind. One intent JSON + one command per diagram.

```text
intent.json  →  sysmld <command> intent.json  →  diagram.sysmld  →  sysmld render / validate --strict
```

`model_files` are relative to the intent. Compose and validate **next to** the `.sysml`.

## Commands (all 15)

| Kind | Command | Aliases | Example intent |
| --- | --- | --- | --- |
| `DefinitionView` | `sysmld definition` | `bdd`, `tree` | `examples/e-bike/e-bike-bdd.json` |
| `InterconnectionView` | `sysmld interconnection` | `compose`, `ibd` | `examples/e-bike/e-bike-ibd.json`, `template/new-project/starter-ibd.json` |
| `StateView` | `sysmld state` | `stm` | `examples/e-bike/e-bike-stm.json`, `template/new-project/starter-stm.json` |
| `ActionView` | `sysmld action` | | `examples/e-bike/e-bike-act.json` |
| `InteractionView` | `sysmld interaction` | | `examples/e-bike/e-bike-int.json` |
| `UseCaseView` | `sysmld usecase` | | `examples/e-bike/e-bike-uc.json` |
| `PackageView` | `sysmld package` | | `examples/e-bike/e-bike-pkg.json` |
| `RequirementView` | `sysmld requirement` | `req` | `examples/e-bike/e-bike-req.json` |
| `ConstraintView` | `sysmld constraint` | | `examples/e-bike/e-bike-cst.json` |
| `AllocationView` | `sysmld allocation` | | `examples/e-bike/e-bike-alloc.json` |
| `FlowView` | `sysmld flow` | | `examples/e-bike/e-bike-flow.json` |
| `AnalysisCaseView` | `sysmld analysis` | | `examples/e-bike/e-bike-acase.json` |
| `VerificationCaseView` | `sysmld verification` | | `examples/e-bike/e-bike-vcase.json` |
| `InterfaceView` | `sysmld interface` | | `examples/e-bike/e-bike-intf.json` |
| `GeneralView` | `sysmld general` | | `examples/e-bike/e-bike-general.json`, `e-bike-context.json` |

Toaster and blender under `examples/` show the same kinds on appliances.

## Intent JSON (every view)

```json
{
  "diagram": "my-ibd",
  "kind": "InterconnectionView",
  "name": "Human-readable title",
  "subject": "alias-or-name",
  "model_files": ["system.sysml"],
  "aliases": { "part": "Package::System::part" },
  "direction": "left-right"
}
```

Then view-specific keys: `nodes`/`edges` (most generic views), `states`/`transitions` (STM), `lifelines`/`messages` (interaction), `boundary_inputs` (IBD).

Rules:

- `"kind"` must be one of the 15 names above. Do not invent kinds.
- Every `model_ref` (and generated IBD port/connection id you care about) needs an `aliases` entry to a real SysML name.
- Orthogonal layout: `direction` is `left-right` | `right-left` | `top-down` | `bottom-up`.
- IBD: `nodes`, `edges`, optional `boundary_inputs`, optional `source_side` / `target_side` when a skip-rank mount must go around boxes.
- STM: `"initial": true` on the start node; do not mark a live loop state `final`.
- Requirement trees: only draw edges that are true (do not hang a child off the wrong parent).
- Package fan-out: one `contains` label on the parent drop is enough.

## After compose

```bash
sysmld render   my-ibd.sysmld
sysmld validate my-ibd.sysmld --strict
```

Then [vision-review](../vision-review/SKILL.md). IBD is not done if any connector crosses a box.

Focused one-shot prompts: [new-interconnection.md](../new-interconnection.md), [new-state-machine.md](../new-state-machine.md), [new-requirement-view.md](../new-requirement-view.md).
