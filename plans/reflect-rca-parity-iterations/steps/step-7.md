# Step 7

**Plan**: `plans/reflect-rca-parity-iterations/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 7: Add Planning-Time File Size Awareness to plan-adhoc Skill

**Objective:** Update plan-adhoc skill with the same file size awareness convention as plan-tdd, adapted for non-TDD context.

**Design Reference:** DD-4 (design lines 108-119)

**File:** `agent-core/skills/plan-adhoc/SKILL.md` (existing, edit)

**Current State:**
- Skill documents ad-hoc runbook creation process
- No guidance on file size awareness during planning

**Changes Required:**

Add file size awareness convention to planner guidance sections. Content is nearly identical to Step 6, adapted for non-TDD terminology (~15 lines):

```markdown
### Planning-Time File Size Awareness

**Convention:** When a step adds content to an existing file, note current file size and plan splits proactively.

**Process:**
1. For each step adding content to existing file: Note `(current: ~N lines, adding ~M)`
2. If `N + M > 350`: Include a split step in the same phase
3. Threshold is 350, not 400 — leaves 50-line margin for vet fixes and minor additions

**Why 350:** The 400-line limit is a hard fail at commit time. Planning to the exact limit creates brittleness. A 50-line margin is pragmatic.

**Example:**
- Step 2.3 adds authentication handlers to routes.py (current: ~330 lines, adding ~35)
- Step 2.3: Implement authentication handlers (~365 lines total)
- Step 2.4: Split routes.py into routes_auth.py + routes_core.py

**No runtime enforcement:** This is a planning convention. The commit-time `check_line_limits.sh` remains the hard gate. This prevents write-then-split rework loops.
```

**Implementation:**
Locate planner guidance sections in plan-adhoc/SKILL.md (likely within Point 1 phase-by-phase expansion or step planning sections). Insert the file size awareness convention content. Integrate with existing guidance.

**Expected Outcome:**
- Convention documented with process steps (adapted from plan-tdd Step 6)
- Example uses ad-hoc terminology (step numbers, not cycle numbers)
- Rationale and threshold (350) identical to plan-tdd version

**Validation:**
- Read updated skill, verify convention content present
- Verify example uses ad-hoc terminology (not TDD cycles)
- Verify threshold and rationale match plan-tdd Step 6

**Success Criteria:**
- ~15 lines added to plan-adhoc/SKILL.md
- Contains process steps, threshold (350), example adapted for ad-hoc context
- Integrated with existing planner guidance sections

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-7-execution.md`

---
