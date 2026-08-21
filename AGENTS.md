# Agent notes for SysMLD

SysMLD is a **stdlib-only**, deterministic SysML v2 diagram toolkit. Same model + intent must always produce the same `.sysmld` / SVG. You are helping someone take this toolkit onto their own system — not lock them into a commercial suite.

## How to work here

1. **Python >= 3.11.** Core code stays in the standard library. Optional PNG via cairosvg is the only existing exception — do not add runtime dependencies.
2. **Determinism.** No clocks, randomness, or unordered hashes in layout or IDs. Use `_clean()` / `routing.clean()` for coordinates. `from __future__ import annotations` and full type hints.
3. **Schema wins.** `schemas/sysmld.schema.json` is the contract. Update `sysmld-specification.md` only when the format or schema changes.
4. **Do not invent view kinds.** There are exactly 15. See the table in [README.md](README.md) and [skills/compose-views/SKILL.md](skills/compose-views/SKILL.md).
5. **Hard routing rule:** connections must **never** pass over boxes (no edge through a node, label, or part rectangle). Route around obstacles. Hop-overs are only for **line-on-line** crossings — never as an excuse to clip a box. IBD is the highest visual priority; if docs/skills and routing collide, finish routing first.
6. **Vision review before calling a view done.** Tests passing is not enough. Open the SVG/PNG and look. Use [skills/vision-review/SKILL.md](skills/vision-review/SKILL.md).
7. **ElectricBike names are frozen.** Do not rename package `ElectricBike`, part defs/usages, stems under `examples/e-bike/`, or other ids in that example. Mr. SW MSML mirrors them. No old→new mapping.

## Typical loop

```text
.sysml  →  intent.json  →  sysmld <kind>  →  .sysmld  →  sysmld render / validate --strict
```

- New user project: [skills/bootstrap-project/SKILL.md](skills/bootstrap-project/SKILL.md) and [template/new-project/](template/new-project/).
- Write or edit textual SysML: [skills/author-model/SKILL.md](skills/author-model/SKILL.md).
- Intent JSON + composer command: [skills/compose-views/SKILL.md](skills/compose-views/SKILL.md).
- Visual / meaning QA: [skills/vision-review/SKILL.md](skills/vision-review/SKILL.md).

Copy `template/new-project/` for a greenfield model. Do not clone toaster as the starter. Stems match the MSML skill pack (`bootstrap-project`, `author-model`, `compose-views`, `vision-review`).

## Checks

```bash
python3 -m pytest
```

Prefer `python3`. Strict validate next to the `.sysml` (relative `model_files`).
