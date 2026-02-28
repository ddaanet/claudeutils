# Scoring Algorithm Grounding: UserPromptSubmit Topic Injection

## Research Foundation

Six approaches evaluated via parallel diverge-converge:
- **Internal:** `recall/relevance.py` already implements normalized keyword overlap; `when/fuzzy.py` provides fzf V2 DP matching
- **External:** 16 sources across IR textbooks, vendor docs, academic papers (full list in `scoring-external-research.md`)

## Approach Selection

**Selected: Normalized entry coverage** — `|Q ∩ D| / |D|` (reuse `score_relevance()`)

**Rejected approaches with rationale:**
- **BM25/TF-IDF:** TF=1 for all terms (keyword lists), IDF unreliable at N=200. Algorithmic machinery inoperative for this corpus structure.
- **Jaccard/Dice:** Symmetric normalization penalizes entries with larger keyword vocabularies, reducing recall. Wrong orientation for "cheap first layer."
- **Raw overlap count:** No normalization — longer prompts always score higher. Cross-entry comparison unreliable.
- **Query coverage ratio** (`|Q∩D|/|Q|`): Favors broad entries that happen to cover many query terms. Entry coverage better answers "is this prompt about this topic?"

**Why entry coverage fits:**
- Entry-centric: "what fraction of this topic's keywords appear in the prompt?" — high score = prompt is about this topic
- Statistic-free: no corpus-wide IDF or document frequency
- Incremental: adding entries requires no index rebuild
- Existing: `score_relevance()` tested and deployed in recall module
- Threshold 0.3 empirically calibrated in production use

## Adaptations

1. **Reuse `score_relevance()` directly** — same formula, same threshold as starting point
2. **Inverted index for performance** — instead of iterating all 347 entries, build keyword→entries map for O(|Q|) candidate lookup, then score only candidates
3. **No term weighting** — validated: IDF adds noise at N=200, TF=1 everywhere

## Grounding Quality

**Strong.** External research validates approach class. Internal codebase implements exact formula. Selection is reuse-grounded, not invented.

## Sources

- Internal: `plans/reports/scoring-internal-codebase.md`, `plans/userpromptsubmit-topic/reports/explore-dependencies.md`
- External: `plans/reports/scoring-external-research.md` (16 sources)
