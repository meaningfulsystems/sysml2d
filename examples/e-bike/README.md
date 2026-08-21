# Electric Bike Examples

A street-legal class e-bike: frame, battery pack, motor controller, hub motor, rider interface, and brakes.

- `e-bike.sysml` is the SysML v2 model.
- `*.json` files are deterministic composer intent files.
- `*.sysmld` files are generated diagram layouts.
- `*.svg` files are rendered output.

```bash
sysmld definition      examples/e-bike/e-bike-bdd.json
sysmld interconnection examples/e-bike/e-bike-ibd.json
sysmld state           examples/e-bike/e-bike-stm.json
sysmld action          examples/e-bike/e-bike-act.json
sysmld interaction     examples/e-bike/e-bike-int.json
sysmld usecase         examples/e-bike/e-bike-uc.json
sysmld package         examples/e-bike/e-bike-pkg.json
sysmld requirement     examples/e-bike/e-bike-req.json
sysmld constraint      examples/e-bike/e-bike-cst.json
sysmld allocation      examples/e-bike/e-bike-alloc.json
sysmld flow            examples/e-bike/e-bike-flow.json
sysmld analysis        examples/e-bike/e-bike-acase.json
sysmld verification    examples/e-bike/e-bike-vcase.json
sysmld interface       examples/e-bike/e-bike-intf.json
sysmld general         examples/e-bike/e-bike-general.json
sysmld general         examples/e-bike/e-bike-context.json
```
