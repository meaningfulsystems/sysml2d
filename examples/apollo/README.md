# Apollo 11 / Block II (AS-506)

Room-locked names so [MSML](https://github.com/meaningfulsystems/msml) `projects/apollo/` can twin. **Match these identifiers exactly.** S-IC / S-II / S-IVB are labels; SysML ids are `SIC`, `SII`, `SIVB` (hyphens are not legal identifiers). `surface/EVA` twins as `surfaceEVA`.

This is **SysML2d** (`.sysml` / `.sysmld` / SVG), not MSML.

## Locked packages / parts

- **SaturnV:** SIC, SII, SIVB, IU (LVDC inside IU), SLA, LES
- **CSM:** CM, SM, SCS, AGC_CM, IMU, DSKY, SPS, RCS, ECLSS
- **LM:** descent, ascent, PNGS, AGC_LM, AGS, DPS, APS, RCS, landingRadar, rendezvousRadar
- **Crew:** CDR, CMP, LMP, A7L, PLSS
- **Ground:** KSC_LCC, MCC (`MOCR2` — A11 is MOCR 2), RTCC, MSFN Goldstone / Madrid / Honeysuckle + NASCOM
- **Recovery:** `Hornet` (USS Hornet) under `RecoveryForces`

Do **not** collapse: AGC_CM, AGC_LM, DSKY (CM ×2 + LM ×1), AGS, IU LVDC, USB.

OK to collapse: engine hydraulics, every MSFN ship.

## Morning delta (Mrs. Researcher)

Sourced numbers only. SPS loaded mass and CSM lunar Δv stay UNKNOWN — do not invent them.

**Tank loads (A11 Press Kit p.109)** — no longer UNKNOWN: S-IC 5,022,674 / 288,750; LOX 3,307,855; RP-1 1,426,069; liftoff 7,653,854 lbf. S-II 1,059,171 / 79,918; LOX 821,022; LH2 158,221. S-IVB 260,523 / 25,000; LOX 192,023; LH2 43,500. IU 4,306 lb; CM 12,250; SM 51,243.

**AGC:** A11 ropes `Comanche055` + `Luminary1A` (LMY99/1). AGS hardware sourced; A11 AGS flight-program name UNKNOWN. P-numbers are not global: `CMC_Entry` P61–P67 = ENTRY, `LGC_Landing` P63–P68 = LANDING. V37 mode, V36 fresh start, V69 restart. 1201/1202 is exec overflow, not an abort. PIPA CM 5.85 cm/s/pulse vs LM 1.0. LVDC 82.03125 µs, 26+2 bits; no digital AGC↔LVDC.

**Engine conflicts** (cite both, no silent winner): SPS 20,500 PK vs 21,500 TN D-7375. DPS 9,870 / 1,050–6,300 PK vs 10,500 10:1 TN D-7143.

- **Electrical (A11 Press Kit):** SM `FC1` `FC2` `FC3`; CM `AgZn1`–`AgZn3` + `charger`; LM six AgZn (4 descent / 2 ascent) + `ECA` each; 28 V DC; `inverter1` `inverter2` at 117 V 400 Hz.
- **AGS (TN-7990):** `AEA` + `ASA` + `DEDA`. AEA 4096 × 18-bit, half/half, 5 μs, 32.7 lb. Not a landing computer.
- **Docking:** CM `probe` / LM `drogue`, `ringLatches` (12), soft then hard, hardware removed for transfer (`hardwareOff`).
- **RCS:** SM 100 lbf/engine (A11 PK p.93); LM 100 lbf/engine (A11 PK p.106); CM 93 lbf. SM `quadA`–`quadD`. CM `systemA` / `systemB` (two × six 93 lbf); no auto translation. Loaded SM/CM RCS propellant mass UNKNOWN — do not invent. Δv table still UNKNOWN.

**Stack serials (do not revert tank loads or rope IDs):** S-IC-6 / S-II-6 / S-IVB-6N / IU-6 / SLA-14.

**MCC / recovery / EVA:** A11 MCC is MOCR 2; handoff Mission Rule 1-21 at tower clear. VHF 296.8 / 259.7 MHz; recovery 243.0 MHz. Splash 195:18:35 MET, 13 nmi, Hornet. EVA CDR 2:48 / LMP 2:40.

**Isolation / cryo / APS / LM O2:** No stage-to-stage electrical power; no CSM–LM propellant crossfeed. A11 SM cryo is 2+2, not J-mission. APS 1.5° cant. Descent O2 2800 vs 3000 psi — cite both.

## Mission STM

countdown → boost → earthOrbit → TLI → dock/eject (`dockEject`) → translunar → LOI → undock → DOI → descent → surface/EVA → ascent → rendezvous → TEI → entry → recovery

TD&E is its own GO/NO-GO (CMP-owned, SM RCS, probe/drogue + 12 latches). LM stays in the SLA until extract. A11 PK: TLI 02:44:15 GET → sep/dock ~03:20 → LM extract ~04:09 → translunar coast → LOI-1 75:54:28 GET. Do not jump translunar → LOI; do not invent Δv.

Abort machine (parallel): pad, I–IV, contingency TLI, lunar, SPS.

Reference instance is Apollo 11 / Block II. Sourced numbers only; UNKNOWN / TBD marked.

## Compose

```bash
sysmld definition      examples/apollo/apollo-bdd.json
sysmld interconnection examples/apollo/apollo-ibd.json
sysmld state           examples/apollo/apollo-stm.json
sysmld state           examples/apollo/apollo-stm-abort.json
```

Connections must never pass over boxes. Hop-overs are line-on-line only.
