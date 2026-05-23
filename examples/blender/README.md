# Blender Examples

This folder contains a complete blender model and generated SysMLD views for the current view vocabulary.

## Primary Inputs

- `blender.sysml` is the SysML v2 model.
- `*.json` files are deterministic composer intent files.
- `*.sysmld` files are generated diagram layout documents.
- `*.svg` files are rendered output.

## Common Commands

Regenerate the interconnection, definition tree, and state machine:

```bash
sysmld interconnection examples/blender/blender-ibd-composed.json
sysmld render          examples/blender/blender-ibd-composed.sysmld

sysmld definition examples/blender/blender-bdd.json
sysmld render     examples/blender/blender-bdd.sysmld

sysmld state  examples/blender/blender-stm.json
sysmld render examples/blender/blender-stm.sysmld
```

Regenerate specialized views with the matching command:

```bash
sysmld package       examples/blender/blender-pkg.json
sysmld requirement   examples/blender/blender-req.json
sysmld constraint    examples/blender/blender-cst.json
sysmld action        examples/blender/blender-act.json
sysmld interaction   examples/blender/blender-int.json
sysmld usecase       examples/blender/blender-uc.json
sysmld allocation    examples/blender/blender-alloc.json
sysmld flow          examples/blender/blender-flow.json
sysmld analysis      examples/blender/blender-acase.json
sysmld verification  examples/blender/blender-vcase.json
sysmld interface     examples/blender/blender-intf.json
sysmld general       examples/blender/blender-general.json
```

Generated `.sysmld` and `.svg` files live at the example root. Intent `.json` files are the deterministic source inputs.
