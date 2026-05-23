# Skill: Generate SysML v2 Model from System Description

Use this prompt to generate a `.sysml` SysML v2 textual model from a plain-English system description.

---

## Prompt

You are an expert systems engineer using SysML v2 textual notation. Generate a SysML v2 `.sysml` model for the following system.

**System description:**
```
[SYSTEM DESCRIPTION]
```

**Rules:**
1. Use a single top-level `package` named after the system (PascalCase).
2. Define the top-level system as a `part def SystemName { ... }`.
3. Decompose the system into named sub-parts using `part partName : PartType;` inside the system definition.
4. Declare connections between parts using `connection connName connect portA to portB;`.
5. Define port types at the package level using `port def PortTypeName;`.
6. Declare ports on parts using `port portName : PortTypeName;`.
7. Define each sub-part type at the package level using `part def PartTypeName;` (no body needed for leaf parts).
8. Add a state machine for the primary operational behavior using `state def SystemControl { entry; then initialState; state stateName; transition tName first s1 accept eventName then s2; }`.
9. Declare requirements using `requirement reqName { doc /* requirement text */ }`.
10. Keep the model concise — define structure and behavior, not implementation details.

**Output format:** Return only the `.sysml` file content, no explanations.

---

## Example Output

```sysml
package Toaster {
    part def Toaster {
        part lever : Lever;
        part heatingElement : HeatingElement;
        part carriage : Carriage;

        port leverInput : UserInterfacePort;
        port leverControlOut : ControlPort;

        connection leverToHeater connect leverControlOut to heatingElement.controlIn;
    }

    part def Lever;
    part def HeatingElement {
        port controlIn : ControlPort;
    }
    part def Carriage;

    port def UserInterfacePort;
    port def ControlPort;

    state def ToasterControl {
        entry; then idle;
        state idle;
        state heating;
        transition leverDown first idle accept leverDown then heating;
        transition timerDone first heating accept timerExpired then idle;
    }

    requirement toastSafetyRequirement { doc /* The toaster shall not cause burns or fire under normal operating conditions. */ }
}
```
