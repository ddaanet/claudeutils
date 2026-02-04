# Jobs

Plan lifecycle tracking. Updated when plans change status.

**Status:** `requirements` → `designed` → `planned` → `complete`

## Complete (Archived)

*14 plans completed and deleted. Git history preserves all designs/reports.*

Use `git log --all --oneline -- plans/<name>/` to find commits, `git show <hash>:<path>` to retrieve files.

**Recent:**
- `design-workflow-enhancement` — Outline-first design workflow, documentation checkpoint, requirements validation
- `feedback-fixes` — Handoff quality, tdd-task restructure, submodule-safety hook
- `task-prose-keys` — Replaced hash tokens with prose key validation (validate-tasks.py)

**One-off documents (complete):**
- `majestic-herding-rain.md` — Gitmoji integration (implemented in commit skill)
- `robust-waddling-bunny.md` — Memory index D-3 RCA (fix applied)
- `review-requirements-consistency.md` — Requirements review (one-time)

## In Progress

| Plan | Status | Current Step | Task Key |
|------|--------|--------------|----------|
| claude-tools-recovery | planned | Re-testing phase | — |
| claude-tools-rewrite | planned | Paused (stubs) | — |

## Designed

| Plan | Notes |
|------|-------|
| commit-unification | May be superseded by commit-rca-fixes |
| prompt-composer | Oldest plan, at risk |

## Requirements

| Plan | Task Key | Notes |
|------|----------|-------|
| continuation-passing | — | Opus design needed |
| handoff-lite-issue | — | Issue investigation |
| handoff-validation | — | Requires continuation-passing |
| markdown | — | Markdown cleanup test corpus |
| requirements-skill | — | New skill |
| runbook-identifiers | — | Purpose unclear |
| validator-consolidation | — | Move to claudeutils package |

