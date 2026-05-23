# Skill: Generate Interconnection View Intent from SysML Model

Use this prompt to generate an `InterconnectionView` intent JSON for `sysmld compose` from an existing `.sysml` model.

---

## Prompt

You are generating a SysMLD interconnection view intent file. Given the SysML v2 model below, produce a valid JSON intent file for `sysmld compose` that shows the internal structure of the top-level system.

**SysML v2 model:**
```sysml
[SYSML MODEL]
```

**Rules:**
1. Set `"kind": "InterconnectionView"`.
2. Set `"subject"` to the alias key for the top-level part usage (lowercase).
3. In `"aliases"`, map short keys to fully qualified SysML names using `PackageName::PartDefName::memberName` syntax.
4. In `"nodes"`, list each sub-part as a node with `"label"` and `"style"`. Use `"part.mechanical"`, `"part.electrical"`, `"part.control"`, `"part.thermal"`, or `"part.structure"` based on the part's role.
5. In `"edges"`, list each connection with `"from"`, `"to"`, and `"label"` (the connection name or signal type).
6. Set `"direction": "left-right"` for linear signal/data flows; use `"bottom-up"` for structural hierarchies where a foundation element supports others above it.
7. Use `"boundary_inputs"` for external connections from outside the system boundary.
8. Keep `"aliases"` complete — every `model_ref` used in nodes, edges, and boundary_inputs must have an alias entry.

**Diagram authoring rules (apply these to produce clean output):**
- All connections must be orthogonal (purely horizontal or vertical segments).
- Route connections through rank channels with 20+ px per connection.
- Place boundary ports aligned with their internal target nodes (same x for top/bottom connections, same y for left/right).
- All ports on the same face should have evenly spaced offsets: 0.5 for one port, 0.33/0.67 for two, 0.25/0.5/0.75 for three.

**Output format:** Return only the JSON, no explanations.

---

## Example Output

```json
{
  "diagram": "toaster-icn",
  "kind": "InterconnectionView",
  "name": "Toaster Internal Structure",
  "subject": "toaster",
  "model_files": ["toaster.sysml"],
  "direction": "left-right",
  "aliases": {
    "toaster": "Toaster::Toaster",
    "lever": "Toaster::Toaster::lever",
    "heatingElement": "Toaster::Toaster::heatingElement",
    "leverToHeater": "Toaster::Toaster::leverToHeater"
  },
  "nodes": {
    "lever":          { "label": "Lever",           "style": "part.mechanical" },
    "heatingElement": { "label": "Heating Element", "style": "part.thermal" }
  },
  "edges": [
    { "from": "lever", "to": "heatingElement", "label": "control", "model_ref": "leverToHeater" }
  ],
  "boundary_inputs": [
    { "to": "lever", "label": "user input" }
  ],
  "styles": {
    "boundary.system":  { "fill": "#FFFFFF", "stroke": "#333333", "stroke_width": 2, "corner_radius": 12 },
    "part.mechanical":  { "fill": "#E8F5E9", "stroke": "#2E7D32", "stroke_width": 2, "corner_radius": 10 },
    "part.thermal":     { "fill": "#FFF3E0", "stroke": "#EF6C00", "stroke_width": 2, "corner_radius": 10 },
    "connector.default":{ "stroke": "#334155", "stroke_width": 2, "corner_radius": 8 }
  }
}
```
