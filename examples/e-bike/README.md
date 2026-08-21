# Electric Bike

Architecture: [e-bike-architecture-summary.md](e-bike-architecture-summary.md).

Street-legal EPAC (EN 15194): cadence PAS, no certified throttle, 25 km/h cutoff, walk assist ≤ 6 km/h. Rear geared hub, no regeneration. **250 W is the EU continuous rating.** **40 N·m is hub peak torque, not continuous** — it does not sit with 250 W at 25 km/h as a continuous operating point. Charge path is charger → BMS → pack.

- `e-bike.sysml` is the SysML v2 model.
- `*.json` files are deterministic composer intent files.
- `*.sysmld` files are generated diagram layouts.
- `*.svg` files are rendered output.

Bindings used in the views:

- Tour 60 km uses `usableWh` (500 Wh) and `energyPerKm` (~8.3 Wh/km), not Eco / PAS-1.
- 50 ms brake inhibit is a separate electronic design target from either lever. EN 15194:2017 clause 4.2.13 Power management is motor-assist cut-off after pedaling stops (2 m; brake lever switches only relax that to 5 m), not vehicle brake distance. That clause allocates to the controller and sensors, not `brakeSystem`.
- Charge safety is allocated to `BatteryPack::bms`.
- Ride safety and assist limit allocate to brakes, controller, cadence sensor, wheel-speed sensor, and BMS. Cadence alone cannot enforce 25 km/h.
- Lighting is StVZO / ISO 6742, not UN ECE R113.
- RideControl `walk` is `do / ≤ 6 km/h`. Fault reset returns to Off. Charging is entered only from Off.
- `energyBalance` is pack energy only. Rider watts use `riderInputBalance`.
- Ports live on child parts. The parent interconnection view connects those ports.

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
