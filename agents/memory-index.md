# Memory Index

Condensed knowledge catalog. Read referenced files when working in related areas.

**Append-only.** Never remove or consolidate entries — each entry is a keyword-rich discovery surface for on-demand knowledge. Growth is bounded by consolidation rate (~5-10 entries/session) and total token cost is modest (200 entries ≈ 5000 tokens).

## Behavioral Rules

- Tool batching enforcement is unsolved - documentation unreliable, hookify rules add bloat, cost-benefit unclear → `agents/learnings.md`
- Script-First Evaluation: check project recipes (just --list) before ad-hoc commands - recipes encode institutional knowledge → `agent-core/fragments/project-tooling.md`
- Don't delegate when context already loaded - delegation makes agent re-read everything, wastes tokens → `agents/decisions/workflows.md`
- Use AskUserQuestion tool for multi-option choices, not prose questions - y/n binds to last question creating ambiguity → `agent-core/fragments/communication.md`
- Three-tier assessment (direct/lightweight delegation/full runbook) determines implementation approach based on complexity → `agents/decisions/workflows.md`
- Automation directives need unambiguous boundaries - use explicit prohibitions not vague "drive to completion" → `agent-core/fragments/communication.md`

## Workflow Patterns

- Weak orchestrator pattern: task agents report to files (quiet execution) to prevent context pollution → `agents/decisions/workflows.md`
- TDD workflow: RED (failing tests) → GREEN (behavior hints, not prescriptive code) → REFACTOR cycles → `agents/decisions/workflows.md`
- Handoff pattern: store learnings inline in session.md, not separate file system - simpler to edit and update → `agents/decisions/workflows.md`
- Tier 1 (direct), Tier 2 (lightweight Task delegation), Tier 3 (full runbook with prepare-runbook.py) → `agents/decisions/workflows.md`
- Checkpoint process: fix checkpoint (just dev) then vet checkpoint at natural boundaries, not per-step → `agents/decisions/workflows.md`
- Commit verification defense-in-depth: tdd-task checks commit content, orchestrate checks working tree state → `agents/decisions/workflows.md`
- TDD commit squashing: backup tag → reset --soft → squashed commit, preserves cycle detail in reports → `agents/decisions/workflows.md`
- All tiers end with /handoff --commit - handoff captures context/learnings regardless of session restart need → `agents/decisions/workflows.md`
- Handoff --commit assumes commit succeeds - session.md reflects post-commit state, no pending commit language → `agents/decisions/workflows.md`
- Leverage vet agent context for fixes instead of launching new agents - saves token waste from re-reading → `agents/decisions/workflows.md`
- Single-layer complexity assessment - no double-assessment between entry point and planning skill → `agents/decisions/workflows.md`

## Technical Decisions

- Module architecture: minimal __init__.py (1 line), private helpers stay with callers for cohesion → `agents/decisions/architecture.md`
- Path encoding: simple / → - character replacement, special root handling ("/" → "-") → `agents/decisions/architecture.md`
- Pydantic BaseModel for all data structures - automatic validation, JSON serialization, type safety → `agents/decisions/architecture.md`
- Complexity management: extract helpers when exceeding limits, fix properly instead of # noqa suppressions → `agents/decisions/architecture.md`
- Feedback processing: three-stage pipeline (collect → analyze → rules) with noise filtering and deduplication → `agents/decisions/architecture.md`
- Markdown formatter: remark-cli chosen over Prettier - idempotent, CommonMark compliant, preserves YAML → `agents/decisions/architecture.md`
- Memory index is append-only with no limit - consolidation loses keyword discovery, growth bounded naturally → `agents/decisions/architecture.md`
- Claude Code rule files with path frontmatter for automatic context injection when editing domain files → `agents/decisions/architecture.md`
- Model terminology: premium (Opus), standard (Sonnet), efficient (Haiku) - clearer than T1/T2/T3 → `agents/decisions/architecture.md`
- Skill discovery needs 4 layers - CLAUDE.md fragment, path rules, in-workflow reminders, directive description → `agents/decisions/architecture.md`
- Agent frontmatter YAML must use multi-line syntax (|) for descriptions with examples to prevent parse errors → `agents/decisions/architecture.md`
- Symlinks can become regular files after formatters - verify symlinks after just dev, ruff format operations → `agents/decisions/architecture.md`
- Heredocs work in sandbox via TMPPREFIX="${TMPDIR:-/tmp}/zsh" in claude-env.sh (zsh-specific fix) → `agents/decisions/architecture.md`

## Tool & Infrastructure

- Sandbox bypass requires both permissions.allow (no prompt) and dangerouslyDisableSandbox (reliable bypass) → `agent-core/fragments/sandbox-exemptions.md`
- prepare-runbook.py must git add its own artifacts - script owns knowledge of what it creates (IMPLEMENTED) → `agents/learnings.md`
- Submodule commits: when modified, commit submodule first then stage pointer in parent to avoid sync drift (IMPLEMENTED) → `agents/learnings.md`
- Hook development: use both additionalContext (agent sees) and systemMessage (user sees), YAML must be strict → `agent-core/fragments/claude-config-layout.md`
- Session shortcuts: x (smart execute/resume), xc (execute + commit), r (strict resume), s (status display) → `agent-core/fragments/execute-rule.md`
- Vet agent selection: vet-agent (review only, Tier 1/2) vs vet-fix-agent (review + fix, Tier 3 orchestration) → `agent-core/fragments/vet-requirement.md`
- TDD RED phase tests must verify behavior with mocking/fixtures, not just structure (exit code, key existence) → `agents/decisions/testing.md`
- UserPromptSubmit hooks cannot rewrite prompts - only add additionalContext or block, no matcher support → `agent-core/fragments/claude-config-layout.md`
- Hooks only active in main session - do NOT fire in sub-agents spawned via Task tool → `agent-core/fragments/claude-config-layout.md`
- Hook security: use exact match for restore operations, not startswith() - prevents shell operator exploitation → `agent-core/fragments/claude-config-layout.md`
- Case-sensitive shortcuts unreliable for LLM interpretation - use distinct tokens (xc vs x) not case (X vs x) → `agent-core/fragments/execute-rule.md`
- Shortcut systems need two layers - hook for exact-match expansion, fragment for inline vocabulary comprehension → `agent-core/fragments/execute-rule.md`
