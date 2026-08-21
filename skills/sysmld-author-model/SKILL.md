---
name: sysmld-author-model
description: Write or update SysML v2 textual models in the SysMLD style. Use when adding packages, parts, ports, connections, states, or requirements to a .sysml file.
---

# Author a SysML v2 textual model

SysMLD reads a **minimal** textual subset. Keep models concise: structure and behavior, not implementation.

## Shape

```sysml
package SystemName {
    part def SystemName {
        part child : ChildType;
        port boundaryPort : PortType;
        connection connName connect portA to portB;
    }

    part def ChildType { port p : PortType; }
    port def PortType;

    state def SystemControl {
        entry; then idle;
        state idle;
        state running;
        transition start first idle accept startCmd then running;
        transition stop  first running accept stopCmd then idle;
    }

    requirement safetyRequirement { doc /* Shall not harm the operator. */ }
}
```

## Rules

1. One top-level `package` (PascalCase). Top-level system is `part def SystemName { ... }`.
2. Usages: `part name : Type;` inside the system. Types: `part def Type;` at package level.
3. Ports: `port def PortType;` then `port name : PortType;` on the owner.
4. Connections: `connection name connect a to b;` — names become `model_ref` targets.
5. State machines: `state def Name { entry; then firstState; state s; transition t first a accept event then b; }`.
6. Requirements: `requirement name { doc /* text */ }`. Put real numbers in the doc when they matter (range, latency, energy).
7. Optional: `item def`, `flow`, `interface def`, `use case Name { include other; }`, `allocation`, analysis/verification cases — only if a view will show them.
8. `use case` / `state` / `action` / `interaction` bodies that open `{` must nest correctly; the indexer treats those as scopes.

## Working in this repo

- **ElectricBike ids are frozen.** Do not rename that package, its parts, or `examples/e-bike/` stems.
- Do not invent a second name for an existing element so a diagram “looks nicer.”
- New systems get a **new** package name. Copy [templates/new-system/starter.sysml](../../templates/new-system/starter.sysml).

## After edits

Every intent `aliases` map and `model_ref` must still resolve. Run `sysmld validate <file>.sysmld --strict` from the directory that holds the `.sysml`.

Longer one-shot prompt: [new-model.md](../new-model.md).
