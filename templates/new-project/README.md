# New project starter

Copy this folder onto your own project. Rename the `StarterSystem` package, aliases, and file stems. Do not clone toaster or e-bike as the starter. This is a **SysML2d** starter (`.sysml` / `.sysmld` / SVG). Do not mix in `.msml` files — that is the paired MSML toolchain.

Requires Python 3.11+ and SysMLD installed (`pip install -e .` from the SysMLD repo, or `PYTHONPATH=src`).

```bash
sysmld interconnection starter-ibd.json
sysmld state           starter-stm.json
sysmld render          starter-ibd.sysmld
sysmld render          starter-stm.sysmld
sysmld validate        starter-ibd.sysmld --strict
sysmld validate        starter-stm.sysmld --strict
```

Open the SVGs. An IBD is not done if any connector crosses a box.

Agent path: [AGENTS.md](../../AGENTS.md) and the four skills (`bootstrap-project`, `author-model`, `compose-views`, `vision-review`) under [skills/](../../skills/).
