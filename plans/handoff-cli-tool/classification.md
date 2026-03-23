# Classification: Fix handoff-cli RC5 findings

**Date:** 2026-03-23
**Input:** plans/handoff-cli-tool/reports/deliverable-review.md (RC5: 0C/2M/10m)
**Plan status:** rework
**Round:** 5

## Composite Decomposition

| # | Finding | Behavioral? | Classification | Action |
|---|---------|-------------|----------------|--------|
| M-1 | `_strip_hints` state reset | Yes (logic path) | Defect | `prev_was_hint = False` → `True` at continuation branch |
| M-2 | `vet_check` missing `cwd` | Yes (new param) | Defect | Thread `cwd` through `_load_review_patterns`, `_find_reports`, `vet_check` |
| m-1 | `## Message` EOF semantics | Yes (add conditional) | Conformance | Add `is_message_section` flag to `_split_sections` |
| m-2 | `step_reached` unused | No | Accept | Vestigial but schema-conformant — no action |
| m-3 | Pipeline stage ordering | No | Accept | Valid deviation — no action |
| m-4 | Diagnostic output guarded | Yes (remove guard) | Conformance | Remove `if git_output:` — emit diagnostics unconditionally |
| m-5 | stderr discarded | Yes (capture change) | Robustness | Capture stderr in `_run_precommit`/`_run_lint` |
| m-6 | `_git()` strips stdout | No (docstring) | Documentation | Add porcelain warning to docstring |
| m-7 | Ternary precedence | No (formatting) | Readability | Parenthesize `(... if amend else ...)` |
| m-8 | Local init helpers persist | No (test refactor) | Test quality | Replace with `init_repo_minimal` in 2 pre-existing files |
| m-9 | No multi-continuation test | No (test addition) | Test coverage | Add multi-continuation + single-space edge case tests |
| m-10 | Missing dash-prefix assertion | No (test addition) | Test quality | Add `- ` prefix assertion |

## Overall

- **Classification:** Defect/conformance batch — all mechanisms specified by review
- **Implementation certainty:** High — exact code locations and fixes provided
- **Requirement stability:** High — design specs and observable behaviour
- **Behavioral code check:** M-1/M-2/m-1/m-4/m-5 are behavioral; remainder non-behavioral
- **Work type:** Production
- **Artifact destination:** production
- **Model:** sonnet
- **Evidence:** Review report provides root cause, fix mechanism, and code locations for all items

## Routing

Defect batch with complete investigation (review report = specification). Route: `/inline plans/handoff-cli-tool execute`
