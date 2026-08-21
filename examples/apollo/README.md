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
