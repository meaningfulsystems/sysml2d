# Apollo 11 / Block II (AS-506)

Room-locked names so [MSML](https://github.com/meaningfulsystems/msml) `projects/apollo/` can twin. **Match these identifiers exactly.** S-IC / S-II / S-IVB are labels; SysML ids are `SIC`, `SII`, `SIVB` (hyphens are not legal identifiers). `surface/EVA` twins as `surfaceEVA`.

This is **SysML2d** (`.sysml` / `.sysmld` / SVG), not MSML.

## Locked packages / parts

- **SaturnV:** SIC, SII, SIVB, IU (LVDC inside IU), SLA, LES
- **CSM:** CM, SM, SCS, AGC_CM, IMU, DSKY, SPS, RCS, ECLSS
- **LM:** descent, ascent, PNGS, AGC_LM, AGS, DPS, APS, RCS, landingRadar, rendezvousRadar
- **Crew:** CDR, CMP, LMP, A7L, PLSS
- **Ground:** KSC_LCC, MCC, RTCC, MSFN Goldstone / Madrid / Honeysuckle + NASCOM

Do **not** collapse: AGC_CM, AGC_LM, DSKY (CM ×2 + LM ×1), AGS, IU LVDC, USB.

OK to collapse: engine hydraulics, every MSFN ship.

## Morning delta (Mrs. Researcher)

Sourced numbers only. Tank loads / Δv / A11 rope IDs stay UNKNOWN.

- **Electrical (A11 Press Kit):** SM `FC1` `FC2` `FC3`; CM `AgZn1`–`AgZn3` + `charger`; LM six AgZn (4 descent / 2 ascent) + `ECA` each; 28 V DC; `inverter1` `inverter2` at 117 V 400 Hz.
- **AGS (TN-7990):** `AEA` + `ASA` + `DEDA`. AEA 4096 × 18-bit, half/half, 5 μs, 32.7 lb. Not a landing computer.
- **Docking:** CM `probe` / LM `drogue`, `ringLatches` (12), soft then hard, hardware removed for transfer (`hardwareOff`).
- **RCS:** SM `quadA`–`quadD` (per-engine lbf UNKNOWN in press kit). CM `systemA` / `systemB` (two × six 93 lbf); no auto translation.

## Mission STM

countdown → boost → earthOrbit → TLI → translunar → LOI → undock → DOI → descent → surface/EVA → ascent → rendezvous → TEI → entry → recovery

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
