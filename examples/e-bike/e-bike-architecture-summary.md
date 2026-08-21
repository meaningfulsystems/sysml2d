# Electric Bike Architecture Summary

This document summarizes the street-legal EPAC (EN 15194) SysML v2 model and its generated SysMLD views. The model covers rider-facing cases, quantitative requirements, structure, ride-control behavior, interfaces, flows, analyses, verification, and traceability.

The bicycle is cadence PAS only: no certified throttle, assist cutoff at 25 km/h, walk assist at or below 6 km/h. The hub is rear geared with no regeneration. **250 W is the EU continuous rating.** **40 N·m is hub peak torque, not continuous** — that torque does not sit with 250 W at 25 km/h as a continuous operating point. Charge energy enters the BMS, then the pack.

## Cases

The use cases are Ride Bike, Adjust Assist, and Charge Bike. The rider associates with ride and assist only. The charger associates with charge only. Ride includes Adjust Assist. Analysis cases cover Tour-mode range and brake-inhibit latency. Verification cases check range, brake cutoff, charge safety, and the 25 km/h assist limit.

![Electric Bike Use Cases](e-bike-uc.svg)

![Electric Bike Analysis Cases](e-bike-acase.svg)

![Electric Bike Verification Cases](e-bike-vcase.svg)

## Operating Context

The bike interacts with the rider, an off-board charger, and the road. The context view makes those external exchanges explicit before the internals are decomposed.

![Electric Bike Operating Context](e-bike-context.svg)

## Requirements

Requirements carry the numbers that bind the example: Tour-mode 500 Wh / ~8.3 Wh/km for 60 km, 50 ms electronic brake inhibit plus the EN 15194 5 m / 2 m distance cutoff, 25 km/h assist cut, walk assist ≤ 6 km/h, EU continuous 250 W, StVZO / ISO 6742 lighting. Charge safety is allocated to the BMS inside the pack (UL 2849).

![Electric Bike Requirements](e-bike-req.svg)

## Hierarchical Structure

The definition tree composes the bike from frame, battery pack (with nested BMS), motor controller, rear geared hub, human interface, brake system, cadence sensor, and wheel-speed sensor. The hub box states EU continuous 250 W and 40 N·m peak torque separately.

![Electric Bike Definition Tree](e-bike-bdd.svg)

## Interaction

The interaction view follows a ride from power-on through assist command, phase current to the rear geared hub, brake lever, inhibit, and torque-off.

![Electric Bike Interaction](e-bike-int.svg)

## State Behavior

RideControl starts in Off. Power goes to Standby; cadence starts Assist; the walk button starts walk (`do / ≤ 6 km/h`). Charging is entered only from Off. Fault is reached from Assist on overcurrent; reset returns to Off, not Standby.

![Electric Bike Ride Control](e-bike-stm.svg)

## Action Behavior

The action view describes power-on, assist selection, pedaling, brake inhibit, torque delivery, plug-in, and charge stop.

![Electric Bike Ride Actions](e-bike-act.svg)

## Interconnection View

The interconnection view shows child-part ports only. Charge arrives at the BMS, then the pack contactor. Cadence and wheel-speed sensors feed the controller so the 25 km/h cut is not cadence-only. Connections do not pass over boxes.

![Electric Bike Interconnection](e-bike-ibd.svg)

## Interfaces and Flows

The interface view covers rider, charge, drive, and brake interfaces. The flow view is charger → BMS → pack → controller → hub → road, with rider command and brake inhibit on the side.

![Electric Bike Interfaces](e-bike-intf.svg)

![Electric Bike Flows](e-bike-flow.svg)

## Constraints and Allocations

The constraint view keeps pack energy (`energyBalance`) separate from rider watts (`riderInputBalance`). Tour range binds `usableWh` and `energyPerKm`. The allocation view maps Ride Safety and Assist Limit onto brakes, controller, both sensors, and the BMS; charge safety maps to the BMS.

![Electric Bike Constraints](e-bike-cst.svg)

![Electric Bike Allocations](e-bike-alloc.svg)

## Package and Trace Overview

The package view organizes structure, behavior, requirements, analysis, and verification. The general trace view ties a use case, requirement, and verification case together.

![Electric Bike Packages](e-bike-pkg.svg)

![Electric Bike Cross-View Trace](e-bike-general.svg)

## Scope

This example is one EN 15194 EPAC class, not a product line. Throttle variants, mid-drive kits, and regenerative hubs are out of scope. `ThrottleCommand` remains an unused item.
