package StarterSystem {
    part def StarterSystem {
        part sensor : Sensor;
        part controller : Controller;
        part actuator : Actuator;

        port environmentIn : SignalPort;
        port sensorIn : SignalPort;
        port sensorOut : SignalPort;
        port controllerSenseIn : SignalPort;
        port controllerCmdOut : SignalPort;
        port actuatorIn : SignalPort;

        connection envToSensor connect environmentIn to sensorIn;
        connection sensorToController connect sensorOut to controllerSenseIn;
        connection controllerToActuator connect controllerCmdOut to actuatorIn;
    }

    part def Sensor;
    part def Controller;
    part def Actuator;

    port def SignalPort;

    state def Cycle {
        entry; then idle;

        state idle;
        state running;
        state fault;

        transition start
            first idle
            accept startCmd
            then running;

        transition stop
            first running
            accept stopCmd
            then idle;

        transition trip
            first running
            accept faultDetect
            then fault;

        transition reset
            first fault
            accept resetCmd
            then idle;
    }
}
