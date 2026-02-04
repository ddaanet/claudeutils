# Cycle 2.7

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-2-7-notes.md`

---

## Cycle 2.7: Parse transcript for context tokens (fallback path)

**Objective**: calculate_context_tokens() parses transcript file when current_usage is None (R2 requirement)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py creates StatuslineInput with current_usage=None, mocks Path.open to return transcript JSONL with assistant message containing usage tokens, asserts calculate_context_tokens() returns sum of tokens

**Expected failure:**
```
AssertionError: assert 0 == 200
```

**Why it fails:** calculate_context_tokens() returns 0 when current_usage is None (no fallback yet)

**Verify RED:** pytest tests/test_statusline_context.py::test_calculate_context_tokens_from_transcript -xvs
- Must fail with AssertionError (returns 0 instead of token sum)
- If passes, STOP - transcript fallback may already exist

---

**GREEN Phase:**

**Implementation:** Add parse_transcript_context() helper that reads last 1MB of transcript file, parses JSONL in reverse, finds first assistant message with non-zero tokens

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Add parse_transcript_context(transcript_path: str) → int, read last 1MB with seek, parse lines in reverse, filter type=="assistant" and not isSidechain, sum 4 token fields, return first non-zero
- File: src/claudeutils/statusline/context.py
  Action: Update calculate_context_tokens() to call parse_transcript_context() when current_usage is None

**Verify GREEN:** pytest tests/test_statusline_context.py::test_calculate_context_tokens_from_transcript -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-7-notes.md

---
