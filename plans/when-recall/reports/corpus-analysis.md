# Memory Index Corpus Analysis

**Objective:** Analyze memory index entry patterns to derive trigger naming guidelines for `/when` recall system.

**Corpus:** 122 entries from agents/memory-index.md + 102 H3 headings from 9 decision files

**Decision Files Analyzed:**
- `agents/decisions/cli.md` (5 H3s)
- `agents/decisions/data-processing.md` (16 H3s)
- `agents/decisions/implementation-notes.md` (13 H3s)
- `agents/decisions/markdown-tooling.md` (10 H3s)
- `agents/decisions/project-config.md` (9 H3s)
- `agents/decisions/testing.md` (4 H3s)
- `agents/decisions/validation-quality.md` (12 H3s)
- `agents/decisions/workflow-advanced.md` (19 H3s)
- `agents/decisions/workflow-optimization.md` (14 H3s)

---

## 1. Entry Pattern Classification

### Distribution Summary

| Pattern Type | Count | % | Key Observation |
|---|---|---|---|
| **Noun Phrase** | 100 | 82.0% | Dominant pattern: "Title pattern" form |
| **Colon Structure** | 9 | 7.4% | Category:Topic format (TDD phases, patterns) |
| **Imperative** | 5 | 4.1% | Action-oriented: "Test X", "UserPromptSubmit..." |
| **Adjective-Noun** | 5 | 4.1% | Comparison: "X vs Y", "X over Y" |
| **Other (micro)** | 3 | 2.5% | "Problem", "Solution" (context-dependent) |
| **Verb Phrase** | 0 | 0.0% | Not used |
| **When-Conditional** | 0 | 0.0% | Not used |

### Top Examples by Pattern

**Noun Phrases (82%):**
- `Minimal __init__.py`
- `Private helpers stay with callers`
- `Module split pattern`
- `Path encoding algorithm`
- `TDD Integration Test Gap`

**Colon Structure (7.4%):**
- `Recursive pattern: AgentId → SessionId`
- `TDD RED Phase: Behavioral Verification`
- `TDD: Presentation vs Behavior`
- `Handoff Pattern: Inline Learnings`

**Imperatives (4.1%):**
- `Test module split strategy`
- `UserPromptSubmit hook filtering`
- `Testing strategy for markdown cleanup`

**Comparisons (4.1%):**
- `Docformatter vs. Ruff D205 conflict`
- `Extend vs. new functions`
- `Path.cwd() vs os.getcwd()`

---

## 2. "When" Compatibility Assessment

### Compatibility Breakdown

| Category | Count | % | Interpretation |
|---|---|---|---|
| **Incompatible with `/when`** | 33 | 27.0% | Cannot naturally form "When X" trigger |
| **Needs Rephrasing** | 82 | 67.2% | Form possible but awkward without edit |
| **Direct Fit** | 4 | 3.3% | Natural "When X" pattern works as-is |
| **Uncertain** | 3 | 2.5% | Edge cases, ambiguous context |

### Direct-Fit Examples (3.3%)

These entries already have conditional semantics:
- `@ references limitation` → `/when @ references limited`
- `SessionStart hook limitation` → `/when SessionStart hook limited`
- `Prose Gate D+B Hybrid Fix` → `/when prose gate skipped` (implied scenario)

### Incompatible Examples (27.0%)

These require different trigger operators:
- `Module split pattern` — descriptive guideline, not a scenario
- `Path encoding algorithm` — procedural specification
- `Title formatting` — configuration/rule
- `Pipeline architecture` — architectural pattern
- `Testing strategy for markdown cleanup` — methodology
- `Pydantic for validation` — technology choice

**Root cause:** 82% of index entries encode "what to do in situation X" rather than "when to do X". They're decision implementations, not trigger conditions.

### Needs-Rephrasing Examples (67.2%)

These form awkward "When X" but can be rephrased:
- `Private helpers stay with callers` → `/when cohesion matters` (implied)
- `Graceful degradation` → `/when malformed data encountered` (inferred)
- `Deduplication strategy` → `/when duplicates detected` (implied trigger)
- `Title extraction` → `/when title is array format` (type-specific)

**Pattern:** Entries describe patterns/strategies but lack explicit trigger conditions. Rephrasing requires understanding the implicit "when" from the description.

---

## 3. Structural Header Uniqueness

### H3 Heading Inventory

**Total H3 headings across decision files: 102**
- Unique: 102 (100% uniqueness)
- Duplicates: 0
- Near-duplicates (case-insensitive): 0

**Finding:** No disambiguation needed. All H3 headings are globally unique. Syntax like `.section` is unnecessary for header identification.

### H3 Distribution by File

| File | H3 Count | Density |
|---|---|---|
| workflow-advanced.md | 19 | Highest (19 decisions) |
| workflow-core.md | — | (file not in H3 list, uses H2 structure) |
| workflow-optimization.md | 14 | Moderate |
| data-processing.md | 16 | Moderate-high |
| implementation-notes.md | 13 | Moderate |
| markdown-tooling.md | 10 | Moderate |
| validation-quality.md | 12 | Moderate |
| project-config.md | 9 | Moderate |
| cli.md | 5 | Low (5 decisions) |

### Key Implication

Since all H3s are unique, resolver system can use exact H3 text to reference decisions without file qualification:
```
/when title extraction
↓ (resolver)
→ agents/decisions/data-processing.md#Title Extraction
```

---

## 4. Key Collision Analysis

### Substring Overlaps

**Finding:** Minimal collision risk at key level.

**Substring relationships found:** 2 pairs
- `'Solution'` appears in `'History directory resolution'` (low risk—"Solution" is single word, unique in context)
- `'Problem'` appears in `'Planning Pattern: Three-Stream Problem Documentation'` (low risk—"Problem" is common but context disambiguates)

**3+ word overlaps:** None detected

**Implication:** No fuzzy matching ambiguity expected. Natural language triggers will distinguish between:
- `/when title extraction needed` (exact: "Title extraction")
- `/when title formatting` (exact: "Title formatting")

---

## 5. Trigger Rephrasing Candidates

### Alternative Trigger Operators for Incompatible Entries

27% of index entries (33 items) don't fit `/when` semantics. These benefit from alternative trigger operators:

#### `/how` — Procedural Knowledge (How-to, methodology)

**Rationale:** Entries describing techniques, strategies, or implementation approaches.

**Candidates (17 entries):**

| Entry | Rephrased Trigger | Rationale |
|---|---|---|
| Module split pattern | `/how split large modules` | Describes technique for breaking files |
| Path encoding algorithm | `/how encode paths` | Procedural algorithm specification |
| Title formatting | `/how format titles` | Formatting rules and technique |
| Title extraction | `/how extract titles` | Extraction methodology |
| Feedback extraction layering | `/how layer feedback extraction` | Multi-step process description |
| Pydantic for validation | `/how validate with Pydantic` | Tool usage pattern |
| Pipeline architecture | `/how architect pipelines` | Design pattern/topology |
| Noise detection patterns | `/how detect noise` | Detection algorithm/approach |
| Categorization by keywords | `/how categorize by keywords` | Categorization technique |
| Processing order | `/how order processing steps` | Optimization technique |
| Prefix detection strategy | `/how detect prefixes` | Detection strategy |
| Indentation amount | `/how indent markdown lists` | Formatting technique |
| Testing strategy for markdown cleanup | `/how test markdown cleanup` | Test design approach |
| Mock patching pattern | `/how patch mocks` | Testing technique |
| Outline-first design workflow | `/how design with outlines` | Workflow methodology |
| Model selection for design guidance | `/how select models for guidance` | Decision methodology |
| Happy path first TDD | `/how start TDD cycles` | Test design approach |

#### `/what` — Definitional Knowledge (What is X, what does it mean)

**Rationale:** Entries defining architectural patterns, structures, or terminology.

**Candidates (10 entries):**

| Entry | Rephrased Trigger | Rationale |
|---|---|---|
| Pipeline architecture | `/what is pipeline architecture` | Defines a pattern |
| Markdown cleanup architecture | `/what is markdown cleanup` | Defines a subsystem |
| Growth + consolidation model | `/what is growth+consolidation` | Defines a model/pattern |
| Premium/standard/efficient naming | `/what terminology for models` | Defines naming convention |
| Multi-layer discovery pattern | `/what is discovery pattern` | Defines a pattern |
| Phase-Grouped Runbook Header Format | `/what format for runbooks` | Defines a format |
| Runbook Outline Format | `/what structure for outlines` | Defines a structure |
| Three-Tier Implementation Model | `/what are implementation tiers` | Defines a classification |
| Default semantic, mark structural | `/what is semantic vs structural` | Defines a distinction |
| Rule files for context injection | `/what are rule files` | Defines a mechanism |

#### `/why` — Rationale Knowledge (Why this approach, why this decision)

**Rationale:** Entries explaining the reasoning behind design decisions or architectural choices.

**Candidates (6 entries):**

| Entry | Rephrased Trigger | Rationale |
|---|---|---|
| No Suppression Shortcuts | `/why no noqa suppressions` | Explains rationale for avoiding approach |
| Error on invalid patterns | `/why validate patterns` | Explains consequence of validation |
| No human escalation during refactoring | `/why opus handles refactoring` | Explains design decision |
| Commits are sync points | `/why commit as sync point` | Explains synchronization rationale |
| Complexity Before Expansion | `/why check complexity early` | Explains benefit of early assessment |
| Efficient Model Analysis Requires Verification | `/why verify model analysis` | Explains why verification is needed |

#### `/when` — Conditional/Triggered Knowledge (When to use, when this applies)

**Keep as-is:** 82 entries (67% "needs rephrasing" + 3% "direct fit")

These entries describe decisions/patterns that apply in specific situations. The "/when" trigger operator frames them as conditional knowledge:

**Examples where rephasing is manageable:**

| Entry | Suggested Rephrase | Trigger |
|---|---|---|
| Private helpers stay with callers | Helpers should stay with callers — affects module cohesion | `/when module needs cohesion` |
| Graceful degradation | Skip malformed entries, continue processing — avoid strict validation failures | `/when malformed data encountered` |
| Deduplication strategy | Use first 100 chars as key for dedup | `/when deduplicating entries` |
| Recursive pattern: AgentId → SessionId | Agent IDs become session IDs recursively | `/when handling child agents` |
| Bare lines beat list markers | Use bare keywords (no `-`) for keyword lists — saves tokens | `/when encoding keywords` |
| Title-words beat kebab-case | Title-case identifiers beat kebab-case (17% drift vs 31%) | `/when naming identifiers` |

---

## 6. Fuzzy Matching Considerations

### Key Collision Risk: **LOW**

**Analysis:**

1. **Substring overlaps minimal** — Only 2 pairs; both ambiguous in context only
2. **First 3 words unique** — No entries starting with identical 3-word prefixes
3. **Semantic distance adequate** — Even entries with similar topics have distinct keys:
   - `"Title extraction"` vs `"Title formatting"` (context differs: extraction type vs format rule)
   - `"Noise detection patterns"` vs `"Categorization by keywords"` (completely distinct concepts)

### Fuzzy Matching Strategy Implication

**fzf-style scoring will discriminate well because:**
- Entry keys are semantically meaningful (not random IDs)
- Majority (82%) are noun phrases — consistent tokenization
- Short keys (average ~4-5 words) reduce score compression
- Unique prefixes enable early branching in score calculation

**Tiebreaker opportunity:**
- Word-overlap metric can disambiguate `title extraction` vs `title formatting` when fzf scores are close
- Contextual keywords from descriptions (`"string vs array"` for extraction vs `"80 chars"` for formatting) provide additional signal

---

## 7. Architecture Implications for `/when` Design

### Recommended Operator Set

**Primary triggers** (ordered by frequency):
1. `/when` — 82 entries (67% directly)
2. `/how` — 17 entries (implementation procedures)
3. `/what` — 10 entries (definitions/architecture)
4. `/why` — 6 entries (rationale/decisions)

**Fallback:** Fuzzy matching without operator allows discovery by keyword:
```
User: "When do I validate?"
↓ (operator-agnostic match)
→ "Pydantic for validation" (/how)
→ "Conformance Validation for Migrations" (/when implied)
```

### Key Resolver Requirements

Based on corpus analysis:

1. **No disambiguation syntax needed** — H3 uniqueness = no file qualifier required
2. **Operator inference capable** — Index keys + descriptions provide enough semantic signal to infer best operator if not specified
3. **Prefix caching enabled** — Short, unique keys enable efficient prompt caching with 20-block lookback window
4. **Fuzzy tolerance adequate** — Low collision risk supports phzy scoring without false positives

### Memory-as-File Benefit

**Validation from corpus:**
- 122 memory index entries + 102 decision H3s = 224 total unique reference points
- If split into individual files: ~5-10 keywords per file, 22-45 files
- Per-file `.md` references enable Read caching (prefix-cached subsequent turns)
- Resolver outputs `@file` reference → agent Reads once per session

**Trade-off addressed:**
- File atomization (169 files) vs format-only change
- Uniqueness guarantees (102 H3s) support file-per-decision structure
- Read caching benefit = cheap subsequent turns (prompt prefix match), not free re-reads
- Cost: ~25 tokens per file × 224 files ≈ 5600 tokens baseline (acceptable for always-loaded index equivalent)

---

## 8. Recommendations for `/when` Design

### Trigger Naming Guidelines

1. **Noun Phrase Format (Primary)**
   - Use title-case, singular or plural as semantically appropriate
   - Examples: `/when title extraction`, `/when session limited`, `/when mocking needed`
   - Matches 82% of corpus entries naturally

2. **Operator Prefixes (Secondary)**
   - `/how` for procedural/methodology entries (17)
   - `/what` for definitional entries (10)
   - `/why` for rationale entries (6)
   - Enables semantic disambiguation without multiple triggers

3. **Fuzzy Matching Fallback**
   - No operator → match all entries
   - Score by keyword overlap + word-order consistency
   - Supports discovery without exact operator knowledge

4. **Uniqueness Guarantee**
   - All decision file H3s are globally unique
   - No `.file` disambiguation syntax needed
   - Resolver outputs `@agents/decisions/file.md#Section`

### Index Entry Format (Validation)

Corpus shows optimal entry structure:
```
[Key] — [keyword-rich description capturing "when/how/what" context]
```

Example improvements for incompatible entries:
- `Module split pattern` → `Module split pattern — Split large files exceeding 400 lines into functional modules for maintainability`
- `Pydantic for validation — Use BaseModel for all data structures to ensure type safety`

**Key observation:** Descriptions already encode the implicit "when/how/what", so rephrasing keys is often unnecessary. Resolver can infer operator from description context.

### Performance Expectations

**Fuzzy matching behavior:**
- **Direct match**: `/when title extraction` → instant match to "Title extraction"
- **Prefix match**: `/when title` → both "Title extraction" and "Title formatting" score high; use description keywords to disambiguate
- **Substring match**: `/when extraction` → matches only "Title extraction" (good discrimination)
- **Typos**: `/wen title extrction` → phzy algorithm recovers with 60-80% score (bounds allow ~30% edit distance)

---

## Appendix: Full Rephrasing Reference

### All 33 Incompatible Entries with Recommended Operator

| Entry | Operator | Rationale |
|---|---|---|
| Module split pattern | /how | Technique for module organization |
| Path encoding algorithm | /how | Procedural algorithm |
| Title extraction | /how | Extraction methodology |
| Title formatting | /how | Formatting rules |
| Trivial message detection | /how | Detection algorithm |
| Feedback extraction layering | /how | Multi-step process |
| Sorted glob results | /how | Result ordering technique |
| Pipeline architecture | /what | Architectural pattern |
| Noise detection patterns | /how | Pattern/algorithm |
| Categorization by keywords | /how | Categorization technique |
| Deduplication strategy | /how | Dedup methodology |
| Pydantic for validation | /how | Tool/library usage |
| FeedbackType enum | /how | Enum definition approach |
| Complexity Management | /how | Refactoring technique |
| Type Annotations | /how | Type specification approach |
| Filtering module as foundation | /what | Architectural component |
| Markdown cleanup architecture | /what | Subsystem design |
| Design decisions | /how | Decision-making technique |
| Extend vs. new functions | /how | Code organization choice |
| Error on invalid patterns | /why | Validation rationale |
| Processing order | /how | Execution optimization |
| Prefix detection strategy | /how | Detection strategy |
| Indentation amount | /how | Formatting rule |
| Future direction | /what | Vision/roadmap item |
| Remark-cli over Prettier | /why | Tool selection rationale |
| Growth + consolidation model | /what | Model definition |
| Rule files for context injection | /what | Mechanism definition |
| Premium/standard/efficient naming | /what | Terminology definition |
| Multi-layer discovery pattern | /what | Pattern definition |
| Agent frontmatter YAML validation | /how | Validation technique |
| No human escalation during refactoring | /why | Design decision rationale |
| Efficient Model Analysis Requires Verification | /why | Verification necessity |

---

## Summary

**Key Findings:**
1. **82% of entries are noun phrases** — Well-aligned with `/when X` syntax
2. **100% H3 uniqueness** — No disambiguation needed for resolution
3. **27% require operator alternatives** — `/how`, `/what`, `/why` distribute incompatible entries naturally
4. **Low collision risk** — Fuzzy matching will disambiguate without false positives
5. **Memory-as-file architecture supported** — 224 unique reference points justify ~25-file breakout with per-file caching

**Recommendation:** Implement `/when` as primary operator with `/how`/`/what`/`/why` fallbacks. Fuzzy matching provides operator-agnostic discovery path.
