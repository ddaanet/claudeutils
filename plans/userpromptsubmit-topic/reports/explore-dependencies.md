# Dependency Exploration Report: UserPromptSubmit Topic Injector

**Date:** 2026-02-28
**Focus:** Integration dependencies for keyword-matching topic injector feature

---

## Summary

The UserPromptSubmit topic injector will integrate three core systems: (1) **keyword extraction from memory index entries** (index_parser.py), (2) **trigger-to-section resolution** (resolver.py), and (3) **hook output channels** (userpromptsubmit-shortcuts.py). The memory-index.md contains 347 entries across agents/decisions files, parseable through two formats: new-style `/when trigger | extras` entries and legacy `key — description` entries. The resolver uses fuzzy matching to map user queries to decision file sections. The hook has a 4-tier architecture (Tier 1 commands, Tier 2 directives, Tier 2.5 pattern guards, Tier 3 continuation parsing) with two output channels: additionalContext (prose) and systemMessage (brief). Keyword matching will leverage the existing `_extract_keywords()` function and WhenEntry.extra_triggers to rank matches.

---

## Key Findings

### 1. Keyword Extraction: `index_parser.py`

**Location:** `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/src/claudeutils/recall/index_parser.py`

**Purpose:** Parse memory-index.md into structured entries with keyword extraction for recall system.

**Core Data Model:**

```python
class IndexEntry(BaseModel):
    """Parsed entry from memory-index.md."""
    key: str                    # Text before em-dash (or trigger for /when /how)
    description: str            # Text after em-dash (empty for new format)
    referenced_file: str        # File path from parent H2 heading
    section: str                # Parent H2 heading text
    keywords: set[str]          # Extracted from key + description
```

**Key Functions:**

| Function | Signature | Purpose |
|----------|-----------|---------|
| `_extract_keywords(text: str)` | `-> set[str]` | Tokenize text, remove stopwords, return lowercase keyword set |
| `_parse_new_format_line()` | `(line, current_file, current_section) -> IndexEntry \| None` | Parse `/when trigger \| extras` or `/how trigger \| extras` format |
| `_parse_old_format_line()` | `(line, current_file, current_section) -> IndexEntry \| None` | Parse legacy `key — description` format |
| `parse_memory_index(index_file: Path)` | `-> list[IndexEntry]` | Main API: read file, track H2 sections, parse all entries |

**Tokenization Details:**

```python
# _extract_keywords() implementation
def _extract_keywords(text: str) -> set[str]:
    tokens = re.split(r"[\s\-_.,;:()[\]{}\"'`]+", text.lower())
    return {token for token in tokens if token and token not in STOPWORDS}
```

- **Delimiters:** whitespace, hyphens, underscores, punctuation (`,;:()[]{}"'` `)
- **Stopwords:** 59-entry list (articles, auxiliaries, prepositions, pronouns, common verbs)
- **Output:** lowercase token set, no ordering

**Parsing Rules:**

- Skips H2 sections with titles starting with "Behavioral Rules" or "Technical Decisions" (no clear file targets)
- Processes both `/when trigger | extras` and `/how trigger | extras` in same pass
- Falls back to legacy `key — description` format (still supported)
- Returns empty list if file not readable
- Combines key + description (or trigger + extras) for keyword extraction

**Example Parsing:**

Input file:
```markdown
## agents/decisions/testing.md

/when writing mock tests | mock patch, test doubles
TDD RED Phase — verify behavior with mocking fixtures
```

Output:
```python
[
    IndexEntry(
        key="writing mock tests",
        description="",
        referenced_file="agents/decisions/testing.md",
        section="agents/decisions/testing.md",
        keywords={"writing", "mock", "tests", "patch", "test", "doubles"}
    ),
    IndexEntry(
        key="TDD RED Phase",
        description="verify behavior with mocking fixtures",
        referenced_file="agents/decisions/testing.md",
        section="agents/decisions/testing.md",
        keywords={"tdd", "red", "phase", "verify", "behavior", "mocking", "fixtures"}
    )
]
```

**Integration Points for Topic Injector:**

- Use `_extract_keywords()` to parse user prompt into tokens
- Compare keyword sets with parsed memory-index entries
- Rank matches by keyword overlap + entry extras (WhenEntry.extra_triggers analogue in IndexEntry)
- Return top-N matching entries for topic context injection

---

### 2. Section Resolution: `resolver.py`

**Location:** `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/src/claudeutils/when/resolver.py`

**Purpose:** Resolve trigger queries or section names to decision file content via three resolution modes.

**Main API:**

```python
def resolve(query: str, index_path: str, decisions_dir: str) -> str:
    """Resolve query to decision file content via prefix-based routing.

    Args:
        query: The search query (bare trigger text, may include ".." or "." prefix)
        index_path: Path to memory index file
        decisions_dir: Path to decisions directory

    Returns:
        Resolved content as string (markdown with heading + section content + source reference)

    Raises:
        ResolveError: If query cannot be resolved (missing file, ambiguous heading, etc)
    """
```

**Resolution Modes (Router):**

```python
# From resolve() implementation
if query.startswith(".."):
    return _resolve_file(query[2:].strip(), decisions_dir)
if query.startswith("."):
    return _resolve_section(query[1:].strip(), decisions_dir)
return _resolve_trigger(query, index_path, decisions_dir)
```

| Mode | Prefix | Behavior | Return Type |
|------|--------|----------|-------------|
| File | `..` | Exact file lookup in decisions_dir | Full file content with source path |
| Section | `.` | Case-insensitive heading search across all files | Section content (heading + body to next heading at same level) |
| Trigger | (none) | Fuzzy match in index, resolve via WhenEntry, extract section | Section content (heading + body + source) |

**Trigger Resolution Pipeline (`_resolve_trigger()`):**

1. **Parse index** via `parse_index(index_file)` → list[WhenEntry]
2. **Fuzzy match** on WhenEntry.trigger via `fuzzy.rank_matches(query, candidates, limit=1)`
3. **Find entry** by matched trigger text
4. **Resolve section file** from WhenEntry.section → decision file path
5. **Find heading** in file via case-insensitive search + fuzzy fallback (`_find_heading()`)
6. **Extract section** using heading boundary detection (`_extract_section_content()`)
7. **Format output** with heading + content + source reference

**Section Extraction (`_extract_section_content()`):**

```python
def _extract_section_content(heading: str, file_content: str) -> str:
    # 1. Find start_idx of heading line
    # 2. Scan from start_idx+1 until next heading at same or higher level
    # 3. Return lines[start_idx:end_idx]
    # Heading level determined by count of leading #
```

**Error Handling:**

```python
class ResolveError(Exception):
    """Error during resolution."""
```

Raised in these scenarios:

| Scenario | Error Message Format |
|----------|----------------------|
| File not found | `"File '{filename}' not found in decision files.\nAvailable:\n  ..{file1}\n  ..{file2}"` |
| Section not found | `"Section '{query}' not found.\nAvailable:\n  .{heading1}\n  .{heading2}"` (max 10 suggestions) |
| Ambiguous heading | `"Ambiguous heading '{query}' found in: {file1}, {file2}"` |
| Missing in file | `"Section not found in {file_path}: {heading_text}"` |
| File read failure | `"Failed to read {file_path}: {error}"` |

**Data Model (WhenEntry):**

```python
class WhenEntry(BaseModel):
    operator: str              # "when" or "how"
    trigger: str               # Trigger phrase (bare, no operator)
    extra_triggers: list[str]  # Pipe-delimited extras (e.g., ["mock patch", "test doubles"])
    line_number: int           # Line in index file
    section: str               # H2 section header (file path or bare name)
```

**Output Format Example:**

```
# When Writing Mock Tests

Mock tests prevent side effects and isolate behavior.

Use test doubles for external dependencies.

Source: agents/decisions/testing.md
```

**Integration Points for Topic Injector:**

- Use `resolve()` to fetch full section content given matched trigger
- Parse WhenEntry.extra_triggers as secondary keywords for ranking
- Handle ResolveError gracefully (user prompt matching may surface non-indexed topics)
- Output channel: additionalContext receives formatted content (markdown + source)

---

### 3. Hook Architecture: `userpromptsubmit-shortcuts.py`

**Location:** `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/agent-core/hooks/userpromptsubmit-shortcuts.py`

**Purpose:** Expand workflow shortcuts and parse continuation chains before sending to Claude API.

**4-Tier Expansion Architecture:**

```
Tier 1: Command shortcuts (exact match, own line) — single skill or status
  s, x, xc, r, h, hc, ci, c, y, ? → [#status], [#execute], etc.

Tier 2: Directive shortcuts (colon prefix, additive) — behavioral directives
  d:, p:, b:, q:, learn: → [DISCUSS], [PENDING], [BRAINSTORM], [QUICK], [LEARN]

Tier 2.5: Pattern guards (additive with Tier 2) — context-aware injection
  - Skill editing detected → load plugin-dev:skill-development
  - CCG platform keywords detected → use claude-code-guide agent

Tier 3: Continuation parsing (multi-skill chains, Tier 2-incompatible) — skill sequencing
  /skill1 args1, /skill2 args2 → [CONTINUATION-PASSING] directive
```

**Tier Mutual Exclusion:**

```python
# From main() implementation
if stripped in COMMANDS:          # Tier 1 match
    output = {"additionalContext": expansion, ...}
    return                        # Exclusive

directive_matches = scan_for_directives(prompt)
if directive_matches:             # Tier 2 match
    context_parts.append(...)
    output = {"additionalContext": combined_context, ...}
    return                        # Exclusive — skip Tier 3

# Tier 2.5 (pattern guards) additive regardless
if EDIT_SKILL_PATTERN.search(prompt):
    context_parts.append(...)

if CCG_PATTERN.search(prompt):
    context_parts.append(...)

# Tier 3 only if no Tier 2
registry = build_registry()
parsed = parse_continuation(prompt, registry)
if parsed:
    context_parts.append(format_continuation_context(parsed))
```

**Output Channels:**

Two independent channels delivered in single hook response:

```python
output = {
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": "...",  # Prose instruction for Claude (expanded content)
    },
    "systemMessage": "...",           # Brief summary for system message (optional)
}
```

| Channel | Content | Audience | Length |
|---------|---------|----------|--------|
| additionalContext | Full prose expansion (multi-line) | Claude (main context) | Unbounded |
| systemMessage | Brief behavioral summary (1 line) | Status bar / system message | 60-80 chars (terminal constraint) |

**Tier 2 (Directives) Output:**

```python
_DISCUSS_EXPANSION = "[DISCUSS] Evaluate critically, do not execute...\n\n..."
_DISCUSS_SYS = "discuss: assess, stress-test, state verdict. (5 lines)"

# Output for d: directive
{
    "additionalContext": "[DISCUSS] ...",
    "systemMessage": "discuss: assess, stress-test, state verdict. (5 lines)"
}
```

**Tier 2.5 (Pattern Guards) Output:**

```python
# Skill editing pattern
context_parts.append(
    "Load /plugin-dev:skill-development before editing skill files. "
    "Load /plugin-dev:agent-development before editing agent files. "
    "Skill descriptions require 'This skill should be used when...' format."
)
system_parts.append("Agent instructed: load skill-development skill")

# CCG platform keywords pattern
context_parts.append(
    "Platform question detected. Use claude-code-guide agent "
    "(subagent_type='claude-code-guide') for authoritative Claude Code documentation."
)
system_parts.append("Agent instructed to use claude-code-guide")
```

**Tier 3 (Continuation Parsing):**

```python
def parse_continuation(prompt: str, registry: dict) -> dict | None:
    """Parse multi-skill continuation chains.

    Returns:
        None if <= 1 skill detected (pass-through)
        {
            "current": {"skill": str, "args": str},
            "continuation": [{"skill": str, "args": str}, ...]
        }
    """
```

**Continuation Formats:**

```python
# Mode 2: Inline prose with delimiters
"/design plans/X/requirements.md, /runbook plans/X/design.md"
"/handoff and /commit"
"/orchestrate then /deliverable-review"

# Mode 3: Multi-line list (specific pattern, more specific than Mode 2)
"/design plans/X/requirements.md
and
- /runbook plans/X/design.md
- /deliverable-review plans/X/brief.md"
```

**Continuation Output Format:**

```python
def format_continuation_context(parsed: dict) -> str:
    """Format parsed continuation as additionalContext string."""
    # [CONTINUATION-PASSING]
    # Current: /design <args>
    # Continuation: /runbook <args>, /deliverable-review <args>
    #
    # After completing the current skill, invoke the NEXT continuation entry:
    #   Skill(skill: "runbook", args: "<args> [CONTINUATION: /deliverable-review <args>]")
    #
    # Do NOT include continuation metadata in Task tool prompts.
```

**Continuation Registry Caching:**

```python
def build_registry() -> dict[str, dict[str, Any]]:
    """Build registry of cooperative skills (cached).

    Returns:
        {
            "design": {
                "cooperative": True,
                "default-exit": ["/handoff --commit", "/commit"]
            },
            ...
        }
    """
```

Cache mechanics:

- **Path:** `{TMPDIR}/continuation-registry-{hash16}.json`
- **Hash key:** sorted skill file paths + project dir
- **Validation:** checks file mtime against cache timestamp; invalidates if any source modified
- **Extraction:** scans SKILL.md YAML frontmatter for `continuation.cooperative` and `continuation.default-exit`

**Pattern Guards (Tier 2.5):**

```python
# Regex patterns for context injection
EDIT_SKILL_PATTERN = re.compile(
    rf"(?:fix|edit|update|improve|change|modify|rewrite|refactor)\b.*\b(?:skill|agent|plugin|hook)|"
    rf"\b(?:skill|agent|plugin|hook)\b.*\b(?:fix|edit|update|improve|change|modify|rewrite|refactor)",
    re.IGNORECASE
)

CCG_PATTERN = re.compile(
    r"\b(?:hooks?|PreToolUse|PostToolUse|SessionStart|UserPromptSubmit|mcp\s+server|"
    r"slash\s+command|settings\.json|\.claude/|plugin\.json|keybinding|IDE\s+integration|"
    r"agent\s+sdk)\b",
    re.IGNORECASE
)
```

**Hook Input/Output JSON:**

```python
# Input (from Claude)
hook_input = json.load(sys.stdin)
prompt = hook_input.get("prompt", "").strip()

# Output (to Claude)
print(json.dumps(output))
sys.exit(0)  # or sys.exit(1) on error
```

**Integration Points for Topic Injector:**

- Add Tier 2.5 pattern guard for topic-matching detection (e.g., keywords from user prompt match memory-index)
- Output via additionalContext with resolved section content + source reference
- Brief systemMessage: `"topic-inject: <trigger-name>"`
- Ensure mutual exclusion: Tier 2 directives take precedence (topic injection deferred if user explicitly uses `d:`, `p:`, etc.)
- Error handling: catch exceptions in registry building and pattern matching (degraded mode: pass-through)

---

### 4. Memory Index Content: `agents/memory-index.md`

**Location:** `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/agents/memory-index.md`

**Statistics:**

- **Total entries:** 347 (counted via grep `/when \|/how `)
- **Format:** New-style `/when trigger | extras` and `/how trigger | extras` exclusively
- **Sections:** Multiple agents/decisions files listed as H2 headings
- **No legacy format:** No `key — description` entries in current memory-index.md

**Entry Structure:**

```markdown
## agents/decisions/<filename>.md

/when <trigger phrase> | <extra keyword 1>, <extra keyword 2>
/how <trigger phrase> | <extra keyword 1>, <extra keyword 2>
```

**Example Entries:**

```markdown
## agents/decisions/cli.md

/when getting current working directory
/how output errors to stderr
/when cli commands are llm-native | internal stdout markdown exit-code no-stderr
/how configure script entry points
/when writing CLI output | no destructive suggestions agents follow instructions

## agents/decisions/testing.md

/when writing mock tests | mock patch, test doubles
/how format runbook phase headers
/when choosing test framework | pytest pytest-cov fixtures
```

**Representative Patterns:**

| Pattern | Example | Count Estimate |
|---------|---------|-----------------|
| No extras | `/when getting current working directory` | ~80 (23%) |
| Single extra | `/when choosing X \| option1` | ~100 (29%) |
| Multiple extras | `/when topic \| extra1, extra2, extra3` | ~167 (48%) |
| `/when` entries | All entries starting with `/when` | ~200 (58%) |
| `/how` entries | All entries starting with `/how` | ~147 (42%) |

**Keyword Extraction Opportunities:**

From the 347 entries:
- Trigger phrases yield domain-specific keywords (e.g., "mock", "testing", "cli", "git", "hook")
- Extra_triggers (pipe-delimited) add secondary context (e.g., "pytest", "fixtures", "mocking")
- Combined keyword sets enable fuzzy ranking: user prompt tokens matched against entry keyword unions

**File Coverage:**

```markdown
## agents/decisions/cli.md — 11 entries
## agents/decisions/data-processing.md — 18 entries
## agents/decisions/defense-in-depth.md — 9 entries
## agents/decisions/deliverable-review.md — 3 entries
## agents/decisions/execution-strategy.md — 4 entries
## agents/decisions/hook-patterns.md — 14 entries
## agents/decisions/implementation-notes.md — 20 entries
## agents/decisions/markdown-tooling.md — 12 entries
## agents/decisions/operational-practices.md — 21 entries
## agents/decisions/operational-tooling.md — 35 entries
## agents/decisions/orchestration-execution.md — 28 entries
## agents/decisions/pipeline-contracts.md — 44 entries
## agents/decisions/project-config.md — 8 entries
## agents/decisions/prompt-structure-research.md — 5 entries
## agents/decisions/testing.md — 18 entries
## agents/decisions/validation-quality.md — 9 entries
## agents/decisions/workflow-advanced.md — 18 entries
## agents/decisions/workflow-core.md — 8 entries
## agents/decisions/workflow-execution.md — 10 entries
## agents/decisions/workflow-optimization.md — 8 entries
## agents/decisions/workflow-planning.md — 20 entries
```

---

### 5. Test Patterns and Fixtures

**Test Files:**

1. **`test_recall_index_parser.py`** — Tests for memory-index.md parsing
2. **`test_when_index_parser.py`** — Tests for /when and /how format parsing
3. **`test_when_resolver.py`** — Tests for resolution modes and output formatting
4. **`test_when_resolver_errors.py`** and **`test_when_resolver_hyphenated.py`** — Error handling and edge cases

**Key Test Patterns:**

**Index Parsing (test_recall_index_parser.py):**

```python
def test_parse_memory_index_simple_entry(tmp_path: Path) -> None:
    """Parse simple index entry with key — description."""
    index_file = tmp_path / "index.md"
    index_file.write_text(
        "## agents/decisions/testing.md\n\n"
        "TDD RED Phase — verify behavior with mocking fixtures\n"
    )
    result = parse_memory_index(index_file)
    assert result[0].key == "TDD RED Phase"
    assert result[0].description == "verify behavior with mocking fixtures"
    assert "tdd" in result[0].keywords
    assert "with" not in result[0].keywords  # Stopword filtered
```

Test fixtures:
- **tmp_path:** pytest fixture for isolated temp directories
- **index_file.write_text():** Direct markdown file creation
- **Assertions:** Check IndexEntry fields (key, description, referenced_file, section, keywords)

**Resolution (test_when_resolver.py):**

```python
def test_trigger_mode_resolves(tmp_path: Path) -> None:
    """Trigger mode resolves query via fuzzy matching."""
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## testing\n"
        "/when writing mock tests | mock patch, test doubles\n"
    )
    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()
    decision_file = decisions_dir / "testing.md"
    decision_file.write_text(
        "## When Writing Mock Tests\n\n"
        "Mock tests prevent side effects...\n"
    )
    result = resolve("writing mock tests", str(index_file), str(decisions_dir))
    assert "# When Writing Mock Tests" in result
    assert "Mock tests prevent side effects" in result
```

Test fixtures:
- **tmp_path / "decisions":** Simulates decisions directory structure
- **Multi-file setup:** Index file + decision files in same test
- **Fuzzy matching test:** Query doesn't match exact capitalization; fuzzy fallback used

**Error Handling (implicit in test_when_resolver.py):**

```python
def test_file_mode_resolves(tmp_path: Path) -> None:
    # ...
    with pytest.raises(ResolveError):
        resolve("..nonexistent.md", str(index_file), str(decisions_dir))
```

**Integration Points for Topic Injector Tests:**

1. **Keyword matching tests:** Compare user prompt tokens against IndexEntry.keywords
2. **Ranking tests:** Verify top-N selection by keyword overlap + extra_triggers
3. **Hook integration tests:** Verify additionalContext output formatting
4. **End-to-end tests:** User prompt → keyword extraction → index matching → section resolution → context injection

---

## Patterns and Cross-Cutting Observations

### Keyword Extraction Consistency

- **IndexEntry.keywords** and **WhenEntry.extra_triggers** provide two keyword sources
- `_extract_keywords()` is stable (stopword list, regex delimiters unchanged)
- Both can be combined: `indexed_keywords ∪ extra_trigger_keywords` for richer matching
- Lowercase normalization allows case-insensitive matching

### Resolution Pipeline Robustness

- **Fuzzy matching** in resolver handles abbreviations and missing articles
- **Section extraction** via heading level detection prevents over-inclusion
- **Error messages** include suggestions (up to 10 headings), user-friendly
- **Output format** is consistent (H1 heading + section body + source reference)

### Hook Output Architecture

- **Dual channels** (additionalContext + systemMessage) separate prose from UI display
- **Tier mutual exclusion** prevents conflicting directives (Tier 1 > Tier 2 > Tier 3)
- **Pattern guards** (Tier 2.5) are additive—can fire alongside Tier 2 or 3
- **Continuation registry caching** avoids repeated YAML parsing and filesystem scans

### Entry Format Versioning

- **Dual format support:** Legacy `key — description` and modern `/when trigger | extras`
- **Gradual migration:** Both formats coexist; old format skipped in memory-index but supported in recall
- **Extra triggers:** Pipe-delimited in new format, encoded as CSV in extras string

---

## Gaps and Unresolved Questions

### 1. Keyword Overlap Ranking Algorithm

- **Question:** How to rank IndexEntry matches by keyword overlap? Simple intersection? Jaccard similarity?
- **Impact:** Topic injector must define ranking strategy (e.g., prioritize exact keyword matches over substring matches)
- **Evidence:** Tests use assertions, not ranking scores; algorithm design required

### 2. Extra Triggers Integration with IndexEntry

- **Question:** IndexEntry has only `keywords: set[str]`; WhenEntry has `extra_triggers: list[str]`. Should topic injector use resolved WhenEntry.extra_triggers or pre-extracted IndexEntry.keywords?
- **Impact:** Two code paths: (a) parse index → match keywords, or (b) parse index → resolve trigger → fetch WhenEntry → use extra_triggers
- **Decision needed:** Hybrid approach? Dual ranking (primary: keywords, secondary: extra_triggers)?

### 3. False Positive Filtering in Pattern Matching

- **Question:** Hook's `_should_exclude_reference()` filters skill references. How to prevent topic injection for prose mentions of memory-index entries (e.g., "when fixing bugs" in normal conversation)?
- **Impact:** Risk of injecting topics when user is discussing, not querying
- **Mitigation:** Pattern guards need heuristics (keyword density? sentence structure? explicit directive markers?)

### 4. Performance: Keyword Extraction at Runtime

- **Question:** Should keyword extraction happen once (at index parse time, stored in IndexEntry) or at query time (user prompt tokenization)?
- **Evidence:** Current code extracts keywords once during `parse_memory_index()`, reuses the set
- **Trade-off:** Pre-extraction saves runtime CPU; dynamic extraction adapts to prompt context

### 5. Context Window Impact

- **Question:** How much memory-index content fits in additionalContext without exceeding token budgets?
- **Evidence:** No explicit limit in userpromptsubmit-shortcuts.py; `format_continuation_context()` builds multi-line prose
- **Design decision needed:** Cap resolution results? Truncate section content?

### 6. Continuation Registry Loading in Hooks

- **Question:** `build_registry()` loads SKILL.md files from `.claude/skills` and plugins. Topic injector won't need continuation registry; should it be skipped for topic injection?
- **Evidence:** Tier 3 only activates if no Tier 2 directives; topic injection could coexist with Tier 3
- **Impact:** Registry loading is cached but still has file I/O cost on cache miss

### 7. Hook Exit Code Semantics

- **Question:** When should hook exit with 0 vs 1? Current code exits 0 for pass-through; 1 only on error. Topic injection success should be silent (0)?
- **Evidence:** No explicit error paths in topic matching logic; graceful degradation expected
- **Design decision needed:** Should failed matches be logged? Silent pass-through?

---

## Integration Checklist for Topic Injector Implementation

### Phase 1: Keyword Matching
- [ ] Design ranking algorithm (keyword overlap metric)
- [ ] Implement keyword-to-IndexEntry matching
- [ ] Test fuzzy matching for misspellings/variations

### Phase 2: Hook Integration
- [ ] Add topic-injection pattern guard (Tier 2.5) or separate tier
- [ ] Implement output formatting (additionalContext + systemMessage)
- [ ] Ensure mutual exclusion with Tier 1 and Tier 2

### Phase 3: Resolution and Output
- [ ] Call `resolve()` for top-ranked entries
- [ ] Handle ResolveError gracefully (omit if missing, don't block)
- [ ] Format combined additionalContext (multiple resolved sections)

### Phase 4: Testing
- [ ] Unit tests: keyword extraction from user prompt
- [ ] Unit tests: ranking algorithm (expected order)
- [ ] Integration tests: hook input → additionalContext output
- [ ] End-to-end tests: realistic user prompts → injected topics

### Phase 5: Performance and Edge Cases
- [ ] Benchmark keyword extraction (profile on 347-entry index)
- [ ] Test topic injection with Tier 2 directives (precedence)
- [ ] Test with missing decision files (error handling)
- [ ] Test with empty user prompts (no false positives)

---

## Code Snippets for Reference

### Extracting Keywords from User Prompt

```python
from claudeutils.recall.index_parser import _extract_keywords

prompt = "how to write unit tests with mocking"
prompt_keywords = _extract_keywords(prompt)
# → {"write", "unit", "tests", "mocking"}
```

### Matching Keywords Against Indexed Entries

```python
from claudeutils.recall.index_parser import parse_memory_index

index_entries = parse_memory_index(Path("agents/memory-index.md"))

prompt_keywords = _extract_keywords("writing mock tests")
# → {"writing", "mock", "tests"}

matches = [
    (entry, len(prompt_keywords & entry.keywords))
    for entry in index_entries
]
matches.sort(key=lambda x: x[1], reverse=True)
top_match = matches[0][0] if matches and matches[0][1] > 0 else None
# → IndexEntry(key="writing mock tests", ...)
```

### Resolving Entry to Section Content

```python
from claudeutils.when.resolver import resolve, ResolveError

trigger_phrase = top_match.key
try:
    content = resolve(trigger_phrase, "agents/memory-index.md", "agents/decisions")
    # content includes heading + section body + "Source: agents/decisions/<file>.md"
except ResolveError as e:
    # Handle missing file or section; log error, skip injection
    pass
```

### Hook Output Formatting

```python
import json
import sys

output = {
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": f"Topic matched: {trigger_phrase}\n\n{content}",
    },
    "systemMessage": f"topic-inject: {trigger_phrase}"
}
print(json.dumps(output))
sys.exit(0)
```

---

## Files Affected / Modified

**Dependency Files (Read-Only for Topic Injector):**
- `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/src/claudeutils/recall/index_parser.py` — keyword extraction, IndexEntry model
- `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/src/claudeutils/when/resolver.py` — section resolution API
- `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/agent-core/hooks/userpromptsubmit-shortcuts.py` — hook architecture, output channels
- `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/agents/memory-index.md` — 347 indexed entries

**Test Files (Reference):**
- `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/tests/test_recall_index_parser.py` — IndexEntry parsing tests
- `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/tests/test_when_resolver.py` — section resolution tests
- `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/tests/test_when_index_parser.py` — WhenEntry parsing tests

**Implementation Files (To Be Created):**
- Topic matcher module (keyword-to-entry mapping)
- Hook integration (Tier 2.5 pattern guard or new tier)
- Tests for topic matching and hook output

---

## Summary Table: Key Interfaces

| Module | Class/Function | Signature | Returns | Purpose |
|--------|---|---|---|---|
| index_parser | IndexEntry | (Pydantic model) | — | Parsed memory-index entry with keywords |
| index_parser | `_extract_keywords()` | `(text: str) -> set[str]` | set of lowercase tokens | Keyword extraction (stopword-filtered) |
| index_parser | `parse_memory_index()` | `(index_file: Path) -> list[IndexEntry]` | List of entries | Parse entire memory-index.md |
| when.index_parser | WhenEntry | (Pydantic model) | — | Entry from /when /how format |
| when.index_parser | `parse_index()` | `(index_path: Path) -> list[WhenEntry]` | List of entries | Parse /when /how entries from index |
| resolver | `resolve()` | `(query: str, index_path: str, decisions_dir: str) -> str` | Section content (markdown + source) | Resolve trigger/heading/file to content |
| resolver | ResolveError | (Exception) | — | Raised on resolution failure |
| userpromptsubmit-shortcuts | `main()` | `() -> None` | JSON to stdout | Hook entry point; routes to appropriate tier |
| userpromptsubmit-shortcuts | `parse_continuation()` | `(prompt: str, registry: dict) -> dict \| None` | Continuation dict or None | Parse multi-skill chains |
| userpromptsubmit-shortcuts | `find_skill_references()` | `(prompt: str, registry: dict) -> list[tuple]` | List of (pos, skill_name, args_start) | Locate skill references in prompt |
| userpromptsubmit-shortcuts | `build_registry()` | `() -> dict[str, dict[str, Any]]` | Skill registry dict (cached) | Load cooperative skills from files |

