# Phase 2: Skill Updates (handoff + remember)

**Complexity:** Low-moderate (careful insertion, preserve existing behavior)
**Model:** Sonnet
**Scope:** ~50 lines total across 2 skills

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

## Step 2.2: Update Remember Skill Quality Criteria

**Objective:** Add learnings quality and staging retention guidance to remember skill.

**Implementation:**

Modify `agent-core/skills/remember/SKILL.md`:

**1. Locate insertion point:**
- Find section "### 4. Apply + Verify" (around line 56)
- Insert new sections after this section, before "### 5. Document"

**2. New section: Learnings Quality Criteria**

Insert after "### 4. Apply + Verify":

```markdown
### Learnings Quality Criteria

**Principle-level (consolidate):** ✅
- States a general constraint or pattern
- Applies beyond the specific incident
- Example: "Always load skill context before editing"

**Incident-specific (reject/revise):** ❌
- Describes what happened, not what to do
- Narrow to one case, not generalizable
- Example: "Edited skill without loading it" → revise to principle

**Meta-learnings (use sparingly):**
- Rules about rules — only when behavioral constraint required
- Example: "Soft limits normalize deviance" → consolidate if recurrent
```

**3. New section: Staging Retention Guidance**

Insert after "Learnings Quality Criteria":

```markdown
### Staging Retention Guidance

**Keep in staging (do not consolidate):**
- Entries < 7 active days old (insufficient validation)
- Entries with pending cross-references (depend on other work)
- Entries under active investigation

**Consolidate:**
- Entries ≥ 7 active days with proven validity
- Entries that have been applied consistently
- Entries referenced by multiple sessions

**Drop (remove from staging):**
- Superseded by newer entry on same topic
- Contradicted by subsequent work
- Incident-specific without generalizable principle
```

**4. Cross-reference examples:**

Consider adding examples from current `agents/learnings.md`:
- Principle-level: "Prose gates skipped" (line ~85) — general pattern
- Incident-specific: (none currently) — show what NOT to consolidate
- Meta-learning: "Hard limits vs soft limits" (line ~31) — rules about rules

**Expected Outcome:**

Remember skill updated with quality guidance:
- Two new sections after "### 4. Apply + Verify"
- Learnings Quality Criteria with 3 categories (✅ and ❌ markers)
- Staging Retention Guidance with 3 categories (keep/consolidate/drop)
- Examples illustrate good vs bad learnings
- No changes to protocol steps 1-4a

**Validation:**

```bash
# Verify sections added
grep -n "### Learnings Quality Criteria" agent-core/skills/remember/SKILL.md
grep -n "### Staging Retention Guidance" agent-core/skills/remember/SKILL.md

# Verify position (after step 4, before step 5)
grep -B2 "### Learnings Quality Criteria" agent-core/skills/remember/SKILL.md | grep "### 4"
grep -A5 "### Staging Retention Guidance" agent-core/skills/remember/SKILL.md | grep "### 5"
```

Expected:
- Both new sections present
- Positioned between step 4 and step 5
- No unintended changes to protocol steps

**Unexpected Result Handling:**

If sections don't fit structurally:
- **Step 4 has substeps**: Insert after all substeps (after 4a)
- **Section numbering issues**: These are non-numbered sections (no "### 4.x" — just "###")
- **Markdown formatting**: Verify ✅ and ❌ emoji render correctly

**Error Conditions:**

| Condition | Action |
|-----------|--------|
| Section 4 not found | Verify remember skill structure matches documentation |
| Emoji not supported | Use text: "(consolidate)" and "(reject)" |
| Duplicate sections | Check for existing quality criteria, merge if present |

**Success Criteria:**

- [ ] "Learnings Quality Criteria" section added after step 4
- [ ] "Staging Retention Guidance" section added after quality criteria
- [ ] Both sections positioned before step 5 "Document"
- [ ] Examples provided for each category (principle, incident, meta)
- [ ] Keep/consolidate/drop criteria clearly differentiated
- [ ] No changes to existing protocol steps 1-5
- [ ] Markdown formatting correct (✅ and ❌ render)

**Report Path:** `plans/learnings-consolidation/reports/phase-2-execution.md`

**Design References:**
- D-1: Step 4c insertion point
- D-3: Trigger evaluation thresholds
- D-6: Reactive refactoring flow
- D-7: Graceful failure (try/catch)
- Implementation Component 4: Handoff skill modification
- Implementation Component 5: Remember skill update
