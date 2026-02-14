# Workflow RCA Fixes

## Requirements

### Functional Requirements

**FR-1: Restructure runbook-review.md as type-agnostic**
Restructure the four review axes (vacuity, dependency ordering, density, checkpoint spacing) with type-neutral definitions, then TDD-specific and general-specific detection bullets under each. Update process section to use "item" instead of "cycle." Add file growth projection as fifth axis. Vacuity axis must cover both scaffolding vacuity (existence-check-only tests) and behavioral vacuity (cycle N+1's RED entailed by cycle N's GREEN on the same function).

Acceptance: Each axis has a type-agnostic concept definition, `**TDD:**` detection bullets, `**General:**` detection bullets, and a type-neutral action. Process section references "item (cycle or step)" not "cycle."

Grounding: RCA #1 (general-step detection gap) + RCA #2 (file growth). `runbook-review.md` created 4.5h before per-phase typing shipped, never updated. Same file needs growth axis from RCA #2.

**FR-2: Expand review-plan skill Section 11 with general detection patterns**
Add general-step detection criteria for vacuity (scaffolding), ordering (artifact dependency), and density (same-file composable changes) alongside existing TDD criteria.

Acceptance: Sections 11.1-11.3 each have explicit `**General:**` bullets with detection patterns.

Grounding: RCA #1. Section 10 checks structure; Section 11 checks semantics. General phases currently get structural review only.

**FR-3: Add LLM failure mode gate to Phase 0.95 fast-path**
Before fast-path promotion, run inline check for vacuity, ordering, density, checkpoints. Fix issues inline before promotion.

Acceptance: Phase 0.95 includes validation step referencing all four axes before reformatting.

Grounding: RCA #1 §2.1. Fast-path bypasses Phase 1 expansion and Phase 3 holistic review — outline review becomes the only gate.

**FR-4: Add general-step reference material**
Add general-step content to `agent-core/skills/runbook/references/`: granularity criteria, anti-patterns, and at least one complete example.

Acceptance: Each of patterns.md, anti-patterns.md, examples.md has a general-step section.

Grounding: RCA #1 §2.4. All four reference files are TDD-only. Planners have no reference material for general steps.

**FR-5: Outline growth validation gate**
Add review criterion to outline-review-agent: validate projected file sizes against 400-line enforcement threshold. Split phases must precede first phase exceeding 350 cumulative. Flag outlines with >10 cycles modifying same file but no growth projection.

Acceptance: `runbook-outline-review-agent.md` includes growth projection validation with specific thresholds.

Grounding: RCA #2. Outline projected correctly but compared against wrong threshold (700 vs 400). No review gate cross-checked projection against enforcement limit.

**FR-6: Delete Phase 1.4 (file size awareness)**
Remove Phase 1.4 from runbook skill. Redundant with outline-level enforcement (FR-5).

Acceptance: Phase 1.4 section removed from SKILL.md.

Grounding: RCA #2 §C1. Per-item tracking during expansion places cognitive load on expanding agent, is unenforced, and mid-phase splits break coherence.

**FR-7: Vet status taxonomy**
Replace binary FIXED/UNFIXABLE with four statuses: FIXED, DEFERRED, OUT-OF-SCOPE, UNFIXABLE. UNFIXABLE requires subcategory (U-REQ, U-ARCH, U-DESIGN) and investigation summary. Add Deferred Items report section.

Acceptance: `vet-fix-agent.md` contains taxonomy with criteria for each status, examples, subcategory codes, and report template section.

Grounding: RCA #3. Binary model forces over-escalation. 3 of 7 UNFIXABLE labels across reports were organizational deferrals (RCA #4 evidence). ODC research supports orthogonal classification — defect type × trigger prevents conflation.

**FR-8: Investigation-before-escalation protocol**
Add mandatory checklist before UNFIXABLE classification: (1) check scope OUT list, (2) check design for documented deferral, (3) Glob/Grep for existing patterns, (4) only then classify UNFIXABLE with evidence.

Acceptance: `vet-fix-agent.md` contains sequenced gate between issue identification and UNFIXABLE label. Each gate diverts to correct status (OUT-OF-SCOPE, DEFERRED, FIXED via pattern-matching).

Grounding: RCA #3 Axis 2 (asymmetric incentives). Escalation is zero-cost without investigation gates. The protocol creates escalation cost, changing agent behavior. Incidents 2 and 3 would have been prevented by Glob/Grep step alone.

**FR-9: UNFIXABLE validation in detection protocol**
After grep-for-UNFIXABLE, validate each has subcategory code, investigation summary, and is not in scope OUT list. Resume agent for reclassification if validation fails.

Acceptance: `vet-requirement.md` UNFIXABLE detection section includes validation steps.

Grounding: RCA #3 F5. Mechanical grep catches UNFIXABLE; validation catches misclassification.

**FR-10: Orchestrate template enforcement**
Checkpoint delegation must populate structured IN/OUT scope fields. Fail loudly (log warning, not silent) if fields are empty prose instead of structured lists.

Acceptance: Orchestrate skill checkpoint delegation template has enforcement guidance.

Grounding: RCA #3 Axis 1 (two-layer failure). Every checkpoint across worktree-update and worktree-skill used prose scope, never structured IN/OUT. Template exists but was never used.

**FR-11: Semantic propagation checklist**
When a design introduces new terminology, type systems, or behavioral semantics: outline review verifies artifact inventory includes all files referencing old semantics. Grep-based, classify as producer (rewrite) or consumer (update).

Acceptance: `runbook-outline-review-agent.md` includes semantic propagation check under execution readiness.

Grounding: RCA #1 D3 (meta root cause). Pattern across 3 features: per-phase typing, workflow unification, implementation-notes move — all shipped without updating semantic consumers.

**FR-12: Agent convention injection via skills frontmatter**
Wrap key fragments (deslop, error-handling, code-removal) as lightweight skills. Add `skills:` frontmatter references to review and autofix agents (vet-fix-agent, design-vet-agent, plan-reviewer, outline-review-agent, refactor).

Acceptance: Fragment-wrapping skills exist. Target agents have `skills:` references and produce output following injected conventions (e.g., deslopped prose).

Grounding: Discussion in this session. Only plan-reviewer currently uses `skills:` frontmatter. Review agents operate without project conventions. Microsoft's agent orchestration patterns recommend: "Assign each agent a model that matches the complexity of its task" — conventions are part of capability.

**FR-13: Memory index injection for sub-agents**
Inject memory index as a skill via `skills:` frontmatter. Sub-agents discover triggers from injected index, invoke recall via Bash (`agent-core/bin/when-resolve.py when "<trigger>"` or equivalent CLI path).

Acceptance: At least one sub-agent (vet-fix-agent) has memory index injected and can recall decisions via Bash. Transport instruction in agent definition or memory-index skill prolog.

Grounding: Discussion in this session. `/when` and `/how` are skills; sub-agents lack Skill tool. Index provides discovery (behavioral trigger); Bash provides transport (recall mechanism).

**FR-14: Design skill Phase C density checkpoint**
Add a density check to design skill Phase C (outline generation). Flag when outline items are too granular (single-line changes inflated to full items) or too coarse (multiple modules in one item). TDD non-code marking is already handled by per-phase typing — this addresses the remaining density gap.

Acceptance: Design skill Phase C includes density validation step with criteria for too-granular and too-coarse items.

Grounding: Session.md sub-item. Phase C outlines can be overly dense, creating downstream runbook bloat.

**FR-15: Design-time repetition helper prescription**
When design specifies repeated identical operations (>5 calls to same API, subprocess, or pattern), recommend extracting a private helper. Generic guidance — not specific to subprocess or any particular API.

Acceptance: Design skill or design guidance includes helper extraction recommendation with threshold and rationale.

Grounding: RCA #2 Fix 4. `_git()` helper reduced cli.py by 30% (477→336 lines). Prescribed at design time, the file would never have exceeded 400 lines. Pattern is general: any repeated operation benefits from extraction to reduce formatter expansion and improve maintainability.

**FR-16: Deliverable review as post-orchestration workflow step**
Document deliverable review as a defined workflow step after runbook orchestration completes. Requires opus session. Produces conformance verification against design FRs.

Acceptance: Workflow terminology section or orchestrate skill references deliverable review as post-orchestration step with model requirement.

Grounding: Process RCA #5. No conformance gate exists — scaffolded-but-unimplemented features survive the pipeline. Deliverable review already catches these issues but is currently ad-hoc.

**FR-17: Execution-to-planning feedback requirement**
Document the requirement for global replanning escalation when execution discovers structural plan failures (test strategy wrong, assumption invalid, phase approach needs rethinking). Distinguish from local recovery (refactor agent) and item-level escalation (UNFIXABLE).

Acceptance: Requirement documented with clear handoff to error handling framework design (`wt/error-handling`).

Grounding: When-recall incident — test plan required redesign, sonnet orchestrator patched ad-hoc. Planner-executor research distinguishes local replanning (revise subtask) from global replanning (escalate when issues exceed local scope). Our system has local but not global.

**FR-18: Review-fix integration rule**
When review agent recommendations target an existing section (by heading match), merge into that section rather than appending a parallel section. Applies to outline-review-agent, vet-fix-agent, and plan-reviewer fix application.

Acceptance: Fix-application logic includes integration check: if recommendation references an existing heading, insert within that section. No duplicate heading concepts in output.

Grounding: RCA runbook-outline-review Pattern 2. Round 1 review appended "## Expansion Guidance (from outline review)" when "## Expansion Guidance" already existed 60 lines above. Default append behavior creates structural duplication.

### Constraints

**C-1: All changes are prose edits to existing files**
No code changes. All fixes modify skill definitions, agent definitions, decision documents, or fragment files. Rationale: these are process/documentation fixes grounded in RCA evidence.

**C-2: Agent composition uses native `skills:` mechanism**
No custom build tooling for agent composition. Use existing `skills:` YAML frontmatter for fragment injection. Rationale: plan-reviewer already uses this; native mechanism stays current without maintenance.

**C-3: Fragment-wrapping skills must pass skill-reviewer**
New skills wrapping fragments need validation that raw fragment content works as injected skill content. Rationale: skills may need adaptation (prolog, triggering description) vs raw fragment copy.

**C-4: Execution feedback deferred to error handling framework**
FR-17 captures the requirement but implementation belongs in `wt/error-handling` design. This plan documents the gap and dependency only.

### Out of Scope

- Formal workflow verification tooling (TLA+, Alloy, Petri nets) — separate requirements artifact (`workflow-formal-analysis`)
- Commit CLI tool — branched to `wt/commit-cli`
- When/how CLI subcommand — depends on plugin convention constraints, design during implementation
- Error handling framework implementation — `wt/error-handling` worktree
- Code changes to `claudeutils` package
- Upstream plugin-dev documentation of `skills:` frontmatter — independent task

### Dependencies

- `wt/error-handling` — FR-17 documents requirement; implementation lives there
- Skill-reviewer verdict on fragment-as-skill viability — affects FR-12 approach
- Plugin convention constraints — affects memory index recall transport path (FR-13)

### Open Questions

- Q-1: Does `skills:` inject full SKILL.md content or just specific sections? Affects fragment skill design (FR-12)
- Q-2: Token cost per skill injection — how many skills before agent context is crowded? Affects which agents get which fragments (FR-12)
- Q-3: Process RCA gaps (conformance gate, scaffolding detection) — are these vet criteria additions, orchestrate post-steps, or new review agents? Affects FR-14 implementation shape

### Skill Dependencies (for /design)

- Load `plugin-dev:skill-development` before design (skills creation in FR-12, FR-13)
- Load `plugin-dev:agent-development` before design (agent frontmatter modifications in FR-12, FR-13)

## Research Grounding

### Workflow Verification (van der Aalst)
Workflow nets verify **soundness**: absence of deadlocks, livelocks, anomalies. 8 soundness notions, all decidable for basic nets. Our pipeline has quality gates that can deadlock (UNFIXABLE stops everything), bypass paths (Phase 0.95), missing feedback arcs — all detectable by soundness analysis.

### Defect Classification (IBM ODC, AI-ODC)
ODC taxonomy: defect **type** × **trigger** — orthogonal axes. Type = what changed, trigger = what surfaced it. Our vet taxonomy maps to ODC impact dimension. AI-ODC extends with Data/Learning/Thinking categories. Key insight: our UNFIXABLE conflates type (scope deferral) with trigger (vet review) — orthogonal classification prevents this.

### Agent Orchestration Patterns (Microsoft Azure)
Sequential + handoff + maker-checker patterns match our workflow. Missing: **magentic orchestration** (dynamic task ledger with replanning) — the execution-to-planning feedback gap. Anti-pattern: "using deterministic patterns for inherently nondeterministic workflows."

### Replanning / Execution Feedback (DyFlow, planner-executor)
Local replanning (revise subtask) vs global replanning (escalate beyond local scope). Our system has local (refactor agent) but not global (test strategy failure → no path). Hierarchical replanning separates strategic oversight from tactical execution.

### Sources
- [Soundness of workflow nets](https://link.springer.com/article/10.1007/s00165-010-0161-4) — van der Aalst et al., 2011
- [AI-ODC Framework](https://arxiv.org/html/2508.17900v1) — AI-specific defect classification
- [Agent Orchestration Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns) — Microsoft Azure Architecture Center
- [DyFlow](https://arxiv.org/html/2509.26062) — Dynamic workflow framework
- [Complexity of soundness](https://dl.acm.org/doi/10.1145/3531130.3533341) — EXPSPACE/PSPACE results
- [Hierarchical Multi-Agent Taxonomy](https://arxiv.org/html/2508.12683)
