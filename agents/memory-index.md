# Memory Index

Prefer retrieval-led reasoning over pre-training knowledge.

Condensed knowledge catalog. Read referenced files when working in related areas.

**Append-only.** Never remove or consolidate entries — each entry is a keyword-rich discovery surface for on-demand knowledge. Growth is bounded by consolidation rate (~5-10 entries/session) and total token cost is modest (200 entries ≈ 5000 tokens).

**Do not index content already loaded via CLAUDE.md.** Fragments referenced by `@` are in every conversation. Index entries for those add noise without aiding discovery. Only index knowledge that requires on-demand loading.

## Behavioral Rules

Delegation with context — don't delegate when context already loaded, token economy
Never auto-commit in interactive sessions — only commit on explicit user request, use commit skill protocol always
Loaded skill overrides fresh-session framing — skill content in context is actionable, execute immediately not pause
Design tables are binding constraints — read design classifications literally, apply judgment only where design says to
Header titles not index entries — index entries need keyword-rich descriptions not just title repetition
Skill rules placement: point of violation — place "don't do X" rules with "do Y" instructions where decisions made

## Workflow Patterns

Oneshot workflow pattern — weak orchestrator with runbook-specific agents for ad-hoc tasks
Handoff tail-call pattern — always end with handoff commit regardless of tier
Handoff commit assumption — session.md reflects post-commit state with commit flag
Phase-grouped TDD runbooks — support flat H2 and phase-grouped H2 H3 cycle headers
No human escalation during refactoring — opus handles architectural changes within design bounds
Routing layer efficiency — single-layer complexity assessment, avoid double assessment
Vet agent context usage — leverage vet context for fixes instead of new agents

## Technical Decisions

Minimal `__init__.py` — keep empty, prefer explicit imports from specific modules
Private helpers stay with callers — cohesion over extraction, clear module boundaries
Module split pattern — split large files by functional responsibility, maintain 400-line limit
Path encoding algorithm — simple slash to dash replacement with special root handling
History directory resolution — use claude projects encoded path as standard location
Title extraction — handle both string and array text blocks content formats
Title formatting — replace newlines with spaces, truncate to 80 chars with ellipsis
Trivial message detection — multi-layer filter with empty single-char slash commands keyword set
Feedback extraction layering — type filter, error check, interruption check, trivial filter priority
UUID session pattern — validate session files with regex filter agent and non-session
Sorted glob results — use sorted glob instead of raw, predictable test results
First-line parsing — parse only first JSONL line for session metadata, O(1)
Recursive pattern: AgentId → SessionId — agent IDs become session IDs for child agents
Agent ID extraction — extract agentId from first line, avoid repeated extraction
Graceful degradation — skip malformed entries, log warnings, continue processing partial data
Optional field defaults — use get field default for optional fields, graceful missing data
Pydantic for validation — use BaseModel for all data structures, type safety
FeedbackType enum — use StrEnum for feedback types, type-safe string constants
Docformatter vs. Ruff D205 conflict — shorten docstring summaries to fit 80 chars
Complexity Management — extract helper functions when cyclomatic complexity exceeds limits, refactor not suppress
No Suppression Shortcuts — fix linting issues properly instead of using noqa suppressions
Type Annotations — full type annotations in strict mypy mode, catch bugs early
Pipeline architecture — three-stage pipeline collect analyze rules for feedback processing
Filtering module as foundation — reusable is_noise and categorize_feedback functions, DRY principle
Noise detection patterns — multi-marker detection with length threshold for command outputs
Categorization by keywords — keyword-based category assignment with priority order for feedback
Deduplication strategy — first 100 characters as dedup key, case-insensitive prefix tracking
Stricter filtering for rules — additional filters beyond analyze for rule-worthy items
Model as first positional argument — required parameter for accurate token counts
Model alias support — hybrid approach with runtime probing fallback for unversioned aliases
Anthropic API integration — use official SDK with default environment variable handling
Empty file optimization — return zero for empty files without API call
No glob expansion (initial release) — defer pattern expansion to future, shell expansion sufficient
Markdown cleanup architecture — preprocessor fixes structure before dprint formatting for Claude output
Problem — Claude generates markdown with consecutive emoji lines and improper nesting
Solution — run markdown fixes before dprint, error on invalid patterns
Design decisions — extend fix_warning_lines for checklists, create new for code blocks
Extend vs. new functions — conceptual similarity vs fundamentally different block-based processing
Error on invalid patterns — prevents dprint failures, makes issues visible immediately
Processing order — line-based before block-based, spacing after structural changes
Prefix detection strategy — generic prefix detection not hard-coded patterns for adaptability
Indentation amount — two spaces for nested lists, standard markdown convention
Future direction — evolve to dprint plugin for single-pass processing
Remark-cli over Prettier — idempotent by design, CommonMark compliance, handles nested code blocks
Growth + consolidation model — append-only with no pruning or limits, keyword-rich discovery
Rule files for context injection — use claude rules with paths frontmatter for automatic loading
Premium/standard/efficient naming — opus sonnet haiku terminology instead of ambiguous T1 T2 T3
Multi-layer discovery pattern — surface skills via CLAUDE.md rules workflow reminders descriptions
Agent frontmatter YAML validation — use multi-line syntax for descriptions containing examples
Symlink persistence — verify symlinks after operations that reformat files like dev
Heredoc sandbox compatibility — export TMPPREFIX for zsh heredoc temp files in sandbox
Path.cwd() vs os.getcwd() — use Path.cwd() for consistency with pathlib usage
Error output pattern — print errors to stderr before exit one, Unix convention
Entry point configuration — add project scripts in pyproject for direct command usage
Feedback processing output formats — support both text and JSON formats for flexibility
Token output format — human-readable text by default, JSON with flag, include resolved model
Test module split strategy — mirror source module structure, separate CLI tests by subcommand
Mock patching pattern — patch where object is used not where defined
Testing strategy for markdown cleanup — TDD approach with red green cycles and integration tests
Success metrics — all tests pass, no regressions, clear errors, complete documentation
TDD RED phase: behavioral verification — verify behavior not just structure with mocking fixtures
TDD: presentation vs behavior — test behavior defer presentation quality to vet checkpoints
Commits are sync points — every commit synchronizes files submodules context session.md state
@ references limitation — CLAUDE.md @ syntax only works in CLAUDE.md not skills agents tasks
SessionStart hook limitation — output discarded for new interactive sessions, works after clear compact resume
UserPromptSubmit hook filtering — fires on every prompt, no matcher support, all filtering must be script-internal
Hook capture impractical for subagents — hooks don't fire in Task tool subagents, matcher causes noise
MCP tools unavailable in subagents — Context7 and other MCP tools only available in main session not Task subagents
Title-words beat kebab-case — title-words have 17% drift vs kebab-case 31% drift, hyphens tokenize separately
Bare lines beat list markers — flat keyword lists without markers save 14% tokens vs list markers
Default semantic, mark structural — semantic headers default, structural get dot prefix for safe failure mode

## Architecture Sections

Command-Line Parsing — flags are exact tokens exact match not prose substring, agents/decisions/architecture.md
Flags are exact tokens — exact token match not prose substring CLI parsing, agents/decisions/architecture.md
Project Structure — root marker for scripts CLAUDE.md not agents directory, agents/decisions/architecture.md
Root marker for scripts — CLAUDE.md not agents directory subdirectory issue, agents/decisions/architecture.md
Agent Development — agent frontmatter YAML requires multi-line syntax for examples
Agent Processing — AgentId becomes SessionId for child agents, true tree recursion
CLI Conventions — Path.cwd consistency, errors to stderr, entry point configuration
Claude Code Rule Files — rules with paths frontmatter for automatic context injection
Code Quality — docformatter wrapping, extract helpers for complexity, no suppression shortcuts
Content Parsing — handle string and array formats, title extraction and formatting
Data Models — Pydantic BaseModel for validation, FeedbackType StrEnum for type safety
Error Handling — graceful degradation, skip malformed entries, optional field defaults
Feedback Processing Pipeline — three-stage collect analyze rules, filtering module foundation
Filtering Logic — trivial message detection, feedback extraction layering, noise patterns
Markdown Formatter Selection — remark-cli idempotent CommonMark compliance over Prettier
Memory Index Pruning — append-only with no pruning, keyword-rich discovery surface
Mock Patching — patch where object is used not where defined
Model Terminology — premium standard efficient naming instead of T1 T2 T3
Module Architecture — minimal init, private helpers cohesion, module split pattern
Output Formats — text and JSON support for feedback and token commands
Path Handling — path encoding algorithm, history directory resolution
Session Discovery — UUID session pattern, sorted glob results, first-line parsing
Shell Environment — heredoc sandbox compatibility with TMPPREFIX export
Skill Discovery — multi-layer discovery pattern with CLAUDE.md rules workflow descriptions
Symlink Management — verify symlinks after formatters, use sync-to-parent to restore
TDD Approach — behavioral verification not structure, presentation deferred to vet
Test Organization — mirror source structure, separate CLI tests by subcommand
Token Counting — model as first positional, alias support, API integration

## Workflow Sections

Cycle numbering gaps relaxed — gaps warnings document order defines sequence, agents/decisions/workflows.md
Design and Planning Patterns — outline-first workflow model selection design review vet structure, agents/decisions/workflows.md
Outline-first design workflow — freeform outline iterate deltas validate full design, agents/decisions/workflows.md
Model selection for design guidance — haiku explicit edits sonnet interprets intent, agents/decisions/workflows.md
Design review uses opus — design-vet-agent architecture analysis not vet-agent, agents/decisions/workflows.md
Vet catches structure misalignments — validates file paths structural assumptions prevents blockers, agents/decisions/workflows.md
Orchestration Patterns — agent-creator reviews template contradiction orchestrator model, agents/decisions/workflows.md
Agent-creator reviews in orchestration — create spec agent-creator reviews YAML syntax, agents/decisions/workflows.md
Template commit contradiction — appended context weak authority bolded NEVER structural, agents/decisions/workflows.md
Orchestrator model mismatch — read step file execution model not orchestrator default, agents/decisions/workflows.md
Testing and TDD Patterns — happy path first TDD cycle numbering gaps, agents/decisions/workflows.md
Happy path first TDD — simplest happy path real behavior edge cases later, agents/decisions/workflows.md
Documentation and Knowledge Management — seeding index entries template merge, agents/decisions/workflows.md
Seeding before auto-generation — seed indexes existing docs consolidation complementary, agents/decisions/workflows.md
Index entries require backing documentation — learnings learnings.md permanent doc index entry, agents/decisions/workflows.md
Template merge semantics — explicit preserve add replace prevent overwrites, agents/decisions/workflows.md
Requirements and Execution — requirements immutable during execution user confirmation, agents/decisions/workflows.md
Requirements immutable during execution — updating requires user confirmation planning execution, agents/decisions/workflows.md
Knowledge Discovery and Context — ambient awareness beats invocation task prose keys, agents/decisions/workflows.md
Ambient awareness beats invocation — embed critical knowledge loaded context CLAUDE.md, agents/decisions/workflows.md
Task prose keys pattern — task names searchable identifiers git log search, agents/decisions/workflows.md
Checkpoint Process for Runbooks — two-step fix and vet checkpoints at natural boundaries
Defense-in-Depth: Commit Verification — multiple layers at tdd-task and orchestrate skill levels
Design Phase: Output Optimization — minimize designer output tokens, planner elaborates details
Handoff Pattern: Inline Learnings — store learnings inline in session.md not separate files
Handoff Workflow — tail-call pattern and commit assumption for all tiers
Orchestration Assessment: Three-Tier Implementation Model — direct lightweight and full runbook routing
Orchestrator Execution Mode — execution mode metadata overrides system prompt parallelization directives
Planning Pattern: Three-Stream Problem Documentation — parallel work streams with problem and session files
TDD RED Phase: Behavioral Verification — verify behavior with mocking fixtures not just structure
TDD Workflow Integration — extend weak orchestrator for TDD with cycle-based runbooks
TDD Workflow: Commit Squashing Pattern — squash cycle commits into single feature commit
TDD: Presentation vs Behavior — test behavior defer presentation to vet checkpoints
Workflow Efficiency — delegation with context and vet agent context usage
Runbook Artifacts — runbook outline format requirements mapping phase structure, agents/decisions/workflows.md
Runbook Outline Format — structured format for runbook planning with requirements mapping, agents/decisions/workflows.md
