# Apollo 11 Architecture Summary

This document summarizes the Apollo 11 / Block II (AS-506) SysML v2 model and its generated SysMLD views. The reference instance is the flown stack: Saturn V through CSM and LM, crew, KSC, Mission Control, and MSFN. Numbers that have a source are stated; values without a source stay UNKNOWN.

The model is not a complete vehicle handbook. It is a whole-stack architecture with system views and a smaller set of subsystem views (CSM/LM, AGC/GNC, ground, EPS, RCS, docking, mission and abort state machines).

## Cases

Fly Mission includes the lunar EVA. Recover Crew and Range Safety sit beside it. Analysis cases cover the USB links and consumables. Verification cases check the CSM USB numbers, the A7L suit, P27 uplink verbs, and the range-safety destruct path.

![Apollo Use Cases](apollo-uc.svg)

![Apollo Analysis Cases](apollo-acase.svg)

![Apollo Verification Cases](apollo-vcase.svg)

## Operating Context

Earth and Moon are the environment. The context view places the stack between KSC, MCC, MSFN, and recovery before the internals are opened.

![Apollo Operating Context](apollo-context.svg)

## Requirements

The requirement view carries sourced conflicts without picking a silent winner: SPS 20,500 lbf (Press Kit) vs 21,500 lbf (TN D-7375); DPS 9,870 / 1,050–6,300 lbf (Press Kit) vs 10,500 lbf 10:1 (TN D-7143). Tank loads are Press Kit p.109. SPS loaded mass, CSM lunar Δv, loaded SM/CM RCS propellant, and the A11 AGS flight-program name stay UNKNOWN.

![Apollo Requirements](apollo-req.svg)

## Hierarchical Structure

The system definition tree is Saturn V (`SIC`, `SII`, `SIVB`, IU with LVDC, SLA, LES), CSM, LM, crew, and ground. Stage labels keep the hyphens (S-IC / S-II / S-IVB); identifiers cannot.

![Apollo System Definition](apollo-bdd.svg)

## Interaction

The interaction view follows a command-load and voice path from MCC through CCATS and MSFN to the CSM, with P27 as a separate uplink.

![Apollo Interaction](apollo-int.svg)

## Mission and Abort State

The mission machine is countdown → boost → earthOrbit → TLI → dock/eject → translunar → LOI → undock → DOI → descent → surface/EVA → ascent → rendezvous → TEI → entry → recovery.

Transposition, docking, and LM extract (`dockEject`) sit after TLI and before the long translunar coast. Official GET: TLI 02:44:15, TDE about 03:20–04:09, LOI-1 75:54:28. The abort machine runs in parallel: pad, modes I–IV, contingency TLI, lunar, and SPS.

![Apollo Mission Phases](apollo-stm.svg)

![Apollo Abort Modes](apollo-stm-abort.svg)

## Action Behavior

The action view covers AGC power-up, antenna selection, Path A and P27 command loads, R47 AGS init, P63/P64/P66 landing, P70/P71 abort, and probe/drogue docking.

![Apollo Actions](apollo-act.svg)

## System Interconnection

The vehicle IBD is the stack: RSO destruct, KSC umbilicals, IU guidance to the stages, SLA to the SM and LM, CM–SM, docking, USB, NASCOM, and recovery to the CM. A second interconnection view keeps the same topology at vehicle grain. Connections do not pass over boxes.

![Apollo System Interconnection](apollo-ibd.svg)

![Apollo Vehicle Interconnection](apollo-ibd-vehicle.svg)

## CSM and LM

CSM structure is CM (SCS, `AGC_CM`, two DSKYs, ECLSS, probe and latches) and SM (SPS, four RCS quads, three fuel cells). LM structure is descent (DPS, four AgZn, ECA) and ascent (PNGS, `AGC_LM`, AGS, APS, RCS, radars). The two vehicles stay separate; there is no CSM–LM propellant crossfeed.

![CSM Definition](apollo-bdd-csm.svg)

![LM Definition](apollo-bdd-lm.svg)

![CSM Interconnection](apollo-ibd-csm.svg)

![LM Interconnection](apollo-ibd-lm.svg)

## AGC and GNC

There are two Block II AGCs. CM ropes are Comanche 055; LM ropes are Luminary 1A (LMY99/1). CMC P61–P67 is entry; LGC P63–P68 is landing — the P-numbers are not global. AGS is AEA + ASA + DEDA and is not a landing computer. IU LVDC stays off the AGC data path (82.03125 µs, 26+2 bits).

![AGC Definition](apollo-bdd-agc.svg)

![AGC Interconnection](apollo-ibd-agc.svg)

![GNC Interconnection](apollo-ibd-gnc.svg)

![AGS Interconnection](apollo-ibd-ags.svg)

## Ground, MSFN, and MCC

KSC LCC hands off to MCC at tower clear (Mission Rule 1-21). Apollo 11 flies from MOCR 2. MSFN is Goldstone, Madrid, and Honeysuckle plus NASCOM; the ship inventory is collapsed. RTCC is five IBM 360/75; which machine is MOC vs DSC on A11 is UNKNOWN.

![MCC / RTCC](apollo-ibd-mcc.svg)

![MSFN Interconnection](apollo-ibd-msfn.svg)

![MSFN Definition](apollo-bdd-msfn.svg)

## Electrical Power

SM power is three fuel cells on a 2+2 cryo set (not a J-mission 3+3). CM has three AgZn batteries, a charger, and two 117 V 400 Hz inverters. LM has six AgZn (four descent, two ascent) and an ECA on each stage. There is no stage-to-stage electrical power.

![EPS Definition](apollo-bdd-eps.svg)

![SM Fuel Cells](apollo-ibd-eps-sm.svg)

## RCS

SM RCS is 100 lbf per engine (Press Kit p.93), four quads. LM RCS is 100 lbf per engine (Press Kit p.106). CM RCS is two systems of six 93 lbf engines with no automatic translation. Loaded SM/CM RCS propellant mass is UNKNOWN.

![SM RCS Quads](apollo-ibd-rcs.svg)

![CM RCS Systems](apollo-ibd-rcs-cm.svg)

## Docking

The CM probe meets the LM drogue. Twelve ring latches take the stack from soft dock to hard dock; hardware is then removed for transfer. That sequence is a docking-mode machine, separate from the mission-phase `dockEject` state.

![Docking Interconnection](apollo-ibd-dock.svg)

![Docking Mode](apollo-stm-dock.svg)

## Interfaces and Flows

USB numbers are sourced: CSM uplink 2106.40625 MHz, LM uplink 2101.802 MHz. VHF is 296.8 / 259.7 MHz; recovery is 243.0 MHz. The flow view is MCC → NASCOM → MSFN → CSM/LM, with a separate RSO destruct path.

![Apollo Interfaces](apollo-intf.svg)

![Apollo Flows](apollo-flow.svg)

## Constraints and Allocations

Constraints cover USB links, lunar delay (~1.3 s), F-1 thrust, AGC cycle time, and ignition mass. Allocations bind boost and TLI to the IU, the two AGCs to CM and LM, AGS to the LM, LVDC to the IU, and EPS/RCS/docking to the vehicles that own them.

![Apollo Constraints](apollo-cst.svg)

![Apollo Allocations](apollo-alloc.svg)

## Package and Trace Overview

Packages follow Saturn V, CSM, LM, crew, and ground. The general view traces a flown-mission use case to the sourced requirements and verification cases.

![Apollo Packages](apollo-pkg.svg)

![Apollo Cross-View Trace](apollo-general.svg)

## Scope

This is Apollo 11 only. Later J-mission cryo, LRV, and SIM bay are out of scope. Entry blackout duration, A11 food intake, and a complete 30-ft MSFN inventory stay UNKNOWN.
