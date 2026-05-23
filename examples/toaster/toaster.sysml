package Toaster {
    part def Toaster {
        part lever : Lever;
        part powerAndControlSubsystem : PowerAndControlSubsystem;
        part heatingElement : HeatingElement;
        part carriage : Carriage;
        part chassis : Chassis;
        part buttons : Buttons;
        part crumbTray : CrumbTray;
        part powerCord : PowerCord;

        port leverInput : UserInterfacePort;
        port buttonInput : UserInterfacePort;
        port trayPullInput : UserInterfacePort;
        port mainsPower : PowerPort;
        port cordPowerIn : PowerPort;
        port cordPowerOut : PowerPort;
        port buttonUserInputIn : UserInterfacePort;
        port buttonControlOut : ControlPort;
        port buttonMountIn : MechanicalPort;
        port subsystemMountIn : MechanicalPort;
        port leverUserInputIn : UserInterfacePort;
        port leverControlOut : ControlPort;
        port leverMechanicalOut : MechanicalPort;
        port controlInput : ControlPort;
        port buttonControlIn : UserInterfacePort;
        port heatCommandOut : ControlPort;
        port heaterControlIn : ControlPort;
        port subsystemPowerIn : PowerPort;
        port heaterHeatOut : HeatPort;
        port carriageHeatIn : HeatPort;
        port carriageLeverIn : MechanicalPort;
        port carriageGuideIn : MechanicalPort;
        port crumbTrayUserInputIn : UserInterfacePort;
        port crumbTrayGuideIn : MechanicalPort;
        port chassisGuideOut : MechanicalPort;
        port chassisButtonMountOut : MechanicalPort;
        port chassisSubsystemMountOut : MechanicalPort;
        port chassisCrumbTrayGuideOut : MechanicalPort;

        connection leverInputToLever connect leverInput to leverUserInputIn;
        connection buttonInputToButtons connect buttonInput to buttonUserInputIn;
        connection trayPullToCrumbTray connect trayPullInput to crumbTrayUserInputIn;
        connection buttonsToPowerControl connect buttonControlOut to buttonControlIn;
        connection mainsToCord connect mainsPower to cordPowerIn;
        connection cordToPowerControl connect cordPowerOut to subsystemPowerIn;
        connection leverToControl connect leverControlOut to controlInput;
        connection leverToCarriage connect leverMechanicalOut to carriageLeverIn;
        connection chassisToCarriage connect chassisGuideOut to carriageGuideIn;
        connection chassisToButtons connect chassisButtonMountOut to buttonMountIn;
        connection chassisToPowerControl connect chassisSubsystemMountOut to subsystemMountIn;
        connection chassisToCrumbTray connect chassisCrumbTrayGuideOut to crumbTrayGuideIn;
        connection controlToHeater connect heatCommandOut to heaterControlIn;
        connection heaterToCarriage connect heaterHeatOut to carriageHeatIn;
    }

    part def Lever;
    part def PowerAndControlSubsystem;
    part def HeatingElement;
    part def Carriage;
    part def Chassis;
    part def Buttons;
    part def CrumbTray;
    part def PowerCord;

    port def UserInterfacePort;
    port def PowerPort;
    port def ControlPort;
    port def HeatPort;
    port def MechanicalPort;

    state def ToasterControl {
        entry; then idle;

        state idle;
        state heating;
        state done;
        state error;

        transition leverDown
            first idle
            accept leverDown
            then heating;

        transition timerExpired
            first heating
            accept timerExpired
            then done;

        transition carriageUpDone
            first done
            accept carriageUp
            then idle;

        transition overheat
            first heating
            accept overheat
            then error;

        transition carriageJam
            first heating
            accept carriageJam
            then error;

        transition powerFault
            first heating
            accept powerFault
            then error;

        transition carriageUpAbort
            first heating
            accept carriageUp
            then idle;

        transition reset
            first error
            accept reset
            then idle;
    }

    package ToasterModel;
    package ToasterStructure;
    package ToasterBehavior;
    package ToasterRequirements;
    package ToasterAnalysis;
    package ToasterVerification;

    part user : User;
    part mainsSupply : MainsSupply;
    part environment : KitchenEnvironment;
    part def User;
    part def MainsSupply;
    part def KitchenEnvironment;

    interface def UserInterface;
    interface def PowerInterface;
    interface def ThermalInterface;
    interface def MechanicalInterface;
    item def BreadSlice;
    item def ToastSlice;
    item def ElectricalEnergy;
    item def HeatEnergy;
    item def UserCommand;
    item def CrumbDebris;

    flow breadIntoSlot;
    flow toastOutOfSlot;
    flow mainsPowerFlow;
    flow heatFlowToBread;
    flow crumbFlowToTray;
    flow userCommandFlow;

    requirement toastSafetyRequirement       { doc /* The toaster shall not cause burns, electrical shock, or fire under normal operating conditions. */ }
    requirement electricalSafetyRequirement  { doc /* The toaster shall comply with applicable electrical safety standards for household appliances. */ }
    requirement browningRequirement          { doc /* The toaster shall produce uniform browning across the full bread surface area for each browning level setting. */ }
    requirement timingRequirement            { doc /* The timer shall control heating duration within ±5% of the selected setting across all browning levels. */ }
    requirement userInterfaceRequirement     { doc /* The user shall be able to insert bread, select browning level, and cancel toasting without tools. */ }
    requirement cleanabilityRequirement      { doc /* The crumb tray shall be removable and washable without tools. */ }
    requirement serviceabilityRequirement    { doc /* The toaster shall be serviceable by a qualified technician without specialized equipment. */ }
    requirement powerRatingRequirement       { doc /* The toaster shall operate within its rated power consumption under all normal use conditions. */ }
    requirement surfaceTemperatureRequirement { doc /* Exterior surfaces accessible during operation shall not exceed safe touch temperature limits. */ }
    requirement thermalCutoffRequirement     { doc /* The toaster shall include a thermal cutoff that disables heating if internal temperature exceeds a safe threshold. */ }
    requirement browningLevelsRequirement    { doc /* The toaster shall provide at least three distinct and repeatable browning level settings. */ }
    requirement carriageReleaseRequirement   { doc /* The carriage shall release automatically when the timer expires or when the user presses cancel. */ }
    requirement crumbTrayForceRequirement    { doc /* The crumb tray shall require no more than 10 N removal force under all operating conditions. */ }
    requirement cycleLifeRequirement         { doc /* The toaster shall complete at least 10,000 toast cycles before requiring maintenance. */ }

    constraint def heatEnergyBalance;
    constraint def toastTimingEstimate;
    constraint def electricalPowerLimit;
    constraint def browningTemperatureEstimate;
    constraint def surfaceTemperatureLimit;
    constraint def carriageReleaseTiming;
    attribute targetBrowning;
    attribute toastTemperature;
    attribute toastDuration;
    attribute inputPower;
    attribute surfaceTemperature;
    attribute releaseTime;
    attribute trayRemovalForce;

    action insertBread;
    action lowerLever;
    action latchCarriage;
    action energizeHeater;
    action monitorToastTimer;
    action releaseCarriage;
    action presentToast;
    action removeCrumbTray;

    interaction toastCycleInteraction;
    use case toastBreadUseCase;
    use case cancelToastUseCase;
    use case emptyCrumbTrayUseCase;
    analysis case thermalPerformanceAnalysis;
    analysis case electricalLoadAnalysis;
    verification case verifyToastBrowning;
    verification case verifyElectricalSafety;
    verification case verifyCrumbTrayRemoval;
    verification case verifyCarriageRelease;
    verification case verifySurfaceTemperature;

    allocation allocateSafetyToPowerControl;
    allocation allocateHeatToHeater;
    allocation allocateBrowningToToastCycle;
    allocation allocateCleanabilityToCrumbTray;
    allocation allocateCarriageReleaseToMechanism;
    allocation allocateSurfaceTemperatureToChassis;
}
