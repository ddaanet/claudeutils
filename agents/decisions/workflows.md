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
