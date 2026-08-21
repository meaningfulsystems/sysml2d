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
        }
        part def SII {
            part J2 : J2;
        }
        part def SIVB {
            part J2 : J2;
        }
        part def IU {
            part LVDC : LVDC;
        }
        part def SLA;
        part def LES;
        part def F1;
        part def J2;
        part def LVDC;
    }

    package CSM {
        part def CSM {
            part CM : CM;
            part SM : SM;
        }
        part def CM {
            part SCS : SCS;
            part AGC_CM : AGC_CM;
            part IMU : IMU;
            part DSKY : DSKY;
            part DSKY2 : DSKY;
            part RCS : RCS;
            part ECLSS : ECLSS;
            part USB : USB;
            part EMS : EMS;
            connection AGC_CMToDSKY connect AGC_CM to DSKY;
            connection AGC_CMToDSKY2 connect AGC_CM to DSKY2;
            connection SCSToAGC_CM connect SCS to AGC_CM;
            connection SCSToRCS connect SCS to RCS;
            connection AGC_CMToIMU connect AGC_CM to IMU;
            connection ECLSSToAGC_CM connect ECLSS to AGC_CM;
        }
        part def SM {
            part SPS : SPS;
            part RCS : RCS;
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
            connection oscToErasable connect oscillator to erasable;
            connection oscToFixed connect oscillator to fixed;
        }
        part def IMU;
        part def DSKY;
        part def SPS;
        part def RCS;
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
        part def BMAG;
        part def TVC;
        part def RHC;
        part def ErasableMemory;
        part def FixedMemory;
        part def Oscillator;
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
            connection PNGSToAGC_LM connect PNGS to AGC_LM;
            connection AGC_LMToDSKY connect AGC_LM to DSKY;
            connection AGC_LMToAGS connect AGC_LM to AGS;
            connection AGC_LMToAPS connect AGC_LM to APS;
            connection AGC_LMToRCS connect AGC_LM to RCS;
            connection PNGSToLandingRadar connect PNGS to landingRadar;
            connection PNGSToRendezvousRadar connect PNGS to rendezvousRadar;
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
            connection oscToErasable connect oscillator to erasable;
            connection oscToFixed connect oscillator to fixed;
        }
        part def AGS;
        part def DPS;
        part def APS;
        part def RCS;
        part def IMU;
        part def DSKY;
        part def landingRadar;
        part def rendezvousRadar;
        part def USB;
        part def ErasableMemory;
        part def FixedMemory;
        part def Oscillator;
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
        }
        part def CMP {
            part A7L : A7L;
        }
        part def LMP {
            part A7L : A7L;
            part PLSS : PLSS;
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
            part MOCR : MOCR;
            part CCATS : CCATS;
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
    part def RecoveryForces;

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
        transition TLICutoff first TLI accept tliComplete then translunar;
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
        state p63;
        state p64;
        state p66;
        state p68;
        state p70;
        state p71;
        transition toP63 first p00 accept p63 then p63;
        transition toP64 first p63 accept p64 then p64;
        transition toP66 first p64 accept p66 then p66;
        transition toP68 first p66 accept p68 then p68;
        transition toP70 first p63 accept p70 then p70;
        transition toP71 first p70 accept p71 then p71;
        transition toP12 first p68 accept p12 then p12;
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
        state p61;
        state p62;
        state p67;
        transition toP11 first p00 accept p11 then p11;
        transition toP27 first p00 accept p27 then p27;
        transition toP40 first p00 accept p40 then p40;
        transition toP61 first p00 accept p61 then p61;
        transition toP62 first p61 accept p62 then p62;
        transition toP67 first p62 accept p67 then p67;
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
    requirement lm5ConsumableRequirement { doc /* LM-5: descent O2 ~48 lb @ 3000 psi; ascent O2 ~2.4 lb ×2; descent water 332 lb; ascent water 42 lb ×2; LCG 1200 Btu/man-h steady. */ }
    requirement a7lRequirement { doc /* A7L: 3.75±0.25 psid; EV 19.69 kg; PLSS usable O2 1.04 lb / 4 h at 1200 Btu/h. */ }
    requirement foodRequirement { doc /* Food plan 2200±300 kcal/d. A11 actual intake UNKNOWN. */ }
    requirement delayRequirement { doc /* Lunar delay = range/c (~1.3 s). Entry blackout duration UNKNOWN. */ }
    requirement earthOrbitRequirement { doc /* Earth parking orbit 100 nmi planned. */ }
    requirement f1Requirement { doc /* F-1 ×5 @ 1,530,000 lbf each (SA-507). F-1 hydraulics collapsed. */ }
    requirement j2Requirement { doc /* J-2 ×5 @ 230,000 lbf (S-II); J-2 ×1 @ 207,000 lbf (S-IVB). */ }
    requirement spsRequirement { doc /* SPS 20,500 lbf (PK 69-83K). */ }
    requirement dpsRequirement { doc /* DPS 10,500 lbf, 10:1, ±6° (TN D-7143). */ }
    requirement apsRequirement { doc /* APS 3,500 lbf, 90% in 0.450 s (TN D-7082). */ }
    requirement a11MassRequirement { doc /* A11 PK masses: ignition 6,484,280 lb; first motion 6,398,535; LES 8,930; LM descent dry 4,483; LM RCS 604; DPS load 18,100; APS load 5,214. Stage tank loads and Δv table UNKNOWN. */ }
    requirement agcRequirement { doc /* Two AGCs: AGC_CM and AGC_LM. Block II: 16-bit, 2048 E / 36864 F, 1.024 MHz, MCT 11.7 μs (AGCIS 30). CM = 1 AGC + 2 DSKY. LM = 1 AGC + 1 DSKY. Do not merge. A11 rope IDs UNKNOWN. */ }
    requirement agsRequirement { doc /* AGS is a separate computer. Memory UNKNOWN. R47 inits it from PNGS. */ }
    requirement iuGncRequirement { doc /* IU LVDC stays separate from AGC. IU owns boost+TLI. */ }
    requirement rsoRequirement { doc /* RSO is OUTSIDE MCC. UHF destruct, safed after Earth orbit. */ }
    requirement a11AtypicalRequirement { doc /* A11 vs generic lunar stack: (1) first landing, one short EVA, 196 h vs 336 h ECLSS spec; (2) no LRV, no SIM bay; (3) P66 was the A11-flown landing program; (4) Parkes + Goldstone 210-ft is A11 coverage; (5) F-1 1,530,000 lbf sourced as SA-507, not AS-506; (6) PK masses A11-only; tank/Δv UNKNOWN; (7) rope IDs UNKNOWN. */ }
    requirement scsRequirement { doc /* CSM SCS is the Block II analog backup to AGC_CM. Crew selects AGC_CM vs SCS. Full SCS switch deck TBD. */ }
    requirement pngsRequirement { doc /* LM PNGS is AGC_LM + IMU + landingRadar + rendezvousRadar. AGS is separate. Do not merge PNGS with AGS. */ }
    requirement eclssLoopRequirement { doc /* CM ECLSS loops: O2, water, LiOH CO2 removal, suit circuit. 5.0 psia 100% O2; CO2 ≤7.6 torr; LiOH 1.5 man-day, swap 12 h. SM O2 640 lb; potable 36 lb / waste 56 lb. */ }
    requirement rtccRequirement { doc /* RTCC: five IBM 360/75. MOC+DSC roles; which-is-which on A11 UNKNOWN. */ }
    requirement msfnSiteRequirement { doc /* 3×85-ft USB: Goldstone, Madrid, Honeysuckle + NASCOM. MSFN ships collapsed. Complete 30-ft inventory UNKNOWN. */ }
    requirement kscRequirement { doc /* KSC_LCC: Firing Room 1, RCA 110A pair, ACE, umbilicals, pad cryo. Handoff MCC at tower clear. */ }

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
}
