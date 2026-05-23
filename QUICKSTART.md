# SysMLD Quick Start

This guide takes you from zero to a working model-backed diagram in about 10 minutes.

## 1. Install

Requires Python 3.11 or newer.

```bash
git clone https://github.com/meaningfulsystems/sysml2d.git
cd sysml2d
pip install -e .
```

Verify it works:

```bash
sysmld --help
```

## 2. Explore the Examples

The fastest way to understand SysMLD is to look at an existing example and regenerate it.

```bash
# Regenerate the toaster mechanical interconnection diagram
sysmld interconnection examples/toaster/toaster-mech-composed.json
sysmld render          examples/toaster/toaster-mech-composed.sysmld

# Open the result
open examples/toaster/toaster-mech-composed.svg
```

You should see a block diagram of the toaster's mechanical subsystem. The `.json` file is the compact input; the `.sysmld` file is the generated layout; the `.svg` is the rendered output.

## 3. Write Your First Model

Create a file called `coffee-maker.sysml`:

```sysml
package CoffeeMaker {
    part def CoffeeMaker {
        part waterTank   : WaterTank;
        part heater      : Heater;
        part pump        : Pump;
        part brewHead    : BrewHead;
        part controlPanel: ControlPanel;

        port mainsPower  : PowerPort;
        port waterIn     : FluidPort;
        port coffeeOut   : FluidPort;

        connection powerToHeater  connect mainsPower   to heater.powerIn;
        connection waterToTank    connect waterIn       to waterTank.fillPort;
        connection tankToPump     connect waterTank.out to pump.in;
        connection pumpToBrewHead connect pump.out      to brewHead.waterIn;
        connection controlToHeater connect controlPanel.heatCmd to heater.controlIn;
    }

    part def WaterTank  { port fillPort : FluidPort; port out : FluidPort; }
    part def Heater     { port powerIn  : PowerPort; port controlIn : ControlPort; }
    part def Pump       { port in : FluidPort; port out : FluidPort; }
    part def BrewHead   { port waterIn : FluidPort; }
    part def ControlPanel { port heatCmd : ControlPort; }

    port def PowerPort;
    port def FluidPort;
    port def ControlPort;
}
```

## 4. Write an Intent File

Create `coffee-maker-ibd.json` to describe the interconnection diagram:

```json
{
  "diagram":     "coffee-maker-ibd",
  "kind":        "InterconnectionView",
  "name":        "Coffee Maker Internal Structure",
  "subject":     "coffeeMaker",
  "model_files": ["coffee-maker.sysml"],
  "direction":   "left-right",
  "aliases": {
    "coffeeMaker":  "CoffeeMaker::CoffeeMaker",
    "waterTank":    "CoffeeMaker::CoffeeMaker::waterTank",
    "heater":       "CoffeeMaker::CoffeeMaker::heater",
    "pump":         "CoffeeMaker::CoffeeMaker::pump",
    "brewHead":     "CoffeeMaker::CoffeeMaker::brewHead",
    "controlPanel": "CoffeeMaker::CoffeeMaker::controlPanel"
  },
  "nodes": {
    "waterTank":    { "label": "Water Tank",    "style": "part.mechanical" },
    "heater":       { "label": "Heater",        "style": "part.thermal"    },
    "pump":         { "label": "Pump",          "style": "part.mechanical" },
    "brewHead":     { "label": "Brew Head",     "style": "part.mechanical" },
    "controlPanel": { "label": "Control Panel", "style": "part.control"    }
  },
  "edges": [
    { "from": "waterTank",    "to": "pump",      "label": "water flow" },
    { "from": "pump",         "to": "brewHead",  "label": "pressurised water" },
    { "from": "controlPanel", "to": "heater",    "label": "heat command" }
  ],
  "boundary_inputs": [
    { "to": "waterTank",    "label": "fill water" },
    { "to": "controlPanel", "label": "user input" }
  ],
  "styles": {
    "boundary.system":  { "fill": "#FFFFFF", "stroke": "#333333", "stroke_width": 2, "corner_radius": 12 },
    "part.mechanical":  { "fill": "#E8F5E9", "stroke": "#2E7D32", "stroke_width": 2, "corner_radius": 10 },
    "part.thermal":     { "fill": "#FFF3E0", "stroke": "#EF6C00", "stroke_width": 2, "corner_radius": 10 },
    "part.control":     { "fill": "#E3F2FD", "stroke": "#1565C0", "stroke_width": 2, "corner_radius": 10 },
    "connector.default":{ "stroke": "#334155", "stroke_width": 2, "corner_radius": 8 }
  }
}
```

## 5. Generate and Render

```bash
sysmld interconnection coffee-maker-ibd.json
sysmld render          coffee-maker-ibd.sysmld
open                   coffee-maker-ibd.svg
```

You now have a model-backed interconnection diagram generated deterministically from your SysML v2 model.

## 6. Validate Against the Model

```bash
sysmld validate coffee-maker-ibd.sysmld --strict
```

Strict validation checks that every element ID in the diagram resolves to a real named element in `coffee-maker.sysml`. If you rename something in the model, the validator will tell you exactly which diagram references broke.

## 7. Add a State Machine

Add a state def to `coffee-maker.sysml`:

```sysml
    state def CoffeeMakerControl {
        entry; then idle;
        state idle;
        state brewing;
        state done;
        state error;
        transition brew   first idle    accept brewCommand  then brewing;
        transition finish first brewing accept brewComplete then done;
        transition fault  first brewing accept overheat     then error;
        transition reset  first done    accept reset        then idle;
        transition clear  first error   accept reset        then idle;
    }
```

Create `coffee-maker-stm.json`:

```json
{
  "diagram":     "coffee-maker-stm",
  "kind":        "StateView",
  "name":        "Coffee Maker Control State Machine",
  "subject":     "coffeeMakerControl",
  "model_files": ["coffee-maker.sysml"],
  "direction":   "left-right",
  "default_w":   130,
  "default_h":   60,
  "aliases": {
    "coffeeMakerControl": "CoffeeMaker::CoffeeMakerControl",
    "idle":               "CoffeeMaker::CoffeeMakerControl::idle",
    "brewing":            "CoffeeMaker::CoffeeMakerControl::brewing",
    "done":               "CoffeeMaker::CoffeeMakerControl::done",
    "error":              "CoffeeMaker::CoffeeMakerControl::error"
  },
  "states": {
    "initial": { "initial": true },
    "idle":    { "label": "Idle",    "model_ref": "idle" },
    "brewing": { "label": "Brewing", "model_ref": "brewing" },
    "done":    { "label": "Done",    "model_ref": "done" },
    "error":   { "label": "Error",   "model_ref": "error" }
  },
  "transitions": [
    { "from": "initial", "to": "idle",    "label": "" },
    { "from": "idle",    "to": "brewing", "label": "brew command" },
    { "from": "brewing", "to": "done",    "label": "brew complete" },
    { "from": "brewing", "to": "error",   "label": "overheat" },
    { "from": "done",    "to": "idle",    "label": "reset" },
    { "from": "error",   "to": "idle",    "label": "reset" }
  ]
}
```

```bash
sysmld state  coffee-maker-stm.json
sysmld render coffee-maker-stm.sysmld
open          coffee-maker-stm.svg
```

## Next Steps

- Browse all 15 view types in [examples/toaster](examples/toaster) and [examples/blender](examples/blender)
- Read [sysmld-specification.md](sysmld-specification.md) for the complete format reference
- Use the prompt templates in [skills/](skills/) to generate models and intent files with AI assistance
- Run `pytest` to verify the full test suite passes
- See [CONTRIBUTING.md](CONTRIBUTING.md) to add a new view type or contribute a fix
