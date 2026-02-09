# fzf Algorithm Research — `/when` Fuzzy Matching Engine

## Algorithm Overview

fzf implements a modified Smith-Waterman algorithm for **character-level subsequence matching**. Two variants:

- **V2 (default):** O(nm) dynamic programming, optimal scoring. Builds score matrix examining all possible alignments.
- **V1 (fallback):** Greedy shortest-match, faster, suboptimal. Used for very long inputs.

Core idea: find where pattern characters appear (in order) within the candidate string, then score by position quality.

## Scoring System

### Constants (from algo.go)

| Constant | Value | Purpose |
|----------|-------|---------|
| scoreMatch | 16 | Base score per matched character |
| scoreGapStart | -3 | Penalty for starting a gap |
| scoreGapExtension | -1 | Penalty per additional gap character |
| bonusBoundary | 8 | Match at word boundary |
| bonusNonWord | 8 | Match after non-word character |
| bonusCamel123 | 7 | CamelCase transition |
| bonusConsecutive | 4 | Each consecutive matched character |
| bonusFirstCharMultiplier | 2 | First character match bonus multiplied |
| bonusBoundaryWhite | 10 | Match after whitespace |
| bonusBoundaryDelimiter | 9 | Match after delimiter (/, -, _) |

### Scoring Schemes

Three schemes adjust boundary bonuses for different content types:

- **default** — generic scoring
- **path** — elevated bonus for path separators (/)
- **history** — no bonuses (preserves chronological order)

### How Scoring Works

For query `pp` against `Peter Piper picked pepper`:
1. Each `p` in query must appear in order in candidate
2. Matching at word boundary (P in Peter, P in Piper) scores higher than mid-word
3. Consecutive matches score higher than separated ones
4. Gap penalties accumulate for characters between matches

## Python Implementations

### pfzy (recommended for `/when`)

- **What:** Pure Python port of fzy algorithm (fzy ≈ fzf scoring, different optimization)
- **API:** `fuzzy_match("query", ["candidate1", "candidate2"])` → sorted results with scores + indices
- **License:** MIT
- **Dependencies:** None (pure Python)
- **Install:** `pip install pfzy`
- **Caveat:** Async API by default (`asyncio.run()` wrapper needed for sync use)

### RapidFuzz

- **What:** C++ backed fuzzy matching (Levenshtein distance family, NOT fzf algorithm)
- **Strengths:** Fast, production-grade, extensive metrics
- **Weakness:** Different algorithm family — edit distance, not subsequence matching

### thefuzz (FuzzyWuzzy)

- **What:** Levenshtein-based, pure Python
- **Weakness:** Slow, different algorithm family, legacy

## Evaluation for `/when`

### The Matching Problem

`/when` needs to match an agent's trigger query against ~169 `@uniquefuzzy` keys. Example:

```
Agent types:  /when writing mock tests
Keys to match: "mock-patch", "test-split", "path-encode", "mock-patch-location"
Expected:     "mock-patch" (highest score)
```

Key characteristics:
- **Corpus:** ~169 short keys (1-3 words, hyphenated or slug-form)
- **Queries:** Agent-typed trigger phrases (2-5 words, natural language)
- **Scale:** Tiny — performance irrelevant, correctness matters
- **Error tolerance:** Typos unlikely (agent-generated), but partial recall common (agent remembers "mock" but not exact key)

### fzf Algorithm: Strengths for `/when`

1. **Subsequence matching handles partial recall** — query "mock test" matches key "mock-patch-test" even without exact substring
2. **Boundary bonuses reward word-start matches** — "mock" matching at word boundary in "mock-patch" scores higher than mid-word
3. **Delimiter awareness** — hyphens in keys (`mock-patch`) treated as boundaries, each word-start gets bonus
4. **Battle-tested scoring** — millions of users have validated the ranking intuition
5. **Handles prefix matching naturally** — first-char multiplier means partial prefix typing ranks well

### fzf Algorithm: Weaknesses for `/when`

1. **Character-level, not token-level** — fzf matches individual characters, but `/when` keys are word-oriented. Query "path" matches "mock-**p**-**a**-**t**-**h**" and "**path**-encode" — boundary bonuses help but character-level can produce surprising matches
2. **Designed for interactive filtering, not batch lookup** — fzf assumes user refines query seeing results; `/when` is fire-and-forget (agent gets one shot)
3. **Short keys reduce discrimination** — with 5-15 character keys, score differences between candidates are small. fzf shines with longer strings (file paths, command history)
4. **No semantic understanding** — "writing tests" won't match "test-split" better than "test-hooks" even though the former is more relevant. But this is true of all lexical algorithms.

### Alternative: Simple Word-Overlap Scoring

For `/when`'s specific use case, a simpler approach may suffice:

```python
def score(query_words, key_words):
    """Score based on word overlap + position."""
    overlap = query_words & key_words
    prefix_bonus = 2 if key_words[0] in query_words else 0
    return len(overlap) + prefix_bonus
```

Pros: Interpretable, predictable, word-level semantics. Cons: No typo tolerance, rigid word boundaries.

### Recommendation

**Use fzf-style scoring (via pfzy or custom implementation) as the primary engine, with word-overlap as tiebreaker.**

Rationale:
- fzf handles the common case well (partial recall, word boundaries)
- Word-overlap scoring as secondary signal adds semantic discrimination
- pfzy provides a working Python implementation, zero dependencies
- Custom implementation is ~80 lines if we want to tune scoring constants for our use case

### Tuning Opportunities

If using fzf algorithm, tune for `/when`'s short-key domain:
- **Increase bonusBoundaryDelimiter** — hyphens in keys are primary word separators
- **Increase bonusConsecutive** — consecutive word matches should dominate
- **Reduce scoreGapExtension penalty** — gaps between words are expected in natural queries
- **Consider word-level preprocessing** — normalize query "writing mock tests" → "mock test" (strip verbs/articles) before character-level matching

## Implementation Sketch

```python
# Option A: Use pfzy directly
from pfzy import fuzzy_match
import asyncio

def resolve_when(query: str, keys: list[str]) -> list[str]:
    """Match query against uniquefuzzy keys, return ranked results."""
    results = asyncio.run(fuzzy_match(query, keys))
    return [r["value"] for r in results[:5]]  # top 5

# Option B: Custom fzf-lite (~80 lines)
# Port scoring constants, implement single-pass scorer
# Advantage: tune constants for short-key domain
# See algo.go for reference implementation
```

## Sources

- [fzf algo.go — scoring constants and V2 algorithm](https://github.com/junegunn/fzf/blob/master/src/algo/algo.go)
- [fzf DeepWiki — algorithm overview](https://deepwiki.com/junegunn/fzf/2.2-fuzzy-matching-algorithm)
- [fzy ALGORITHM.md — Smith-Waterman adaptation](https://github.com/jhawthorn/fzy/blob/master/ALGORITHM.md)
- [pfzy — Python port of fzy](https://github.com/kazhala/pfzy)
- [RapidFuzz — C++ backed fuzzy matching](https://github.com/rapidfuzz/RapidFuzz)
- [frizbee — SIMD Smith-Waterman matcher](https://github.com/saghen/frizbee)
