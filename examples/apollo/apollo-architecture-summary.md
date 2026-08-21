# Apollo Architecture

This document is the architecture and system-design description of the Apollo 11 / Block II system modeled in `apollo.sysml`. The example instance is Apollo 11 / AS-506 (SA-506): Saturn V serials S-IC-6 / S-II-6 / S-IVB-6N / IU-6 / SLA-14, CSM-107 *Columbia*, LM-5 *Eagle*. A reviewer should be able to understand purpose, context, requirements, structure, interfaces, behavior, and allocations without opening the model. Generated views appear after the written architecture.

This is an example model, not a certifiable vehicle. Numbers are from NASA primary sources cited in the model (Apollo 11 Press Kit 69-83K, Saturn V Flight Manual, Apollo Experience Reports, AGCIS / MIT IL, TN D-6718 / D-6724 / D-7082 / D-7143 / D-7375 / D-8093 / D-8227 / TN-7990). Values not in those extracts are left unmarked. There is no official CSM lunar Δv table in the sources used here — that table is not invented.

Hyphens are not legal identifiers: S-IC / S-II / S-IVB appear as `SIC`, `SII`, `SIVB`. The mission phase surface/EVA is `surfaceEVA`.

## 1. Purpose and Mission

Apollo 11 is a lunar-orbit-rendezvous (LOR) mission. Saturn V places the CSM and LM in Earth parking orbit. TLI sends the stack toward the Moon. After transposition, docking, and LM extract, the docked vehicles coast translunar. The CSM performs LOI and later TEI. The LM undocks, does DOI and powered descent, lands, supports one surface EVA, ascends, and rendezvous with the CSM. The crew returns in the CM for entry and recovery.

This is Apollo 11 only — first landing, one short EVA, no LRV, no SIM bay, P66 as the flown landing program, MOCR 2, SM cryo 2+2. J-mission variants are out of scope.

Crew safety in this model is not LES-only. LES is the pad / Mode I escape tower on the stack. Later-mode crew safety that is actually modeled: `AbortMode` (pad, I–IV, contingency TLI, lunar, SPS); RSO UHF destruct (outside MCC, safed after Earth orbit); CM heat shield for entry; ECLSS / A7L / PLSS; and recover-crew to *Hornet*. There is no single `crewSafetyRequirement` element.

## 2. Operating Context

The stack sits among first-class parts, not one Ground actor.

| Part | Role |
|------|------|
| CDR / CMP / LMP | Flight crew. CDR (Armstrong) and LMP (Aldrin) carry PLSS for EVA. CMP has no PLSS in the model. |
| KSC LC-39 / `KSC_LCC` | Launch commit: Firing Room 1, RCA 110A pair, ACE, umbilicals, pad cryo |
| MCC Houston | Flight control after tower clear. Apollo 11 uses **MOCR 2**. |
| RTCC | Five IBM 360/75. Trajectory and uplink. MOC vs DSC roles on A11 are unmarked. |
| GSFC / NASCOM | Ground wideband network |
| MSFN | Goldstone / Madrid / Honeysuckle 85-ft USB triad, plus named 30-ft, ships (collapsed), ARIA |
| AFETR range safety (`RSO`) | UHF destruct, **outside MCC**, safed after Earth orbit |
| TF-130 / USS *Hornet* (CV-12) | Recovery. Splash 195:18:35 MET, 13 nmi from target |
| Earth / Moon | Celestial context |

Handoff is KSC → MCC at tower clear — **Mission Rule 1-21**. RSO is not MCC.

Context flows: MCC → MSFN (Path A / voice); RSO → vehicle (destruct UHF, not via MCC); MSFN ↔ Earth (USB / 210-ft / Parkes); MSFN ↔ Moon (~1.3 s lunar delay).

## 3. Stakeholders and Use Cases

| Stakeholder | Associated use cases |
|-------------|----------------------|
| CDR, MCC | Fly Mission (includes Lunar EVA) |
| CDR | Lunar EVA |
| MCC | Recover Crew |
| RSO | Range Safety |

**Analysis cases:** USB link analysis (`usbCsmLink` → CSM USB requirement); consumable analysis (CM ECS requirement).

**Verification cases** (names only — no part, port, or effect is bound): `verifyUsbCsm`, `verifyA7l`, `verifyP27`, `verifyRso`.

## 4. Requirements

The model states sourced requirements as documentation on named requirement elements. Conflicts are cited both ways with no silent winner.

### Mass and propellant (A11 Press Kit p.109)

| Item | Sourced value |
|------|---------------|
| S-IC-6 | 5,022,674 lb fueled / 288,750 lb dry; LOX 3,307,855; RP-1 1,426,069; liftoff **7,653,854 lbf** |
| S-II-6 | 1,059,171 / 79,918; LOX 821,022; LH2 158,221 |
| S-IVB-6N | 260,523 / 25,000; LOX 192,023; LH2 43,500 |
| IU-6 | 4,306 lb |
| CM | 12,250 lb |
| SM | 51,243 lb |
| Also PK | Ignition 6,484,280 lb; first motion 6,398,535; LES 8,930; LM descent dry 4,483; LM RCS 604; DPS load 18,100; APS load 5,214 |

### Engines

| Engine | Source A | Source B |
|--------|----------|----------|
| SPS | 20,500 lbf (Press Kit) | 21,500 lbf vac (TN D-7375) |
| DPS | 9,870 / 1,050–6,300 lbf (Press Kit) | 10,500 lbf 10:1 (TN D-7143) |
| APS | 3,500 lbf; 90% in 0.450 s; **1.5° cant** (TN D-7082) | — |
| F-1 ×5 | 1,530,000 lbf each, sourced as **SA-507**, not AS-506 | hydraulics collapsed |
| J-2 S-II ×5 | 230,000 lbf | — |
| J-2 S-IVB ×1 | 207,000 lbf | — |

### RCS

SM 100 lbf/engine (PK p.93), four quads. LM 100 lbf/engine (PK p.106). CM 93 lbf/engine; two systems of six; no automatic translation.

### Guidance computers

| System | Sourced parameters | Source |
|--------|-------------------|--------|
| AGC (two: `AGC_CM`, `AGC_LM`) | Block II 16-bit; 2048 E / 36864 F; 1.024 MHz; MCT **11.7 µs**; 65 lb / 70 W. CM = 1 AGC + 2 DSKY. LM = 1 AGC + 1 DSKY | AGCIS 30 |
| A11 ropes | Comanche **055** on AGC_CM; Luminary **1A LMY99/1** on AGC_LM | `agcRequirement` |
| P-numbers | CMC P61–P67 = **entry**; LGC P63–P68 = **landing**. Not one shared P-number machine | `agcRequirement` |
| PIPA | CM 5.85 cm/s/pulse; LM 1.0 cm/s/pulse | `pipaRequirement` |
| IU LVDC | 82.03125 µs; 26+2 bits; **no digital AGC↔LVDC**. IU owns boost + TLI | `iuGncRequirement` |
| AGS | AEA + ASA + DEDA; AEA 4096×18, 5 µs, 32.7 lb; **not a landing computer**. R47 inits from PNGS | TN-7990 |

V37 mode, V36 fresh start, V69 restart. 1201/1202 is executive overflow, not an abort.

### Electrical power (Press Kit)

SM: FC1–FC3; cryo **2+2** (not J-mission 3+3). CM: AgZn1–3 + charger; two 117 V 400 Hz inverters. LM: six AgZn (4 descent / 2 ascent) + ECA each. Bus 28 V DC. **No stage-to-stage electrical power. No CSM–LM propellant crossfeed.**

### Communications

| Link | Sourced parameters |
|------|-------------------|
| USB CSM | Uplink 2106.40625 MHz; PM down 2287.5; FM down 2272.5; PCM 51.2 or 1.6 kbps; uplink digital ~2 kbps; PRN range 992 kbps, ±15 m, ~540,000 mi unambiguous |
| USB LM | Uplink 2101.802 MHz; down 2282.5; steerable 20.5 dB tx; amplitron 20 W; no simultaneous PM+FM |
| CSM HGA | Wide 8.0 / med 18.0 / narrow 25.7 dB; PA 11.2 W PM / 12.6 W FM; **crew-selected**, not ground-commandable on Block II |
| Path A | FC → CCC → RTCC → CCATS → site 642B → USB 70 kHz |
| P27 | Verbs **V70–V73 only**; separate from CCATS |
| VHF | 296.8 / 259.7 MHz |
| Recovery | 243.0 MHz |

### ECLSS, EVA, orbit, timing

| Parameter | Value |
|-----------|-------|
| CM cabin | 5.0 psia 100% O2; CO2 ≤ 7.6 torr |
| CM spec vs A11 | 3 crew / 14 d spec; A11 **196 h** vs 336 h spec |
| SM O2 / water | 640 lb O2; potable 36 lb / waste 56 lb |
| LiOH | 1.5 man-day; swap 12 h |
| LM-5 descent O2 | ~48 lb — **2800 psi vs 3000 psi, both cited** |
| LM-5 ascent O2 | ~2.4 lb ×2 |
| LM-5 water | descent 332 lb; ascent 42 lb ×2 |
| LCG | 1200 Btu/man-h steady |
| A7L | 3.75±0.25 psid; EV 19.69 kg |
| PLSS | usable O2 1.04 lb / 4 h at 1200 Btu/h |
| Food plan | 2200±300 kcal/d (A11 actual intake unmarked) |
| Earth parking orbit | **100 nmi planned** |
| Lunar delay | range/c ≈ 1.3 s |
| EVA | one surface EVA; CDR 2:48 / LMP 2:40 (**flown** A11 instance) |
| TLI / dock / extract / LOI-1 | **planned GET** (A11 Press Kit): TLI 02:44:15; dock ~03:20; extract ~04:09; LOI-1 75:54:28 |
| Splash | 195:18:35 MET, 13 nmi, *Hornet* — model does not mark planned or flown |
| Landing program | **P66 flown** |

Docking: TD&E is its own GO/NO-GO, CMP-owned, SM RCS. CM probe / LM drogue + 12 ring latches. LM stays in the SLA until `dockEject` (after TLI, before translunar coast).

### Unmarked (do not invent)

- CSM lunar Δv (no official table in the sources used)
- SPS loaded mass
- SM/CM RCS loaded propellant mass
- RCS Δv table
- A11 AGS flight-program name
- A11 actual food intake (kcal)
- Entry blackout duration
- RTCC MOC vs DSC which-is-which on A11
- Complete MSFN 30-ft inventory (ships collapsed)
- Full SCS switch deck (TBD in the model)
- CMP personal name (not in the model)

## 5. Structure

```
Apollo11
├── SaturnV
│   ├── SIC → F1          S-IC-6
│   ├── SII → J2          S-II-6
│   ├── SIVB → J2         S-IVB-6N
│   ├── IU → LVDC         IU-6
│   ├── SLA               SLA-14; four petals; LM extract after transposition
│   └── LES
├── CSM
│   ├── CM                12,250 lb
│   │   ├── SCS → BMAG, TVC, RHC
│   │   ├── AGC_CM → erasable, fixed, oscillator, Comanche055
│   │   ├── IMU, DSKY, DSKY2
│   │   ├── RCS → systemA, systemB
│   │   ├── ECLSS → oxygen, water, LiOH, suit circuit
│   │   ├── USB, EMS
│   │   ├── AgZn1–3, charger, inverter1–2
│   │   └── probe, ringLatches (12)
│   └── SM                51,243 lb; SPS load unmarked; cryo 2+2
│       ├── SPS
│       ├── RCS → quadA–D
│       └── FC1–FC3
├── LM
│   ├── descent → DPS, AgZn1–4, ECA
│   └── ascent
│       ├── PNGS → IMU, landingRadar, rendezvousRadar
│       ├── AGC_LM → erasable, fixed, oscillator, Luminary1A
│       ├── AGS → AEA, ASA, DEDA
│       ├── APS, RCS, DSKY, USB, drogue
│       └── AgZn1–2, ECA
├── Crew → CDR (A7L, PLSS), CMP (A7L), LMP (A7L, PLSS)
├── Ground → KSC_LCC, MCC (RTCC, MOCR2, CCATS; FLIGHT, CAPCOM, EECOM, CCC, FDO), MSFN, NASCOM
├── RSO
└── recovery → Hornet
```

Pad stack: S-IC-6, S-II-6, S-IVB-6N, IU-6, SLA-14 (LM-5), SM, CM, LES.

Keep two AGCs, AGS, IU LVDC, LES, descent vs ascent, and three crew. PNGS is AGC_LM + IMU + radars — not AGS. SCS is the Block II analog backup to AGC_CM.

Mechanical stack: SIC → SII → SIVB → IU → SLA → SM; LES → CM → SM; SLA → LM descent; CM probe ↔ LM drogue; descent ↔ ascent mate.

## 6. Interfaces and Interconnections

| From | To | Why |
|------|----|-----|
| RSO | S-IC | UHF destruct — outside MCC |
| KSC_LCC | S-IC | Pad umbilicals |
| KSC_LCC | MCC | Voice handoff at tower clear (Mission Rule 1-21) |
| IU LVDC | S-IC, S-II, S-IVB | Boost and TLI guidance |
| MSFN | CM, LM | USB |
| NASCOM | Ground, MCC | Wideband |
| MCC CCATS | MSFN 642B | Path A command uplink |
| Separate P27 path | AGC | V70–V73 only |
| Recovery | CM | 243.0 MHz |
| CM probe + 12 latches | LM drogue | Soft then hard dock; hardware removed for transfer |

Port types: UHF destruct, umbilical, voice, guidance, mechanical, docking, USB, NASCOM, command, recovery.

Isolation: no stage-to-stage electrical power; no CSM–LM propellant crossfeed.

## 7. Behavior

### Mission phases (`MissionPhase`)

```
countdown → boost → earthOrbit → TLI → dockEject → translunar → LOI → undock → DOI → descent → surfaceEVA → ascent → rendezvous → TEI → entry → recovery
```

| Trigger | From → to |
|---------|-----------|
| `towerClear` | countdown → boost |
| `orbitalInsertion` (SECO) | boost → earthOrbit |
| `tliBurn` | earthOrbit → TLI |
| `tliComplete` | TLI → dockEject |
| `lmExtract` | dockEject → translunar |
| `loiBurn` (SPS) | translunar → LOI |
| `lunarOrbit` | LOI → undock |
| `doiBurn` (DPS) | undock → DOI |
| `p63` | DOI → descent |
| `p68` | descent → surfaceEVA |
| `p12` | surfaceEVA → ascent |
| `p30` | ascent → rendezvous |
| `teiBurn` (SPS) | rendezvous → TEI |
| `ei` | TEI → entry |
| `recoveryForce` | entry → recovery |

`dockEject` is after TLI and before translunar coast. **Planned GET** (A11 Press Kit): TLI 02:44:15, dock ~03:20, extract ~04:09, then coast, LOI-1 75:54:28. Those times are not labeled flown. P66 is the flown landing program.

### Abort modes (`AbortMode`)

Parallel to the nominal machine: pad, I, II, III, IV, contingency TLI, lunar, SPS.

### Computer mode machines (separate)

- **CMC entry:** P61 → P62 → P63 → P64 → P65 → P66 → P67 (entry only).
- **LGC landing:** P63 → P64 → {P65 | P66} → P67 → P68 (landing only). Apollo 11 flew **P66**.
- **AGC_CM modes:** P00, P11, P20, P27, P40, P51, P52 plus V37 / V36 / V69 / 1201/1202.
- **AGC_LM modes:** P00, P12, P20, P27, P30, P70, P71 plus the same verb/alarm pattern; P70 → P71 abort chain.
- **SCS:** AGC_CM ↔ attitude hold / rate command / min impulse; crew selects AGC_CM vs SCS.
- **AGS:** idle → operate (R47 from PNGS) → follow PNGS → idle. AGS does not land.
- **ECLSS:** cabin → suit → EVA (PLSS) → cabin.
- **Docking mode** (not the mission `dockEject` state): undocked → soft (probe capture) → hard (twelve latches) → hardware off (transfer prep).

### Actions

AGC power-up (CM and LM), antenna selection, Path A load, P27 load, R47 AGS init, P63 braking, P64 approach, P66 landing, P70/P71 abort, soft dock, hard dock, remove docking hardware.

## 8. Allocations

| Function | Allocated to |
|----------|--------------|
| Boost, TLI | IU LVDC |
| Destruct | RSO (outside MCC) |
| LOI / TEI / entry | AGC_CM |
| Landing / ascent / LM abort | AGC_LM |
| Backup attitude | AGS — does not land |
| Atmosphere / thermal | ECLSS |
| EVA | EMU (A7L + PLSS) |
| Trajectory / uplink | RTCC |
| RF | MSFN |
| Launch commit | KSC_LCC |
| Flight direction after handoff | FLIGHT (MOCR) |
| Heat shield | CM only (entry) |
| Pad / Mode I escape | LES |
| Later-mode abort | `AbortMode` I–IV, contingency TLI, lunar, SPS — not LES |
| Path A | CCATS |
| Path B | P27 |
| EPS | SM fuel cells, CM AgZn, LM descent AgZn |
| Docking | CM probe, LM drogue |
| RCS | SM quads, CM systems |

Allocation names in the model: `allocateBoostToIU`, `allocateTliToIU`, `allocateDestructToRSO`, `allocateAGC_CMToCM`, `allocateAGC_LMToLM`, `allocateAGSToLM`, `allocateLVDCToIU`, `allocatePathAToCCATS`, `allocatePathBToP27`, `allocateEPSToSM`, `allocateEPSToCM`, `allocateEPSToDescent`, `allocateDockToCM`, `allocateDockToLM`, `allocateRCSToSM`, `allocateRCSToCM`.

## 9. Parameters, Constraints, and Scope

Named constraints: `usbCsmLink`, `usbLmLink`, `lunarDelay`, `f1Thrust`, `agcCycle`, `a11IgnitionMass`.

| Parameter | Value |
|-----------|-------|
| CSM USB uplink | 2106.40625 MHz |
| CSM PM downlink | 2287.5 MHz |
| LM USB uplink | 2101.802 MHz |
| Lunar delay | ~1.3 s |
| F-1 | 1,530,000 lbf — **SA-507 citation, not an AS-506 requirement** |
| AGC MCT | 11.7 µs |
| Ignition mass | 6,484,280 lb |
| Earth parking orbit | 100 nmi |

**In scope:** Apollo 11 / Block II / AS-506.

**Out of scope:** J-mission 3+3 cryo, LRV, SIM bay, extended EVA. F-1 1,530,000 lbf is an SA-507 citation, not an AS-506 figure.

**Unmarked / TBD:** CSM lunar Δv, SPS loaded mass, SM/CM RCS loaded propellant mass. See also §4 (AGS flight-program name, A11 food intake, entry blackout, RTCC MOC/DSC, 30-ft MSFN inventory, SCS switch deck).

## 10. Open Risks

- CSM lunar Δv, SPS loaded mass, and SM/CM RCS loaded propellant mass stay unmarked. There is no official CSM lunar Δv table in the sources used here.
- F-1 1,530,000 lbf is an SA-507 citation. It is not an AS-506 requirement.
- A11 AGS flight-program name, A11 actual food intake, entry blackout duration, RTCC MOC vs DSC on A11, and the complete 30-ft MSFN inventory stay unmarked.
- Verification cases are names only.

---

## Generated Views

The figures below are the generated SysMLD views for this model. They illustrate the architecture above; they do not replace it.

### System Views

Context, sourced requirements, the pad-stack definition, the vehicle interconnection, and the two state machines are the system grain.

![Apollo Operating Context](apollo-context.svg)

![Apollo Requirements](apollo-req.svg)

![Apollo Definition](apollo-bdd.svg)

![Apollo Interconnection](apollo-ibd.svg)

![Apollo Mission Phases](apollo-stm.svg)

![Apollo Abort Modes](apollo-stm-abort.svg)

### Cases

Fly Mission includes the lunar EVA. Recover Crew and Range Safety sit beside it. Analysis cases are `usbLinkAnalysis` and `consumableAnalysis`. Verification cases are names only.

![Apollo Use Cases](apollo-uc.svg)

![Apollo Analysis Cases](apollo-acase.svg)

![Apollo Verification Cases](apollo-vcase.svg)

### Interaction and Action

Command loads and voice travel MCC → CCATS → MSFN → CSM, with P27 as a separate uplink. The action view covers AGC power-up, antenna selection, Path A and P27 loads, R47 AGS init, P63/P64/P66 landing, P70/P71 abort, and probe/drogue docking.

![Apollo Interaction](apollo-int.svg)

![Apollo Actions](apollo-act.svg)

### Vehicle Interconnection

The vehicle interconnection keeps the same stack topology at a coarser grain: RSO destruct, KSC umbilicals, IU guidance, SLA, CM–SM, docking, USB, NASCOM, and recovery.

![Apollo Vehicle Interconnection](apollo-ibd-vehicle.svg)

### CSM and LM

CSM structure is CM (SCS, AGC_CM, two DSKYs, ECLSS, probe and latches) and SM (SPS, four RCS quads, three fuel cells). LM structure is descent (DPS, four AgZn, ECA) and ascent (PNGS, AGC_LM, AGS, APS, RCS, radars). The vehicles stay separate; there is no propellant crossfeed.

![CSM Definition](apollo-bdd-csm.svg)

![LM Definition](apollo-bdd-lm.svg)

![CSM Interconnection](apollo-ibd-csm.svg)

![LM Interconnection](apollo-ibd-lm.svg)

### AGC and GNC

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

### Ground, MSFN, and MCC

KSC LCC hands off to MCC at tower clear (Mission Rule 1-21). Apollo 11 flies from MOCR 2. MSFN is Goldstone, Madrid, and Honeysuckle plus NASCOM.

![MCC / RTCC](apollo-ibd-mcc.svg)

![MSFN Interconnection](apollo-ibd-msfn.svg)

![MSFN Definition](apollo-bdd-msfn.svg)

### Electrical Power

SM power is three fuel cells on a 2+2 cryo set. CM has three AgZn batteries, a charger, and two 117 V 400 Hz inverters. LM has six AgZn (four descent, two ascent) and an ECA on each stage. There is no stage-to-stage electrical power.

![EPS Definition](apollo-bdd-eps.svg)

![SM Fuel Cells](apollo-ibd-eps-sm.svg)

![CM Electrical Power](apollo-ibd-eps-cm.svg)

![LM Electrical Power](apollo-ibd-eps-lm.svg)

### RCS

SM RCS is 100 lbf per engine (Press Kit p.93), four quads. LM RCS is 100 lbf per engine (Press Kit p.106). CM RCS is two systems of six 93 lbf engines with no automatic translation.

![SM RCS Quads](apollo-ibd-rcs.svg)

![CM RCS Systems](apollo-ibd-rcs-cm.svg)

### Docking

The CM probe meets the LM drogue. Twelve ring latches take the stack from soft dock to hard dock; hardware is then removed for transfer. That sequence is a docking-mode machine, separate from the mission-phase dock/eject state.

![Docking Interconnection](apollo-ibd-dock.svg)

![Docking Mode](apollo-stm-dock.svg)

### ECLSS

Cabin atmosphere, suits, and thermal control stay on the CSM and LM environmental loops. The CM cabin is 5.0 psia O2.

![ECLSS Definition](apollo-bdd-eclss.svg)

![ECLSS Interconnection](apollo-ibd-eclss.svg)

![ECLSS States](apollo-stm-eclss.svg)

### Interfaces and Flows

USB numbers are sourced: CSM uplink 2106.40625 MHz, LM uplink 2101.802 MHz. VHF is 296.8 / 259.7 MHz; recovery is 243.0 MHz. The flow view is MCC → NASCOM → MSFN → CSM/LM, with a separate RSO destruct path.

![Apollo Interfaces](apollo-intf.svg)

![Apollo Flows](apollo-flow.svg)

### Constraints and Allocations

Constraints cover USB links, lunar delay (~1.3 s), F-1 thrust, AGC cycle time, and ignition mass. The allocation view binds the mappings in the Allocations section above.

![Apollo Constraints](apollo-cst.svg)

![Apollo Allocations](apollo-alloc.svg)

### Package and Trace Overview

Packages follow Saturn V, CSM, LM, crew, and ground. The general view traces a flown-mission use case to the sourced requirements and verification cases.

![Apollo Packages](apollo-pkg.svg)

![Apollo Cross-View Trace](apollo-general.svg)
