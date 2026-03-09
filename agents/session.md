# Session Handoff: 2026-03-09

**Status:** Grounding complete for both questions. Discuss protocol updated (stress-test → research claims). Next: run A/B test.

## Completed This Session

**Grounding (verb form):**
- Q1 (fuzzy matcher): Prefix mismatch causes 0.0 scores — well-characterized deficiency of character-level matching. Fix belongs in matcher, not entry format. (file: plans/reports/how-verb-form-grounding.md)
- Q2 (agent recognition): External research can't answer — requires empirical A/B test. Forced selection design (TREC/Cranfield) makes silent failures observable.
- A/B methodology grounded: FormatSpread (ICLR 2024), ProSA (EMNLP 2024), McNemar's test for paired binary outcomes. (file: plans/reports/how-verb-form-ab-methodology.md)

**Discuss protocol revision:**
- Mined 9 "I was wrong" sessions + 29 pushback worktree sessions for protocol effectiveness data
- Found: stress-test has zero observed perspective-change value. All changes triggered by new facts, reframing, or exposed research gaps
- Removed stress-test, replaced with "research your own claims" step in pushback.md and hook expansion
- Framings marked as internal reasoning (think block), not output
- (file: plans/reports/discuss-protocol-mining.md)

**Previous session (carried forward):**
- Scrapped original grounding — answered wrong questions (fuzzy self-matching, index-driven query distribution)

## In-tree Tasks

- [x] **Restart grounding** — `/ground` | sonnet
  - Both questions grounded. Q1: matcher deficiency confirmed. Q2: requires A/B test (methodology grounded).
- [ ] **Verb form AB test** — `/ground` | sonnet
  - Forced selection design: 15-20 task contexts, paired comparison, McNemar's test
  - Infrastructure: index variant generator, task selector, prompt harness, analysis script
  - Methodology: plans/reports/how-verb-form-ab-methodology.md

## Worktree Tasks

- [ ] **Fix prefix tolerance** — `src/claudeutils/when/fuzzy.py` | sonnet
  - Zero tolerance for prefix noise (0.0 scores on one-token mismatch). Separate from format decision.

## Reference Files

- `plans/reports/how-verb-form-grounding.md` — synthesis report (Moderate grounding)
- `plans/reports/how-verb-form-ab-methodology.md` — A/B test methodology (Strong grounding)
- `plans/reports/discuss-protocol-mining.md` — discuss protocol effectiveness analysis
- `plans/reports/how-verb-form-internal-codebase.md` — matcher algorithm, removeprefix band-aid, index format
- `plans/reports/how-verb-form-external-research.md` — fuzzy matching + LLM sensitivity literature
- `plans/reports/how-verb-form-ab-methodology-internal.md` — existing test infrastructure
- `plans/reports/how-verb-form-ab-methodology-external.md` — methodology literature
- `plans/prototypes/` — extraction scripts, reusable for A/B test infrastructure
- `src/claudeutils/when/fuzzy.py` — production fuzzy matcher
- `src/claudeutils/when/resolver.py` — `removeprefix("to ")` band-aid at line 196

## Next Steps

Run A/B test using forced selection design from methodology report.
