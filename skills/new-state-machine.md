# Skill: Generate State Machine Intent from SysML Model

Use this prompt to generate a `StateView` intent JSON for `sysmld stm` from an existing `.sysml` model that contains a `state def`.

---

## Prompt

You are generating a SysMLD state machine view intent file. Given the SysML v2 model below, produce a valid JSON intent file for `sysmld stm` that shows the state machine for the primary control behavior.

**SysML v2 model:**
```sysml
[SYSML MODEL]
```

**Rules:**
1. Set `"kind": "StateView"`.
2. Set `"direction": "left-right"` (states flow left to right in sequence).
3. In `"states"`, declare every state in the `state def`. Use `"initial": true` for the initial pseudostate node and list it first. Do not use `"final": true` unless the state machine genuinely terminates — most control loops return to idle.
4. In `"transitions"`, list every transition. Use the SysML transition `accept` event name as `"label"`. Mark backward transitions (returning to an earlier state) naturally — the composer handles arc routing.
5. In `"aliases"`, map every state and transition to its fully qualified SysML name.
6. Use `"default_w": 130, "default_h": 60` for regular states. The composer sizes initial/final pseudostates automatically.

**Output format:** Return only the JSON, no explanations.

---

## Example Output

```json
{
  "diagram": "toaster-stm",
  "kind": "StateView",
  "name": "Toaster Control State Machine",
  "subject": "toasterControl",
  "model_files": ["toaster.sysml"],
  "direction": "left-right",
  "default_w": 130,
  "default_h": 60,
  "aliases": {
    "toasterControl": "Toaster::ToasterControl",
    "idle":           "Toaster::ToasterControl::idle",
    "heating":        "Toaster::ToasterControl::heating",
    "leverDown":      "Toaster::ToasterControl::leverDown",
    "timerExpired":   "Toaster::ToasterControl::timerExpired"
  },
  "states": {
    "initial": { "initial": true },
    "idle":    { "label": "Idle",    "model_ref": "idle" },
    "heating": { "label": "Heating", "model_ref": "heating" }
  },
  "transitions": [
    { "from": "initial", "to": "idle",    "label": "" },
    { "from": "idle",    "to": "heating", "label": "lever down",   "model_ref": "leverDown" },
    { "from": "heating", "to": "idle",    "label": "timer expired","model_ref": "timerExpired" }
  ]
}
```
