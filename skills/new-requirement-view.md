# Skill: Generate Requirement View Intent from SysML Model

Use this prompt to generate a `RequirementView` intent JSON for `sysmld req` from an existing `.sysml` model.

---

## Prompt

You are generating a SysMLD requirement view intent file. Given the SysML v2 model below, produce a valid JSON intent file for `sysmld req` that shows the requirement hierarchy.

**SysML v2 model:**
```sysml
[SYSML MODEL]
```

**Rules:**
1. Set `"kind": "RequirementView"`.
2. Set `"direction": "top-down"` — parent requirements at top, derived requirements below.
3. In `"nodes"`, list each `requirement` from the model. Use the requirement name as the node id. Set `"label"` to a short human-readable name (2–4 words). Use `"symbol": "requirement"` (the default).
4. In `"edges"`, add `"derive"` edges from a parent requirement to its derived children, `"refine"` edges from implementation elements to requirements, and `"trace"` edges for informal traceability.
5. Use `"rank"` on each node if you want precise control over the hierarchy level (0 = top level, 1 = derived, 2 = more specific).
6. In `"aliases"`, map each requirement node id to its qualified SysML name.
7. Keep the view focused — show at most 8–10 requirements. Use `GeneralView` for larger overviews.

**Note:** This view is a pragmatic overview diagram. Relationship labels (`derive`, `refine`, `trace`) are SysMLD edge labels, not SysML v2 stereotype syntax. They correctly reference SysML v2 model elements.

**Output format:** Return only the JSON, no explanations.

---

## Example Output

```json
{
  "diagram": "toaster-req",
  "kind": "RequirementView",
  "name": "Toaster Requirements",
  "subject": "toaster",
  "model_files": ["toaster.sysml"],
  "direction": "top-down",
  "aliases": {
    "toaster": "Toaster::Toaster",
    "safetyReq":   "Toaster::toastSafetyRequirement",
    "electricalReq":"Toaster::electricalSafetyRequirement",
    "browningReq": "Toaster::browningRequirement",
    "timingReq":   "Toaster::timingRequirement"
  },
  "nodes": {
    "safetyReq":    { "label": "Toast Safety",     "model_ref": "safetyReq",    "rank": 0 },
    "electricalReq":{ "label": "Electrical Safety","model_ref": "electricalReq","rank": 1 },
    "browningReq":  { "label": "Browning Quality", "model_ref": "browningReq",  "rank": 1 },
    "timingReq":    { "label": "Toast Timing",     "model_ref": "timingReq",    "rank": 1 }
  },
  "edges": [
    { "from": "safetyReq", "to": "electricalReq", "label": "derive" },
    { "from": "safetyReq", "to": "browningReq",   "label": "derive" },
    { "from": "safetyReq", "to": "timingReq",     "label": "derive" }
  ]
}
```
