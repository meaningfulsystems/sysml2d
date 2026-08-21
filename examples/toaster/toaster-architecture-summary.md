# Toaster Architecture

This document is the architecture and system-design description of the two-slice household toaster modeled in `toaster.sysml`. A reviewer should be able to understand purpose, context, requirements, structure, interfaces, behavior, and allocations without opening the model. Generated views appear after the written architecture.

This is an example model, not a certifiable appliance. Requirement text and numbers come from the SysML model. The model does not name an external standard.

## 1. Purpose and Mission

The system is a countertop two-slice toaster. Its mission is to accept bread, apply controlled heat for a selected browning level, present toast, and allow the user to cancel a cycle or empty crumbs without tools.

The model is a single baseline product, not a product line. Four-slice, bagel, defrost, and wide-slot variants are not modeled.

## 2. Operating Context

The toaster sits in a kitchen among three external parts: the user, a mains supply, and the kitchen environment. Bread enters the slots; toast and crumbs leave; heat and noise go to the surroundings.

| External part | Role |
|---------------|------|
| User | Inserts bread, lowers the lever, sets browning, cancels, pulls the crumb tray |
| Mains supply | Electrical energy into the power cord |
| Kitchen environment | Receives waste heat and noise |

Items that cross the boundary: `BreadSlice`, `ToastSlice`, `ElectricalEnergy`, `HeatEnergy`, `UserCommand`, `CrumbDebris`.

External-facing ports on the toaster are user inputs (lever, buttons, tray pull) and mains power. `MainsSupply` has no voltage or frequency in the model.

## 3. Stakeholders and Use Cases

The only named stakeholder is the user. A service technician is implied by a serviceability requirement but is not modeled as an actor.

**Use cases**

- **Toast Bread** — primary cycle.
- **Cancel Toast** — extends Toast Bread.
- **Empty Crumb Tray** — included by Toast Bread; tray is removable without tools.

**Analysis cases**

- **Thermal Performance** — uses the heat-energy constraint against browning.
- **Electrical Load** — uses the electrical-power constraint against electrical safety.

**Verification cases** (names only — no part, port, or effect is bound)

`verifyToastBrowning`, `verifyElectricalSafety`, `verifyCrumbTrayRemoval`, `verifyCarriageRelease`, `verifySurfaceTemperature`.

## 4. Requirements

The model states fourteen requirements. IDs such as REQ-T-xxx appear only on views and are listed here for cross-reference.

| ID (view) | Requirement | Quantitative target in the model |
|-----------|-------------|----------------------------------|
| REQ-T-001 | Toast safety — no burns, shock, or fire under normal use | none |
| REQ-T-002 | Electrical safety — comply with applicable household-appliance electrical safety standards | none (no standard named in the model) |
| REQ-T-003 | Uniform browning across the bread surface at each setting | none |
| REQ-T-004 | Timer accuracy | **±5%** of the selected setting |
| — | User interface — insert bread, select browning, cancel, without tools | none |
| — | Cleanability — crumb tray removable and washable without tools | none |
| — | Serviceability — serviceable by a qualified technician without specialized equipment | none |
| REQ-T-010 | Operate within rated power under normal use | rated watts unmarked |
| REQ-T-011 | Exterior accessible surfaces shall not exceed safe touch temperature | touch temperature unmarked |
| REQ-T-012 | Disable heating if internal temperature exceeds a safe threshold | cutoff threshold unmarked |
| REQ-T-020 | Distinct, repeatable browning levels | **at least three** |
| REQ-T-021 | Carriage releases on timer expiry or cancel | carriage-release time unmarked |
| REQ-T-030 | Crumb-tray removal force | **no more than 10 N** |
| REQ-T-040 | Cycle life before maintenance | **at least 10,000** toast cycles |

There is no thermal-cutoff part in the structure. The cutoff statement is a requirement only. Power claims in this note refer to the modeled `mainsPower` → cord → `powerAndControlSubsystem` → `heatingElement` path.

## 5. Structure

The toaster is a single-level composition. Part definitions have no nested internals.

```
Toaster
├── chassis
├── lever
├── buttons
├── powerAndControlSubsystem
├── heatingElement
├── carriage
├── crumbTray
└── powerCord
```

The definition view marks crumb tray `0..1` and the others `1`. Multiplicity is not written in the SysML source.

Port types used on the toaster: user-interface, power, control, heat, and mechanical. Ports are declared on the toaster, not on the empty child part definitions.

## 6. Interfaces and Interconnections

**Why the connections exist:** the user starts and stops the cycle through the lever and buttons; mains energy reaches the control subsystem through the cord; the subsystem commands the heater; the heater heats the carriage; the chassis locates the moving and mounted parts.

| Connection | From → to | Why |
|------------|-----------|-----|
| Lever / button / tray inputs | Boundary → lever, buttons, crumb tray | User actuation |
| Mains → cord → power and control | Power | Energize control and heater switching |
| Lever → power and control | Control | Toast request / latch |
| Buttons → power and control | Control | Browning and cancel |
| Power and control → heater | Control | Heat command |
| Heater → carriage | Thermal | Heat to bread |
| Lever → carriage | Mechanical | Lift / release |
| Chassis → carriage, buttons, power and control, crumb tray | Mechanical | Guide and mount |

The electrical interconnection view shows buttons, lever, cord, power and control, and heater. The mechanical interconnection view shows chassis, lever, buttons, carriage, crumb tray, and the control-subsystem mount. Those two views split the same model connections by domain.

Interface definitions (`UserInterface`, `PowerInterface`, `ThermalInterface`, `MechanicalInterface`) are stubs. They do not declare carried features in the model.

## 7. Behavior

### States (`ToasterControl`)

Initial state is Idle.

| From | Trigger | To |
|------|---------|-----|
| Idle | lever down | Heating |
| Heating | timer expired | Done |
| Done | carriage up | Idle |
| Heating | carriage up | Idle (cancel / early release) |
| Heating | overheat | Error |
| Heating | carriage jam | Error |
| Heating | power fault | Error |
| Error | reset | Idle |

Done is a normal state, not a final node: cycle complete is distinct from bread removal. The three heating-to-error transitions are separate in the model; the state view collapses them to one fault edge.

### Toast cycle (actions)

Insert bread → lower lever → latch carriage → energize heater → monitor timer (loop until done) → release carriage → present toast.

Emptying the crumb tray is a use case; it is not an action on the toast-cycle diagram.

### Interaction

User lowers the lever; the lever requests toast from power and control; power and control commands the heater and later releases the carriage; toast is available to the user.

## 8. Allocations

Allocation elements exist in the model; most endpoints are only on the allocation view.

| Allocation | Source | Target (view) |
|------------|--------|---------------|
| Safety to power and control | Toast safety | Power and control subsystem |
| Heat to heater | Browning | Heating element |
| Browning to toast cycle | Browning | Energize-heater action |
| Cleanability to crumb tray | Cleanability | Crumb tray |
| Carriage release to mechanism | name only | endpoints **not in model** |
| Surface temperature to chassis | name only | endpoints **not in model** |

Timing, user interface, serviceability, power rating, thermal cutoff, browning-level count, tray force, and cycle life have no allocation in the model or views.

## 9. Parameters, Constraints, and Scope

Constraint definitions exist as names only — `heatEnergyBalance`, `toastTimingEstimate`, `electricalPowerLimit`, `browningTemperatureEstimate`, `surfaceTemperatureLimit`, `carriageReleaseTiming`. The model has no equations.

Attributes declared without values: `targetBrowning`, `inputPower`, `toastDuration`, `toastTemperature`, `surfaceTemperature`, `releaseTime`, `trayRemovalForce`.

**Out of scope:** 4-slice, bagel, defrost, and wide-slot variants; coil, thermostat, and latch geometry; constraint equations.

## 10. Open Risks

- Rated watts, mains voltage and frequency, touch-temperature limit, thermal-cutoff threshold, and carriage-release time are unmarked.
- `thermalCutoffRequirement` has no matching part.
- `allocateCarriageReleaseToMechanism` and `allocateSurfaceTemperatureToChassis` are names without model endpoints.
- Constraint definitions have no equations.
- Verification cases are names only.

---

## Generated Views

The figures below are the generated SysMLD views for this model. They illustrate the architecture above; they do not replace it.

### Cases

The toaster cases focus on toasting bread, cancelling a toast cycle, and removing crumbs. Analysis cases are `thermalPerformanceAnalysis` and `electricalLoadAnalysis`. Verification cases are names only.

![Toaster Use Cases](toaster-uc.svg)

![Toaster Analysis Cases](toaster-acase.svg)

![Toaster Verification Cases](toaster-vcase.svg)

### Operating Context

The toaster interacts with the user, bread, the mains outlet, the kitchen environment, finished toast, and crumb debris.

![Toaster Operating Context](toaster-context.svg)

### Requirements

Requirement nodes follow the SysML model text.

![Toaster Requirements](toaster-req.svg)

### Hierarchical Structure

The definition tree composes chassis, lever, buttons, power and control, heating element, carriage, crumb tray, and power cord.

![Toaster Definition Tree](toaster-bdd.svg)

### Interaction

The interaction view shows the user lowering the lever, the control subsystem commanding heat, the carriage being released, and toast becoming available.

![Toaster Interaction](toaster-int.svg)

### State Behavior

Idle, Heating, Done, and Error. Done is a normal state. Error covers overheat, jam, and power fault, with reset to Idle.

![Toaster State Machine](toaster-stm.svg)

### Action Behavior

The toast cycle from bread insertion through lever, latch, heat, timer, release, and presentation.

![Toaster Toast Cycle](toaster-act.svg)

### Interconnection Views

Electrical interconnection separates user controls, cord power, power and control logic, and the heater command. Mechanical interconnection separates chassis mounting, lever lift, button mounting, carriage guidance, and crumb-tray guidance.

![Toaster Electrical Interconnection](toaster-electrical-icn.svg)

![Toaster Mechanical Interconnection](toaster-mech-composed.svg)

### Interfaces and Flows

User, power, mechanical, and thermal interfaces. Flows are bread, toast, mains energy, heat, user commands, and crumbs.

![Toaster Interfaces](toaster-intf.svg)

![Toaster Flows](toaster-flow.svg)

### Constraints and Allocations

Named energy, timing, power, browning, surface-temperature, and release constraints. Allocations map the requirements that the view binds onto parts and actions.

![Toaster Constraints](toaster-cst.svg)

![Toaster Allocations](toaster-alloc.svg)

### Package and Trace Overview

Packages are structure, behavior, requirements, analysis, and verification. The general view traces a use case, requirement, action, part, and verification case.

![Toaster Packages](toaster-pkg.svg)

![Toaster Cross-View Trace](toaster-general.svg)
