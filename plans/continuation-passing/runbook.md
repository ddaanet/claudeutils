# Continuation Passing Implementation Runbook

**Context**: Implement continuation passing system for skill chaining via hook parser, cooperative skill protocol, and frontmatter declarations.

**Source**: plans/continuation-passing/design.md
**Design**: plans/continuation-passing/design.md (D-1 through D-7)

**Status**: Ready for execution
**Created**: 2026-02-09

---

## Weak Orchestrator Metadata

**Total Steps**: 14 steps (4 hook + 6 skills + 4 test/doc)

**Execution Model**:
- Steps 1.1-1.4: Sonnet (hook implementation — registry builder, parser logic, integration)
- Steps 2.1-2.6: Sonnet (skill modifications — interpreting design intent for protocol text, not mechanical edits)
- Steps 3.1-3.3: Haiku (unit test implementation — standard pytest patterns)
- Steps 3.4: Sonnet (integration test — hook → skill → tail-call → skill logic)
- Steps 3.5: Sonnet (empirical validation — corpus extraction and analysis)
- Steps 3.6-3.8: Haiku (documentation updates — fragment creation, decision file updates)

**Step Dependencies**:
- Phase 1: Sequential (1.1 → 1.2 → 1.3, then 1.4 parallel with testing)
- Phase 2: All steps independent (different files)
- Phase 3: Steps 3.1-3.3 parallel, 3.4-3.5 depend on 3.1-3.3, 3.6-3.8 independent

**Parallelization Opportunities:**
- Phase 2: All 6 skill modifications can run in parallel
- Phase 3: Unit tests (3.1-3.3) can run in parallel
- Phase 3: Documentation (3.6-3.8) can run in parallel with tests

**Error Escalation**:
- Haiku → Sonnet: Test failures requiring semantic analysis, corpus analysis failures
- Sonnet → User: Design gaps discovered during implementation, empirical validation metrics fail targets

**Report Locations**: `plans/continuation-passing/reports/step-*-execution.md`

**Success Criteria**:
- Hook outputs correct `additionalContext` for all 3 parsing modes
- All 6 skills have frontmatter and protocol sections
- All tests pass (parser, registry, consumption, integration)
- Empirical validation: 0% false positives, <5% false negatives
- Documentation complete and committed

**Prerequisites**:
- Phase 1 depends on existing hook structure (userpromptsubmit-shortcuts.py) — ✓ verified
- Phase 2 depends on skill file locations (agent-core/skills/*/SKILL.md) — ✓ verified
- Phase 3 depends on test infrastructure (tests/ directory, pytest) — ✓ verified

---

## Common Context

**Requirements (from design):**
- FR-1: Prose continuation syntax — hook parser with delimiter detection + registry lookup
- FR-2: Sequential execution — peel-first-pass-remainder protocol
- FR-3: Continuation consumption — cooperative skill protocol
- FR-4: Structured continuation (multi-line) — `and\n- /skill` list marker detection
- FR-5: Prose-to-explicit translation — registry matching + empirical validation
- FR-6: Sub-agent isolation — convention + explicit prohibition
- FR-7: Cooperative skill protocol — frontmatter declaration + consumption protocol
- FR-8: Uncooperative skill wrapping — out of scope (explicitly optional)
- NFR-1: Light cooperation — skills understand protocol, not specific downstream skills
- NFR-2: Context list for cooperation detection — frontmatter scanning + registry cache
- NFR-3: Ephemeral continuations — passed through execution, never persisted
- C-1: No sub-agent leakage — continuation stripped from Task tool prompts
- C-2: Explicit stop — empty continuation = terminal (no tail-call)

**Scope boundaries:**
- **In scope:** Hook parser, registry builder, skill frontmatter, consumption protocol, unit tests, integration test, empirical validation, documentation
- **Out of scope:** FR-8 (uncooperative skill wrapping), cross-session continuation (not in requirements), mid-chain error recovery (deferred to error handling framework design)

**Key Constraints:**
- Preserve existing hook Tier 1/2 behavior (exact-match commands, colon-prefix directives)
- Non-skill input passes through silently (exit 0, no output)
- Skills use exact protocol text from design (not interpreted variations)
- Continuation never persisted in session.md or learnings.md

**Project Paths:**
- Hook script: `agent-core/hooks/userpromptsubmit-shortcuts.py`
- Skills: `agent-core/skills/{design,plan-adhoc,plan-tdd,orchestrate,handoff,commit}/SKILL.md`
- Tests: `tests/test_continuation_*.py`
- Fragment: `agent-core/fragments/continuation-passing.md`
- Decisions: `agents/decisions/workflow-optimization.md`

**Conventions:**
- Frontmatter: YAML syntax, `continuation:` block with `cooperative` and `default-exit` fields
- Transport format: `[CONTINUATION: /skill1 args1, /skill2 args2]` in Skill args suffix
- Registry caching: SHA256 hash of sorted paths + project directory, mtime-based invalidation
- Test module naming: `test_continuation_parser.py`, `test_continuation_registry.py`, `test_continuation_consumption.py`, `test_continuation_integration.py`, `test_continuation_empirical.py`

---

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
# Phase 2: Skill Modifications

**Objective:** Add frontmatter declarations and consumption protocol to 6 skills

**Context:** All cooperative skills need:
1. Frontmatter `continuation:` block with `cooperative: true` and `default-exit` list
2. Consumption protocol section (~5-8 lines) replacing hardcoded tail-calls
3. `Skill` tool added to `allowed-tools` if not present

## Common Phase Context

**Design references:**
- D-2: Explicit passing via Skill args (`[CONTINUATION: ...]` suffix format)
- D-3: Default exit appending (hook appends terminal skill's default exit)
- D-5: Sub-agent isolation (prohibition in protocol)

**Consumption protocol template** (use verbatim from design):
```markdown
## Continuation

As the **final action** of this skill:

1. Read continuation from `additionalContext` (first skill in chain) or from `[CONTINUATION: ...]` suffix in Skill args (chained skills)
2. If continuation is empty: stop (terminal)
3. Consume first entry as tail-call target
4. Invoke via Skill tool: `Skill(skill: "<target>", args: "<target-args> [CONTINUATION: <remainder>]")`

**CRITICAL:** Do NOT include continuation metadata in Task tool prompts. Continuation is for main-agent skill chaining only.
```

---

## Steps 2.1-2.3: Workflow Planning Skills (Template Pattern)

**Skills:** `/design`, `/plan-adhoc`, `/plan-tdd`

**Execution Model:** Sonnet (interpreting design intent for protocol text)

**Pattern:**
For each skill, apply these modifications:

### 1. Add frontmatter `continuation:` block

```yaml
continuation:
  cooperative: true
  default-exit: ["/handoff --commit", "/commit"]
```

### 2. Add `Skill` to `allowed-tools` (if not present)

**Note:** Only `/design` needs this addition. `/plan-adhoc` and `/plan-tdd` already have `Skill` in their allowed-tools.

### 3. Remove hardcoded tail-call section

**Current locations per design Component 3:**
- `/design`: C.5 "Handoff and Commit" section (line ~219: "CRITICAL: As the final action, invoke `/handoff --commit`")
- `/plan-adhoc`: Step 3 "Tail-call `/handoff --commit`" section (line ~688)
- `/plan-tdd`: Step 6 "Tail-call `/handoff --commit`" section (similar location at end)

### 4. Add continuation protocol section

Insert the consumption protocol template (from Common Phase Context above) where the hardcoded tail-call was removed.

**Expected Outcome:**
Each skill has frontmatter declaration, protocol section, and hardcoded tail-call removed.

---

## Step 2.4: Update /orchestrate Skill

**Execution Model:** Sonnet

**File:** `agent-core/skills/orchestrate/SKILL.md`

**Implementation:**

### 1. Add frontmatter `continuation:` block

```yaml
continuation:
  cooperative: true
  default-exit: ["/handoff --commit", "/commit"]
```

### 2. Add `Skill` to `allowed-tools`

Current `allowed-tools: Task, Read, Bash, Grep, Glob`
Updated: `allowed-tools: Task, Read, Bash, Grep, Glob, Skill`

### 3. Add continuation protocol section

**Note:** Design states "/orchestrate has no hardcoded Skill tail-call to remove — suggests next actions in prose". Add continuation protocol alongside existing completion handling (Section 6 "Completion").

Insert protocol at end of skill, after completion section:

```markdown
## Continuation

As the **final action** of this skill:

1. Read continuation from `additionalContext` (first skill in chain) or from `[CONTINUATION: ...]` suffix in Skill args (chained skills)
2. If continuation is empty: stop (terminal)
3. Consume first entry as tail-call target
4. Invoke via Skill tool: `Skill(skill: "<target>", args: "<target-args> [CONTINUATION: <remainder>]")`

**CRITICAL:** Do NOT include continuation metadata in Task tool prompts. Continuation is for main-agent skill chaining only.
```

**Expected Outcome:**
/orchestrate skill has frontmatter, `Skill` tool, and continuation protocol added. Existing completion prose preserved.

---

## Step 2.5: Update /handoff Skill

**Execution Model:** Sonnet

**File:** `agent-core/skills/handoff/SKILL.md`

**Implementation:**

### 1. Add frontmatter `continuation:` block

```yaml
continuation:
  cooperative: true
  default-exit: ["/commit"]
```

**Note:** `/handoff` default exit is `["/commit"]` only when `--commit` flag present. Hook handles this conditional logic (design "Handoff --commit Special Case" line 249-252).

### 2. Replace hardcoded tail-call section

**Current location:** "Tail-Call: --commit Flag" section (line ~213: "If `--commit` flag was provided: As the **final action** of this skill, invoke `/commit` using the Skill tool.")

**Replacement:** Continuation protocol template (from Common Phase Context).

**Expected Outcome:**
/handoff skill has frontmatter and continuation protocol. Conditional default exit handled by hook, not skill logic.

---

## Step 2.6: Update /commit Skill

**Execution Model:** Sonnet

**File:** `agent-core/skills/commit/SKILL.md`

**Implementation:**

### 1. Add frontmatter `continuation:` block

```yaml
continuation:
  cooperative: true
  default-exit: []
```

**Note:** `/commit` is terminal — empty `default-exit` list.

### 2. No other changes needed

`/commit` already terminal (displays STATUS and stops). No hardcoded tail-call to remove, no protocol section needed (empty continuation = no tail-call).

**Expected Outcome:**
/commit skill has frontmatter with empty `default-exit`. No behavioral changes.

---

## Phase Checkpoint

After all 6 skills modified:

**Verify frontmatter:**
```bash
# Check each skill has continuation block
grep -A 3 "continuation:" agent-core/skills/{design,plan-adhoc,plan-tdd,orchestrate,handoff,commit}/SKILL.md
```

Expected: All 6 skills have `continuation:` block with correct `default-exit` values.

**Verify Skill tool:**
```bash
# Check /design and /orchestrate have Skill in allowed-tools
grep "allowed-tools:" agent-core/skills/{design,orchestrate}/SKILL.md
```

Expected: Both include `Skill` in allowed-tools list.

**Verify protocol sections:**
```bash
# Check continuation protocol section exists
grep -l "## Continuation" agent-core/skills/{design,plan-adhoc,plan-tdd,orchestrate,handoff}/SKILL.md
```

Expected: 5 files (all except /commit).

**Run precommit:**
```bash
just precommit
```

Expected: All checks pass (no YAML syntax errors).

If checks fail: STOP and report which skill/check failed.

If checks pass: Proceed to Phase 3.

# Phase 3: Testing, Validation, and Documentation

**Objective:** Unit tests + integration test + empirical validation + documentation

---

## Step 3.1: Unit Tests for Continuation Parser

**Execution Model:** Haiku

**File:** `tests/test_continuation_parser.py`

**Test scenarios** (from design Component 4):
1. Single skill with args → default exit appended
2. Inline prose (`, /` delimiter) → correct split
3. Multi-line list (`and\n- /skill`) → correct entries
4. Path args not treated as skills
5. Connecting words in prose not continuation
6. Flag handling (`/handoff --commit`)
7. Unknown skill ignored
8. Terminal skill (`/commit`) → empty continuation

**Report Path:** `plans/continuation-passing/reports/step-3-1-execution.md`

---

## Step 3.2: Unit Tests for Registry Builder

**Execution Model:** Haiku

**File:** `tests/test_continuation_registry.py`

**Test scenarios:**
1. Frontmatter scanning extracts `cooperative` and `default-exit`
2. Non-cooperative skills excluded (`cooperative: false` or missing)
3. Cache invalidation on mtime change

**Report Path:** `plans/continuation-passing/reports/step-3-2-execution.md`

---

## Step 3.3: Unit Tests for Consumption Protocol

**Execution Model:** Haiku

**File:** `tests/test_continuation_consumption.py`

**Test scenarios:**
1. Peel first entry from `[CONTINUATION: /a, /b, /c]` → target: `/a`, remainder: `/b, /c`
2. Last entry consumption → target: `/commit`, remainder: empty
3. Empty continuation → terminal (no tail-call)

**Report Path:** `plans/continuation-passing/reports/step-3-3-execution.md`

---

## Step 3.4: Integration Test (2-Skill Chain)

**Execution Model:** Sonnet

**File:** `tests/test_continuation_integration.py`

**Test flow:**
1. Hook parses `/design, /plan-adhoc` → emits `additionalContext`
2. First skill reads `additionalContext` → tail-calls `/plan-adhoc` with `[CONTINUATION: /handoff --commit, /commit]`
3. Second skill reads `args` suffix → tail-calls `/handoff --commit` with `[CONTINUATION: /commit]`
4. Verify chain completes correctly

**Report Path:** `plans/continuation-passing/reports/step-3-4-execution.md`

---

## Step 3.5: Empirical Validation Against Session Corpus

**Execution Model:** Sonnet

**Objective:** Validate parser accuracy against real user inputs (FR-5, D-7)

**Procedure:**
1. Extract unique user prompts containing `/` from `~/.claude/projects/*/` session transcripts
2. Run parser against each prompt
3. Manual review: classify as correct/false-positive/false-negative
4. Calculate metrics:
   - False positive rate (args misidentified as continuations)
   - False negative rate (explicit continuations missed)

**Target metrics:**
- False positives: 0% (critical — corrupts skill args)
- False negatives: <5% (acceptable — user retypes)

**Report Path:** `plans/continuation-passing/reports/step-3-5-empirical-validation.md`

---

## Step 3.6: Create Continuation Passing Fragment

**Execution Model:** Haiku

**File:** `agent-core/fragments/continuation-passing.md`

**Content:**
- Protocol overview (hook → skill → tail-call)
- Frontmatter schema for skill developers
- Consumption protocol template
- Transport format specification
- Sub-agent isolation requirement

**Report Path:** `plans/continuation-passing/reports/step-3-6-execution.md`

---

## Step 3.7: Update Workflow Optimization Decisions

**Execution Model:** Haiku

**File:** `agents/decisions/workflow-optimization.md`

**Add entries:**
- Continuation passing pattern (D-1 through D-7 summary)
- Default exit appending mechanism
- Hook-based parsing rationale

**Report Path:** `plans/continuation-passing/reports/step-3-7-execution.md`

---

## Step 3.8: Update Skill Development References

**Execution Model:** Haiku

**File:** Check if `plugin-dev:skill-development` skill needs frontmatter schema mention

**Action:** Add brief note about `continuation:` frontmatter block if cooperative skills are discussed.

**Report Path:** `plans/continuation-passing/reports/step-3-8-execution.md`

---

## Final Checkpoint

After Step 3.8 completes:

**Run full test suite:**
```bash
just test
```

Expected: All tests pass (parser, registry, consumption, integration).

**Verify empirical validation:**
- False positive rate: 0%
- False negative rate: <5%

**Verify documentation:**
- Fragment exists and is complete
- Decision files updated
- Skill development guide mentions frontmatter (if applicable)

**Run precommit:**
```bash
just precommit
```

Expected: All checks pass.

If checks fail: STOP and report which test/check failed.

If checks pass: Implementation complete. Ready for commit.

---

## Design Decisions

Referencing key decisions from design document:

- **D-1 (Hook as parsing layer):** UserPromptSubmit hook handles all parsing centrally for reliability
- **D-2 (Explicit passing via Skill args):** `[CONTINUATION: ...]` suffix in args parameter is transport
- **D-3 (Default exit appending):** Hook appends terminal skill's default exit automatically
- **D-4 (Ephemeral continuation lifecycle):** Never persisted, discarded on completion/error
- **D-5 (Sub-agent isolation):** Convention + prohibition in protocol (no continuation in Task prompts)
- **D-6 (Parsing strategy):** 3 modes with mode detection order (Mode 3 → Mode 2 → Mode 1)
- **D-7 (Prose-to-explicit translation):** Registry matching with empirical validation

---

## Dependencies

**Before This Runbook:**
- Existing hook infrastructure (userpromptsubmit-shortcuts.py) — verified
- Skill files with YAML frontmatter support — verified
- Test infrastructure (pytest) — verified

**After This Runbook:**
- Hook outputs continuation metadata for skill chains
- Skills consume continuations via Skill tool
- Backward compatible (solo invocations unchanged)
- Empirically validated against session corpus

---

## Notes

**Migration safety:** Frontmatter additions are inert without hook. Skills with protocol but no hook-injected continuation behave as before (no tail-call). Hook activation completes the system.

**Rollback:** Remove Tier 3 from hook → skills fall back to no continuation → protocol is no-op. Frontmatter remains but has no effect.

**Performance:** Registry caching ensures <5ms overhead per prompt (NFR-2 target).

