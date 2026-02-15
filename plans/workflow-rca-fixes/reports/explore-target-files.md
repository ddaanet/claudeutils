# Exploration Report: Target Files Structure

**Scope:** Analysis of 7 key files in design, planning, and vet workflow
**Date:** 2026-02-14
**Purpose:** Understand current structure before designing edits for workflow-rca-fixes

---

## Summary

The 7 files form a unified architecture for design → planning → execution workflows:
- **Decision files** (runbook-review.md, pipeline-contracts.md) define review heuristics and contracts
- **Skill files** (runbook, design) orchestrate multi-phase processes with clear gates and delegation
- **Agent files** (outline-review, vet-fix, plan-reviewer) implement automated review + fix workflows
- **Skills frontmatter** only used in plan-reviewer; lightweight mechanism for injecting skill content
- **Repeating patterns:** Fix-all policy, UNFIXABLE escalation, execution context requirement, file-based reporting

---

## File Details

### 1. agents/decisions/runbook-review.md (89 lines)

**Sections:**
- Review Axes (4 major detection patterns)
  - When Detecting Vacuous TDD Cycles
  - When Ordering Runbook Dependencies
  - When Evaluating Cycle Density
  - When Spacing Runbook Checkpoints
- Process (5 sequential steps)
- Sources (4 academic references)
- When Planning For File Growth (decision capsule: 2026-02-12)

**Key Content Patterns:**
- **Detection heuristics:** Each axis contains "when X then do Y" statements (3-5 per axis)
- **Evidence grounding:** All axes cite academic sources (links + authors)
- **Rationale format:** "Grounding:" explains why the pattern matters
- **Decision capsules:** Dated entries (2026-02-12) capture decision + anti-pattern + evidence
- **LLM failure mode coverage:** Explicit references to model-size scaling (13.6-31.7% wrong logical direction rate)

**Classification tables:** None (detection heuristics are prose-based)

**Lines per section:**
- Review Axes: 62 lines
- Process: 5 lines
- Sources: 5 lines
- File Growth decision: 9 lines

---

### 2. agents/decisions/pipeline-contracts.md (110 lines)

**Sections:**
- When Transformation Table (6-stage pipeline with defect types, review gates, review criteria)
- How To Review Delegation Scope Template (required/optional fields)
- When UNFIXABLE Escalation (fix-all pattern + escalation flow)
- When Phase Type Model (TDD vs general, per-phase type declarations)
- When Vet Escalation Calibration (decision capsule + 3 sub-decisions)
  - When Vet Flags Out-of-Scope Items
  - When Vet Receives Execution Context
  - When Vet-Fix-Agent Rejects Planning Artifacts
- When Expansion Reintroduces Defects (decision capsule)

**Key Content Patterns:**
- **Classification table (T1-T6):** 6-row transformation pipeline with required/optional fields
- **Contract template:** Required/optional fields for review delegation (5 required, 2 optional)
- **Decision capsules:** Dated (2026-02-12), include "Problem", "Evidence", "Anti-pattern", "Correct pattern", "Root cause"
- **Routing directives:** Which agent to use for which artifact type
- **Scope boundaries:** DEFERRED vs UNFIXABLE distinction (critical for escalation logic)

**Classification depth:**
- T1-T6 table with columns: Transformation, Input, Output, Defect Types, Review Gate, Review Criteria
- Each transformation has specific output artifact type and review agent assignment
- Gateway cascade: T1(design-vet-agent) → T2(outline-review-agent) → T3-4(plan-reviewer) → T5(prepare-runbook.py) → T6(vet-fix-agent)

**Embedded decision schemas:**
- UNFIXABLE vs DEFERRED distinction with examples (line 67: "Cycle 0.6 vet flagged session filtering as UNFIXABLE despite...")
- Vet escalation calibration pattern: "Agents treat uncertainty as escalation trigger rather than scanning existing patterns"

---

### 3. agent-core/skills/runbook/SKILL.md (821 lines)

**Frontmatter:**
```yaml
name: runbook
model: sonnet
allowed-tools: Task, Read, Write, Edit, Skill, Bash(mkdir:*, agent-core/bin/prepare-runbook.py, echo:*|pbcopy)
requires: Design document, CLAUDE.md
outputs: plans/<job-name>/runbook.md + prepare-runbook.py ready
user-invocable: true
```

**Section Breakdown:**
- Introductory context (17 lines)
- Per-Phase Type Model (19 lines) — declares type: tdd vs type: general
- When to Use (13 lines)
- **Three-Tier Assessment** (57 lines)
  - Tier 1: Direct Implementation
  - Tier 2: Lightweight Delegation
  - Tier 3: Full Runbook
- **Planning Process (Tier 3 Only)** (666 lines) — 13 sub-phases (0.5, 0.75, 0.85, 0.9, 0.95, 1, 1.4, 2, 2.5, 3, 4)
  - Phase 0.5: Discover Codebase Structure (29 lines)
  - Phase 0.75: Generate Runbook Outline (43 lines)
  - Phase 0.85: Consolidation Gate — Outline (35 lines)
  - Phase 0.9: Complexity Check Before Expansion (33 lines)
  - Phase 0.95: Outline Sufficiency Check (22 lines)
  - Phase 1: Phase-by-Phase Expansion (53 lines)
  - TDD Cycle Planning Guidance (104 lines) — embedded sub-section
  - Mandatory Conformance Validation (11 lines)
  - Phase 1.4: File Size Awareness (8 lines)
  - Phase 2: Assembly and Metadata (49 lines)
  - Phase 2.5: Consolidation Gate — Runbook (24 lines)
  - Phase 3: Final Holistic Review (23 lines)
  - Phase 4: Prepare Artifacts and Handoff (24 lines)
- Checkpoints (32 lines) — Light vs Full checkpoint tiers
- What NOT to Test (9 lines)
- Cycle/Step Ordering Guidance (13 lines)
- Common Pitfalls (20 lines)
- Runbook Template Structure (52 lines)
- References (6 lines)
- Integration (11 lines)

**Key Content Patterns:**
- **Phase-based organization:** 13 sequential phases with clear entry/exit criteria
- **Consolidation gates:** Explicit points to merge trivial phases/items (0.85, 2.5)
- **Callback mechanism:** Phase 0.9 describes feedback loop for over-large runbooks
- **Delegation pattern:** Uses Task tool with model/context specified
- **Review checkpoints:** Light (Fix + Functional) vs Full (Fix + Vet + Functional)
- **Template structure:** Shows expected runbook format with metadata sections
- **TDD-specific subsection:** 104-line embedded section with prose test quality rules and assertion validation

**Assertions validation rules:**
```
| Weak (vague) | Strong (specific) |
| "returns correct value" | "returns string containing 🥈 emoji" |
```

**File size awareness (lines 504-511):** Convention noted for proactive splits at 350-line threshold

---

### 4. agent-core/skills/design/SKILL.md (340 lines)

**Frontmatter:**
```yaml
description: Entry point for complexity triage (simple/moderate/complex) → routes work
allowed-tools: Task, Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
user-invocable: true
model: (implied sonnet from context, explicit mentions are recommendations)
```

**Section Breakdown:**
- Design Skill intro (9 lines)
- Downstream Consumer (3 lines)
- **Process (322 lines)**
  - Phase 0: Complexity Triage (7 lines)
    - Simple → Execute directly
    - Moderate → Skip design, route to /runbook
    - Complex → Proceed with A-C
  - **Phase A: Research + Outline (150 lines)**
    - A.0: Requirements Checkpoint (18 lines) — Skill dependency scanning
    - A.1: Documentation Checkpoint (17 lines) — 5-level hierarchy with flexibility
    - A.2: Explore Codebase (5 lines) — Delegate to quiet-explore
    - A.3-4: External Research (4 lines) — Context7 + WebSearch
    - A.5: Produce Plan Outline (18 lines)
    - A.6: FP-1 Checkpoint - Review Outline (17 lines)
  - **Phase B: Iterative Discussion (16 lines)**
    - Open outline, user feedback, designer applies deltas
    - 3-round convergence guidance
  - **Phase C: Generate Design (142 lines)**
    - C.1: Create Design Document (77 lines)
      - Dense output principle
      - Classification tables as binding constraints
      - Requirements section with FR/NFR traceability
      - Documentation Perimeter section
      - Skill-loading directives (plugin-dev:*)
      - Execution model directives
    - C.2: Checkpoint Commit (5 lines)
    - C.3: Vet Design (8 lines) — Delegate to design-vet-agent
    - C.4: Check for Unfixable Issues (7 lines)
    - C.5: Handoff and Commit (7 lines) — `/handoff --commit`
- Output Expectations (10 lines)
- Constraints (3 lines)

**Key Content Patterns:**
- **Triage gates:** 3-tier decision tree (simple/moderate/complex)
- **Documentation hierarchy:** 5-level fallback system (local→skills→Context7→explore→web)
- **Skill dependencies:** Explicit indicators for agent/skill/hook/plugin creation
- **Classification tables marked as binding:** Planners must pass through verbatim
- **Documentation Perimeter:** Designer specifies required reading for planner
- **Skill-loading directives:** Explicit pre-planning skill setup (e.g., "Load plugin-dev:hook-development before planning")
- **Execution model directives:** Opus required for workflow/skill/agent edits
- **Handoff tail-call:** `/handoff --commit` chains to `/commit` which displays next task

**A.1 Documentation Checkpoint flexibility:**
- Level 1: Local knowledge (memory-index, decisions, fragments)
- Level 2: Skills (plugin-dev:*)
- Level 3: Context7 (library documentation)
- Level 4: Explore (quiet-explore agent)
- Level 5: Web (WebSearch/WebFetch)
- Note: "Not all levels needed for every task"

---

### 5. agent-core/agents/outline-review-agent.md (347 lines)

**Frontmatter:**
```yaml
name: outline-review-agent
description: Reviews design outlines post-Phase A.5, validates soundness/completeness/feasibility
model: sonnet
color: cyan
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
```

**Section Breakdown:**
- Role (4 lines) — Review + fix-all + escalate unfixable
- **Review Protocol (321 lines)**
  - 1. Validate Inputs (17 lines) — Check requirements exist, artifact is outline.md
  - 2. Load Context (6 lines) — Read requirements, outline, exploration reports
  - 3. Review Criteria (34 lines) — 6 dimensions
    - Soundness (4 criteria)
    - Completeness (4 criteria)
    - Scope (4 criteria)
    - Feasibility (4 criteria)
    - Clarity (5 criteria)
    - Requirements Traceability (3 criteria)
  - 4. Traceability Matrix (20 lines) — FR/NFR mapping with coverage assessment
  - 5. Apply Fixes (19 lines) — Fix-all policy with constraints
  - 6. Write Review Report (73 lines) — Structured report format
  - 7. Return Result (16 lines) — Filepath or error format
- Critical Constraints (11 lines)
- Edge Cases (20 lines)
- Verification (6 lines)
- Response Protocol (9 lines)

**Key Content Patterns:**
- **Input validation errors:** Structured error format with Details, Context, Recommendation
- **6-dimension review matrix:** Each dimension has 3-5 criteria (explicit list format)
- **Traceability matrix format:** Requirement | Outline Section | Coverage | Notes
- **Coverage assessment labels:** Complete / Partial / Missing
- **Fix-all rationale:** "Document review is low-risk. Unlike code changes, outline fixes have no unintended side effects."
- **Fix constraints:** Preserve intent/voice, don't expand scope, note new decisions
- **Assessment criteria:** 3-level scale (Ready / Needs Iteration / Needs Rework)
- **Error format:** Structured with 4 fields (Error, Details, Context, Recommendation)

**Traceability focus:**
- Maps FR-* to outline sections
- Coverage assessment drives fixes (missing → add placeholders with TODOs)
- Explicit references required (FR-1 → Section X)

---

### 6. agent-core/agents/vet-fix-agent.md (437 lines)

**Frontmatter:**
```yaml
name: vet-fix-agent
description: Code review agent that applies all fixes directly. Review + write report + fix + return filepath.
model: sonnet
color: cyan
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "AskUserQuestion"]
```

**Section Breakdown:**
- Role (6 lines) — Review implementation changes (not planning/design)
- **Review Protocol (387 lines)**
  - 0. Validate Task Scope (34 lines) — Rejects runbooks, design docs; requires requirements context
  - 1. Determine Scope (11 lines) — Ask user via AskUserQuestion if not provided
  - 2. Gather Changes (27 lines) — Git commands for different scope types
  - 3. Analyze Changes (64 lines) — 11 analysis dimensions
    - Code Quality (11 items)
    - Project Standards (5 items)
    - Security (4 items)
    - Testing (6 items)
    - Documentation (3 items)
    - Completeness (3 items)
    - Requirements Validation (2 items)
    - Design Anchoring (4 items)
    - Alignment (3 items)
    - Integration Review (4 items)
    - Runbook file references (5 items)
    - Self-referential modification (3 items)
  - 4. Write Review Report (55 lines) — Structured report with sections
  - 5. Apply Fixes (25 lines) — Fix ALL issues, update report with status
  - 6. Return Result (11 lines) — Filepath or error
- Critical Constraints (9 lines)
- Edge Cases (16 lines)
- Verification (6 lines)
- Response Protocol (9 lines)

**Key Content Patterns:**
- **Task scope validation:** Rejects planning artifacts (runbooks) and design docs
- **Execution context requirement:** IN/OUT scope, changed files, prior state, design reference
- **Scope determination:** Uses AskUserQuestion tool with 5 preset options
- **Analysis dimensions:** 12 major categories with 3-11 sub-criteria each
- **Status labels:** FIXED / DEFERRED / UNFIXABLE (DEFERRED if in OUT scope or documented future work)
- **DEFERRED vs UNFIXABLE:** Distinction is explicit (scope is not technical blocker)
- **Deslop rules:** Mentioned in Code Quality section (no trivial docstrings, narration comments, section banners, premature abstractions)
- **Self-referential check:** Flags steps that mutate own plan directory (creates ordering dependency)
- **Runbook file reference check:** Glob to verify paths, Grep to verify function names

**Analysis depth:**
- 64 lines of explicit review criteria organized by domain
- Special handling for runbooks vs code (file reference validation, self-referential modification)
- Requirements validation requires context provided in task

---

### 7. agent-core/agents/plan-reviewer.md (183 lines)

**Frontmatter:**
```yaml
name: plan-reviewer
description: Reviews runbook phase files for TDD/general quality and LLM failure modes
model: sonnet
color: yellow
tools: ["Read", "Grep", "Glob", "Write", "Edit", "Skill"]
skills:
  - review-plan
```

**Section Breakdown:**
- Role (8 lines) — Review runbooks, write audit trail, fix all, escalate unfixable
- Agent Purpose (9 lines) — 3 functions (audit trail, autofix, escalation)
- Document Validation (10 lines) — Accepts TDD/general/mixed; rejects design/code
- Outline Validation (8 lines) — Checks for prior outline review; skips for phase files
- Requirements Inheritance (6 lines) — Inherits requirements from outline
- Review Criteria (19 lines) — Delegates to review-plan skill
  - TDD phases (4 criteria)
  - General phases (4 criteria)
  - All phases (4 LLM failure modes)
  - Prose quality rule
- Fix-All Policy (15 lines) — Fix all issues, constrain scope, escalate UNFIXABLE
- Standard Workflow (8 lines) — 7 sequential steps
- Report Structure (32 lines) — Template with sections
- Return Protocol (21 lines) — Success/success-with-escalation/failure formats

**Key Content Patterns:**
- **Skills frontmatter usage:** Single skill injection (review-plan) for reusable review logic
- **Phase type detection:** Auto-detects from headers (`## Cycle` vs `## Step`)
- **Outline review check:** Warning if prior review missing (except for phase files)
- **Delegation to skill:** Offloads detailed analysis to review-plan skill
- **LLM failure modes:** 4 categories (vacuity, dependency ordering, density, checkpoint spacing)
- **Prose quality rule:** "If executor could write different tests satisfying prose, it's too vague"
- **UNFIXABLE criteria:** Missing requirements in design, structure problems, cross-phase dependencies, scope conflicts
- **Return protocol:** Filepath on success; filepath + ESCALATION note if unfixable issues; error format for failures

**Skills frontmatter:**
```yaml
skills:
  - review-plan
```
Only usage of `skills:` field across all 7 files. Pattern: lightweight skill injection for reusable multi-phase logic.

---

## Cross-File Patterns

### 1. Fix-All Policy (Universal)

**Stated in:** outline-review-agent, vet-fix-agent, plan-reviewer

**Pattern:**
- All issues (critical, major, minor) are fixed automatically
- No triage or filtering by priority
- Rationale: Low-risk changes + early remediation prevents drift
- Status tracking: FIXED / DEFERRED / UNFIXABLE

**Variance by context:**
- Outline/design reviews: "Document review is low-risk"
- Code reviews: Constrained to minimal, targeted fixes
- Runbooks: Preserve intent, don't expand scope

### 2. Escalation Protocol (Universal)

**Pattern:**
- UNFIXABLE issues are documented and escalated
- Caller greps for UNFIXABLE in report
- DEFERRED vs UNFIXABLE distinction (explicit scope vs technical blocker)
- Three status labels used consistently (FIXED / DEFERRED / UNFIXABLE)

**File examples:**
- pipeline-contracts.md: UNFIXABLE escalation description (lines 30-36)
- vet-fix-agent.md: DEFERRED example at line 331-334
- plan-reviewer.md: UNFIXABLE criteria at lines 103-107

### 3. Execution Context Requirement

**Stated in:**
- pipeline-contracts.md (When Vet Receives Execution Context, lines 75-85)
- vet-fix-agent.md (Section 0, lines 68-85)

**Fields required:**
- Scope IN: What was implemented
- Scope OUT: What is NOT yet done (prevents false positives)
- Changed files: Explicit list
- Requirements: Summary of what output should satisfy
- **Optional:** Prior state, design reference

**Purpose:** Prevents reviewing against stale filesystem state, prevents confabulating issues from future phases

### 4. File-Based Reporting (Universal)

**Pattern:**
- All agents write reports to file
- Return filepath only (no summary in return message)
- Report contains audit trail + issue listing + fixes applied
- Locations: `plans/[plan]/reports/[review-type].md` or `tmp/[timestamp].md`

**Report structure components (consistent across agents):**
- Summary (2-3 sentences)
- Overall Assessment (categorical)
- Issues Found (Critical/Major/Minor with Status)
- Fixes Applied (change list)
- Assessment-specific sections (Traceability, Requirements, Recommendations)
- Verification/Positive Observations

### 5. Task Scope Validation (Outline, Design, Vet)

**Pattern:**
- Each agent validates it received correct artifact type
- Structured error format: Error | Details | Context | Recommendation
- Rejects wrong types (outline-review rejects design.md, vet-fix rejects runbooks)

**Error format (consistent):**
```
Error: [What failed]
Details: [Error message or diagnostic info]
Context: [What was being attempted]
Recommendation: [What to do]
```

### 6. Type-Aware Review (plan-reviewer specific)

**Pattern:**
- TDD phases: RED/GREEN discipline, prescriptive code detection, cycle sequencing
- General phases: Prerequisite validation, step clarity, script evaluation sizing
- All phases: LLM failure modes (vacuity, ordering, density, checkpoints)

**Type detection:** Auto-detects from headers (`## Cycle` vs `## Step`)

### 7. Traceability & Mapping

**Locations:**
- outline-review-agent: Traceability matrix (FR-* → outline section)
- vet-fix-agent: Requirements validation table (FR-* → file:line + evidence)
- plan-reviewer: Requirements inheritance from outline

**Pattern:** Explicit mapping with coverage assessment (Complete/Partial/Missing/Satisfied)

### 8. Callback/Gate Mechanisms

**Locations:**
- runbook skill Phase 0.9: Complexity check with callback levels
- runbook skill Phase 0.85, 2.5: Consolidation gates (merge trivial phases/items)
- design skill: 3-tier assessment (simple/moderate/complex)

**Levels:** item → outline → design → outline → requirements

### 9. Decision Capsules

**Used in:**
- runbook-review.md: "When Planning For File Growth" (2026-02-12)
- pipeline-contracts.md: "When Vet Escalation Calibration" + 3 sub-decisions (2026-02-12)

**Structure:** Decision Date | Problem | Evidence | Anti-pattern | Correct pattern | Root cause

---

## Skills Frontmatter Usage

**Only instance:** plan-reviewer.md lines 17-18
```yaml
skills:
  - review-plan
```

**Pattern:**
- Single skill injection
- Agent file declares which skill to load
- Skill provides detailed analysis logic (reusable across phases)
- Agent orchestrates: validation → skill delegation → report writing → fix application

**Not used in:**
- outline-review-agent (direct review logic embedded)
- vet-fix-agent (direct review logic embedded)
- design skill (delegates to sub-agents via Task, not skills frontmatter)
- runbook skill (delegates to sub-agents via Task, not skills frontmatter)

---

## Content Density & Organization

### File Size Summary
| File | Lines | Sections | Subsections |
|------|-------|----------|-------------|
| runbook-review.md | 89 | 4 | 7 (4 detection patterns) |
| pipeline-contracts.md | 110 | 6 | 13 (3 sub-decisions in one) |
| runbook/SKILL.md | 821 | 13 | 80+ (deeply nested) |
| design/SKILL.md | 340 | 2 | 20+ (A/B/C phases + sub-phases) |
| outline-review-agent.md | 347 | 8 | 30+ (review protocol with 7 sub-steps) |
| vet-fix-agent.md | 437 | 9 | 40+ (review protocol with 6 major steps) |
| plan-reviewer.md | 183 | 9 | 18+ (standard workflow) |

### Nesting Depth
- **Runbook skill:** 13 main phases (0.5, 0.75, 0.85, 0.9, 0.95, 1, 1.4, 2, 2.5, 3, 4); Phase 1 contains TDD Cycle Planning Guidance subsection (104 lines)
- **Design skill:** 3 phases (A/B/C); Phase A has 6 sub-steps (A.0-A.6); Phase C has 5 sub-steps (C.1-C.5)
- **Review protocols:** 6-7 sequential steps with detailed sub-bullets under each

---

## Gaps & Observations

### Existing Strengths
1. **Consistent escalation model:** UNFIXABLE detection via grep, DEFERRED for scoped items
2. **Clear role separation:** Outline review (completeness), design vet (feasibility), runbook review (TDD/LLM modes), code vet (implementation)
3. **Skill frontmatter mechanism:** Lightweight, native injection (plan-reviewer uses it effectively)
4. **Explicit type tagging:** Per-phase TDD vs general declarations reduce ambiguity
5. **Academic grounding:** runbook-review.md cites research on LLM failure modes

### Notable Gaps
1. **Execution context requirement documented but not enforced:** vet-fix-agent has optional field handling (Section 0), no validation logic
2. **Phase type detection** in runbook skill (Phase 0.75) requires outline markup; plan-reviewer auto-detects but skill does not validate
3. **Prose assertion quality rule** in plan-reviewer (line 85) is single sentence; no detailed guidance on what makes vague vs strong
4. **Skill-loading directives** in design skill (C.1) specify which skills but no guidance on when to defer vs front-load
5. **Memory index integration** mentioned in runbook skill Phase 0.5 but no mechanism shown (agent can't invoke `/when` or `/how`)

### Opportunity Areas (for FR Design)
1. **Detection heuristic unification:** runbook-review.md patterns (vacuity, ordering, density, checkpoints) could be formalized as reusable checks
2. **Execution context enforcement:** Could be a pre-step validation in review agents (currently optional)
3. **Type awareness in design:** design skill doesn't guide planners on when to declare TDD vs general for each phase
4. **Skill composition:** Multiple agents use similar review structure (outline/design/runbook/code) — common skill could reduce duplication
5. **Fragment-as-skill pattern:** Current fragments (error-handling, vet-requirement, deslop) are injected via CLAUDE.md; could be skills for better component boundaries

---

## Patterns Ready for Extraction/Formalization

### 1. Review-Plan Skill (Partial Extraction Opportunity)
- **Current:** Only plan-reviewer uses `skills: [review-plan]`
- **Pattern:** Type-aware review (TDD vs general) + LLM failure mode checks
- **Potential:** All runbook reviews (outline, phases, full) could share this
- **Cost:** Skill creation effort vs token savings from reuse

### 2. Fix-All Decision Framework
- **Locations:** 3 agents (outline, vet, plan-reviewer)
- **Pattern:** Consistent justification + status labels
- **Potential:** Could be a shared decision rule in agents/decisions/

### 3. Execution Context Validation
- **Current:** Documented but not enforced
- **Pattern:** Pre-step check for IN/OUT scope, changed files list
- **Potential:** Reusable validation component for phased work

### 4. Traceability Matrix Generation
- **Current:** outline-review-agent and vet-fix-agent both build requirement-to-artifact mappings
- **Pattern:** Explicit table with Coverage assessment column
- **Potential:** Shared template or skill for consistency

### 5. Error Reporting Format
- **Current:** Consistent across outline, vet, plan-reviewer (Error | Details | Context | Recommendation)
- **Pattern:** Structured 4-field format
- **Potential:** Could be a shell template or shared convention doc

---

## Recommendation for Workflow-RCA-Fixes

**Target files have clear architectural boundaries:**
1. **Decision files** (runbook-review, pipeline-contracts) — Define heuristics and contracts
2. **Skills** (runbook, design) — Orchestrate multi-phase workflows
3. **Agents** (outline-review, vet-fix, plan-reviewer) — Implement automated review + fix

**For FR implementation:**
- FR-1-11 (prose edits): Update decision files + skills sequentially
- FR-12/13 (agent composition): New skill files + agent frontmatter updates
- FR-14/15 (design skill fixes): Direct edits to design skill phases
- FR-16 (deliverable review): New agent file + integration into design skill
- FR-17 (execution feedback): Links to error-handling design, implementation deferred

**No conflicts detected** between target files. Changes to one layer (e.g., decision files) won't require rewrites of agent implementations if new decisions are backward-compatible with existing escalation/reporting patterns.
