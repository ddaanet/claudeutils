# Step 2.2

**Plan**: `plans/learnings-consolidation/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

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
# Phase 3: Agent Definitions (remember-task + memory-refactor)

**Complexity:** Moderate-high (embed protocol, pre-checks, reporting)
**Model:** Sonnet
**Scope:** ~200 lines total across 2 agents

---
