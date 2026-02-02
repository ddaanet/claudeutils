# Step 6 Execution Report

**Objective:** Add step 7 to design skill that invokes `/handoff --commit` after applying fixes.

**Status:** COMPLETE

## Actions Taken

Edited `agent-core/skills/design/SKILL.md`:

**Added new step 7 after step 6 (Apply Fixes):**
- CRITICAL directive to invoke `/handoff --commit` as final action
- Chain explanation: handoff → commit → STATUS
- Next step context (typically planning phase)
- Rationale for universal tail behavior

**Placement:**
- Inserted between step 6 (Apply Fixes) and Output Expectations section
- Maintains logical flow from fixes → handoff → commit

## Validation

✅ Step 7 exists after step 6
✅ Tail-call instruction present with CRITICAL emphasis
✅ Chain documented (handoff → commit → STATUS)
✅ Next task context explained
✅ No step count needed in intro (Process section doesn't mention count)

## Outcome

Design skill now chains into handoff → commit → STATUS, providing universal termination pattern. Users see next pending task (typically planning phase) after design completes.
