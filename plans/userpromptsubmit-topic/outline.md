# Design Outline: UserPromptSubmit Topic Injection

## Approach

Ambient recall injection via UserPromptSubmit hook. When a user prompt contains keywords matching memory-index entries, resolve the corresponding decision file sections and inject as additionalContext. User sees matched trigger lines in systemMessage.

**Scoring algorithm:** Reuse `score_relevance()` from `recall/relevance.py` — normalized entry coverage (`|Q∩D|/|D|`, threshold 0.3). Grounding: BM25/TF-IDF inoperative for this corpus (TF=1, N=200); Jaccard penalizes recall. Entry coverage is tested, deployed, statistic-free. See `plans/reports/scoring-algorithm-grounding.md`.

**Architecture:** New module `src/claudeutils/recall/topic_matcher.py` containing the matching pipeline. Hook integration in `userpromptsubmit-shortcuts.py` — parallel detector block in the flattened architecture.

**Prerequisite complete:** Hook tier flattening delivered. All features are parallel detectors accumulating into `context_parts`/`system_parts` with single output assembly. No early returns. Commands match any line. Integration tests cover all feature combinations.

## Key Decisions

### D-1: Scoring formula — entry coverage via direct `score_relevance()` call [FR-2]
`|prompt_keywords ∩ entry_keywords| / |entry_keywords|`, threshold 0.3. Call `score_relevance()` directly (synthetic session_id `"hook"`). Entry-centric: "what fraction of this topic's keywords appear in the prompt?" — high score means the prompt is about this topic.

### D-2: Inverted index for candidate lookup [FR-1, FR-4]
Build keyword → list[IndexEntry] mapping from parsed index. On prompt arrival, tokenize prompt → collect candidate entries via keyword lookup → score only candidates. Avoids iterating all entries. Cached alongside parsed index (same mtime invalidation).

### D-3: Additive with all features [FR-5, NFR-2, C-1]
Topic injection is one of several parallel feature detectors in the flattened hook architecture. All features (command expansion, directive tagging, pattern guards, continuation parsing, topic injection) fire independently and accumulate into unified `context_parts`/`system_parts` output.

- Commands — match any line (not just first), expand, accumulate
- Directives — detect behavioral modifiers, accumulate
- Pattern guards — detect domain keywords, accumulate
- Continuations — detect multi-skill chains, accumulate
- Topic injection — detect decision-relevant keywords, accumulate

**Integration point:** Topic injection is a new detector block in the existing parallel architecture. Inserts between pattern guards and continuation parsing in `main()`. No insertion-point complexity — same accumulate pattern as all other features.

### D-4: Cache strategy — project-local `tmp/` [FR-4, NFR-1]
- Cache path: `tmp/topic-index-{hash}.json` (project-local per CLAUDE.md tmp rule)
- Hash key: memory-index.md path + project dir
- Invalidation: mtime comparison
- Contents: inverted index + parsed entries (avoid re-parsing on each prompt)
- Cold build: parse memory-index.md (all entries) + build inverted index. Cheap — regeneration on worktree creation is acceptable.
- Must fit within 5s hook timeout shared with all features.
- Note: continuation registry currently uses `$TMPDIR` — migration to `tmp/` is a separate pending task.

### D-5: Resolution — section extraction from decision files [FR-3]
For top-N matched entries above threshold, extract the decision section content from the file referenced by `IndexEntry.referenced_file`. Each `IndexEntry` carries `referenced_file` (H2 heading = file path) and `key` (trigger text) — use these to locate the decision file and extract the section headed by the trigger's `When`/`How` heading. Reuse `_extract_section_content()` from `when/resolver.py` for heading-boundary extraction. Handle missing files or sections silently (skip entry, no hook failure). Combine resolved sections into single additionalContext payload.

Note: `resolve()` itself is not called — it expects a query string for fuzzy CLI lookup via `WhenEntry`. The hook has exact `IndexEntry` references, so direct file + heading extraction is the correct path.

### D-6: Token budget — entry count cap [FR-6, C-3]
Cap injected entries at N (design decision: start with 3, calibrate empirically). When matches exceed cap, highest-scored entries win. Token counting deferred per C-3 (requirements note: "token count replaces line count when token count caching infrastructure lands").

### D-7: Dual-channel output [FR-3, FR-7, C-2]
- `additionalContext`: resolved decision sections with heading + content + source. Prefixed with context header.
- `systemMessage`: matched trigger lines (full `/when trigger | extras` minus `/when` prefix), newline-separated, with injected line count: `"topic (N lines):\ntrigger1 | extras\ntrigger2 | extras"`. This entire block is a single entry in `system_parts` — the existing hook joins system_parts with `" | "`, so the topic block must be pre-formatted as one string containing internal newlines.

### D-8: Code block filtering (Q-1) — DROPPED
Dropped (YAGNI). Existing Tier 2.5 pattern guards match full prompts without fence filtering and work in production. Threshold 0.3 + cap 3 limits false positive impact. Add if false positives from code blocks manifest in practice.

### D-9: Pattern guard interaction (Q-2)
Additive, not exclusive. If CCG_PATTERN fires AND topic matching finds hook-related entries, both inject. The contexts are complementary: pattern guard says "use claude-code-guide agent," topic injection provides the relevant decision content. No dedup needed — different content channels.

### D-10: Calibration via retrospective transcript analysis
Parameters (threshold 0.3, cap 3) are declared-ungrounded — borrowed from `score_relevance()` production use for a different context (session-level vs prompt-level keyword overlap). Calibration uses existing `plans/prototypes/session-scraper.py` (extend if needed) to extract prompts + topic systemMessages from `~/.claude/` transcripts, re-run matcher with threshold 0.0 to reconstruct full score distributions, and determine optimal parameters from empirical data. Calibration script work is a separate task, out of scope for this implementation.

**systemMessage format stability:** The systemMessage format is a contract for scraping, not just cosmetic. Include trigger keys in stable, parseable form.

## Scope Boundaries

**IN:**
- Keyword table construction from memory-index.md (FR-1)
- Prompt matching and ranking (FR-2)
- Content resolution and injection via additionalContext (FR-3)
- Cache with mtime invalidation (FR-4)
- Hook integration into flattened architecture (FR-5, assumes prerequisite complete)
- Token/entry budget cap (FR-6)
- User-visible trigger feedback via systemMessage (FR-7)
- Unit tests for matcher module
- Integration tests for hook output

**OUT:**
- Sub-agent recall injection
- Memory-index generation/maintenance
- Deep recall pipeline integration
- Decision file content authoring
- Token counting infrastructure (deferred)
- Code block filtering (dropped — YAGNI, add if needed)
- Calibration script (separate task, uses existing session-scraper prototype)
- Continuation registry migration from `$TMPDIR` to `tmp/` (separate task)
- Fuzzy matching of prompt against triggers (unnecessary — keyword overlap sufficient, fuzzy is for interactive `/when` CLI)

## Affected Files

**New:**
- `src/claudeutils/recall/topic_matcher.py` — matching pipeline (build index, match prompt, resolve entries)
- `tests/test_recall_topic_matcher.py` — unit tests
- `tests/test_ups_topic_integration.py` — integration tests for hook output with topic injection

**Modified:**
- `agent-core/hooks/userpromptsubmit-shortcuts.py` — add topic injection detector block

**Read-only dependencies:**
- `src/claudeutils/recall/index_parser.py` — `_extract_keywords()`, `parse_memory_index()`. Note: `_extract_keywords()` is private API; promote to public (`extract_keywords()`) or inline tokenization logic in topic_matcher.
- `src/claudeutils/recall/relevance.py` — `score_relevance()` (direct call)
- `src/claudeutils/when/resolver.py` — `_extract_section_content()` for heading-boundary extraction (not `resolve()` — see D-5). Note: also private API; same promotion consideration applies.
- `agents/memory-index.md` — source data

## Open Questions

None — Q-1 and Q-2 resolved in D-8 and D-9.

## Risks

- **Performance:** Cold cache parse of all memory-index entries + inverted index build. Mitigation: profile during implementation; regeneration is cheap, budget shared with existing tiers (fast: regex, dict lookup).
- **False positives:** Common keywords ("error", "file", "test") match many entries. Mitigation: threshold 0.3 means entry must have 30%+ of its keywords matched; combined with entry count cap (3), only strong matches surface.
- **Threshold calibration:** 0.3 threshold and cap 3 are declared-ungrounded (different context from `score_relevance()` production use). Calibration via D-10 retrospective analysis. SystemMessage visibility provides real-time observability.
- **Context budget pressure:** Injected content adds to the ~150 user rule budget before adherence degradation (recall: "too many rules in context"). D-6 cap mitigates, but resolved decision sections vary in length. Mitigation: monitor systemMessage line counts during initial deployment; tighten cap if degradation observed.
- ~~**Prerequisite dependency:**~~ Resolved — hook tier flattening delivered.
