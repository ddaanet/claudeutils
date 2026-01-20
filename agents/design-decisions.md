# Design Decisions

Key architectural decisions made during project development.

## Oneshot Workflow Pattern (Completed 2026-01-19)

**Decision:** Implement and validate weak orchestrator pattern with runbook-specific agents for ad-hoc task execution.

**Status:** Complete - All phases delivered, pattern validated, archived to `plans/archive/oneshot-workflow/`

**Key Components:**
- Baseline task agent (`agent-core/agents/quiet-task.md`)
- Runbook preparation script (`agent-core/bin/prepare-runbook.py`)
- 5 skills: `/design`, `/plan-adhoc`, `/orchestrate`, `/vet`, `/remember`
- Complete documentation (`agents/workflow.md`)

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

**Archival:**
- Completion report: `plans/archive/oneshot-workflow/completion-report.md`
- All design and execution artifacts preserved
- Pattern ready for reuse via agent-core skills

**Impact:**
- Production-ready workflow for ad-hoc tasks
- Reduced context overhead through specialized agents
- Standardized terminology across documentation
- Reusable components via agent-core submodule

## TDD Workflow Integration (Completed 2026-01-19)

**Decision:** Extend weak orchestrator pattern to support TDD methodology for feature development.

**Status:** Complete - All 8 steps delivered, production-ready

**Key Components:**
- TDD workflow documentation (`agent-core/agents/tdd-workflow.md`)
- TDD baseline agent (`agent-core/agents/tdd-task.md`)
- `/plan-tdd` skill with 4-point preparation (Design, Phases, Model, Cycles)
- Cycle-based runbooks supporting RED/GREEN/REFACTOR progression
- TDD task agent pattern with cycle-aware instruction sets

**Architecture:**
- Unified design entry point (`/design` skill) supports both oneshot and TDD modes
- RED phase: Write failing tests, document intent
- GREEN phase: Implement minimal working solution
- REFACTOR phase: Improve code quality while maintaining tests
- Cycle-aware task delegation with scoped runbooks per cycle
- Quiet execution pattern preserves orchestrator context

**Key Decisions:**
- Cycle-based splitting: Each RED/GREEN/REFACTOR as separate runbook cycle
- Model assignment: Sonnet for TDD planning, haiku for implementation, opus for design
- Deduplication: Use 4-point prep to avoid overlap with oneshot workflow
- Testing focus: Behavioral verification with full test coverage
- Progressive discovery: Documentation read only when executing TDD workflow

**Impact:**
- Production-ready TDD workflow for test-first development
- Enforced test-first methodology via /plan-tdd skill
- Reusable cycle patterns via agent-core documentation
- Consistent terminology across test and implementation phases

**Implementation Details:**
- See `agents/implementation-notes.md` for Python package implementation
- See `plans/archive/markdown-cleanup/` for markdown preprocessing feature

## Documentation Organization

Comprehensive documentation organized by concern:

**Core Architecture & Instructions:**
- See `agents/design-decisions.md` for high-level architectural decisions and workflow patterns
- See `agents/implementation-notes.md` for detailed implementation decisions
- See `agents/cli-design.md` for CLI-specific patterns and conventions
- See `agents/test-strategy.md` for testing conventions and patterns

**Feature Documentation:**
- See `plans/archive/*/design.md` for completed feature designs

**Progressive Discovery Note:** Don't preload all documentation. Read specific guides only when implementing similar features or patterns.
