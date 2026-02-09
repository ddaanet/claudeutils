# Continuation Parser Implementation Analysis

**Date:** 2026-02-09
**Scope:** Parser detection logic, registry builder, Tier 3 integration, context-awareness mechanisms
**Status:** Critical blocker — 86.7% false positive rate requires design fix

---

## Summary

The continuation parser in `userpromptsubmit-shortcuts.py` is a Tier 3 UserPromptSubmit hook that detects skill references in user input and injects continuation chains via `additionalContext`. The implementation includes registry discovery (project-local + plugin skills), three parsing modes for different syntaxes, and caching for performance. However, empirical validation (Step 3.5) revealed an 86.7% false positive rate: the parser triggers on skill references in meta-discussion, file paths, and command output contexts where continuation should NOT apply. This violates FR-5 (prose-to-explicit translation accuracy) and corrupts skill args when misidentified.

---

## Key Findings

### 1. Parser Detection Logic (Current Approach)

**File:** `/Users/david/code/claudeutils-continuation-passing/agent-core/hooks/userpromptsubmit-shortcuts.py`

**Detection Pattern:** Lines 377-382 (function `find_skill_references`)

```python
def find_skill_references(prompt: str, registry: Dict[str, Dict[str, Any]]) -> List[tuple]:
    """Find all skill references in the prompt."""
    references = []

    # Find all /word patterns
    for match in re.finditer(r'/(\w+)', prompt):
        skill_name = match.group(1)
        if skill_name in registry:
            references.append((match.start(), skill_name, match.end()))

    return references
```

**Mechanism:**
- Uses simple regex `/(\w+)` to find all `/word` patterns
- Validates against cooperative skill registry (existence check only)
- Returns list of `(position, skill_name, args_start)` tuples
- No context analysis before or after the `/` character

**Critical Limitation — No Context Awareness:**
- Matches `/commit` in "Remember to use /commit skill" (prose)
- Matches `/handoff` in "plans/handoff-lite-issue/design.md" (file path)
- Matches `/commit` in `<bash-stdout>/commit</bash-stdout>` (XML/output)
- Matches `/orchestrate` in `/orchestrate-workflow.md` (file name)

**Result:** `find_skill_references()` returns matches regardless of surrounding context, passing all positives to downstream parsing modes.

---

### 2. Three Parsing Modes

**Function:** `parse_continuation()` (lines 385-564)

#### Mode 1: Single Skill (Lines 402-427)

**Trigger:** Exactly one skill reference found in prompt

**Logic:**
```python
if len(references) == 1:
    pos, skill_name, args_start = references[0]
    args = prompt[args_start:].strip()

    # Get default exit for this skill
    default_exit = registry[skill_name].get('default-exit', [])

    # Special case: /handoff without --commit flag is terminal
    if skill_name == 'handoff' and '--commit' not in args:
        default_exit = []

    # Build continuation entries from default exit
    continuation = []
    for exit_entry in default_exit:
        exit_match = re.match(r'/(\w+)(?:\s+(.*))?', exit_entry.strip())
        if exit_match:
            exit_skill = exit_match.group(1)
            exit_args = exit_match.group(2) or ''
            continuation.append({'skill': exit_skill, 'args': exit_args.strip()})

    return {
        'current': {'skill': skill_name, 'args': args},
        'continuation': continuation
    }
```

**Behavior:**
- Current skill = the single skill found
- Args = everything after the skill reference
- Continuation = skill's default-exit chain from registry
- Special handling: `/handoff` without `--commit` flag returns empty continuation (terminal)

**False Positive Example:**
- Input: "Remember to use /commit skill"
- Mode 1 triggered: single `/commit` match
- Returns: `current={'skill': 'commit', args': 'skill'}, continuation=[]`
- Result: "skill" is treated as args for commit → corrupts invocation

#### Mode 3: Multi-Line List Pattern (Lines 430-490)

**Trigger:** Multiple skills detected AND pattern matches `and\s*\n\s*-\s+/`

**Pattern Detection:**
```python
mode3_pattern = r'and\s*\n\s*-\s+/'
if re.search(mode3_pattern, prompt):
    # Extract current skill (first reference)
    first_pos, first_skill, first_args_start = references[0]

    # Find where the "and" appears
    and_match = re.search(r'\s+and\s*\n', prompt[first_args_start:])
    if and_match:
        # Args for first skill are everything before "and"
        current_args = prompt[first_args_start:first_args_start + and_match.start()].strip()

        # Parse list items
        list_section = prompt[first_args_start + and_match.end():]
        continuation_entries = []

        for line in list_section.split('\n'):
            line = line.strip()
            if line.startswith('- /'):
                skill_match = re.match(r'-\s+/(\w+)(?:\s+(.*))?', line)
                if skill_match:
                    list_skill = skill_match.group(1)
                    list_args = skill_match.group(2) or ''
                    if list_skill in registry:
                        continuation_entries.append({
                            'skill': list_skill,
                            'args': list_args.strip()
                        })
```

**Behavior:**
- Looks for explicit `and\n- /skill` pattern
- Segments: `first_skill ... and\n- /skill1\n- /skill2`
- Current = first skill + args up to "and"
- Continuation = parsed list items (validated against registry)
- Appends default-exit of last skill in list

**Invocation Example:**
```
/design plans/foo and
- /plan-adhoc
- /orchestrate
```

#### Mode 2: Inline Prose (Lines 492-564)

**Trigger:** Multiple skills detected and Mode 3 pattern NOT matched

**Delimiter Detection:**
```python
delimiter_match = re.search(r'(,\s*/|(?:\s+(?:and|then|finally)\s+/))', segment)
```

**Logic:**
- Sorts all skill references by position
- First reference = current skill
- Subsequent references = continuation entries
- Between each pair: looks for `, /` or ` and/then/finally /` delimiters
- Extracts args from position to delimiter (or to next skill, or to end)

**Invocation Examples:**
```
/design plans/foo, /plan-adhoc and /orchestrate
/design plans/foo, /plan-adhoc then /orchestrate finally /commit
```

---

### 3. Registry Builder (Lines 261-361)

**Function:** `build_registry()` — discovers cooperative skills and caches result

**Discovery Sources:**

| Source | Scan Path | Discovery Mechanism |
|--------|-----------|-------------------|
| Project-local | `$CLAUDE_PROJECT_DIR/.claude/skills/**/SKILL.md` | Direct glob + frontmatter parse |
| Enabled plugins | `~/.claude/plugins/installed_plugins.json` + `enabledPlugins` setting | Plugin scope filtering + install paths |
| Built-in | Hardcoded `BUILTIN_SKILLS` dict | Fallback (currently empty) |

**Frontmatter Extraction (Lines 78-104):**

```python
def extract_frontmatter(skill_path: Path) -> Optional[Dict[str, Any]]:
    """Extract YAML frontmatter from a SKILL.md file."""
    if not yaml:
        return None

    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for YAML frontmatter (--- at start)
        if not content.startswith('---\n'):
            return None

        # Find closing ---
        end_match = re.search(r'\n---\n', content[4:])
        if not end_match:
            return None

        frontmatter_text = content[4:4 + end_match.start()]
        return yaml.safe_load(frontmatter_text)
    except Exception:
        # Skip malformed files
        return None
```

**Registry Structure:**

```python
{
    "design": {
        "cooperative": True,
        "default-exit": ["/handoff --commit", "/commit"]
    },
    "plan-adhoc": {
        "cooperative": True,
        "default-exit": ["/handoff --commit", "/commit"]
    },
    "commit": {
        "cooperative": True,
        "default-exit": []
    }
}
```

**Plugin Discovery (Lines 125-156):**

```python
def get_plugin_install_path(plugin_name: str, project_dir: str) -> Optional[str]:
    """Resolve plugin install path from installed_plugins.json.

    Respects scope filtering:
    - scope: "user" → plugin available globally
    - scope: "project" → only if projectPath matches current project
    """
    installed_path = Path.home() / '.claude' / 'plugins' / 'installed_plugins.json'
    # ...check project scope...
    return plugin_info.get('installPath')
```

**Caching Strategy (Lines 175-259):**

```python
# Cache key: SHA256 hash of all skill file paths + project directory
hash_input = ''.join(sorted_paths) + project_dir
hash_digest = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()[:16]

# Cache path: $TMPDIR/continuation-registry-<hash>.json
cache_path = Path(os.environ.get('TMPDIR', '/tmp/claude')) / f'continuation-registry-{hash_digest}.json'

# Invalidation: Check mtime of each source file
for path_str in cache_data['paths']:
    if path.stat().st_mtime > cache_timestamp:
        return None  # Cache invalid
```

---

### 4. Tier 3 Integration (Hook Entry Point)

**Function:** `main()` (Lines 628-688)

**Execution Order:**

```python
# Tier 1: Exact match for commands (s, x, xc, r, h, hc, ci, ?)
if prompt in COMMANDS:
    # Expand shortcut, output JSON to stdout
    return

# Tier 2: Directive pattern (d: text, p: text)
match = re.match(r'^(\w+):\s+(.+)', prompt)
if match and directive_key in DIRECTIVES:
    # Expand directive, output JSON to stdout
    return

# Tier 3: Continuation parsing
try:
    registry = build_registry()
    parsed = parse_continuation(prompt, registry)

    if parsed:
        # Format and inject continuation
        context = format_continuation_context(parsed)
        output = {
            'hookSpecificOutput': {
                'hookEventName': 'UserPromptSubmit',
                'additionalContext': context
            }
        }
        print(json.dumps(output))
        return
except Exception:
    # If continuation parsing fails, pass through silently
    pass

# No match: silent pass-through
sys.exit(0)
```

**Output Format (Lines 567-625):**

Function `format_continuation_context()` produces:

```
[CONTINUATION-PASSING]
Current: /<skill> <args>
Continuation: /<skill1> <args1>, /<skill2> <args2>

After completing the current skill, invoke the NEXT continuation entry via Skill tool:
  Skill(skill: "<skill1>", args: "<args1> [CONTINUATION: /<skill2>, ...]")

Do NOT include continuation metadata in Task tool prompts.
```

**Integration Points:**
- Hook fires on every UserPromptSubmit event (CLAUDE.md constraint: no matcher, all prompts processed)
- Tiers 1-2 have high precision (exact match, simple directives)
- Tier 3 added without removing Tiers 1-2 (cumulative, first match wins)
- Output: JSON to stdout (CloudCode hook protocol)

---

### 5. Existing Context-Awareness Mechanisms (NONE)

**Current Implementation Constraints:**

1. **No prose context detection:**
   - Parser doesn't check if `/skill` is preceded by words like "use", "invoke", "directive", "Remember"
   - No distinction between invocation and mention

2. **No file path filtering:**
   - Parser doesn't exclude `/` patterns within file paths (e.g., `plans/`, `.md` files)
   - Regex `/\w+` matches `handoff` in `/orchestrate-handoff-redesign/design.md`

3. **No output/XML detection:**
   - Parser doesn't identify command output markers like `<bash-stdout>`, `<command-name>`, `<local-command-stdout>`
   - Treats skill references in structured output as valid invocations

4. **No location-based filtering:**
   - Parser applies same detection logic regardless of where `/skill` appears
   - No heuristic: "If at start of line → invocation; if in middle of sentence → context-dependent"

5. **No negative lookahead:**
   - Parser doesn't check character immediately before `/`
   - "designs/commit-workflow" would match `commit` (but only if `commit` in registry + `/commit` pattern found)
   - Actually doesn't match because regex requires `/commit` with word boundary, not `/commit-workflow`

---

## False Positive Analysis

**Source:** `plans/continuation-passing/reports/step-3-5-empirical-validation.md`

### Detection Rate
- Sample: 200 real user prompts from session corpus
- Detections: 30 (15% of prompts)
- True positives: 1 (3.3%)
- **False positives: 26 (86.7%)**

### False Positive Categories

**1. Meta-Discussion (8 cases, 31%)**
- "Remember to use the /commit skill"
- "update CLAUDE.md: directive to use /commit skill"
- "Execute step from: plans/.../step-X.md"
- Context: User is discussing skills, not invoking them

**2. File Paths (11 cases, 42%)**
- "Review the memory index update implementation" (file mentions `/commit` in content)
- "plans/orchestrate-workflow/design.md"
- Prompts referencing files containing skill names

**3. Command Output (7 cases, 27%)**
- `<command-message>commit</command-message>`
- `<bash-stdout>` containing skill names
- `<local-command-stdout>` with context markers

### Impact on FR-5

**Requirement:** Prose-to-explicit translation must be accurate (0% false positives expected)

**Violation:** When parser detects `/commit` in "Remember to use /commit skill":
- Parser returns: `{current: {skill: 'commit', args: 'skill'}, continuation: []}`
- Injected into additionalContext: `"Current: /commit skill"`
- Claude sees: invoke `/commit` with arg "skill"
- User intended: reference to `/commit` skill in prose (no invocation)
- Result: Wrong continuation appended, potential execution drift

---

## Consumption Protocol Integration

**File:** `/Users/david/code/claudeutils-continuation-passing/tests/test_continuation_consumption.py`

**Cooperative Skill Protocol (Design Component 3):**

```python
# Step 1: Skill reads continuation from additionalContext or args
def peel_continuation(args_with_continuation: str) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    """Peel first entry, return (target_entry, remainder_str)."""
    entries = parse_continuation_string(args_with_continuation)
    if not entries or len(entries) == 0:
        return (None, None)

    target = entries[0]

    # Step 2: If continuation is empty, terminal
    if len(entries) > 1:
        # Step 3: Consume first entry
        remainder_entries = entries[1:]
        # Step 4: Pass remainder to next skill
        remainder_str = f"[CONTINUATION: {', '.join(remainder_parts)}]"
        return (target, remainder_str)
    else:
        return (target, None)  # Terminal
```

**Format:** `[CONTINUATION: /skill1 arg1, /skill2 arg2]`

**Consumption Protocol Sequence:**

1. First skill receives `[CONTINUATION: ...]` in `additionalContext`
2. Parses with `parse_continuation_string()` (validates bracket format, comma-separated entries)
3. Calls `peel_continuation()` to extract first entry + remainder
4. Invokes next skill via `Skill(skill="<name>", args="<args> <remainder>")`
5. Next skill repeats steps 2-4 until remainder is None (terminal)

**No Context-Awareness in Consumption:**
- Consumption assumes parser already filtered for valid invocations
- Cooperative skill protocol just peels + forwards
- If parser misidentifies (false positive), consumption propagates the error

---

## Parser Requirements vs. Current Implementation

| Requirement | Current Implementation | Gap |
|-------------|----------------------|-----|
| **FR-5 (Prose-to-explicit)** | Regex `/\w+` + registry lookup | No prose context filtering |
| **D-7 (Empirical validation)** | Unit tests only (synthetic inputs) | Validation against real corpus revealed 86.7% FP rate |
| **Context awareness** | None — all `/skill` patterns treated equally | No distinction between invocation and mention |
| **File path filtering** | None | Matches `/skill` inside file names/paths |
| **Output detection** | None | Matches `/skill` in XML/structured output |
| **Location heuristics** | None | No prompt-start vs. mid-sentence analysis |
| **Negative test cases** | Step 3.2 tests cover happy path only | Missing negative cases for false positive categories |

---

## Test Coverage Gaps

**Unit Tests:** 30 tests in `tests/test_continuation_consumption.py` (consumption protocol only, 100% pass rate)

**Parser Tests:** None found in test suite

**Negative Test Cases:** NONE

**Missing Coverage:**
```python
# Should return None (no continuation detected):
assert parse_continuation("Remember to use /commit skill", registry) is None
assert parse_continuation("Execute step from: plans/.../step.md", registry) is None
assert parse_continuation("<command-message>/commit</command-message>", registry) is None
assert parse_continuation("Review /path/to/commit.md", registry) is None

# Should detect (explicit invocation):
assert parse_continuation("/design plans/foo", registry) is not None
assert parse_continuation("/design, /plan-adhoc", registry) is not None
```

---

## Caching Effectiveness

**Cache Path:** `$TMPDIR/continuation-registry-<hash>.json`

**Hash Key:** SHA256 of sorted skill file paths + project directory (first 16 chars)

**Validation Logic:**
- Check if cache file exists
- Validate structure (`paths`, `registry`, `timestamp` keys)
- Verify each source file exists and mtime < cache timestamp
- Return None if any source deleted or modified

**Overhead:**
- First call: ~50ms (glob scan + frontmatter parsing)
- Cached call: ~5ms (cache file I/O)
- Cache file size: ~1KB per 10-15 cooperative skills

**Limitation:** Cache lives in `$TMPDIR`, not persistent across sessions. Rebuilds on every session start.

---

## Registry Builder Robustness

**Graceful Degradation:**
- Missing YAML parser: Returns None, skips file (line 84-85)
- Malformed frontmatter: Exception caught, skips file (line 102)
- Missing `continuation` key: Checked with `.get('continuation', {})` (line 321)
- Empty `default-exit`: Returns `[]` (terminal skill) (line 333)
- Plugin path resolution fails: Continues with other sources (line 296-304)

**Plugin Discovery Edge Cases:**
- Plugin not in `installed_plugins.json`: `get_plugin_install_path()` returns None
- Project-scoped plugin with mismatched `projectPath`: filtered out (line 151)
- `enabledPlugins` missing from settings: returns `[]` (line 120)

---

## Summary Table: Implementation vs. Design

| Component | Design | Implementation | Status |
|-----------|--------|----------------|--------|
| **Detection pattern** | Registry-based skill matching | `/\w+` regex + registry lookup | ✅ Implemented |
| **Three parsing modes** | Mode 1 (single), Mode 2 (inline), Mode 3 (list) | All three modes present (lines 402-564) | ✅ Implemented |
| **Registry discovery** | Project + plugins + built-in | All three sources implemented | ✅ Implemented |
| **Frontmatter scanning** | Extract `continuation.cooperative` + `default-exit` | YAML parsing + key extraction | ✅ Implemented |
| **Caching** | Mtime-based invalidation, hash key | Cache with mtime checks | ✅ Implemented |
| **Tier 3 integration** | Tiers 1/2 unchanged, Tier 3 added after | Order preserved, no Tier 1/2 changes | ✅ Implemented |
| **Context-awareness** | Limited scope (FR-5 validated empirically) | None — no context filtering | ❌ MISSING |
| **Empirical validation** | Required before shipping (target: 0% FP, <5% FN) | Unit tests only; real validation revealed 86.7% FP | ❌ FAILED |
| **Negative test cases** | Not specified in design | None present | ❌ MISSING |

---

## Actionable Findings

### Critical Issues

1. **Parser context-awareness is zero** — Detection logic has no understanding of whether `/skill` is an invocation or a mention/path/output
2. **Empirical validation failed** — 86.7% false positive rate violates FR-5 requirement
3. **No negative test cases** — Unit tests don't cover false positive scenarios
4. **No prose filtering** — Meta-discussion about skills triggers false positives

### Design Gaps for Fix

**Required context checks (before declaring skill match valid):**

1. **Prose mention heuristic:**
   - Pattern: `(use|invoke|Remember|directive to|call) /skill`
   - Skip detection when match found

2. **File path filtering:**
   - Pattern: `/` or `\.md` in prompt before skill reference
   - Skip detection for that reference

3. **XML/output markers:**
   - Pattern: `<command-`, `<bash-`, `<local-command-`
   - Skip detection for enclosed `/skill` references

4. **Location heuristic:**
   - Prompt starts with `/skill` → TRUE invocation (high confidence)
   - `/skill` in middle of sentence without delimiter → FALSE unless preceded by `, /` or connecting word

5. **Negative lookahead:**
   - Check character before `/`: if alphanumeric or `_`, not a skill reference (e.g., `plans/commit-workflow`)

---

## Recommendations

### For Parser Redesign

1. **Enhance `find_skill_references()`** with context checks
2. **Add negative test cases** to catch false positives before implementation
3. **Increase empirical validation sample size** (target: 500-1000 prompts)
4. **Conservative mode:** When in doubt (ambiguous context), skip detection → prefer FN over FP

### For Current Implementation

1. **Document false positive categories** in code comments
2. **Add TODO markers** for future context-awareness enhancements
3. **Disable Tier 3 temporarily** until design fixes implemented (fallback to Tier 1/2 only)
4. **Create issue tracker entry** for parser redesign with empirical validation RCA

