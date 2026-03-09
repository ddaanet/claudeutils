# Session: Worktree — Calibrate validation thresholds

**Status:** Focused worktree for parallel execution.

## In-tree Tasks

- [ ] **Calibrate validation thresholds** — `/design plans/ar-threshold-calibration/problem.md` | sonnet
  - Measure distributions for all 5 thresholds against 366-entry dataset, set at natural breakpoints, implement user-configurable defaults with feedback pipeline
  - Thresholds: keyword overlap %, specificity range, keyword count, content words, discriminating count
  - Human judgment needed for "is this a true duplicate" / "is this over-specific" labeling
