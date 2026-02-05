# Workflow Patterns

Workflow-related architectural decisions and patterns.

## Oneshot Workflow Pattern

**Decision Date:** 2026-01-19

**Decision:** Implement and validate weak orchestrator pattern with runbook-specific agents for ad-hoc task execution.

**Status:** Complete - All phases delivered, pattern validated

**Key Components:**
- Baseline task agent (`agent-core/agents/quiet-task.md`)
- Runbook preparation script (`agent-core/bin/prepare-runbook.py`)
- 5 skills: `/design`, `/plan-adhoc`, `/orchestrate`, `/vet`, `/remember`
- Complete documentation (documented in CLAUDE.md and agent-core)

**Weak orchestrator pattern:**

**Pattern Validation:**
- Haiku successfully executes runbook steps using runbook-specific agents
- Error escalation works (haiku → sonnet → opus)
- Quiet execution pattern maintains lean orchestrator context
- Context caching via runbook-specific agents reduces token costs

**Terminology Standardization:**
- Job = user's goal
- Design = architectural spec from opus
- Runbook = implementation steps (replaces "plan" in execution context)
- Step = individual unit of work
- Runbook prep = 4-point process (Evaluate, Metadata, Review, Split)

**Impact:**
- Production-ready workflow for ad-hoc tasks
- Reduced context overhead through specialized agents
- Standardized terminology across documentation
- Reusable components via agent-core submodule

## TDD Workflow Integration

**Decision Date:** 2026-01-19, Updated 2026-01-26

**Decision:** Extend weak orchestrator pattern to support TDD methodology for feature development.

**Status:** Complete - All 8 steps delivered, production-ready

**Key Components:**
- TDD workflow documentation (`agent-core/agents/tdd-workflow.md`)
- TDD baseline agent (`agent-core/agents/tdd-task.md`)
- `/plan-tdd` skill with 5-phase execution (includes automated review)
- Cycle-based runbooks supporting RED/GREEN/REFACTOR progression
- TDD task agent pattern with cycle-aware instruction sets
- TDD runbook reviewer (`agent-core/agents/tdd-plan-reviewer.md`) for prescriptive code detection
- Review skill (`agent-core/skills/review-tdd-plan/`) for anti-pattern detection

**TDD workflow:**

**Architecture:**
- Unified design entry point (`/design` skill) supports both oneshot and TDD modes
- RED phase: Write failing tests, document intent
- GREEN phase: Describe behavior and provide hints (NOT prescriptive code)
- REFACTOR phase: Improve code quality while maintaining tests
- **Automated review**: tdd-plan-reviewer detects prescriptive code violations
- **Mandatory prepare-runbook.py**: Generates step files before /orchestrate
- Cycle-aware task delegation with scoped runbooks per cycle
- Quiet execution pattern preserves orchestrator context

**Key Decisions:**
- Cycle-based splitting: Each RED/GREEN/REFACTOR as separate runbook cycle
- Model assignment: Sonnet for TDD planning, haiku for implementation, opus for design
- Deduplication: Use 4-point prep to avoid overlap with oneshot workflow
- Testing focus: Behavioral verification with full test coverage
- Progressive discovery: Documentation read only when executing TDD workflow
- Anti-pattern detection: Automated review prevents prescriptive code in GREEN phases
- Mandatory artifact generation: prepare-runbook.py must run before /orchestrate

**Impact:**
- Production-ready TDD workflow for test-first development
- Enforced test-first methodology via /plan-tdd skill
- Prescriptive code detection prevents "copy-paste" implementations
- Reusable cycle patterns via agent-core documentation
- Consistent terminology across test and implementation phases
- Proper execution flow: design → plan → review → prepare → orchestrate

## Handoff Pattern: Inline Learnings

**Handoff pattern:**

**Decision Date:** 2026-01-27

**Decision:** Store session learnings inline in `session.md` rather than separate file system.

**Rationale:**
- Separate file system (pending.md + individual learning files) requires script management
- Inline learnings are easier to edit, update, and refine during handoffs
- Simpler workflow without add-learning.py complexity
- Single source of truth for session state

**Implementation:**
- Removed `agents/learnings/` directory entirely
- All learnings now in `session.md` Recent Learnings section
- Handoff skill simplified (removed script dependencies)

**Impact:**
- Reduced handoff complexity
- Easier to discover and update learnings
- Self-contained session documentation

## Design Phase: Output Optimization

**Decision Date:** 2026-01-27

**Decision:** Minimize designer (premium model) output tokens by writing for intelligent readers.

**Rationale:**
- Large tasks require planning step anyway - planner can infer details
- Dense design output aligns with planning needs
- Intelligent downstream agents don't need obvious details spelled out

**Pattern:**
- Designer produces concise, high-level architectural guidance
- Planner elaborates details during runbook creation
- Implementation agents work from detailed runbook steps

**Impact:**
- Reduced token cost in premium design phase
- No loss of implementation quality (detail added in planning)
- Faster design sessions

## Planning Pattern: Three-Stream Problem Documentation

**Decision Date:** 2026-01-27

**Decision:** Document parallel work streams with `problem.md` (analysis) + `session.md` (design proposals).

**Rationale:**
- Enables async prioritization without re-discovering context
- User can select work stream based on documented analysis
- Scales well for complex sessions with multiple improvement areas

**Structure:**
```
plans/<stream-name>/
├── problem.md      # Analysis: what's broken, why it matters
└── session.md      # Design proposals and decisions
```

**Example:** During TDD session, documented handoff skill improvements, model awareness, and plan-tdd improvements as separate streams with complete analysis.

**Impact:**
- Better context preservation across sessions
- User can prioritize work streams easily
- Clear separation of analysis vs design

## TDD Workflow: Commit Squashing Pattern

**TDD commit squashing:**

**Decision Date:** 2026-01-27

**Decision:** Squash TDD cycle commits into single feature commit while preserving granular cycle progression in reports.

**Pattern:**
1. Create backup tag before squashing
2. `git reset --soft <base-commit>` to staging area
3. Create squashed commit with feature message
4. Cherry-pick subsequent commits (if any)
5. Test result before cleanup
6. Delete backup tag after verification

**Rationale:**
- Clean git history (one commit per feature)
- Complete cycle-by-cycle implementation preserved in runbook reports
- Avoids polluting history with WIP commits

**Impact:**
- Production-ready commit history
- Full audit trail in execution reports
- Easy to review feature implementation holistically

## Orchestrator Execution Mode

**Decision Date:** 2026-01-31

**Decision:** Execution mode metadata in orchestrator plan overrides system prompt parallelization directives.

**Problem:** System prompt parallelization directive (strong emphasis, 3x repetition) overrides orchestrate skill sequential requirement when tasks appear syntactically independent but are semantically state-dependent (TDD cycles, git commits).

**Solution:**
- Use `claude0` (`--system-prompt "Empty."`) to remove competing directives
- Execution mode metadata in orchestrator plan is authoritative
- ONE Task call per message when execution mode is sequential
- Plan must include rationale and explicit override instructions

**Pattern:**
```markdown
**Execution Mode:** STRICT SEQUENTIAL

**Rationale:** TDD cycles modify shared state. Parallel execution causes git commit race conditions and RED phase violations.

**Override:** Execute ONE Task call per message, regardless of syntactic independence.
```

**Rationale:**
- Syntactic independence (no parameter dependencies) != semantic independence (state dependencies)
- Strong directive language ("CRITICAL", "MUST", all-caps) matches system prompt emphasis level
- Explicit rationale prevents future misinterpretation

**Impact:**
- Prevents race conditions in TDD workflow execution
- Clear contract between planner and orchestrator
- Eliminates ambiguity in execution mode requirements

## Orchestration Assessment: Three-Tier Implementation Model

**Three-tier assessment:**

**Decision Date:** 2026-01-31 (updated 2026-01-31)

**Decision:** Plan skills use three-tier assessment to route work appropriately. This supersedes the original binary (direct vs runbook) decision.

**Three Tiers:**

**Tier 1 (Direct Implementation):**
- Design complete (no open decisions)
- All edits straightforward (<100 lines each)
- Total scope: <6 files
- Single session, single model
- No parallelization benefit
- **Sequence:** Implement directly → vet agent → apply fixes → `/handoff --commit`

**Tier 2 (Lightweight Delegation):**
- Design complete, scope moderate (6-15 files or 2-4 logical components)
- Work benefits from agent isolation but not full orchestration
- Components are sequential (no parallelization benefit)
- No model switching needed
- **Sequence:** Delegate via Task tool (quiet-task/tdd-task) with context in prompts → vet agent → `/handoff --commit`

**Tier 3 (Full Runbook):**
- Multiple independent steps (parallelizable)
- Steps need different models
- Long-running / multi-session execution
- Complex error recovery
- >15 files or complex coordination
- **Sequence:** 4-point process → prepare-runbook.py → handoff → restart → orchestrate

**Rationale:** Matches orchestration overhead to task complexity. Tier 1 avoids unnecessary process for simple tasks. Tier 2 provides middle ground with context isolation but minimal overhead. Tier 3 preserves full pipeline for complex work.

**Impact:** Prevents unnecessary runbook creation for straightforward tasks while surfacing lightweight delegation as middle ground.

## Checkpoint Process for Runbooks

**Checkpoint process:**

**Decision Date:** 2026-01-31

**Decision:** Two-step checkpoints at natural boundaries in runbook execution.

**Pattern:**
1. **Fix checkpoint:** `just dev` (lint, tests, build verification)
2. **Vet checkpoint:** Quality review (code review, architecture validation)

**Rationale:** Balances early issue detection with cost efficiency. Avoids both extremes: all-at-once vetting (late detection) and per-step vetting (excessive overhead).

**Impact:** Optimal cost-benefit for runbook quality assurance.

## Phase-Grouped TDD Runbooks

**Decision Date:** 2026-01-31

**Decision:** Support both flat (H2) and phase-grouped (H2 + H3) cycle headers in runbooks.

**Patterns:**
- Flat: `## Cycle X.Y`
- Phase-grouped: `## Phase N` / `### Cycle X.Y`

**Implementation:** `prepare-runbook.py` regex changed from `^## Cycle` to `^###? Cycle`

**Rationale:** Phase grouping improves readability for large runbooks with logical phases.

**Impact:** Flexible runbook structure for different complexity levels.

## Cycle Numbering Gaps Relaxed

**Decision Date:** 2026-02-04

**Decision:** Gaps in cycle numbering are warnings, not errors. Duplicates and invalid start numbers remain errors.

**Rationale:** Document order defines execution sequence — numbers are stable identifiers, not sequence indicators. Treating gaps as fatal errors caused excessive editing churn (10+ edits per gap).

**Implementation:** `prepare-runbook.py` validation downgraded gap detection from ERROR to WARNING.

**Impact:** Reduced editing friction during runbook creation while maintaining validation for actual errors.

## No Human Escalation During Refactoring

**Decision Date:** 2026-01-31

**Decision:** Design decisions are made during `/design` phase. Opus handles architectural refactoring within design bounds. Human escalation only for execution blockers.

**Rationale:** Blocking pipeline for human input during refactoring is expensive.

**Impact:** Faster execution, clear separation between design (user input) and implementation (automated).

## Defense-in-Depth: Commit Verification

**Commit verification:**

**Decision Date:** 2026-01-31

**Decision:** Multiple layers of commit verification at different execution levels.

**Layers:**
- **tdd-task agent:** Post-commit sanity check (verify commit contains expected files)
- **orchestrate skill:** Post-step tree check (escalate if working tree dirty)

**Rationale:** Catches different failure modes at different levels (commit content vs working tree state).

**Impact:** Robust commit verification without single point of failure.

## Handoff Workflow

### Handoff Tail-Call Pattern

**Handoff tail-call:**

**Decision Date:** 2026-02-01

**Decision:** All tiers (1/2/3) must end with `/handoff --commit`, never bare `/commit`.

**Anti-pattern:** Tier 1/2 skip handoff because "no session restart needed"

**Correct pattern:** Always tail-call `/handoff --commit` — handoff captures session context and learnings regardless of tier

**Rationale:** Handoff is about context preservation, not just session restart. Even direct implementations produce learnings and update pending task state.

**Impact:** Consistent workflow termination across all tier levels.

### Handoff Commit Assumption

**Handoff commit assumption:**

**Decision Date:** 2026-02-01

**Decision:** session.md reflects post-commit state when `--commit` flag is used.

**Anti-pattern:** Writing "Ready to commit" in Status or "pending commit" in footer when `--commit` flag is active

**Correct pattern:** Write status reflecting post-commit state — the tail-call makes commit atomic with handoff

**Rationale:** Next session reads session.md post-commit. Stale commit-pending language causes agents to re-attempt already-completed commits. The rule against commit tasks in Pending/Next Steps must extend to ALL sections.

**Impact:** Prevents duplicate commit attempts in subsequent sessions.

## Workflow Efficiency

### Delegation with Context

**Delegation with context:**

**Decision Date:** 2026-02-01

**Decision:** Don't delegate when context is already loaded.

**Anti-pattern:** Reading files, gathering context, then delegating to another agent (which re-reads everything)

**Correct pattern:** If you already have files in context, execute directly — delegation adds re-reading overhead

**Rationale:** Token economy. Agent overhead (context setup + re-reading) exceeds cost of continuing in current model.

**Corollary:** Delegate when task requires *new* exploration you haven't done yet.

**Impact:** Reduces token waste from redundant context loading.

### Routing Layer Efficiency

**Single-layer complexity:**

**Decision Date:** 2026-02-01

**Decision:** Single-layer complexity assessment, not double assessment.

**Anti-pattern:** Entry point skill assesses complexity, then routes to planning skill which re-assesses complexity (tier assessment)

**Correct pattern:** Single entry point with triage that routes directly to the appropriate depth — no intermediate routing layer

**Rationale:** Each assessment reads files, analyzes scope, produces output. Two assessments for the same purpose is pure waste.

**Example:** Oneshot assessed simple/moderate/complex, then /plan-adhoc re-assessed Tier 1/2/3 — same function, different labels.

**Impact:** Eliminates redundant analysis overhead.

### Vet Agent Context Usage

**Decision Date:** 2026-02-01

**Decision:** Leverage vet agent context for fixes instead of launching new agents.

**Anti-pattern:** When removal agent makes mistakes and vet catches them, launching a new fix agent (which re-reads everything)

**Correct pattern:** If vet agent has context of what's wrong, leverage it. If caller also has context (from reading vet report), apply fixes directly.

**Rationale:** Tier 1/2 pattern — caller reads report, applies fixes with full context. No need for another agent round-trip.

**Impact:** Faster fix cycles without redundant context loading.

## Design and Planning Patterns

### Outline-First Design Workflow

**Outline-first design workflow:**

**Decision Date:** 2026-02-04

**Decision:** Produce freeform outline first, iterate with user via incremental deltas, then generate full design after validation.

**Anti-pattern:** Producing full design.md in a single pass, then discovering user wanted different approach.

**Escape hatch:** If user already specified approach/decisions/scope, compress outline+discussion into single validation.

**Rationale:** Early validation prevents wasted effort on wrong direction. Iterative refinement captures user intent accurately.

**Impact:** Higher quality designs aligned with user expectations, less re-work.

### Model Selection for Design Guidance

**Model selection design guidance:**

**Decision Date:** 2026-02-04

**Decision:** Haiku for explicit edits with exact text provided, sonnet for generating markdown from design guidance.

**Anti-pattern:** Assigning haiku to tasks requiring interpretation of design intent ("add escape hatch if...").

**Rationale:** Haiku executes what's specified, sonnet interprets intent and produces explicit text.

**Trade-off:** Sonnet costs more but prevents re-work from under-specified haiku tasks.

**Impact:** Appropriate model selection reduces execution errors and re-work.

### Design Review Uses Opus

**Decision Date:** 2026-02-04 (superseded by design-vet-agent)

**Original Decision:** Use `Task(subagent_type="general-purpose", model="opus")` for design review.

**Current Decision:** Use `Task(subagent_type="design-vet-agent")` — dedicated agent with opus model.

**Anti-pattern:** Using vet-agent for design review (vet is implementation-focused — code quality, patterns, correctness).

**Rationale:** General-purpose agent strengths (architecture analysis, multi-file exploration, complex investigation) align with design review needs.

**Benefits:** Artifact-return pattern (detailed report to file), specialized review protocol, consistent with vet-agent/vet-fix-agent structure.

**Impact:** Three-agent vet system: vet-agent (code, sonnet), vet-fix-agent (code + fixes, sonnet), design-vet-agent (architecture, opus).

### Vet Catches Structure Misalignments

**Vet catches structure misalignments:**

**Decision Date:** 2026-02-04

**Decision:** Vet agent validates file paths AND structural assumptions via Glob/Read during review.

**Anti-pattern:** Writing runbook steps based on assumed structure ("lines ~47-78") without reading actual files.

**Example:** plan-adhoc Point 0.5 actually at line 95, plan-tdd uses "Actions:" not "Steps:".

**Impact:** Prevented execution failures from incorrect section identification. Vet review with path validation is a blocker-prevention mechanism, not just quality check.

**Critical:** Always validate structural assumptions during vet reviews.

## Orchestration Patterns

### Agent-Creator Reviews in Orchestration

**Agent-creator reviews in orchestration:**

**Decision Date:** 2026-02-04

**Decision:** Task agent creates file from spec, then `plugin-dev:agent-creator` reviews and fixes (YAML syntax, description quality, prompt structure).

**Anti-pattern:** Only using agent-creator for interactive agent creation from scratch.

**Mechanism:** Custom `## Orchestrator Instructions` in runbook specifies per-step subagent_type override. prepare-runbook.py already extracts custom orchestrator sections.

**Confirmed empirically:** agent-creator is cooperative in review mode, has Write access.

**Impact:** Higher quality agent files through specialized review.

### Template Commit Contradiction

**Template commit contradiction:**

**Decision Date:** 2026-02-04

**Problem:** quiet-task.md says "NEVER commit unless task explicitly requires" while prepare-runbook.py appends "Commit all changes before reporting success".

**Root cause:** Baseline template designed for ad-hoc delegation (no auto-commit), but orchestrated execution requires clean tree after every step.

**Fix:** Qualified quiet-task.md line 112 to add "or a clean-tree requirement is specified".

**Broader lesson:** Appended context at bottom of agent file has weak positional authority vs bolded NEVER in core constraints section — contradictions resolve in favor of the structurally prominent directive.

**Impact:** Resolved directive conflict, clarified when commits are required.

### Orchestrator Model Mismatch

**Orchestrator model mismatch:**

**Decision Date:** 2026-02-04

**Problem:** Using orchestrator's own model (haiku) for all step agent Task invocations.

**Root cause:** Orchestrate skill said "model: [from orchestrator metadata, typically haiku]" — ambiguous, conflated orchestrator model with step execution model.

**Correct pattern:** Read each step file's "Execution Model" field and pass that to Task tool's model parameter.

**Impact:** Haiku step agents skip complex behaviors (vet delegation, commit sequences) that sonnet would follow.

**Fix:** Clarified orchestrate skill Section 3.1 — model comes from step file, not orchestrator default.

## Testing and TDD Patterns

### Happy Path First TDD

**Happy path first TDD:**

**Decision Date:** 2026-02-04

**Decision:** Start with simplest happy path that exercises real behavior; test edge cases only when they need special handling.

**Anti-pattern:** Testing empty/degenerate cases first (cycle 1: empty list returns []; stub never replaced).

**Rationale:** Empty-first ordering produces stubs that satisfy tests but never get replaced with real implementations.

**Impact:** Test-driven implementations that exercise actual behavior from first cycle.

## Runbook Artifacts

### Runbook Outline Format

**Decision Date:** 2026-02-05

**Decision:** Use structured outline format for runbook planning with requirements mapping and phase organization.

**Format:**

```markdown
# Runbook Outline: <name>

**Design:** plans/<job>/design.md
**Type:** tdd | general

.## Requirements Mapping

| Requirement | Phase | Steps/Cycles | Notes |
|-------------|-------|--------------|-------|
| FR-1 | 1 | 1.1, 1.2 | Core functionality |
| FR-2 | 2 | 2.1-2.3 | Error handling |

.## Phase Structure

.### Phase 1: <name>
**Objective:** <what this phase accomplishes>
**Complexity:** Low/Medium/High
**Steps:**
- 1.1: <title>
- 1.2: <title>

.### Phase 2: <name>
**Objective:** <what this phase accomplishes>
**Complexity:** Low/Medium/High
**Steps:**
- 2.1: <title>
- 2.2: <title>

.## Key Decisions Reference
- Decision 1: <from design> → affects Phase 1
- Decision 2: <from design> → affects Phase 2
```

**Purpose:**
- Requirements mapping table ensures all design requirements are implemented
- Phase structure provides high-level roadmap before detailed expansion
- Enables early review and validation (outline feedback before full runbook)
- Supports phase-by-phase expansion with incremental reviews

**Usage:**
- Referenced in `/plan-adhoc` Point 0.75
- Referenced in `/plan-tdd` Phase 1.5

**Impact:** Provides holistic view for cross-phase coherence while enabling incremental development with earlier feedback.

## Documentation and Knowledge Management

### Seeding Before Auto-Generation

**Seeding before auto-generation:**

**Decision Date:** 2026-02-04

**Decision:** Seed indexes with entries pointing to existing permanent docs before expecting auto-generation to fill them.

**Anti-pattern:** Leaving knowledge indexes empty until consolidation runs.

**Rationale:** Non-empty index is immediately useful; seeding and consolidation are complementary bootstrap mechanisms.

**Impact:** Immediate value from indexes while consolidation builds them incrementally.

### Index Entries Require Backing Documentation

**Index entries require backing documentation:**

**Decision Date:** 2026-02-04

**Decision:** Learnings → learnings.md → /remember → permanent doc → index entry.

**Anti-pattern:** Adding memory-index entries for concepts without permanent docs.

**Rationale:** Index entries are discovery surfaces for on-demand knowledge; they must point somewhere.

**Impact:** Index serves as reliable discovery mechanism, not aspirational wishlist.

### Template Merge Semantics

**Template merge semantics:**

**Decision Date:** 2026-02-04

**Decision:** Partial templates with explicit merge semantics — PRESERVE existing sections, ADD new items, REPLACE only specified content.

**Anti-pattern:** Generic templates that imply "replace structure with this form" (causes learnings deletion).

**Rationale:** "Template" implies blank slate; explicit semantics (preserve/add/replace) prevent unintended overwrites.

**Impact:** Safe template usage without data loss.

## Requirements and Execution

### Requirements Immutable During Execution

**Requirements immutable during execution:**

**Decision Date:** 2026-02-04

**Decision:** Requirements MUST NOT be updated if task execution made them outdated; updating requires explicit user confirmation.

**Anti-pattern:** Updating requirement files during task execution when implementation discovers they're outdated.

**Rationale:** Requirements document intent and decisions at planning time; execution discovering they're wrong means either (1) requirements need user review/approval before updating, or (2) implementation needs to match requirements despite being outdated.

**Impact:** Clear separation between planning (requirements) and execution (implementation).

## Knowledge Discovery and Context

### Ambient Awareness Beats Invocation

**Ambient awareness beats invocation:**

**Decision Date:** 2026-02-04

**Research:** From Vercel study: Ambient context (100%) outperformed skill invocation (79%).

**Problem:** Skills not triggered 56% of cases — decision about "when to invoke" is failure point.

**Correct pattern:** Embed critical knowledge in loaded context (CLAUDE.md, memory-index).

**Directive:** "Prefer retrieval-led reasoning over pre-training knowledge" (memory-index.md header).

**Impact:** Always-available context beats sometimes-invoked skills.

### Task Prose Keys Pattern

**Task prose keys pattern:**

**Decision Date:** 2026-02-04

**Pattern:** Task names serve as identifiers (no hash tokens needed).

**Implementation:** git log -S for on-demand history search, case-insensitive matching.

**Benefit:** Near-zero marginal cost, natural language keys, context recovery via task-context.sh.

**Impact:** Task names are both human-readable and machine-searchable identifiers.

## .Commit Workflow Patterns

### Commit RCA Fixes Active

**Decision Date:** 2026-02-05

**Decision:** Three commit RCA fixes implemented and active in workflow.

**Fixes:**
1. **Submodule awareness:** Commit submodule first, then stage pointer in parent
2. **Artifact staging:** prepare-runbook.py stages its own artifacts via `git add`
3. **Orchestrator stop rule:** Absolute "no exceptions" language, deleted contradictory scenarios

**Status:** All fixes implemented and committed, active in current workflow.

**Impact:** Prevents submodule sync drift, missing artifacts in commits, and dirty-state rationalization.

### Precommit Is Read-Only

**Decision Date:** 2026-02-05

**Decision:** `just precommit` must not modify source files (unlike `just dev` which autoformats).

**Exemption:** Volatile session state (`agents/session.md`) is exempt — `#PNDNG` token expansion runs in precommit.

**Rationale:** Precommit is validation, not transformation. Session state is ephemeral metadata, not source code.

**Impact:** Clear separation between validation (precommit) and transformation (dev) workflows.

## .Planning Workflow Patterns

### Outline Enables Phase-by-Phase Expansion

**Decision Date:** 2026-02-05

**Decision:** Generate holistic outline first, then expand phase-by-phase with review after each.

**Anti-pattern:** Generate full runbook monolithically, review at end (late feedback).

**Rationale:** Outline provides cross-phase coherence; per-phase expansion provides earlier feedback. Quality preserved: outline catches structure issues before expensive full generation.

**Impact:** Earlier feedback, better cross-phase coherence, reduced rework.

### Phase-by-Phase Review Pattern

**Decision Date:** 2026-02-05

**Decision:** For each phase: generate → delegate to reviewer (fix-all) → check for escalation → proceed.

**Anti-pattern:** Generate all phase files, then review/fix at end (batch optimization).

**Root cause:** Agent rationalized "saving time" by batching file generation.

**Key insight:** "For each phase" means iterative loop, not parallel generation.

**Impact:** Prevents drift accumulation, enables early course correction.

### Review Agent Fix-All Pattern

**Decision Date:** 2026-02-05

**Decision:** Review agents autofix everything, escalate unfixable issues.

**Three functions:**
1. Write review as audit trail (enables deviation monitoring)
2. Fix ALL issues directly (critical, major, minor)
3. Escalate unfixable to caller

**Escalation format:** Return filepath + "ESCALATION: N unfixable issues require attention"

**Applies to:** tdd-plan-reviewer, outline-review-agent, runbook-outline-review-agent, design-vet-agent

**Rationale:** Document fixes are low-risk; implementation fixes (vet-agent) remain review-only due to higher risk.

**Impact:** Caller handles escalation only, not routine fixes. Audit trail preserved for process improvement.

### Recommendations Inline Transmission

**Decision Date:** 2026-02-05

**Decision:** Append "Expansion Guidance" section to artifact being consumed (inline), not separate report.

**Anti-pattern:** Review agent writes recommendations to report file that gets ignored.

**Rationale:** Phase expansion reads outline; guidance co-located ensures consumption.

**Example:** runbook-outline-review-agent appends guidance to outline.md directly.

**Impact:** Guidance reaches executor, not lost in separate report file.

### Prose Test Descriptions Save Tokens

**Decision Date:** 2026-02-05

**Decision:** Use prose descriptions with specific assertions in TDD RED phases, not full test code.

**Anti-pattern:** Full test code in runbook RED phases (copy-paste pattern).

**Token math:** Prose saves ~80% planning output tokens; haiku generates test code during execution anyway.

**Quality gate:** Prose must be behaviorally specific — "contains 🥈 emoji" not "returns correct value". tdd-plan-reviewer validates prose quality.

**Impact:** Significant token savings in planning phase without quality loss.

### Complexity Before Expansion

**Decision Date:** 2026-02-05

**Decision:** Check complexity BEFORE expansion; callback to previous level if too large.

**Anti-pattern:** Expand all cycles regardless of complexity, discover problems late.

**Callback levels:** step → outline → design → design outline → requirements (human input)

**Fast paths:** Pattern cycles get template+variations; trivial phases get inline instructions.

**Key insight:** Complexity assessment is planning concern (sonnet/opus), not executor concern (haiku). Haiku optimizes for completion, not scope management.

**Impact:** Catch structure problems early, prevent executor overload.

### Consolidation Gates Reduce Orchestrator Overhead

**Decision Date:** 2026-02-05

**Decision:** Merge trivial work with adjacent complexity at two gates.

**Anti-pattern:** Trivial cycles left as standalone steps (config change, single constant).

**Gates:**
- **Gate 1 (Phase 1.6):** After outline — merge trivial phases with adjacent phases
- **Gate 2 (Phase 4.5):** After assembly — merge isolated cycles with related features

**Constraints:** Never cross phases, keep merged cycles ≤5 assertions, preserve test isolation.

**Rationale:** Haiku can handle "update constant X then implement feature Y" in one delegation.

**Impact:** Reduced orchestrator overhead for trivial work without losing test granularity.

### Workflow Feedback Loop Insights

**Decision Date:** 2026-02-05

**Decision:** Apply feedback loop principles to planning workflows.

**Principles:**
- **Alignment:** Review all agent output against requirements from clean context
- **Autofix:** Apply fixes immediately (don't rely on caller reading recommendations)
- **Outline:** Use staged expansion with alignment correction to prevent drift
- **Complexity gate:** Check before expansion, callback if too large

**Impact:** Self-correcting planning process prevents late-stage rework.

### Dogfooding Validates Design

**Decision Date:** 2026-02-05

**Decision:** Apply new process to its own planning (self-referential validation).

**Pattern:** Use the process you're designing to plan its own implementation.

**Example:** workflow-feedback-loops runbook planned using the feedback loop process it describes.

**Benefit:** Catches design issues before formal implementation. Phase-by-phase expansion with delegated reviews worked smoothly.

**Impact:** Design validation through practical application.

## .TDD Workflow Patterns

### TDD GREEN Behavioral Descriptions

**Decision Date:** 2026-02-05

**Decision:** Describe behavioral requirements with approach hints in GREEN phase, not complete implementation code.

**Anti-pattern:** Writing complete implementation code in GREEN phase that can be copied verbatim.

**Correct pattern:** Describe behavioral requirements, provide approach hints, specify file location.

**Structure:** Behavior (WHAT code must DO) / Approach (high-level HOW) / Hint (specific technique)

**Rationale:** TDD discipline requires executor to WRITE code satisfying tests, not transcribe prescribed code.

**Impact:** Enforces test-first methodology, prevents copy-paste implementations.

## .Model Selection Patterns

### Efficient Model Analysis Requires Verification

**Decision Date:** 2026-02-05

**Decision:** Use haiku for execution tasks, delegate architectural analysis to sonnet/opus, verify results.

**Anti-pattern:** Accepting haiku/sonnet analysis for critical architectural decisions without review.

**Example:** Haiku structural header analysis was incorrect (marked semantic headers as structural); sonnet analysis was correct.

**Rationale:** Efficient models optimize for speed, may miss nuance in architectural distinctions.

**Impact:** Appropriate model selection for analysis vs execution tasks.
