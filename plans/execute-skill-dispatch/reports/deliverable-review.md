# Deliverable Review: execute-skill-dispatch

**Date:** 2026-03-01
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | + | - |
|------|------|---|---|
| Code | src/claudeutils/planstate/inference.py | +8 | -2 |
| Test | tests/test_planstate_inference.py | +23 | -30 |
| Test | tests/test_userpromptsubmit_execute.py | +145 | -0 |
| Agentic prose | agent-core/fragments/execute-rule.md | +2 | -2 |
| Code | agent-core/hooks/userpromptsubmit-shortcuts.py | +96 | -0 |
| Agentic prose | agent-core/skills/handoff/SKILL.md | +1 | -0 |
| Agentic prose | agent-core/skills/prioritize/SKILL.md | +1 | -1 |

**Total:** 7 files, +276/-35, net +241 lines.

**Conformance baseline:** `plans/execute-skill-dispatch/requirements.md` (no design.md — Moderate classification routed to /runbook).

## Gap Analysis

| Requirement | Status | Reference |
|---|---|---|
| FR-1: Execute mode invokes task command as skill call | Covered | execute-rule.md MODE 2 — "Invoke the task's backtick command — via Skill tool for `/skill` commands, or Bash for script commands. Do not reinterpret the command or implement the work directly." |
| FR-2: UPS hook injects task command for execute mode | Covered | userpromptsubmit-shortcuts.py:874-999 — `_extract_execute_command()` parses session.md, injects `Invoke: <cmd>` into additionalContext |
| FR-3: Execute-rule prose aligns with structural enforcement | Covered | execute-rule.md MODE 2 prose matches hook injection semantics |
| C-1: Hook performance budget | Covered | Lazy import inside try/except in `_try_planstate_command` |
| C-2: Structural fix, not prose strengthening | Covered | FR-2 hook is structural enforcement; FR-3 prose reinforces |
| C-3: Backward compatibility | Covered | `test_xc_does_not_inject` confirms non-x modes unaffected; regex patterns exclude completed/blocked/failed/canceled tasks |

**Missing deliverables:** None.

**Unspecified deliverables:**
- `tests/test_planstate_inference.py` changes — justified (companion fix-planstate-detector plan)
- `agents/learnings.md` additions — justified (process learnings from execution)

## Critical Findings

None.

## Major Findings

1. **Private API import across module boundary** — `_try_planstate_command` (userpromptsubmit-shortcuts.py:880-882) imports `_determine_status` and `_derive_next_action` from `claudeutils.planstate.inference`. These are underscore-prefixed private functions, creating cross-package coupling between `agent-core/hooks/` and `src/claudeutils/planstate/`.

   - **Axis:** modularity
   - **Impact:** If inference module refactors private functions (rename, merge, change signature), the hook silently degrades to session.md command via try/except. Silent degradation of planstate override is hard to detect.
   - **Fix:** Use public API `infer_state(plan_dir)` and read `.next_action` from the returned `PlanState`. The `_collect_artifacts()` overhead is a few `Path.exists()` calls — negligible vs C-1 budget.

## Minor Findings

**Docstring accuracy:**
- `infer_state` docstring (inference.py:150) says "Status priority: ready > planned > designed > outlined > requirements" — omits `lifecycle` which is highest priority. This line was touched in the diff (added `outlined`). The companion function `_determine_status` docstring (line 68) correctly includes `lifecycle`.

**Test coverage:**
- No backward compatibility test for `r` (resume) mode. C-3 explicitly names `#resume` as unchanged. Only `xc` is tested in `TestExecuteBackwardCompat`. Implementation is correct (gates on `first_command == "x"` at line 996), but `r` is the mode most explicitly called out in C-3.
- `test_x_skips_non_eligible_tasks` assertion at line 51 uses `ctx.split("Invoke:")[-1]` — fragile if injection format changes. Direct `assert "Invoke: /commit" not in ctx` would be clearer.

## Summary

- **Critical:** 0
- **Major:** 1
- **Minor:** 3

All FRs and constraints are satisfied. The Major finding is a modularity concern (private API coupling) that doesn't affect correctness but creates maintenance risk. Minor findings are docstring accuracy and test coverage gaps.
