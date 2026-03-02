# Active Recall System

Brief from architectural discussion (2026-03-02).

## Vision

Replace training-data reliance for operational methodology with grounded recall. Training provides reasoning capability; recall provides authoritative inputs to reason over. Interaction structure (skills, tool gates, PreToolUse hooks) enforces application at the right moments.

## Core Architecture Decisions

### Recall-Explore-Recall Pattern

Primary differentiator over RAG. Agent recalls based on initial understanding, explores codebase, recalls again with enriched context. Second pass matches entries invisible from initial request alone.

Classical RAG retrieves by content similarity (what a document says). This system retrieves by applicability condition (when/where an entry applies). Precision improves with model reasoning capability, not embedding quality.

### Trigger Class Distinction

- **`when` entries:** Situational — match on agent context/situation. Primarily project decisions. Nuance matters, hand-curation justified.
- **`how` entries:** Task-descriptive — match on agent's current task. Primarily reference documentation. Automation-safe — documentation headings are already close to triggers.

### Hierarchical Index

Root index maps domains to child indices. Lookup is O(log_k(N)) with branching factor k. Current flat memory-index (~200 entries) is halfway there — sections as implicit domains. Splitting into separate files + root pointer is mechanical.

Required for scaling: bulk documentation conversion will produce thousands of entries exceeding flat index capacity.

### Three Learning Categories

- **Internal decisions:** Project choices. Invalidated only by explicit user decision.
- **External environment facts:** Dependency/tool facts. Auto-invalidated on version change. Corpus partitioned by dependency — version bump triggers subtree re-evaluation only.
- **Hybrid:** Internal decisions grounded in external facts. Version change triggers re-evaluation; decision may survive if reasoning still holds.

### Automated Documentation Conversion

External reference documentation (Python stdlib, pytest, pydantic, click, ruff, mypy) converted to how/when entries via sonnet-grade agents + corrector pass. Corrector validates trigger specificity and dedup in clean context.

### Memory Format Grounding

Prerequisite before bulk conversion. Needs `/ground` on: naming conventions, trigger structure, how/when distinction formalization, index hierarchy design.

## Relationship to Existing Work

**Absorbs or relates to:**
- Recall tool consolidation (1.9) — rename, mode reduction, resolver simplification
- Generate memory index (1.4) — keyword declarations, diff display
- Recall deduplication (1.0) — session context filtering
- Recall pipeline (1.0) — stdin format, session log dedup
- Recall learnings design (0.9) — learnings.md as resolvable entries

**Grounding artifacts:**
- `plans/reports/recall-lifecycle-grounding.md` — lifecycle patterns, mode assignments
- `plans/reports/recall-lifecycle-internal-codebase.md` — internal inventory
- `plans/reports/recall-lifecycle-external-research.md` — external frameworks

## Benchmark Positioning

SWE-ContextBench (Zhu et al., Feb 2026): evaluates five experience reuse paradigms, finds only oracle summary reuse reliably improves performance. Gap: no benchmark tests LLM-resolved indexes or recall-explore-recall. Position as sixth paradigm — if it matches oracle performance without an oracle, that demonstrates intentional indexation value.
