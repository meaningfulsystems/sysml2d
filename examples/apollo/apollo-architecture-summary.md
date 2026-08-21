# Apollo Architecture Summary

This document summarizes the Apollo 11 / Block II system model and its generated views. The instance is AS-506 (SA-506, CSM-107 Columbia, LM-5 Eagle). Numbers are from NASA primary sources (Apollo 11 Press Kit 69-83K, Saturn V Flight Manual, Apollo Experience Reports, AGCIS / MIT IL, TN D-6718 / D-6724 / D-8093 / D-8227 / TN-7990). Values not in those extracts are left unmarked. There is no single official CSM lunar Δv table in the sources used here.

## Operating Context

The stack sits among CDR/CMP/LMP, KSC LC-39, MCC Houston (A11 used MOCR 2), GSFC/NASCOM, MSFN (Goldstone/Madrid/Honeysuckle 85-ft triad plus named 30-ft, ships, ARIA), AFETR range safety, and TF-130 (USS Hornet). Those are first-class parts, not one Ground actor.

## Requirements (sourced)

- S-IC liftoff 7,653,854 lbf; fueled 5,022,674 lb. S-II 1,059,171 lb. S-IVB 260,523 lb. IU 4,306 lb (PK p.109).
- CM 12,250 lb; SM 51,243 lb; DPS 18,100 lb; APS 5,214 lb; LM RCS 604 lb.
- SPS 20,500 (PK) vs 21,500 vac (TN D-7375). DPS 9,870 / 1,050–6,300 (PK) vs 10,500 and 10:1 (TN D-7143). APS 3,500 lbf, 1.5° cant. SM/LM RCS 100 lbf; CM 93 lbf.
- AGC 2048 E / 36864 F, 11.7 µs, 65 lb / 70 W. A11: Comanche 055 / Luminary 1A LMY99/1. AGS AEA 4096×18, 5 µs, 32.7 lb.
- CM 5.0 psia O2; A11 196 h. PLSS 4 h / 1.04 lb O2. USB CSM 2106.40625/2287.5/2272.5; LM 2101.802/2282.5. VHF 296.8/259.7; recovery 243.0.
- Unmarked: CSM lunar Δv, SPS loaded mass, SM/CM RCS loaded mass, A11 AGS program name, A11 kcal.

## Structure

Pad stack: S-IC-6, S-II-6, S-IVB-6N, IU-6, SLA-14 (LM-5), SM, CM, LES. No stage-to-stage electrical power; no CSM–LM propellant crossfeed. Keep two AGCs, AGS, IU LVDC, LES, descent vs ascent, three crew.

## State Behavior

Mission STM: countdown → boost → earthOrbit → TLI → dockEject → translunar → LOI → undock → DOI → descent → surface/EVA → ascent → rendezvous → TEI → entry → recovery. A11 GET: TLI 02:44:15, dock ~03:20, extract ~04:09, LOI-1 75:54:28, splash 195:18:35 / 13 nmi. CMC P61–P67 is entry; LGC P63–P68 is landing. Do not share one P-number STM. Handoff Mission Rule 1-21. RSO ≠ MCC.

## Allocations

Boost/TLI → IU LVDC. LOI/TEI/entry → AGC_CM. Landing/ascent/LM abort → AGC_LM; backup AGS (does not land). Atmosphere → ECS. EVA → EMU. Trajectory/uplink → RTCC. RF → MSFN. Launch commit → KSC; destruct → RSO; flight → FLIGHT. Heat shield → CM only.

## System Views

Context, sourced requirements, the pad-stack definition, the vehicle interconnection, and the two state machines are the system grain.

![Apollo Operating Context](apollo-context.svg)

![Apollo Requirements](apollo-req.svg)

![Apollo Definition](apollo-bdd.svg)

![Apollo Interconnection](apollo-ibd.svg)

![Apollo Mission Phases](apollo-stm.svg)

![Apollo Abort Modes](apollo-stm-abort.svg)

## Cases

Fly Mission includes the lunar EVA. Recover Crew and Range Safety sit beside it. Analysis cases cover the USB links and consumables. Verification cases check the CSM USB numbers, the A7L suit, P27 uplink, and the range-safety destruct path.

![Apollo Use Cases](apollo-uc.svg)

![Apollo Analysis Cases](apollo-acase.svg)

![Apollo Verification Cases](apollo-vcase.svg)

## Interaction and Action

Command loads and voice travel MCC → CCATS → MSFN → CSM, with P27 as a separate uplink. The action view covers AGC power-up, antenna selection, Path A and P27 loads, R47 AGS init, P63/P64/P66 landing, P70/P71 abort, and probe/drogue docking.

![Apollo Interaction](apollo-int.svg)

![Apollo Actions](apollo-act.svg)

## Vehicle Interconnection

The vehicle interconnection keeps the same stack topology at a coarser grain: RSO destruct, KSC umbilicals, IU guidance, SLA, CM–SM, docking, USB, NASCOM, and recovery.

![Apollo Vehicle Interconnection](apollo-ibd-vehicle.svg)

## CSM and LM

CSM structure is CM (SCS, AGC_CM, two DSKYs, ECLSS, probe and latches) and SM (SPS, four RCS quads, three fuel cells). LM structure is descent (DPS, four AgZn, ECA) and ascent (PNGS, AGC_LM, AGS, APS, RCS, radars). The vehicles stay separate; there is no propellant crossfeed.

![CSM Definition](apollo-bdd-csm.svg)

![LM Definition](apollo-bdd-lm.svg)

![CSM Interconnection](apollo-ibd-csm.svg)

![LM Interconnection](apollo-ibd-lm.svg)

## AGC and GNC

There are two Block II AGCs. CM ropes are Comanche 055; LM ropes are Luminary 1A (LMY99/1). CMC P61–P67 is entry; LGC P63–P68 is landing. AGS is AEA + ASA + DEDA and is not a landing computer. IU LVDC stays off the AGC data path.

![AGC Definition](apollo-bdd-agc.svg)

![AGC Interconnection](apollo-ibd-agc.svg)

![GNC Interconnection](apollo-ibd-gnc.svg)

![AGS Interconnection](apollo-ibd-ags.svg)

![CMC Major Modes](apollo-stm-cmc.svg)

![LGC Major Modes](apollo-stm-lgc.svg)

![AGC CM States](apollo-stm-agc-cm.svg)

![AGC LM States](apollo-stm-agc-lm.svg)

![AGS States](apollo-stm-ags.svg)

![SCS Modes](apollo-stm-scs.svg)

## Ground, MSFN, and MCC

KSC LCC hands off to MCC at tower clear (Mission Rule 1-21). Apollo 11 flies from MOCR 2. MSFN is Goldstone, Madrid, and Honeysuckle plus NASCOM.

![MCC / RTCC](apollo-ibd-mcc.svg)

![MSFN Interconnection](apollo-ibd-msfn.svg)

![MSFN Definition](apollo-bdd-msfn.svg)

## Electrical Power

SM power is three fuel cells on a 2+2 cryo set. CM has three AgZn batteries, a charger, and two 117 V 400 Hz inverters. LM has six AgZn (four descent, two ascent) and an ECA on each stage. There is no stage-to-stage electrical power.

![EPS Definition](apollo-bdd-eps.svg)

![SM Fuel Cells](apollo-ibd-eps-sm.svg)

![CM Electrical Power](apollo-ibd-eps-cm.svg)

![LM Electrical Power](apollo-ibd-eps-lm.svg)

## RCS

SM RCS is 100 lbf per engine (Press Kit p.93), four quads. LM RCS is 100 lbf per engine (Press Kit p.106). CM RCS is two systems of six 93 lbf engines with no automatic translation.

![SM RCS Quads](apollo-ibd-rcs.svg)

![CM RCS Systems](apollo-ibd-rcs-cm.svg)

## Docking

The CM probe meets the LM drogue. Twelve ring latches take the stack from soft dock to hard dock; hardware is then removed for transfer. That sequence is a docking-mode machine, separate from the mission-phase dock/eject state.

![Docking Interconnection](apollo-ibd-dock.svg)

![Docking Mode](apollo-stm-dock.svg)

## ECLSS

Cabin atmosphere, suits, and thermal control stay on the CSM and LM environmental loops. The CM cabin is 5.0 psia O2.

![ECLSS Definition](apollo-bdd-eclss.svg)

![ECLSS Interconnection](apollo-ibd-eclss.svg)

![ECLSS States](apollo-stm-eclss.svg)

## Interfaces and Flows

USB numbers are sourced: CSM uplink 2106.40625 MHz, LM uplink 2101.802 MHz. VHF is 296.8 / 259.7 MHz; recovery is 243.0 MHz. The flow view is MCC → NASCOM → MSFN → CSM/LM, with a separate RSO destruct path.

![Apollo Interfaces](apollo-intf.svg)

![Apollo Flows](apollo-flow.svg)

## Constraints and Allocations

Constraints cover USB links, lunar delay (~1.3 s), F-1 thrust, AGC cycle time, and ignition mass. The allocation view binds the mappings in the Allocations section above.

![Apollo Constraints](apollo-cst.svg)

![Apollo Allocations](apollo-alloc.svg)

## Package and Trace Overview

Packages follow Saturn V, CSM, LM, crew, and ground. The general view traces a flown-mission use case to the sourced requirements and verification cases.

![Apollo Packages](apollo-pkg.svg)

![Apollo Cross-View Trace](apollo-general.svg)
