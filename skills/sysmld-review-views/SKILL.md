---
name: sysmld-review-views
description: Vision QA for SysMLD diagrams — no line through boxes, hop-overs only for line crossings, human-readable layout, and MSML-style meaning checks.
---

# Review SysMLD views

Tests passing is **not** sufficient. Open the SVG or PNG and look.

## Hard visual rule

Connections must **never** pass over boxes: no edge through a node, label, or part rectangle. Route around obstacles.

Hop-overs (small half-circle arcs) are **only** for line-on-line crossings. A hop that continues through a box is a defect.

IBD is the highest visual priority. If a Frame-style skip-rank mount clips a part, reorder ports, change ranks, or add an around-the-box channel. Do not “accept one hop-over” as cover for a clip.

## Human-readable bar

A systems engineer should see what the model is saying without decoding a mess.

- Orthogonal segments; labels beside the line (or clearly next to it).
- 1:1 pairs stay straight when boxes align.
- Fan-out/fan-in use channels or one shared bus near a single source — not a plate of noodles.
- Boundary ports line up with their targets.
- No leftover canvas larger than a small pad under the last message / last state.

## Meaning checks (MSML-style)

Ask what the figure **claims**, then check the model:

| Question | Fail if |
| --- | --- |
| Who is inside vs outside? | Extra item nodes on a context view; merged inbound/outbound lines |
| What does this transition hit? | Fault→Off that *looks* like it enters Standby |
| What is the parent of this requirement? | Display hanging off Assist Limit when it is a sibling |
| Which actor owns this use case? | Charger missing; include arrow backwards |
| Are the numbers the stakeholder cares about visible? | Lost 500 Wh / 60 km / 25 km/h / 50 ms (e-bike) or the project’s equivalents |
| Is the story still there? | IBD mounts, action cycle, allocation 1:1, verification 1:1 quietly dropped |

When reviewing `examples/e-bike/`, **do not rename ElectricBike ids.**

## How to inspect

1. Compose and render the intent you changed.
2. Read the SVG paths against part rectangles (or render PNG). Geometry beats a first glance.
3. For IBD, assert no interior hits (see `tests/test_interconnection_view.py` `_route_box_hits`).
4. Fail the view if any connector crosses a box. Fix routing or intent; do not ship the clip.

## Verdicts

Use **pass** / **still rough** / **fail**. Fail = box clip or wrong meaning. Still rough = readable but crowded (long rails, tight pairs). Pass = meaning is clear and the hard rule holds.
