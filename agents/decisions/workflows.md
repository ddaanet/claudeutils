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
