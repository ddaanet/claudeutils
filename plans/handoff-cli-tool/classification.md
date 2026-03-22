# Classification: Fix handoff-cli round 2 findings

**Date:** 2026-03-22
**Input:** plans/handoff-cli-tool/reports/deliverable-review.md (round 2: 1C/4M/6m)
**Plan status:** rework
**Round:** 2 (prior classification was round 1: 5C/11M/12m)

## Composite Decomposition

| # | Finding | Behavioral Code? | Classification | Destination |
|---|---------|-------------------|----------------|-------------|
| C#1 | `_commit_submodule` returncode unchecked | Yes | Moderate | production |
| M#2 | SKILL.md missing `claudeutils:*` | No | Simple | agentic-prose |
| M#3 | `_error()` not informative (S-3) | Yes | Moderate | production |
| M#5 | `_worktree ls` stale dedup | Yes | Moderate | production |
| m-1 | Dead `render_next` | No | Simple | production |
| m-2 | `▶` doesn't skip worktree tasks | Yes | Simple | production |
| m-3 | `_is_dirty()` strip bug | Yes | Simple | production |
| m-4 | Dead `step_reached` | No | Simple | production |
| m-5 | Old section name bypass | Yes | Simple | production |
| m-6 | Weak test `or` assertion | No | Simple | production |

**Split out:** M#4 (skill-CLI integration) → `plans/skill-cli-integration/` (Complex, opus)

## Overall

- **Classification:** Moderate (composite)
- **Implementation certainty:** High
- **Requirement stability:** High
- **Behavioral code check:** Yes (C#1, M#3, M#5, m-2, m-3, m-5)
- **Work type:** Production
- **Artifact destination:** production (code), agentic-prose (M#2)
- **Model:** sonnet
- **Evidence:** All findings have concrete file:line refs; patterns established in round 1 fixes

## Scope

**In scope:** C#1, M#2, M#3, M#5, m-1 through m-6 = 10 findings
**Split:** M#4 → separate plan (skill-cli-integration)

## Routing

Moderate (non-prose) → `/runbook plans/handoff-cli-tool`
