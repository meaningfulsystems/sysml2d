---
name: bootstrap-project
description: Start a new user project from the starter template — folder layout, first .sysml, first IBD+STM intents, and compose/render/validate commands.
---

# Bootstrap a new SysMLD system

Use this when someone wants **their own** system, not a fork of toaster/blender/e-bike.

## Copy the starter

```bash
cp -R template/new-project/ ../my-system
cd ../my-system
```

From a checkout of this repo you can also keep the folder inside the repo while renaming the package.

Starter contents:

| File | Role |
| --- | --- |
| `README.md` | Local commands |
| `starter.sysml` | SysML v2 stub (`StarterSystem`) |
| `starter-ibd.json` | InterconnectionView intent |
| `starter-stm.json` | StateView intent |

## Rename before it ships

1. Change the top-level `package` and `part def` in `starter.sysml`.
2. Update every qualified name in `aliases` (`Package::Def::member`).
3. Rename file stems if you want (`starter-*` → `pump-*`, etc.).
4. Keep `model_files` pointing at the `.sysml` next to the intent (relative paths).

Do **not** copy ElectricBike ids. That example is frozen for MSML.

## First commands

Requires Python 3.11+ and `pip install -e .` from the SysMLD repo (or `PYTHONPATH=src`).

```bash
sysmld interconnection starter-ibd.json
sysmld state           starter-stm.json
sysmld render          starter-ibd.sysmld
sysmld render          starter-stm.sysmld
sysmld validate        starter-ibd.sysmld --strict
sysmld validate        starter-stm.sysmld --strict
```

Open the SVGs. Do not call IBD done if any connector crosses a box.

## Next

- Grow the `.sysml` with [author-model](../author-model/SKILL.md).
- Add more view kinds with [compose-views](../compose-views/SKILL.md).
- QA with [vision-review](../vision-review/SKILL.md).

One-shot prompt leftovers (not per-view agent files): [new-model.md](../new-model.md), [new-interconnection.md](../new-interconnection.md), [new-state-machine.md](../new-state-machine.md).
