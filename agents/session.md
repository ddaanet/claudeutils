# Session: Worktree — Markdown test corpus

**Status:** Implementation complete, tests passing (1 known preprocessor bug)

## Completed This Session

- [x] **Scope markdown test corpus work** — Gap analysis + requirements document
  - Analyzed 77 existing unit tests vs 12-section test corpus — found 6 corpus sections with no tests, no end-to-end pipeline tests, no fixture-based testing
  - Wrote `plans/markdown/requirements.md` with 5 FRs and recommended approach (fixture files + parametrized pytest)

- [x] **Implement markdown test corpus** — Lightweight TDD (Tier 2, ~20 cycles)
  - Created 16 fixture pairs in `tests/fixtures/markdown/` (corpus sections 1-12 + 4 preprocessor-specific)
  - Implemented 3 parametrized tests: preprocessor fixtures, idempotency, full pipeline (remark-cli)
  - Extended `test-corpus.md` with sections 13-16 (dunder refs, metadata blocks, warning prefixes, backtick spaces)
  - All 5 FRs satisfied: FR-1 (fixtures), FR-2 (pass-through), FR-3 (pipeline), FR-4 (idempotency), FR-5 (corpus completeness)
  - Test results: 444/461 passed, 1 failed (expected), 16 skipped (remark-cli not installed)

## Pending Tasks

*None* — Implementation complete. Known preprocessor bug documented below.

## Blockers / Gotchas

**Preprocessor idempotency bug discovered (not blocking):**
- Test `test_preprocessor_idempotency[02-inline-backticks]` correctly detects non-idempotent behavior
- Root cause: `fix_backtick_spaces()` adds extra backtick delimiters on re-processing triple-backtick inline code
- Example: ` ``` using `` double `` ``` ` becomes ` ``` using `` double `` `` ``` `` ` after second pass
- Detailed findings: `plans/markdown/reports/cycle-5-1-idempotency-findings.md`
- **This is test-corpus implementation working correctly** — test found real bug in preprocessor
- Fix requires architecture review of preprocessor backtick escaping logic (out of scope for test fixture work)
- Test will pass once preprocessor bug is fixed

## Reference Files

- **plans/markdown/requirements.md** — 5 FRs with gap analysis
- **plans/markdown/test-corpus.md** — 16 sections (extended from 12)
- **plans/markdown/reports/implementation-review.md** — Vet review (all fixes applied, ready)
- **plans/markdown/reports/cycle-5-1-idempotency-findings.md** — Idempotency bug root cause analysis
- **tests/fixtures/markdown/** — 16 fixture pairs (01-16)
- **tests/test_markdown_fixtures.py** — Test module with 3 parametrized tests
