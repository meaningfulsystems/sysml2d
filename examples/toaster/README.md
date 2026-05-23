# Toaster Examples

This folder contains a complete toaster model and generated SysMLD views for the current view vocabulary.

## Primary Inputs

- `toaster.sysml` is the SysML v2 model.
- `*.json` files are deterministic composer intent files.
- `*.sysmld` files are generated diagram layout documents.
- `*.svg` files are rendered output.

## Common Commands

Regenerate the mechanical and electrical interconnection views:

```bash
sysmld interconnection examples/toaster/toaster-mech-composed.json
sysmld render          examples/toaster/toaster-mech-composed.sysmld

sysmld interconnection examples/toaster/toaster-electrical-icn.json
sysmld render          examples/toaster/toaster-electrical-icn.sysmld
```

Regenerate the definition tree and state machine:

```bash
sysmld definition examples/toaster/toaster-bdd.json
sysmld render     examples/toaster/toaster-bdd.sysmld

sysmld state  examples/toaster/toaster-stm.json
sysmld render examples/toaster/toaster-stm.sysmld
```

Regenerate specialized views with the matching command:

```bash
sysmld requirement   examples/toaster/toaster-req.json
sysmld constraint    examples/toaster/toaster-cst.json
sysmld action        examples/toaster/toaster-act.json
sysmld interaction   examples/toaster/toaster-int.json
sysmld usecase       examples/toaster/toaster-uc.json
sysmld allocation    examples/toaster/toaster-alloc.json
sysmld flow          examples/toaster/toaster-flow.json
sysmld analysis      examples/toaster/toaster-acase.json
sysmld verification  examples/toaster/toaster-vcase.json
sysmld interface     examples/toaster/toaster-intf.json
sysmld general       examples/toaster/toaster-general.json
```

Add `--graph` to an interconnection command to write optional topology sidecars:

```bash
sysmld interconnection examples/toaster/toaster-electrical-icn.json --graph
```

## Manual References

The `manual/` folder keeps hand-tuned SysMLD/SVG diagrams for reference. The intended workflows are direct composition, manual SysMLD authoring, or composing first and then editing the generated SysMLD.
