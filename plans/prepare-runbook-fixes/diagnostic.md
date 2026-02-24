# Diagnostic: prepare-runbook.py Step File Generation Bugs

**Date:** 2026-02-24
**Severity:** Minor (context noise in generated step files, not execution-blocking)
**Source file:** `agent-core/bin/prepare-runbook.py`

## Bug 1: Trailing Phase Preamble in Boundary Step Files

### Symptom

Last step file of each phase includes the next phase's full preamble as trailing content. Example: `step-1-4.md` ends with the Phase 2 preamble (scope, files, key constraints).

### Root Cause

`extract_cycles()` at line 104:

```python
# Line 150
elif line.startswith("## ") and current_cycle is not None and not in_fence:
```

Cycle accumulation terminates only on H2 (`## `) headers. Phase preambles use H3 (`### Phase N: Title`). The last cycle in a phase accumulates everything after it until EOF or the next H2 — including `### Phase N+1:` preamble content.

Lines 161-163 (final cycle flush) capture all remaining content unconditionally:
```python
if current_cycle is not None:
    current_cycle["content"] = "\n".join(current_content).strip()
```

### Fix Options

**Option A (targeted):** Add H3 phase header as termination condition:
```python
elif (line.startswith("## ") or re.match(r"^### Phase\s+\d+", line)) and current_cycle is not None and not in_fence:
```

**Option B (general):** Strip content after the last `---` separator in cycle content, since phase preambles are always preceded by `---`.

**Option C (content trim):** In `generate_cycle_file()`, detect and strip `### Phase` content from `cycle["content"]` before writing.

Option A is most precise — matches the structural pattern rather than content heuristics.

### Reproduction

Run `prepare-runbook.py` against any multi-phase runbook. Check last step file of each non-final phase for `### Phase N+1:` content.

---

## Bug 2: Non-existent `runbook.md` Path in Step Metadata

### Symptom

All generated step files reference a non-existent path in their metadata header:

```markdown
**Plan**: `plans/<name>/runbook.md`
```

Actual source files are `runbook-phase-{1-4}.md`. No `runbook.md` exists.

### Root Cause

`generate_cycle_file()` at line 1048 uses `runbook_path` argument:
```python
f"**Plan**: `{runbook_path}`",
```

Called from `validate_and_create` at line 1385:
```python
step_file_content = generate_cycle_file(
    cycle,
    str(runbook_path),  # <-- canonical path, not actual source
    ...
)
```

`validate_and_create` receives `runbook_path` which is either a synthetic canonical path or a now-removed combined file. The path is written as provenance metadata but doesn't correspond to any existing file.

Same issue in `generate_step_file()` at line 1000 for general steps.

### Fix Options

**Option A:** Use actual source phase file path: `plans/<name>/runbook-phase-{N}.md` — requires passing phase number to the generator.

**Option B:** Use the plan directory path instead: `plans/<name>/` — always valid, identifies the plan without claiming a specific file.

**Option C:** Verify path exists before writing; fall back to plan directory if not found.

Option A is most accurate — step files trace back to their actual source.

---

## Evidence (fixed manually 2026-02-24)

- `plans/orchestrate-evolution/steps/step-1-4.md` — removed 19 lines of Phase 2 preamble
- `plans/orchestrate-evolution/steps/step-2-4.md` — removed 22 lines of Phase 3 preamble
- `plans/orchestrate-evolution/steps/step-3-4.md` — removed 19 lines of Phase 4 preamble
