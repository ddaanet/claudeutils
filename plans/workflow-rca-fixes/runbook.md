---
name: workflow-rca-fixes
model: sonnet
---

# Workflow RCA Fixes — Implementation Runbook

**Context**: Five root cause analyses identified 18 process gaps in the agent workflow pipeline. All gaps are prose defects in skill definitions, agent definitions, decision documents, and fragments. No code changes required.

**Design**: plans/workflow-rca-fixes/design.md
**Requirements**: plans/workflow-rca-fixes/requirements.md (20 FRs, 4 constraints)
**Status**: Ready
**Created**: 2026-02-15

---

## Weak Orchestrator Metadata

**Total Steps**: 16

**Execution Model**:
- All steps: Sonnet (prose edits, reviews, semantic analysis)
- Diagnostic review: Opus (Phases 1-4 only, interactive sessions)

**Step Dependencies**: Sequential within phases. Cross-phase dependencies: Phase 1 creates skills → Phase 2-6 agents use updated skills; Phase 2 updates review logic → Phase 3+ use updated logic; Phase 3 updates vet-fix-agent → Phase 4-6 use updated taxonomy.

**Error Escalation**:
- Sonnet → User: Review finds UNFIXABLE issues, skill-reviewer/agent-creator escalates validation failures
- Phase checkpoints: Restart required after Phases 1, 3-5; interactive diagnostic review after Phases 1-4

**Report Locations**: plans/workflow-rca-fixes/reports/

**Success Criteria**: All 20 FRs implemented, all artifacts passing domain-specific review, all restart-requiring changes functional after session restarts.

**Prerequisites**:
- plugin-dev:skill-development loaded (✓ Step 1.1-1.2 skill creation)
- plugin-dev:agent-development loaded (✓ all agent frontmatter modifications)
- Continuation passing section of orchestrate/SKILL.md read (✓ understanding agent composition)
- Existing non-invocable skills examined (✓ review-plan, plugin-dev-validation, handoff-haiku)

---

## Common Context

**Requirements Summary:**

All 20 FRs mapped across 6 phases:
- FR-1 to FR-3: Runbook review overhaul (Phase 2)
- FR-4: General-step reference material (Phase 5)
- FR-5, FR-11: Runbook outline review enhancements (Phase 4)
- FR-6: Delete obsolete Phase 1.4 (Phase 6)
- FR-7 to FR-10, FR-18: Vet agent overhaul (Phase 3)
- FR-12, FR-13: Agent composition via skills (Phase 1)
- FR-14, FR-15, FR-19: Design skill improvements (Phase 5)
- FR-16: Deliverable review workflow step (Phase 5)
- FR-17: Execution feedback requirement (Phase 6)
- FR-20: Design-vet-agent review criteria (Phase 5)

**Scope Boundaries:**
- **In scope:** Prose edits to skills, agents, fragments, decision documents
- **Out of scope:** Code changes, error-handling framework implementation, upstream plugin-dev docs, formal workflow verification

**Key Constraints:**
- C-1: All prose edits. No code changes.
- C-2: Native `skills:` mechanism for agent composition.
- C-3: Fragment-wrapping skills must pass skill-reviewer.
- C-4: FR-17 documents requirement only; implementation deferred to `wt/error-handling`.

**Key Design Decisions:**

1. **Reflexive bootstrapping order** — improve each tool before using it downstream. Order: composition (Phase 1) → runbook review (Phase 2) → vet (Phase 3) → outline review (Phase 4) → content edits (Phase 5) → cleanup (Phase 6).

2. **Convention injection via skills** — `skills:` frontmatter injects full SKILL.md (~300-400 tokens per skill, 2-3 per agent manageable).

3. **Four-status vet taxonomy** — FIXED/DEFERRED/OUT-OF-SCOPE/UNFIXABLE with investigation gates → prevents over-escalation.

4. **Review-fix integration** — merge into existing sections by heading match, not append.

5. **Diagnostic review as interactive opus session** — NOT delegated, enabled for Phases 1-4 (self-referential), skipped for Phases 5-6 (content).

6. **All general phase types** — No TDD phases — all prose edits, no behavioral code changes.

7. **Execution model** — Sonnet for edits, opus for diagnostic review (Phases 1-4 only).

**Project Structure:**
- Agent definitions: `agent-core/agents/`
- Skill definitions: `agent-core/skills/`
- Decision documents: `agents/decisions/`
- Fragments: `agent-core/fragments/`
- Plugin-dev skills: loaded via Skill tool (skill-development, agent-development)

---

### Phase 1: Agent Composition (type: general)

**Complexity:** Medium (3 steps, ~150 lines)
**Model:** Sonnet
**Restart required:** Yes (agent frontmatter changes)
**Diagnostic review:** Yes (improving review tools)
**FRs addressed:** FR-12, FR-13

---

## Step 1.1: Create error-handling skill

**Objective**: Wrap error-handling.md fragment as a skill for injection into bash-heavy agents.

**Prerequisites**:
- Read `agent-core/skills/project-conventions/SKILL.md` (early bootstrap reference)
- Read `agent-core/fragments/error-handling.md` (content to wrap)
- plugin-dev:skill-development loaded

**Implementation**:

Create `agent-core/skills/error-handling/SKILL.md` following project-conventions pattern:

1. YAML frontmatter:
   - name: error-handling
   - description: "This skill should be used when bash-heavy agents need error suppression guidance. Provides error handling rules for agents that execute bash commands frequently."
   - user-invocable: false

2. Skill prolog (brief purpose statement)

3. Include full content of `agent-core/fragments/error-handling.md`

**Expected Outcome**: Skill file created at `agent-core/skills/error-handling/SKILL.md` following fragment-wrapping pattern.

**Error Conditions**:
- If skill structure invalid → review frontmatter format
- If content duplicates → ensure single source of truth (fragment content only)

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer (plugin-dev): "Review error-handling skill for structure, frontmatter quality, and progressive disclosure"
3. Read review report
4. If UNFIXABLE: STOP, escalate to user
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-1.1-skill-review.md

---

## Step 1.2: Create memory-index skill

**Objective**: Wrap memory-index.md with Bash transport prolog for sub-agent recall.

**Prerequisites**:
- Read `agents/memory-index.md` (content to wrap)
- Read error-handling skill from Step 1.1 (pattern reference)
- plugin-dev:skill-development loaded

**Implementation**:

Create `agent-core/skills/memory-index/SKILL.md`:

1. YAML frontmatter:
   - name: memory-index
   - description: "This skill should be used when sub-agents need memory recall capabilities. Provides index of when/how entries with Bash transport for agents without Skill tool access."
   - user-invocable: false

2. Skill prolog with Bash transport explanation:
   - Sub-agents lack Skill tool
   - Must invoke via Bash: `agent-core/bin/when-resolve.py when "<trigger>"`
   - Index syntax unchanged from main agent `/when` invocations

3. Include full content of `agents/memory-index.md`

**Expected Outcome**: Skill file created at `agent-core/skills/memory-index/SKILL.md` with transport prolog and memory index content.

**Error Conditions**:
- If transport prolog unclear → add concrete Bash invocation examples
- If index content malformed → verify memory-index.md structure

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review memory-index skill for transport prolog clarity and index completeness"
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-1.2-skill-review.md

---

## Step 1.3: Update agent frontmatters (batch)

**Objective**: Inject skills frontmatter into 5 agent definitions.

**Prerequisites**:
- Steps 1.1-1.2 committed (skills exist on disk)
- Read all 5 target agent files to verify current state
- plugin-dev:agent-development loaded

**Implementation**:

Update frontmatter for 5 agents in single edit session:

1. `agent-core/agents/vet-fix-agent.md`:
   - Add `skills: [project-conventions, error-handling, memory-index]`

2. `agent-core/agents/design-vet-agent.md`:
   - Verify `skills: [project-conventions]` present (early bootstrap)
   - Add if missing

3. `agent-core/agents/outline-review-agent.md`:
   - Add `skills: [project-conventions]`

4. `agent-core/agents/plan-reviewer.md`:
   - Add `skills: [project-conventions]`
   - Note: already has review-plan skill reference

5. `agent-core/agents/refactor.md`:
   - Add `skills: [project-conventions, error-handling]`

**Expected Outcome**: All 5 agent definitions have `skills:` frontmatter referencing appropriate skills. Single commit with all changes.

**Error Conditions**:
- If skills field malformed → verify YAML array syntax
- If skills don't exist → check Steps 1.1-1.2 completed
- If agent files not found → verify paths with Glob

**Validation**:
1. Commit all frontmatter changes together
2. Delegate to agent-creator (plugin-dev): "Review and validate batch frontmatter updates for 5 agents at agent-core/agents/. Check skills references are valid and appropriate for each agent."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-1.3-agent-batch-review.md

---

**Phase 1 Checkpoint**:
1. Run `just sync-to-parent` with dangerouslyDisableSandbox: true (creates symlinks in .claude/skills/)
2. Verify symlinks created: `ls -la .claude/skills/` should show error-handling and memory-index
3. Commit checkpoint if needed
4. Restart session (agent frontmatter changes require discovery)
5. Proceed to Phase 2

---

### Phase 2: Runbook Review Overhaul (type: general)

**Complexity:** High (3 steps, ~200 lines)
**Model:** Sonnet
**Restart required:** No (runbook-review.md accessed via /when recall, skills loaded on demand — none require restart)
**Diagnostic review:** Yes (improving review logic)
**FRs addressed:** FR-1, FR-2, FR-3

---

## Step 2.1: Restructure runbook-review.md as type-agnostic

**Objective**: Transform 4 review axes from TDD-only to type-agnostic with TDD/General bullets, add file growth as 5th axis, add behavioral vacuity detection.

**Prerequisites**:
- Read `agents/decisions/runbook-review.md` (current state)
- Read `agents/decisions/pipeline-contracts.md` (T1-T6 defect classification context)

**Implementation**:

Restructure runbook-review.md:

1. **Four axes restructure** (vacuity, ordering, density, checkpoints):
   - For each axis: type-neutral definition, then subsections:
     - **TDD:** [TDD-specific detection criteria]
     - **General:** [General-specific detection criteria]

2. **Add file growth as 5th axis**:
   - Definition: projected file sizes vs 400-line threshold
   - Detection: lines-per-cycle/step projection, split points
   - Both types: cumulative line tracking, split-phase placement

3. **Update process section**:
   - Use "item (cycle or step)" terminology throughout
   - Replace TDD-specific language with type-conditional phrasing

4. **Add behavioral vacuity detection**:
   - **TDD:** For each cycle pair (N, N+1) on same function, verify N+1's RED assertion would fail given N's GREEN. If not, cycles are behaviorally vacuous.
   - **General:** For consecutive steps modifying same artifact, verify step N+1 produces outcome not achievable by extending step N's implementation alone. If achievable, steps should be merged.
   - **Heuristic (both):** cycles/steps > LOC/20 signals consolidation needed.

**Expected Outcome**: runbook-review.md has 5 type-agnostic axes, behavioral vacuity detection for both types, and type-neutral process terminology.

**Error Conditions**:
- If axes remain TDD-specific → verify General subsections added
- If vacuity detection vague → add concrete verification steps
- If terminology inconsistent → grep for TDD-only terms, replace with item/cycle/step conditionals

**Validation**:
1. Commit changes
2. Delegate to vet-fix-agent: "Review runbook-review.md restructuring. Verify all 5 axes have type-agnostic definitions with TDD/General subsections, behavioral vacuity detection is concrete, and process section uses conditional terminology."
3. Read review report, grep for UNFIXABLE
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-2.1-vet-review.md

---

## Step 2.2: Expand review-plan Section 11 with general detection

**Objective**: Add `**General:**` detection bullets to Sections 11.1-11.3 (vacuity, ordering, density).

**Prerequisites**:
- Read `agent-core/skills/review-plan/SKILL.md` (current Section 11)
- Step 2.1 committed (runbook-review.md has General detection criteria as reference)

**Implementation**:

Expand Section 11 (LLM Failure Mode Detection):

1. **Section 11.1 (Vacuity Detection)**:
   - Preserve existing TDD content
   - Add `**General:**` subsection with:
     - Scaffolding-only steps (file creation without behavioral change)
     - Steps producing outcomes achievable by extending prior step
     - Heuristic: steps > LOC/20

2. **Section 11.2 (Ordering Defects)**:
   - Preserve existing TDD content
   - Add `**General:**` subsection with:
     - Steps referencing structures from later steps
     - Prerequisites not validated before use
     - Foundation-after-behavior inversions

3. **Section 11.3 (Density Issues)**:
   - Preserve existing TDD content
   - Add `**General:**` subsection with:
     - Adjacent steps on same artifact with <20 LOC delta
     - Multi-step sequences collapsible to single step
     - Over-granular decomposition without clear boundary

4. **Add restart-reason verification** (metadata validation):
   - For each phase claiming "Restart required: Yes", verify the stated reason matches restart trigger rules
   - Restart triggers: agent definitions (.claude/agents/), hooks, plugins, MCP only
   - NOT restart triggers: decision documents, skills, fragments loaded on-demand via /when recall
   - Distinction: @-referenced files have content loaded at startup; indexed-but-recalled files do not
   - Detection: grep phase headers for "Restart required: Yes", cross-reference artifact type against trigger rules

**Expected Outcome**: Section 11 expanded with General detection criteria mirroring runbook-review.md's new axes. Restart-reason verification added to metadata validation.

**Error Conditions**:
- If General criteria duplicate TDD → differentiate by artifact type (tests vs implementations)
- If criteria too abstract → add concrete detection heuristics
- If section numbering breaks → preserve 11.1, 11.2, 11.3 structure

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review review-plan Section 11 expansion. Verify General subsections added to 11.1-11.3, criteria are concrete and distinct from TDD, and structure preserved."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-2.2-skill-review.md

---

## Step 2.3: Add LLM failure mode gate to runbook Phase 0.95

**Objective**: Add inline validation step in Phase 0.95 before fast-path promotion to check vacuity, ordering, density, checkpoints.

**Prerequisites**:
- Read `agent-core/skills/runbook/SKILL.md` Phase 0.95 section
- Step 2.1 committed (criteria reference from runbook-review.md)

**Implementation**:

In Phase 0.95 (Outline Sufficiency Check), add validation step before promotion:

1. **Gate placement**: After sufficiency criteria check, before "If sufficient → promote outline to runbook"

2. **Gate content**:
   ```
   **LLM failure mode gate (before promotion):**
   Check for common planning defects (criteria from runbook-review.md updated in Step 2.1):
   - Vacuity: any items that only create scaffolding without functional outcome?
   - Ordering: any items referencing structures from later items?
   - Density: adjacent items on same function with <1 branch difference?
   - Checkpoints: gaps >10 items without checkpoint?
   Fix inline before promotion. If unfixable, fall through to Phase 1 expansion.
   ```

3. **Integration**: Gate runs before promotion decision, fixes applied inline, unfixable issues trigger normal Phase 1 path.

**Expected Outcome**: Phase 0.95 has inline LLM failure mode check preventing defective outlines from fast-path promotion.

**Error Conditions**:
- If gate criteria vague → reference specific runbook-review.md sections
- If gate placement wrong → ensure it's before promotion, after sufficiency
- If unfixable path unclear → specify fallthrough to Phase 1

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review runbook Phase 0.95 LLM failure mode gate addition. Verify gate checks all 4 criteria, placement before promotion is correct, and unfixable fallthrough is clear."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-2.3-skill-review.md

---

**Phase 2 Checkpoint**:
1. All review logic updated (runbook-review.md, review-plan, runbook skill)
2. No restart required (decision documents and skills loaded on demand, not at startup)
3. Proceed to Phase 3

---

### Phase 3: Vet Agent Overhaul (type: general)

**Complexity:** High (3 steps, ~300 lines including taxonomy split)
**Model:** Sonnet
**Restart required:** Yes (agent definition + fragment changes)
**Diagnostic review:** Yes (improving vet tools)
**FRs addressed:** FR-7, FR-8, FR-9, FR-10, FR-18

---

## Step 3.1: Add four-status taxonomy and investigation protocol to vet-fix-agent

**Objective**: Create vet-taxonomy.md reference file and update vet-fix-agent to use four-status system with investigation-before-escalation protocol and review-fix integration rule.

**Prerequisites**:
- Read `agent-core/agents/vet-fix-agent.md` (current: 436 lines)
- Note: projected +150 lines exceeds 400-line threshold → split required
- Read `agents/decisions/pipeline-contracts.md` (ODC classification context)

**Implementation**:

**Part A: Create taxonomy reference file**

Create `agent-core/agents/vet-taxonomy.md`:

1. **Four-status definitions**:
   - FIXED: Applied, no action needed
   - DEFERRED: Real issue, explicitly out of scope (maps to scope OUT), informational
   - OUT-OF-SCOPE: Not relevant to current review, informational
   - UNFIXABLE: Technical blocker requiring user decision (with subcategory)

2. **UNFIXABLE subcategory codes**:
   - U-REQ: Requirements ambiguity or conflict
   - U-ARCH: Architectural constraint or design conflict
   - U-DESIGN: Design decision needed, multiple valid approaches

3. **Subcategory examples** (1-2 per code)

4. **Deferred Items report section template**:
   ```
   ## Deferred Items

   The following items were identified but are out of scope:
   - **[Item]** — Reason: [why deferred, reference to scope OUT or design]
   ```

**Part B: Update vet-fix-agent**

Update `agent-core/agents/vet-fix-agent.md`:

1. **Add reference to vet-taxonomy.md**:
   - In frontmatter or early in system prompt
   - "Consult vet-taxonomy.md for status definitions and subcategory codes"

2. **Add 4-gate investigation-before-escalation checklist**:
   - Before classifying UNFIXABLE, must complete:
     1. Check scope OUT list → classify as OUT-OF-SCOPE if listed
     2. Check design for documented deferral → classify as DEFERRED if found
     3. Glob/Grep for existing patterns in codebase → apply pattern if found (FIXED)
     4. Only then classify UNFIXABLE with subcategory code and investigation summary

3. **Add review-fix integration rule (FR-18)**:
   - Before applying fix: Grep target file for heading the fix targets
   - If heading exists: Edit within that section (merge, don't append)
   - If no match: Append as new section
   - Prevents structural duplication from parallel sections

**Expected Outcome**:
- vet-taxonomy.md created with all four statuses, subcategories, examples, template
- vet-fix-agent updated to reference taxonomy, include 4-gate checklist, and merge-not-append fix rule
- Combined file sizes under threshold (taxonomy ~150, vet-fix-agent reduced to ~440)

**Error Conditions**:
- If taxonomy file incomplete → verify all statuses have clear criteria
- If checklist gates vague → add concrete actions for each gate
- If integration rule ambiguous → specify Grep → Edit flow explicitly

**Validation**:
1. Commit both files (taxonomy + vet-fix-agent update)
2. Delegate to agent-creator (plugin-dev): "Review and fix vet-fix-agent.md and vet-taxonomy.md. Verify taxonomy has complete status definitions with examples, vet-fix-agent references taxonomy correctly, 4-gate checklist is concrete, and review-fix integration rule specifies Grep-then-Edit flow."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-3.1-agent-review.md

---

## Step 3.2: Update vet-requirement.md (UNFIXABLE validation + execution context enforcement)

**Objective**: Add UNFIXABLE validation steps and strengthen execution context requirements in vet-requirement.md.

**Dependencies**: Step 3.1 (vet-taxonomy.md must exist and be committed)

**Prerequisites**:
- Read `agent-core/fragments/vet-requirement.md` (current state)
- Step 3.1 committed (vet-taxonomy.md available as reference)

**Implementation**:

Update `agent-core/fragments/vet-requirement.md`:

1. **Update "Three issue statuses" → "Four issue statuses"**:
   - Add OUT-OF-SCOPE status between DEFERRED and UNFIXABLE
   - Align descriptions with vet-taxonomy.md
   - Four statuses: FIXED, DEFERRED, OUT-OF-SCOPE, UNFIXABLE

2. **Add UNFIXABLE validation steps** (after grep-for-UNFIXABLE in detection protocol):
   - Check each UNFIXABLE has subcategory code (U-REQ, U-ARCH, U-DESIGN)
   - Check each has investigation summary showing 4-gate checklist completion
   - Cross-reference against scope OUT list (should not overlap)
   - If validation fails: Resume agent for reclassification with guidance

3. **Strengthen execution context section** (FR-10):
   - Add requirement: IN/OUT scope fields must be structured lists, not empty prose
   - Add enforcement language: "Fail loudly if fields are missing or unstructured"
   - Add template example showing proper IN/OUT structure
   - Specify: OUT section prevents false positives, IN section grounds review

**Expected Outcome**: vet-requirement.md has four-status taxonomy, concrete UNFIXABLE validation with resume protocol, and strict execution context enforcement.

**Error Conditions**:
- If status descriptions diverge from taxonomy → align with vet-taxonomy.md
- If validation steps non-actionable → specify what to check and how
- If execution context enforcement vague → add "must" language and fail conditions

**Validation**:
1. Commit changes
2. Delegate to vet-fix-agent: "Review vet-requirement.md updates using vet-taxonomy.md from Step 3.1. Verify four statuses align with taxonomy, UNFIXABLE validation is concrete and includes resume protocol, and execution context section has strict enforcement guidance with structured field requirements."
3. Read review report, grep for UNFIXABLE
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-3.2-vet-review.md

---

## Step 3.3: Add orchestrate template enforcement

**Objective**: Add checkpoint delegation template with structured IN/OUT scope enforcement to orchestrate skill.

**Prerequisites**:
- Read `agent-core/skills/orchestrate/SKILL.md` (current delegation patterns)
- Steps 3.1-3.2 committed (vet-requirement.md enforcement as reference)

**Implementation**:

Update `agent-core/skills/orchestrate/SKILL.md`:

1. **Add checkpoint delegation template section**:
   - Placement: In delegation or checkpoint guidance area
   - Template content:
     ```
     Review [scope description].

     **Scope:**
     - IN: [list what was implemented]
     - OUT: [list what is NOT yet done — do NOT flag these]

     **Changed files:** [file list from git diff --name-only]

     **Requirements:**
     - [requirement 1]
     - [requirement 2]

     Fix all issues. Write report to: [report-path]
     Return filepath or error.
     ```

2. **Add enforcement guidance**:
   - Require structured IN/OUT scope fields (bulleted lists)
   - Fail loudly if empty or prose-only
   - Specify: run precommit first to ground "Changed files" in reality
   - Note: prevents confabulating future-phase issues

**Expected Outcome**: orchestrate skill has checkpoint delegation template with strict IN/OUT scope structure and enforcement guidance.

**Error Conditions**:
- If template missing required fields → verify IN, OUT, Changed files, Requirements all present
- If enforcement guidance weak → add "must" language and failure protocol
- If precommit-first ordering unclear → specify sequence explicitly

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review orchestrate skill checkpoint delegation template addition. Verify template has all required fields (IN, OUT, Changed files, Requirements), enforcement guidance is strict, and precommit-first ordering is clear."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-3.3-skill-review.md

---

**Phase 3 Checkpoint**:
1. All vet logic updated (taxonomy created, vet-fix-agent uses 4-status, vet-requirement enforces validation, orchestrate has template)
2. Restart session required (agent definition + fragment changes)
3. Proceed to Phase 4

---

### Phase 4: Runbook Outline Review Agent (type: general)

**Complexity:** Medium (1 step, ~100 lines, handles 2 FRs)
**Model:** Sonnet
**Restart required:** Yes (agent definition changes)
**Diagnostic review:** Yes (improving outline review)
**FRs addressed:** FR-5, FR-11

**Note on step density**: Single step handles two related criteria (growth validation + semantic propagation) for same agent. Splitting would create unnecessary commits/reviews for same file. Both criteria enhance same review phase (execution readiness).

---

## Step 4.1: Add outline growth validation and semantic propagation checklist

**Objective**: Add file growth projection validation and semantic propagation checklist to runbook-outline-review-agent for execution readiness.

**Prerequisites**:
- Read `agent-core/agents/runbook-outline-review-agent.md` (current review criteria)
- Read `plans/workflow-rca-fixes/reports/runbook-outline-review.md` (context from this session's outline review)

**Implementation**:

Update `agent-core/agents/runbook-outline-review-agent.md`:

1. **Add growth validation criterion** (FR-5):
   - **Placement**: Under execution readiness or outline quality section
   - **Content**:
     - Validate projected file sizes vs 400-line threshold
     - Formula: current_lines + (items × avg_lines_per_item)
     - Split phases must precede first phase exceeding 350 cumulative lines
     - Flag outlines with >10 cycles/steps on same file without projection note
   - **Fix action**: Recommend split-phase insertion or consolidation

2. **Add semantic propagation checklist** (FR-11):
   - **Placement**: Under execution readiness section
   - **Content**:
     - When design introduces new terminology/types: verify artifact inventory complete
     - Grep-based classification: producer files (rewrite with new semantics) vs consumer files (update to use new semantics)
     - All files referencing old semantics must appear in outline (producers as rewrites, consumers as updates)
   - **Detection**: Grep design for "terminology change", "rename", "semantic shift" patterns
   - **Fix action**: List missing consumer files, recommend outline items

3. **Add deliverable-level traceability check**:
   - **Grounding**: Interactive opus review this session caught FR-10 with 2 deliverables but 1 step mapping
   - **Content**:
     - Cross-reference outline coverage against design deliverables table, not just FR numbers
     - Each design deliverable row must map to an outline step
     - FRs with multiple deliverables need multiple step mappings
   - **Detection**: Extract deliverables table from design, verify each row has outline step reference
   - **Fix action**: Identify unmapped deliverables, recommend outline additions

**Expected Outcome**: runbook-outline-review-agent has growth projection validation with 350-line threshold and split-phase placement logic, semantic propagation checklist with grep-based classification, and deliverable-level traceability verification.

**Error Conditions**:
- If growth formula unclear → specify calculation with concrete example
- If semantic propagation abstract → add grep patterns and classification criteria
- If traceability check vague → specify table extraction and row-by-row verification
- If placement disrupts flow → integrate within existing execution readiness section

**Validation**:
1. Commit changes
2. Delegate to agent-creator (plugin-dev): "Review runbook-outline-review-agent.md additions. Verify growth validation has concrete formula and 350-line threshold, semantic propagation checklist has grep-based detection and producer/consumer classification, deliverable-level traceability check is grounded in session finding, and all criteria are actionable."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-4.1-agent-review.md

---

**Phase 4 Checkpoint**:
1. Outline review logic updated with growth validation, semantic propagation, and deliverable traceability
2. Restart session required (agent definition changes)
3. Proceed to Phase 5

---

### Phase 5: Design + Runbook Skill Fixes (type: general)

**Complexity:** Medium (4 steps, ~250 lines)
**Model:** Sonnet
**Restart required:** Yes (design-vet-agent.md + workflows-terminology.md fragment)
**Diagnostic review:** No (content edits informed by diagnostic findings)
**FRs addressed:** FR-4, FR-14, FR-15, FR-16, FR-19, FR-20

---

## Step 5.1: Create general-step reference material

**Objective**: Create general-patterns.md reference file and update anti-patterns.md and examples.md with general-step content.

**Prerequisites**:
- Read `agent-core/skills/runbook/references/` directory structure
- Read existing references/anti-patterns.md and references/examples.md (pattern understanding)
- plugin-dev:skill-development loaded (progressive disclosure guidance)

**Implementation**:

**Part A: Create general-patterns.md**

Create `agent-core/skills/runbook/references/general-patterns.md`:

1. **Granularity criteria**:
   - Atomic steps (single file, single concern, <100 lines changed)
   - Composable steps (multiple files, related changes, shared validation)
   - Complex steps (>100 lines, needs separate planning)

2. **Prerequisite validation patterns**:
   - Creation steps: must include "**Prerequisite:** Read [file:lines] — understand [behavior/flow]"
   - Transformation steps: self-contained recipe sufficient
   - Investigation gates: when to require codebase exploration before implementation

3. **Composable vs atomic guidelines**:
   - When to split: unrelated files, different validation criteria
   - When to merge: same file, sequential operations, shared success criteria

**Part B: Update anti-patterns.md**

Update `agent-core/skills/runbook/references/anti-patterns.md`:

1. **Add general-step anti-patterns section**:
   - Missing investigation prerequisites for creation steps
   - Vague success criteria ("analysis complete" vs "analysis has 6 sections with line numbers")
   - Success criteria checking structure when step should verify content/behavior
   - Steps without concrete Expected Outcome
   - Ambiguous Error Conditions
   - Referencing downstream consumers instead of upstream source (e.g., referencing an agent that applies criteria instead of the decision document that defines them — in bootstrapping pipelines, downstream consumers may not be updated yet)

**Part C: Update examples.md**

Update `agent-core/skills/runbook/references/examples.md`:

1. **Add complete general-step example**:
   - Show all fields: Objective, Prerequisite, Implementation, Expected Outcome, Error Conditions, Validation
   - Include both creation step (with prerequisite) and transformation step (self-contained)
   - Demonstrate concrete success criteria

**Expected Outcome**:
- general-patterns.md created with granularity criteria and prerequisite patterns
- anti-patterns.md has general-step anti-patterns section
- examples.md has complete general-step examples (creation + transformation)

**Error Conditions**:
- If patterns too abstract → add concrete heuristics and thresholds
- If anti-patterns lack corrections → add "correct pattern" for each anti-pattern
- If examples incomplete → verify all required fields present and filled

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review runbook references additions. Verify general-patterns.md has concrete granularity criteria and prerequisite patterns, anti-patterns.md general section has corrections, and examples.md has complete general-step examples with all required fields."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-5.1-skill-review.md

---

## Step 5.2: Add density checkpoint, repetition helper, and validation steps to design skill

**Objective**: Enhance design skill Phase C with density validation, helper extraction guidance, agent-name validation, and late-addition completeness check.

**Prerequisites**:
- Read `agent-core/skills/design/SKILL.md` Phase C section
- Read `agents/decisions/runbook-review.md` density axis (reference from Phase 2)

**Implementation**:

Update `agent-core/skills/design/SKILL.md` Phase C:

1. **Add density checkpoint to Phase C (FR-14)**:
   - **Placement**: After outline generation, before deliverables table
   - **Content**:
     - Flag too-granular phases: >8 items per phase, adjacent items <20 LOC delta
     - Flag too-coarse phases: single item handling >3 unrelated concerns
     - Recommend split or merge based on density analysis
   - **Heuristic**: items per phase × avg LOC per item should be 100-300 range

2. **Add repetition helper prescription (FR-15)**:
   - **Placement**: Within Phase C outline guidance or design principles
   - **Content**:
     - When >5 operations follow same pattern (e.g., "update field X in files A, B, C, D, E, F")
     - Recommend extracting helper function/script
     - Threshold: 5+ repetitions of same operation structure
   - **Note**: Reduces token cost and error rate in implementation

3. **Add agent-name validation step (FR-19)**:
   - **Placement**: Phase C validation checklist
   - **Content**:
     - Before finalizing design: Glob agent directories to verify all agent references resolve to actual files
     - Check: `agent-core/agents/`, `.claude/agents/`
     - If agent name doesn't exist: flag as design error (not implementation issue)
   - **Prevention**: Catches outline-review-agent vs runbook-outline-review-agent type errors

4. **Add late-addition completeness check (FR-19)**:
   - **Placement**: Phase C validation checklist (after agent-name validation)
   - **Content**:
     - Requirements added after outline review must trigger re-validation for:
       - Traceability: does new FR map to outline step?
       - Mechanism: does new FR specify concrete implementation approach?
     - If added post-outline without mechanism: flag for completion
   - **Grounding**: FR-18 added during design session bypassed outline-level validation

**Expected Outcome**: design skill Phase C has density checkpoint with LOC-based heuristics, repetition helper guidance with 5+ threshold, agent-name Glob validation, and late-addition re-validation protocol.

**Error Conditions**:
- If density heuristic unclear → add concrete LOC ranges and item count thresholds
- If helper threshold arbitrary → justify with token cost or error rate rationale
- If validation steps non-actionable → specify tools (Glob) and failure actions
- If late-addition check vague → specify what to re-validate and when

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review design skill Phase C additions. Verify density checkpoint has concrete heuristics, repetition helper has justified threshold, agent-name validation specifies Glob directories, and late-addition check is grounded in session finding with clear re-validation steps."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-5.2-skill-review.md

---

## Step 5.3: Add deliverable review to workflow terminology

**Objective**: Document deliverable review as post-orchestration workflow step in workflows-terminology.md.

**Prerequisites**:
- Read `agent-core/fragments/workflows-terminology.md` (current workflow route)
- Read `agents/decisions/deliverable-review.md` (context for deliverable identification)

**Implementation**:

Update `agent-core/fragments/workflows-terminology.md`:

1. **Add to implementation workflow route** (after orchestrate, before handoff):
   - Current: `/design` → `/runbook` → [plan-reviewer] → prepare-runbook.py → `/orchestrate` → [vet agent]
   - Updated: `/design` → `/runbook` → [plan-reviewer] → prepare-runbook.py → `/orchestrate` → [vet agent] → **[deliverable-review] (opus)**

2. **Add deliverable review description**:
   - **Trigger**: After orchestration complete, before final handoff
   - **Model**: Opus (architectural assessment)
   - **Scope**: Production artifacts requiring quality assessment
   - **Process**: Parallel opus agents partitioned by artifact type, consolidated findings
   - **Reference**: `/deliverable-review` skill for invocation

3. **Note optional nature**:
   - Required for: multi-artifact plans, novel implementations, architectural changes
   - Optional for: single-artifact plans, routine updates, well-tested patterns
   - User judgment determines applicability

**Expected Outcome**: workflows-terminology.md has deliverable review as documented workflow step with opus model requirement and optional-applicability guidance.

**Error Conditions**:
- If workflow route unclear → verify arrow notation and agent bracketing consistent
- If deliverable review description vague → specify opus requirement and parallel-agent pattern
- If optional-nature ambiguous → add concrete triggers for when required vs optional

**Validation**:
1. Commit changes
2. Delegate to vet-fix-agent: "Review workflows-terminology.md deliverable review addition. Verify workflow route updated with deliverable-review step, description specifies opus and parallel-agent pattern, and optional-nature guidance has concrete applicability criteria."
3. Read review report, grep for UNFIXABLE
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-5.3-vet-review.md

---

## Step 5.4: Add review criteria to design-vet-agent

**Objective**: Add cross-reference agent-name validation and mechanism-check criteria to design-vet-agent.

**Prerequisites**:
- Read `agent-core/agents/design-vet-agent.md` (current review criteria)
- Step 5.2 committed (design skill validation as parallel reference)

**Implementation**:

Update `agent-core/agents/design-vet-agent.md`:

1. **Add cross-reference criterion (FR-20)**:
   - **Placement**: Under completeness or verification section
   - **Content**:
     - Glob agent directories (`agent-core/agents/`, `.claude/agents/`) to verify all agent names referenced in design resolve to actual files
     - Check deliverables table, phase specifications, any prose mentioning "agent X"
     - Flag mismatches: agent referenced but doesn't exist, or name typo (e.g., outline-review-agent vs runbook-outline-review-agent)
   - **Grounding**: Design targeted wrong agent in current plan

2. **Add mechanism-check criterion (FR-20)**:
   - **Placement**: Under feasibility or clarity section
   - **Content**:
     - For each FR or deliverable specifying behavior change: verify concrete mechanism present
     - Red flags: "improve", "enhance", "better" without specifying how
     - Requirements: algorithm description, data structure choice, control flow change, or reference to existing pattern
     - Flag mechanism-free specifications that planner cannot implement
   - **Grounding**: FR-18 in current plan lacked implementation approach

**Expected Outcome**: design-vet-agent has cross-reference criterion with Glob-based validation and mechanism-check criterion flagging behavior-without-mechanism patterns.

**Error Conditions**:
- If cross-reference unclear → specify Glob patterns and what to verify
- If mechanism-check abstract → add concrete red flags and requirement examples
- If criteria placement disrupts flow → integrate within existing sections (completeness, feasibility)

**Validation**:
1. Commit changes
2. Delegate to agent-creator (plugin-dev): "Review design-vet-agent.md criteria additions. Verify cross-reference criterion specifies Glob directories and validation logic, mechanism-check has concrete red flags and mechanism requirements, and both are grounded in session findings."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-5.4-agent-review.md

---

**Phase 5 Checkpoint**:
1. All content edits complete (runbook references, design skill, workflows terminology, design-vet-agent)
2. Restart session required (design-vet-agent change + workflows-terminology.md fragment loaded via CLAUDE.md)
3. Proceed to Phase 6

---

### Phase 6: Cleanup + Feedback Requirement (type: general)

**Complexity:** Low (2 steps, ~50 lines)
**Model:** Sonnet
**Restart required:** No
**Diagnostic review:** No
**FRs addressed:** FR-6, FR-17

---

## Step 6.1: Delete Phase 1.4 from runbook skill

**Objective**: Remove obsolete Phase 1.4 (file size awareness) section from runbook skill, now redundant with outline-level enforcement from Phase 4.

**Prerequisites**:
- Read `agent-core/skills/runbook/SKILL.md` to locate Phase 1.4 section
- Step 4.1 committed (outline-level growth validation as replacement)

**Implementation**:

Update `agent-core/skills/runbook/SKILL.md`:

1. **Locate Phase 1.4 section**:
   - Section title: "Phase 1.4: File Size Awareness"
   - Content: convention for noting file sizes during item planning

2. **Delete entire section**:
   - Remove heading, content, examples
   - Update section references if Phase 1.4 mentioned elsewhere in skill
   - Update table of contents if present

3. **Verify no orphaned references**:
   - Grep runbook SKILL.md for "1.4", "file size awareness", "file growth" in Phase 1 context
   - Remove or update any cross-references

**Expected Outcome**: Phase 1.4 section deleted from runbook skill, no orphaned references remain, outline-level enforcement (from Phase 4) is now the mechanism.

**Error Conditions**:
- If section not found → verify current Phase 1.4 exists with Grep
- If orphaned references remain → update cross-references or table of contents
- If deletion breaks section numbering → phases are named, not strictly numbered (acceptable)

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review runbook skill Phase 1.4 deletion. Verify entire section removed, no orphaned references remain, and skill structure is intact."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-6.1-skill-review.md

---

## Step 6.2: Document execution-to-planning feedback requirement

**Objective**: Add execution-to-planning feedback requirement to orchestration-execution.md, documenting when local recovery is insufficient and global replanning is needed.

**Prerequisites**:
- Read `agents/decisions/orchestration-execution.md` (current execution patterns)
- Read `agents/decisions/workflow-core.md` (workflow context)

**Implementation**:

Update `agents/decisions/orchestration-execution.md`:

1. **Add new section**: "Execution-to-Planning Feedback" or integrate into existing error handling section

2. **Document three escalation tiers**:
   - **Item-level (UNFIXABLE)**: execution blocked by missing design decision → orchestrator stops, escalates to user
   - **Local recovery (refactor agent)**: implementation needs restructuring within same design → delegate to refactor agent, continue
   - **Global replanning (new)**: execution reveals design flaw requiring replanning → stop execution, return to planning phase

3. **Global replanning triggers**:
   - Design assumptions invalidated by implementation (e.g., "this API doesn't support X" when design assumed it did)
   - Scope creep detected during execution (multiple UNFIXABLE of same type indicating missing phase)
   - Runbook structure broken (dependency cycles, blocked items accumulating)
   - Test plan inadequate (coverage gaps discovered during implementation)

4. **Handoff to error-handling worktree**:
   - Note: FR-17 documents requirement only
   - Implementation: deferred to `wt/error-handling` worktree
   - That worktree will design concrete detection, escalation protocol, and replanning handoff

**Expected Outcome**: orchestration-execution.md has three-tier escalation model with global replanning triggers documented and implementation deferred to wt/error-handling.

**Error Conditions**:
- If tiers unclear → add concrete examples for each tier
- If global triggers vague → specify detection criteria or symptoms
- If handoff note missing → ensure FR-17 implementation deferral is explicit

**Validation**:
1. Commit changes
2. Delegate to vet-fix-agent: "Review orchestration-execution.md execution-to-planning feedback addition. Verify three escalation tiers are documented with distinctions, global replanning triggers are concrete, and implementation deferral to wt/error-handling is clear."
3. Read review report, grep for UNFIXABLE
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-6.2-vet-review.md

---

**Phase 6 Checkpoint**:
1. Final cleanup complete (Phase 1.4 deleted, execution feedback documented)
2. All 20 FRs implemented across 6 phases
3. No restart required (no agent/fragment loaded via CLAUDE.md changed)
4. Runbook execution complete

---

## Final Validation

After Phase 6 completion:

1. **Requirements coverage check**:
   - Verify all 20 FRs addressed (cross-reference requirements mapping table)
   - Confirm all deliverables created or updated per design

2. **Artifact quality check**:
   - All skills passed skill-reviewer
   - All agents passed agent-creator
   - All fragments/decisions passed vet-fix-agent
   - No unresolved UNFIXABLE issues

3. **Restart verification** (Phases 1, 3-5):
   - Phase 1: Agent frontmatter changes functional
   - Phase 3: vet-fix-agent + vet-requirement.md changes active
   - Phase 4: runbook-outline-review-agent changes active
   - Phase 5: design-vet-agent + workflows-terminology.md changes active

4. **Success criteria**: All 20 FRs implemented, all artifacts passing review, all restart-requiring changes verified.
