# Workflow RCA Fixes — Design Outline

## Approach

All 18 FRs are prose edits to existing files (C-1). No code changes. Group into 5 editing clusters that can be sequenced as phases, each targeting a cohesive set of files.

Open questions Q-1/Q-2 resolved empirically: `skills:` injects full SKILL.md (~300-1400 tokens each), manageable for 2-3 skills per agent. Q-3 resolved by mapping to existing mechanisms.

## Phases (reflexive bootstrap order)

Phase ordering follows tool-usage dependency: improve each agent/skill before it's needed by subsequent phases. Design→apply is collapsed — each phase's design specifies exact edits, applied immediately.

**Restart rule:** Agent definitions and fragments are loaded at session start. Every phase that edits an agent definition or fragment requires restart before proceeding. Skill SKILL.md content resolves at agent spawn time (no restart needed for content-only changes), but adding new `skills:` entries to agent frontmatter requires restart.

**Review-after-edit rule:** After each final edit to a skill or agent definition, run the appropriate reviewer with autofix:
- **Skills:** Delegate to `skill-reviewer` agent (plugin-dev). Current limitation: Read/Grep/Glob only (no Write). Pattern: skill-reviewer reports → executor applies fixes from report. Validates frontmatter, trigger description, progressive disclosure, writing style.
- **Agents:** Delegate to `agent-creator` agent (plugin-dev) with review+fix prompt. Has Write+Read access → can apply fixes directly. Prompt with: "Review and fix this agent definition at [path] — validate frontmatter fields, triggering examples, system prompt structure, tool selection. Apply fixes directly."
- **Decision files / fragments:** Use `vet-fix-agent` with execution context.
- **Sequence:** Edit → reviewer (report/autofix) → apply fixes if needed → diagnostic review (if enabled) → restart (if agent/fragment) → proceed to next phase.

**Diagnostic review rule (optional, opus):** After reviewer pass, stop the session primed for interactive opus diagnostic. NOT delegated — opus needs full conversation context for effective RCA. Purpose: catch defects the mechanical reviewer missed, trace root causes through the pipeline, feed findings back into subsequent phases.

- **When to enable:** Phases improving review/vet tools themselves (Phases 1-4 in this job), first use of modified agents, architecturally significant changes. Skip for low-risk content edits (Phases 5-6).
- **Priming:** Before stopping, output a diagnostic primer block containing:
  - What was edited and why (FR reference, acceptance criteria)
  - Reviewer report path and summary of findings
  - Methodology to apply (see below)
  - Suggested prompts: "review using [methodology]", "RCA", "RCA deeper"
  - Files to examine
- **Methodology per artifact type:**
  - Skills/agents: `plugin-dev:agent-development` and `plugin-dev:skill-development` patterns as review criteria
  - Runbook review artifacts: `agents/decisions/runbook-review.md` (four axes)
  - Vet/pipeline artifacts: `agents/decisions/pipeline-contracts.md` (T1-T6 defect classification)
  - Design artifacts: No formal review methodology exists yet — use pipeline-contracts defect classification + alignment verification against requirements
- **Interactive RCA protocol:** User drives iterative deepening in opus session:
  1. **Surface pass:** "Review the changes and reviewer output" — what issues were found? What was missed? Any miscalibration?
  2. **"RCA":** For each finding, trace to pipeline stage origin — which transformation (T1-T6) introduced the defect?
  3. **"RCA deeper":** For systemic patterns, trace to root cause in process — missing review gate, weak detection heuristic, or methodology gap?
  4. **Stop criterion:** User judgment — no new findings, or findings loop to already-identified root cause
- **Feedback paths:**
  - Findings affecting current job → edit artifacts immediately in the opus session (reflexive bootstrapping)
  - Findings affecting workflow infrastructure → append to learnings.md
  - Findings affecting other jobs → append as pending tasks to session.md
- **Session flow:** Edit (sonnet) → reviewer (sonnet) → stop with primer → user switches to opus → interactive diagnostic + RCA → apply fixes → restart → resume next phase (sonnet)
- **Research grounding:** MAR (Multi-Agent Reflexion) shows single-LLM self-reflection exhibits "degeneration of thought." Our pattern separates mechanical review (sonnet, same model that edited) from analytical critique (opus, different model with interactive depth). Flow-of-Action shows SOP-constrained RCA reduces hallucinations — methodology documents serve as SOPs.
- **Methodology gap:** No formal `design-review-methodology.md` or `agent-review-methodology.md` exists. For this job, use pipeline-contracts + plugin-dev patterns. Creating formal methodology documents is a follow-on task.

**Phase 1: Agent composition** (FR-12, FR-13) — *improves all downstream agents*
- **Prerequisite:** Load `plugin-dev:skill-development` and `plugin-dev:agent-development` before executing. Read `agent-core/skills/orchestrate/SKILL.md` continuation passing section and existing `user-invocable: false` skills (review-plan, plugin-dev-validation, handoff-haiku) as reference patterns for non-invocable injected skills.
- Create `agent-core/skills/project-conventions/SKILL.md` (FR-12): Bundle deslop + token-economy + tmp-directory into single skill (~400 tokens). CC sub-agent prompt has no prose quality rules, no token economy, no tmp-directory constraint — gap analysis confirmed against CC system prompts.
- Create `agent-core/skills/error-handling/SKILL.md` (FR-12): Keep separate for bash-heavy agents only (~100 tokens). CC sub-agents get no error suppression guidance.
- Edit agent frontmatter (FR-12): Add `skills:` references — vet-fix-agent gets [project-conventions, error-handling], design-vet-agent gets [project-conventions], outline-review-agent gets [project-conventions], plan-reviewer gets [project-conventions] (already has review-plan), refactor gets [project-conventions, error-handling]
- Create `agent-core/skills/memory-index/SKILL.md` (FR-13): Wrap agents/memory-index.md as skill with transport instruction prolog — "Sub-agents invoke: agent-core/bin/when-resolve.py when '<trigger>'" for Bash recall
- Edit agent frontmatter (FR-13): Add `skills: [memory-index]` to vet-fix-agent (minimum viable test), others as needed
- **Restart required** after this phase (agent frontmatter changes)

**Phase 2: Runbook review overhaul** (FR-1, FR-2, FR-3) — *improves plan-reviewer before it reviews any runbook*
- Edit `agents/decisions/runbook-review.md` (FR-1): Restructure four axes as type-agnostic (concept → TDD detection → general detection → action), add behavioral vacuity detection (cycle N+1 RED fails given cycle N GREEN), add file growth as 5th axis (lines-per-cycle projection with 400-line threshold), update process section to use "item (cycle or step)" instead of "cycle"
- Edit `agent-core/skills/review-plan/SKILL.md` (FR-2): Expand Section 11 (LLM Failure Modes) with general-step detection patterns — add `**General:**` bullets to 11.1 (vacuity: scaffolding-only steps), 11.2 (ordering: artifact dependency), 11.3 (density: same-file composable changes)
- Edit `agent-core/skills/runbook/SKILL.md` (FR-3): Add LLM failure mode gate to Phase 0.95 fast-path — before reformatting, run inline check for vacuity, ordering, density, checkpoints; fix issues before promotion
- **Restart required** after this phase (runbook-review.md is loaded via CLAUDE.md @-ref)

**Phase 3: Vet agent overhaul** (FR-7, FR-8, FR-9, FR-10, FR-18) — *improves vet-fix-agent before it vets any output*
- Edit `agent-core/agents/vet-fix-agent.md` (FR-7): Replace binary FIXED/UNFIXABLE with four-status taxonomy — FIXED, DEFERRED, OUT-OF-SCOPE, UNFIXABLE; UNFIXABLE requires subcategory (U-REQ, U-ARCH, U-DESIGN) and investigation summary; add Deferred Items report section
- Edit `agent-core/agents/vet-fix-agent.md` (FR-8): Add investigation-before-escalation protocol — mandatory checklist before UNFIXABLE: (1) check scope OUT list, (2) check design for documented deferral, (3) Glob/Grep for existing patterns, (4) only then classify UNFIXABLE with evidence
- Edit `agent-core/fragments/vet-requirement.md` (FR-9): Add UNFIXABLE validation in detection protocol — after grep-for-UNFIXABLE, validate each has subcategory code, investigation summary, and is not in scope OUT list; resume agent for reclassification if validation fails
- Edit `agent-core/fragments/vet-requirement.md` (FR-10): Strengthen execution context requirement — checkpoint delegation must populate structured IN/OUT scope fields, fail loudly if fields are empty prose instead of structured lists
- Edit `agent-core/skills/orchestrate/SKILL.md` (FR-10): Add checkpoint delegation template enforcement guidance — reference structured template with IN/OUT scope lists, log warning if fields missing
- Edit `agent-core/agents/vet-fix-agent.md` (FR-18): Add review-fix integration rule — when recommendation targets existing section (by heading match), merge into that section rather than appending parallel section; prevents duplicate heading concepts
- **Restart required** after this phase (agent definition changes)

**Phase 4: Outline review agent** (FR-5, FR-11) — *improves outline-review-agent before it reviews any outline*
- Edit `agent-core/agents/outline-review-agent.md` (FR-5): Add outline growth validation gate — validate projected file sizes against 400-line enforcement threshold, flag outlines with >10 cycles modifying same file but no growth projection, split phases must precede first phase exceeding 350 cumulative lines
- Edit `agent-core/agents/outline-review-agent.md` (FR-11): Add semantic propagation checklist under execution readiness — when design introduces new terminology/type systems/behavioral semantics, verify artifact inventory includes all files referencing old semantics, grep-based classification as producer (rewrite) or consumer (update)
- **Restart required** after this phase (agent definition changes)

**Phase 5: Design + runbook skill fixes** (FR-4, FR-14, FR-15, FR-16)
- Create `agent-core/skills/runbook/references/general-patterns.md` (FR-4): Add granularity criteria (single-responsibility per step, prerequisite validation patterns, composable vs atomic operations)
- Edit `agent-core/skills/runbook/references/anti-patterns.md` (FR-4): Add general-step anti-patterns section (scaffolding vacuity, missing prerequisite investigation, same-file density bloat)
- Edit `agent-core/skills/runbook/references/examples.md` (FR-4): Add at least one complete general-step example with prerequisite validation, script evaluation, conformance verification
- Edit `agent-core/skills/design/SKILL.md` Phase C.1 (FR-14): Add density checkpoint before generating design — flag when outline items are too granular (single-line changes inflated to full items) or too coarse (multiple modules in one item); TDD non-code marking already handled by per-phase typing
- Edit `agent-core/skills/design/SKILL.md` Phase C.1 (FR-15): Add repetition helper prescription — when design specifies repeated identical operations (>5 calls to same API, subprocess, or pattern), recommend extracting private helper; generic guidance with threshold and maintainability rationale
- Edit `agent-core/fragments/workflows-terminology.md` Implementation workflow route (FR-16): Add deliverable review as post-orchestration workflow step — requires opus session, produces conformance verification against design FRs, distinct from runbook execution

**Phase 6: Runbook skill cleanup + feedback requirement** (FR-6, FR-17)
- Edit `agent-core/skills/runbook/SKILL.md` (FR-6): Delete Phase 1.4 section (file size awareness) — redundant with outline-level enforcement (FR-5)
- Edit `agents/decisions/orchestration-execution.md` (FR-17): Document execution-to-planning feedback requirement — distinguish local recovery (refactor agent) from global replanning escalation (test strategy wrong, assumption invalid, phase approach needs rethinking); requirement captured, implementation deferred to `wt/error-handling` per C-4

## Key Decisions

1. **Convention injection via skills:** Bundle deslop + token-economy + tmp-directory into `project-conventions` skill (~400 tokens). Keep error-handling separate (~100 tokens) for bash-heavy agents. Drop code-removal (CC natively covers "delete unused"). Gap analysis against CC system prompts confirms sub-agents receive no prose quality rules, no token economy, no tmp-directory constraint. Research grounding: Anthropic's context engineering recommends focused task context over comprehensive information; ACE framework shows 10.6% performance gain from strategic knowledge injection.

2. **Memory index skill:** Wrap `agents/memory-index.md` as skill. Sub-agents get index in context, invoke `agent-core/bin/when-resolve.py when "<trigger>"` for recall (Bash transport, not Skill tool).

3. **Behavioral vacuity detection:** Add to runbook-review.md: "For each cycle pair (N, N+1) on same function, verify N+1's RED assertion would fail given N's GREEN. If not, cycles are behaviorally vacuous." Heuristic: cycles > LOC/20 signals consolidation. This addresses FR-1's requirement for behavioral vacuity alongside existing scaffolding vacuity detection.

4. **Review-fix integration (FR-18):** When fix targets existing section heading, merge into section. Prevents duplicate sections from append-only fix application. Pattern emerged in outline-review-agent Round 1 review (appended "## Expansion Guidance (from outline review)" when "## Expansion Guidance" already existed 60 lines above).

5. **Reflexive bootstrapping:** When improving tools, apply each improvement before using that tool in subsequent steps. Phase ordering follows the dependency graph of tool usage: improve agent composition first (skills injection), then review logic (plan-reviewer), then vet logic (vet-fix-agent), then outline review. Each improvement is immediately available to subsequent steps. This collapses the design→plan→execute pipeline into design→apply for prose-edit work, since the design document specifies exact edits and there's nothing to "execute" separately. Generalizes beyond this job: any self-referential improvement task should apply changes in dependency order of tool usage, not in logical grouping order.

6. **Three-layer validation:** Each artifact edit goes through: (a) domain-specific reviewer with autofix (skill-reviewer for skills, agent-creator for agents, vet-fix-agent for decisions/fragments), (b) optional interactive opus diagnostic session with iterative RCA for self-referential improvements — session stops primed, user switches to opus, (c) restart and proceed. Layer (b) enabled for Phases 1-4 (improving review tools), skipped for Phases 5-6 (content edits). Separates mechanical review (sonnet, same model) from analytical critique (opus, interactive depth) — avoids MAR's "degeneration of thought" from single-model self-reflection.

7. **Phase types:** All phases are general (prose edits). No TDD phases — no behavioral code changes. Phase 4 creates new SKILL.md files but these are content authoring, not code implementation.

8. **Execution model:** Sonnet for edits, opus for diagnostic review passes (Phases 1-4 only). Phases 5-6 are sonnet throughout.

## Scope Boundaries

**In scope:** 18 FRs, all prose edits to existing files + new skill wrapper files
**Out of scope:** Code changes, error-handling framework implementation (FR-17 documents requirement only), upstream plugin-dev documentation, formal workflow verification

## Requirements Traceability

All 18 FRs mapped to phases:

| Requirement | Phase | Target Files |
|-------------|-------|--------------|
| FR-1 | 2 | runbook-review.md |
| FR-2 | 2 | review-plan/SKILL.md |
| FR-3 | 2 | runbook/SKILL.md |
| FR-4 | 5 | runbook/references/ |
| FR-5 | 4 | outline-review-agent.md |
| FR-6 | 6 | runbook/SKILL.md |
| FR-7 | 3 | vet-fix-agent.md |
| FR-8 | 3 | vet-fix-agent.md |
| FR-9 | 3 | vet-requirement.md |
| FR-10 | 3 | vet-requirement.md, orchestrate/SKILL.md |
| FR-11 | 4 | outline-review-agent.md |
| FR-12 | 1 | New skills/, agent frontmatter |
| FR-13 | 1 | New skills/memory-index/, agent frontmatter |
| FR-14 | 5 | design/SKILL.md |
| FR-15 | 5 | design/SKILL.md |
| FR-16 | 5 | workflows-terminology.md |
| FR-17 | 6 | orchestration-execution.md |
| FR-18 | 3 | vet-fix-agent.md |

## Open Questions (Resolved)

- Q-1: `skills:` injects full SKILL.md → design for all-or-nothing injection, keep wrapper skills small
- Q-2: ~300-400 tokens per small skill, ~1200 for large → 2-3 skills per agent is manageable (~5-10% overhead)
- Q-3: Conformance gate = existing outline-review-agent (FR-11 adds semantic propagation); scaffolding detection = existing Section 11.1 vacuity (FR-2 adds general bullets)
