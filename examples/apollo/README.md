# Apollo 11 / Block II (AS-506)

Architecture: [apollo-architecture-summary.md](apollo-architecture-summary.md).

This folder is a SysML v2 model of the flown Apollo 11 stack (`.sysml` / `.sysmld` / SVG). Hyphens are not legal identifiers, so S-IC / S-II / S-IVB appear as `SIC`, `SII`, `SIVB`. The mission phase surface/EVA is `surfaceEVA`.

Figures that have a source are stated. Values without a source stay UNKNOWN. SPS loaded mass and CSM lunar Δv are UNKNOWN.

## Packages

- **SaturnV:** SIC, SII, SIVB, IU (LVDC + ST-124 + FCC), SLA (8 panels: 4 jettison / 4 stay), LES
- **CSM:** CM, SM, SCS, AGC_CM, IMU, DSKY, SPS, RCS, ECLSS
- **LM:** descent (DPS, AgZn, ECA, landingRadar), ascent (PNGS, AGC_LM, AGS, APS, RCS, rendezvousRadar)
- **Crew:** CDR, CMP, LMP, A7L, PLSS
- **Ground:** KSC_LCC, MCC (Apollo 11 is MOCR 2), RTCC, MSFN Goldstone / Madrid / Honeysuckle + NASCOM
- **Recovery:** Hornet under RecoveryForces

AGC_CM, AGC_LM, the CM and LM DSKYs, AGS, IU (LVDC + ST-124 + Flight Control Computer), and USB stay distinct. AGS display is DEDA, not DSKY.

## Sourced figures

**Tank loads (A11 Press Kit p.109):** S-IC 5,022,674 / 288,750; LOX 3,307,855; RP-1 1,426,069; liftoff 7,653,854 lbf. S-II 1,059,171 / 79,918; LOX 821,022; LH2 158,221. S-IVB 260,523 / 25,000; LOX 192,023; LH2 43,500. IU 4,306 lb; CM 12,250; SM 51,243.

**AGC:** Comanche 055 on AGC_CM; Luminary 1A (LMY99/1) on AGC_LM. AGS hardware is sourced; the A11 AGS flight-program name is UNKNOWN. CMC P61–P67 is entry; LGC P63–P68 is landing. V37 mode, V36 fresh start, V69 restart. 1201/1202 is executive overflow, not an abort. PIPA CM 5.85 cm/s/pulse vs LM 1.0. LVDC 82.03125 µs, 26+2 bits; no digital AGC↔LVDC.

**Engine conflicts** (both cited): SPS 20,500 lbf (Press Kit) vs 21,500 lbf (TN D-7375). DPS 9,870 / 1,050–6,300 lbf (Press Kit) vs 10,500 lbf 10:1 (TN D-7143).

- **Electrical (Press Kit):** SM FC1–FC3; CM AgZn1–AgZn3 + charger; LM six AgZn (4 descent / 2 ascent) + ECA each; 28 V DC; two 117 V 400 Hz inverters.
- **AGS (TN-7990):** AEA + ASA + DEDA. AEA 4096 × 18-bit, 5 μs, 32.7 lb. Not a landing computer.
- **Docking:** CM probe / LM drogue, 12 ring latches, soft then hard, hardware removed for transfer.
- **RCS:** SM 100 lbf/engine (Press Kit p.93); LM 100 lbf/engine (Press Kit p.106); CM 93 lbf. Loaded SM/CM RCS propellant mass is UNKNOWN. Δv table is UNKNOWN.

Stack serials: S-IC-6 / S-II-6 / S-IVB-6N / IU-6 / SLA-14.

MCC is MOCR 2; handoff at tower clear is Mission Rule 1-21. VHF 296.8 / 259.7 MHz; recovery 243.0 MHz. Splash 195:18:35 MET, 13 nmi, Hornet. EVA CDR 2:48 / LMP 2:40. SM cryo is 2+2. APS 1.5° cant. Descent O2 2800 vs 3000 psi — both cited. No stage-to-stage electrical power; no CSM–LM propellant crossfeed.

## Mission phases

countdown → boost → earthOrbit → TLI → dock/eject → translunar → LOI → undock → DOI → descent → surface/EVA → ascent → rendezvous → TEI → entry → recovery

TD&E is a GO/NO-GO after TLI and before translunar coast (CMP, SM RCS, probe/drogue + 12 latches). TLI GET — three labels only: PK planned 02:44:15, A11-FP planned 2:44:26, flown 02:44:16 (MSC-00171). TD&E ~03:20–04:09 planned.

LOI-1 planned 75:54:28 GET — A11-FP is the only planned source. Flown LOI-1 ~075:49:50 GET (PAD / Mission Report). Two LOI-1 numbers only. P66 is the flown landing program.

Abort machine (parallel): pad, I–IV, contingency TLI, lunar, SPS.

## Compose

```bash
sysmld definition      examples/apollo/apollo-bdd.json
sysmld interconnection examples/apollo/apollo-ibd.json
sysmld state           examples/apollo/apollo-stm.json
sysmld state           examples/apollo/apollo-stm-abort.json
```

Connections must never pass over boxes. Hop-overs are line-on-line only.
