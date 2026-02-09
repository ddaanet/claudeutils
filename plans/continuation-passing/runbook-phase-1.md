# Phase 1: Hook Implementation

**Objective:** Build continuation parser and registry in userpromptsubmit-shortcuts.py

**Context:** Extend existing hook script that processes Tier 1 (commands) and Tier 2 (directives) shortcuts. Add Tier 3 continuation parsing that fires when input contains registered skill references.

## Common Phase Context

**Target file:** `agent-core/hooks/userpromptsubmit-shortcuts.py` (currently ~105 lines)

**Design references:**
- D-1: Hook as parsing layer (central parsing, fires before Claude processes input)
- D-6: Parsing strategy (3 modes: single skill, inline prose, multi-line list)
- D-7: Prose-to-explicit translation (registry matching for disambiguation)

**Key constraints:**
- Preserve existing Tier 1/2 behavior (exact-match commands, colon-prefix directives)
- Tier 3 fires only when Tiers 1/2 don't match AND input contains registered skills
- Non-skill input passes through silently (exit 0, no output)

---

## Step 1.1: Implement Cooperative Skill Registry Builder

**Objective:** Build registry of cooperative skills from 3 sources with frontmatter metadata extraction.

**Execution Model:** Sonnet

**Implementation:**

Create registry builder function that scans for cooperative skills:

**Three discovery sources:**

1. **Project-local skills:**
   - Glob: `$CLAUDE_PROJECT_DIR/.claude/skills/**/SKILL.md`
   - Direct frontmatter scan

2. **Enabled plugins:**
   - Read `~/.claude/settings.json` → `enabledPlugins` list
     ```json
     {
       "enabledPlugins": ["plugin-dev", "my-custom-plugin"]
     }
     ```
   - Read `~/.claude/plugins/installed_plugins.json` → resolve install paths
     ```json
     {
       "plugin-dev": {
         "installPath": "/Users/user/.claude/plugins/cache/claude-plugins-official/plugin-dev/abc123",
         "scope": "user"
       },
       "my-custom-plugin": {
         "installPath": "/path/to/custom/plugin",
         "scope": "project",
         "projectPath": "/Users/user/code/myproject"
       }
     }
     ```
   - Check plugin scope filtering:
     - `scope: "user"` → include for all projects
     - `scope: "project"` → include only if `projectPath` matches `$CLAUDE_PROJECT_DIR`
   - Glob each enabled plugin: `<installPath>/skills/**/SKILL.md`

3. **Built-in skills (fallback list):**
   ```python
   BUILTIN_SKILLS = {
       # Empty initially — all cooperative skills are project-local or plugin-based
       # Add entries here if built-in skills need continuation support
   }
   ```

**Frontmatter extraction:**

For each SKILL.md file found:
- Parse YAML frontmatter
- Check `continuation.cooperative: true`
- Extract `continuation.default-exit` list (array of skill references)
- Skip if `cooperative` is missing or false

**Registry structure:**
```python
{
    "design": {
        "cooperative": True,
        "default_exit": ["/handoff --commit", "/commit"]
    },
    "plan-adhoc": {
        "cooperative": True,
        "default_exit": ["/handoff --commit", "/commit"]
    },
    # ... etc
}
```

**Error handling:**
- Skip malformed YAML (log warning, continue)
- Skip skills without continuation block
- Handle missing files gracefully (plugin uninstalled but in settings)

**Expected Outcome:**

Function returns dictionary mapping skill names to metadata. Calling `build_registry()` discovers all cooperative skills and their default exits.

**Validation:**
- Verify project-local skills discovered (agent-core/skills/*/SKILL.md)
- Verify enabled plugins scanned correctly
- Verify non-cooperative skills excluded

**Success Criteria:**
- Registry contains all 6 cooperative skills from design:
  - `/design`, `/plan-adhoc`, `/plan-tdd`, `/orchestrate` → `default_exit: ["/handoff --commit", "/commit"]`
  - `/handoff` → `default_exit: ["/commit"]` (only when `--commit` flag present)
  - `/commit` → `default_exit: []` (terminal)
- Each entry has `cooperative: True` and `default_exit` list
- Non-cooperative skills excluded from registry

**Report Path:** `plans/continuation-passing/reports/step-1-1-execution.md`

---

## Step 1.2: Implement Continuation Parser (Modes 1-3)

**Objective:** Parse user input to detect skill references and build continuation chain.

**Execution Model:** Sonnet

**Implementation:**

Create parser function that handles three modes:

**Mode 1 — Single skill (no continuation):**
- Input contains exactly one `/skill` reference
- No other registered skills detected
- Append skill's default exit to continuation

**Example:**
```
Input: "/design plans/foo"
→ current: {skill: "design", args: "plans/foo"}
→ continuation: ["/handoff --commit", "/commit"]
```

**Mode detection order** (resolves ambiguity when patterns overlap):
1. Check Mode 3 pattern first: `and\n- /skill` (more specific)
2. Check Mode 2 pattern: inline `, /` or connecting words (more general)
3. First match wins

**Mode 2 — Inline prose (FR-1, FR-3):**
- Multiple `/skill` references on one line
- Delimiters: `, /` or connecting words (`and`, `then`, `finally`) before `/skill`
- Split into current + continuation

**Example:**
```
Input: "/design plans/foo, /plan-adhoc and /orchestrate"
→ current: {skill: "design", args: "plans/foo"}
→ continuation: [{skill: "plan-adhoc"}, {skill: "orchestrate"}]
```

**Mode 3 — Multi-line list (FR-4):**
- Pattern: `and\n- /skill args` (exact pattern: connecting word + newline + list marker)
- `and` keyword on first line signals continuation
- Subsequent `- /skill` lines are entries

**Example:**
```
Input: "/design plans/foo and
- /plan-adhoc design.md
- /orchestrate foo"
→ current: {skill: "design", args: "plans/foo"}
→ continuation: [{skill: "plan-adhoc", args: "design.md"}, {skill: "orchestrate", args: "foo"}]
```

**Disambiguation (D-7):**
- Scan input for `/word` patterns
- Match each against cooperative registry
- Only registered skills recognized as continuation entries
- Path arguments like `/plans/foo/bar` won't match (not in registry)
- Connecting words in args (e.g., "design and implement") ignored unless followed by registered skill

**Default exit appending (D-3):**
- Identify last skill in chain (user's chain or current skill if solo)
- Look up last skill's `default_exit` from registry
- Append default exit entries to continuation
- Special case: `/handoff` without `--commit` flag is terminal (no default exit)

**Examples:**
```
User: "/design plans/foo"
Last skill: design
Default exit: ["/handoff --commit", "/commit"]
Full chain: ["/handoff --commit", "/commit"]

User: "/design, /plan-adhoc"
Last skill: plan-adhoc
Default exit: ["/handoff --commit", "/commit"]
Full chain: ["/plan-adhoc", "/handoff --commit", "/commit"]

User: "/handoff"
Last skill: handoff (no --commit flag)
Default exit: [] (terminal)
Full chain: [] (terminal)

User: "/commit"
Last skill: commit
Default exit: [] (terminal)
Full chain: [] (terminal)
```

**Mid-chain /handoff without --commit flag:**
- If `/handoff` (no `--commit`) appears mid-chain, user-specified continuation is preserved
- Example: `/design, /handoff, /commit` → chain is `[/handoff, /commit]`
- Rationale: User explicitly specified `/commit`, so `/handoff` terminal default doesn't apply
- Only solo `/handoff` invocation uses empty default exit

**Function signature:**
```python
def parse_continuation(prompt: str, registry: dict) -> Optional[dict]:
    """Parse prompt for continuation.

    Returns:
        None if no skill detected (pass-through)
        {
            "current": {"skill": str, "args": str},
            "continuation": [{"skill": str, "args": str}, ...]
        }
    """
```

**Expected Outcome:**

Parser correctly identifies skill references, splits into current + continuation, and appends default exits.

**Unexpected Result Handling:**
- No registered skills found → return None (silent pass-through)
- Ambiguous parse → resolved by mode detection order (Mode 3 checked first)
- Malformed input → return None (pass-through)
- Empty continuation after default exit appending → return empty list (terminal)

**Validation:**
- Single skill: `/design plans/foo` → continuation = default exit only
- Inline prose: `/design, /plan-adhoc` → correct split
- Multi-line: `and\n- /skill` pattern → correct entries
- Path args: `/design /plans/foo/bar` → path not treated as skill
- Connecting words: "design and implement" → not a continuation
- Flag handling: `/handoff --commit` → parser detects flag, registry returns `["/commit"]` for handoff+flag
- Mid-chain handoff: `/design, /handoff, /commit` → user-specified `/commit` preserved
- Unknown skill: `/design, /nonexistent` → nonexistent ignored
- Terminal skill: `/commit` → empty continuation

**Success Criteria:**
- All 8 test scenarios from design Component 4 pass
- Registry disambiguation works (paths and prose ignored)
- Default exits appended correctly

**Report Path:** `plans/continuation-passing/reports/step-1-2-execution.md`

---

## Step 1.3: Integrate Tier 3 into Existing Hook

**Objective:** Wire continuation parser into userpromptsubmit-shortcuts.py as Tier 3.

**Execution Model:** Sonnet

**Implementation:**

**Tier processing order:**
1. **Tier 1:** Exact match shortcuts (`s`, `x`, `xc`, `r`, `h`, `hc`, `ci`, `?`) — unchanged
2. **Tier 2:** Directive shortcuts (`d:`, `p:`) — unchanged
3. **NEW — Tier 3:** Continuation parsing — if input contains registered skills

**Tier 3 logic:**

```python
# After Tier 1 and Tier 2 checks fail
registry = build_registry()  # Step 1.1 function
parsed = parse_continuation(prompt, registry)  # Step 1.2 function

if parsed is None:
    # No registered skills found
    sys.exit(0)  # Silent pass-through

# Build additionalContext JSON
continuation_entries = [
    f"/{entry['skill']}" + (f" {entry['args']}" if entry.get('args') else "")
    for entry in parsed['continuation']
]
continuation_str = ", ".join(continuation_entries)

current_skill = f"/{parsed['current']['skill']}"
current_args = parsed['current'].get('args', '')
if current_args:
    current_skill += f" {current_args}"

additional_context = f"""[CONTINUATION-PASSING]
Current: {current_skill}
Continuation: {continuation_str}

After completing the current skill, invoke the NEXT continuation entry via Skill tool:
  Skill(skill: "{parsed['continuation'][0]['skill']}", args: "{parsed['continuation'][0].get('args', '')} [CONTINUATION: {', '.join(continuation_entries[1:])}]")

Do NOT include continuation metadata in Task tool prompts."""

output = {
    'hookSpecificOutput': {
        'hookEventName': 'UserPromptSubmit',
        'additionalContext': additional_context
    }
    # No systemMessage — continuation is internal to Claude
}
print(json.dumps(output))
```

**Design reference:** D-2 specifies `additionalContext` format (prose with structured prefix, not raw JSON).

**Key integration points:**
- Tier 3 fires only when Tiers 1/2 don't match
- Requires registry from Step 1.1
- Requires parser from Step 1.2
- No output change for non-skill input (silent pass-through preserved)

**Expected Outcome:**

Hook emits `additionalContext` JSON when skill references detected. No output for non-skill input.

**Unexpected Result Handling:**
- Registry build fails → log warning, fall through to silent pass-through
- Parser raises exception → log error, fall through to silent pass-through
- Empty continuation after parsing → emit terminal format

**Terminal continuation format:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "[CONTINUATION-PASSING]\nCurrent: /commit\nContinuation: (empty)\n\nSkill is terminal. No tail-call needed."
  }
}
```

**Validation:**
- Tier 1 shortcuts still work (`s`, `x`, etc.)
- Tier 2 directives still work (`d:`, `p:`)
- Non-skill input passes through silently
- Skill input emits correct `additionalContext`
- Single-skill invocation includes default exit

**Success Criteria:**
- All existing hook behavior preserved
- Continuation metadata injected for skill inputs
- `additionalContext` format matches design specification (D-2)
- No `systemMessage` emitted (continuation is internal)

**Report Path:** `plans/continuation-passing/reports/step-1-3-execution.md`

---

## Step 1.4: Add Registry Caching (NFR-2)

**Objective:** Cache registry to temp file with mtime-based invalidation.

**Execution Model:** Sonnet

**Implementation:**

**Cache strategy:**
- Cache file: `$TMPDIR/continuation-registry-<hash>.json`
- Hash algorithm: SHA256 of concatenated sorted paths + project directory
  - Input: `sorted(skill_file_paths) + [CLAUDE_PROJECT_DIR]`
  - Output: first 16 chars of SHA256 hex digest
  - Example: `continuation-registry-a1b2c3d4e5f6g7h8.json`
- Invalidation: Any skill file mtime > cache mtime → rebuild

**Cache structure:**
```json
{
    "paths": [
        "/path/to/.claude/skills/design/SKILL.md",
        "/path/to/.claude/skills/plan-adhoc/SKILL.md",
        ...
    ],
    "registry": {
        "design": {"cooperative": true, "default_exit": [...]},
        ...
    },
    "timestamp": 1707350000
}
```

**Caching logic:**

```python
def get_cached_registry() -> Optional[dict]:
    """Load registry from cache if valid."""
    cache_path = get_cache_path()
    if not cache_path.exists():
        return None

    cache_data = json.loads(cache_path.read_text())

    # Check if any source file modified since cache
    for path in cache_data['paths']:
        if Path(path).stat().st_mtime > cache_data['timestamp']:
            return None  # Invalidated

    return cache_data['registry']

def save_registry_cache(registry: dict, paths: list) -> None:
    """Save registry to cache."""
    cache_path = get_cache_path()
    cache_data = {
        'paths': paths,
        'registry': registry,
        'timestamp': time.time()
    }
    cache_path.write_text(json.dumps(cache_data))
```

**Integration with Step 1.1:**

Modify `build_registry()` to check cache first:
```python
def build_registry() -> dict:
    cached = get_cached_registry()
    if cached is not None:
        return cached

    # Build from scratch (Step 1.1 logic)
    registry, paths = discover_and_parse()
    save_registry_cache(registry, paths)
    return registry
```

**Performance target:** <50ms first call, <5ms cached (NFR-2).

**Expected Outcome:**

Registry loads from cache on subsequent calls. Cache invalidates when skill files modified.

**Unexpected Result Handling:**
- Cache file corrupted → delete cache, rebuild
- Cache directory not writable → skip caching, build on every call (degraded mode)
- Hash collision (unlikely) → acceptable (just rebuilds unnecessarily)

**Validation:**
- First call builds registry and writes cache
- Second call loads from cache (<5ms)
- Modifying skill file invalidates cache
- Next call after invalidation rebuilds

**Success Criteria:**
- Cache file created at expected path
- Subsequent calls use cache (verify via timing or log)
- mtime-based invalidation works correctly
- Degraded mode works if caching unavailable

**Report Path:** `plans/continuation-passing/reports/step-1-4-execution.md`

---

## Phase Checkpoint

After Step 1.4 completes:

**Verify hook outputs:**
Run manual test of all 3 parsing modes:
```bash
# Mode 1: Single skill
printf '{"prompt": "/design plans/foo"}' | agent-core/hooks/userpromptsubmit-shortcuts.py

# Mode 2: Inline prose
printf '{"prompt": "/design plans/foo, /plan-adhoc and /orchestrate"}' | agent-core/hooks/userpromptsubmit-shortcuts.py

# Mode 3: Multi-line (use printf with literal newline)
printf '{"prompt": "/design plans/foo and\\n- /plan-adhoc\\n- /orchestrate"}' | agent-core/hooks/userpromptsubmit-shortcuts.py

# Terminal case
printf '{"prompt": "/commit"}' | agent-core/hooks/userpromptsubmit-shortcuts.py
```

Expected: All 3 emit correct `additionalContext` JSON with continuation metadata.

**Functional check:**
- Verify registry contains 6 cooperative skills
- Verify parser handles all edge cases from Step 1.2 validation
- Verify Tier 1/2 shortcuts still work

If checks fail: STOP and report which mode/scenario failed.

If checks pass: Proceed to Phase 2.
