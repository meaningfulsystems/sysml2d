# Agent notes for SysML2d

This repo is **SysML2d**, not MSML.

**SysML2d** is a stdlib-only, deterministic **SysML v2** diagram toolkit: `.sysml` + intent JSON + `.sysmld` + SVG. Same model + intent must always produce the same layout. This is the open-source replacement path for expensive tool-locked SysML 2 suites.

**[MSML](https://github.com/meaningfulsystems/msml)** is a paired, **SysML 1-inspired** language: `.msml` + `.msmd` + PNG. It shares the e-bike *names*, not the language. MSML is not SysML v2. Do not claim this repo is MSML.

A first-time systems engineer picks **one** toolchain per project. Do not mix `.sysml` and `.msml` in the same model.

Hero path: study [examples/e-bike/](examples/e-bike/), then start a new system with the four skills below. Do not clone toaster as the starter.

## How to work here

1. **Python >= 3.11.** Core code stays in the standard library. Optional PNG via cairosvg is the only existing exception — do not add runtime dependencies.
2. **Determinism.** No clocks, randomness, or unordered hashes in layout or IDs. Use `_clean()` / `routing.clean()` for coordinates. `from __future__ import annotations` and full type hints.
3. **Schema wins.** `schemas/sysmld.schema.json` is the contract. Update `sysmld-specification.md` only when the format or schema changes.
4. **Do not invent view kinds.** There are exactly 15. See the table in [README.md](README.md) and [skills/compose-views/SKILL.md](skills/compose-views/SKILL.md).
5. **Hard routing rule:** connections must **never** pass over boxes (no edge through a node, label, or part rectangle). Route around obstacles. Hop-overs are only for **line-on-line** crossings — never as an excuse to clip a box. IBD is the highest visual priority; if docs/skills and routing collide, finish routing first.
6. **Vision review before calling a view done.** Tests passing is not enough. Open the SVG/PNG and look. Use [skills/vision-review/SKILL.md](skills/vision-review/SKILL.md).
7. **ElectricBike names are frozen.** Do not rename package `ElectricBike`, part defs/usages, stems under `examples/e-bike/`, or other ids in that example. MSML mirrors those names. No old→new mapping.

## Typical loop

```text
.sysml  →  intent.json  →  sysmld <kind>  →  .sysmld  →  sysmld render / validate --strict
```

- New user project: [skills/bootstrap-project/SKILL.md](skills/bootstrap-project/SKILL.md) and [template/new-project/](template/new-project/).
- Write or edit textual SysML v2: [skills/author-model/SKILL.md](skills/author-model/SKILL.md).
- Intent JSON + composer command: [skills/compose-views/SKILL.md](skills/compose-views/SKILL.md).
- Visual / meaning QA: [skills/vision-review/SKILL.md](skills/vision-review/SKILL.md).

Copy `template/new-project/` for a greenfield model. Skill folder stems match MSML (`bootstrap-project`, `author-model`, `compose-views`, `vision-review`); language-specific bits (`.sysml`, `sysmld` CLI) stay in the skill body.

## Checks

```bash
python3 -m pytest
```

Prefer `python3`. Strict validate next to the `.sysml` (relative `model_files`).
