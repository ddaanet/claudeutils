# Runbook: Skill-CLI Integration

**Tier:** 2 (Lightweight Delegation)
**Design:** `plans/skill-cli-integration/outline.md`
**Dependency order:** Phase 1 → Phase 2 → [RESTART] → Phase 3 + Phase 4 (parallel)

## Common Context

**Outline decisions:** D-1 (trigger convention `^Status\.$`), D-2 (commit composition boundary), D-3 (execute-rule simplification).

**Spike prototype:** `tmp/spike-stop-hook/status-hook.sh` — validated mechanism. Production changes: real CLI call, tightened regex, ANSI reset per line.

**Hook conventions:**
- Existing hooks in `agent-core/hooks/`
- Registration in `.claude/settings.json` under `hooks.Stop`
- Hook input: JSON on stdin with `last_assistant_message`, `stop_hook_active`
- Hook output: JSON with `systemMessage` (and optionally `additionalContext`)
- Existing Stop hook: `stop-health-fallback.sh` (runs on sessions without SessionStart)

**Test pattern for bash hooks:** pytest with subprocess — no existing hook tests in project. Test helper runs `bash <hook-path>` with JSON piped to stdin, parses JSON output. Hook uses `${STATUS_CMD:-claudeutils _status}` for testability.

---

### Phase 1: Hook core behavior (type: tdd)

**Artifact:** `agent-core/hooks/stop-status-display.sh`
**Test file:** `tests/test_stop_hook_status.py`
**Model:** sonnet

#### Cycle 1.1: Trigger detection + loop guard

**Bootstrap:** Create `agent-core/hooks/stop-status-display.sh` with stub (reads stdin, exits 0). Create `tests/test_stop_hook_status.py` with `run_hook()` helper that runs script via subprocess, pipes JSON stdin, returns parsed JSON output. Do not commit.

---

**RED Phase:**

**Test:** `test_trigger_positive_match`
**Assertions:**
- Input `{"last_assistant_message": "Status.", "stop_hook_active": false}` → output dict contains `"systemMessage"` key
- Input `{"last_assistant_message": "Check the Status.", "stop_hook_active": false}` → output is empty dict (substring, not full line)
- Input `{"last_assistant_message": "Status", "stop_hook_active": false}` → output is empty dict (no period)
- Input `{"last_assistant_message": "Status.\nMore text", "stop_hook_active": false}` → output is empty dict (not last line)

**Expected failure:** `AssertionError` — stub exits 0 with no output, positive case expects systemMessage key

**Verify RED:** `pytest tests/test_stop_hook_status.py::test_trigger_positive_match -v`

**Test:** `test_loop_guard`
**Assertions:**
- Input `{"last_assistant_message": "Status.", "stop_hook_active": true}` → output is empty dict (guard prevents action)

**Expected failure:** Same — stub produces no output regardless, but assertion structure must be present for GREEN verification

**Verify RED:** `pytest tests/test_stop_hook_status.py::test_loop_guard -v`

---

**GREEN Phase:**

**Implementation:** Trigger detection with full-line regex and loop guard

**Behavior:**
- Read JSON from stdin, extract `last_assistant_message` and `stop_hook_active`
- If `stop_hook_active` is true, exit 0 immediately
- Match `last_assistant_message` against `^Status\.$` (full line, period required)
- On match: output JSON with `systemMessage` containing placeholder text (real CLI in cycle 1.2)
- No match: exit 0

**Approach:** `jq` for JSON parsing (consistent with spike), `grep -qx 'Status\.'` or bash `[[ == ]]` for regex, `jq -n` for JSON output

**Changes:**
- File: `agent-core/hooks/stop-status-display.sh`
  Action: Replace stub with detection logic
  Location hint: Full file replacement

**Verify GREEN:** `just green`

---

#### Cycle 1.2: CLI integration + ANSI formatting

**Prerequisite:** Read `agent-core/hooks/stop-status-display.sh` — understand current trigger detection from cycle 1.1

---

**RED Phase:**

**Test:** `test_output_calls_status_command`
**Assertions:**
- With env `STATUS_CMD="echo 'mock status line'"` and trigger input → `systemMessage` contains `"mock status line"`
- Verifies hook delegates to configurable command

**Test:** `test_output_has_ansi_reset_per_line`
**Assertions:**
- With env `STATUS_CMD="printf 'line1\nline2\nline3'"` and trigger input → each non-empty line in `systemMessage` starts with `\033[0m`
- Empty lines may or may not have reset (implementation choice)

**Test:** `test_cli_failure_graceful`
**Assertions:**
- With env `STATUS_CMD="false"` (exit 1) and trigger input → `systemMessage` contains fallback text (not empty, not crash)

**Expected failure:** `AssertionError` — cycle 1.1 uses placeholder text, not CLI command

**Verify RED:** `pytest tests/test_stop_hook_status.py::test_output_calls_status_command -v`

---

**GREEN Phase:**

**Implementation:** Replace placeholder with configurable CLI call and ANSI formatting

**Behavior:**
- Run `${STATUS_CMD:-claudeutils _status}` to get status output
- Prepend `\033[0m` (ANSI reset) to each line of output
- On CLI failure: use "Status unavailable" fallback
- Package formatted output as `systemMessage` in JSON response

**Approach:** Capture CLI stdout, pipe through sed or while-read loop to prepend reset code, use jq for JSON construction

**Changes:**
- File: `agent-core/hooks/stop-status-display.sh`
  Action: Replace placeholder output with CLI call + ANSI formatting
  Location hint: Inside the trigger-matched branch

**Verify GREEN:** `just green`

---

### Phase 2: Hook registration (type: inline)

**Model:** sonnet

Register `stop-status-display.sh` in `.claude/settings.json` alongside existing `stop-health-fallback.sh`.

**Edit:** `.claude/settings.json` — add second entry to `hooks.Stop[0].hooks` array:
```json
{
  "type": "command",
  "command": "bash $CLAUDE_PROJECT_DIR/agent-core/hooks/stop-status-display.sh"
}
```

**Verify:** `just precommit` passes. `jq '.hooks.Stop' .claude/settings.json` shows both hooks.

**⚠️ RESTART BOUNDARY:** Hook config changes require session restart. Phases 3 and 4 execute in a new session.

---

### Phase 3: execute-rule.md simplification (type: inline)

**Model:** opus (agentic-prose)
**Blocked by:** Phase 2 + restart

**Edit:** `agent-core/fragments/execute-rule.md` — MODE 1 section

**Remove:** The rendering template — everything between "**STATUS display format:**" and the end of MODE 1's rendering specification (~100 lines). Includes:
- STATUS display format code block
- In-tree list format
- Worktree section rendering rules
- Unscheduled Plans rendering rules
- Parallel task detection rendering
- "Status source" line referencing `claudeutils _worktree ls`

**Keep:**
- MODE 1 trigger definitions (what makes something MODE 1)
- "**Behavior:** Display pending tasks with metadata, then wait for instruction."
- Graceful degradation rules (missing session.md, old format, old section name)
- Planstate-derived commands table (agent needs this for `x`/`r` task pickup, independent of STATUS rendering)
- Session continuation rules
- Next task when in-tree blocked

**Add:** After "Behavior" line:
```
**Rendering:** Output `Status.` as final line — Stop hook renders via `_status` CLI.
```

**Update all STATUS references in other modes:**
- MODE 3 (EXECUTE+COMMIT): "display STATUS" → "output `Status.`"
- MODE 5 (WORKTREE SETUP): if it references STATUS display → same update
- Post-commit display in shortcuts table: reference updated MODE 1

**Verify:** `just precommit` passes. Grep for orphaned "Display STATUS per execute-rule.md MODE 1" in the same file.

---

### Phase 4: Commit skill composition (type: inline)

**Model:** opus (agentic-prose)
**Blocked by:** Phase 2 + restart
**Parallel with:** Phase 3

**Edit:** `agent-core/skills/commit/SKILL.md`

**Composition boundary (from D-2):**

| Skill keeps | Moves to CLI |
|------------|-------------|
| Step 1 discovery (git diff, git status, artifact-prefix grep) | Step 4 staging (`git add`) |
| Step 1 vet classification (trivial/non-trivial/report check) | Validation gates (precommit/lint) |
| Step 1b submodule info gathering (what changed in submodule) | Submodule commit execution |
| Step 1c settings triage | — |
| Step 2 draft message | — |
| Step 3 gitmoji selection | — |

**Replace Step 4 (Stage, commit, verify)** with CLI composition step:

Build structured markdown input per CLI format:
- `## Files` — from git status (unstaged + staged files)
- `## Options` — from skill flags: `--test` → `just-lint`, `--lint` → `just-lint`, `--no-vet` or trivial classification → `no-vet`
- `## Submodule <path>` — if submodule changes detected, include submodule commit message (blockquote format)
- `## Message` — drafted message with gitmoji prefix

Pipe to CLI:
```
echo "$INPUT" | claudeutils _commit
```

On CLI exit 0: success. On exit 1: validation failure (surface CLI output). On exit 2: parse error (surface and fix input).

**Replace Post-Commit section:** Remove "Display STATUS per execute-rule.md MODE 1." Replace with:
```
Output `Status.` — Stop hook renders.
```

**Remove:** Step 1b detailed submodule commit procedure (CWD rule, git -C patterns). CLI handles this. Skill only gathers submodule change info for the `## Submodule` input section.

**Verify:** `just precommit` passes. Read through skill flow end-to-end for coherence.
