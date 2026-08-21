# Blender Architecture

This note is an educational architecture walkthrough of the countertop blender modeled in `blender.sysml`. It uses a **simplified MagicGrid** spine: problem domain first, then solution domain. It is not a Department of Defense Architecture Framework (DoDAF) product. There are no Operational / Systems / Technical View (OV / SV / TV) products and no capability taxonomies.

A new systems engineer should be able to learn the *system* and the *method* from this note without opening the Systems Modeling Language (SysML) source. The `.sysml` model is authoritative when a generated view label disagrees.

This is an example model, not a certifiable appliance. Requirement text and numbers come from the SysML model.

## How to read this note (simplified MagicGrid)

MagicGrid separates **what the system must do for someone** from **how the design does it**.

**Problem domain**

1. Purpose / mission — why the system exists, in plain language.
2. Stakeholders and use cases — every actor, include/extend, and the analysis and verification *names*.
3. Requirements — model text wins. Quantitative targets appear only when they are bound in the `.sysml`.

**Solution domain**

4. Structure and interfaces — parts, ports that exist, what connects to what and why, and the operating boundary.
5. Behavior — states, actions, interactions, and fault paths.
6. Parametrics / constraints — equations if present; names only if not.
7. Allocations — requirements or behavior mapped onto parts that actually exist.

Sections 8 and 9 walk every generated figure — Block Definition Diagram (BDD), Internal Block Diagram (IBD), and State Machine (STM) among them — and then list unmarked items and out-of-scope work.

---

## 1. Purpose / mission

The system is a baseline countertop blender. Its mission is to accept ingredients, blend them under program control until a smoothness threshold is reached, stop on user command or fault, and allow the container to be cleaned.

The model is a single baseline, not a product line.

## 2. Stakeholders and use cases

The only named stakeholder is the user.

**Use cases**

- **Make Smoothie** — primary program.
- **Stop Blend** — **extends** Make Smoothie.
- **Clean Container** — **included** by Make Smoothie.

**Analysis cases** (named studies; they bind named constraints, not measured results)

- **Motor Load** (`motorLoadAnalysis`) — `torqueSpeedLoadEstimate` against motor control.
- **Smoothness Detection** (`smoothnessDetectionAnalysis`) — `smoothnessThresholdEstimate` against the smoothness-detection requirement.

**Verification cases** (names only — no part, port, or effect is bound)

`verifyLidInterlock`, `verifySmoothnessDetection`, `verifyStopCommand`, `verifyOvercurrentProtection`, `verifyContainerSeat`.

## 3. Requirements

The model states thirteen requirements. Identifiers such as REQ-B-xxx appear only on generated views. View labels are not treated as requirements.

| ID (view only) | Model requirement | Quantitative target in the model |
|----------------|-------------------|----------------------------------|
| REQ-B-001 | The motor shall not run unless the lid is fully seated and locked | none |
| REQ-B-002 | The control panel shall start, pause, and stop the motor in response to user commands within 200 ms | **within 200 ms** |
| REQ-B-003 | The smoothness sensor shall detect blend completion and signal the control panel | none |
| REQ-B-004 | The blender shall operate within its rated power envelope under all normal blending loads | rated magnitude **not in model** |
| — | The user shall be able to start, pause, and stop blending without tools | none |
| — | The container, lid, and blade assembly shall be dishwasher-safe or washable under running water | none |
| — | Serviceable by a qualified technician without specialized equipment | none |
| REQ-B-020 | The motor shall maintain set speed within ±10% across all normal blending loads | **±10%** |
| REQ-B-010 | The lid interlock shall disable the motor within 50 ms of lid removal detection | **within 50 ms** |
| REQ-B-021 | Overcurrent protection shall cut power before motor damage occurs | trip time **not in model** |
| REQ-B-030 | Smoothness threshold configurable for at least three blend program profiles | **at least three** profiles |
| REQ-B-040 | Operate below 85 dB(A) at the operator position during normal use | **below 85 dB(A) at the operator position** (model wording; not a blender certification) |
| REQ-B-050 | The container shall lock to the motor base with positive mechanical engagement and deliberate release | none |

The model requires pause. The state machine has no pause state or transition. There is no interlock part; lid-to-container is a mechanical connection, and `interlockLatencyRequirement` is a requirement on that behavior. Mains is `MainsSupply`, item `ElectricalEnergy`, flow `mainsPowerFlow`, and a stub `PowerInterface`. There is **no** `PowerPort`.

## 4. Structure and interfaces

### Operating context / boundary

The blender sits on a counter among the user, ingredients, and a mains supply. A smoothie is the produced output.

| External part | Role |
|---------------|------|
| User | Loads ingredients, closes the lid, starts / stops / powers the blender, pours |
| Ingredients | Material loaded into the container |
| Mains supply | Electrical energy |
| Smoothie | Blend output |

Items that cross the boundary: `ElectricalEnergy`, `RotationalEnergy`, `SmoothnessSignal`, `UserCommand`. `Fruit` and `Liquid` are declared and unused.

`MainsSupply` has no voltage in the model. `ContainerInterface` is declared and not wired.

### Parts

The blender is a single-level composition. Child part definitions are empty.

```
Blender
├── tamper              (0..1 on the definition view)
├── lid
├── container
├── bladeAssembly
├── driveCoupling
├── smoothnessSensor
├── motorBase
├── motor
└── controlPanel
```

The definition view marks tamper `0..1`; the SysML source does not state multiplicity.

Port types that exist: mechanical, drive, sensor, and control. There is no power port on the blender.

### What connects to what, and why

The lid and container must be seated before torque is legal. The motor base locates motor, panel, and coupling. The coupling transmits rotation to the blades and vibration to the smoothness sensor. The panel commands the motor and receives blend-complete.

| Connection | From → to | Why |
|------------|-----------|-----|
| Tamper ↔ lid | Mechanical | Optional tamper fit |
| Lid ↔ container | Mechanical | Lid seat / interlock geometry |
| Container ↔ blade | Mechanical | Blade mounted in the jar |
| Container ↔ motor base | Mechanical | Seat and lock |
| Base → motor, control panel, drive coupling | Mechanical | Mount |
| Motor → coupling → blade | Drive | Torque to shear |
| Coupling → smoothness sensor | Sensor | Vibration / load for completion |
| Sensor → control panel | Control | Blend-complete |
| Control panel → motor | Control | Speed / stop |

Flows (item/flow names, not ports): `ingredientsIntoContainer`; `commandToControlPanel`; `mainsPowerFlow` from `MainsSupply` (no `PowerPort`); `motorTorqueFlow`; `bladeShearFlow`; `smoothnessFeedbackFlow`.

## 5. Behavior

### States (`BlenderControl`)

Top-level states are Off and a composite Powered. Entering Powered goes to Ready. A single power-off transition leaves the composite.

| From | Trigger | To |
|------|---------|-----|
| Off | power switch on | Powered (Ready) |
| Powered | power switch off | Off |
| Ready | start command | Blending |
| Blending | smoothness signal | Ready |
| Blending | stop command | Ready |
| Blending | timeout | Ready |
| Blending | fault | Error |
| Blending | lid opened | Error |
| Blending | blade jam | Error |
| Blending | overcurrent | Error |
| Blending | sensor fault | Error |
| Error | reset | Ready |

Timeout duration is not in the model. The state view collapses the five blending-to-error transitions into one fault edge.

### Smoothie program (actions)

Load ingredients → close lid → power on → start program → spin blades ⇄ sense smoothness (loop until smooth) → stop motor → pour smoothie.

### Interaction

User start → control panel speed command → motor torque → coupling rotation to blades and vibration to the sensor → smoothness signal back to the panel → stop.

## 6. Parametrics / constraints

Constraint names: `torqueSpeedLoadEstimate`, `motorPowerLimit`, `blendTimingEstimate`, `interlockStopTiming`, `smoothnessThresholdEstimate`, `noisePowerTradeoff`. The model has **no equations**.

System-level attributes are declared without values: `commandedSpeed`, `motorTorque`, `blendDuration`, `smoothnessIndex`, `motorSpeed`, `interlockLatency`, `motorPower`, `noiseLevel`.

## 7. Allocations

Six allocation names exist in the model. The allocation view binds three of them to parts that exist.

| Allocation | Source | Target that exists |
|------------|--------|--------------------|
| `allocateInterlockToControlPanel` | Lid interlock | `controlPanel` |
| `allocateTorqueToMotor` | Motor control | `motor` and `spinBladeAssembly` |
| `allocateSmoothnessToSensor` | Smoothness detection | `smoothnessSensor` |
| `allocateCleaningToContainer` | name only | endpoints **not in model** |
| `allocateProtectionToMotorBase` | name only | endpoints **not in model** |
| `allocateInterfaceToControlPanel` | name only | endpoints **not in model** |

---

## 8. Diagram walkthrough

The figures are generated SysMLD views. They illustrate the architecture above; they do not replace it. When a view label disagrees with the `.sysml`, the model wins.

**Shared symbol key**

- Stick figure — actor.
- Ellipse — use case.
- Dashed arrow labeled `include` / `extend` — use-case dependency.
- Rectangle with `«requirement»` — a requirement node (view identifier only).
- Rectangle — part usage.
- Small square on a box edge — port.
- Solid line between ports — connection. Lines must not pass through boxes.
- Rounded rectangle — state. A large rounded frame is a composite state.
- Arrow between states — transition, labeled with the trigger.
- Rounded action box — an action on a control-flow diagram.
- Lifeline / message — interaction (sequence).

### Problem domain

#### Use cases — `blender-uc.svg`

**MagicGrid layer:** problem / stakeholders.

**Question:** Who uses the blender, and which jobs can they ask of it?

**How to read it:** The User actor associates with three ellipses inside the Blender boundary. Stop Blend **extends** Make Smoothie. Clean Container is **included** by Make Smoothie.

**Symbols:** actor, use-case ellipses, include/extend dashed arrows, system boundary.

![Blender Use Cases](blender-uc.svg)

#### Analysis cases — `blender-acase.svg`

**MagicGrid layer:** problem / analysis.

**Question:** Which named studies exist?

**How to read it:** Motor Load and Smoothness Detection sit against named constraints. They do not publish measured results.

**Symbols:** analysis-case nodes and constraint names.

![Blender Analysis Cases](blender-acase.svg)

#### Verification cases — `blender-vcase.svg`

**MagicGrid layer:** problem / verification (names only).

**Question:** Which checks are named?

**How to read it:** Five verification-case names. None binds a part, port, or effect.

**Symbols:** verification-case nodes.

![Blender Verification Cases](blender-vcase.svg)

#### Operating context — `blender-context.svg`

**MagicGrid layer:** problem / context (boundary of the solution).

**Question:** What sits outside the blender?

**How to read it:** User, ingredients, mains supply, and the produced smoothie surround the blender. Mains energy is an item flow, not a `PowerPort`.

**Symbols:** external parts and item flows.

![Blender Operating Context](blender-context.svg)

#### Requirements — `blender-req.svg`

**MagicGrid layer:** problem / requirements.

**Question:** What shalls does the model state?

**How to read it:** Bound numbers are 200 ms controls, 50 ms lid interlock, ±10% set speed, at least three blend profiles, and below 85 dB(A) at the operator position. Rated watts and overcurrent trip time are unmarked. View-only identifiers are not model elements.

**Symbols:** `«requirement»` rectangles.

![Blender Requirements](blender-req.svg)

### Solution domain

#### Definition tree (Block Definition Diagram) — `blender-bdd.svg`

**MagicGrid layer:** solution / structure.

**Question:** What parts compose the blender?

**How to read it:** A BDD is a composition tree: tamper, lid, container, blade assembly, drive coupling, smoothness sensor, motor base, motor, and control panel.

**Symbols:** part boxes and composition lines.

![Blender Definition Tree](blender-bdd.svg)

#### Internal interconnection (Internal Block Diagram) — `blender-ibd-composed.svg`

**MagicGrid layer:** solution / interfaces.

**Question:** How do the parts mount, drive, sense, and command each other?

**How to read it:** An IBD shows parts as boxes and connections as lines between ports. Follow lid → container → base, then motor → coupling → blades, and sensor → panel → motor. There is no power-port box.

**Symbols:** part boxes, ports, mechanical / drive / sensor / control connections.

![Blender Internal Structure](blender-ibd-composed.svg)

#### Interfaces — `blender-intf.svg`

**MagicGrid layer:** solution / interfaces.

**Question:** Which interface definitions exist?

**How to read it:** User controls, power (stub), drive, and sensing. `PowerInterface` is a name only. `ContainerInterface` is declared and not wired.

**Symbols:** interface nodes.

![Blender Interfaces](blender-intf.svg)

#### Flows — `blender-flow.svg`

**MagicGrid layer:** solution / interfaces (items).

**Question:** Which items move?

**How to read it:** Ingredients, commands, mains energy (`mainsPowerFlow`), torque, blade shear, and smoothness feedback. Mains is an item/flow, not a port.

**Symbols:** item/flow nodes and arrows.

![Blender Flows](blender-flow.svg)

#### State machine — `blender-stm.svg`

**MagicGrid layer:** solution / behavior.

**Question:** Which modes does the blender occupy?

**How to read it:** The STM has Off and a composite Powered. Ready, Blending, and Error sit inside Powered. Error covers general fault, lid opened during blend, blade jam, overcurrent, and sensor fault. Pause is required in text and is not a state.

**Symbols:** rounded states, composite frame, transition arrows.

![Blender State Machine](blender-stm.svg)

#### Smoothie-program actions — `blender-act.svg`

**MagicGrid layer:** solution / behavior.

**Question:** What is the ordered blend procedure?

**How to read it:** Load → close lid → power on → start → spin ⇄ sense → stop → pour.

**Symbols:** action boxes and control-flow arrows.

![Blender Smoothie Program](blender-act.svg)

#### Interaction — `blender-int.svg`

**MagicGrid layer:** solution / behavior.

**Question:** Who talks to whom during a smoothie program?

**How to read it:** Lifelines for user, control panel, motor, coupling, blades, and smoothness sensor. Messages follow start, torque, vibration, completion, and stop.

**Symbols:** lifelines and messages.

![Blender Interaction](blender-int.svg)

#### Constraints — `blender-cst.svg`

**MagicGrid layer:** solution / parametrics.

**Question:** Which named constraints exist?

**How to read it:** Speed, torque, load, timing, interlock, smoothness, power, and noise names. There are no equations in the model.

**Symbols:** constraint nodes and unbound attributes.

![Blender Constraints](blender-cst.svg)

#### Allocations — `blender-alloc.svg`

**MagicGrid layer:** solution / allocations.

**Question:** Which shalls are mapped onto parts or actions that exist?

**How to read it:** Interlock → control panel; motor control → motor and spin-blades; smoothness → sensor. Cleaning, protection, and interface allocations are names without model endpoints.

**Symbols:** requirement boxes, part boxes, dashed allocate arrows.

![Blender Allocations](blender-alloc.svg)

#### Packages — `blender-pkg.svg`

**MagicGrid layer:** model organization (supports every MagicGrid layer).

**Question:** How is the model packaged?

**How to read it:** Structure, behavior, requirements, analysis, and verification packages.

**Symbols:** package nodes.

![Blender Packages](blender-pkg.svg)

#### Cross-view trace — `blender-general.svg`

**MagicGrid layer:** trace across MagicGrid layers.

**Question:** Can one path be followed from a use case through a requirement and an action to a part and a verification name?

**How to read it:** A single teaching thread among those element kinds. It is not extra requirements.

**Symbols:** mixed-kind nodes and trace lines.

![Blender Cross-View Trace](blender-general.svg)

---

## 9. Open risks / unmarked / out of scope

**Unmarked:** rated power magnitude, blend timeout duration, and overcurrent trip time.

**Model gaps:** There is no `PowerPort`; mains energy is only an item/flow (`ElectricalEnergy` / `mainsPowerFlow`). Pause is required in `motorControlRequirement` and `userControlsRequirement` but has no state or transition. There is no interlock part; only the lid–container mechanical connection and the 50 ms requirement. `allocateCleaningToContainer`, `allocateProtectionToMotorBase`, and `allocateInterfaceToControlPanel` are names without model endpoints. Constraint definitions have no equations. Verification cases are names only.

**Out of scope:** product-line variants; dishwasher material certifications; a detailed digital sensor protocol; pause as a state.

This remains an example model, not a certifiable product.
