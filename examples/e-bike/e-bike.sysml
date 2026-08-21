package ElectricBike {
    part def ElectricBike {
        part frame : Frame;
        part batteryPack : BatteryPack;
        part motorController : MotorController;
        part hubMotor : HubMotor;
        part humanInterface : HumanInterface;
        part brakeSystem : BrakeSystem;

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
    part def BatteryPack;
    part def MotorController;
    part def HubMotor;
    part def HumanInterface;
    part def BrakeSystem;

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
            accept cadenceOrThrottle
            then assist;

        transition stopAssist
            first assist
            accept noPedalAndClosedThrottle
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
    item def ThrottleCommand;
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

    requirement rideSafetyRequirement       { doc /* Brake input shall cut motor torque before the wheel can keep driving the rider. */ }
    requirement rangeRequirement            { doc /* The bike shall provide at least 60 km of PAS-1 range on a 500 Wh pack. */ }
    requirement assistLimitRequirement      { doc /* Assist shall cut off at 25 km/h for the EU class being certified. */ }
    requirement chargeSafetyRequirement     { doc /* Charging shall stop on over-temperature, over-voltage, or charger disconnect. */ }
    requirement brakeOverrideRequirement    { doc /* Motor inhibit shall assert within 50 ms of either brake lever. */ }
    requirement batteryCutoffRequirement    { doc /* The BMS shall open the pack contactor before any cell exceeds its voltage or temperature limit. */ }
    requirement displayRequirement          { doc /* The rider shall see speed, assist level, and remaining range without removing hands from the bars. */ }
    requirement structuralRequirement       { doc /* The frame shall carry rider, cargo, and battery loads without yielding. */ }

    constraint def energyBalance;
    constraint def rangeEstimate;
    constraint def assistPowerLimit;
    constraint def brakeLatencyLimit;
    attribute packEnergy;
    attribute riderPower;
    attribute assistPower;
    attribute rangeKm;
    attribute cutoffSpeed;
    attribute brakeLatency;

    action powerOnBike;
    action selectAssist;
    action pedalAndThrottle;
    action applyBrake;
    action inhibitMotor;
    action deliverTorque;
    action plugInCharger;
    action stopCharge;

    interaction startRideInteraction;
    use case rideBikeUseCase;
    use case chargeBikeUseCase;
    use case lockBikeUseCase;
    use case adjustAssistUseCase;
    analysis case rangeAnalysis;
    analysis case brakeLatencyAnalysis;
    verification case verifyRange;
    verification case verifyBrakeCutoff;
    verification case verifyChargeSafety;
    verification case verifyAssistLimit;

    allocation allocateSafetyToBrakes;
    allocation allocateRangeToBattery;
    allocation allocateAssistToController;
    allocation allocateChargeToBms;
}
