package Apollo11 {
    part def Apollo11 {
        part SaturnV : SaturnV;
        part CSM : CSM;
        part LM : LM;
        part Crew : Crew;
        part Ground : Ground;
        part RSO : RSO;
        part recovery : RecoveryForces;

        port rsoDestructOut : UhfDestructPort;
        port SICDestructIn : UhfDestructPort;
        port KSC_LCCUmbilicalOut : UmbilicalPort;
        port SICUmbilicalIn : UmbilicalPort;
        port KSC_LCCHandoffOut : VoicePort;
        port MCCHandoffIn : VoicePort;
        port IUBoostOut : GuidancePort;
        port SICIuIn : GuidancePort;
        port SIIIuIn : GuidancePort;
        port SIVBIuIn : GuidancePort;
        port IUTliOut : GuidancePort;
        port SIVBTliIn : GuidancePort;
        port SICToSIIOut : MechanicalPort;
        port SIIFromSICIn : MechanicalPort;
        port SIIToSIVBOut : MechanicalPort;
        port SIVBFromSIIIn : MechanicalPort;
        port SIVBToIUOut : MechanicalPort;
        port IUFromSIVBIn : MechanicalPort;
        port IUToSLAOut : MechanicalPort;
        port SLAFromIUIn : MechanicalPort;
        port SLAToSMOut : MechanicalPort;
        port SMFromSLAIn : MechanicalPort;
        port LESToCMOut : MechanicalPort;
        port CMFromLESIn : MechanicalPort;
        port CMToSMOut : MechanicalPort;
        port SMFromCMIn : MechanicalPort;
        port SLALmOut : MechanicalPort;
        port descentSlaIn : MechanicalPort;
        port CMDockOut : DockingPort;
        port ascentDockIn : DockingPort;
        port descentToAscentOut : MechanicalPort;
        port ascentFromDescentIn : MechanicalPort;
        port MSFNUsbOut : UsbPort;
        port CMUsbIn : UsbPort;
        port LMUsbIn : UsbPort;
        port NASCOMOut : NascomPort;
        port NASCOMIn : NascomPort;
        port NASCOMToMCCOut : NascomPort;
        port MCCFromNASCOMIn : NascomPort;
        port MCCCcatsOut : CommandPort;
        port MSFN642BIn : CommandPort;
        port recoveryToCMOut : RecoveryPort;
        port CMRecoveryIn : RecoveryPort;

        connection rsoToSIC connect rsoDestructOut to SICDestructIn;
        connection KSC_LCCToSIC connect KSC_LCCUmbilicalOut to SICUmbilicalIn;
        connection KSC_LCCToMCCHandoff connect KSC_LCCHandoffOut to MCCHandoffIn;
        connection IUToSIC connect IUBoostOut to SICIuIn;
        connection IUToSII connect IUBoostOut to SIIIuIn;
        connection IUToSIVBBoost connect IUBoostOut to SIVBIuIn;
        connection IUToSIVBTli connect IUTliOut to SIVBTliIn;
        connection SICToSII connect SICToSIIOut to SIIFromSICIn;
        connection SIIToSIVB connect SIIToSIVBOut to SIVBFromSIIIn;
        connection SIVBToIU connect SIVBToIUOut to IUFromSIVBIn;
        connection IUToSLA connect IUToSLAOut to SLAFromIUIn;
        connection SLAToSM connect SLAToSMOut to SMFromSLAIn;
        connection LESToCM connect LESToCMOut to CMFromLESIn;
        connection CMToSM connect CMToSMOut to SMFromCMIn;
        connection SLAToDescent connect SLALmOut to descentSlaIn;
        connection CMToAscent connect CMDockOut to ascentDockIn;
        connection descentToAscent connect descentToAscentOut to ascentFromDescentIn;
        connection MSFNToCMUsb connect MSFNUsbOut to CMUsbIn;
        connection MSFNToLMUsb connect MSFNUsbOut to LMUsbIn;
        connection NASCOMToGround connect NASCOMOut to NASCOMIn;
        connection NASCOMToMCC connect NASCOMToMCCOut to MCCFromNASCOMIn;
        connection MCCToMSFNCommand connect MCCCcatsOut to MSFN642BIn;
        connection recoveryToCM connect recoveryToCMOut to CMRecoveryIn;
    }

    package SaturnV {
        part def SaturnV {
            part SIC : SIC;
            part SII : SII;
            part SIVB : SIVB;
            part IU : IU;
            part SLA : SLA;
            part LES : LES;
        }
        part def SIC {
            part F1 : F1;
            doc /* Stack serial S-IC-6. A11 PK p.109: 5,022,674 fueled / 288,750 dry; LOX 3,307,855; RP-1 1,426,069; liftoff 7,653,854 lbf. */
        }
        part def SII {
            part J2 : J2;
            doc /* Stack serial S-II-6. A11 PK p.109: 1,059,171 fueled / 79,918 dry; LOX 821,022; LH2 158,221. */
        }
        part def SIVB {
            part J2 : J2;
            doc /* Stack serial S-IVB-6N. A11 PK p.109: 260,523 fueled / 25,000 dry; LOX 192,023; LH2 43,500. */
        }
        part def IU {
            part LVDC : LVDC;
            doc /* Stack serial IU-6. A11 PK p.109: 4,306 lb. */
        }
        part def SLA { doc /* Stack serial SLA-14. Four petals; LM extract after transposition. */ }
        part def LES;
        part def F1;
        part def J2;
        part def LVDC { doc /* 82.03125 µs, 26+2 bits. No digital AGC↔LVDC. */ }
    }

    package CSM {
        part def CSM {
            part CM : CM;
            part SM : SM;
            connection SMToCMPower connect SM to CM;
        }
        part def CM {
            doc /* A11 PK p.109: 12,250 lb. */
            part SCS : SCS;
            part AGC_CM : AGC_CM;
            part IMU : IMU;
            part DSKY : DSKY;
            part DSKY2 : DSKY;
            part RCS : RCS;
            part ECLSS : ECLSS;
            part USB : USB;
            part EMS : EMS;
            part AgZn1 : AgZn;
            part AgZn2 : AgZn;
            part AgZn3 : AgZn;
            part charger : charger;
            part inverter1 : inverter;
            part inverter2 : inverter;
            part probe : probe;
            part ringLatches : ringLatches;
            part systemA : RCSSystem;
            part systemB : RCSSystem;
            connection AGC_CMToDSKY connect AGC_CM to DSKY;
            connection AGC_CMToDSKY2 connect AGC_CM to DSKY2;
            connection SCSToAGC_CM connect SCS to AGC_CM;
            connection SCSToRCS connect SCS to RCS;
            connection AGC_CMToIMU connect AGC_CM to IMU;
            connection ECLSSToAGC_CM connect ECLSS to AGC_CM;
            connection chargerToAgZn1 connect charger to AgZn1;
            connection chargerToAgZn2 connect charger to AgZn2;
            connection chargerToAgZn3 connect charger to AgZn3;
            connection AgZn1ToInverter1 connect AgZn1 to inverter1;
            connection AgZn3ToInverter2 connect AgZn3 to inverter2;
            connection probeToLatches connect probe to ringLatches;
            connection RCSToSystemA connect RCS to systemA;
            connection RCSToSystemB connect RCS to systemB;
        }
        part def SM {
            doc /* A11 PK p.109: 51,243 lb. SPS loaded mass UNKNOWN. A11 SM cryo is 2+2 (two H2 + two O2), not J-mission 3+3. */
            part SPS : SPS;
            part RCS : RCS;
            part FC1 : FC;
            part FC2 : FC;
            part FC3 : FC;
            part quadA : quad;
            part quadB : quad;
            part quadC : quad;
            part quadD : quad;
            connection FC1ToFC2 connect FC1 to FC2;
            connection FC2ToFC3 connect FC2 to FC3;
            connection RCSToQuadA connect RCS to quadA;
            connection RCSToQuadB connect RCS to quadB;
            connection RCSToQuadC connect RCS to quadC;
            connection RCSToQuadD connect RCS to quadD;
        }
        part def SCS {
            part BMAG : BMAG;
            part TVC : TVC;
            part RHC : RHC;
            connection RHCToBMAG connect RHC to BMAG;
            connection BMAGToTVC connect BMAG to TVC;
        }
        part def AGC_CM {
            part erasable : ErasableMemory;
            part fixed : FixedMemory;
            part oscillator : Oscillator;
            part Comanche055 : Rope;
            connection oscToErasable connect oscillator to erasable;
            connection oscToFixed connect oscillator to fixed;
        }
        part def IMU;
        part def DSKY;
        part def SPS;
        part def RCS { doc /* SM: 100 lbf per engine (A11 PK p.93), four quads. CM: 93 lbf per engine. Loaded SM/CM RCS propellant mass UNKNOWN — do not invent. */ }
        part def ECLSS {
            part oxygenLoop : OxygenLoop;
            part waterLoop : WaterLoop;
            part co2Removal : LiOHCanister;
            part suitCircuit : SuitCircuit;
            connection o2ToSuit connect oxygenLoop to suitCircuit;
            connection waterToSuit connect waterLoop to suitCircuit;
            connection suitToLioh connect suitCircuit to co2Removal;
        }
        part def USB;
        part def EMS;
        part def AgZn;
        part def charger;
        part def inverter;
        part def probe;
        part def ringLatches;
        part def RCSSystem { doc /* CM RCS: two × six 93 lbf engines. No auto translation. Loaded CM RCS propellant mass UNKNOWN. */ }
        part def FC;
        part def quad { doc /* SM RCS quad: 100 lbf per engine (A11 PK p.93). Loaded SM RCS propellant mass UNKNOWN. */ }
        part def BMAG;
        part def TVC;
        part def RHC;
        part def ErasableMemory;
        part def FixedMemory;
        part def Oscillator;
        part def Rope;
        part def OxygenLoop;
        part def WaterLoop;
        part def LiOHCanister;
        part def SuitCircuit;
    }

    package LM {
        part def LM {
            part descent : descent;
            part ascent : ascent;
        }
        part def descent {
            part DPS : DPS;
            part AgZn1 : AgZn;
            part AgZn2 : AgZn;
            part AgZn3 : AgZn;
            part AgZn4 : AgZn;
            part ECA : ECA;
            connection ECAToAgZn1 connect ECA to AgZn1;
            connection ECAToAgZn2 connect ECA to AgZn2;
            connection ECAToAgZn3 connect ECA to AgZn3;
            connection ECAToAgZn4 connect ECA to AgZn4;
        }
        part def ascent {
            part PNGS : PNGS;
            part AGC_LM : AGC_LM;
            part AGS : AGS;
            part APS : APS;
            part RCS : RCS;
            part DSKY : DSKY;
            part landingRadar : landingRadar;
            part rendezvousRadar : rendezvousRadar;
            part USB : USB;
            part drogue : drogue;
            part AgZn1 : AgZn;
            part AgZn2 : AgZn;
            part ECA : ECA;
            connection PNGSToAGC_LM connect PNGS to AGC_LM;
            connection AGC_LMToDSKY connect AGC_LM to DSKY;
            connection AGC_LMToAGS connect AGC_LM to AGS;
            connection AGC_LMToAPS connect AGC_LM to APS;
            connection AGC_LMToRCS connect AGC_LM to RCS;
            connection PNGSToLandingRadar connect PNGS to landingRadar;
            connection PNGSToRendezvousRadar connect PNGS to rendezvousRadar;
            connection ECAToAgZn1 connect ECA to AgZn1;
            connection ECAToAgZn2 connect ECA to AgZn2;
        }
        part def PNGS {
            part IMU : IMU;
            part landingRadar : landingRadar;
            part rendezvousRadar : rendezvousRadar;
            connection IMUToLandingRadar connect IMU to landingRadar;
            connection IMUToRendezvousRadar connect IMU to rendezvousRadar;
        }
        part def AGC_LM {
            part erasable : ErasableMemory;
            part fixed : FixedMemory;
            part oscillator : Oscillator;
            part Luminary1A : Rope;
            connection oscToErasable connect oscillator to erasable;
            connection oscToFixed connect oscillator to fixed;
        }
        part def AGS {
            part AEA : AEA;
            part ASA : ASA;
            part DEDA : DEDA;
            connection AEAToASA connect AEA to ASA;
            connection AEAToDEDA connect AEA to DEDA;
        }
        part def AEA { doc /* TN-7990: 4096 × 18-bit, half/half, 5 μs, 32.7 lb. Not a landing computer. */ }
        part def ASA;
        part def DEDA;
        part def AgZn;
        part def ECA;
        part def drogue;
        part def DPS;
        part def APS { doc /* APS 3,500 lbf; 90% in 0.450 s (TN D-7082); 1.5° cant. */ }
        part def RCS { doc /* LM RCS: 100 lbf per engine (A11 PK p.106). */ }
        part def IMU;
        part def DSKY;
        part def landingRadar;
        part def rendezvousRadar;
        part def USB;
        part def ErasableMemory;
        part def FixedMemory;
        part def Oscillator;
        part def Rope;
    }

    package Crew {
        part def Crew {
            part CDR : CDR;
            part CMP : CMP;
            part LMP : LMP;
        }
        part def CDR {
            part A7L : A7L;
            part PLSS : PLSS;
            doc /* Armstrong. Surface EVA 2:48. */
        }
        part def CMP {
            part A7L : A7L;
        }
        part def LMP {
            part A7L : A7L;
            part PLSS : PLSS;
            doc /* Aldrin. Surface EVA 2:40. */
        }
        part def A7L;
        part def PLSS;
    }

    package Ground {
        part def Ground {
            part KSC_LCC : KSC_LCC;
            part MCC : MCC;
            part RTCC : RTCC;
            part MSFN : MSFN;
            part NASCOM : NASCOM;
        }
        part def KSC_LCC;
        part def MCC {
            part RTCC : RTCC;
            part MOCR2 : MOCR;
            part CCATS : CCATS;
            doc /* A11 MCC is MOCR 2. Handoff from KSC_LCC at tower clear — Mission Rule 1-21. */
        }
        part def RTCC {
            part ibm360a : IBM360_75;
            part ibm360b : IBM360_75;
            part ibm360c : IBM360_75;
            part ibm360d : IBM360_75;
            part ibm360e : IBM360_75;
        }
        part def IBM360_75;
        part def MOCR {
            part FLIGHT : FLIGHT;
            part CAPCOM : CAPCOM;
            part EECOM : EECOM;
            part CCC : CCC;
            part FDO : FDO;
        }
        part def FLIGHT;
        part def CAPCOM;
        part def EECOM;
        part def CCC;
        part def FDO;
        part def CCATS;
        part def MSFN {
            part Goldstone : Goldstone;
            part Madrid : Madrid;
            part Honeysuckle : Honeysuckle;
            part ships : AISShip;
        }
        part def Goldstone;
        part def Madrid;
        part def Honeysuckle;
        part def AISShip;
        part def NASCOM;
    }

    part def RSO;
    part def RecoveryForces {
        part Hornet : Hornet;
        doc /* USS Hornet (CV-12). Splash 195:18:35 MET, 13 nmi from target. */
    }
    part def Hornet;

    port def UhfDestructPort;
    port def UmbilicalPort;
    port def VoicePort;
    port def GuidancePort;
    port def MechanicalPort;
    port def DockingPort;
    port def UsbPort;
    port def NascomPort;
    port def CommandPort;
    port def RecoveryPort;

    state def MissionPhase {
        entry; then countdown;
        state countdown;
        state boost;
        state earthOrbit;
        state TLI;
        state dockEject;
        state translunar;
        state LOI;
        state undock;
        state DOI;
        state descent;
        state surfaceEVA;
        state ascent;
        state rendezvous;
        state TEI;
        state entry;
        state recovery;
        transition liftoff first countdown accept towerClear then boost;
        transition seoi first boost accept orbitalInsertion then earthOrbit;
        transition startTLI first earthOrbit accept tliBurn then TLI;
        transition startDockEject first TLI accept tliComplete then dockEject;
        transition startTranslunar first dockEject accept lmExtract then translunar;
        transition startLOI first translunar accept loiBurn then LOI;
        transition LOICutoff first LOI accept lunarOrbit then undock;
        transition startDOI first undock accept doiBurn then DOI;
        transition startDescent first DOI accept p63 then descent;
        transition touchdown first descent accept p68 then surfaceEVA;
        transition startAscent first surfaceEVA accept p12 then ascent;
        transition startRndz first ascent accept p30 then rendezvous;
        transition startTEI first rendezvous accept teiBurn then TEI;
        transition startEntry first TEI accept ei then entry;
        transition splashdown first entry accept recoveryForce then recovery;
    }

    state def AbortMode {
        entry; then nominal;
        state nominal;
        state pad;
        state I;
        state II;
        state III;
        state IV;
        state contingencyTLI;
        state lunar;
        state SPS;
        transition abortPad first nominal accept padAbort then pad;
        transition abortI first nominal accept modeI then I;
        transition abortII first nominal accept modeII then II;
        transition abortIII first nominal accept modeIII then III;
        transition abortIV first nominal accept modeIV then IV;
        transition abortTLI first nominal accept contingencyTli then contingencyTLI;
        transition abortLunar first nominal accept lunarAbort then lunar;
        transition abortSPS first nominal accept spsAbort then SPS;
    }

    state def AGC_LM_Mode {
        entry; then p00;
        state p00;
        state p12;
        state p20;
        state p27;
        state p30;
        state p70;
        state p71;
        state mode;
        state freshStart;
        state restart;
        state execOverflow;
        transition v37 first p00 accept v37 then mode;
        transition v37ToP12 first mode accept p12 then p12;
        transition v37ToP27 first mode accept p27 then p27;
        transition v37ToP30 first mode accept p30 then p30;
        transition v37ToP70 first mode accept p70 then p70;
        transition v36 first p00 accept v36 then freshStart;
        transition v36ToP00 first freshStart accept v36done then p00;
        transition v69 first p00 accept v69 then restart;
        transition v69ToP00 first restart accept v69done then p00;
        transition alarm1201 first mode accept alarm1201 then execOverflow;
        transition alarm1202 first mode accept alarm1202 then execOverflow;
        transition overflowToP00 first execOverflow accept resume then p00;
        transition toP71 first p70 accept p71 then p71;
    }

    state def LGC_Landing {
        entry; then p63;
        state p63;
        state p64;
        state p65;
        state p66;
        state p67;
        state p68;
        transition toP64 first p63 accept p64 then p64;
        transition toP65 first p64 accept p65 then p65;
        transition toP66 first p64 accept p66 then p66;
        transition toP67 first p66 accept p67 then p67;
        transition p65ToP68 first p65 accept p68 then p68;
        transition p66ToP68 first p66 accept p68 then p68;
        transition p67ToP68 first p67 accept p68 then p68;
    }

    state def SCSMode {
        entry; then AGC_CM;
        state AGC_CM;
        state attHold;
        state rateCommand;
        state minImpulse;
        transition scsToHold first AGC_CM accept scsAttHold then attHold;
        transition scsToRate first AGC_CM accept scsRate then rateCommand;
        transition scsToMin first AGC_CM accept scsMinImpulse then minImpulse;
        transition scsToAGC first attHold accept returnAGC then AGC_CM;
        transition scsRateToAGC first rateCommand accept returnAGC then AGC_CM;
        transition scsMinToAGC first minImpulse accept returnAGC then AGC_CM;
    }

    state def AGSMode {
        entry; then idle;
        state idle;
        state operate;
        state followPNGS;
        transition agsOn first idle accept agsOperate then operate;
        transition r47 first operate accept r47Init then followPNGS;
        transition agsOff first operate accept agsStandby then idle;
    }

    state def AGC_CM_Mode {
        entry; then p00;
        state p00;
        state p11;
        state p20;
        state p27;
        state p40;
        state p51;
        state p52;
        state mode;
        state freshStart;
        state restart;
        state execOverflow;
        transition v37 first p00 accept v37 then mode;
        transition v37ToP11 first mode accept p11 then p11;
        transition v37ToP27 first mode accept p27 then p27;
        transition v37ToP40 first mode accept p40 then p40;
        transition v36 first p00 accept v36 then freshStart;
        transition v36ToP00 first freshStart accept v36done then p00;
        transition v69 first p00 accept v69 then restart;
        transition v69ToP00 first restart accept v69done then p00;
        transition alarm1201 first mode accept alarm1201 then execOverflow;
        transition alarm1202 first mode accept alarm1202 then execOverflow;
        transition overflowToP00 first execOverflow accept resume then p00;
    }

    state def CMC_Entry {
        entry; then p61;
        state p61;
        state p62;
        state p63;
        state p64;
        state p65;
        state p66;
        state p67;
        transition toP62 first p61 accept p62 then p62;
        transition toP63 first p62 accept p63 then p63;
        transition toP64 first p63 accept p64 then p64;
        transition toP65 first p64 accept p65 then p65;
        transition toP66 first p65 accept p66 then p66;
        transition toP67 first p66 accept p67 then p67;
    }

    state def ECLSSMode {
        entry; then cabin;
        state cabin;
        state suit;
        state eva;
        transition toSuit first cabin accept suitConnect then suit;
        transition toEva first suit accept plss then eva;
        transition toCabin first eva accept ingress then cabin;
    }

    state def DockingMode {
        entry; then undocked;
        state undocked;
        state soft;
        state hard;
        state hardwareOff;
        transition capture first undocked accept probeCapture then soft;
        transition hardDock first soft accept twelveLatches then hard;
        transition removeHw first hard accept transferPrep then hardwareOff;
    }

    package ApolloModel;
    package ApolloStructure;
    package ApolloBehavior;
    package ApolloRequirements;
    package ApolloAnalysis;
    package ApolloVerification;

    part earth : Earth;
    part moon : Moon;
    part def Earth;
    part def Moon;

    interface def UsbInterface;
    interface def CommandInterface;
    interface def P27Interface;
    interface def DestructInterface;
    item def UsbUplink;
    item def UsbDownlinkPm;
    item def UsbDownlinkFm;
    item def P27Load;
    item def CcatsLoad;
    item def PrnRange;
    item def CrewVoice;
    flow usbCsmFlow;
    flow usbLmFlow;
    flow commandPathA;
    flow commandPathB;
    flow destructFlow;
    flow nascomFlow;

    requirement usbCsmRequirement { doc /* USB CSM: uplink 2106.40625 MHz; PM down 2287.5; FM down 2272.5. PCM 51.2 or 1.6 kbps. Uplink digital ~2 kbps. PRN range 992 kbps, ±15 m, ~540,000 mi unambiguous. */ }
    requirement usbLmRequirement { doc /* USB LM: uplink 2101.802 MHz; down 2282.5. LM steerable 20.5 dB tx; amplitron 20 W; no simultaneous PM+FM. */ }
    requirement csmHgaRequirement { doc /* CSM HGA: wide 8.0 dB / med 18.0 / narrow 25.7. PA 11.2 W PM / 12.6 W FM. Antennas CREW-selected, not ground-commandable on Block II. */ }
    requirement p27Requirement { doc /* P27 uplink verbs ONLY V70–V73 (clock/block/scatter). Separate from CCATS real-time command-load path. */ }
    requirement commandPathARequirement { doc /* Path A: FC→CCC→RTCC→CCATS→site 642B→USB 70 kHz. */ }
    requirement cmEcsRequirement { doc /* CM ECLSS: 3 crew / 14 d spec; 5.0 psia 100% O2; CO2 ≤7.6 torr; SM O2 640 lb; potable 36 lb / waste 56 lb; LiOH 1.5 man-day, swap 12 h. A11 mission 196 h vs 336 h spec. */ }
    requirement lm5ConsumableRequirement { doc /* LM-5: descent O2 ~48 lb — 2800 psi vs 3000 psi (cite both, no silent winner); ascent O2 ~2.4 lb ×2; descent water 332 lb; ascent water 42 lb ×2; LCG 1200 Btu/man-h steady. */ }
    requirement a7lRequirement { doc /* A7L: 3.75±0.25 psid; EV 19.69 kg; PLSS usable O2 1.04 lb / 4 h at 1200 Btu/h. */ }
    requirement foodRequirement { doc /* D-7720 April 1967 plan baseline: 2800 kcal/man/day CM, 3200 kcal/man/day LM. Not A11 flown intake. A11 actual intake UNKNOWN. */ }
    requirement delayRequirement { doc /* Lunar delay = range/c (~1.3 s). Entry blackout duration UNKNOWN. */ }
    requirement earthOrbitRequirement { doc /* Earth parking orbit 100 nmi planned. */ }
    requirement f1Requirement { doc /* F-1 ×5 @ 1,530,000 lbf each (SA-507). F-1 hydraulics collapsed. */ }
    requirement j2Requirement { doc /* J-2 ×5 @ 230,000 lbf (S-II); J-2 ×1 @ 207,000 lbf (S-IVB). */ }
    requirement spsRequirement { doc /* Engine conflict — cite both, no silent winner: SPS 20,500 lbf (PK) vs 21,500 lbf (TN D-7375). SPS loaded mass UNKNOWN. */ }
    requirement dpsRequirement { doc /* Engine conflict — cite both, no silent winner: DPS 9,870 / 1,050–6,300 lbf (PK) vs 10,500 lbf 10:1 (TN D-7143). */ }
    requirement apsRequirement { doc /* APS 3,500 lbf, 90% in 0.450 s (TN D-7082); 1.5° cant. */ }
    requirement a11MassRequirement { doc /* Stack serials S-IC-6 / S-II-6 / S-IVB-6N / IU-6 / SLA-14. A11 PK p.109 tank loads (no longer UNKNOWN): S-IC 5,022,674 fueled / 288,750 dry; LOX 3,307,855; RP-1 1,426,069; liftoff 7,653,854 lbf. S-II 1,059,171 / 79,918; LOX 821,022; LH2 158,221. S-IVB 260,523 / 25,000; LOX 192,023; LH2 43,500. IU 4,306 lb; CM 12,250; SM 51,243. Also PK: ignition 6,484,280 lb; first motion 6,398,535; LES 8,930; LM descent dry 4,483; LM RCS 604; DPS load 18,100; APS load 5,214. SPS loaded mass UNKNOWN. CSM lunar Δv UNKNOWN — do not invent. */ }
    requirement agcRequirement { doc /* Two AGCs: AGC_CM and AGC_LM. Block II: 16-bit, 2048 E / 36864 F, 1.024 MHz, MCT 11.7 μs (AGCIS 30). CM = 1 AGC + 2 DSKY. LM = 1 AGC + 1 DSKY. Do not merge. A11 ropes: Comanche 055 + Luminary 1A LMY99/1. P-numbers are not global: CMC P61–P67 = ENTRY; LGC P63–P68 = LANDING. V37 mode, V36 fresh start, V69 restart. 1201/1202 is exec overflow, not an abort. */ }
    requirement agsRequirement { doc /* AGS = AEA + ASA + DEDA (TN-7990). AEA 4096 × 18-bit, half/half, 5 μs, 32.7 lb. Not a landing computer. R47 inits it from PNGS. A11 AGS flight-program name UNKNOWN. */ }
    requirement pipaRequirement { doc /* PIPA scale: CM 5.85 cm/s/pulse vs LM 1.0 cm/s/pulse. */ }
    requirement epsRequirement { doc /* A11 Press Kit electrical: SM three fuel cells; A11 SM cryo is 2+2, not J-mission. CM three AgZn + charger; LM six AgZn (4 descent / 2 ascent) + ECA each; 28 V DC; two 117 V 400 Hz inverters. No stage-to-stage electrical power. No CSM–LM propellant crossfeed. */ }
    requirement dockingRequirement { doc /* TD&E is its own GO/NO-GO, CMP-owned, SM RCS. CM probe / LM drogue + 12 ring latches; soft then hard dock; hardware removed for transfer. LM remains in the SLA until dockEject (after TLI, before translunar coast). A11 PK planned GET: TLI 02:44:15 GET; CSM sep / transposition / dock ~03:20; LM extract ~04:09; then translunar coast; LOI-1 75:54:28 GET. No invented Δv. */ }
    requirement rcsRequirement { doc /* RCS thrust: SM 100 lbf per engine (A11 PK p.93); LM 100 lbf per engine (A11 PK p.106); CM 93 lbf. SM four quads. CM two × six 93 lbf engines; no auto translation. Loaded SM/CM RCS propellant mass UNKNOWN — do not invent. Δv table still UNKNOWN. */ }
    requirement iuGncRequirement { doc /* IU LVDC stays separate from AGC. LVDC 82.03125 µs, 26+2 bits. No digital AGC↔LVDC. IU owns boost+TLI. */ }
    requirement rsoRequirement { doc /* RSO is OUTSIDE MCC. UHF destruct, safed after Earth orbit. */ }
    requirement a11AtypicalRequirement { doc /* A11 vs generic lunar stack: (1) first landing, one short EVA — CDR 2:48 / LMP 2:40 — 196 h vs 336 h ECLSS spec; (2) no LRV, no SIM bay; (3) P66 was the A11-flown landing program; (4) Parkes + Goldstone 210-ft is A11 coverage; (5) F-1 1,530,000 lbf sourced as SA-507, not AS-506; (6) PK p.109 tank loads A11-only; SPS loaded mass UNKNOWN; CSM lunar Δv UNKNOWN; (7) ropes Comanche 055 + Luminary 1A LMY99/1; AGS flight-program name UNKNOWN; (8) A11 MCC is MOCR 2; (9) A11 SM cryo is 2+2, not J-mission. */ }
    requirement scsRequirement { doc /* CSM SCS is the Block II analog backup to AGC_CM. Crew selects AGC_CM vs SCS. Full SCS switch deck TBD. */ }
    requirement pngsRequirement { doc /* LM PNGS is AGC_LM + IMU + landingRadar + rendezvousRadar. AGS is separate. Do not merge PNGS with AGS. */ }
    requirement eclssLoopRequirement { doc /* CM ECLSS loops: O2, water, LiOH CO2 removal, suit circuit. 5.0 psia 100% O2; CO2 ≤7.6 torr; LiOH 1.5 man-day, swap 12 h. SM O2 640 lb; potable 36 lb / waste 56 lb. */ }
    requirement rtccRequirement { doc /* RTCC: five IBM 360/75. MOC+DSC roles; which-is-which on A11 UNKNOWN. */ }
    requirement msfnSiteRequirement { doc /* 3×85-ft USB: Goldstone, Madrid, Honeysuckle + NASCOM. MSFN ships collapsed. Complete 30-ft inventory UNKNOWN. */ }
    requirement kscRequirement { doc /* KSC_LCC: Firing Room 1, RCA 110A pair, ACE, umbilicals, pad cryo. Handoff MCC at tower clear — Mission Rule 1-21. */ }
    requirement vhfRequirement { doc /* VHF 296.8 / 259.7 MHz. Recovery 243.0 MHz. */ }
    requirement isolationRequirement { doc /* No stage-to-stage electrical power. No CSM–LM propellant crossfeed. */ }
    requirement recoveryRequirement { doc /* Splash 195:18:35 MET, 13 nmi from target, USS Hornet (CV-12). */ }
    requirement evaRequirement { doc /* One surface EVA (A11-atypical vs later J). CDR 2:48 / LMP 2:40. PLSS + A7L. */ }

    constraint def usbCsmLink;
    constraint def usbLmLink;
    constraint def lunarDelay;
    constraint def f1Thrust;
    constraint def agcCycle;
    constraint def a11IgnitionMass;
    attribute usbCsmUplinkMhz;
    attribute usbCsmPmDownMhz;
    attribute usbLmUplinkMhz;
    attribute lunarDelayS;
    attribute f1Lbf;
    attribute mctUs;
    attribute ignitionLb;
    attribute earthOrbitNmi;

    action powerOnAGC_CM;
    action powerOnAGC_LM;
    action selectAntenna;
    action sendPathA;
    action sendP27;
    action r47InitAGS;
    action p63Braking;
    action p64Approach;
    action p66Landing;
    action p70Abort;
    action p71Abort;
    action softDock;
    action hardDock;
    action removeDockingHw;

    interaction commandPathAInteraction;
    interaction p27UplinkInteraction;
    use case flyMissionUseCase {
        include lunarEvaUseCase;
    }
    use case lunarEvaUseCase;
    use case recoverCrewUseCase;
    use case rangeSafetyUseCase;
    analysis case usbLinkAnalysis;
    analysis case consumableAnalysis;
    verification case verifyUsbCsm;
    verification case verifyA7l;
    verification case verifyP27;
    verification case verifyRso;

    allocation allocateBoostToIU;
    allocation allocateTliToIU;
    allocation allocateDestructToRSO;
    allocation allocateAGC_CMToCM;
    allocation allocateAGC_LMToLM;
    allocation allocateAGSToLM;
    allocation allocateLVDCToIU;
    allocation allocatePathAToCCATS;
    allocation allocatePathBToP27;
    allocation allocateEPSToSM;
    allocation allocateEPSToCM;
    allocation allocateEPSToDescent;
    allocation allocateDockToCM;
    allocation allocateDockToLM;
    allocation allocateRCSToSM;
    allocation allocateRCSToCM;
}
