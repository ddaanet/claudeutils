---
name: hook-batch-phase-2
model: sonnet
---

# Phase 2: PreToolUse Recipe-Redirect Hook

**Type:** TDD
**Target:** `agent-core/hooks/pretooluse-recipe-redirect.py` (new file)
**Test file:** `tests/test_pretooluse_recipe_redirect.py` (new file)
**Design ref:** `plans/hook-batch/outline.md` (Phase 2)

**Prerequisites:**
- Read `agent-core/hooks/userpromptsubmit-shortcuts.py` main() — understand hook output JSON structure: `{hookSpecificOutput: {hookEventName, additionalContext}, systemMessage}`. PreToolUse hook uses `hookEventName: "PreToolUse"` and additionalContext only (no systemMessage per D-6).
- Read `tests/test_userpromptsubmit_shortcuts.py` lines 1-35 — understand `call_hook()` helper pattern (importlib.util loading, stdin mock, stdout capture). Replicate this pattern for the new test file.
- Verify `agent-core/hooks/pretooluse-recipe-redirect.py` does NOT exist yet — this is a new file.

**Key decisions:**
- D-1: Command hook (not prompt) — deterministic, fast, no LLM cost
- D-2: Python (complex pattern matching)
- D-6: Informative only — exit 0, additionalContext injection, no blocking, no systemMessage
- Hook receives PreToolUse event with `tool_name: "Bash"` and `tool_input.command`
- Three redirect patterns: `ln` → `just sync-to-parent`, `git worktree` → `claudeutils _worktree`, `git merge` → `claudeutils _worktree merge`
- NOT patterns: `python3` and `python` commands are denied in settings.json but have no project recipe equivalent — do NOT add redirect for these

---

## Cycle 2.1: Script Structure and Silent Pass-Through

**Objective:** Create script skeleton that reads stdin JSON, extracts `tool_input.command`, exits 0 silently for unmatched commands.

---

**RED Phase:**

**Test:** `test_script_loads`
**File:** `tests/test_pretooluse_recipe_redirect.py` — create new file with HOOK_PATH definition and `call_hook()` helper

**HOOK_PATH setup:**
```
HOOK_PATH = Path(__file__).parent.parent / "agent-core" / "hooks" / "pretooluse-recipe-redirect.py"
```

Load with importlib.util (same pattern as test_userpromptsubmit_shortcuts.py). Test that `HOOK_PATH.exists()` is True and module loads without error.

**Assertions for test_script_loads:**
- `HOOK_PATH.exists()` is `True`
- Module loads without ImportError

**Test:** `test_unknown_command_silent_passthrough`

**Assertions:**
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "echo hello"}})` returns `{}` (empty dict — exit 0, no output)
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "pytest tests/"}})` returns `{}`
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "just test"}})` returns `{}`

**Test:** `test_missing_command_field_passthrough`

**Assertions:**
- `call_hook({"tool_name": "Bash", "tool_input": {}})` returns `{}` (no `command` key — graceful default, no crash)
- `call_hook({"tool_name": "Bash"})` returns `{}` (no `tool_input` key — graceful default)

**Test:** `test_output_format_when_match_exists`
(placeholder test to verify output format — will pass after Cycle 2.2 adds pattern logic, but structure is verified here)

**Assertions:**
- When a redirect fires (e.g., `"ln -sf ..."` command), result dict has key `"hookSpecificOutput"`
- `result["hookSpecificOutput"]["hookEventName"]` equals `"PreToolUse"`
- `result["hookSpecificOutput"]` has key `"additionalContext"` with a non-empty string
- Result does NOT have a `"systemMessage"` key (D-6: additionalContext only)

Note: `test_output_format_when_match_exists` will remain failing (RED) until Cycle 2.2 adds the redirect.

**call_hook() helper signature:**
```python
def call_hook(hook_input: dict) -> dict:
    # serialize hook_input to JSON → stdin
    # capture stdout → parse JSON or return {} on empty/exit-0
```

**Expected failure:**
- `test_script_loads`: `AssertionError` — `HOOK_PATH.exists()` is False (file doesn't exist yet)
- `test_unknown_command_silent_passthrough`: `ModuleNotFoundError` or `RuntimeError` loading missing file

**Why it fails:** `agent-core/hooks/pretooluse-recipe-redirect.py` does not exist.

**Verify RED:** `pytest tests/test_pretooluse_recipe_redirect.py::test_script_loads -v`

---

**GREEN Phase:**

**Implementation:** Create `agent-core/hooks/pretooluse-recipe-redirect.py` with stdin parsing and pass-through.

**Behavior:**
- Shebang: `#!/usr/bin/env python3`
- Read stdin as JSON — `json.load(sys.stdin)`
- Extract `tool_input.command` — `hook_input.get('tool_input', {}).get('command', '')`
- If no redirect matches: `sys.exit(0)` with no output (silent pass-through)
- `main()` function callable from tests; `if __name__ == '__main__': main()`

**Approach:** Minimal script — import json, sys; main() reads and exits. Redirect logic added in Cycle 2.2.

**Output format (for Cycle 2.2 reference):**
```python
output = {
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'additionalContext': '<redirect message>'
    }
    # NO 'systemMessage' key (D-6: informative only)
}
print(json.dumps(output))
```

**Changes:**
- File: `agent-core/hooks/pretooluse-recipe-redirect.py`
  Action: Create new file with main() function
  Location hint: new file in `agent-core/hooks/`
- File: `tests/test_pretooluse_recipe_redirect.py`
  Action: Create new test file with HOOK_PATH, call_hook() helper, and test classes

**Verify GREEN:** `pytest tests/test_pretooluse_recipe_redirect.py -v -k "not test_output_format_when_match_exists"`
(Note: `test_output_format_when_match_exists` stays failing until Cycle 2.2 — this is expected)
**Verify no regression:** `pytest tests/test_userpromptsubmit_shortcuts.py -v`

---

## Cycle 2.2: All Redirect Patterns (ln + git worktree + git merge)

**Objective:** Add all three redirect patterns in one parametrized cycle. Each match injects additionalContext explaining why the command is blocked and what to use instead.

---

**RED Phase:**

**Prerequisite:** Read `agent-core/hooks/pretooluse-recipe-redirect.py` — understand current pass-through structure. Note command extraction uses `tool_input.command`.

**Test:** `test_ln_command_redirect`
**File:** `tests/test_pretooluse_recipe_redirect.py` — add to new class `TestRedirectPatterns`

**Assertions:**
- `result = call_hook({"tool_name": "Bash", "tool_input": {"command": "ln -sf agent-core/skills .claude/skills"}})` → non-empty
- `result["hookSpecificOutput"]["additionalContext"]` contains `"just sync-to-parent"`
- `result["hookSpecificOutput"]["hookEventName"]` equals `"PreToolUse"`
- `result` does NOT have `"systemMessage"` key

**Test:** `test_ln_bare_command_redirect`

**Assertions:**
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "ln"}})["hookSpecificOutput"]["additionalContext"]` contains `"just sync-to-parent"`
  (bare `ln` with no args still redirects)

**Test:** `test_git_worktree_redirect`

**Assertions:**
- `result = call_hook({"tool_name": "Bash", "tool_input": {"command": "git worktree add --detach ../my-task HEAD"}})` → non-empty
- `result["hookSpecificOutput"]["additionalContext"]` contains `"claudeutils _worktree"`
- `result["hookSpecificOutput"]["additionalContext"]` does NOT contain `"claudeutils _worktree merge"` (generic worktree, not merge-specific)

**Test:** `test_git_merge_redirect`

**Assertions:**
- `result = call_hook({"tool_name": "Bash", "tool_input": {"command": "git merge main"}})` → non-empty
- `result["hookSpecificOutput"]["additionalContext"]` contains `"claudeutils _worktree merge"`

**Test:** `test_passthrough_non_redirect_commands`

**Assertions (all return `{}`):**
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "git status"}})` → `{}`
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "git log --oneline"}})` → `{}`
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "pytest tests/"}})` → `{}`
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "just test"}})` → `{}`
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "python3 script.py"}})` → `{}` (python3 denied in settings.json but has no recipe redirect)

**Test:** `test_output_format_when_match_exists`
(This was failing RED from Cycle 2.1 — it now passes)

**Assertions (verify from Cycle 2.1):**
- `result = call_hook({"tool_name": "Bash", "tool_input": {"command": "ln -sf x y"}})`
- `"hookSpecificOutput"` in result, `result["hookSpecificOutput"]["hookEventName"] == "PreToolUse"`
- `"additionalContext"` in result["hookSpecificOutput"]
- `"systemMessage"` not in result

**Expected failure:** `AssertionError` — `call_hook({"tool_name": "Bash", "tool_input": {"command": "ln -sf ..."}})` currently returns `{}` (script has no redirect logic, just pass-through)

**Why it fails:** No pattern-matching logic in `pretooluse-recipe-redirect.py` yet.

**Verify RED:** `pytest tests/test_pretooluse_recipe_redirect.py::TestRedirectPatterns -v`

---

**GREEN Phase:**

**Implementation:** Add three redirect pattern checks to `pretooluse-recipe-redirect.py` main().

**Behavior:**
- Check order matters — check `git merge` BEFORE generic `git` patterns; check `git worktree` before other git subcommands
- `ln` match: `command.startswith('ln ') or command == 'ln'`
- `git worktree` match: `command.startswith('git worktree')`
- `git merge` match: `command.startswith('git merge')`
- On match: build output dict with hookEventName "PreToolUse" and additionalContext; print JSON; return (don't sys.exit)
- No systemMessage (D-6)

**Redirect messages:**
- `ln`: "`ln` is blocked. Use `just sync-to-parent` instead — it encodes correct symlink targets, ordering, and cleanup of stale links."
- `git worktree`: "Use `claudeutils _worktree` instead of `git worktree`. It handles session.md updates, submodule registration, focused sessions, and branch management."
- `git merge`: "Use `claudeutils _worktree merge` instead of `git merge`. It handles session.md conflict resolution, submodule lifecycle, and merge invariants."

**Approach:** Three `if/elif` checks at top of main() body, after command extraction. Each branch builds output and returns.

**Changes:**
- File: `agent-core/hooks/pretooluse-recipe-redirect.py`
  Action: Add redirect pattern checks in main() after command extraction
  Location hint: before the final `sys.exit(0)` pass-through

**Verify GREEN:** `pytest tests/test_pretooluse_recipe_redirect.py -v`
**Verify no regression:** `pytest tests/test_userpromptsubmit_shortcuts.py tests/test_pretooluse_recipe_redirect.py -v`

---

## Phase 2 Completion Validation

After both cycles pass:

```bash
pytest tests/test_pretooluse_recipe_redirect.py tests/test_userpromptsubmit_shortcuts.py -v
```

**Success criteria:**
- All new tests pass: script loads, pass-through works, all 3 redirects fire correctly
- `test_passthrough_non_redirect_commands` passes — no false positives
- `test_output_format_when_match_exists` passes (format validation)
- All Phase 1 tests (`test_userpromptsubmit_shortcuts.py`) still pass

**Stop conditions:**
- RED fails to fail → STOP: verify `pretooluse-recipe-redirect.py` doesn't exist yet (Cycle 2.1) or has no redirect logic yet (Cycle 2.2)
- GREEN passes without implementation → STOP: test too weak
- `git merge` redirect also fires on `git merge-base` → fix: use `command.startswith('git merge ')` or `command == 'git merge'` to avoid false positive on `git merge-base`
- Implementation needs architectural decision → STOP, escalate
