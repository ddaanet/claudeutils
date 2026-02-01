# Step 3

**Plan**: `/Users/david/code/claudeutils/plans/design-workflow-enhancement/runbook.md`
**Common Context**: See plan file for context

---

## Step 3: Update Skills

**Objective**: Update design skill (restructure) and plan skills (add documentation perimeter reading)

**Execution Model**: Sonnet (interprets design guidance into skill edits)

**Implementation**:

**3.1 - Update design skill** (`agent-core/skills/design/SKILL.md`):

**First:** Read full skill file to identify current section structure (numbered steps vs phases, exact headings).

From design "Step mapping" table (lines 68-79), restructure skill from current Steps 0-7 into Phases A-C:

**Changes needed**:
- Replace "### 1. Understand Request" + "### 1.5. Memory Discovery" (lines ~40-54) → Phase A.1 (documentation checkpoint using hierarchy from design lines 85-103)
- Replace "### 2. Explore Codebase" (lines ~56-60) → Phase A.2 (delegate to quiet-explore, specify report path)
- Replace "### 3. Research (if needed)" (lines ~62-64) → Phase A.3-4 (Context7 + web research, call directly from main session)
- Split "### 4. Create Design Document" (lines ~66-94) into:
  - Phase A.5 (outline) — new section for outline creation + presentation
  - Phase C.1 (full design) — move current Step 4 content here, add documentation perimeter requirement (design lines 104-126)
- Rename "### 5. Vet Design" (lines ~96-110) → Phase C.3 (general-purpose opus review - keep unchanged)
- Rename "### 6. Apply Fixes" (lines ~112-116) → Phase C.4 (keep unchanged)
- Rename "### 7. Handoff and Commit" (lines ~118-129) → Phase C.5 (keep unchanged)

**Phase B (new)**: Insert between Phase A and Phase C — iterative discussion section from design lines 53-59

**Preservation mapping**:
- "### 0. Complexity Triage" (lines ~20-36) → Keep as-is before Phase A
- Plugin-topic skill-loading directive (currently in Step 4 lines ~86-94) → Move to Phase A.5 (outline section)
- Tail-call to `/handoff --commit` (currently Step 7 lines ~120-127) → Becomes Phase C.5 (no change)

**3.2 - Update plan-adhoc skill** (`agent-core/skills/plan-adhoc/SKILL.md`):

Add "Read documentation perimeter" as first numbered item (item 0) within Point 0.5 section, before the existing "Discover relevant prior knowledge" item.

**Insertion point**: After "### Point 0.5: Discover Codebase Structure (REQUIRED)" heading (line ~95), before "**Before writing any runbook content:**"

**New content**:
```markdown
**0. Read documentation perimeter (if present):**

If design document includes "Documentation Perimeter" section:
- Read all files listed under "Required reading"
- Note Context7 references (may need additional queries)
- Factor knowledge into step design

This provides designer's recommended context. Still perform discovery steps 1-2 below for path verification and memory-index scan.
```

**After insertion**: Renumber existing items (currently 1-2) to (1-2) — no change needed, just verify they remain after new item 0.

**3.3 - Update plan-tdd skill** (`agent-core/skills/plan-tdd/SKILL.md`):

Add documentation perimeter reading to Phase 1 as Step 0, before existing actions.

**Insertion point**: After "### Phase 1: Intake (Tier 3 Only)" heading and "**Objective:** Load design and project conventions." (lines ~104-106), before "**Actions:**" section.

**New content** (insert as first numbered item in Actions list, before "1. **Determine design path:**"):
```markdown
0. **Read documentation perimeter (if present):**
   - If design includes "Documentation Perimeter" section, read all listed files under "Required reading"
   - Note Context7 references for potential additional queries
   - This provides designer's recommended context before discovery

```

**After insertion**: Existing actions 1-4 remain numbered as-is (they're already correctly numbered).

**Expected Outcome**: design skill restructured into 3-phase workflow, plan-adhoc and plan-tdd updated with documentation perimeter reading

**Unexpected Result Handling**:
- If skill structure doesn't match expected sections: Read full skill file to identify actual structure, then apply changes
- If unclear how to integrate guidance: Report ambiguity to user

**Error Conditions**:
- Skill file missing → Error with specific path
- Section not found where expected → Read file, report actual structure

**Validation**:
- All 3 skill files modified
- design skill has Phases A-C structure
- plan-adhoc has documentation perimeter reading in Point 0.5
- plan-tdd has documentation perimeter reading in Phase 1
- YAML frontmatter still valid after edits

**Success Criteria**:
- 3 skill files updated
- Structural changes preserve existing logic flow
- No YAML parse errors

**Report Path**: `plans/design-workflow-enhancement/reports/step-3-skill-updates.md`

---
