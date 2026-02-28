# Scoring Algorithm External Research

**Task:** UserPromptSubmit topic injection
**Purpose:** Evaluate keyword-based scoring approaches for matching user prompts (~10-200 tokens) against 200+ memory-index entries (each 5-20 keywords). Sub-second latency. Python. "Cheap first layer" complementing deep recall.

---

## Context and Constraints

- **Query size:** 10-200 tokens (short to medium)
- **Corpus:** 200+ entries, each 5-20 keywords (very short "documents")
- **Latency:** Sub-second for full corpus scan
- **Infrastructure:** Tokenization + stopword removal already provided
- **Role:** First-pass filter — high recall preferred over precision; cost is cheap relative to deep recall

---

## Approach 1: Simple Keyword Overlap Count (Intersection Size)

### How It Works

Represent the query and each entry as sets of terms. Score = number of terms in common.

`score(Q, D) = |Q ∩ D|`

### Scoring Formula

`score = len(query_terms & entry_terms)`

### Computational Complexity

- Per-entry: O(min(|Q|, |D|)) for set intersection
- Full corpus: O(N × |Q|) where N = number of entries
- No precomputation required beyond tokenization

### Strengths for This Use Case

- Zero setup — no corpus statistics, no index build
- Trivially implemented with Python `set` operations (stdlib only)
- Directly rewards any keyword match; will not penalize for missing terms
- Fully incremental — add new entries without any recomputation
- Predictable scoring: one matched term = one point, unambiguous

### Weaknesses for This Use Case

- No term weighting — common terms (e.g., "error", "file") score identically to rare, discriminative terms
- Longer queries always produce higher absolute scores for any given entry, making cross-query comparisons unreliable
- Does not normalize for entry length — an entry with 20 keywords has more chances to match than one with 5
- No notion of "all matched" vs "one matched" relative to either side's size

### Implementation Complexity

- ~5-10 LOC
- Dependencies: none (Python stdlib `set`)
- No index structure needed

### Corpus-Wide Statistics Required

None.

### Named References/Sources

- [BM25 relevance scoring - Azure AI Search](https://learn.microsoft.com/en-us/azure/search/index-similarity-and-scoring) — notes overlap count as BM25's conceptual ancestor
- [Introduction to Information Retrieval (Manning et al., Stanford)](https://nlp.stanford.edu/IR-book/pdf/07system.pdf) — establishes intersection as the baseline binary IR model

---

## Approach 2: TF-IDF with Cosine Similarity

### How It Works

Represent each entry and the query as weighted term vectors. Term weight = TF × IDF, where TF is term frequency in the document and IDF penalizes terms that appear across many documents. Score = cosine similarity between query vector and entry vector.

### Scoring Formula

```
TF(t, D)  = count of term t in document D
IDF(t)    = log(N / df(t))      where df(t) = number of docs containing t
weight    = TF(t, D) × IDF(t)
score(Q, D) = cos_sim(vector(Q), vector(D)) = (Q·D) / (|Q| × |D|)
```

### Computational Complexity

- Index build: O(N × |D|) — one pass over corpus
- Per-query: O(|Q| + N) with sparse vectors
- Memory: O(V × N) where V = vocabulary size (sparse in practice)

### Strengths for This Use Case

- IDF naturally down-weights common terms, reducing noise from stopword false positives
- Cosine normalization handles length variation — comparable scores across entries of different sizes
- Established, well-understood baseline with known behavior
- Can be implemented with stdlib (math, collections) using dict-based sparse vectors

### Weaknesses for This Use Case

- **Corpus-size sensitivity:** IDF is unreliable at N=200. A term appearing in 100/200 entries gets low IDF even if it's meaningfully discriminative in context. IDF requires a stable, large corpus to be meaningful.
- **Static index:** Adding new entries or modifying existing ones invalidates IDF values — full rebuild required to maintain correctness
- **Entry length irrelevance:** With 5-20 keywords per entry, there is negligible within-entry TF variation — every term appears once, so TF=1 everywhere. TF dimension adds no information for this structure.
- **Cosine edge case:** Empty or near-empty vectors produce undefined or zero similarity regardless of partial match
- Typical implementation via scikit-learn; pure-stdlib implementation is ~50-80 LOC

### Implementation Complexity

- ~50-80 LOC with stdlib (sparse dict vectors, manual IDF computation)
- Or 5-10 LOC with `scikit-learn` (`TfidfVectorizer` + `cosine_similarity`)
- Dependencies: none for stdlib; scikit-learn + numpy for library path

### Corpus-Wide Statistics Required

Yes — IDF requires document frequency counts across all entries before any query can be scored. Must be recomputed when entries change.

### Named References/Sources

- [Comparing BM25 vs TF-IDF: Which is Better? — MyScale](https://www.myscale.com/blog/bm25-vs-tf-idf-deep-dive-comparison/)
- [Understanding TF-IDF and BM-25 — KMW Technology](https://kmwllc.com/index.php/2020/03/20/understanding-tf-idf-and-bm-25/)
- [TF-IDF and BM25 for RAG — a complete guide](https://www.ai-bites.net/tf-idf-and-bm25-for-rag-a-complete-guide/)
- [Scoring, term weighting and the vector space model (Stanford IR Book)](https://nlp.stanford.edu/IR-book/pdf/06vect.pdf)

---

## Approach 3: BM25 (Okapi BM25)

### How It Works

Probabilistic ranking function extending TF-IDF with term frequency saturation (k₁ parameter) and document length normalization (b parameter). Prevents long documents from dominating via IDF and caps the marginal gain of repeated terms.

### Scoring Formula

```
BM25(D, Q) = Σ IDF(q_i) × [f(q_i, D) × (k₁ + 1)] / [f(q_i, D) + k₁ × (1 - b + b × |D| / d_avg)]

IDF(q_i) = log((N - df(q_i) + 0.5) / (df(q_i) + 0.5) + 1)   [Lucene variant, avoids negatives]

Default parameters: k₁ = 1.2 or 1.5, b = 0.75
```

Where f(q_i, D) = term frequency of query term i in document D, |D| = document length, d_avg = average document length across corpus.

### Computational Complexity

- Index build: O(N × |D|) — compute df, d_avg, and inverted index
- Per-query: O(|Q| + matched docs) with inverted index; O(N × |Q|) brute force
- Inverted index lookup is standard practice for large corpora; brute force is fine at N=200

### Strengths for This Use Case

- Industry-standard baseline — well understood, widely validated
- Term frequency saturation prevents over-reward of repeated terms
- Length normalization theoretically handles variable entry sizes
- Lucene IDF variant (with +1) avoids negative scores for common terms
- `rank-bm25` Python package: single dependency (numpy only), ~200 LOC

### Weaknesses for This Use Case

- **Critical misfit — TF irrelevance:** With 5-20 keywords per entry (all appearing once), TF=1 for every term. The TF saturation mechanism is entirely inoperative — BM25 reduces to IDF-weighted overlap at this entry structure.
- **Critical misfit — length normalization noise:** Entries are 5-20 keywords. d_avg ≈ 12. b=0.75 introduces length normalization, but the variance is too small (5-20 tokens) to produce meaningful discrimination. The normalization adds computation without benefit.
- **IDF instability at N=200:** The same small-corpus IDF reliability problem as TF-IDF. With 200 entries, a term appearing in 100 entries gets penalized heavily even if it is a legitimate discriminative keyword.
- **Negative IDF edge case:** Standard BM25 IDF is negative when df > N/2. Lucene adds +1 to prevent this; implementations vary. `rank-bm25` handles this correctly but behavior must be verified.
- **BM25+ variant** (lower-bounding term contribution) was designed to address short document recall, but the underlying TF=1 structure remains a fundamental limitation here.
- Requires corpus statistics; static index degrades with entry additions

### Implementation Complexity

- ~5-10 LOC with `rank-bm25` (requires numpy)
- ~100-150 LOC pure stdlib
- Dependencies: `rank-bm25` (numpy only) for library path; heavier for `bm25s` (numpy + scipy/numba)

### Corpus-Wide Statistics Required

Yes — document frequencies, average document length, inverted index. Must be rebuilt when entries change.

### Named References/Sources

- [Okapi BM25 — Wikipedia](https://en.wikipedia.org/wiki/Okapi_BM25)
- [Practical BM25 Part 2: The BM25 Algorithm and Its Variables — Elastic](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables)
- [BM25 vs TF-IDF: Which Ranks Text Better? — MLWorks/Medium](https://medium.com/mlworks/why-bm25-algorithm-over-tf-idf-67bc009d20de)
- [rank-bm25 — PyPI](https://pypi.org/project/rank-bm25/)
- [Which BM25 Do You Mean? A Large-Scale Reproducibility Study — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7148026/)

---

## Approach 4: Jaccard Similarity

### How It Works

Set-based similarity: ratio of intersection to union. Normalizes overlap against both query size and entry size simultaneously.

### Scoring Formula

`J(Q, D) = |Q ∩ D| / |Q ∪ D|`

Equivalent to: `intersection_size / (|Q| + |D| - intersection_size)`

Score range: [0, 1]. Score = 1 means identical sets.

### Computational Complexity

- Per-entry: O(min(|Q|, |D|)) for set intersection; O(|Q| + |D|) for union
- Full corpus: O(N × (|Q| + |D|))
- No precomputation required

### Strengths for This Use Case

- Normalized: scores are comparable across entries of different lengths and queries of different lengths
- No corpus statistics required — fully incremental
- Set operations are fast and readable in Python (stdlib)
- Score interpretation is intuitive: what fraction of all relevant terms matched?
- Penalizes both missed query terms and irrelevant entry keywords symmetrically

### Weaknesses for This Use Case

- **Union penalty:** Jaccard penalizes large-vocabulary entries even when they match all query terms. An entry with 20 keywords matching 5 of 10 query terms scores lower than an entry with 5 keywords matching the same 5 terms. For a "cheap first layer" that prioritizes recall, this is a meaningful penalty.
- **Query-size sensitivity:** Short queries with even one match produce high Jaccard scores relative to long queries with many matches. The metric does not distinguish "matched everything" from "matched one of many."
- No term weighting — common and rare terms score equally
- Research (Semantic Scholar paper: "Using of Jaccard Coefficient for Keywords Similarity") shows Jaccard works well for near-duplicate detection but is not optimized for asymmetric query-vs-keyword-set retrieval

### Implementation Complexity

- ~5-10 LOC
- Dependencies: none (Python stdlib `set`)

### Corpus-Wide Statistics Required

None.

### Named References/Sources

- [Jaccard index — Wikipedia](https://en.wikipedia.org/wiki/Jaccard_index)
- [Jaccard Similarity — IBM Think](https://www.ibm.com/think/topics/jaccard-similarity)
- [Using of Jaccard Coefficient for Keywords Similarity — Semantic Scholar](https://www.semanticscholar.org/paper/Using-of-Jaccard-Coefficient-for-Keywords-Niwattanakul-Singthongchai/db467107ad133e44085780da5296b840e2a32e9e)
- [Jaccard Similarity — Study Machine Learning](https://studymachinelearning.com/jaccard-similarity-text-similarity-metric-in-nlp/)

---

## Approach 5: Query Coverage Ratio

### How It Works

Measures what fraction of the query's terms appear in the entry. Unlike Jaccard, the denominator is the query size only — not the union. This is an asymmetric measure focused on "how much of what was asked is covered?"

### Scoring Formula

`coverage(Q, D) = |Q ∩ D| / |Q|`

Score range: [0, 1]. Score = 1.0 means all query terms appear in the entry.

### Computational Complexity

- Per-entry: O(min(|Q|, |D|))
- Full corpus: O(N × |Q|)
- No precomputation required

### Strengths for This Use Case

- Optimized for recall — any entry that covers all query terms scores 1.0 regardless of how many extra keywords the entry has
- Does not penalize entries for having additional keywords beyond the query
- Natural fit for a "cheap first layer": surface everything that plausibly matches the query, then let deep recall discriminate
- Incremental — no corpus statistics
- Trivial to implement
- Aligns with the asymmetric structure: the query is the signal source; the entry is the target

### Weaknesses for This Use Case

- Does not penalize false positives from the entry's side — an entry with 100 keywords matching 1 query term scores the same as a targeted 5-keyword entry matching the same term
- Score does not normalize for query length when comparing across multiple queries (but within a single query pass, this is irrelevant)
- No term weighting — a common matched term scores identically to a rare matched term

### Implementation Complexity

- ~5-10 LOC
- Dependencies: none (Python stdlib `set`)

### Corpus-Wide Statistics Required

None.

### Named References/Sources

- [Scoring, term weighting and the vector space model (Stanford IR Book)](https://nlp.stanford.edu/IR-book/pdf/06vect.pdf) — coverage-type measures discussed in IR context
- [Using the Weighted Keyword Model to Improve Information Retrieval for Answering Biomedical Questions — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3041568/) — term coverage as IR feature
- [Improving Scientific Document Retrieval with Concept Coverage-based Query Set Generation — arXiv](https://arxiv.org/abs/2502.11181) — concept coverage as retrieval quality signal

---

## Approach 6: Dice Coefficient (Sørensen-Dice)

### How It Works

Set overlap metric related to Jaccard but gives more weight to intersection. Computed as twice the intersection divided by the sum of both set sizes (not the union as in Jaccard).

### Scoring Formula

`Dice(Q, D) = 2 × |Q ∩ D| / (|Q| + |D|)`

Score range: [0, 1].

### Computational Complexity

- Per-entry: O(min(|Q|, |D|))
- Full corpus: O(N × (|Q| + |D|))
- No precomputation required

### Strengths for This Use Case

- More sensitive to overlap in small sets than Jaccard (places greater relative weight on matches)
- Score is bounded and interpretable
- Stdlib only

### Weaknesses for This Use Case

- Monotonically related to Jaccard for fixed set sizes — does not produce different ranking order, only different score scale
- Shares Jaccard's union-denominator problem: penalizes entries with many keywords, reducing recall
- No term weighting
- In practice, Jaccard and Dice produce equivalent rankings for the same corpus; choosing one over the other has no functional impact on retrieval quality

### Implementation Complexity

- ~5-10 LOC
- Dependencies: none

### Corpus-Wide Statistics Required

None.

### Named References/Sources

- [Sørensen-Dice coefficient — Wikipedia](https://en.wikipedia.org/wiki/S%C3%B8rensen%E2%80%93Dice_coefficient)
- [Dice Similarity Score Explained — Restackio](https://www.restack.io/p/similarity-search-answer-dice-similarity-score-cat-ai)
- [Classical retrieval and overlap measures satisfy requirements for rankings based on Lorenz curve — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0306457304000627) — Jaccard, Dice, cosine characterized as equivalent ranking functions

---

## Synthesis Notes

### Why TF and TF Saturation Are Irrelevant Here

Both TF-IDF and BM25 derive significant differentiation from term frequency within a document. In this corpus, each entry is a keyword list where every term appears exactly once (TF=1 for all terms). This makes the TF dimension inoperative:

- TF-IDF reduces to IDF-weighted binary vectors
- BM25's k₁ saturation term reduces to a constant multiplier since f(q,D) ∈ {0,1}

Both algorithms still benefit from IDF weighting, but their defining advantages over simpler approaches vanish.

### Why IDF Is Unreliable at N=200

IDF = log(N / df). With N=200 entries and a term appearing in 100 entries, IDF = log(2) ≈ 0.69. With a term in 50 entries, IDF = log(4) ≈ 1.39. The IDF dynamic range across a 200-entry corpus is narrow, and statistical reliability is low — adding or removing 10 entries can meaningfully shift scores. IDF is calibrated for thousands-to-millions-document corpora.

### Asymmetry of the Problem

The retrieval task is query-centric: "find entries relevant to this query." The query is the signal; the entry is the target. This asymmetry favors query-coverage-denominated metrics (query coverage ratio) over symmetric metrics (Jaccard, Dice) that penalize entry vocabulary size. An entry with 20 keywords is not a weaker match candidate than one with 5 keywords merely because it has more knowledge.

### Corpus Statistics as Maintenance Burden

For a memory index that is incrementally updated (new entries added, old entries modified), maintaining corpus statistics (IDF, d_avg) requires either full index rebuilds or complex incremental update logic. Statistics-free approaches (intersection count, Jaccard, query coverage) have zero maintenance cost for index updates.

---

## Summary Comparison Table

| Approach | Relevance Quality | Stdlib Only | Sub-second @ 200 entries | No Corpus Stats | LOC Estimate | Fits Short "Documents" |
|----------|------------------|-------------|--------------------------|-----------------|--------------|------------------------|
| Keyword Overlap Count | Low — no term weighting | Yes | Yes | Yes | ~5-10 | Yes |
| TF-IDF + Cosine | Moderate — IDF unreliable at N=200; TF inoperative | Possible (~50-80 LOC) | Yes | No (full rebuild on change) | 50-80 stdlib / 5-10 sklearn | Poor — TF=1 everywhere |
| BM25 (Okapi) | Moderate — same IDF/TF issues; length norm irrelevant at 5-20 tokens | No (needs numpy or full reimpl) | Yes | No (full rebuild on change) | ~100-150 stdlib / 5 with rank-bm25 | Poor — TF=1, length norm noise |
| Jaccard Similarity | Moderate — symmetric, penalizes large-vocab entries | Yes | Yes | Yes | ~5-10 | Moderate — penalizes recall |
| Query Coverage Ratio | Good for recall layer — query-centric, no false negatives from large entries | Yes | Yes | Yes | ~5-10 | Yes |
| Dice Coefficient | Same ranking as Jaccard — no practical difference | Yes | Yes | Yes | ~5-10 | Moderate — penalizes recall |

### Evaluation Criteria Ratings (1=poor, 3=good)

| Approach | Relevance Quality | Simplicity | Performance | Maintenance |
|----------|------------------|------------|-------------|-------------|
| Overlap Count | 1 | 3 | 3 | 3 |
| TF-IDF + Cosine | 2 | 2 | 3 | 1 |
| BM25 | 2 | 2 | 3 | 1 |
| Jaccard | 2 | 3 | 3 | 3 |
| Query Coverage Ratio | 3 | 3 | 3 | 3 |
| Dice Coefficient | 2 | 3 | 3 | 3 |

### Key Finding

For this specific use case — short queries against keyword-list entries in a 200-entry corpus as a high-recall cheap first layer — **query coverage ratio** scores best on the evaluation criteria. It is:

- Query-centric (aligns with retrieval goal)
- Zero maintenance (no corpus statistics)
- Trivial to implement (stdlib, ~5 LOC)
- High recall (does not penalize entries for extra vocabulary)
- Sub-second at any realistic corpus size

BM25 and TF-IDF carry algorithmic machinery (TF saturation, length normalization, IDF weighting) that adds implementation and maintenance cost without providing benefit when entry documents are uniform 5-20 keyword lists in a 200-entry corpus. Their advantages emerge at scale (thousands of documents, variable-length prose documents) and become liabilities at small scale.

**Overlap count** is appropriate as the simplest possible baseline or for cases where the threshold for triggering is binary (any match = candidate). **Jaccard/Dice** add normalization for cross-query comparison but reduce recall by penalizing large-keyword entries.

---

## Sources

- [Okapi BM25 — Wikipedia](https://en.wikipedia.org/wiki/Okapi_BM25)
- [Practical BM25 Part 2: The BM25 Algorithm and Its Variables — Elastic](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables)
- [Comparing BM25 vs TF-IDF: Which is Better? — MyScale](https://www.myscale.com/blog/bm25-vs-tf-idf-deep-dive-comparison/)
- [BM25 vs TF-IDF: Which Ranks Text Better? — MLWorks/Medium](https://medium.com/mlworks/why-bm25-algorithm-over-tf-idf-67bc009d20de)
- [Understanding TF-IDF and BM-25 — KMW Technology](https://kmwllc.com/index.php/2020/03/20/understanding-tf-idf-and-bm-25/)
- [TF-IDF and BM25 for RAG — a complete guide](https://www.ai-bites.net/tf-idf-and-bm25-for-rag-a-complete-guide/)
- [Comparing full text search algorithms: BM25, TF-IDF, and Postgres — Evan Schwartz](https://emschwartz.me/comparing-full-text-search-algorithms-bm25-tf-idf-and-postgres/)
- [Comparing BM25, TF-IDF, and Hybrid Search for MCP Tool Discovery — StackOne](https://www.stackone.com/blog/mcp-tool-search-bm25-tfidf-hybrid/)
- [Jaccard index — Wikipedia](https://en.wikipedia.org/wiki/Jaccard_index)
- [Jaccard Similarity — IBM Think](https://www.ibm.com/think/topics/jaccard-similarity)
- [Using of Jaccard Coefficient for Keywords Similarity — Semantic Scholar](https://www.semanticscholar.org/paper/Using-of-Jaccard-Coefficient-for-Keywords-Niwattanakul-Singthongchai/db467107ad133e44085780da5296b840e2a32e9e)
- [Sørensen-Dice coefficient — Wikipedia](https://en.wikipedia.org/wiki/S%C3%B8rensen%E2%80%93Dice_coefficient)
- [Scoring, term weighting and the vector space model (Stanford IR Book)](https://nlp.stanford.edu/IR-book/pdf/06vect.pdf)
- [Introduction to Information Retrieval, Chapter 7 (Stanford/Cambridge)](https://nlp.stanford.edu/IR-book/pdf/07system.pdf)
- [Using the Weighted Keyword Model to Improve Information Retrieval for Answering Biomedical Questions — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3041568/)
- [Improving Scientific Document Retrieval with Concept Coverage-based Query Set Generation — arXiv](https://arxiv.org/abs/2502.11181)
- [rank-bm25 — PyPI](https://pypi.org/project/rank-bm25/)
- [Which BM25 Do You Mean? A Large-Scale Reproducibility Study — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7148026/)
- [BM25 relevance scoring — Azure AI Search / Microsoft Learn](https://learn.microsoft.com/en-us/azure/search/index-similarity-and-scoring)
- [Classical retrieval and overlap measures — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0306457304000627)
