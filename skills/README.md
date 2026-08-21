# SysMLD Skills

Installable Cursor-style skills for taking SysML2d onto a new project. Stems match the MSML skill pack — **not** one file per view kind, and **no** `sysmld-` prefix. This repo is SysML v2 (`.sysml` / `.sysmld` / SVG). MSML is a different language (`.msml` / `.msmd` / PNG). Do not mix them.

| Skill | When to use it |
| --- | --- |
| [bootstrap-project](bootstrap-project/SKILL.md) | Start a new user project from [templates/new-project/](../templates/new-project/) |
| [author-model](author-model/SKILL.md) | Write or update SysML v2 textual models in this style |
| [compose-views](compose-views/SKILL.md) | Write intent JSON and run the right `sysmld` command (all 15 kinds) |
| [vision-review](vision-review/SKILL.md) | Vision QA: no line through a box, hop-overs only for line crossings, meaning checks |

Repo working rules for agents: [AGENTS.md](../AGENTS.md). Language-specific bits (`.sysml`, `sysmld` CLI) stay in the skill body.

## One-shot leftovers

These `.md` files are paste-in prompts, not per-view agent files. Prefer the four skills above.

| File | Purpose |
| --- | --- |
| [new-model.md](new-model.md) | Generate a `.sysml` model from a system description |
| [new-interconnection.md](new-interconnection.md) | Generate an IBD intent JSON from a `.sysml` model |
| [new-state-machine.md](new-state-machine.md) | Generate a state machine intent JSON from a `.sysml` model |
| [new-requirement-view.md](new-requirement-view.md) | Generate a requirement view intent JSON from a `.sysml` model |
