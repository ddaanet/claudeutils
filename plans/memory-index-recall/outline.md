# Memory Index Recall — Testing Methodology Outline

## Approach

Empirical evaluation of memory-index effectiveness via transcript analysis of real Claude Code sessions. Extend claudeutils to extract tool usage (Read calls specifically) from assistant messages in JSONL transcripts, then correlate with memory-index entries to measure recall.

**Core question:** When an agent works on a topic covered by a memory-index entry, does it read the referenced file?

**Method:** Retrospective transcript analysis (not controlled experiments).

**Rationale:** Real session data already exists. Controlled experiments are expensive, non-deterministic, and test agent capability rather than index design. Transcript analysis measures actual behavior at scale.

**Baseline comparison:** Compare recall rates in recent sessions (with memory-index) against historical sessions from before the index existed (or sessions where no relevant index entry was present). This measures the marginal impact of the index on file discovery.

## Research Hypothesis

**H0 (Null hypothesis):** Memory-index entries do not increase the rate at which agents read relevant documentation files. Observed differences are due to chance or confounding factors (session complexity, user guidance, model improvements).

**H1 (Alternative hypothesis):** When a memory-index entry is relevant to a session's topic, agents are more likely to read the referenced file compared to sessions without a relevant entry, indicating the index aids discovery.

**Validity threats:**
- **Confounding by user guidance:** User may explicitly tell agent to read a file
- **Temporal effects:** Agent capability may improve over time independent of index
- **Selection bias:** Sessions with index may differ systematically from baseline sessions

**Mitigation:** Track explicit user file references, analyze session date ranges, stratify by session complexity.

## Success Criteria

**Minimum viable results** (proceed to use index insights for iteration):
- **Recall rate ≥50%:** When a memory-index entry is relevant, agent reads the file in at least half of cases
- **Lift vs baseline ≥20%:** Recall rate with index is at least 20 percentage points higher than baseline
- **Discovery method:** >70% of successful reads are direct (not preceded by Grep/Glob search)

**Ideal results** (index is highly effective):
- Recall rate ≥80%
- Lift vs baseline ≥40%
- Discovery method: >90% direct reads

**Failure indicators** (index needs redesign):
- Recall rate <30%
- No significant lift vs baseline
- Most reads preceded by search (index not being consulted)

## Key Decisions

- **Retrospective over prospective:** Analyze existing sessions rather than running new experiments. Cheaper, larger sample, measures real behavior.
- **Tool extraction as foundation:** Extend JSONL parsing to extract assistant tool calls (tool name, arguments). This has value beyond this experiment (general observability).
- **Relevance via keyword matching:** Map session topics to memory-index entries using keyword overlap between user prompts and index entry text. Not perfect, but tractable.
- **Read-file correlation as primary metric:** Success = agent Read a file referenced by a relevant index entry. Failure = agent used Grep/Glob to discover it, or never found it.

## Scope

**In scope:**
- Extract tool usage from assistant JSONL entries (new parsing capability)
- Build relevance mapping: session topics → expected memory-index entries
- Calculate recall metrics: did agent read referenced files when entries were relevant?
- Distinguish direct reads (index-guided) from search-then-read (ad-hoc discovery)
- Report with results from real session corpus

**Out of scope:**
- Controlled A/B experiments (with/without index)
- Real-time instrumentation via hooks
- Modifying the memory-index format
- Causal claims (correlation only — can't prove index caused the read)
- Sub-agent read tracking (memory-index loaded in main session only, not re-read in Task subagents; measuring sub-agent reads wouldn't reflect index effectiveness)

## Open Questions

- **Relevance threshold:** How many keyword matches between session content and index entry text constitute "relevant"? Need to calibrate via manual review pilot (see Implementation Sketch #4).

## Implementation Sketch

1. **Sample selection** — Select corpus of 20-30 recent sessions spanning diverse topics (workflow development, debugging, design, implementation). Include 10-15 historical sessions (pre-index baseline) for comparison. Ensure topic coverage aligns with memory-index entry distribution.

2. **Tool usage extraction** — New parsing function to extract tool calls from assistant entries (toolName, arguments, result status). Capture timestamp for temporal ordering.

3. **Memory-index parser** — Parse memory-index.md into structured data: section → entries → {keywords, referenced_file}. Track index version per session (git commit hash at session timestamp).

4. **Session topic classifier** — Extract topics from user prompts via keyword extraction.
   - **Relevance calibration:** Run manual pilot on 5 sessions. For each session, human annotator marks which index entries should be relevant. Use this ground truth to calibrate keyword matching threshold (e.g., ≥3 keywords overlap = relevant).

5. **Relevance scorer** — Match session topics to index entries, produce relevance scores using calibrated threshold.

6. **Recall calculator** — For relevant entries, check if agent Read the referenced file.
   - **Temporal constraint:** Read must occur AFTER the prompt that triggered relevance (not before).
   - **Discovery pattern detection:** Classify each successful read as:
     - **Direct:** Read call with no preceding Grep/Glob for that file in same session
     - **Search-then-read:** Grep/Glob call mentioning file path or directory, followed by Read
     - **Ambiguous:** Grep/Glob calls exist but unclear if they led to the Read

7. **Report generator** — Produce structured report with:
   - Overall recall rate (with-index vs baseline)
   - Per-entry recall rates (which entries are effective, which are not)
   - Discovery method distribution (direct vs search-then-read)
   - False negative analysis (relevant entry, no read — was file not needed, or was discovery failed?)
   - Confounding factor notes (user-directed reads, temporal trends)
   - Recommendations for index iteration (entries to add, remove, or rephrase)
