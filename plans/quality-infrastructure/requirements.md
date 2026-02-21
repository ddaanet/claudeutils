# Quality Infrastructure Reform — Requirements

## Context

Line-limit precommit failures produce recurring wrong responses: output compression, premature file splitting, lint circumvention via intermediate variables. Investigation revealed systemic issues across exception handling, formatter interaction, rule placement, and naming.

Grounding report: `plans/reports/code-density-grounding.md`
User feedback: annotated `src/claudeutils/cli.py` (12 anti-pattern markers, in working tree — `git diff src/claudeutils/cli.py` or `git checkout -- src/claudeutils/cli.py` to discard)

## FR-1: Deslop Restructuring

Split `agent-core/fragments/deslop.md` into two targets:

**Prose rules → `communication.md` (ambient):**
- State information directly (no hedging/framing/preamble)
- Answer immediately (skip acknowledgments)
- Reference, never recap
- Let results speak
- Commit to your answer

**Code rules → pipeline-only (correct agent, refactoring, merge):**
- Docstrings only when non-obvious
- Comments explain why, never what
- No section banners
- Abstractions only when second use exists
- Guard only at trust boundaries
- Expose fields directly until access control needed
- Build for current requirements

**Principle line** ("Slop is the gap...") — move to communication.md or discard.

Remove `deslop.md` from CLAUDE.md `@`-references after migration. Inject code deslop into correct agent context (mechanism TBD in design — skills frontmatter, inline, or fragment reference).

## FR-2: Code Density Decisions

Add entries to `agents/decisions/cli.md` for 5 grounded principles. Each entry states the **general principle first**, then the project implementation as instance (per `/ground` framing rule):

1. **Expected state checks return booleans** — normal program states checked with boolean returns, not exceptions. Project: `_git_ok(*args) -> bool` for exit-code checks.
2. **Consolidate display and exit** — error termination as single call, not display+exit sequence. Project: `_fail(msg, code=1) -> Never`.
3. **Formatter expansion signals abstraction need** — 5+ lines after opinionated formatting = too many parameters for inline use. Extract helper with default kwargs.
4. **Exceptions for exceptional events only** — custom exception classes, not `ValueError`. Lint rule satisfaction via proper design (custom class), not circumvention (intermediate `msg` variable).
5. **Error handling layers don't overlap** — context collection at failure site, display at top level. Never both.

Add corresponding `/when` triggers to `agents/memory-index.md`.

## FR-3: Rename Review/Correct Infrastructure

Noun-based agent names — drop `-agent` suffix. Domain prefix where disambiguation matters. All review agents that apply fixes are "correctors"; review-only and audit-only agents are "reviewers"/"auditors".

Rename across the entire project:

| Old | New | Rationale |
|-----|-----|-----------|
| `vet-fix-agent` | `corrector` | General-purpose corrector (review+fix) |
| `vet-agent` | `reviewer` | General-purpose reviewer (review-only) |
| `design-vet-agent` | `design-corrector` | Design doc corrector (opus) |
| `outline-review-agent` | `outline-corrector` | Design outline corrector (Phase A.5) |
| `runbook-outline-review-agent` | `runbook-outline-corrector` | Runbook outline corrector (Phase 1.5) |
| `plan-reviewer` | `runbook-corrector` | Runbook phase file corrector |
| `review-tdd-process` | `tdd-auditor` | TDD process audit (assessment-only) |
| `vet-taxonomy.md` | *(embed in corrector)* | Not an agent — embed status table inline |
| `vet-fix-report` | `correction` | Report naming convention |
| `vet-requirement.md` | TBD (may be absorbed into pipeline) | Fragment |
| `/vet` skill | `/review` skill | Skill directory |

**Open question:** Is `reviewer` (review-only, no fixes) still used in practice? Pending empirical evaluation — audit call sites before design.

### Rename Brainstorm — Impact Inventory

**Agent definitions (7 agents + 1 embed):**
- `agent-core/agents/vet-fix-agent.md` → `corrector.md`
- `agent-core/agents/vet-agent.md` → `reviewer.md`
- `agent-core/agents/design-vet-agent.md` → `design-corrector.md`
- `agent-core/agents/outline-review-agent.md` → `outline-corrector.md`
- `agent-core/agents/runbook-outline-review-agent.md` → `runbook-outline-corrector.md`
- `agent-core/agents/plan-reviewer.md` → `runbook-corrector.md`
- `agent-core/agents/review-tdd-process.md` → `tdd-auditor.md`
- `agent-core/agents/vet-taxonomy.md` → embed in `corrector.md`, delete file

**Agent references in other agents (4 files):**
- `tdd-auditor.md` (was review-tdd-process) — references corrector
- `runbook-corrector.md` (was plan-reviewer) — references corrector
- `runbook-outline-corrector.md` — references corrector
- `outline-corrector.md` — references corrector

**Skills (7 files):**
- `commit/SKILL.md` — vet-requirement reference
- `runbook/references/examples.md` — vet delegation examples
- `runbook/references/general-patterns.md` — vet patterns
- `design/SKILL.md` — design-vet-agent reference
- `deliverable-review/SKILL.md` — vet-fix-agent delegation
- `orchestrate/SKILL.md` — vet delegation
- `doc-writing/SKILL.md` — vet reference
- `vet/SKILL.md` → rename to `review/SKILL.md`
- `plugin-dev-validation/SKILL.md` — vet reference

**Fragments (1 file):**
- `vet-requirement.md` — rename or absorb into pipeline (decision depends on FR-1 deslop restructuring — if quality rules move to pipeline, vet-requirement may merge with correct agent context)

**Docs (2 files):**
- `tdd-workflow.md` — vet references
- `general-workflow.md` — vet references

**Other agent-core (2 files):**
- `README.md` — agent inventory
- `bin/focus-session.py` — vet reference

**Decision files (6 files):**
- `pipeline-contracts.md` — vet-fix-agent routing table, UNFIXABLE protocol
- `operational-practices.md` — vet delegation learnings
- `workflow-optimization.md` — vet context reuse
- `workflow-advanced.md` — vet delegation
- `project-config.md` — agent configuration
- `orchestration-execution.md` — vet delegation patterns

**Memory index (1 file):**
- `agents/memory-index.md` — /when triggers referencing vet

**Session files (2 files):**
- `agents/session.md` — task descriptions referencing vet
- `agents/learnings.md` — vet learnings

**Rules (1 file):**
- `.claude/rules/plugin-dev-validation.md` — vet reference

**Symlinks:**
- `.claude/agents/` and `.claude/skills/` — regenerated via `just sync-to-parent`

**Total: ~37 files, ~26 in agent-core, ~10 in agents/decisions, ~1 in .claude**

### Rename Constraints

- **Requires restart** — agent definitions load at session start
- **Subagent_type values** — Task tool's `subagent_type` parameter uses agent filenames. Rename must be atomic (all references updated before symlink sync)
- **Git history** — `git mv` preserves blame history. Prefer `git mv` over delete+create.
- **Symlinks** — `just sync-to-parent` regenerates all symlinks from agent-core. Run after renames.
- **Cross-reference consistency** — text search for old names post-rename to catch stragglers

### Terminology Table

| Context | Old Term | New Term |
|---------|----------|----------|
| General corrector (review+fix) | vet-fix-agent | corrector |
| General reviewer (read-only) | vet-agent | reviewer |
| Design corrector | design-vet-agent | design-corrector |
| Design outline corrector | outline-review-agent | outline-corrector |
| Runbook outline corrector | runbook-outline-review-agent | runbook-outline-corrector |
| Runbook phase corrector | plan-reviewer | runbook-corrector |
| TDD process auditor | review-tdd-process | tdd-auditor |
| Status taxonomy | vet-taxonomy | *(embedded in corrector)* |
| Review report | vet report | review report |
| Fix report | vet-fix report | correction |
| Process | vetting | review/correction |
| Fragment | vet-requirement | review-requirement or absorbed |
| Skill | /vet | /review |

## FR-4: Code Refactoring Scope

Implementation targets for the codebase quality sweep task (already pending):

- Add `_git_ok(*args) -> bool` to `src/claudeutils/worktree/utils.py`
- Add `_fail(msg, code=1) -> Never` to `src/claudeutils/worktree/utils.py`
- Replace 13 raw `subprocess.run(["git", ...])` calls with `_git_ok` across cli.py, merge.py, utils.py
- Replace 18 `click.echo(err=True) + raise SystemExit` patterns with `_fail` across cli.py, merge.py
- Replace exception-as-control-flow patterns (3 sites) with `_git_ok` boolean checks
- Custom exception classes for domain errors in `src/claudeutils/cli.py` (SessionNotFoundError, etc.)

## Dependencies

- FR-1 (deslop restructuring) and FR-3 (rename) interact at `vet-requirement.md` — fragment may be absorbed or renamed
- FR-3 (rename) requires restart after completion
- FR-4 (code refactoring) is independent — can execute in parallel with FR-1/FR-3
- FR-2 (decisions) should follow FR-1 and FR-3 — entries should use new terminology

## Non-Requirements

- No changes to exit code semantics (1=error, 2=safety gate)
- No changes to `_git()` helper signature
- No new agent definitions — only renaming existing ones
- Click exception hierarchy (`ClickException`, `UsageError`) evaluated and rejected — `_fail()` is simpler for this project's exit code semantics
