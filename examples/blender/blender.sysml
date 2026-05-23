package Blender {
    part def Blender {
        part tamper : Tamper;
        part lid : Lid;
        part container : Container;
        part bladeAssembly : BladeAssembly;
        part driveCoupling : DriveCoupling;
        part smoothnessSensor : SmoothnessSensor;
        part motorBase : MotorBase;
        part motor : Motor;
        part controlPanel : ControlPanel;

        port tamperLidMechanical : MechanicalPort;
        port lidTamperMechanical : MechanicalPort;
        port lidContainerMechanical : MechanicalPort;
        port containerLidMechanical : MechanicalPort;
        port containerBladeMount : MechanicalPort;
        port bladeMountIn : MechanicalPort;
        port containerMechanical : MechanicalPort;
        port baseMechanical : MechanicalPort;
        port baseMotorMountOut : MechanicalPort;
        port motorMountIn : MechanicalPort;
        port baseControlPanelMountOut : MechanicalPort;
        port panelMountIn : MechanicalPort;
        port baseCouplingMountOut : MechanicalPort;
        port couplingMountIn : MechanicalPort;
        port bladeDriveIn : DrivePort;
        port couplingDriveOut : DrivePort;
        port couplingDriveIn : DrivePort;
        port motorDriveOut : DrivePort;
        port couplingVibrationOut : SensorPort;
        port sensorVibrationIn : SensorPort;
        port sensorCompleteOut : ControlPort;
        port panelCompleteIn : ControlPort;
        port panelMotorCommandOut : ControlPort;
        port motorCommandIn : ControlPort;

        connection tamperToLid connect tamperLidMechanical to lidTamperMechanical;
        connection lidToContainer connect lidContainerMechanical to containerLidMechanical;
        connection containerToBlade connect containerBladeMount to bladeMountIn;
        connection containerToBase connect containerMechanical to baseMechanical;
        connection motorBaseToMotor connect baseMotorMountOut to motorMountIn;
        connection motorBaseToControlPanel connect baseControlPanelMountOut to panelMountIn;
        connection motorBaseToDriveCoupling connect baseCouplingMountOut to couplingMountIn;
        connection couplingToBlade connect couplingDriveOut to bladeDriveIn;
        connection motorToCoupling connect motorDriveOut to couplingDriveIn;
        connection couplingToSensor connect couplingVibrationOut to sensorVibrationIn;
        connection sensorToControlPanel connect sensorCompleteOut to panelCompleteIn;
        connection controlPanelToMotor connect panelMotorCommandOut to motorCommandIn;
    }

    part def Tamper;
    part def Lid;
    part def Container;
    part def BladeAssembly;
    part def DriveCoupling;
    part def SmoothnessSensor;
    part def MotorBase;
    part def Motor;
    part def ControlPanel;

    port def MechanicalPort;
    port def DrivePort;
    port def SensorPort;
    port def ControlPort;

    state def BlenderControl {
        entry; then off;

        state off;
        state powered {
            entry; then ready;

            state ready;
            state blending;
            state error;

            transition start
                first ready
                accept startCommand
                then blending;

            transition smoothieComplete
                first blending
                accept smoothnessSignal
                then ready;

            transition stopCommand
                first blending
                accept stopCommand
                then ready;

            transition timeout
                first blending
                accept timeout
                then ready;

            transition fault
                first blending
                accept fault
                then error;

            transition lidOpened
                first blending
                accept lidOpened
                then error;

            transition bladeJam
                first blending
                accept bladeJam
                then error;

            transition overcurrent
                first blending
                accept overcurrent
                then error;

            transition sensorFault
                first blending
                accept sensorFault
                then error;

            transition resetError
                first error
                accept reset
                then ready;
        }

        transition powerOn
            first off
            accept powerSwitchOn
            then powered;

        transition powerOff
            first powered
            accept powerSwitchOff
            then off;
    }

    package BlenderModel;
    package BlenderStructure;
    package BlenderBehavior;
    package BlenderRequirements;
    package BlenderAnalysis;
    package BlenderVerification;

    part user : User;
    part mainsSupply : MainsSupply;
    part ingredients : Ingredients;
    part smoothie : Smoothie;
    part def User;
    part def MainsSupply;
    part def Ingredients;
    part def Smoothie;

    interface def UserControlsInterface;
    interface def PowerInterface;
    interface def DriveInterface;
    interface def SensingInterface;
    interface def ContainerInterface;
    item def Fruit;
    item def Liquid;
    item def ElectricalEnergy;
    item def RotationalEnergy;
    item def SmoothnessSignal;
    item def UserCommand;

    flow ingredientsIntoContainer;
    flow commandToControlPanel;
    flow mainsPowerFlow;
    flow motorTorqueFlow;
    flow bladeShearFlow;
    flow smoothnessFeedbackFlow;

    requirement lidInterlockRequirement             { doc /* The motor shall not run unless the lid is fully seated and locked. */ }
    requirement motorControlRequirement             { doc /* The control panel shall start, pause, and stop the motor in response to user commands within 200 ms. */ }
    requirement smoothnessDetectionRequirement      { doc /* The smoothness sensor shall detect blend completion and signal the control panel when the threshold is reached. */ }
    requirement powerRequirement                    { doc /* The blender shall operate within its rated power envelope under all normal blending loads. */ }
    requirement userControlsRequirement             { doc /* The user shall be able to start, pause, and stop blending without tools. */ }
    requirement cleaningRequirement                 { doc /* The container, lid, and blade assembly shall be dishwasher-safe or washable under running water. */ }
    requirement serviceRequirement                  { doc /* The blender shall be serviceable by a qualified technician without specialized equipment. */ }
    requirement motorSpeedRequirement               { doc /* The motor shall maintain set speed within ±10% across all normal blending loads. */ }
    requirement interlockLatencyRequirement         { doc /* The lid interlock shall disable the motor within 50 ms of lid removal detection. */ }
    requirement overcurrentProtectionRequirement    { doc /* The motor circuit shall include overcurrent protection that cuts power before motor damage occurs. */ }
    requirement smoothnessThresholdRequirement      { doc /* The smoothness sensor threshold shall be configurable to support at least three blend program profiles. */ }
    requirement noiseRequirement                    { doc /* The blender shall operate below 85 dB(A) at the operator position during normal use. */ }
    requirement containerSeatRequirement            { doc /* The container shall lock to the motor base with a positive mechanical engagement requiring deliberate user action to release. */ }

    constraint def torqueSpeedLoadEstimate;
    constraint def smoothnessThresholdEstimate;
    constraint def motorPowerLimit;
    constraint def blendTimingEstimate;
    constraint def noisePowerTradeoff;
    constraint def interlockStopTiming;
    attribute commandedSpeed;
    attribute motorTorque;
    attribute blendDuration;
    attribute smoothnessIndex;
    attribute motorSpeed;
    attribute interlockLatency;
    attribute motorPower;
    attribute noiseLevel;

    action loadIngredients;
    action closeLid;
    action powerOnBlender;
    action startBlendProgram;
    action spinBladeAssembly;
    action senseSmoothness;
    action stopMotor;
    action pourSmoothie;

    interaction smoothieProgramInteraction;
    use case makeSmoothieUseCase;
    use case stopBlendUseCase;
    use case cleanContainerUseCase;
    analysis case motorLoadAnalysis;
    analysis case smoothnessDetectionAnalysis;
    verification case verifyLidInterlock;
    verification case verifySmoothnessDetection;
    verification case verifyStopCommand;
    verification case verifyOvercurrentProtection;
    verification case verifyContainerSeat;

    allocation allocateInterlockToControlPanel;
    allocation allocateTorqueToMotor;
    allocation allocateSmoothnessToSensor;
    allocation allocateCleaningToContainer;
    allocation allocateProtectionToMotorBase;
    allocation allocateInterfaceToControlPanel;
}
