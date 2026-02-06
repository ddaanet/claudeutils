# Step 2.1

**Plan**: `plans/learnings-consolidation/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 2.1: Add Step 4c to Handoff Skill

**Objective:** Insert consolidation trigger logic into handoff workflow while preserving existing protocol.

**Implementation:**

Modify `agent-core/skills/handoff/SKILL.md`:

**1. Locate insertion point:**
- Find Step 4b: "Check invalidated learnings" (lines ~115-140)
- Find Step 5: "Session Size Check" (lines ~160-165)
- Insert new Step 4c between these two

**2. Step 4c content:**

```markdown
### 4c. Consolidation Trigger Check

Run `agent-core/bin/learning-ages.py agents/learnings.md` to get age data.

**Trigger conditions (any one sufficient):**
- File exceeds 150 lines (size trigger)
- 14+ active days since last consolidation (staleness trigger)

**If triggered:**
1. Filter entries with age ≥ 7 active days
2. Check batch size ≥ 3 entries
3. If sufficient: delegate to remember-task agent with filtered entry list
4. Read report from returned filepath
5. If report contains escalations:
   - **Contradictions**: Note in handoff output under Blockers/Gotchas
   - **File limits**: Execute refactor flow (see below)

**Refactor flow (when file at 400-line limit):**

Handoff executes these steps after reading remember-task report with file-limit escalation:

1. Delegate to memory-refactor agent for the specific target file
2. Memory-refactor agent splits file, runs `validate-memory-index.py` autofix
3. Re-invoke remember-task with only the entries that were skipped due to file limit
4. Read second report
5. Check for remaining escalations (contradictions or additional file limits)

Note: This is handoff's perspective. Design D-6 describes the full 7-step flow including remember-task's internal steps (detect → skip → report).

**If not triggered or batch insufficient:**
- Skip consolidation (no action needed)
- Continue to step 5

**On error:**
- Catch exception during script execution or agent delegation
- Log error to stderr: `echo "Consolidation skipped: [error-message]" >&2`
- Note in handoff output: "Consolidation skipped: [brief-reason]"
- Continue to step 5 (consolidation failure must not block handoff per NFR-1)
```

**3. Update frontmatter allowed-tools:**

Change line 4 from:
```yaml
allowed-tools: Read, Write, Edit, Bash(wc:*), Skill
```

To:
```yaml
allowed-tools: Read, Write, Edit, Bash(wc:*, agent-core/bin/learning-ages.py:*), Task, Skill
```

**4. Step numbering preservation:**

Verify:
- [ ] Step 4c inserted between 4b and 5
- [ ] Step 5 ("Session Size Check") unchanged
- [ ] All subsequent steps (6, 7, 8) unchanged
- [ ] No renumbering required

**Expected Outcome:**

Handoff skill updated with consolidation trigger:
- Step 4c present and correctly positioned
- Tool permissions include learning-ages.py and Task
- Trigger thresholds match design (150 lines, 14 days staleness, 7 days freshness, 3 minimum batch)
- Error handling wraps entire step 4c
- Refactor flow documented (detect → spawn → retry)

**Validation:**

```bash
# Verify insertion point
grep -n "### 4c" agent-core/skills/handoff/SKILL.md

# Verify step 5 unchanged
grep -A5 "### 5\." agent-core/skills/handoff/SKILL.md

# Verify tool permissions
grep "allowed-tools:" agent-core/skills/handoff/SKILL.md | head -1
```

Expected:
- Step 4c line number between 4b and 5
- Step 5 content matches original (session size check with wc command)
- Tool permissions include `learning-ages.py` and `Task`

**Unexpected Result Handling:**

If insertion breaks skill:
- **Step numbering collision**: Verify no duplicate "### 4c" headers exist
- **Tool permission error**: Ensure Bash pattern uses wildcard for arguments: `Bash(wc:*, agent-core/bin/learning-ages.py:*)`
- **Skill fails to load**: Check YAML frontmatter syntax (allowed-tools is comma-separated string)

**Error Conditions:**

| Condition | Action |
|-----------|--------|
| Step 4b not found | Verify current handoff skill version matches documentation |
| Step 5 already numbered 4c | Existing modification conflict, escalate to user |
| Tool syntax error | Check comma separation, no quotes around tool list |

**Success Criteria:**

- [ ] Step 4c inserted between 4b and 5 (no renumbering)
- [ ] Tool permissions include `agent-core/bin/learning-ages.py` and `Task`
- [ ] Trigger thresholds explicit (150 lines, 14 days, 7 days, 3 minimum)
- [ ] Refactor flow documented with 5 sub-steps
- [ ] Error handling try/catch pattern documented
- [ ] Step 5 "Session Size Check" unchanged
- [ ] No unintended changes to other steps

---
