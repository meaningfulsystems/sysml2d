# Electric Bike Architecture

This document is the architecture and system-design description of the street-legal EPAC modeled in `e-bike.sysml`. A reviewer should be able to understand purpose, context, requirements, structure, interfaces, behavior, and allocations without opening the model. Generated views appear after the written architecture.

The bicycle is cadence PAS only: no certified throttle, assist cutoff at 25 km/h, walk assist at or below 6 km/h. The hub is rear geared with no regeneration. **250 W is the EU continuous rating (EN 15194), not peak power.** **40 N·m is hub peak torque, not continuous** — that torque does not sit with 250 W at 25 km/h as a continuous operating point. Charge energy enters the BMS, then the pack.

## 1. Purpose and Mission

The system is one Electrically Power Assisted Cycle (EPAC) class under EN 15194. Its mission is to assist a rider’s pedaling on the road within the legal continuous-power and speed limits, cut torque on brake input, and accept charge from an off-board charger through the pack BMS.

It is not a throttle bike, not a mid-drive kit, and not a regenerative hub. Tour-mode range is the only bound range scenario.

## 2. Operating Context

Rider, charger, and road are first-class external parts. They stay on the operating-context view. They are not decomposed inside the internal interconnection view.

| External part | Role | Context exchange |
|---------------|------|------------------|
| Rider | Commands the bike | `riderCommandFlow` |
| Charger | Off-board charge source | `chargeEnergyFlow` |
| Road | Tractive load | `roadLoadFlow` |

Boundary entries on the internal interconnection view (ports on children, not parent-owned externals):

- Rider → `humanInterface.riderIn`
- Charger → `batteryPack.bms.chargerIn`
- Road load → `hubMotor.roadLoadIn`

Port types: `RiderPort`, `ChargePort`, `MechanicalPort`, `PowerPort`, `DrivePort`, `ControlPort`.

## 3. Stakeholders and Use Cases

| Stakeholder | Associated use cases |
|-------------|----------------------|
| Rider | Ride Bike, Adjust Assist |
| Charger | Charge Bike only |

Ride Bike **includes** Adjust Assist. The charger is not associated with ride or assist.

**Analysis cases**

- Range analysis — `energyBalance` and the Tour binding against the range requirement.
- Tour-range analysis — `tourRangeBind` against the range requirement.
- Brake-latency analysis — `brakeLatencyLimit` against brake override.

**Verification cases**

- Verify range.
- Verify brake cutoff.
- Verify charge safety.
- Verify assist limit.

## 4. Requirements

IDs are from the requirement view; text and numbers are from the model.

| ID | Requirement | Quantitative target | Source in the model |
|----|-------------|---------------------|---------------------|
| REQ-E-001 | Ride safety — fail-silent torque cut. Brake, controller, cadence sensor, wheel-speed sensor, and BMS shall cut motor torque. Cadence-only cannot enforce 25 km/h | qualitative | EN 15194 EPAC safety (stated in the assist-limit family) |
| REQ-E-002 | Tour-mode range | **500 Wh** usable / **~8.3 Wh/km** ≥ **60 km**. Not Eco / PAS-1 | Tour scenario binding |
| REQ-E-003 | Assist limit — cadence PAS only, no certified throttle | Assist cut **25 km/h**; walk assist **≤ 6 km/h** | **EN 15194** |
| REQ-E-004 | Charge safety — stop on over-temperature, over-voltage, or charger disconnect. BMS opens the pack contactor | qualitative | **UL 2849** |
| REQ-E-010 | Electronic brake inhibit | **≤ 50 ms** from either lever (~10× tighter than the EN 15194 distance test) | design target vs EN 15194 distance test |
| REQ-E-011 | BMS opens the pack contactor before any cell exceeds voltage or temperature limits | qualitative | UL 2849 (via charge safety) |
| REQ-E-012 | Assistance ceases after pedaling stops | **5 m**, and **2 m** where that tighter clause applies | **EN 15194** |
| REQ-E-013 | Walk assist is not a throttle | **≤ 6 km/h** | **EN 15194** |
| REQ-E-014 | Continuous assist power | **250 W EU continuous** — distinct from hub peak torque **40 N·m** | **EN 15194** |
| REQ-E-020 | Display speed, assist level, and remaining range without removing hands from the bars | qualitative | not cited |
| REQ-E-030 | Frame carries rider, cargo, and battery loads without yielding | qualitative | not cited |
| REQ-E-040 | Lighting | **StVZO / ISO 6742**, not UN ECE R113 | **StVZO**, **ISO 6742** |

## 5. Structure

Six `ElectricBike` part usages are `frame`, `batteryPack`, `motorController`, `hubMotor`, `humanInterface`, and `brakeSystem`. The model also has `cadenceSensor`, `wheelSpeedSensor`, and a nested `batteryPack::bms`.

```
ElectricBike
├── frame
├── batteryPack
│   └── bms
├── motorController
├── hubMotor          continuousPower, wheelTorque
├── humanInterface    cadence PAS, walk assist, display; no throttle
├── brakeSystem
├── cadenceSensor
└── wheelSpeedSensor
```

`HubMotor` documentation: rear geared hub; regen none; EU continuous rating 250 W (EN 15194); hub peak torque 40 N·m — not continuous; 40 N·m does not sit with 250 W at 25 km/h as a continuous operating point.

`continuousPower` and `wheelTorque` are declared on the hub. Literal 250 W / 40 N·m values are in the documentation and view labels, not as SysML attribute bindings.

Lighting and a separate display part are not in the structure. Display is a function of `humanInterface`. `packEnergy` and `packVoltage` are declared without values.

## 6. Interfaces and Interconnections

Interfaces: rider (`PedalCadence`, `WalkAssistCommand`), charge (`ChargeEnergy`, `ElectricalEnergy`), drive (`WheelTorque`), brake (`BrakeInhibit`). `ThrottleCommand` is defined and unused — it is not on RideControl or HumanInterface.

**Charge path (only this path):** charger → `bms.chargerIn` (`chargerToBms`) → `bms.contactorOut` → `batteryPack.powerOut` (`bmsToPackPower`) → `motorController.powerIn`. The charger does not feed the pack and the BMS in parallel.

| Connection | From → to | Why |
|------------|-----------|-----|
| Frame mounts | frame → battery, hub, human interface, brakes | Mechanical location |
| Pack power | battery pack → controller | Traction energy after the BMS contactor |
| Phase drive | controller → hub | Assist torque |
| Assist command | human interface → controller | PAS / walk / display commands |
| Inhibit | brake system → controller | Fail-silent cut |
| Cadence | cadence sensor → controller `sensorIn` | Pedal presence |
| Wheel speed | wheel-speed sensor → controller `sensorIn` | 25 km/h cut — cadence cannot do this alone |
| Charge | charger → BMS → pack | UL 2849 charge safety |
| Road load | road → hub | Tractive load (context, not an internal actor) |

`frameToMotor` exists in the model. The interconnection view leaves the frame-to-hub mount off the drawing so frame mounts do not hop each other.

## 7. Behavior

### RideControl states

Initial state is Off.

| State | Notes |
|-------|-------|
| Off | Only state that may enter Charging |
| Standby | Powered, not assisting |
| Assist | Cadence PAS |
| walk | `do / speed <= 6 km/h` — EPAC walk assist, not a throttle |
| charging | Entered only from Off |
| fault | Reset returns to Off, not Standby |

| From | Trigger | To |
|------|---------|-----|
| Off | power button | Standby |
| Standby | cadence pedal | Assist |
| Assist | no pedal | Standby |
| Standby | walk button | walk |
| walk | walk release or brake | Standby |
| Assist | brake lever | Standby |
| Off | charger connected | charging |
| charging | charge full or charger removed | Off |
| Standby | power button | Off |
| Assist | overcurrent or cutout | fault |
| fault | reset | Off |

There is no charging transition from Standby. There is no overcurrent transition from Standby. There is no fault-to-Standby reset.

### Ride actions and interaction

Power on → select assist → pedal → apply brake → inhibit motor → deliver (or drop) torque. Plug-in and charge-stop are the charge path. The interaction lifeline for the hub is the rear geared hub.

## 8. Allocations

| Requirement | Allocated to |
|-------------|--------------|
| Ride safety | `brakeSystem`, `motorController`, `cadenceSensor`, **`wheelSpeedSensor`**, `bms` |
| Range | `batteryPack` |
| Assist limit | `motorController`, **`wheelSpeedSensor`** |
| Charge safety | `bms` |

Ride safety and assist limit both allocate to the wheel-speed sensor. Cadence-only cannot enforce 25 km/h.

## 9. Parameters, Constraints, and Scope

| Parameter | Value in the model |
|-----------|--------------------|
| Tour usable energy | 500 Wh |
| Tour energy per km | ~8.3 Wh/km |
| Tour range | ≥ 60 km |
| Assist cutoff | 25 km/h |
| Walk assist | ≤ 6 km/h |
| EU continuous power | 250 W |
| Hub peak torque | 40 N·m (not a continuous pair with 250 W at 25 km/h) |
| Electronic brake inhibit | ≤ 50 ms |
| EN 15194 distance cutoff | 5 m / 2 m |

`energyBalance` is pack electrical energy only. Rider pedal watts use `riderInputBalance`. Do not add rider watts to pack `usableWh`. `tourRangeBind` is `usableWh / energyPerKm` for Tour 60 km — not Eco / PAS-1.

Constraint names `rangeEstimate`, `assistPowerLimit`, `brakeLatencyLimit`, and `thermalDerate` have no formulas in the model.

**Out of scope:** throttle variants, mid-drive kits, regenerative hubs, UN ECE R113 lighting, Eco / PAS-1 range, charging from Standby, treating 40 N·m as continuous with 250 W at 25 km/h.

**Unmarked:** pack nameplate energy, pack voltage, lighting hardware, a separate display part. `ThrottleCommand` remains an unused item.

---

## Generated Views

The figures below are the generated SysMLD views for this model. They illustrate the architecture above; they do not replace it.

### Cases

Ride Bike, Adjust Assist, and Charge Bike. The rider associates with ride and assist only. The charger associates with charge only. Ride includes Adjust Assist.

![Electric Bike Use Cases](e-bike-uc.svg)

![Electric Bike Analysis Cases](e-bike-acase.svg)

![Electric Bike Verification Cases](e-bike-vcase.svg)

### Operating Context

The bike interacts with the rider, an off-board charger, and the road. Those externals stay on context, not inside the internal interconnection view.

![Electric Bike Operating Context](e-bike-context.svg)

### Requirements

Tour-mode 500 Wh / ~8.3 Wh/km for 60 km, 50 ms electronic brake inhibit plus the EN 15194 5 m / 2 m distance cutoff, 25 km/h assist cut, walk assist ≤ 6 km/h, EU continuous 250 W, StVZO / ISO 6742 lighting.

![Electric Bike Requirements](e-bike-req.svg)

### Hierarchical Structure

Frame, battery pack with nested BMS, motor controller, rear geared hub, human interface, brake system, cadence sensor, and wheel-speed sensor. The hub box states EU continuous 250 W and 40 N·m peak torque separately.

![Electric Bike Definition Tree](e-bike-bdd.svg)

### Interaction

Power-on through assist command, phase current to the rear geared hub, brake lever, inhibit, and torque-off.

![Electric Bike Interaction](e-bike-int.svg)

### State Behavior

RideControl starts in Off. Power goes to Standby; cadence starts Assist; the walk button starts walk (`do / ≤ 6 km/h`). Charging is entered only from Off. Fault is reached from Assist on overcurrent; reset returns to Off.

![Electric Bike Ride Control](e-bike-stm.svg)

### Action Behavior

Power-on, assist selection, pedaling, brake inhibit, torque delivery, plug-in, and charge stop.

![Electric Bike Ride Actions](e-bike-act.svg)

### Interconnection View

Child-part ports only. Charge arrives at the BMS, then the pack contactor. Cadence and wheel-speed sensors feed the controller. Connections do not pass over boxes.

![Electric Bike Interconnection](e-bike-ibd.svg)

### Interfaces and Flows

Rider, charge, drive, and brake interfaces. Flow is charger → BMS → pack → controller → hub → road, with rider command and brake inhibit on the side.

![Electric Bike Interfaces](e-bike-intf.svg)

![Electric Bike Flows](e-bike-flow.svg)

### Constraints and Allocations

Pack energy (`energyBalance`) is separate from rider watts (`riderInputBalance`). Allocations map ride safety and assist limit onto brakes, controller, both sensors, and the BMS; charge safety maps to the BMS.

![Electric Bike Constraints](e-bike-cst.svg)

![Electric Bike Allocations](e-bike-alloc.svg)

### Package and Trace Overview

Structure, behavior, requirements, analysis, and verification. The general view traces a use case, requirement, and verification case.

![Electric Bike Packages](e-bike-pkg.svg)

![Electric Bike Cross-View Trace](e-bike-general.svg)
