# Workflow Pipeline Redesign: Outline

Supersedes previous outline (10 artifact patches). Scope expanded to complete pipeline analysis after identifying structural gaps that patches can't fix.

## Problem

The design-to-deliverable pipeline has structural gaps that allow LLM antipatterns past review gates. Previous approach patched individual artifacts; this session found that the gaps are architectural: wrong agent routing, broken recommendation propagation, missing review criteria at expansion stage, and contradictory autofix instructions.

**Pipeline stages:** `/design` → `/plan-{tdd,adhoc}` → `/orchestrate` → deliverable

Each stage is a transformation that can introduce defects. Each transformation needs a review gate that checks for the specific defects it can introduce. The current pipeline has review gates, but they're inconsistently applied, route to wrong agents, and don't re-validate after the most error-prone transformation (outline → phase expansion).

## Pipeline Analysis: Current State

### Transformation Table

| # | Transformation | Defect Type | Current Gate | Gap |
|---|---------------|-------------|-------------|-----|
| T1 | Requirements → Design | Incomplete, infeasible | design-vet-agent (opus) | None — works |
| T2 | Design → Outline | Missing reqs, wrong decomposition | runbook-outline-review-agent | None — has LLM failure mode checks |
| T3 | Outline → Phase files | **Vacuity re-introduction, prescriptive code, density bloat** | **TDD: tdd-plan-reviewer (TDD discipline only) / Adhoc: vet-fix-agent (REJECTS planning artifacts)** | **G1 G2 G3 G6** |
| T4 | Phase files → Runbook | Cross-phase inconsistency | TDD: tdd-plan-reviewer (holistic) / Adhoc: vet-agent (review-only) | **G2 G4** |
| T5 | Runbook → Step artifacts | Generation errors | prepare-runbook.py | None — automated |
| T6 | Steps → Implementation | Wrong behavior, stubs, drift | vet-fix-agent (checkpoints) | Minor (G7) |

**T3 is the critical gap.** Phase expansion is the most error-prone transformation — the LLM must elaborate outline entries into detailed steps/cycles. Outline review catches vacuity and ordering, but expansion can re-introduce them. The post-expansion review gate is either missing criteria (TDD) or routing to the wrong agent (adhoc).

### Gap Inventory

**G1: Adhoc phase review routes to wrong agent**
- plan-adhoc Point 1 delegates to `vet-fix-agent`
- vet-fix-agent explicitly rejects planning artifacts: "Error: Wrong agent type... This agent reviews implementation changes, not planning artifacts"
- Result: Either error or silent misroute

**G2: Autofix contradiction in plan-adhoc**
- Point 1 step 2: "Delegate to vet-fix-agent (fix-all mode) — Agent applies all fixes"
- Point 1 step 3: "Apply all fixes from vet review — Update phase file with fixes"
- Planner re-applies fixes the agent already applied. Contradicts autofix principle.
- Same pattern at Point 3: uses review-only vet-agent, then says "REQUIRED: Apply all fixes" in the delegation prompt — vet-agent has no Edit tool

**G3: No LLM failure mode re-validation after expansion**
- runbook-outline-review-agent checks: vacuity, ordering, density, checkpoints (lines 116-137)
- tdd-plan-reviewer checks: prescriptive code, RED/GREEN sequencing, prose quality
- **Missing:** LLM failure mode re-validation at phase level. Evidence: worktree-update had 3 vacuous cycles, 1 missing requirement post-expansion, 0 caught by phase review.
- plan-adhoc has NO failure mode checks at phase level at all

**G4: Recommendation propagation dead-ends**
- Expansion Guidance (inline in outline) → consumed by planner. Works.
- tdd-plan-reviewer report "Recommendations" → NOT consumed by anyone
- vet-agent report "Recommendations" → NOT consumed by anyone
- Pattern: only inline recommendations propagate; report recommendations are write-only

**G5: Agent name ambiguity**
- plan-adhoc uses "vet agent" without specifying which. Point 1 says vet-fix-agent, Point 3 says vet-agent. Different agents, different behavior (fix vs review-only).

**G6: Missing alignment context in review delegations**
- Phase review delegations lack scope IN/OUT per vet-requirement.md
- tdd-plan-reviewer gets no execution context
- Without scope boundaries, reviewer may flag future-phase items as missing

**G7: Orchestrate general completion doesn't vet**
- TDD path: delegates to vet-fix-agent + review-tdd-process. Complete.
- General path: "Suggest next action: delegate to vet-fix-agent" — suggests but doesn't do it

## Proposed Changes

### Decision 1: Phase-level review agent for adhoc

**Options:**
- **A) Extend tdd-plan-reviewer → plan-reviewer (handles both TDD + adhoc)** — rename agent + skill, add adhoc step-quality criteria alongside TDD criteria, conditional on artifact type. Single maintenance surface.
- **B) Use vet-agent (review-only) + planner applies fixes** — matches Tier 1/2 pattern (caller has context). No new agents. But: No LLM failure mode checks, no autofix.
- **C) Create adhoc-plan-reviewer** — new agent, loads LLM failure mode criteria from runbook-review.md. Clean separation. But: agent proliferation, duplicated LLM criteria.

Recommendation: **A**. Fewest new artifacts. review-tdd-plan skill already has fix-all pattern. LLM failure mode criteria go in the skill (applicable to both). TDD-specific criteria conditional on `type: tdd`.

### Decision 2: LLM failure mode criteria location

- **A) In review-plan skill (unified)** — single source, loaded by plan-reviewer agent
- **B) Separate skill (review-plan-llm-modes)** — reusable by multiple agents, separation of concerns
- **C) Reference runbook-review.md directly** — agents read the decision doc at review time

Recommendation: **A**. The criteria are tightly coupled with review — separation adds indirection without reuse benefit. runbook-outline-review-agent has its own copy (acceptable: different agent, different application stage).

### Decision 3: Recommendation propagation

For phase-level review recommendations that should influence the next phase or final review:
- **A) Inline in phase file** (like Expansion Guidance pattern) — proven, consumed automatically
- **B) Explicit "read report" step** in skill — fragile, depends on planner compliance
- **C) Drop** — phase review fixes issues directly; recommendations that can't be fixed are UNFIXABLE escalations

Recommendation: **C**. If the reviewer can fix it, fix it. If it can't fix it, escalate. Recommendations-as-suggestions is the gap that created G4. The fix-all pattern eliminates the need for recommendation propagation.

## Fixes by Pipeline Stage

### Stage: /design
- Add `agents/decisions/runbook-review.md` to Documentation Perimeter for tasks producing runbooks
- No structural changes

### Stage: /plan-adhoc
- **Point 1 (phase review):** Replace vet-fix-agent with plan-reviewer agent. Remove manual fix step. Add scope IN/OUT context to delegation. Add LLM failure mode directive.
- **Point 3 (final review):** Replace vet-agent with plan-reviewer for holistic review with autofix. Remove manual fix loop (agent fixes directly).
- **Throughout:** Replace ambiguous "vet agent" with explicit agent names

### Stage: /plan-tdd
- **Phase 3 (per-phase review):** Add LLM failure mode criteria (NEW: vacuity, ordering, density, checkpoints) to plan-reviewer delegation alongside existing TDD-specific checks (prescriptive code, RED/GREEN sequencing). Both sets checked together for TDD artifacts.
- **Phase 5 (holistic review):** Same — add LLM failure mode re-validation

### Stage: /orchestrate
- **Completion (adhoc):** Change suggestion to actual delegation to vet-fix-agent (match TDD path behavior)

### Supporting artifacts
- **review-tdd-plan skill → review-plan skill:** Add LLM failure mode section (four axes from runbook-review.md: vacuity, ordering, density, checkpoints). Add adhoc step-quality section (prerequisite validation, script evaluation, clarity). TDD criteria conditional on `type: tdd`.
- **tdd-plan-reviewer agent → plan-reviewer agent:** Update name, update description, update document validation to accept both TDD and adhoc artifacts
- **vet skill (/vet):** Add execution context section, UNFIXABLE handling guidance, cross-reference vet-requirement.md
- **vet-fix-agent:** Add UNFIXABLE format to return protocol. TODO: Specify UNFIXABLE format (match plan-reviewer pattern: dedicated section in report with issue title + blocker reason). Cross-reference vet-requirement.md UNFIXABLE Detection Protocol for escalation criteria.

### Deferred (separate tasks, unchanged)
- Skills prolog / agent-skill restructuring
- Plugin-dev upstream contributions
- Design skill internal updates
- Vet agent duplication extraction

## Scope

**IN:**
- Pipeline analysis and gap fixes (G1-G7)
- Agent rename: tdd-plan-reviewer → plan-reviewer, review-tdd-plan → review-plan
- LLM failure mode integration into plan-level review skill
- Adhoc step-quality criteria in review skill
- plan-adhoc agent routing and autofix fixes
- plan-tdd LLM failure mode additions
- orchestrate adhoc completion fix
- vet skill context guidance
- vet-fix-agent UNFIXABLE format
- Reference updates for agent rename (plan-adhoc, plan-tdd, orchestrate, prepare-runbook.py)
- Symlink synchronization (just sync-to-parent)

**OUT:**
- prepare-runbook.py (works correctly)
- Skills prolog restructuring
- Plugin-dev upstream contributions
- Design skill changes
- worktree-update runbook fixes
- New agent creation (extending existing)

## Open Questions

1. Agent rename scope: renaming tdd-plan-reviewer → plan-reviewer requires updating all references (plan-tdd, plan-adhoc, orchestrate, symlinks, prepare-runbook.py baseline detection). Is this acceptable churn, or should we keep the name and broaden scope?

2. plan-adhoc is 1136 lines. The fixes are surgical (Point 1, Point 3, agent references). Should the design specify exact edit locations, or describe the semantic change and let the planner find them?

3. Should the I/O contracts from the transformation table be embedded in each skill (as a reference section), or remain in a central decision document?

## Mode

Adhoc workflow (not TDD). This work modifies skill/agent definitions and planning artifacts — no behavioral tests needed. Downstream: `/plan-adhoc` for runbook creation.

Execution model: opus for skill/agent definition edits (architectural artifacts), sonnet for planning.
