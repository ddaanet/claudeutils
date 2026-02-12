# Workflow Fixes: Outline

## Problem

Eight workflow artifacts have accumulated known issues from learnings, session reviews, and the worktree-update LLM failure mode analysis. Issues range from process gaps (tdd-plan-reviewer missing LLM failure mode detection) to maintenance burden (250+ lines duplicated across vet agents) to consistency gaps.

## Approach

Targeted fixes to each artifact. No restructuring of agent-skill relationships (that's a separate pending task re: skills prolog pattern). Focus on correctness, consistency, and closing documented gaps.

**Mode:** General (infrastructure fixes). Downstream: `/plan-adhoc`.

## Fixes by Artifact

### tdd-plan-reviewer + review-tdd-plan skill

**Problem:** Only validates TDD discipline (prescriptive code, RED/GREEN sequencing). Does not detect LLM failure modes (vacuity, dependency ordering, density, checkpoint spacing). Worktree-update review proved these are distinct concerns — tdd-plan-reviewer caught 0 of 8 semantic findings.

**Fix:**
- Add LLM failure mode detection criteria to review-tdd-plan skill (reference `agents/decisions/runbook-review.md` four-axis methodology)
- Criteria: vacuous cycle detection, dependency ordering validation, cycle density analysis, checkpoint spacing check
- Apply at BOTH per-phase review (Phase 3) AND holistic review (Phase 5)
- tdd-plan-reviewer agent itself needs minimal changes — it loads the skill

**Evidence:** `plans/worktree-update/reports/runbook-review-llm-failure-modes.md` — 3 vacuous cycles, 1 critical missing requirement, 1 density issue, 1 checkpoint gap, all missed by tdd-plan-reviewer.

### plan-tdd

**Problems:**
- Phase 3 mentions "background review pattern" without specifying `run_in_background=true`
- Expansion guidance from outline review not explicitly consumed before Phase 3 expansion
- Phase 5 holistic review doesn't specify LLM failure mode re-validation

**Fixes:**
- Add explicit Task tool call format with `run_in_background=true` for Phase 3 per-phase reviews
- Add "Read Expansion Guidance from outline" step before Phase 3 expansion begins
- Add LLM failure mode re-validation directive in Phase 5 holistic review (reference review-tdd-plan skill)

**Note:** Reference files (`references/patterns.md` etc.) exist and are valid — exploration report had a false finding.

### plan-adhoc

**Problems:**
- Vet-fix-agent delegations don't mention execution context (Scope IN/OUT, Changed Files)
- "vet agent" references ambiguous (vet-fix-agent vs vet-agent vs vet skill?)

**Fixes:**
- Add execution context template to vet delegation examples (from vet-requirement.md)
- Clarify agent references: specify vet-fix-agent (for checkpoints) vs vet-agent (for review-only)

### vet-fix-agent

**Problems:**
- No UNFIXABLE format in return protocol (tdd-plan-reviewer has one, this doesn't)
- No reference to vet-requirement.md for execution context expectations
- 250+ lines duplicated with vet-agent (separate pending task for prolog restructuring)

**Fixes (this design):**
- Add UNFIXABLE escalation format to return protocol (match tdd-plan-reviewer pattern)
- Add cross-reference to vet-requirement.md in agent header or validation section
- Duplication extraction deferred to "skills prolog" pending task

### vet skill (/vet)

**Problems:**
- No mention of execution context requirements
- No mention of UNFIXABLE handling
- No cross-reference to vet-requirement.md fragment

**Fixes:**
- Add execution context section (reference vet-requirement.md template)
- Add UNFIXABLE detection guidance
- Cross-reference vet-requirement.md for delegation patterns

### runbook-outline-review-agent

**Problems:**
- Expansion Guidance section appended to outline but plan-tdd doesn't explicitly read it before expansion
- Review criteria already include LLM failure modes (lines 116-137) — this is the CORRECT agent for that concern
- No issues with the agent itself — it's the consumer (plan-tdd) that has the gap

**Fix:** Minimal — verify criteria completeness against `agents/decisions/runbook-review.md`. May need sharpening of detection rules based on worktree-update findings (e.g., self-declared vacuity: "should pass immediately" is a signal).

### plugin-dev:skill-development

**Problem:** Doesn't document the `skills:` frontmatter field for agent-skill coupling. Agents can reference skills via `skills: [skill-name]` in frontmatter — this is how tdd-plan-reviewer loads review-tdd-plan. The skill-development guide should mention this consumption pattern.

**Fix:** Add section on "Skills consumed by agents" covering `skills:` frontmatter.

**Upstream:** Contribute as PR/issue to official Claude Code plugin-dev plugin. The `skills:` frontmatter field is a real feature the official docs should cover.

### plugin-dev:agent-development

**Problem:** Frontmatter fields section documents `name`, `description`, `model`, `color`, `tools` — but NOT `skills`. The `skills:` field is how agents load skill content. Missing from documentation.

**Fix:** Add `skills` to frontmatter fields documentation with format and usage guidance.

**Upstream:** Same as plugin-dev:skill-development — contribute to official plugin.

### plan-adhoc and plan-tdd (selection guidance)

**Problem:** No guidance on when to use plan-adhoc vs plan-tdd. Users might invoke wrong skill (Issue 9 from exploration report).

**Fix:** Add "When to Use vs Other Planning Skills" section to both:
- If design specifies TDD approach → use plan-tdd
- If design is general (refactoring, infrastructure, migration) → use plan-adhoc
- If unsure → check design.md for "Test Strategy" or "TDD" mentions

**Location:** Add before existing "When to Use" section in both skills (after frontmatter).

### vet skill and plan-adhoc (agent name clarity)

**Problem:** References to "vet agent" without clarifying which (vet-agent vs vet-fix-agent). (Issue 10 from exploration report).

**Fix:**
- vet SKILL.md: Add "Agent Selection" subsection after "When to Use" — clarify vet-agent (review-only) vs vet-fix-agent (review+fix)
- plan-adhoc: Change "Delegate to vet agent" → "Delegate to vet-fix-agent" (explicit)

## Scope

**IN:**
- All 10 artifacts listed above (8 original + 2 clarification fixes)
- Implements pending task: "Integrate LLM failure mode checks into tdd-plan-reviewer"

**OUT:**
- Agent-skill restructuring / skills prolog pattern (noted as separate pending task)
- /autofix skill creation (noted as separate pending task)
- Vet duplication extraction (deferred to prolog restructuring)
- Design skill audit findings (separate existing pending task: "Update design skill")
- worktree-update runbook fixes (separate existing pending task)
- Session.md task state updates (completed at handoff, not during execution)

## Resolved Questions

1. **Plugin-dev skills:** Upstream contributions to official plugin-dev plugin (PR/issue). The `skills:` field is a real feature that should be in official docs.
2. **Plan-tdd reference files:** Files exist — exploration report was wrong. No fix needed.
3. **Vet duplication:** Defer to skills prolog task.
4. **Session.md task:** Mark "Integrate LLM failure mode checks into tdd-plan-reviewer" complete at handoff.

## Complexity Assessment

10 artifacts, all targeted edits (no new architecture). Most fixes are adding missing sections, cross-references, or sharpening criteria. The substantive work is tdd-plan-reviewer + review-tdd-plan skill (LLM failure mode integration).

Estimate: Tier 2 (moderate) — well-defined scope, known patterns, but breadth across 10 files.
