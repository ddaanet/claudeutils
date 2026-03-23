# Classification: Fix handoff-cli RC6 findings

**Date:** 2026-03-23
**Input:** plans/handoff-cli-tool/reports/deliverable-review.md (RC6: 0C/1M/5m)
**Plan status:** rework
**Round:** 6

## Composite Decomposition

| # | Finding | Behavioral? | Classification | Action |
|---|---------|-------------|----------------|--------|
| M-1 | No test for `_split_sections` `in_message` flag | Yes (new test) | Moderate | Add regression test: `## ` after `## Message` stays in body |
| m-1 | `test_commit_cli_success` vacuous commit check | No (assertion) | Simple | Add `git log` confirmation |
| m-2 | Imprecise submodule assertion | No (string literal) | Simple | `"## Submodule"` → `"## Submodule: agent-core"` |
| m-3 | Multi-submodule commit order not tested | Yes (new test) | Moderate | Add ordering test (low priority — rare scenario) |
| m-4 | Redundant checkbox check in `render_pending` | No (dead code) | Simple | Remove `task.checkbox == " "` from line 45 |
| m-5 | `ParsedTask` imported from different modules | No (import path) | Simple | Align to canonical import path |

## Overall

- **Classification:** Conformance/coverage batch — all mechanisms specified by review
- **Implementation certainty:** High — exact code locations and expected behavior provided
- **Requirement stability:** High — design specs and review findings
- **Behavioral code check:** M-1/m-3 add test functions; remaining are non-behavioral
- **Work type:** Production
- **Artifact destination:** production
- **Model:** sonnet
- **Evidence:** Review provides file:line references, expected behavior, and fix mechanisms for all items

## Routing

All items execution-ready with known approaches. Route: `/inline plans/handoff-cli-tool execute`
