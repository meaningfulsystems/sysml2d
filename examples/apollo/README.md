# Apollo 11 / Block II (AS-506)

Sourced first cut for the **whole stack**: launch vehicle, CSM/LM, crew, GNC/AGC, ground computers, MCC/MSFN, comms, mission phases. Mrs. Researcher’s ground/crew and vehicles/AGC briefs are source of truth. **Do not invent.** UNKNOWN is marked. Vehicle tank loads, Δv table, A11 rope IDs, AGS memory, RTCC MOC-vs-DSC mapping, 4th AIS ship, complete 30-ft inventory, entry blackout, and A11 food intake stay UNKNOWN.

This is **SysML2d** (`.sysml` / `.sysmld` / SVG), not MSML. Names are chosen to match the MSML pack.

Do **not** collapse: S-IC / S-II / S-IVB / IU / SLA / LES / CM / SM / LM descent / LM ascent; two AGCs; two CM DSKYs vs one LM DSKY; AGS (AEA+ASA); IU LVDC+ST-124+FCC; EMS; USB vs RSO; three crew parts; P27 (V70–V73) vs CCATS path A.

OK to collapse: F-1 hydraulics, ullage/retro as sets, every verb/noun, every MSFN ship/aircraft in diagrams (ships remain named in the model).

```bash
sysmld definition      examples/apollo/apollo-bdd.json
sysmld interconnection examples/apollo/apollo-ibd.json
sysmld interconnection examples/apollo/apollo-ibd-vehicle.json
sysmld interconnection examples/apollo/apollo-ibd-gnc.json
sysmld interconnection examples/apollo/apollo-ibd-mcc.json
sysmld state           examples/apollo/apollo-stm.json
sysmld state           examples/apollo/apollo-stm-abort.json
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

Connections must never pass over boxes.
