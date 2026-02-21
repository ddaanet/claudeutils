---
name: hook-batch-phase-3
model: haiku
---

# Phase 3: PostToolUse Auto-Format Hook

**Type:** General
**Target:** `agent-core/hooks/posttooluse-autoformat.sh` (new file)
**Design ref:** `plans/hook-batch/outline.md` (Phase 3)

**Prerequisites:**
- Run `which ruff` and `which docformatter` to verify tool availability before creating script
- Verify `agent-core/hooks/posttooluse-autoformat.sh` does NOT exist yet

**Key decisions:**
- D-2: Bash (simple command orchestration, no complex pattern matching)
- D-3: File-specific ruff only (`ruff check --fix-only --quiet` + `ruff format --quiet`), NOT full `just format`
- PostToolUse hook receives Write|Edit events with `tool_input.file_path`
- Non-fatal: script always exits 0; formatting errors go to stderr, do not block the write
- D-1: Command hook type

---

## Step 3.1: Create Auto-Format Script

**Objective:** Create `agent-core/hooks/posttooluse-autoformat.sh` that runs ruff + docformatter on Python files after Write/Edit completes.

**Script Evaluation:** Medium — new Bash script with JSON parsing via python3 -c subprocess, conditional execution, tool availability checks.

**Execution Model:** Haiku

**Prerequisite:**
- Verify `which ruff` → ruff is available at known path
- Verify `which docformatter` → docformatter availability (script handles missing gracefully)
- Read `.claude/settings.json` hooks section to confirm Write|Edit PostToolUse hook structure expected

**Implementation:**

Script logic (ordered):
1. Read stdin JSON — use `python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("tool_input",{}).get("file_path",""))' 2>/dev/null` to extract `file_path`
2. If `file_path` is empty → exit 0 (no file to format)
3. If file does not end in `.py` → exit 0 (skip non-Python files)
4. Run: `ruff check --fix-only --quiet "$file_path"` (auto-fix linting issues)
5. Run: `ruff format --quiet "$file_path"` (format)
6. If `command -v docformatter >/dev/null 2>&1`: run `docformatter --in-place "$file_path"` (optional)
7. Silent on success — no stdout output
8. Any errors go to stderr (non-fatal) — wrap ruff calls in `|| true` equivalent using `2>&1` redirect or explicit error capture

Script header:
```
#!/usr/bin/env bash
set -euo pipefail
```

Note: `set -euo pipefail` combined with explicit `|| true` on optional docformatter prevents early exit on missing tool.

**Expected Outcome:** Script file created at `agent-core/hooks/posttooluse-autoformat.sh` with execute permissions. Script parses PostToolUse stdin JSON, formats `.py` files with ruff, optionally runs docformatter.

**Error Conditions:**
- python3 not available → STOP, report (python3 required by other hooks; this is a system issue)
- ruff not available → log to stderr, exit 0 (non-fatal — formatting is best-effort)
- docformatter not available → skip silently (optional tool)
- file_path extraction fails → exit 0 (non-fatal pass-through)

**Validation:**
```bash
# Set execute permissions
chmod +x agent-core/hooks/posttooluse-autoformat.sh

# Test 1: Python file formatting
echo '{"tool_name":"Write","tool_input":{"file_path":"agent-core/hooks/posttooluse-autoformat.sh"}}' \
  | bash agent-core/hooks/posttooluse-autoformat.sh
# Expected: silent (sh file, not .py — gets skipped)

# Test 2: Non-.py file skip
echo '{"tool_name":"Write","tool_input":{"file_path":"README.md"}}' \
  | bash agent-core/hooks/posttooluse-autoformat.sh
# Expected: silent, exit 0

# Test 3: Empty tool_input
echo '{"tool_name":"Write","tool_input":{}}' \
  | bash agent-core/hooks/posttooluse-autoformat.sh
# Expected: silent, exit 0

# Test 4: Python file (use a real .py file to verify ruff runs)
echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"agent-core/hooks/pretooluse-recipe-redirect.py\"}}" \
  | bash agent-core/hooks/posttooluse-autoformat.sh
# Expected: silent (ruff runs, no output on already-formatted file)
```

---

## Step 3.2: Validate Auto-Format Behavior

**Objective:** Confirm the script handles edge cases correctly: non-.py skip, missing file, real .py formatting.

**Script Evaluation:** Small — validation commands only, no new files.

**Execution Model:** Haiku

**Implementation:**

```bash
# Verify script exists and is executable
test -x agent-core/hooks/posttooluse-autoformat.sh && echo "✓ Script exists and executable"

# Verify non-.py is skipped (exit 0, no output)
result=$(echo '{"tool_name":"Edit","tool_input":{"file_path":"agent-core/justfile"}}' \
  | bash agent-core/hooks/posttooluse-autoformat.sh 2>&1)
[ -z "$result" ] && echo "✓ Non-.py file skipped silently"

# Verify missing file_path is handled gracefully
result=$(echo '{}' | bash agent-core/hooks/posttooluse-autoformat.sh 2>&1)
echo "Exit code: $?" && echo "Output: '$result'"
# Expected: exit 0, no crash

# Verify ruff runs on a real Python file without crashing
echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"agent-core/bin/learning-ages.py\"}}" \
  | bash agent-core/hooks/posttooluse-autoformat.sh
echo "Exit code: $?" # Expected: 0
```

**Expected Outcome:** All validation checks pass — script handles edge cases gracefully, no crashes, non-.py files skipped.

**Error Conditions:**
- Any validation command exits non-zero → diagnose and fix script
- Script crashes on `{}` input → fix empty-input guard in Step 3.1

**Validation:**
- All check commands above exit 0
- `wc -l agent-core/hooks/posttooluse-autoformat.sh` → between 20-50 lines (compact Bash)

---

## Phase 3 Completion

**Success criteria:**
- `agent-core/hooks/posttooluse-autoformat.sh` exists with execute permissions
- All Step 3.2 validation checks pass
- Script handles non-.py, empty input, and missing tool gracefully
- `pytest tests/ -v` → all existing tests still pass (no regression)
