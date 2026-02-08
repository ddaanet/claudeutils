# Step 6

**Plan**: `plans/reflect-rca-parity-iterations/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 6: Add Planning-Time File Size Awareness to plan-tdd Skill

**Objective:** Update plan-tdd skill to include convention for noting current file sizes when adding content and proactively planning splits when approaching the 400-line limit.

**Design Reference:** DD-4 (design lines 108-119)

**File:** `agent-core/skills/plan-tdd/SKILL.md` (existing, edit)

**Current State:**
- Skill documents TDD runbook creation process
- No guidance on file size awareness during planning

**Changes Required:**

Add file size awareness convention to planner guidance sections. Exact location depends on current structure — search for sections discussing cycle planning or implementation details. Add ~15 lines:

```markdown
### Planning-Time File Size Awareness

**Convention:** When a cycle adds content to an existing file, note current file size and plan splits proactively.

**Process:**
1. For each cycle adding content to existing file: Note `(current: ~N lines, adding ~M)`
2. If `N + M > 350`: Include a split step in the same phase
3. Threshold is 350, not 400 — leaves 50-line margin for vet fixes and minor additions

**Why 350:** The 400-line limit is a hard fail at commit time. Planning to the exact limit creates brittleness. A 50-line margin is pragmatic.

**Example:**
- Cycle 3.2 adds format_model() to display.py (current: ~320 lines, adding ~40)
- Cycle 3.2: Implement format_model() (~360 lines total)
- Cycle 3.3: Split display.py into display_core.py + display_formatters.py

**No runtime enforcement:** This is a planning convention. The commit-time `check_line_limits.sh` remains the hard gate. This prevents write-then-split rework loops.
```

**Implementation:**
Locate planner guidance sections in plan-tdd/SKILL.md (likely within Phase 1-3 or cycle planning sections). Insert the file size awareness convention content above. Integrate with existing guidance — if there's a "Cycle Planning" section, add this as a subsection.

**Expected Outcome:**
- Convention documented with process steps (note sizes, check threshold, plan splits)
- Rationale explains 350-line margin (not 400)
- Example demonstrates notation and split planning
- Clarifies this is planning convention, not runtime enforcement

**Validation:**
- Read updated skill, verify convention content present
- Verify 350-line threshold explained with margin rationale
- Verify example shows both notation and split step

**Success Criteria:**
- ~15 lines added to plan-tdd/SKILL.md
- Contains process steps, threshold (350), example, runtime enforcement note
- Integrated with existing planner guidance sections

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-6-execution.md`

---
