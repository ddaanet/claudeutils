# Outline Review: hook-batch

**Artifact**: plans/hook-batch/outline.md
**Date**: 2026-02-20T00:00:00
**Mode**: review + fix-all

## Summary

The outline incorporates all design discussion additions (b: = brainstorm, additive directives, graduated r expansion, hooks.json as source of truth, dual delivery for session health). Two major issues were identified and fixed: the outline referenced userpromptsubmit-plan.md for execution order without noting that the plan's execution order is superseded by D-7, and the plan's b: item still says "needs user input" despite D-5 resolving it. Two minor issues were also fixed: missing python3/python exclusion note for Phase 2, and missing JSON parsing constraint for Phase 3's Bash script.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| UserPromptSubmit: line-based shortcut matching | Phase 1, item 1 | Complete | — |
| UserPromptSubmit: r expansion (graduated lookup) | Phase 1, item 2 | Complete | conversation → session.md → git status |
| UserPromptSubmit: xc/hc continuation-chain style | Phase 1, item 3 | Complete | `[execute, commit]` format |
| UserPromptSubmit: additive directives (D-7) | Phase 1, item 4; D-7; Plan overrides | Complete | Plan override note added (FIXED) |
| UserPromptSubmit: p: dual output | Phase 1, item 5 | Complete | — |
| UserPromptSubmit: b: = brainstorm (D-5) | Phase 1, item 6; D-5; Plan overrides | Complete | Plan override note added (FIXED) |
| UserPromptSubmit: q: + learn: directives | Phase 1, item 7 | Complete | learn: already long-form, no alias needed |
| UserPromptSubmit: skill-editing guard | Phase 1, item 8 | Complete | — |
| UserPromptSubmit: CCG integration | Phase 1, item 9 | Complete | — |
| PreToolUse: recipe-redirect hook | Phase 2 | Complete | python3/python exclusion note added (FIXED) |
| PostToolUse: auto-format hook | Phase 3 | Complete | JSON parsing constraint added (FIXED) |
| SessionStart: 3 health checks | Phase 4 | Complete | dual delivery, flag-file gating, systemMessage output |
| learning-ages.py: --summary flag | Phase 4 prerequisite | Complete | — |
| hooks.json: config source of truth (D-8) | Phase 5; D-8; Approach | Complete | — |
| sync-to-parent: hook config merge | Phase 5 | Complete | sync-hooks-config.py helper |
| Restart verification | Scope IN; Phase 5 | Complete | — |
| Remove python3/python from recipe-redirect patterns | Phase 2 | Complete | Exclusion noted explicitly (FIXED) |

**Traceability Assessment**: All requirements covered.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Stale execution order in userpromptsubmit-plan.md not flagged**
   - Location: Phase 1, Implementation details paragraph
   - Problem: The outline references `plans/hook-batch/userpromptsubmit-plan.md` for "pattern specs, expansion strings, and execution order for items 4-9." But the plan's execution order (Step 2) says "Tier 2: Directive scan (first directive match wins, returns)" — directly contradicting D-7 (additive directives). An implementer following the plan's execution order would implement first-match-wins, breaking the additive behavior.
   - Fix: Added "Plan overrides" block noting that the plan's Step 2 execution order is superseded by D-7, and that additive scanning with no early return is the correct behavior.
   - **Status**: FIXED

2. **userpromptsubmit-plan.md item 5 still says "Needs user input"**
   - Location: Phase 1, Implementation details paragraph (via plan reference)
   - Problem: The plan's item 5 (b: directive) says "Needs user input before implementing" — but D-5 resolves this. An implementer reading the plan would stop at item 5 awaiting input that was already provided in design discussion.
   - Fix: Added to "Plan overrides" block: item 5 is resolved by D-5, b: = brainstorm, diverge without converging.
   - **Status**: FIXED

### Minor Issues

1. **Phase 2 silent on python3/python exclusion**
   - Location: Phase 2, Pattern matches list
   - Problem: settings.json denies `Bash(python:*)` and `Bash(python3:*)`. The brief specifies "Remove python3/python from recipe-redirect patterns." The outline correctly omits them from the pattern list, but provides no explanation — an implementer might add them as obvious candidates.
   - Fix: Added note explaining that python3/python are denied in denylist but not redirect patterns (no project recipe equivalent).
   - **Status**: FIXED

2. **Phase 3 Bash script JSON parsing constraint missing**
   - Location: Phase 3, Logic step 1
   - Problem: Phase 3 is a `.sh` script that must extract `file_path` from stdin JSON. Raw Bash string manipulation on JSON is fragile and error-prone. No constraint is stated.
   - Fix: Added inline note to Logic step 1: "Use `python3 -c` or `jq` for JSON parsing — do not use raw Bash string manipulation on JSON."
   - **Status**: FIXED

## Fixes Applied

- Phase 1 — Replaced "Implementation details" note with two-part note: plan reference (pattern specs + expansion strings only, not execution order) + "Plan overrides" block listing D-7 and D-5 supersessions
- Phase 2 — Added note clarifying python3/python exclusion from redirect patterns
- Phase 3, Logic step 1 — Added JSON parsing constraint (python3 -c or jq)

## Positive Observations

- All design discussion additions are correctly incorporated: b: = brainstorm (D-5), additive directives (D-7), graduated r expansion, xc/hc continuation-chain format, hooks.json as source of truth (D-8), dual delivery for session health with flag-file gating.
- D-6 (PreToolUse is informative, not blocking) is correctly motivated — denylist is enforcement, hook is UX.
- #10373 degraded-mode rationale is clear and the Stop fallback design is sound.
- Phase type tagging (TDD vs General) is consistent and appropriate.
- Files Affected table maps cleanly to phases with no gaps.
- learn: already-long-form treatment (no alias needed) correctly reflected in item 7.

## Recommendations

- Phase 3 (.sh with JSON parsing): even with the python3 -c constraint, consider whether a .py script would be simpler. D-2 made Bash the choice for "simple command orchestration" — but JSON parsing in a .sh file complicates that. Low priority since the constraint now guards against the failure mode.
- The prior review's outline-review.md (Q-1 recommendation for user input on b:) is now resolved by D-5. No action needed.

---

**Ready for user presentation**: Yes
