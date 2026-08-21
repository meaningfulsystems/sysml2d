package ElectricBike {
    part def ElectricBike {
        part frame : Frame;
        part batteryPack : BatteryPack;
        part motorController : MotorController;
        part hubMotor : HubMotor;
        part humanInterface : HumanInterface;
        part brakeSystem : BrakeSystem;
        part cadenceSensor : CadenceSensor;
        part wheelSpeedSensor : WheelSpeedSensor;

        connection frameToBattery connect frame.batteryMountOut to batteryPack.mountIn;
        connection frameToMotor connect frame.motorMountOut to hubMotor.mountIn;
        connection frameToInterface connect frame.interfaceMountOut to humanInterface.mountIn;
        connection frameToBrakes connect frame.brakeMountOut to brakeSystem.mountIn;
        connection batteryToController connect batteryPack.powerOut to motorController.powerIn;
        connection controllerToMotor connect motorController.driveOut to hubMotor.driveIn;
        connection interfaceToController connect humanInterface.commandOut to motorController.commandIn;
        connection brakesToController connect brakeSystem.inhibitOut to motorController.inhibitIn;
        connection cadenceToController connect cadenceSensor.cadenceOut to motorController.sensorIn;
        connection wheelSpeedToController connect wheelSpeedSensor.speedOut to motorController.sensorIn;
        connection riderToInterface connect humanInterface.riderIn to humanInterface.commandOut;
        connection chargerToBattery connect batteryPack.bms.chargerIn to batteryPack.powerOut;
        connection roadToMotor connect hubMotor.roadLoadIn to hubMotor.driveIn;
    }

    part def Frame {
        port batteryMountOut : MechanicalPort;
        port motorMountOut : MechanicalPort;
        port interfaceMountOut : MechanicalPort;
        port brakeMountOut : MechanicalPort;
    }
    part def BatteryPack {
        part bms : BMS;
        port mountIn : MechanicalPort;
        port powerOut : PowerPort;
        connection bmsToPackPower connect bms.contactorOut to powerOut;
    }
    part def BMS {
        port chargerIn : ChargePort;
        port contactorOut : PowerPort;
    }
    part def MotorController {
        port powerIn : PowerPort;
        port driveOut : DrivePort;
        port commandIn : ControlPort;
        port inhibitIn : ControlPort;
        port sensorIn : ControlPort;
    }
    part def HubMotor {
        doc /* Rear geared hub. No regenerative braking. */
        port mountIn : MechanicalPort;
        port driveIn : DrivePort;
        port roadLoadIn : MechanicalPort;
    }
    part def HumanInterface {
        doc /* Cadence PAS, walk assist, and display. No throttle. */
        port mountIn : MechanicalPort;
        port commandOut : ControlPort;
        port riderIn : RiderPort;
    }
    part def BrakeSystem {
        port mountIn : MechanicalPort;
        port inhibitOut : ControlPort;
    }
    part def CadenceSensor {
        port cadenceOut : ControlPort;
    }
    part def WheelSpeedSensor {
        port speedOut : ControlPort;
    }

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
        state walk { doc /* do / speed <= 6 km/h. EPAC walk assist, not a throttle. */ }
        state charging { doc /* EPAC: Charging only from Off, not Standby. */ }
        state fault { doc /* resetFault is Fault→Off, not Standby. */ }

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

        transition startWalk
            first standby
            accept walkButton
            then walk;

        transition stopWalk
            first walk
            accept walkRelease
            then standby;

        transition brakeWalk
            first walk
            accept brakeLever
            then standby;

        transition brakeCut
            first assist
            accept brakeLever
            then standby;

        transition plugIn
            first off
            accept chargerConnected
            then charging;  // EPAC: charge only from Off

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
            then off;  // locked: Fault→Off, not Standby
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
    item def WalkAssistCommand { doc /* EPAC walk assist ≤ 6 km/h. Not a throttle. */ }
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

    requirement rideSafetyRequirement       { doc /* Motor fail-silent: brake input, controller, cadenceSensor, wheelSpeedSensor, and BMS shall cut motor torque before the wheel can keep driving the rider. Cadence-only cannot enforce 25 km/h. */ }
    requirement rangeRequirement            { doc /* Tour-mode scenario only: usableWh 500 Wh / energyPerKm ~8.3 Wh/km ≥ 60 km. Not Eco / PAS-1; undemonstrated unless this scenario is bound. */ }
    requirement assistLimitRequirement      { doc /* EPAC (EN 15194): cadence PAS only, no certified throttle. Assist shall cut off at 25 km/h — enforced by wheelSpeedSensor; cadence-only cannot enforce 25 km/h. Walk assist ≤ 6 km/h is a real EPAC feature, not a throttle. */ }
    requirement walkAssistRequirement       { doc /* EPAC walk assist shall not exceed 6 km/h. Walk assist is not a throttle. */ }
    requirement continuousPowerRequirement  { doc /* Continuous assist shall not exceed 250 W. */ }
    requirement chargeSafetyRequirement     { doc /* Charging shall stop on over-temperature, over-voltage, or charger disconnect. UL 2849: the BMS inside the pack opens the contactor. */ }
    requirement brakeOverrideRequirement    { doc /* Electronic inhibit shall assert within 50 ms of either brake lever. This is ~10x tighter than the EN 15194 distance test. */ }
    requirement en15194DistanceRequirement  { doc /* EN 15194 distance cutoff: assistance shall cease within 5 m after pedaling stops, and within 2 m where that tighter clause applies. */ }
    requirement batteryCutoffRequirement    { doc /* The BMS shall open the pack contactor before any cell exceeds its voltage or temperature limit. */ }
    requirement displayRequirement          { doc /* The rider shall see speed, assist level, and remaining range without removing hands from the bars. */ }
    requirement structuralRequirement       { doc /* The frame shall carry rider, cargo, and battery loads without yielding. */ }
    requirement lightingRequirement         { doc /* Lighting shall follow StVZO / ISO 6742. Not UN ECE R113. */ }

    constraint def energyBalance { doc /* Pack electrical energy only. Do not add rider watts to pack energy; they are different sources. */ }
    constraint def riderInputBalance { doc /* Rider pedal watts are a mechanical source, not pack energy. */ }
    constraint def rangeEstimate;
    constraint def assistPowerLimit;
    constraint def brakeLatencyLimit;
    constraint def tourRangeBind { doc /* Tour 60 km: usableWh / energyPerKm. Do not mix rider watts into pack usableWh. */ }
    constraint def thermalDerate;
    attribute packEnergy;
    attribute usableWh;
    attribute energyPerKm;
    attribute packVoltage;
    attribute riderPower;
    attribute assistPower;
    attribute rangeKm;
    attribute cutoffSpeed;
    attribute walkAssistSpeed;
    attribute continuousPowerW;
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
    allocation allocateSafetyToWheelSpeed;
    allocation allocateRangeToBattery;
    allocation allocateAssistToController;
    allocation allocateAssistToWheelSpeed;
    allocation allocateChargeToBms;
}
