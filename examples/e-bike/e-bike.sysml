package ElectricBike {
    part def ElectricBike {
        part frame : Frame;
        part batteryPack : BatteryPack;
        part motorController : MotorController;
        part hubMotor : HubMotor;
        part humanInterface : HumanInterface;
        part brakeSystem : BrakeSystem;
        part cadenceSensor : CadenceSensor;

        port riderCommandIn : RiderPort;
        port chargerIn : ChargePort;
        port roadLoadIn : MechanicalPort;
        port frameBatteryMountOut : MechanicalPort;
        port batteryMountIn : MechanicalPort;
        port frameMotorMountOut : MechanicalPort;
        port motorMountIn : MechanicalPort;
        port frameInterfaceMountOut : MechanicalPort;
        port interfaceMountIn : MechanicalPort;
        port frameBrakeMountOut : MechanicalPort;
        port brakeMountIn : MechanicalPort;
        port batteryPowerOut : PowerPort;
        port controllerPowerIn : PowerPort;
        port controllerDriveOut : DrivePort;
        port motorDriveIn : DrivePort;
        port interfaceCommandOut : ControlPort;
        port controllerCommandIn : ControlPort;
        port brakeInhibitOut : ControlPort;
        port controllerInhibitIn : ControlPort;
        port riderInputIn : RiderPort;
        port chargeInputIn : ChargePort;
        port wheelLoadIn : MechanicalPort;

        connection riderToInterface connect riderCommandIn to riderInputIn;
        connection chargerToBattery connect chargerIn to chargeInputIn;
        connection roadToMotor connect roadLoadIn to wheelLoadIn;
        connection frameToBattery connect frameBatteryMountOut to batteryMountIn;
        connection frameToMotor connect frameMotorMountOut to motorMountIn;
        connection frameToInterface connect frameInterfaceMountOut to interfaceMountIn;
        connection frameToBrakes connect frameBrakeMountOut to brakeMountIn;
        connection batteryToController connect batteryPowerOut to controllerPowerIn;
        connection controllerToMotor connect controllerDriveOut to motorDriveIn;
        connection interfaceToController connect interfaceCommandOut to controllerCommandIn;
        connection brakesToController connect brakeInhibitOut to controllerInhibitIn;
    }

    part def Frame;
    part def BatteryPack {
        part bms : BMS;
    }
    part def BMS;
    part def MotorController;
    part def HubMotor { doc /* Rear geared hub. No regenerative braking. */ }
    part def HumanInterface { doc /* Cadence PAS and display only. No throttle. */ }
    part def BrakeSystem;
    part def CadenceSensor;

    port def RiderPort;
    port def ChargePort;
    port def MechanicalPort;
    port def PowerPort;
    port def DrivePort;
    port def ControlPort;

    state def RideControl {
        entry; then off;

        state off;
        state standby;
        state assist;
        state charging;
        state fault;

        transition powerOn
            first off
            accept powerButton
            then standby;

        transition startAssist
            first standby
            accept cadencePedal
            then assist;

        transition stopAssist
            first assist
            accept noPedal
            then standby;

        transition brakeCut
            first assist
            accept brakeLever
            then standby;

        transition plugIn
            first off
            accept chargerConnected
            then charging;

        transition chargeComplete
            first charging
            accept chargeFull
            then off;

        transition unplug
            first charging
            accept chargerRemoved
            then off;

        transition powerOff
            first standby
            accept powerButton
            then off;

        transition faultFromAssist
            first assist
            accept overcurrentOrCutout
            then fault;

        transition resetFault
            first fault
            accept reset
            then off;
    }

    package BikeModel;
    package BikeStructure;
    package BikeBehavior;
    package BikeRequirements;
    package BikeAnalysis;
    package BikeVerification;

    part rider : Rider;
    part charger : Charger;
    part road : Road;
    part def Rider;
    part def Charger;
    part def Road;

    interface def RiderInterface;
    interface def ChargeInterface;
    interface def DriveInterface;
    interface def BrakeInterface;
    item def PedalCadence;
    item def ThrottleCommand { doc /* Unused by this EPAC. Not on RideControl or HumanInterface. */ }
    item def ElectricalEnergy;
    item def WheelTorque;
    item def BrakeInhibit;
    item def ChargeEnergy;

    flow riderCommandFlow;
    flow chargeEnergyFlow;
    flow batteryPowerFlow;
    flow motorTorqueFlow;
    flow brakeInhibitFlow;
    flow roadLoadFlow;

    requirement rideSafetyRequirement       { doc /* Motor fail-silent: brake input, controller, cadence/speed sensors, and BMS shall cut motor torque before the wheel can keep driving the rider. */ }
    requirement rangeRequirement            { doc /* Tour-mode scenario only: at least 60 km on a 500 Wh pack (~8.3 Wh/km). Not Eco / PAS-1; undemonstrated unless this scenario is bound. */ }
    requirement assistLimitRequirement      { doc /* EPAC (EN 15194): cadence PAS only, no certified throttle. Assist shall cut off at 25 km/h. */ }
    requirement chargeSafetyRequirement     { doc /* Charging shall stop on over-temperature, over-voltage, or charger disconnect. UL 2849: the BMS inside the pack opens the contactor. */ }
    requirement brakeOverrideRequirement    { doc /* Electronic inhibit shall assert within 50 ms of either brake lever. This is ~10x tighter than the EN 15194 distance test. */ }
    requirement en15194DistanceRequirement  { doc /* EN 15194 distance cutoff: assistance shall cease within 5 m after pedaling stops, and within 2 m where that tighter clause applies. */ }
    requirement batteryCutoffRequirement    { doc /* The BMS shall open the pack contactor before any cell exceeds its voltage or temperature limit. */ }
    requirement displayRequirement          { doc /* The rider shall see speed, assist level, and remaining range without removing hands from the bars. */ }
    requirement structuralRequirement       { doc /* The frame shall carry rider, cargo, and battery loads without yielding. */ }
    requirement lightingRequirement         { doc /* Lighting shall follow StVZO / ISO 6742. Not UN ECE R113. */ }

    constraint def energyBalance;
    constraint def rangeEstimate;
    constraint def assistPowerLimit;
    constraint def brakeLatencyLimit;
    constraint def tourRangeBind;
    attribute packEnergy;
    attribute riderPower;
    attribute assistPower;
    attribute rangeKm;
    attribute cutoffSpeed;
    attribute brakeLatency;
    attribute tourWhPerKm;

    action powerOnBike;
    action selectAssist;
    action pedalAndThrottle;
    action applyBrake;
    action inhibitMotor;
    action deliverTorque;
    action plugInCharger;
    action stopCharge;

    interaction startRideInteraction;
    use case rideBikeUseCase {
        include adjustAssistUseCase;
    }
    use case chargeBikeUseCase;
    use case adjustAssistUseCase;
    analysis case rangeAnalysis;
    analysis case tourRangeAnalysis;
    analysis case brakeLatencyAnalysis;
    verification case verifyRange;
    verification case verifyBrakeCutoff;
    verification case verifyChargeSafety;
    verification case verifyAssistLimit;

    allocation allocateSafetyToBrakes;
    allocation allocateSafetyToController;
    allocation allocateSafetyToBms;
    allocation allocateSafetyToSensors;
    allocation allocateRangeToBattery;
    allocation allocateAssistToController;
    allocation allocateChargeToBms;
}
