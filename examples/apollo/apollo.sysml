package Apollo11 {
    part def Apollo11 {
        part mcc : MissionControlHouston;
        part gsfc : GoddardSpaceFlightCenter;
        part msfn : MannedSpaceFlightNetwork;
        part ksc : KennedyLC39;
        part rso : RangeSafetyAFETR;
        part recovery : RecoveryForces;
        part sIc : SIC;
        part sIi : SII;
        part sIvb : SIVB;
        part iu : IU;
        part sla : SLA;
        part les : LES;
        part cm : CM;
        part sm : SM;
        part lmDescent : LMDescent;
        part lmAscent : LMAscent;
        part cdr : Commander;
        part cmp : CommandModulePilot;
        part lmp : LunarModulePilot;

        port rsoDestructOut : UhfDestructPort;
        port sIcDestructIn : UhfDestructPort;
        port kscUmbilicalOut : UmbilicalPort;
        port sIcUmbilicalIn : UmbilicalPort;
        port kscHandoffOut : VoicePort;
        port mccHandoffIn : VoicePort;
        port iuBoostOut : GuidancePort;
        port sIcIuIn : GuidancePort;
        port sIiIuIn : GuidancePort;
        port sIvbIuIn : GuidancePort;
        port iuTliOut : GuidancePort;
        port sIvbTliIn : GuidancePort;
        port sIcToSiiOut : MechanicalPort;
        port sIiFromSicIn : MechanicalPort;
        port sIiToSivbOut : MechanicalPort;
        port sIvbFromSiiIn : MechanicalPort;
        port sIvbToIuOut : MechanicalPort;
        port iuFromSivbIn : MechanicalPort;
        port iuToSlaOut : MechanicalPort;
        port slaFromIuIn : MechanicalPort;
        port slaToSmOut : MechanicalPort;
        port smFromSlaIn : MechanicalPort;
        port lesToCmOut : MechanicalPort;
        port cmFromLesIn : MechanicalPort;
        port cmToSmOut : MechanicalPort;
        port smFromCmIn : MechanicalPort;
        port slaLmOut : MechanicalPort;
        port lmDescentSlaIn : MechanicalPort;
        port cmDockOut : DockingPort;
        port lmAscentDockIn : DockingPort;
        port lmDescentToAscentOut : MechanicalPort;
        port lmAscentFromDescentIn : MechanicalPort;
        port msfnUsbOut : UsbPort;
        port cmUsbIn : UsbPort;
        port lmUsbIn : UsbPort;
        port msfnNascomOut : NascomPort;
        port gsfcNascomIn : NascomPort;
        port gsfcToMccOut : NascomPort;
        port mccFromGsfcIn : NascomPort;
        port mccCcatsOut : CommandPort;
        port msfn642BIn : CommandPort;
        port recoveryToCmOut : RecoveryPort;
        port cmRecoveryIn : RecoveryPort;

        connection rsoToSic connect rsoDestructOut to sIcDestructIn;
        connection kscToSic connect kscUmbilicalOut to sIcUmbilicalIn;
        connection kscToMccHandoff connect kscHandoffOut to mccHandoffIn;
        connection iuToSic connect iuBoostOut to sIcIuIn;
        connection iuToSii connect iuBoostOut to sIiIuIn;
        connection iuToSivbBoost connect iuBoostOut to sIvbIuIn;
        connection iuToSivbTli connect iuTliOut to sIvbTliIn;
        connection sicToSii connect sIcToSiiOut to sIiFromSicIn;
        connection siiToSivb connect sIiToSivbOut to sIvbFromSiiIn;
        connection sivbToIu connect sIvbToIuOut to iuFromSivbIn;
        connection iuToSla connect iuToSlaOut to slaFromIuIn;
        connection slaToSm connect slaToSmOut to smFromSlaIn;
        connection lesToCm connect lesToCmOut to cmFromLesIn;
        connection cmToSm connect cmToSmOut to smFromCmIn;
        connection slaToLmDescent connect slaLmOut to lmDescentSlaIn;
        connection cmToLmAscent connect cmDockOut to lmAscentDockIn;
        connection lmDescentToAscent connect lmDescentToAscentOut to lmAscentFromDescentIn;
        connection msfnToCmUsb connect msfnUsbOut to cmUsbIn;
        connection msfnToLmUsb connect msfnUsbOut to lmUsbIn;
        connection msfnToGsfc connect msfnNascomOut to gsfcNascomIn;
        connection gsfcToMcc connect gsfcToMccOut to mccFromGsfcIn;
        connection mccToMsfnCommand connect mccCcatsOut to msfn642BIn;
        connection recoveryToCm connect recoveryToCmOut to cmRecoveryIn;
    }

    part def SIC {
        part f1Engine1 : F1;
        part f1Engine2 : F1;
        part f1Engine3 : F1;
        part f1Engine4 : F1;
        part f1Engine5 : F1;
    }
    part def SII {
        part j2Engine1 : J2;
        part j2Engine2 : J2;
        part j2Engine3 : J2;
        part j2Engine4 : J2;
        part j2Engine5 : J2;
    }
    part def SIVB {
        part j2Sivb : J2;
    }
    part def IU {
        part lvdc : LVDC;
        part st124 : ST124;
        part fcc : FCC;
    }
    part def SLA;
    part def LES;
    part def CM {
        part cmc : CMC;
        part cmDsky1 : DSKY;
        part cmDsky2 : DSKY;
        part ems : EMS;
        part cmUsb : USB;
        part ecs : CMECS;
    }
    part def SM {
        part sps : SPS;
    }
    part def LMDescent {
        part dps : DPS;
        part descentO2 : Consumable;
        part descentWater : Consumable;
    }
    part def LMAscent {
        part aps : APS;
        part lgc : LGC;
        part lmDsky : DSKY;
        part ags : AGS;
        part aea : AEA;
        part asa : ASA;
        part lmUsb : USB;
        part ascentO2a : Consumable;
        part ascentO2b : Consumable;
        part ascentWaterA : Consumable;
        part ascentWaterB : Consumable;
    }
    part def F1;
    part def J2;
    part def SPS;
    part def DPS;
    part def APS;
    part def CMC;
    part def LGC;
    part def DSKY;
    part def AGS;
    part def AEA;
    part def ASA;
    part def LVDC;
    part def ST124;
    part def FCC;
    part def EMS;
    part def USB;
    part def CMECS;
    part def Consumable;

    part def MissionControlHouston {
        part mocr : MOCR;
        part ssrs : StaffSupportRooms;
        part rtcc : RealTimeComputerComplex;
        part ccats : CCATS;
        part displayControl : DisplayAndControl;
    }
    part def MOCR {
        part flight : FLIGHT;
        part capcom : CAPCOM;
        part eecom : EECOM;
        part gncProp : GNCandProp;
        part fdo : FDO;
        part retro : RETRO;
        part guido : GUIDO;
        part surgeon : SURGEON;
        part network : NETWORK;
        part ccc : CCC;
    }
    part def FLIGHT;
    part def CAPCOM;
    part def EECOM;
    part def GNCandProp;
    part def FDO;
    part def RETRO;
    part def GUIDO;
    part def SURGEON;
    part def NETWORK;
    part def CCC;
    part def StaffSupportRooms;
    part def RealTimeComputerComplex {
        part ibm360a : IBM360_75;
        part ibm360b : IBM360_75;
        part ibm360c : IBM360_75;
        part ibm360d : IBM360_75;
        part ibm360e : IBM360_75;
    }
    part def IBM360_75;
    part def CCATS;
    part def DisplayAndControl;

    part def GoddardSpaceFlightCenter {
        part nascom : NASCOM;
        part nttf : NTTF;
        part networkSupportTeam : NetworkSupportTeam;
    }
    part def NASCOM;
    part def NTTF;
    part def NetworkSupportTeam;

    part def MannedSpaceFlightNetwork {
        part goldstone85 : USB85ft;
        part madrid85 : USB85ft;
        part honeysuckle85 : USB85ft;
        part dsnWings : DSNWings;
        part named30ftUsb : Named30ftUSB;
        part vanguard : AISShip;
        part huntsville : AISShip;
        part redstone : AISShip;
        part aisShip4Unknown : AISShip;
        part aria : ARIASet;
        part goldstone210 : USB210ft;
        part parkes : Parkes;
        part site642B : CommandSite;
    }
    part def USB85ft;
    part def DSNWings;
    part def Named30ftUSB;
    part def AISShip;
    part def ARIASet;
    part def USB210ft;
    part def Parkes;
    part def CommandSite;

    part def KennedyLC39 {
        part firingRoom1 : FiringRoom;
        part rca110aLcc : RCA110A;
        part rca110aMl : RCA110A;
        part ace : ACE;
        part umbilicals : Umbilicals;
        part padCryo : PadCryo;
    }
    part def FiringRoom;
    part def RCA110A;
    part def ACE;
    part def Umbilicals;
    part def PadCryo;
    part def RangeSafetyAFETR;
    part def RecoveryForces {
        part tf130 : TF130;
        part hornet : Hornet;
        part udt : UDT;
        part helos : RecoveryHelos;
    }
    part def TF130;
    part def Hornet;
    part def UDT;
    part def RecoveryHelos;

    part def Commander {
        part a7l : A7L;
        part bio : BioSensor;
        part comm : CrewComm;
        part plss : PLSS;
        part ops : OPS;
    }
    part def CommandModulePilot {
        part a7l : A7L;
        part bio : BioSensor;
        part comm : CrewComm;
    }
    part def LunarModulePilot {
        part a7l : A7L;
        part bio : BioSensor;
        part comm : CrewComm;
        part plss : PLSS;
        part ops : OPS;
    }
    part def A7L;
    part def BioSensor;
    part def CrewComm;
    part def PLSS;
    part def OPS;

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
        state tli;
        state translunar;
        state dockEject;
        state loi;
        state undock;
        state doi;
        state descent;
        state surfaceEva;
        state ascent;
        state rendezvous;
        state tei;
        state entry;
        state recovery;
        transition liftoff first countdown accept towerClear then boost;
        transition seoi first boost accept orbitalInsertion then earthOrbit;
        transition startTli first earthOrbit accept tliBurn then tli;
        transition tliCutoff first tli accept tliComplete then translunar;
        transition dock first translunar accept transpositionDocking then dockEject;
        transition startLoi first dockEject accept loiBurn then loi;
        transition loiCutoff first loi accept lunarOrbit then undock;
        transition startDoi first undock accept doiBurn then doi;
        transition startDescent first doi accept p63 then descent;
        transition touchdown first descent accept p68 then surfaceEva;
        transition startAscent first surfaceEva accept p12 then ascent;
        transition startRndz first ascent accept p30 then rendezvous;
        transition startTei first rendezvous accept teiBurn then tei;
        transition startEntry first tei accept ei then entry;
        transition splashdown first entry accept recoveryForce then recovery;
    }

    state def AbortMode {
        entry; then nominal;
        state nominal;
        state padLes;
        state modeI;
        state modeII;
        state modeIII;
        state modeIV;
        state contingencyTli;
        state spsAbort;
        state p70Dps;
        state p71Aps;
        transition lesAbort first nominal accept padAbort then padLes;
        transition abortModeI first nominal accept modeI then modeI;
        transition abortModeII first nominal accept modeII then modeII;
        transition abortModeIII first nominal accept modeIII then modeIII;
        transition abortModeIV first nominal accept modeIV then modeIV;
        transition abortTli first nominal accept contingencyTli then contingencyTli;
        transition abortSps first nominal accept spsAbort then spsAbort;
        transition abortP70 first nominal accept p70 then p70Dps;
        transition abortP71 first nominal accept p71 then p71Aps;
    }

    state def LgcMajorMode {
        entry; then p00;
        state p00;
        state p12;
        state p20;
        state p27;
        state p30;
        state p31;
        state p32;
        state p33;
        state p34;
        state p35;
        state p40;
        state p42;
        state p51;
        state p52;
        state p57;
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

    state def CmcMajorMode {
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
        state p63;
        state p64;
        state p65;
        state p66;
        state p67;
        transition toP11 first p00 accept p11 then p11;
        transition toP40 first p00 accept p40 then p40;
        transition toP61 first p00 accept p61 then p61;
        transition toP62 first p61 accept p62 then p62;
        transition toP67 first p62 accept p67 then p67;
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
    requirement cmEcsRequirement { doc /* CM ECS: 3 crew / 14 d spec; 5.0 psia 100% O2; CO2 ≤7.6 torr; SM O2 640 lb; potable 36 lb / waste 56 lb; LiOH 1.5 man-day, swap 12 h. A11 mission 196 h vs 336 h spec. */ }
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
    requirement agcRequirement { doc /* Two AGCs. Block II: 16-bit, 2048 E / 36864 F, 1.024 MHz, MCT 11.7 μs (AGCIS 30). CM = 1 AGC + 2 DSKY. LM = 1 AGC + 1 DSKY. Do not merge. CM Colossus; LM Luminary. A11 rope IDs UNKNOWN. */ }
    requirement agsRequirement { doc /* AGS is a separate computer (AEA+ASA). Memory UNKNOWN. R47 inits it from PNGS. */ }
    requirement iuGncRequirement { doc /* IU LVDC + ST-124 + FCC stays separate from AGC. IU owns boost+TLI. */ }
    requirement emsRequirement { doc /* EMS is a CM part, independent of AGC. */ }
    requirement rsoRequirement { doc /* RSO/AFETR is OUTSIDE MCC. UHF destruct, safed after Earth orbit. RSO owns destruct until orbital safing. */ }
    requirement rtccRequirement { doc /* RTCC: five IBM 360/75. MOC+DSC roles; which-is-which on A11 UNKNOWN. */ }
    requirement msfnSiteRequirement { doc /* 3×85-ft USB: Goldstone, Madrid, Honeysuckle + DSN wings. Named 30-ft only — do NOT merge GSFC-1968 and TN D-6723 into “the 14”; complete 30-ft inventory UNKNOWN. 4 AIS ships: Vanguard, Huntsville, Redstone + 4th UNKNOWN. 8 ARIA (no command/track). Goldstone 210-ft + Parkes for A11 descent/TV. */ }
    requirement kscRequirement { doc /* KSC LC-39: Firing Room 1, RCA 110A pair (LCC + ML), ACE in O&C, umbilicals, pad cryo. Handoff MCC at tower clear. */ }

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
    attribute tourUnknown;

    action powerOnCmc;
    action powerOnLgc;
    action selectAntenna;
    action sendPathA;
    action sendP27;
    action r47InitAgs;
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

    allocation allocateBoostToIu;
    allocation allocateTliToIu;
    allocation allocateDestructToRso;
    allocation allocateCmcToCm;
    allocation allocateLgcToLm;
    allocation allocateAgsToLm;
    allocation allocateEmsToCm;
    allocation allocateLvdcToIu;
    allocation allocatePathAToCcats;
    allocation allocatePathBToP27;
}
