# Apollo Architecture

Someone asked me a simple question last week: if Apollo 11 was one mission, why does it take a stack of vehicles, two computers, and a room in Houston that isn't even in charge of the destruct button?

That question stayed with me.

I opened `apollo.sysml` and tried to walk the as-flown stack the way I'd walk a dinner-table argument. Units a curious kid could track. No invented numbers. The Systems Modeling Language (SysML) file wins when a picture disagrees.

Here's the portrait. NASA photo 69-HC-620. Saturn-Apollo 506 (SA-506) rolling to Pad 39-A on 20 May 1969. This is the real vehicle, not a generated view.

![Saturn V SA-506 / Apollo 11 rolled out to Pad 39-A, 20 May 1969. Credit: NASA photo 69-HC-620 (public domain). This is the system portrait, not a generated SysMLD view.](apollo-sa506-rollout.jpg)

*Saturn V SA-506 / Apollo 11 rolled out to Pad 39-A, 20 May 1969. Credit: NASA photo 69-HC-620 (public domain). This is the system portrait, not a generated SysMLD view.*

## One-page overview

I'm not writing a Department of Defense Architecture Framework (DoDAF) product set. There are no Operational View / Systems View / Technical View (OV / SV / TV) products and no capability taxonomies. The first page is just who, why, the stack, and the mission thread.

**Who I'm talking to, and who was on the pad.** The instance is Apollo 11 / Apollo-Saturn 506 (AS-506), as-flown July 1969. I wrote this for anyone who will stay with a ninth-grade history paper and still check a cite. Launch is from the Kennedy Space Center (KSC). After tower clear, Mission Control Center (MCC) Houston sits in Mission Operations Control Room (MOCR) 2. The Manned Space Flight Network (MSFN) talks to the stack. The Range Safety Officer (RSO) sits outside MCC. Recovery is to USS *Hornet*. Earth and Moon are context, not decoration.

**Why bother.** I wanted to see how the as-flown system actually worked, not how a poster remembers it. This is an **example model, not a certifiable** vehicle. After the first page I go problem first, then design, then the holes I still can't fill.

**The stack.** Saturn V serials S-IC-6 / S-II-6 / S-IVB-6N / Instrument Unit (IU)-6 / Spacecraft-LM Adapter (SLA)-14. Command/Service Module (CSM) CSM-107 *Columbia*. Lunar Module (LM) LM-5 *Eagle*. In scope: first landing, one short surface Extravehicular Activity (EVA), model PNGS (cockpit/switch label Primary Guidance, Navigation, and Control System (PGNCS)) program P66 as the flown landing program, Service Module (SM) cryogenic tankage 2+2. Out of scope: later J-mission variants, Lunar Roving Vehicle (LRV), Scientific Instrument Module (SIM) bay, extended EVA, invented change-in-velocity (Δv) tables.

**The mission thread.** Lunar-orbit rendezvous. Three crew. Land two. Bring all three home. Saturn V puts the CSM and the LM into Earth parking orbit. Translunar Injection (TLI) sends the stack toward the Moon. After transposition, docking, and LM extract (`dockEject`), they coast. The CSM burns Lunar Orbit Insertion (LOI) and, later, Trans-Earth Injection (TEI). The LM undocks, burns Descent Orbit Insertion (DOI), lands two crew, supports one surface EVA, ascends, and meets the CSM. The Command Module (CM) brings all three home.

I think about the problem first, then the design. That's simplified MagicGrid. When I map NASA Procedural Requirements (NPR 7123.1) onto that, I keep it as a translation, not a second framework. These rows are not NPR 7123 product titles.

| NASA process idea | Where I put it |
|-------------------|----------------|
| Who needs what | Problem domain — purpose, stakeholders, operating context |
| The shalls | Problem domain — requirements (model text; sourced numbers; unmarked left unmarked) |
| Jobs asked of the stack | Problem domain — named use cases |
| What the design does in time | Solution domain — behavior; mission State Machine (STM) and abort |
| The parts | Solution domain — part tree and interfaces |
| The serialed hardware | Solution domain — S-IC-6, CSM-107, landing radar on descent, IU as Launch Vehicle Digital Computer (LVDC) + ST-124 + Flight Control Computer (FCC) |
| Sourced numbers | Problem domain and named constraints; no invented equations |
| Named checks | Analysis and verification *names* — no part, port, or effect is bound unless the model says so |

Hyphens aren't legal identifiers in the model. S-IC / S-II / S-IVB show up as `SIC`, `SII`, `SIVB`. ST-124 is `ST124`. Surface EVA is `surfaceEVA`.

---

## Problem domain

I start with who needed what. The wiring comes later.

The national job is to land two people on the Moon and return three. This instance is Apollo 11 only. First landing. One short EVA. No rover, no SIM bay. The flown landing program is P66. MCC sits in **MOCR 2**. SM cryo is **2+2**, not the later J-mission 3+3.

Crew safety isn't Launch Escape System (LES)-only. LES is the pad and Mode I escape tower. Later-mode safety that the model actually has: `AbortMode` (pad, I–IV, contingency TLI, lunar, Service Propulsion System (SPS)); RSO ultra-high-frequency (UHF) destruct outside MCC, safed after Earth orbit; the CM heat shield; Environmental Control and Life Support System (ECLSS); A7L pressure garment; Portable Life Support System (PLSS); and recover-crew to *Hornet*. There is no single `crewSafetyRequirement` element.

The stack sits in a world, not in a vacuum. Here's the operating-context picture. I want you to see the people and nets outside the vehicles — and that RSO destruct does not pass through MCC.

![Apollo operating context](apollo-context.svg)

### Who asked for a job

A Stakeholder here is a person or organization that asks a job of the stack. The model doesn't collapse them into one Ground actor.

| Stakeholder / part | Role | Associated use cases |
|--------------------|------|----------------------|
| Commander (CDR), Lunar Module Pilot (LMP), Command Module Pilot (CMP) | Flight crew. CDR (Armstrong) and LMP (Aldrin) carry PLSS for EVA. CMP has no PLSS in the model. CMP personal name is unmarked | CDR: Fly Mission, Lunar EVA |
| KSC Launch Control Center (`KSC_LCC`) | Launch commit: Firing Room 1, RCA 110A pair, Acceptance Checkout Equipment (ACE), umbilicals, pad cryo | context; not a use-case actor |
| MCC (Houston) | Flight control after tower clear. Apollo 11 uses **MOCR 2**. MCC is not a midcourse-correction burn | Fly Mission, Recover Crew |
| Real-Time Computer Complex (RTCC) | Five IBM 360/75. Trajectory and uplink. Mission Operations Computer (MOC) vs Dynamic Standby Computer (DSC) roles on A11 are unmarked | supports MCC |
| Goddard Space Flight Center (GSFC) / NASA Communications Network (NASCOM) | Ground wideband network | context |
| MSFN | Goldstone / Madrid / Honeysuckle 85-ft Unified S-Band (USB) triad, plus named 30-ft, ships (collapsed), Apollo Range Instrumentation Aircraft (ARIA) | context |
| Air Force Eastern Test Range (AFETR) RSO | UHF destruct, **outside MCC**, safed after Earth orbit | Range Safety |
| TF-130 / USS *Hornet* (CV-12) | Recovery. Splash is the flown Ground Elapsed Time (GET): flown 195:18:35 GET. 13 nmi from USS *Hornet*, not from the target. Weather-revised miss ~1.7 nmi | Recover Crew (MCC-owned) |
| Earth / Moon | Celestial context | — |

Handoff is KSC → MCC at tower clear — **Mission Rule 1-21**. RSO is not MCC.

The jobs the model names:

- **Fly Mission** — primary. CDR and MCC associate. **Includes** Lunar EVA.
- **Lunar EVA** — CDR. One surface EVA.
- **Recover Crew** — MCC.
- **Range Safety** — RSO. Separate from Fly Mission.

Analysis cases are names only — no equations and no results: USB link analysis (`usbLinkAnalysis`); consumable analysis (`consumableAnalysis`). Verification cases are names only — no part, port, or effect is bound: `verifyUsbCsm`, `verifyA7l`, `verifyP27`, `verifyRso`.

Here's the use-case picture. Three actors, four ellipses. Fly Mission **Includes** Lunar EVA. Recover Crew belongs to MCC. Range Safety belongs to RSO.

![Apollo use cases](apollo-uc.svg)

Context flows the model names: MCC → MSFN (Path A / voice); RSO → vehicle (destruct UHF, not via MCC); MSFN ↔ Earth (USB / 210-ft / Parkes); MSFN ↔ Moon (~1.3 s lunar delay).

### The shalls, and the fights I won't paper over

I didn't invent a shall to make a table look tidy. Engine thrust conflicts stay cited with no silent winner and no required thrust. A generated box isn't a requirement.

Here's the requirements picture. I want you to see TLI GET with three labels (PK 02:44:15, A11-FP 2:44:26, flown 02:44:16 MSC-00171). Planned LOI-1 is 75:54:28 GET. A11-FP is the **only planned source**. Flown LOI-1 is ~075:49:50 GET. Food is D-7720 April 1967 plan baseline, not flown. Unmarked Δv / SPS load / Reaction Control System (RCS) load stay unmarked.

![Apollo requirements](apollo-req.svg)

#### Mass and propellant (A11 Press Kit p.109)

These Press Kit p.109 loads stay dual-cited with the rest of the model. They are not a required-mass shall.

| Item | Sourced value |
|------|---------------|
| S-IC-6 | 5,022,674 lb fueled / 288,750 lb dry; liquid oxygen (LOX) 3,307,855; RP-1 1,426,069; liftoff **7,653,854 lbf** |
| S-II-6 | 1,059,171 / 79,918; LOX 821,022; liquid hydrogen (LH2) 158,221 |
| S-IVB-6N | 260,523 / 25,000; LOX 192,023; LH2 43,500 |
| IU-6 | 4,306 lb |
| CM | 12,250 lb |
| SM | 51,243 lb |
| Also Press Kit | Ignition 6,484,280 lb; first motion 6,398,535; LES 8,930; LM descent dry 4,483; LM RCS 604; Descent Propulsion System (DPS) load 18,100; LM Ascent Propulsion System (APS) load 5,214 (engine — not the S-IVB Auxiliary Propulsion System / ullage motors) |

#### Engines

No required thrust. SPS and DPS numbers are cited; I don't pick a winner and I don't add a shall. LMA790 (a Grumman Lunar Module document number) is the third DPS cite.

| Engine | Source A | Source B | Source C |
|--------|----------|----------|----------|
| SPS | 20,500 lbf (Press Kit) | 21,500 lbf vac (TN D-7375) | — |
| DPS | 9,870 / 1,050–6,300 lbf (Press Kit) | 10,500 lbf 10:1 (TN D-7143) | 9,870 / 1,050–6,800 lbf (LMA790) |
| LM APS (engine) | 3,500 lbf; 90% in 0.450 s; **1.5° cant** (TN D-7082) | — | — |
| F-1 ×5 | 1,530,000 lbf each, sourced as **SA-507**, not AS-506 | hydraulics collapsed | — |
| J-2 S-II ×5 | 230,000 lbf | — | — |
| J-2 S-IVB ×1 | 207,000 lbf | — | — |

#### RCS

SM 100 lbf/engine (Press Kit p.93), four quads. LM 100 lbf/engine (Press Kit p.106). CM 93 lbf/engine; two systems of six; no automatic translation. Loaded SM/CM RCS propellant mass is unmarked.

#### Guidance computers

| System | Sourced parameters | Source |
|--------|-------------------|--------|
| Apollo Guidance Computer (AGC) — two: `AGC_CM`, `AGC_LM` | Block II 16-bit; 2048 erasable / 36864 fixed; 1.024 MHz; memory cycle time (MCT) **11.7 µs**; 65 lb / 70 W. CM = 1 AGC + 2 Display and Keyboard (DSKY). LM = 1 AGC + 1 DSKY | Apollo Guidance Computer Information Series (AGCIS) 30 |
| A11 ropes | Comanche **055** on AGC_CM; Luminary **1A LMY99/1** on AGC_LM | `agcRequirement` |
| P-numbers | Command Module Computer (CMC) P61–P67 = **entry**; Lunar Module Guidance Computer (LGC) P63–P68 = **landing**. Not one shared P-number machine | `agcRequirement` |
| Pulse Integrating Pendulous Accelerometer (PIPA) | CM 5.85 cm/s/pulse; LM 1.0 cm/s/pulse | `pipaRequirement` |
| IU | Physically LVDC + ST-124 + FCC. LVDC 82.03125 µs; 26+2 bits; **no digital AGC↔LVDC**. IU owns boost + TLI | `iuGncRequirement` |
| Abort Guidance System (AGS) | Abort Electronics Assembly (AEA) + Abort Sensor Assembly (ASA) + Data Entry and Display Assembly (DEDA); AEA 4096×18, 5 µs, 32.7 lb; **not a landing computer**. AGS ≠ DSKY — AGS display is DEDA. R47 inits from PNGS | TN-7990 |

Verb 37 (V37) mode, V36 fresh start, V69 restart. 1201/1202 is executive overflow, not an abort.

PNGS is AGC_LM + Inertial Measurement Unit (IMU) + radars — not AGS. Physical `landingRadar` is on descent only. One `rendezvousRadar` is on ascent only. PNGS connects to both and does not nest either radar.

#### Electrical power (Press Kit)

SM: fuel cells FC1–FC3; cryo **2+2**. CM: silver-zinc (AgZn) 1–3 + charger; two 117 V 400 Hz inverters. LM: six AgZn (4 descent / 2 ascent) + Electrical Control Assembly (ECA) each. Bus 28 V DC. **No stage-to-stage electrical power. No CSM–LM propellant crossfeed.**

#### Communications

| Link | Sourced parameters |
|------|-------------------|
| USB CSM | Uplink 2106.40625 MHz; phase modulation (PM) down 2287.5; frequency modulation (FM) down 2272.5; pulse-code modulation (PCM) 51.2 or 1.6 kbps; uplink digital ~2 kbps; pseudo-random noise (PRN) range 992 kbps, ±15 m, ~540,000 mi unambiguous |
| USB LM | Uplink 2101.802 MHz; down 2282.5; steerable 20.5 dB transmit; amplitron 20 W; no simultaneous PM+FM |
| CSM High-Gain Antenna (HGA) | Wide 8.0 / medium 18.0 / narrow 25.7 dB; power amplifier 11.2 W PM / 12.6 W FM; **crew-selected**, not ground-commandable on Block II |
| Path A | Flight Controller (FC) → Command and Communications Controller (CCC) → RTCC → Communications, Command, and Telemetry System (CCATS) → site 642B → USB 70 kHz |
| P27 | Verbs **V70–V73 only**; separate from CCATS |
| Very High Frequency (VHF) | 296.8 / 259.7 MHz |
| Recovery | 243.0 MHz |

#### Air, food, EVA, clocks

| Parameter | Value |
|-----------|-------|
| CM cabin | 5.0 psia 100% O2; carbon dioxide (CO2) ≤ 7.6 torr |
| CM spec vs A11 | 3 crew / 14 d spec; A11 **196 h** vs 336 h spec |
| SM O2 / water | 640 lb O2; potable 36 lb / waste 56 lb |
| Lithium hydroxide (LiOH) | 1.5 man-day; swap 12 h |
| LM-5 descent O2 | ~48 lb — **teaching figure 2800 psi**; 3000 psi D-6724 is the other text; no required pressure |
| LM-5 ascent O2 | ~2.4 lb ×2 |
| LM-5 water | descent 332 lb; ascent 42 lb ×2 |
| Liquid Cooling Garment (LCG) | 1200 Btu/man-h steady |
| A7L | 3.75±0.25 psid; extravehicular 19.69 kg |
| PLSS | usable O2 1.04 lb / 4 h at 1200 Btu/h |
| Food plan | **TN D-7720 April 1967 plan baseline:** 2800 kcal/man/day CM, 3200 kcal/man/day LM. Not A11 flown intake. Flown kcal unmarked |
| Earth parking orbit | **100 nmi planned** |
| Lunar delay | range/c ≈ 1.3 s |
| EVA | one surface EVA; CDR 2:48 / LMP 2:40 (Technical Note D-8093 Table I). Not the Public Affairs Office (PAO) hatch-to-hatch 2:31:40 |
| TLI | PK planned 02:44:15 GET; A11-FP planned 2:44:26 GET; flown 02:44:16 GET (MSC-00171). Three labels only |
| Transposition, docking, and extraction (TD&E) | ~03:20–04:09 planned |
| LOI-1 | **Planned** 75:54:28 GET. A11-FP is the **only planned source**. **Flown** ~075:49:50 GET (PAD / Mission Report). Two numbers only |
| Splash | flown 195:18:35 GET. 13 nmi from USS *Hornet*, not from the target. Weather-revised miss ~1.7 nmi |
| Landing program | **P66 flown** |

TD&E is its own GO/NO-GO, CMP-owned, SM RCS. CM probe / LM drogue + 12 ring latches. LM stays in the SLA — 8 panels (4 jettison / 4 stay) — until `dockEject` (after TLI, before translunar coast).

Sources in the model: Apollo 11 Press Kit 69-83K; Saturn V Flight Manual; Apollo Experience Reports; AGCIS / Massachusetts Institute of Technology Instrumentation Laboratory (MIT IL); Technical Notes D-6718 / D-6724 / D-7082 / D-7143 / D-7375 / D-7720 / D-8093 / D-8227 / TN-7990; and LMA790 (a Grumman Lunar Module document number). Values not in those extracts stay unmarked. There is no official CSM lunar Δv table in the sources used here. I didn't invent one.

---

## Solution domain

Now the design. What was stacked, what talked to what, and how the flight actually ran.

### How the stack is built

From the ground up: S-IC-6, S-II-6, S-IVB-6N, IU-6, SLA-14 (LM-5 inside), SM, CM, LES.

Here's the system tree. I want you to see Saturn V, CSM, LM, Crew, and Ground stay separate. IU children are LVDC, ST-124, and FCC. SLA is eight-panel. Descent and ascent stay separate. Two AGCs stay separate.

![Apollo system definition](apollo-bdd.svg)

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

I keep two AGCs, AGS, IU (LVDC + ST-124 + FCC), LES, descent vs ascent, and three crew. PNGS is the model name for PGNCS. It isn't AGS. SCS is the Block II analog backup to AGC_CM.

The LM split is where the radars live. Here's the LM tree, then the insides. `landingRadar` lives on descent only. One `rendezvousRadar` lives on ascent only. PNGS doesn't nest either radar. PNGS on ascent talks to `landingRadar` on descent and to `rendezvousRadar` on ascent.

![LM definition](apollo-bdd-lm.svg)

![LM internal connections](apollo-ibd-lm.svg)

Mechanical stack: SIC → SII → SIVB → IU → SLA → SM; LES → CM → SM; SLA → LM descent; CM probe ↔ LM drogue; descent ↔ ascent mate.

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
| PNGS (ascent) | landingRadar (descent) | PNGS talks to the physical landing radar on the descent stage |
| PNGS (ascent) | rendezvousRadar (ascent) | PNGS talks to the one rendezvous radar on ascent |

Here's the vehicle insides. Named ports, named connections. Lines shouldn't pass through boxes. Isolation stays: no stage-to-stage electrical power; no CSM–LM propellant crossfeed.

![Apollo vehicle internals](apollo-ibd.svg)

Port types: UHF destruct, umbilical, voice, guidance, mechanical, docking, USB, NASCOM, command, recovery.

### How the flight ran

The hop I won't let slide is TLI → dockEject → translunar → LOI. There is no TLI→translunar hop. `dockEject` is after TLI and before translunar coast.

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

TLI GET has three labels only: PK planned 02:44:15 GET; A11-FP planned 2:44:26 GET; flown 02:44:16 GET (MSC-00171). TD&E is ~03:20–04:09 planned.

Planned LOI-1 is 75:54:28 GET. A11-FP is the **only planned source**. Flown LOI-1 is ~075:49:50 GET (PAD / Mission Report). Two LOI-1 numbers only. P66 is the flown landing program.

Here's the mission STM. I want you to see that hop — TLI → dockEject → translunar → LOI. TLI boxes carry the three GET labels. LOI-1 boxes carry planned 75:54:28 GET and flown ~075:49:50 GET.

![Apollo mission states](apollo-stm.svg)

Abort runs beside the nominal machine: pad, I, II, III, IV, contingency TLI, lunar, SPS. LES covers pad / Mode I only. Later modes aren't LES. Here's the abort picture. Crew safety isn't the tower alone.

![Apollo abort modes](apollo-stm-abort.svg)

Computer mode machines stay separate. CMC entry is P61 → P62 → P63 → P64 → P65 → P66 → P67 (entry only). LGC landing is P63 → P64 → {P65 | P66} → P67 → P68 (landing only). Apollo 11 flew **P66**. AGC_CM modes include P00, P11, P20, P27, P40, P51, P52 plus V37 / V36 / V69 / 1201/1202. AGC_LM modes include P00, P12, P20, P27, P30, P70, P71 plus the same verb/alarm pattern; P70 → P71 abort chain. SCS: AGC_CM ↔ attitude hold / rate command / min impulse; crew selects AGC_CM vs SCS. AGS: idle → operate (R47 from PNGS) → follow PNGS → idle. AGS does not land. ECLSS: cabin → suit → EVA (PLSS) → cabin. Docking mode (not the mission `dockEject` state): undocked → soft (probe capture) → hard (twelve latches) → hardware off (transfer prep).

Named actions: AGC power-up (CM and LM), antenna selection, Path A load, P27 load, R47 AGS init, P63 braking, P64 approach, P66 landing, P70/P71 abort, soft dock, hard dock, remove docking hardware.

Other generated computer-mode STMs and the package view sit in `examples/apollo/`. I left them out so we could stay on the stack and the mission.

### Named constraints

Named constraints: `usbCsmLink`, `usbLmLink`, `lunarDelay`, `f1Thrust`, `agcCycle`, `a11IgnitionMass`. Names only — no equations and no results. I don't teach them as studies.

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

### Who owns which job

Allocation is a named job landing on a part that exists.

| Function | Allocated to parts that exist |
|----------|-------------------------------|
| Boost, TLI | IU (LVDC + ST-124 + FCC); LVDC is the digital computer |
| Destruct | RSO (outside MCC) |
| LOI / TEI / entry | AGC_CM |
| Landing / ascent / LM abort | AGC_LM |
| Backup attitude | AGS — does not land |
| Atmosphere / thermal | ECLSS |
| EVA | Extravehicular Mobility Unit (EMU) (A7L + PLSS) |
| Trajectory / uplink | RTCC |
| RF | MSFN |
| Launch commit | KSC_LCC |
| Flight direction after handoff | FLIGHT (MOCR) |
| Heat shield | CM only (entry) |
| Pad / Mode I escape | LES |
| Later-mode abort | `AbortMode` I–IV, contingency TLI, lunar, SPS — not LES |
| Path A | CCATS |
| Path B | P27 |
| Electrical Power System (EPS) | SM fuel cells, CM AgZn, LM descent AgZn |
| Docking | CM probe, LM drogue |
| RCS | SM quads, CM systems |

Allocation names in the model: `allocateBoostToIU`, `allocateTliToIU`, `allocateDestructToRSO`, `allocateAGC_CMToCM`, `allocateAGC_LMToLM`, `allocateAGSToLM`, `allocateLVDCToIU`, `allocatePathAToCCATS`, `allocatePathBToP27`, `allocateEPSToSM`, `allocateEPSToCM`, `allocateEPSToDescent`, `allocateDockToCM`, `allocateDockToLM`, `allocateRCSToSM`, `allocateRCSToCM`.

Here's the allocation picture. IU owns boost and TLI. RSO owns destruct. AGC_CM and AGC_LM stay split. AGS is separate. EPS sits on SM, CM, and descent.

![Apollo allocations](apollo-alloc.svg)

---

## What we don't know

Unmarked stays unmarked. I don't invent a number to close a gap.

- CSM lunar Δv (no official table in the sources used)
- SPS loaded mass / CSM-107 SPS loaded lb
- SM/CM RCS loaded propellant mass
- RCS Δv table
- A11 AGS flight-program name
- A11 flown food intake (kcal). TN D-7720 2800/3200 is the 1967 plan baseline, not flown kcal
- Entry blackout duration
- RTCC MOC vs DSC which-is-which on A11
- Complete MSFN 30-ft inventory (ships collapsed); 4th Apollo Instrumentation Ship (AIS) unmarked
- Full SCS switch deck (TBD in the model)
- CMP personal name (not in the model)

In scope: Apollo 11 / Block II / AS-506.

Out of scope: J-mission 3+3 cryo, LRV, SIM bay, extended EVA. F-1 1,530,000 lbf is an SA-507 citation, not an AS-506 figure.

Verification cases remain names only.

This remains an example model, not a certifiable product.

If you had to keep one cut of this stack — the two AGCs, the radar split, or the TLI → dockEject hop — which one would you defend at a dinner table, and what number would you refuse to invent to make the story easier?
