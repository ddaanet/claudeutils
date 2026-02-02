# Plan Skill Fast Paths

**Problem:** Both `/plan-adhoc` and `/plan-tdd` route all work through the full runbook pipeline (4-point process or 5-phase execution). The direct implementation path exists in Point 0 of plan-adhoc but is buried and underdeveloped. Plan-tdd has no equivalent. The commit-rca-fixes job demonstrated the fast path successfully but it required the agent to improvise — no formalized pattern guided it.

**Mode:** General (skill updates, no new infrastructure)
**Downstream:** `/plan-adhoc` (implements changes to both skills)

---

## Requirements

### Functional

- Both plan skills offer explicit fast paths when runbook overhead isn't justified
- Assessment criteria are concrete and consistent between skills
- Fast paths include vet review (not skipped)
- The "implement directly" path has a clear sequence: assess → implement → vet → fix → commit
- Lightweight delegation path surfaces quiet-task/tdd-task as middle ground
- Assessment produces explicit output (not just internal reasoning)

### Non-Functional

- No new skills, scripts, or agents — edits to existing skill files only
- Fast paths must not break existing runbook pipeline (additive, not replacement)
- Consistent structure between plan-adhoc and plan-tdd (same assessment framework, adapted for each methodology)
- "When to Use" / "Do NOT use when" guards updated to not reject simple tasks (tier assessment handles routing)

### Out of Scope

- Lightweight delegation tier as a separate workflow (pending task — this design only surfaces it as an option within plan skills)
- Changes to prepare-runbook.py
- Changes to orchestrate skill
- Changes to `/oneshot` skill routing logic

---

## Design

### Three-Tier Assessment (replaces Point 0)

Both skills get a unified assessment framework with three tiers. Assessment runs first, before any other work.

**Tier 1: Direct Implementation**
- Design complete (no open decisions)
- All edits straightforward (<100 lines each)
- Total scope: <6 files
- Single session, single model
- No parallelization benefit

**Sequence:** Implement directly → `/vet` → apply fixes → `/commit` (no handoff needed — no session restart required)

**Tier 2: Lightweight Delegation**
- Design complete, scope moderate (6-15 files or 2-4 logical components)
- Work benefits from agent isolation (context management) but not full orchestration
- Components are sequential (no parallelization benefit)
- No model switching needed

**Sequence:** Write step descriptions (not full runbook) → delegate each via Task tool (`subagent_type="quiet-task"` or `"tdd-task"`, `model="haiku"`) with relevant context in prompt → vet → commit

**Key distinction from Tier 3:** No prepare-runbook.py, no orchestrator plan, no plan-specific agent. The planner acts as ad-hoc orchestrator, delegating directly via Task tool. Each delegation prompt must include relevant context that would otherwise come from Common Context (file paths, design decisions, conventions).

**Tier 3: Full Runbook**
- Multiple independent steps (parallelizable)
- Steps need different models
- Long-running / multi-session execution
- Complex error recovery
- >15 files or complex coordination

**Sequence:** 4-point process (plan-adhoc) or 5-phase execution (plan-tdd) — existing pipeline unchanged.

### Assessment Output Format

The assessment must be explicit (not just internal reasoning). Format:

```
**Tier Assessment:**
- Files affected: ~N
- Open decisions: none / [list]
- Components: N (sequential / parallel / mixed)
- Model requirements: single / multiple
- Session span: single / multi

**Tier: [1/2/3] — [Direct Implementation / Lightweight Delegation / Full Runbook]**
**Rationale:** [1-2 sentences]
```

When uncertain between tiers, prefer the lower tier (less overhead). Ask user only if genuinely ambiguous.

### Plan-Adhoc Changes

**Update "When to Use" / "Do NOT use when" guards:** Remove "Task is simple and can be executed directly" from "Do NOT use when." The skill is now invoked for all tasks that have a design document; tier assessment handles routing. Simple tasks that need no design at all are handled by `/oneshot` before reaching `/plan-adhoc`.

**Replace Point 0** with three-tier assessment. The current "Implement Directly If" / "Create Runbook If" / "When Uncertain" structure becomes Tier 1/2/3.

**Add Tier 1 sequence** after assessment (new section). Currently Example 1 shows it but no procedural section describes it:
- Implement changes directly using Read/Write/Edit tools
- Invoke `/vet` for review
- Apply high/medium fixes
- Invoke `/commit` directly (no `/handoff` needed — Tier 1 doesn't require session restart)

**Add Tier 2 sequence** (new section):
- Break work into 2-4 logical components
- For each component: delegate via `Task(subagent_type="quiet-task", model="haiku", prompt="...")` with context from design (file paths, decisions, conventions) included in prompt
- After all components complete: invoke `/vet`
- Apply fixes, `/commit`

**Rename "4-Point Planning Process" section** to clarify it's Tier 3 only. Add guard: "Use this process only after assessment determines Tier 3."

The existing Point 0.5 through Point 4 remain unchanged — they're already the Tier 3 pipeline.

### Plan-TDD Changes

**Update "When to Use" / "Do NOT use when" guards:** Remove "Feature is simple without TDD overhead" from "Do NOT use when." Same rationale as plan-adhoc — tier assessment handles routing once invoked.

**Add Phase 0: Tier Assessment** before Phase 1 (Intake). Currently plan-tdd assumes full runbook is always needed.

Same three-tier framework, but with TDD-specific criteria. Phase 0 performs a rough cycle estimate by scanning the design's requirements/phases sections — counting major behavioral increments without the full decomposition of Phase 2-3.

- **Tier 1 (Direct TDD):** ~1-3 cycles estimated, single test file, single source file. Agent writes RED/GREEN inline.
- **Tier 2 (Lightweight TDD):** ~4-10 cycles estimated, 2-3 test files. Delegate individual cycles via Task tool to tdd-task agent.
- **Tier 3 (Full Runbook):** >10 cycles estimated, multiple phases, cross-component dependencies. Proceed to existing Phase 1-5.

**Tier 1 TDD sequence:**
- Write tests and implementation directly (RED/GREEN discipline still applies)
- Invoke `/vet`
- Apply fixes, `/commit`

**Tier 2 TDD sequence:**
- Plan cycle descriptions (lightweight — no full runbook format)
- For each cycle: delegate via `Task(subagent_type="tdd-task", model="haiku", prompt="...")` with context included in each prompt: file paths, design decisions, project conventions, stop conditions specific to this feature
- Intermediate checkpoints: every 3-5 delegated cycles, run tests and review accumulated changes (no formal "phase boundaries" in Tier 2 — planner determines checkpoint intervals)
- Final vet, `/commit`

**Checkpoint divergence from plan-adhoc Tier 2:** Plan-tdd Tier 2 includes intermediate checkpoints because TDD cycles are finer-grained than ad-hoc components — accumulated drift is more likely across 4-10 individual RED/GREEN cycles than across 2-4 larger components. Plan-adhoc Tier 2 vets once after all components complete.

**Context delivery for Tier 2:** The planner includes relevant context from the design document in each Task delegation prompt. This partially recreates what Common Context does in Tier 3, but at smaller scale (2-4 components vs 10+ steps). The trade-off is acceptable: Tier 2 has few enough delegations that prompt-level context is manageable, and the overhead of prepare-runbook.py + plan-specific agent creation isn't justified.

**Renumber existing phases:** Phase 1-5 → stay as-is but add "Tier 3 only" guard at the top.

### Changes to workflows-terminology.md

The fragment describes the routes. Update to mention that plan skills auto-detect tier. The route description stays the same (describes the full pipeline), but add a note: "Plan skills include tier assessment — small tasks bypass runbook creation."

### Changes to Oneshot Workflow Guide

`agent-core/docs/oneshot-workflow.md` needs two updates:

**Stage 3 (Planning Session):** Currently describes only the 4-point process. Update to reflect that `/plan-adhoc` now starts with tier assessment. Tier 1/2 bypass the 4-point process. Add brief description of what happens in each tier.

**Fix stale text:** Line 274 says "Future: Will be complemented by /plan-tdd for feature development." — plan-tdd already exists. Update to reflect current state.

### Relationship to Upstream Routing

The `/oneshot` skill (Stage 1) already classifies tasks as simple/moderate/complex. The tier assessment in plan skills operates at a different level:

- **`/oneshot` "simple job"** = tasks needing no design at all (trivial fixes, single-file changes) → execute directly without invoking any plan skill
- **Plan skill Tier 1** = tasks that went through `/design` but turned out to have small implementation scope → the design is complete, implementation is straightforward

These don't overlap: `/oneshot` decides whether to invoke `/plan-adhoc` at all; the plan skill's tier assessment decides how to implement once invoked. No changes to `/oneshot` routing are needed.

---

## Implementation Notes

**Affected files:**
- `agent-core/skills/plan-adhoc/SKILL.md` — restructure Point 0 into three-tier assessment, add Tier 1 and Tier 2 sequences
- `agent-core/skills/plan-tdd/SKILL.md` — add Phase 0 (tier assessment), add Tier 1 and Tier 2 TDD sequences
- `agent-core/fragments/workflows-terminology.md` — add tier assessment note to route descriptions
- `agent-core/docs/oneshot-workflow.md` — update Stage 3 description, fix stale plan-tdd reference
- `agents/decisions/workflows.md` — update "Orchestration Assessment" entry (line 207-223): replace binary (direct vs runbook) with three-tier model (direct / lightweight delegation / full runbook), update assessment criteria to match tier criteria, note this supersedes the original binary decision

**Testing:** Manual — these are skill instruction changes. Validate by:
- Invoking `/plan-adhoc` with a small task → confirm Tier 1 assessment and direct implementation
- Invoking `/plan-adhoc` with a moderate task → confirm Tier 2 assessment and quiet-task delegation
- Invoking `/plan-tdd` with a 2-cycle feature → confirm Tier 1 direct TDD
- Verifying Tier 3 pipeline still works unchanged for large tasks

---

## Revision History

**v1 (2026-01-31)** — Initial design combining both pending tasks (plan-adhoc fast path + plan-tdd fast paths) into unified three-tier assessment.

**v2 (2026-01-31)** — Applied vet review feedback:
- H1: Added "When to Use" guard updates to both skills (remove simple-task exclusions)
- H2: Specified Task tool invocation pattern for Tier 2 (`subagent_type="quiet-task"`, context in prompt)
- H3: Addressed context delivery for TDD Tier 2 (planner includes context in each delegation prompt)
- M1: Changed Tier 1 to "<6 files" (eliminated overlap with Tier 2)
- M2: Specified Tier 1 ends with `/commit` directly (no handoff/restart needed)
- M3: Clarified relationship between `/oneshot` routing and plan skill tier assessment
- M4: Specified Phase 0 does rough cycle estimate (not full Phase 2-3 decomposition)
- L2: Added stale text fix for oneshot-workflow.md

**v3 (2026-01-31)** — Applied re-review feedback + workflow integration validation:
- Added `agents/decisions/workflows.md` to affected files with specific update description
- M1: Specified workflows.md entry content (three-tier model supersedes binary choice)
- M2: Clarified Tier 2 TDD checkpoints are planner-determined intervals, not phase boundaries
- L1: Documented checkpoint divergence rationale between plan-adhoc and plan-tdd Tier 2
