# SysMLD v0.1 Specification

**Status:** v0.1 implementation specification  
**Schema authority:** `schemas/sysmld.schema.json` is authoritative. This Markdown file explains intent and examples. If this document and the schema conflict, update this document to match the schema unless the schema is intentionally revised.

## 1. Purpose

SysMLD is a JSON diagram/view format for SysML v2 models.

- `.sysml` files contain model semantics.
- `.sysmld` files contain diagram layout and rendering instructions.
- SVG outputs are generated artifacts. PNG output is outside the v0.1 scope.

SysMLD view-kind names and abbreviations are SysMLD-defined. They are not OMG standard diagram codes.

## 2. Document Shape

```json
{
  "$schema": "../../schemas/sysmld.schema.json",
  "version": "0.1",
  "mode": "model_based",
  "model_files": ["toaster.sysml"],
  "aliases": {
    "toaster": "Toaster",
    "lever": "Toaster::lever"
  },
  "diagram": {
    "id": "toaster-icn",
    "kind": "InterconnectionView",
    "name": "Toaster Interconnection",
    "subject": "toaster",
    "canvas": {
      "width": 1000,
      "height": 700,
      "background": "#FFFFFF"
    },
    "frame": {
      "visible": true
    },
    "elements": [],
    "connections": [],
    "annotations": [],
    "styles": {}
  }
}
```

Required top-level fields:

- `version`
- `mode`
- `diagram`

Optional top-level fields:

- `$schema`
- `model_files`
- `aliases`

`theme_files` is optional and omitted when unused.

## 3. Modes

`mode` must be one of:

| Mode | Header code | Rules |
| --- | --- | --- |
| `model_based` | `mb` | `model_files` must be non-empty. Strict validation resolves model references. |
| `sketch` | `sk` | `model_files` must be absent or empty. Model-reference validation is skipped. |

Sketch output must visibly show `.sk` in the rendered frame header.

## 4. View Kinds

The table below maps familiar SysML v1 diagram names to SysML v2 / SysMLD view kinds for reference. SysMLD view kind names are SysMLD-defined and do not replicate OMG standard codes. The v1 column is provided for orientation; SysMLD views are SysML v2 concepts and should not be interpreted as v1 diagram equivalents.

| SysML v1 Diagram | v1 Code | SysMLD View Kind | SysMLD Code | v0.1 Status |
| --- | --- | --- | --- | --- |
| Block Definition Diagram | `bdd` | `DefinitionView` | `def` | tree composer implemented |
| Internal Block Diagram | `ibd` | `InterconnectionView` | `icn` | implemented first |
| Package Diagram | `pkg` | `PackageView` | `pkg` | deterministic composer implemented |
| Parametric Diagram | `par` | `ConstraintView` | `cst` | deterministic composer implemented |
| Requirement Diagram | `req` | `RequirementView` | `req` | requirement composer implemented |
| Activity Diagram | `act` | `ActionView` | `act` | action composer implemented |
| State Machine Diagram | `stm` | `StateView` | `stv` | state composer implemented |
| Sequence Diagram | `sd` | `InteractionView` | `int` | sequence composer implemented |
| Use Case Diagram | `uc` | `UseCaseView` | `uc` | deterministic composer implemented |

Additional view kinds:

| SysMLD View Kind | Code |
| --- | --- |
| `AllocationView` | `alloc` |
| `FlowView` | `flow` |
| `AnalysisCaseView` | `acase` |
| `VerificationCaseView` | `vcase` |
| `InterfaceView` | `intf` |
| `GeneralView` | `gen` |

The additional view kinds above are supported by deterministic composers. Some commands share a generic layered graph composer; others use a view-specific composer when the notation needs it.

## 4.1 Composer Commands

The command-line tool is named `sysmld`.

| Command | Output |
| --- | --- |
| `compose` | InterconnectionView from an interconnection intent file |
| `tree`, `bdd` | DefinitionView tree |
| `stm`, `state` | StateView |
| `package` | PackageView |
| `req` | RequirementView |
| `constraint` | ConstraintView |
| `action` | ActionView |
| `interaction` | InteractionView |
| `usecase` | UseCaseView |
| `allocation` | AllocationView |
| `flow` | FlowView |
| `analysis` | AnalysisCaseView |
| `verification` | VerificationCaseView |
| `interface` | InterfaceView |
| `general` | GeneralView |
| `render` | SVG rendering from `.sysmld` |
| `validate` | Schema-shape and optional strict model validation |

Interconnection composition can also emit optional `.graph.json` and `.graph.svg` topology sidecars with `compose --graph`.

## 5. Frame Header

The frame header follows the SysML v2 graphical notation for part usages
(`FeatureSpecializationPart → Typings → DEFINED_BY = ':'`), which uses
`usageName : TypeName` for the subject bracket.

```text
[<view-code>.<mode-code>] <diagram name> [<subject-usage> : <subject-type>]
```

- `subject-usage` — the role/instance name of the subject element (the alias key in the `.sysmld` file, e.g. `toaster`).
- `subject-type` — the definition/type name of the subject element (the last segment of the resolved qualified name, e.g. `Toaster`).

When only the type is known (subject is not an alias), the colon and usage name are omitted:

```text
[<view-code>.<mode-code>] <diagram name> [<subject-type>]
```

Examples:

```text
[icn.mb] Toaster Interconnection [toaster : Toaster]
[icn.sk] Toaster Sketch
[int.mb] User Interaction [toaster : Toaster]
```

## 6. References And Aliases

Any `model_ref` or `subject` value is resolved as follows:

1. If the value is a key in `aliases`, use the alias target.
2. Otherwise, treat the value as a qualified SysML name.

Alias targets should be qualified SysML names. Aliases are local to one `.sysmld` file.

## 7. Elements

Visible top-level elements require `layout.x`, `layout.y`, `layout.width`, and `layout.height`.

```json
{
  "id": "control-system",
  "model_ref": "controlSystem",
  "symbol": "part_usage",
  "layout": {
    "x": 320,
    "y": 180,
    "width": 160,
    "height": 90,
    "z": 10
  },
  "compartments": {
    "attributes": false,
    "ports": true,
    "actions": false
  },
  "style": "part.control"
}
```

`label` is a view label. It may be shorter than the model's fully qualified name. For part usages, use `role: Type` only when the role and type add distinct information. If the displayed role and type would be effectively the same, prefer the simpler label.

For `InterconnectionView`, default compartments are:

| Compartment | Default |
| --- | --- |
| `attributes` | false |
| `ports` | true |
| `actions` | false |

Ports are boundary-mounted elements:

```json
{
  "id": "control-in",
  "model_ref": "controlInput",
  "symbol": "port",
  "owner": "control-system",
  "placement": {
    "side": "left",
    "offset": 0.5
  }
}
```

`side` is `top`, `right`, `bottom`, or `left`. `offset` is from `0.0` to `1.0`.

## 8. Connections

Connections are semantic, model-backed lines.

```json
{
  "id": "lever-to-control",
  "model_ref": "leverToControl",
  "source": {
    "element": "lever-out",
    "anchor": {
      "side": "right",
      "offset": 0.5
    }
  },
  "target": {
    "element": "control-in",
    "anchor": {
      "side": "left",
      "offset": 0.5
    }
  },
  "route": {
    "kind": "orthogonal",
    "waypoints": [
      { "x": 240, "y": 220 },
      { "x": 320, "y": 220 }
    ]
  },
  "labels": [
    {
      "text": "control",
      "position": {
        "segment": 0,
        "offset": 0.5,
        "dx": 0,
        "dy": -12
      }
    }
  ],
  "style": "connector.signal"
}
```

Rules:

- endpoints reference visible diagram element IDs.
- endpoint anchors use side/offset in v0.1.
- `waypoints` exclude endpoints.
- `route.kind` is `orthogonal` or `polyline`.
- labels use segment-relative placement.
- non-semantic lines belong in `annotations`, not `connections`.

For BDD-style `DefinitionView` composition branches, the displayed relationship is a contained `part` usage owned by a definition. The child box references the child part definition, while the connection `model_ref` should reference the owning part usage, for example `Toaster::Toaster::lever`. Render composition with a filled diamond at the owner end and multiplicity near the part end.

## 9. Annotations

`annotations` are visual-only objects with no `model_ref`. They are for callouts, grouping lines, notes, and other marks that do not represent SysML model semantics.

v0.1 reserves the field and validates it as an array. Rendering support may start minimal.

## 10. Styles

Style resolution order:

1. specification default style
2. imported theme style
3. diagram-local named style
4. element or connection inline override

Common style properties include `fill`, `stroke`, `stroke_width`, `corner_radius`, `label_offset`, `marker_start`, and `marker_end`. `corner_radius` applies to rendered rectangular symbols such as boundaries and part usages, and to routed connection corners. `label_offset` controls the default distance between connection labels and their line segment when a label position does not specify `dx` or `dy`. `marker_start: "composition"` renders a filled composition diamond at the source end of a connection.

## 11. Validation

Validation modes:

| Mode | Purpose |
| --- | --- |
| `schema` | JSON shape and primitive constraints |
| `strict` | aliases, model references, endpoints, routes, renderability |
| `lint` | quality warnings |

Strict-invalid diagrams do not render unless `--force` is provided.

## 12. Rendering

Renderers must build one resolved scene graph and produce SVG and PNG from that same scene graph. PNG must not be produced by reading the SVG file as an intermediate in v0.1.

## 13. Diagram Authoring Rules (for humans and AI)

These rules apply when writing or generating `.sysmld` files. They prevent the most common visual defects.

### 13.1 No diagonal lines

A connection is diagonal when its source anchor point and target anchor point differ in both x and y and no waypoint aligns them on a shared axis first.

**Rule:** every connection must be fully orthogonal. Each segment must be either purely horizontal or purely vertical.

**How to achieve this:** ensure that at least one of the following is true before writing waypoints:
- The source anchor x equals the target anchor x (use a vertical connection with no waypoints).
- The source anchor y equals the target anchor y (use a horizontal connection with no waypoints).
- At least one waypoint is placed such that the first segment travels to the same x or y as the next point, and so on through the route.

**Anchor point formula** (used to check alignment before writing waypoints):

For a port at `placement.side` / `placement.offset` on an owner element at `(ox, oy, ow, oh)`:

| Port side | Port centre | Outward anchor point |
| --- | --- | --- |
| `left`   | `(ox, oy + oh * offset)`       | `(ox - 6, oy + oh * offset)` |
| `right`  | `(ox + ow, oy + oh * offset)`  | `(ox + ow + 6, oy + oh * offset)` |
| `top`    | `(ox + ow * offset, oy)`       | `(ox + ow * offset, oy - 6)` |
| `bottom` | `(ox + ow * offset, oy + oh)`  | `(ox + ow * offset, oy + oh + 6)` |

The port size is 12 px; the outward anchor is 6 px beyond the owner edge.

For a boundary port, the anchor exits inward (toward the diagram interior), so use the opposite face:
- boundary left port → anchor exits right: `(ox + 6, oy + oh * offset)`
- boundary right port → anchor exits left: `(ox + ow - 6, oy + oh * offset)`
- boundary top port → anchor exits bottom: `(ox + ow * offset, oy + 6)`
- boundary bottom port → anchor exits top: `(ox + ow * offset, oy + oh - 6)`

**Minimal waypoint rule:** if anchor points share neither x nor y, one waypoint is required. Place it at `(source_anchor_x, target_anchor_y)` or `(target_anchor_x, source_anchor_y)` — pick the one that keeps the route away from other elements.

### 13.2 No lines through element boxes

A connection segment that passes through an element box looks broken and is unreadable.

**Rule:** every waypoint and every computed segment must clear all element bounding boxes by at least 10 px.

**How to achieve this:**
- Route connections around elements, not through them.
- When a direct path crosses a box, add a waypoint on each side of the box to detour around it.
- Choose the shorter detour (above vs. below, or left vs. right).
- If two elements are in different rank columns, route through the open channel between columns, not through either element.

### 13.3 Minimize line crossings

Crossing connections are harder to trace. They cannot always be avoided, but they should be minimized.

**Rules:**
- Before writing connections, mentally order them by source position (top-to-bottom or left-to-right) and assign route tracks in the same order. Connections whose sources are higher should use tracks that are further from the target column, so the diagonal "fan" unfolds without crossings.
- Connections from the same element on the same side should leave at different y offsets (landscape) or x offsets (portrait) to separate their exit segments.
- If two connections must cross, cross them at a right angle and keep the crossing point away from labels.

### 13.4 Symmetry and visual balance

Symmetry is the single largest contributor to diagram readability. Apply it wherever the model structure permits.

**Same height for similar elements.** Elements of the same kind in the same visual row or column should share a height. Set a common height (e.g. 70 px for leaf parts, 90 px for coupled pairs, 60 px for structural bars) and apply it uniformly. Only break the rule when an element's label is substantially longer than its peers and wrapping would make it unreadable.

**Vertical alignment.** Elements that share a functional level or rank should share the same `layout.y`. Even a 10 px offset between two elements in the same row looks like a mistake. Pick one y value and apply it to the whole row.

**Centre connections on their face.** When a single port occupies a face of an element, its `placement.offset` must be `0.5`. Offset 0.5 means the connection enters or exits the exact centre of that face. Only deviate from 0.5 when two or more ports share the same face, in which case distribute them symmetrically (e.g. 0.33 / 0.67 for two ports, 0.25 / 0.5 / 0.75 for three).

**Align coupled elements on a shared axis.** When two elements have a direct connection (especially a tight mechanical or data coupling), stack them on the same x axis (landscape) or y axis (portrait) so the connection between them is a short straight line with no bends. Set their widths or x positions so their centre lines are the same value.

**Boundary ports align with their internal targets.** A boundary port that connects to a single internal element should be positioned so the connection line is straight with no waypoints. Compute the target port's absolute x (landscape: top/bottom connections) or y (landscape: left/right connections) and set the boundary port's offset to match exactly: `offset = (target_absolute_coord - boundary_origin) / boundary_dimension`.

### 13.5 Equal spacing and margin prompt

Before finalising any layout, run through this checklist:

**Step 1 — fix element sizes first.**
Set a common `height` for all elements at the same functional level. Elements of equal importance should be visually equal. Set widths to the same value unless one element's label is meaningfully longer.

**Step 2 — fix row y values.**
All elements in the same functional row must share the same `layout.y`. Compute the value once and apply it to every element in that row. Do not estimate per-element — set them all to the identical integer.

**Step 3 — compute gaps algebraically, not visually.**
If two gaps should be equal (e.g. the gap between a stacked pair and the gap between that pair and a structural bar), solve for the gap value explicitly:

```
gap = (total_available_height - sum_of_element_heights) / number_of_gaps
```

then set every y using that gap:
```
element_1_y = boundary_y + top_margin
element_2_y = element_1_y + element_1_h + gap
element_3_y = element_2_y + element_2_h + gap
```

**Step 4 — balance margins.**
If no reason to prefer more space at the top or bottom, set `top_margin = bottom_margin`. Compute:

```
margin = (boundary_height - total_element_height - total_gap_height) / 2
```

**Step 5 — verify with arithmetic before writing.**
For each gap, subtract bottom-of-upper from top-of-lower and confirm the values are equal. For each row, confirm all y values are identical. Never guess or nudge.

### 13.6 Use the `sysmld graph` command for initial placement

When generating a new diagram from an intent file, run `sysmld graph intent.json` before committing to final coordinates. This produces a crossing-minimized topology SVG (`.graph.svg`) and a position JSON (`.graph.json`) with suggested `cx`/`cy` centre points.

Translate centre points to element layout coordinates: `layout.x = cx - width/2`, `layout.y = cy - height/2`.

Then adjust positions to separate coupled elements, align vertically-connected ports, and leave routing channels wide enough for the number of connections passing through them (allow at least 20 px per connection in a channel).

For full auto-layout from a compact intent file, use the deterministic composers (`sysmld compose`, `sysmld stm`, `sysmld bdd`, etc.) which compute all coordinates, port placements, and connection waypoints automatically.
