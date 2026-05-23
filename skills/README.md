# SysMLD Skills

This folder contains reusable prompt templates for generating SysMLD content with AI assistance. Each file is a self-contained prompt that can be used with Claude, ChatGPT, or any other LLM.

## Skills

| File | Purpose |
|---|---|
| [new-model.md](new-model.md) | Generate a `.sysml` model from a system description |
| [new-interconnection.md](new-interconnection.md) | Generate an IBD intent JSON from a `.sysml` model |
| [new-state-machine.md](new-state-machine.md) | Generate a state machine intent JSON from a `.sysml` model |
| [new-requirement-view.md](new-requirement-view.md) | Generate a requirement view intent JSON from a `.sysml` model |

## How to Use

Copy the contents of a skill file and paste it into your AI conversation. Replace the `[SYSTEM DESCRIPTION]` or `[SYSML MODEL]` placeholder with your actual content. The skill file provides the context and format constraints the AI needs to produce valid SysMLD output.
