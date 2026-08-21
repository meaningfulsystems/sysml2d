# Apollo 11 / Block II (AS-506)

Sourced first cut for the **whole stack**: launch vehicle, CSM/LM, crew, GNC/AGC, ground computers, MCC/MSFN, comms, mission phases. Reference instance is **Apollo 11 / Block II / AS-506**. Mrs. Researcher’s brief is still coming — skeleton now, refine when it arrives. **Do not invent.** UNKNOWN is marked. Vehicle tank loads, Δv table, A11 rope IDs, AGS memory, RTCC MOC-vs-DSC mapping, 4th AIS ship, complete 30-ft inventory, entry blackout, A11 food intake, and the full SCS switch deck stay UNKNOWN.

This is **SysML2d** (`.sysml` / `.sysmld` / SVG), not MSML. Names are chosen to match the MSML pack.

## Generic lunar stack vs Apollo 11 atypical

Generic stack kept in the model: Saturn V + Block II CSM (CMC + 2 DSKY + SCS + EMS) + LM (PNGS / LGC + 1 DSKY + AGS) + IU LVDC + MSFN + MCC + phases countdown→recovery.

| Flag | Generic lunar stack | Apollo 11 instance |
| --- | --- | --- |
| Stay / EVA | Later H/J: longer stays, multiple EVAs; CM ECS spec 336 h | First landing; **one short EVA**; A11 **196 h vs 336 h** spec |
| Surface / CSM extras | LRV on A15–A17; SIM bay on J-mission CSM | **No LRV**, **no SIM bay** |
| Landing program | P63 / P64 / P66 family is generic | **P66 was the A11-flown landing program** after P63/P64 |
| Descent / TV coverage | 85-ft USB triad is the generic net | **Parkes + Goldstone 210-ft** is A11 coverage, not a stack part |
| F-1 thrust | Stage family | **1,530,000 lbf sourced as SA-507, not AS-506** |
| Masses / Δv | Stage tank loads and Δv table | PK masses are A11-only; **tank / Δv UNKNOWN** |
| AGC rope | Block II memory/clock sourced | **A11 rope IDs UNKNOWN** |

Do **not** collapse: S-IC / S-II / S-IVB / IU / SLA / LES / CM / SM / LM descent / LM ascent; two AGCs; two CM DSKYs vs one LM DSKY; AGS (AEA+ASA); IU LVDC+ST-124+FCC; EMS; SCS vs CMC; PNGS vs LGC vs AGS; USB vs RSO; three crew parts; P27 (V70–V73) vs CCATS path A.

OK to collapse: F-1 hydraulics, ullage/retro as sets, every verb/noun, every MSFN ship/aircraft in diagrams (ships remain named in the model), CMC entry programs P63–P66 (TBD).

```bash
sysmld definition      examples/apollo/apollo-bdd.json
sysmld interconnection examples/apollo/apollo-ibd.json
sysmld interconnection examples/apollo/apollo-ibd-vehicle.json
sysmld interconnection examples/apollo/apollo-ibd-gnc.json
sysmld interconnection examples/apollo/apollo-ibd-mcc.json
sysmld state           examples/apollo/apollo-stm.json
sysmld state           examples/apollo/apollo-stm-abort.json
sysmld state           examples/apollo/apollo-stm-scs.json
sysmld state           examples/apollo/apollo-stm-ags.json
sysmld state           examples/apollo/apollo-stm-lgc.json
sysmld state           examples/apollo/apollo-stm-cmc.json
sysmld action          examples/apollo/apollo-act.json
sysmld interaction     examples/apollo/apollo-int.json
sysmld usecase         examples/apollo/apollo-uc.json
sysmld package         examples/apollo/apollo-pkg.json
sysmld requirement     examples/apollo/apollo-req.json
sysmld constraint      examples/apollo/apollo-cst.json
sysmld allocation      examples/apollo/apollo-alloc.json
sysmld flow            examples/apollo/apollo-flow.json
sysmld analysis        examples/apollo/apollo-acase.json
sysmld verification    examples/apollo/apollo-vcase.json
sysmld interface       examples/apollo/apollo-intf.json
sysmld general         examples/apollo/apollo-general.json
sysmld general         examples/apollo/apollo-context.json
```

Connections must never pass over boxes. Hop-overs are line-on-line only.
