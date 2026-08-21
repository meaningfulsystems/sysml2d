# Electric Bike Examples

EPAC (EN 15194) street-legal class: cadence PAS, no certified throttle, 25 km/h cutoff. Rear geared hub (no regen). BMS lives inside the battery pack (UL 2849).

- `e-bike.sysml` is the SysML v2 model. ElectricBike qualified names are frozen.
- `*.json` files are deterministic composer intent files.
- `*.sysmld` files are generated diagram layouts.
- `*.svg` files are rendered output.

Review bindings (do not treat a first-diagram slogan as truth):

- Tour 60 km binds `usableWh` (500 Wh) and `energyPerKm` (~8.3 Wh/km), not Eco / PAS-1.
- 50 ms brake inhibit is the electronic order. EN 15194 also carries the 5 m / 2 m distance cutoff.
- `allocateChargeToBms` targets `BatteryPack::bms`, not the pack box.
- Ride safety allocates to brakes, controller, cadenceSensor, wheelSpeedSensor, and BMS. Assist Limit also allocates to wheelSpeedSensor — cadence-only cannot enforce 25 km/h.
- `lockBikeUseCase` is deleted (commercial, not EN 15194).
- Lighting is StVZO / ISO 6742, not UN ECE R113.
- RideControl state `walk` (`do / <= 6 km/h`) is a real EPAC feature, not a throttle. `resetFault` is Fault→Off (not Standby). Charging is Off→Charging only. RiderInterface carries `PedalCadence` and `WalkAssistCommand`. `ThrottleCommand` remains unused.
- `energyBalance` binds pack energy only. Rider watts are a different source (`riderInputBalance`).
- Ports live on the child parts (`frame`, `batteryPack`, `motorController`, `hubMotor`, `humanInterface`, `brakeSystem`, `bms`). The parent IBD connects those child ports.

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
