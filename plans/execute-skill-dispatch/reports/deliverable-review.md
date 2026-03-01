# Deliverable Review: execute-skill-dispatch (Re-review)

**Date:** 2026-03-01
**Methodology:** agents/decisions/deliverable-review.md
**Prior review:** 2026-03-01 (1 Major, 3 Minor)

## Inventory

| Type | File | + | - |
|------|------|---|---|
| Code | src/claudeutils/planstate/inference.py | +8 | -2 |
| Test | tests/test_planstate_inference.py | +23 | -30 |
| Test | tests/test_userpromptsubmit_execute.py | +161 | -0 |
| Agentic prose | agent-core/fragments/execute-rule.md | +2 | -2 |
| Code | agent-core/hooks/userpromptsubmit-shortcuts.py | +91 | -0 |
| Agentic prose | agent-core/skills/handoff/SKILL.md | +1 | -0 |
| Agentic prose | agent-core/skills/prioritize/SKILL.md | +1 | -1 |

**Total:** 7 files, +287/-35, net +252 lines.

**Conformance baseline:** `plans/execute-skill-dispatch/requirements.md` (no design.md — Moderate classification routed to /runbook).

## Prior Finding Resolution

| # | Severity | Finding | Status |
|---|----------|---------|--------|
| 1 | Major | Private API import (`_determine_status`, `_derive_next_action`) | **Fixed** — `_try_planstate_command` now imports `infer_state()` public API, reads `state.next_action` |
| 2 | Minor | `infer_state` docstring omits `lifecycle` in priority chain | **Fixed** — docstring at inference.py:150 now reads `lifecycle > ready > planned > designed > outlined > requirements` |
| 3 | Minor | No `r` mode backward-compat test | **Fixed** — `test_r_does_not_inject` added (test_userpromptsubmit_execute.py:147-161) |
| 4 | Minor | Fragile `ctx.split("Invoke:")[-1]` assertion | **Fixed** — replaced with `assert "Invoke: /commit" not in ctx` (line 51) |

All four prior findings resolved.

## Gap Analysis

| Requirement | Status | Reference |
|---|---|---|
| FR-1: Execute mode invokes task command as skill call | Covered | execute-rule.md MODE 2 — "Invoke the task's backtick command — via Skill tool for `/skill` commands, or Bash for script commands. Do not reinterpret the command or implement the work directly." |
| FR-2: UPS hook injects task command for execute mode | Covered | userpromptsubmit-shortcuts.py:874-958 — `_extract_execute_command()` parses session.md, injects `Invoke: <cmd>` into additionalContext |
| FR-3: Execute-rule prose aligns with structural enforcement | Covered | execute-rule.md MODE 2 prose matches hook injection semantics |
| C-1: Hook performance budget | Covered | Lazy import inside try/except in `_try_planstate_command` (line 880) |
| C-2: Structural fix, not prose strengthening | Covered | FR-2 hook is structural enforcement; FR-3 prose reinforces |
| C-3: Backward compatibility | Covered | `test_xc_does_not_inject` + `test_r_does_not_inject` confirm non-x modes unaffected; gate at line 991 (`first_command == "x"`) |

**Missing deliverables:** None.

**Unspecified deliverables:**
- `tests/test_planstate_inference.py` changes — justified (companion fix-planstate-detector plan)
- Enumeration site updates (handoff/SKILL.md, prioritize/SKILL.md) — justified (outlined status propagation)

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

None.

## Cross-Cutting Checks

- **API contract alignment:** `_try_planstate_command` → `infer_state()` → `PlanState.next_action` — consistent chain through public API
- **Path consistency:** Plan name extraction (`_extract_plan_name`) constructs `plans/{name}` matching `_NEXT_ACTION_TEMPLATES` format
- **Naming convention:** `outlined` status consistent across all 5 enumeration sites (inference.py, execute-rule.md, handoff/SKILL.md, prioritize/SKILL.md, test parametrize)
- **Priority chain consistency:** `_determine_status` docstring, `infer_state` docstring, and execute-rule.md STATUS format all agree on ordering

## Summary

- **Critical:** 0
- **Major:** 0
- **Minor:** 0

All four prior findings resolved. No new findings.
