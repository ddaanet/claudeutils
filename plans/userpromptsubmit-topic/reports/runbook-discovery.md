# Runbook Discovery: UserPromptSubmit Topic Injection

**Exploration Date:** 2026-02-28

**Purpose:** Verify file locations and understand existing patterns for UserPromptSubmit topic injection feature.

---

## 1. Hook Architecture (userpromptsubmit-shortcuts.py)

**File:** `/Users/david/code/claudeutils-wt/ups-topic-injection/agent-core/hooks/userpromptsubmit-shortcuts.py`

**Verification Status:** CONFIRMED — Flattened architecture is in place.

### Architecture Overview

The hook implements a **flattened, parallel-accumulation architecture** with no early returns:

1. **Tier 1: Command shortcuts** (lines 34-70)
   - Exact match on its own line
   - COMMANDS dict maps (s, x, xc, r, h, hc, ci, c, y, ?) → expansion strings
   - systemMessage includes expansion or "first wins" warning if multiple commands

2. **Tier 2: Directive shortcuts** (lines 72-165)
   - Colon-prefix pattern (d:, p:, b:, q:, learn: and aliases)
   - DIRECTIVES dict + DIRECTIVE_SYSTEM_MSGS for dual-format output
   - Additive: all matching directives fire in parallel

3. **Tier 2.5: Pattern guards** (lines 170-186)
   - EDIT_SKILL_PATTERN: detects skill/agent editing (injects `/plugin-dev:skill-development`)
   - CCG_PATTERN: detects platform questions (injects `claude-code-guide` subagent directive)
   - Additive: guards fire in parallel with Tier 2

4. **Tier 3: Continuation parsing** (lines 685-796)
   - Multi-skill chain detection (Mode 2: inline prose, Mode 3: multi-line list)
   - Parses continuation chains: `/skill1 args and /skill2 args`
   - Returns None if ≤1 skill (Claude's built-in skill system handles single skills)

### Output Assembly (lines 874-954)

**Accumulator pattern (flattened, no early returns):**
- `context_parts: list[str]` — all expansions combined via `"\n\n".join()`
- `system_parts: list[str]` — brief summaries for systemMessage

**Final output assembly (line 940-950):**
```python
if context_parts:
    combined_context = "\n\n".join(context_parts)  # Flattened
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": combined_context,
        }
    }
    if system_parts:
        output["systemMessage"] = " | ".join(system_parts)
    print(json.dumps(output))
    return
# No match: silent pass-through
sys.exit(0)
```

**Key pattern:** All features accumulate into a single `additionalContext` block. No feature short-circuits; the hook completes all applicable transformations before output assembly.

### Registry Caching (lines 393-581)

**Cache pattern (mtime-based invalidation):**

**Functions:**
- `get_cache_path(paths: list[str], project_dir: str) -> Path` (lines 393-415)
  - Generates cache path via SHA256 hash of sorted skill paths + project dir
  - Uses `TMPDIR` env var, falls back to `/tmp/claude`
  - Returns `<cache_dir>/continuation-registry-{hash}.json`

- `get_cached_registry(cache_path: Path) -> dict[str, Any] | None` (lines 418-458)
  - Loads cache if valid
  - Validates: paths present, timestamps newer than cache
  - Returns None if any source file modified or deleted (cache invalidation)

- `save_registry_cache(registry: dict[str, Any], paths: list[str], cache_path: Path)` (lines 461-478)
  - Stores: `{paths, registry, timestamp: time.time()}`
  - Silent failure (continues in degraded mode if caching fails)

**Cache structure:**
```json
{
  "paths": ["/path/to/skill.md", ...],
  "registry": {
    "skill_name": {
      "cooperative": true,
      "default-exit": ["/handoff --commit", "/commit"]
    },
    ...
  },
  "timestamp": 1234567890.123
}
```

---

## 2. Index Parser (index_parser.py)

**File:** `/Users/david/code/claudeutils-wt/ups-topic-injection/src/claudeutils/recall/index_parser.py`

**Key Functions:**

### `_extract_keywords(text: str) -> set[str]` (lines 72-87)

**Signature:**
```python
def _extract_keywords(text: str) -> set[str]
```

**Behavior:**
- Tokenizes on `[\s\-_.,;:()[\]{}\"'\`]+` (whitespace, punctuation, dashes, underscores)
- Lowercases all tokens
- Removes STOPWORDS (58-word English set: a, an, the, is, are, for, from, with, etc.)
- Returns set of remaining tokens

**Note:** This function is **private** (underscore prefix). No public version exists; it's used internally by `parse_memory_index()`.

### `IndexEntry` (lines 62-69)

**Model fields:**
```python
class IndexEntry(BaseModel):
    key: str                    # Trigger text (key before em-dash)
    description: str            # Text after em-dash
    referenced_file: str        # From H2 heading (file path)
    section: str                # Parent H2 heading text
    keywords: set[str]          # Extracted from key + description
```

### `parse_memory_index(index_file: Path) -> list[IndexEntry]` (lines 142-186)

**Signature:**
```python
def parse_memory_index(index_file: Path) -> list[IndexEntry]
```

**Return type:** `list[IndexEntry]`

**Behavior:**
- Parses memory-index.md into structured entries
- Extracts H2 sections (treated as file paths)
- Supports two entry formats:
  - **New format:** `/when trigger | extra keywords` or `/how trigger | extra keywords`
  - **Old format:** `key — description` (deprecated but supported)
- **Skips sections:** "Behavioral Rules (fragments — already loaded)", "Technical Decisions (mixed — check entry for specific file)"
- Keywords extracted via `_extract_keywords(trigger + " " + extras)` for new format
- **Returns empty list** on file read error (graceful degradation)

---

## 3. Relevance Scorer (relevance.py)

**File:** `/Users/david/code/claudeutils-wt/ups-topic-injection/src/claudeutils/recall/relevance.py`

### `score_relevance()` (lines 18-55)

**Signature:**
```python
def score_relevance(
    session_id: str,
    session_keywords: set[str],
    entry: IndexEntry,
    threshold: float = 0.3,
) -> RelevanceScore
```

**Parameters:**
- `session_id: str` — Session identifier (can be synthetic, no validation)
- `session_keywords: set[str]` — Keywords extracted from session
- `entry: IndexEntry` — Index entry to score against
- `threshold: float = 0.3` — Relevance threshold (default 0.3)

**Return type:** `RelevanceScore`

**Scoring:**
- Computes `score = |intersection| / |entry.keywords|` (normalized keyword overlap)
- Measures what fraction of entry keywords appear in session
- `is_relevant = score >= threshold`
- Returns: score, is_relevant flag, matched_keywords set

**Key property:** `session_id` has no validation — can pass any string, including synthetic IDs.

### `RelevanceScore` (lines 8-15)

**Model fields:**
```python
class RelevanceScore(BaseModel):
    session_id: str
    entry_key: str
    score: float                # 0.0 to 1.0
    is_relevant: bool           # True if score >= threshold
    matched_keywords: set[str]  # Keywords that matched
```

---

## 4. Section Extractor (when/resolver.py)

**File:** `/Users/david/code/claudeutils-wt/ups-topic-injection/src/claudeutils/when/resolver.py`

### `_extract_section_content()` (lines 307-330)

**Signature:**
```python
def _extract_section_content(heading: str, file_content: str) -> str
```

**Parameters:**
- `heading: str` — The heading line to search for (with # markers)
- `file_content: str` — Full file content

**Behavior:**
1. Detects heading level by counting leading `#` characters
2. Finds heading via `_heading_matches()` (case-insensitive comparison)
3. Extracts from heading to next heading of equal or higher level
4. Boundary detection: stops at any line starting with `#` where heading_level ≤ current_level
5. Returns extracted section with trailing newlines stripped
6. Returns empty string if heading not found

**Return type:** `str` (section content)

**Heading boundary rules:**
- Counts leading `#` to determine level
- H2 heading (`##`) stops at any H2 or H1 (`#`)
- H3 heading (`###`) stops at any H2, H1, or H3
- Section includes opening heading line

**Note:** This function is **private** (underscore prefix). There is a public wrapper `_extract_section()` at lines 333-339 that handles file I/O and returns the section.

---

## 5. Memory Index Format (agents/memory-index.md)

**File:** `/Users/david/code/claudeutils-wt/ups-topic-injection/agents/memory-index.md`

**Format Overview (first 30 lines):**

```markdown
# Memory Index

Active knowledge retrieval. Invoke `/when` or `/how` to recall decisions.

**Invocation:**
/when <trigger>        # behavioral knowledge (when to do X)
/how <trigger>         # procedural knowledge (how to do X)

**Navigation:**
/when .Section Title   # section content by heading name
/when ..file.md        # entire decision file (relative to agents/decisions/)

**Consumption:** This index is loaded via CLAUDE.md @-reference. Do NOT re-read this file. Scan entries, invoke `/when` or `/how` for details.

**Append-only.** Do not index content already loaded via CLAUDE.md fragments.
```

**Entry Format:**

```
## agents/decisions/cli.md

/when getting current working directory
/how output errors to stderr
/when cli commands are llm-native | internal stdout markdown exit-code no-stderr
```

**Structure:**
- **H2 headings:** File paths (e.g., `agents/decisions/cli.md`)
- **Entry lines:** `/when trigger` or `/how trigger` optionally followed by `| extra keywords`
- **Pipe extras:** Comma-separated keywords for relevance scoring
- **Append-only:** New entries added to end of appropriate section

---

## 6. Test Patterns

**Explored Files:**
- `/Users/david/code/claudeutils-wt/ups-topic-injection/tests/test_recall_index_parser.py`
- `/Users/david/code/claudeutils-wt/ups-topic-injection/tests/conftest.py`

### Test Structure (test_recall_index_parser.py)

**Fixture pattern:** Uses pytest's `tmp_path` fixture for temporary file creation.

**Example test:**
```python
def test_parse_memory_index_simple_entry(tmp_path: Path) -> None:
    """Parse simple index entry with key — description."""
    index_file = tmp_path / "index.md"
    index_file.write_text(
        "## agents/decisions/testing.md\n\n"
        "TDD RED Phase — verify behavior with mocking fixtures\n"
    )

    result = parse_memory_index(index_file)
    assert len(result) == 1
    assert result[0].key == "TDD RED Phase"
```

**Test coverage:**
- Simple entries, multiple entries, multiple sections
- Keyword extraction validation
- Special section skipping (Behavioral Rules, Technical Decisions)
- New format (/when, /how) and old format (em-dash)
- Nonexistent/empty file handling
- IndexEntry model validation

### conftest.py Patterns

**Location:** `/Users/david/code/claudeutils-wt/ups-topic-injection/tests/conftest.py`

**Key fixtures:**
- `clear_api_key`: autouse fixture clears ANTHROPIC_API_KEY (except e2e tests)
- `temp_project_dir`: Creates temporary project + history directories, patches `get_project_history_dir`
- `mock_anthropic_client`: Factory fixture for mocking Anthropic client with token counts
- `test_markdown_file`: Factory fixture for creating test markdown files
- `markdown_fixtures_dir`: Session-scope directory for test fixtures (autouse)
- `mock_models_api`: Factory for mocking models API responses
- `cli_base_mocks`: Returns dict of 'anthropic' and 'resolve' mocks with API key set

**Pattern:** Factory fixtures are common (return a callable that creates configured mocks). Monkeypatch used for environment variables and module-level patches.

---

## 7. Cache Patterns (Caching Strategy)

**Pattern verified in:** `userpromptsubmit-shortcuts.py`, lines 393-478

**Caching model for topic index (recommended pattern):**

1. **Cache key generation:**
   - SHA256 hash of sorted source file paths + project directory
   - Path: `<TMPDIR>/topic-index-{hash}.json` (following `continuation-registry-{hash}.json` pattern)

2. **Cache structure:**
   ```json
   {
     "paths": ["/path/to/memory-index.md"],
     "cache": {
       "indexed_topics": [...],
       "topics_by_session_id": {...}
     },
     "timestamp": 1234567890.123
   }
   ```

3. **Invalidation:**
   - Check `path.stat().st_mtime > cache_timestamp` for each source file
   - Return None if any file modified or deleted
   - Silent failure on cache write error (degraded mode)

4. **Environment:**
   - Use `os.environ.get("TMPDIR", "/tmp/claude")` for cache directory
   - Create directory with `mkdir(parents=True, exist_ok=True)`

---

## 8. Directory Structure

**tmp/ directory:** ✓ EXISTS and is GITIGNORED

**Verification:**
- Path: `/Users/david/code/claudeutils-wt/ups-topic-injection/tmp/`
- Contains: `.test-sentinel` (marker file) and `claude/` subdirectory
- Status: `.gitignore` includes `/tmp/` at line 6

**Gitignore configuration:**
```
# Secrets
/.env

# Volatile work files
/scratch/
/tmp/
/plans/claude/

# Node.js
/node_modules/

# Python files
__pycache__/
list/

# IDE cruft
/.vscode/

# Local configuration (per-user, not shared)
*.local.*
```

---

## Key Findings Summary

### Confirmed Patterns

1. **Hook architecture is fully flattened** — No early returns, all features accumulate into single `additionalContext` block
2. **Caching uses mtime invalidation** — Match this for topic index cache
3. **Index parser is ready** — `parse_memory_index()` handles both old (em-dash) and new (/when, /how) formats
4. **Relevance scorer is flexible** — Accepts synthetic `session_id`, no validation required
5. **Section extraction is working** — Boundary detection handles multiple heading levels correctly
6. **Test patterns use factories and tmp_path** — Recommended pattern for mock setup and file creation
7. **tmp/ directory exists and is gitignored** — Ready for cache storage

### No Contradictions Found

- Design outline assumptions about flattened hook architecture: **VERIFIED**
- Caching pattern (mtime-based): **VERIFIED** and already in use
- Public vs. private functions: **_extract_keywords is private** (no public version needed for topic index)
- Index parser handles new format: **VERIFIED** (supports `/when trigger | extras`)

### Ready for Implementation

All architectural components are in place and verified. The codebase follows consistent patterns for:
- Flattened accumulation in hooks
- Cache validation via mtime comparison
- Test fixture design via factories
- Graceful error handling (empty lists, None returns on failure)

The topic injection feature can proceed using existing patterns from the continuation registry caching and hook output assembly.

