# Session Handoff: 2026-02-28

**Status:** Design outline complete for UserPromptSubmit topic injection. Hook tier flattening identified as prerequisite.

## Completed This Session

**Design (Phase A + B):**
- `/design plans/userpromptsubmit-topic/requirements.md` — Complex classification, full design process
- `/ground` scoring algorithm: 6 approaches evaluated (BM25, TF-IDF, Jaccard, Dice, overlap, query coverage). Selected: entry coverage via existing `score_relevance()`. Grounding quality: Strong. Reports in `plans/reports/scoring-{internal-codebase,external-research,algorithm-grounding}.md`
- Codebase exploration: 3 scout agents mapped index_parser, resolver, hook architecture, scoring patterns. Report: `plans/userpromptsubmit-topic/reports/explore-dependencies.md`
- Outline produced with 10 decisions (D-1 through D-10), corrector-reviewed
- Discussion deltas applied: D-3 additive all tiers, D-4 project-local tmp, D-8 dropped (YAGNI), D-10 calibration via session-scraper, hook flattening as prerequisite
- FR-4 acceptance criteria updated: `$TMPDIR` → project-local `tmp/`
- Outline corrector review: `plans/userpromptsubmit-topic/reports/outline-review.md`

**Key design decisions from discussion:**
- Scoring: direct `score_relevance()` call, not formula extraction
- Tier architecture: current mutual-exclusion tiers are wrong — features should be parallel detectors with unified output. Commands should match any line, not just first. This is a prerequisite refactor.
- Cache: project-local `tmp/`, not `$TMPDIR`. Continuation registry migration separate task.
- Calibration: retrospective transcript analysis via existing `plans/prototypes/session-scraper.py`, not runtime logging. systemMessage format is a scraping contract.
- Code block filtering: dropped (YAGNI)

## Pending Tasks

- [ ] **Flatten hook tiers** — `/design` | sonnet
  - Plan: (new) | Status: requirements needed
  - Refactor early-return tiers into parallel feature detectors. Commands match any line. Unified output assembly.
- [ ] **UPS topic injection** — `/runbook plans/userpromptsubmit-topic/outline.md` | sonnet
  - Plan: userpromptsubmit-topic | Status: outlined
  - Blocked by: Flatten hook tiers
- [ ] **Calibrate topic params** — extend session-scraper.py | sonnet
  - Plan: (new) | Status: requirements needed
  - Blocked by: UPS topic injection (needs production data first)
- [ ] **Registry cache to tmp** — inline | sonnet
  - Move continuation registry cache from TMPDIR to project-local tmp/
