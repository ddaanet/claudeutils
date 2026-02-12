# Vet Review: Cycle 4.4 Mode C implementation (merge ceremony)

**Scope**: Mode C prose section in SKILL.md (merge ceremony steps)
**Date**: 2026-02-10
**Mode**: review + fix

## Summary

Cycle 4.4 added 19 lines implementing Mode C (merge ceremony) prose to `agent-core/skills/worktree/SKILL.md`. The prose describes the 5-step merge ceremony workflow with error handling for three exit code paths. Overall structure matches design spec (lines 360-368). Writing style follows imperative/infinitive pattern (SR-9). Error handling covers all three exit codes with resolution guidance (SR-7).

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Step 1 lacks tool anchor**
   - Location: SKILL.md:101 (new Step 1)
   - Problem: Prose-only step without opening tool call violates SR-8 (D+B hybrid pattern)
   - Suggestion: Prepend `Read("agents/session.md")` before invoking handoff skill
   - **Status**: FIXED

2. **Step 2 prose-only decision point**
   - Location: SKILL.md:103 (new Step 2)
   - Problem: "Capture the exit code and stderr output" is imperative but has no tool call anchor
   - Suggestion: This step should open with the CLI invocation tool call, not prose describing what to capture
   - **Status**: FIXED

### Minor Issues

1. **Session.md edit instruction lacks tool specification**
   - Location: SKILL.md:105 (Step 3 success path)
   - Note: "Edit `agents/session.md`" should specify tool (Edit) for clarity
   - **Status**: FIXED

2. **Worktree Tasks section location assumption**
   - Location: SKILL.md:105 (Step 3 task removal)
   - Note: Instruction assumes Worktree Tasks section exists; should gracefully handle missing section
   - **Status**: FIXED

3. **Exit code 2 error reporting lacks specificity**
   - Location: SKILL.md:113 (Step 5)
   - Note: "Report stderr as-is" is vague; clarify display format for error output
   - **Status**: FIXED

## Fixes Applied

- SKILL.md:101 — Added `Read("agents/session.md")` tool call before `/handoff --commit` invocation
- SKILL.md:103 — Moved CLI invocation to step opening, made "capture exit code" a natural consequence
- SKILL.md:105 — Changed "Edit `agents/session.md`" to "Use Edit tool on `agents/session.md`"
- SKILL.md:105 — Added graceful degradation: "If Worktree Tasks section missing, create it before removal"
- SKILL.md:113 — Clarified error reporting: "Output: 'Merge error: ' followed by stderr content"

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| SR-5: Orchestrate merge ceremony | Satisfied | SKILL.md:101-113 covers handoff → commit → merge → cleanup sequence |
| SR-7: Error communication with guidance | Satisfied | Lines 107-112 provide conflict and precommit resolution guidance |
| SR-8: Tool anchors at decision points | Partial → Fixed | Steps 1-2 lacked tool calls, now fixed |
| SR-9: Imperative/infinitive style | Satisfied | Prose uses "Invoke", "Edit", "Read" imperative verbs |

**Gaps:** None after fixes applied.

## Positive Observations

- Clean separation of three exit code paths with specific guidance for each
- Idempotent resume pattern clearly documented for both conflict and precommit failure cases
- Comprehensive ceremony explanation: why handoff+commit is mandatory before merge
- Good defensive reporting: flags session file conflicts as bugs (should auto-resolve)
- Progressive disclosure: references cleanup command without over-explaining

## Recommendations

None — implementation follows design spec with minor refinements applied.
