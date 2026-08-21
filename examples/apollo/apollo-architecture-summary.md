# Apollo Architecture

Apollo 11 is one mission. The as-flown stack is still several vehicles, two guidance computers, and a Houston control room that does not own the destruct button.

This paper walks that stack from the Systems Modeling Language (SysML) model in `apollo.sysml`. When a generated view disagrees with the model, the model wins. Numbers appear only when the model already has them. This is an **example model, not a certifiable** vehicle.

The portrait below is NASA photograph 69-HC-620 (National Aeronautics and Space Administration [NASA], 1969a). Saturn-Apollo 506 (SA-506) is rolling to Pad 39-A on 20 May 1969. It is the real vehicle, not a generated view.

![Saturn V SA-506 / Apollo 11 rolled out to Pad 39-A, 20 May 1969. Credit: NASA photo 69-HC-620 (public domain). This is the system portrait, not a generated SysMLD view.](apollo-sa506-rollout.jpg)

*Saturn V SA-506 / Apollo 11 rolled out to Pad 39-A, 20 May 1969. Credit: NASA photo 69-HC-620 (public domain). This is the system portrait, not a generated SysMLD view.*

## One-page overview

This paper is not a Department of Defense Architecture Framework (DoDAF) product set. There are no Operational View / Systems View / Technical View (OV / SV / TV) products and no capability taxonomies. The first page states who the instance is for, why the architecture exists, what the stack is, and the mission thread.

The instance is Apollo 11 / Apollo-Saturn 506 (AS-506), as-flown July 1969. The readers are anyone who will stay with a ninth-grade history paper and still check a cite. Launch is from the Kennedy Space Center (KSC). After tower clear, Mission Control Center (MCC) Houston sits in Mission Operations Control Room (MOCR) 2. The Manned Space Flight Network (MSFN) talks to the stack. The Range Safety Officer (RSO) sits outside MCC. Recovery is to USS *Hornet*. Earth and Moon are context.

The purpose is to show how the as-flown system worked, not how a poster remembers it. After the first page the paper takes the problem first, then the design, then the holes that stay unmarked.

The stack is Saturn V serials S-IC-6 / S-II-6 / S-IVB-6N / Instrument Unit (IU)-6 / Spacecraft-LM Adapter (SLA)-14, Command/Service Module (CSM) CSM-107 *Columbia*, and Lunar Module (LM) LM-5 *Eagle*. In scope: first landing, one short surface Extravehicular Activity (EVA), model PNGS (cockpit/switch label Primary Guidance, Navigation, and Control System (PGNCS)) program P66 as the flown landing program, and Service Module (SM) cryogenic tankage 2+2. Out of scope: later J-mission variants, Lunar Roving Vehicle (LRV), Scientific Instrument Module (SIM) bay, extended EVA, and invented change-in-velocity (Δv) tables.

The mission thread is lunar-orbit rendezvous. Three crew fly. Two land. All three come home. Saturn V places the CSM and the LM in Earth parking orbit. Translunar Injection (TLI) sends the stack toward the Moon. After transposition, docking, and LM extract (`dockEject`), the docked vehicles coast. The CSM burns Lunar Orbit Insertion (LOI) and later Trans-Earth Injection (TEI). The LM undocks, burns Descent Orbit Insertion (DOI), lands two crew, supports one surface EVA, ascends, and meets the CSM. The Command Module (CM) brings all three home.

The paper thinks about the problem first, then the design. That spine is simplified MagicGrid. NASA Procedural Requirements (NPR 7123.1) maps onto it as Who needs what, The shalls, Jobs asked of the stack, What the design does in time, The parts, The serialed hardware, Sourced numbers, and Named checks. Those rows are not NPR 7123 product titles.

Hyphens are not legal identifiers in the model. S-IC / S-II / S-IVB appear as `SIC`, `SII`, `SIVB`. ST-124 appears as `ST124`. Surface EVA is `surfaceEVA`.

## Problem domain

The problem domain is who needed a job from the stack, and which sourced shalls the model actually states. Wiring comes later.

The national job is to land two people on the Moon and return three. This instance is Apollo 11 only: first landing, one short EVA, no rover, no SIM bay. The flown landing program is P66. MCC sits in MOCR 2. SM cryo is 2+2, not the later J-mission 3+3.

Crew safety is not Launch Escape System (LES)-only. LES is the pad and Mode I escape tower. Later-mode safety that the model actually has includes `AbortMode` (pad, I–IV, contingency TLI, lunar, Service Propulsion System (SPS)); RSO ultra-high-frequency (UHF) destruct outside MCC, safed after Earth orbit; the CM heat shield; Environmental Control and Life Support System (ECLSS); A7L pressure garment; Portable Life Support System (PLSS); and recover-crew to *Hornet*. There is no single `crewSafetyRequirement` element.

The stack sits among first-class parts, not one Ground actor. The operating-context figure shows crew, KSC, MCC, the tracking net, RSO, recovery, Earth, and Moon. RSO destruct does not pass through MCC.

![Apollo operating context](apollo-context.svg)

*Apollo operating context. The vehicles sit inside a world; RSO destruct does not route through Houston.*

A Stakeholder here is a person or organization that asks a job of the stack. The Commander (CDR) Armstrong and Lunar Module Pilot (LMP) Aldrin associate with Fly Mission and Lunar EVA and carry PLSS for EVA. The Command Module Pilot (CMP) has no PLSS in the model; the CMP personal name is unmarked. KSC Launch Control Center (`KSC_LCC`) owns launch commit from Firing Room 1, with the RCA 110A pair, Acceptance Checkout Equipment (ACE), umbilicals, and pad cryo, and is context rather than a use-case actor. MCC owns Fly Mission and Recover Crew after tower clear under Mission Rule 1-21; MCC is not a midcourse-correction burn. The Real-Time Computer Complex (RTCC) is five IBM 360/75 machines for trajectory and uplink; Mission Operations Computer (MOC) versus Dynamic Standby Computer (DSC) roles on A11 are unmarked. Goddard Space Flight Center (GSFC) and the NASA Communications Network (NASCOM) carry ground wideband. MSFN is the Goldstone / Madrid / Honeysuckle 85-ft Unified S-Band (USB) triad, plus named 30-ft sites, ships (collapsed), and Apollo Range Instrumentation Aircraft (ARIA). Air Force Eastern Test Range (AFETR) RSO owns Range Safety: UHF destruct, outside MCC, safed after Earth orbit. TF-130 / USS *Hornet* (CV-12) recovers the crew. Splash is flown 195:18:35 GET. Distance is 13 nmi from USS *Hornet*, not from the target. The weather-revised miss is ~1.7 nmi.

Fly Mission is primary. CDR and MCC associate with it. Fly Mission **Includes** Lunar EVA. Recover Crew belongs to MCC. Range Safety belongs to RSO and stays separate from Fly Mission. Analysis cases are names only, with no equations and no results: USB link analysis (`usbLinkAnalysis`) and consumable analysis (`consumableAnalysis`). Verification cases are names only; none binds a part, port, or effect: `verifyUsbCsm`, `verifyA7l`, `verifyP27`, `verifyRso`.

The use-case figure is three actors and four ellipses. The dashed include arrow is Fly Mission to Lunar EVA.

![Apollo use cases](apollo-uc.svg)

*Apollo use cases. Fly Mission includes Lunar EVA; Range Safety stays with RSO.*

Context flows the model names are MCC to MSFN (Path A / voice); RSO to the vehicle on destruct UHF, not via MCC; MSFN to Earth on USB / 210-ft / Parkes; and MSFN to the Moon at about 1.3 s lunar delay.

### Sourced shalls

The model states sourced requirements as documentation on named requirement elements. Engine thrust conflicts are cited with no silent winner and no required thrust. A generated box is not a shall.

Press Kit 69-83K page 109 gives the A11 tank loads and does not turn them into a required-mass shall (NASA, 1969b): S-IC-6 is 5,022,674 lb fueled / 288,750 lb dry, liquid oxygen (LOX) 3,307,855, RP-1 1,426,069, liftoff 7,653,854 lbf; S-II-6 is 1,059,171 / 79,918 with LOX 821,022 and liquid hydrogen (LH2) 158,221; S-IVB-6N is 260,523 / 25,000 with LOX 192,023 and LH2 43,500; IU-6 is 4,306 lb; CM is 12,250 lb; SM is 51,243 lb. The same kit also lists ignition 6,484,280 lb, first motion 6,398,535, LES 8,930, LM descent dry 4,483, LM Reaction Control System (RCS) 604, Descent Propulsion System (DPS) load 18,100, and LM Ascent Propulsion System (APS) load 5,214 (the engine, not the S-IVB Auxiliary Propulsion System / ullage motors).

The engine table is the number fight. There is no required thrust. SPS and DPS cites stay; the model does not pick a winner and does not add a shall. LMA790 (a Grumman Lunar Module document number) is the third DPS cite (NASA, 1969b; NASA, 1973c; NASA, 1973b).

| Engine | Source A | Source B | Source C |
|--------|----------|----------|----------|
| SPS | 20,500 lbf (Press Kit) | 21,500 lbf vac (TN D-7375) | — |
| DPS | 9,870 / 1,050–6,300 lbf (Press Kit) | 10,500 lbf 10:1 (TN D-7143) | 9,870 / 1,050–6,800 lbf (LMA790) |

LM APS is 3,500 lbf, 90% in 0.450 s, 1.5° cant (NASA, 1973a, Technical Note D-7082). F-1 ×5 is 1,530,000 lbf each, sourced as SA-507, not AS-506; F-1 hydraulics are collapsed. J-2 is 230,000 lbf on S-II ×5 and 207,000 lbf on S-IVB ×1.

SM RCS is 100 lbf/engine (NASA, 1969b, p. 93), four quads. LM RCS is 100 lbf/engine (NASA, 1969b, p. 106). CM RCS is 93 lbf/engine, two systems of six, no automatic translation. Loaded SM/CM RCS propellant mass is unmarked.

There are two Apollo Guidance Computers (AGC): `AGC_CM` and `AGC_LM`. Block II is 16-bit, 2048 erasable / 36864 fixed, 1.024 MHz, memory cycle time (MCT) 11.7 µs, 65 lb / 70 W (AGCIS 30). The CM is 1 AGC + 2 Display and Keyboard (DSKY). The LM is 1 AGC + 1 DSKY. A11 ropes are Comanche 055 on AGC_CM and Luminary 1A LMY99/1 on AGC_LM. Command Module Computer (CMC) P61–P67 is entry. Lunar Module Guidance Computer (LGC) P63–P68 is landing. Those are not one shared P-number machine. Pulse Integrating Pendulous Accelerometer (PIPA) scale is CM 5.85 cm/s/pulse versus LM 1.0 cm/s/pulse. The IU is physically LVDC + ST-124 + Flight Control Computer (FCC); LVDC is 82.03125 µs, 26+2 bits, with no digital AGC↔LVDC, and the IU owns boost + TLI. Abort Guidance System (AGS) is Abort Electronics Assembly (AEA) + Abort Sensor Assembly (ASA) + Data Entry and Display Assembly (DEDA): AEA 4096×18, 5 µs, 32.7 lb, not a landing computer (Kurten, 1975, Technical Note D-7990). AGS ≠ DSKY; AGS display is DEDA. R47 inits AGS from PNGS. Verb 37 (V37) is mode, V36 is fresh start, V69 is restart. 1201/1202 is executive overflow, not an abort.

PNGS is AGC_LM + Inertial Measurement Unit (IMU) + radars, not AGS. Physical `landingRadar` is on descent only. One `rendezvousRadar` is on ascent only. PNGS connects to both and does not nest either radar.

Electrical power in the Press Kit is SM fuel cells FC1–FC3 with cryo 2+2; CM silver-zinc (AgZn) 1–3 plus charger and two 117 V 400 Hz inverters; LM six AgZn (4 descent / 2 ascent) plus Electrical Control Assembly (ECA) each; bus 28 V DC (NASA, 1969b). There is no stage-to-stage electrical power and no CSM–LM propellant crossfeed.

USB CSM is uplink 2106.40625 MHz, phase modulation (PM) down 2287.5, frequency modulation (FM) down 2272.5, pulse-code modulation (PCM) 51.2 or 1.6 kbps, uplink digital about 2 kbps, pseudo-random noise (PRN) range 992 kbps, ±15 m, about 540,000 mi unambiguous. USB LM is uplink 2101.802 MHz, down 2282.5, steerable 20.5 dB transmit, amplitron 20 W, no simultaneous PM+FM. CSM High-Gain Antenna (HGA) is wide 8.0 / medium 18.0 / narrow 25.7 dB, power amplifier 11.2 W PM / 12.6 W FM, crew-selected, not ground-commandable on Block II. Path A is Flight Controller (FC) → Command and Communications Controller (CCC) → RTCC → Communications, Command, and Telemetry System (CCATS) → site 642B → USB 70 kHz. P27 is verbs V70–V73 only, separate from CCATS. Very High Frequency (VHF) is 296.8 / 259.7 MHz. Recovery is 243.0 MHz.

CM cabin is 5.0 psia 100% O2, carbon dioxide (CO2) ≤ 7.6 torr. The CM spec is 3 crew / 14 d; A11 is 196 h versus 336 h spec. SM holds 640 lb O2, potable 36 lb / waste 56 lb. Lithium hydroxide (LiOH) is 1.5 man-day, swap 12 h. LM-5 descent O2 is about 48 lb — teaching figure 2800 psi; 3000 psi D-6724 is the other text; no required pressure (NASA, 1972, Technical Note D-6724). LM-5 ascent O2 is about 2.4 lb ×2. Water is descent 332 lb and ascent 42 lb ×2. Liquid Cooling Garment (LCG) is 1200 Btu/man-h steady. A7L is 3.75±0.25 psid, extravehicular 19.69 kg. PLSS usable O2 is 1.04 lb / 4 h at 1200 Btu/h. Food is TN D-7720 April 1967 plan baseline: 2800 kcal/man/day CM, 3200 kcal/man/day LM, not A11 flown intake (Smith et al., 1974). Earth parking orbit is 100 nmi planned. One surface EVA: CDR 2:48 / LMP 2:40 (Technical Note D-8093 Table I). Not the Public Affairs Office (PAO) hatch-to-hatch 2:31:40 (Lutz et al., 1975). Transposition, docking, and extraction (TD&E) is about 03:20–04:09 planned, CMP-owned, SM RCS, CM probe / LM drogue + 12 ring latches. The LM stays in the SLA — 8 panels (4 jettison / 4 stay) — until `dockEject` after TLI and before translunar coast. Landing program is P66 flown.

TLI Ground Elapsed Time (GET) has three labels only.

| TLI label | GET | Source |
|-----------|-----|--------|
| Planned | 02:44:15 GET | Press Kit (NASA, 1969b) |
| Planned | 2:44:26 GET | A11-FP (NASA Manned Spacecraft Center, 1969) |
| Flown | 02:44:16 GET | MSC-00171 (NASA, 1969c) |

Planned LOI-1 is 75:54:28 GET. A11-FP is the **only planned source**. Flown LOI-1 is ~075:49:50 GET (PAD / Mission Report). Two LOI-1 numbers only.

The requirements figure follows that model text. A view label is not a requirement.

![Apollo requirements](apollo-req.svg)

*Apollo requirements. Boxes repeat model text; they do not invent a shall or a third LOI-1 time.*

## Solution domain

The solution domain is how the stack is built, what connects, and how the flight ran.

The pad stack from the ground up is S-IC-6, S-II-6, S-IVB-6N, IU-6, SLA-14 with LM-5 inside, SM, CM, and LES. The system-definition figure is a composition tree: Saturn V, CSM, LM, Crew, and Ground stay separate. IU children are LVDC, ST-124, and FCC. SLA is eight-panel. Descent and ascent stay separate. Two AGCs stay separate.

![Apollo system definition](apollo-bdd.svg)

*Apollo system definition. The serialed vehicles stay separate, and the IU is three boxes, not one computer with a nickname.*

```
Apollo11
├── SaturnV
│   ├── SIC → F1          S-IC-6
│   ├── SII → J2          S-II-6
│   ├── SIVB → J2         S-IVB-6N
│   ├── IU → LVDC, ST-124, FCC     IU-6
│   ├── SLA               SLA-14; 8 panels (4 jettison / 4 stay); LM extract after transposition
│   └── LES
├── CSM
│   ├── CM                12,250 lb
│   │   ├── Stabilization and Control System (SCS) → Body-Mounted Attitude Gyro (BMAG), Thrust Vector Control (TVC), Rotational Hand Controller (RHC)
│   │   ├── AGC_CM → erasable, fixed, oscillator, Comanche055
│   │   ├── IMU, DSKY, DSKY2
│   │   ├── RCS → systemA, systemB
│   │   ├── ECLSS → oxygen, water, LiOH, suit circuit
│   │   ├── USB, Entry Monitor System (EMS)
│   │   ├── AgZn1–3, charger, inverter1–2
│   │   └── probe, ringLatches (12)
│   └── SM                51,243 lb; SPS load unmarked; cryo 2+2
│       ├── SPS
│       ├── RCS → quadA–D
│       └── FC1–FC3
├── LM
│   ├── descent → DPS, AgZn1–4, ECA, landingRadar
│   └── ascent
│       ├── PNGS → IMU
│       ├── AGC_LM → erasable, fixed, oscillator, Luminary1A
│       ├── AGS → AEA, ASA, DEDA
│       ├── APS, RCS, DSKY, USB, drogue, rendezvousRadar
│       └── AgZn1–2, ECA
├── Crew → CDR (A7L, PLSS), CMP (A7L), LMP (A7L, PLSS)
├── Ground → KSC_LCC, MCC (RTCC, MOCR2, CCATS; FLIGHT, CAPCOM, EECOM, CCC, Flight Dynamics Officer (FDO)), MSFN, NASCOM
├── RSO
└── recovery → Hornet
```

PNGS is the model name for PGNCS and is not AGS. SCS is the Block II analog backup to AGC_CM.

The LM split is where the radars live. `landingRadar` lives on descent only. One `rendezvousRadar` lives on ascent only. PNGS does not nest either radar. PNGS on ascent talks to `landingRadar` on descent and to `rendezvousRadar` on ascent.

![LM definition](apollo-bdd-lm.svg)

*LM definition. Descent holds the landing radar; ascent holds the one rendezvous radar.*

![LM internal connections](apollo-ibd-lm.svg)

*LM internals. PNGS crosses the mate to both radars and does not own either one as a child.*

The mechanical stack is SIC → SII → SIVB → IU → SLA → SM, with LES → CM → SM, SLA → LM descent, CM probe to LM drogue, and descent mated to ascent. RSO talks UHF destruct to S-IC, outside MCC. KSC_LCC talks umbilicals to S-IC and hands voice to MCC at tower clear (Mission Rule 1-21). IU LVDC guides S-IC, S-II, and S-IVB for boost and TLI. MSFN talks USB to CM and LM. NASCOM is wideband to Ground and MCC. MCC CCATS talks Path A to MSFN 642B. The separate P27 path is V70–V73 only. Recovery talks 243.0 MHz to the CM. Isolation stays: no stage-to-stage electrical power and no CSM–LM propellant crossfeed.

The hop that must stay is TLI → dockEject → translunar → LOI. There is no TLI→translunar hop. `dockEject` is after TLI and before translunar coast.

countdown → boost → earthOrbit → TLI → dockEject → translunar → LOI → undock → DOI → descent → surfaceEVA → ascent → rendezvous → TEI → entry → recovery

Triggers are `towerClear` into boost, `orbitalInsertion` (SECO) into earthOrbit, `tliBurn` into TLI, `tliComplete` into dockEject, `lmExtract` into translunar, `loiBurn` (SPS) into LOI, `lunarOrbit` into undock, `doiBurn` (DPS) into DOI, `p63` into descent, `p68` into surfaceEVA, `p12` into ascent, `p30` into rendezvous, `teiBurn` (SPS) into TEI, `ei` into entry, and `recoveryForce` into recovery.

The mission STM shows that hop. TLI boxes carry the three GET labels. LOI-1 boxes carry planned 75:54:28 GET and flown ~075:49:50 GET.

![Apollo mission states](apollo-stm.svg)

*Apollo mission states. The locked hop is TLI, then dockEject, then translunar, then LOI.*

Abort runs beside the nominal machine: pad, I, II, III, IV, contingency TLI, lunar, SPS. LES covers pad / Mode I only. Later modes are not LES. Crew safety is not the tower alone.

![Apollo abort modes](apollo-stm-abort.svg)

*Apollo abort modes. Pad and Mode I sit with LES; later modes do not.*

Computer mode machines stay separate. CMC entry is P61 → P62 → P63 → P64 → P65 → P66 → P67 (entry only). LGC landing is P63 → P64 → {P65 | P66} → P67 → P68 (landing only). Apollo 11 flew P66. AGS goes idle → operate (R47 from PNGS) → follow PNGS → idle and does not land. ECLSS goes cabin → suit → EVA (PLSS) → cabin. Docking mode, which is not the mission `dockEject` state, is undocked → soft → hard (twelve latches) → hardware off.

Named constraints are `usbCsmLink`, `usbLmLink`, `lunarDelay`, `f1Thrust`, `agcCycle`, and `a11IgnitionMass`. Names only: no equations and no results, and not taught as studies. F-1 1,530,000 lbf remains an SA-507 citation, not an AS-506 requirement.

Allocation maps a named job onto a part that exists. Boost and TLI allocate to the IU (LVDC + ST-124 + FCC). Destruct allocates to RSO, outside MCC. LOI / TEI / entry allocate to AGC_CM. Landing / ascent / LM abort allocate to AGC_LM. Backup attitude allocates to AGS, which does not land. Atmosphere and thermal allocate to ECLSS. EVA allocates to the Extravehicular Mobility Unit (EMU) (A7L + PLSS). Path A allocates to CCATS. Path B allocates to P27. Electrical Power System (EPS) allocates to SM fuel cells, CM AgZn, and LM descent AgZn. Model names include `allocateBoostToIU`, `allocateTliToIU`, `allocateDestructToRSO`, `allocateAGC_CMToCM`, `allocateAGC_LMToLM`, `allocateAGSToLM`, `allocateLVDCToIU`, `allocatePathAToCCATS`, `allocatePathBToP27`, `allocateEPSToSM`, `allocateEPSToCM`, `allocateEPSToDescent`, `allocateDockToCM`, `allocateDockToLM`, `allocateRCSToSM`, and `allocateRCSToCM`.

![Apollo allocations](apollo-alloc.svg)

*Apollo allocations. IU owns boost and TLI; the two AGCs stay split; RSO owns destruct.*

## What is unmarked

Unmarked stays unmarked. The model does not invent a number to close a gap: CSM lunar Δv (no official table in the sources used); SPS loaded mass / CSM-107 SPS loaded lb; SM/CM RCS loaded propellant mass; RCS Δv table; A11 AGS flight-program name; A11 flown food intake (kcal), because TN D-7720 2800/3200 is the 1967 plan baseline, not flown kcal; entry blackout duration; RTCC MOC versus DSC which-is-which on A11; the complete MSFN 30-ft inventory (ships collapsed) and the 4th Apollo Instrumentation Ship (AIS); the full SCS switch deck (TBD in the model); and the CMP personal name (not in the model).

In scope: Apollo 11 / Block II / AS-506. Out of scope: J-mission 3+3 cryo, LRV, SIM bay, extended EVA. Verification cases remain names only. This remains an example model, not a certifiable product.

Which cut of the stack is hardest to drop — the two AGCs, the radar split, or the TLI → dockEject hop — and which number must stay unmarked?

## References

Kurten. (1975, July). *Technical Note D-7990*.

Lutz et al. (1975, November). *Technical Note D-8093*.

NASA Manned Spacecraft Center, Flight Planning Branch. (1969, July 1). *Apollo 11 Flight Plan* (Final).

National Aeronautics and Space Administration. (1969a, May 20). *69-HC-620* [Photograph].

National Aeronautics and Space Administration. (1969b). *Apollo 11 press kit* (69-83K).

National Aeronautics and Space Administration. (1969c, November). *Apollo 11 Mission Report* (MSC-00171).

National Aeronautics and Space Administration. (1972). *Technical Note D-6724*.

National Aeronautics and Space Administration. (1973a, March). *Technical Note D-7082*.

National Aeronautics and Space Administration. (1973b, March). *Technical Note D-7143*.

National Aeronautics and Space Administration. (1973c, August). *Technical Note D-7375*.

Smith et al. (1974, July). *Food Systems* (Technical Note D-7720).
