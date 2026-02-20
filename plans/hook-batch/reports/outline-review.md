# Outline Review: hook-batch

**Artifact**: plans/hook-batch/outline.md
**Date**: 2026-02-20T00:00:00
**Mode**: review + fix-all

## Summary

The outline is well-structured and technically sound. All four hook events are clearly scoped with appropriate phase types and implementation detail. Five issues were found and fixed: a change-count mismatch propagated through the document, a technical inaccuracy in PostToolUse file_path extraction, a missing preservation note for existing settings.json matchers, an inconsistent b: directive scope treatment, and a stale count in the Approach summary.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| UserPromptSubmit 7 improvements (line-based, directive scope, p: dual output, q:, learn:, b:, skill-editing guard, ccg) | Phase 1 | Complete | Count corrected from 6→7; b: stub/skip treatment clarified |
| PreToolUse recipe-redirect hook | Phase 2 | Complete | Pattern matches, blocking behavior, additionalContext output |
| PostToolUse auto-format hook | Phase 3 | Complete | ruff + docformatter, file_path extraction corrected |
| SessionStart 3 health checks | Phase 4 | Complete | #10373 limitation documented, degraded-mode rationale present |
| learning-ages.py --summary flag | Phase 4 prereq + Files table | Complete | Prerequisite step called out explicitly |
| settings.json registration + symlink sync | Phase 5 | Complete | Preservation of existing matchers now explicit |
| b: directive deferred (semantics TBD) | D-5, Q-1, Phase 1, Scope OUT | Complete | Treatment consistent across all four locations post-fix |

**Traceability Assessment**: All requirements covered.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Change count mismatch throughout document**
   - Location: Approach paragraph (line 5), Phase 1 opening, Scope IN
   - Problem: Brief specifies 7 UserPromptSubmit changes. Outline said "Six changes" in Phase 1 heading and "6 improvements" in Scope IN. The userpromptsubmit-plan.md lists 7 numbered items — b: directive is item 5, deferred but counted. Count inconsistency would cause implementer to think only 6 items needed attention.
   - Fix: Updated Approach summary "6 changes" → "7 changes", Phase 1 "Six changes" → "Seven changes", Scope IN "6 improvements" → "7 improvements (b: stub or skip)". Added b: as item 5 in the numbered list with deferred note.
   - **Status**: FIXED

2. **Technical inaccuracy: PostToolUse file_path extraction from tool_result**
   - Location: Phase 3 Logic step 1
   - Problem: "Extract `file_path` from tool_input (Write) or tool_result" — Edit tool does not put file_path in tool_result. Both Write and Edit provide file_path in tool_input. Implementer following this would write incorrect extraction logic for Edit.
   - Fix: Corrected to "Extract `file_path` from tool_input (both Write and Edit provide `file_path` in tool_input)".
   - **Status**: FIXED

### Minor Issues

1. **Phase 5 doesn't note preservation of existing PreToolUse matchers**
   - Location: Phase 5 bullet list
   - Problem: settings.json has two existing PreToolUse Write|Edit hooks (pretooluse-block-tmp.sh, pretooluse-symlink-redirect.sh) and an existing PostToolUse Bash hook (submodule-safety.py). Phase 5 only said "add recipe-redirect alongside existing submodule-safety" — doesn't flag the Write|Edit PreToolUse matchers. Implementer might overwrite them.
   - Fix: Added "(preserve existing Bash and Write|Edit matchers)" to PreToolUse bullet; added "(existing PostToolUse Bash matcher for submodule-safety stays unchanged)" to PostToolUse bullet.
   - **Status**: FIXED

2. **b: directive scope inconsistency**
   - Location: Scope IN vs Scope OUT
   - Problem: After adding b: as item 5 in Phase 1 with "implement as stub or skip" treatment, b: remained in Scope OUT as "b: directive (semantics TBD)" — creating a contradiction (IN and OUT both claimed it).
   - Fix: Changed Scope OUT entry to "b: directive full implementation (semantics TBD — stub placeholder acceptable, full behavior blocked)" to distinguish stub presence from full implementation deferral.
   - **Status**: FIXED

3. **Stale count in Approach summary**
   - Location: Approach section, line 1 of second paragraph
   - Problem: After Phase 1 count was updated to 7, the Approach summary still said "6 changes to existing 839-line script".
   - Fix: Updated to "7 changes".
   - **Status**: FIXED

4. **Missing reference to userpromptsubmit-plan.md**
   - Location: Phase 1
   - Problem: Brief says "Detailed plan at plans/hook-batch/userpromptsubmit-plan.md" — outline doesn't reference it. Implementer loses the pattern specs, expansion strings, and execution order that are only in that file.
   - Fix: Added "Implementation details: plans/hook-batch/userpromptsubmit-plan.md has full pattern specs, expansion strings, and execution order."
   - **Status**: FIXED

## Fixes Applied

- Approach summary — "6 changes" → "7 changes"
- Phase 1 opening — "Six changes" → "Seven changes"; numbered list updated to 7 items (b: added as item 5, CCG/skill-editing shifted to 6-7)
- Phase 1 — Added deferred note for b: and reference to userpromptsubmit-plan.md
- Phase 3 Logic step 1 — Corrected file_path extraction source (tool_input for both, not tool_result for Edit)
- Phase 5 — Added preservation note for existing PreToolUse matchers and PostToolUse Bash matcher
- Scope IN — "6 improvements" → "7 improvements (b: stub or skip)"
- Scope OUT — "b: directive (semantics TBD)" → "b: directive full implementation (semantics TBD — stub placeholder acceptable, full behavior blocked)"

## Positive Observations

- D-6 (PreToolUse is informative, not blocking) is correct and well-motivated — the denylist provides enforcement, the hook provides UX.
- #10373 degraded-mode rationale is clear: advisory hooks failing silently is acceptable, so limited SessionStart reach doesn't block the phase.
- Phase type tagging (TDD vs General) is appropriate and consistent with how the phases will execute.
- Files Affected table is comprehensive and maps cleanly to phases.
- Key Decisions section captures all non-obvious choices with rationale.

## Recommendations

- Q-1 (b: directive semantics) needs user input before implementation can proceed for that item. Brainstorm, bookmark, and batch are all plausible — the "mirror-letter set" framing doesn't constrain the semantic.
- Phase 3 (PostToolUse auto-format as .sh): consider whether Bash vs Python matters for the `tool_input` stdin JSON parsing. Bash JSON parsing is error-prone; Python would be more robust for the file_path extraction step.
- Phase 2 python3/python deny list pattern match may fire on legitimate uses — consider narrowing to specific script names rather than the interpreter prefix.

---

**Ready for user presentation**: Yes
