# Step 6

**Plan**: `plans/validator-consolidation/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Step 6: Port Memory Index Validator + Tests

**Objective**: Port memory index validation (FR-3: entry existence/ambiguity/duplicates; FR-5: orphan detection as errors) with autofix.

**Execution Model**: Haiku

**Source**: `agent-core/bin/validate-memory-index.py` (~480 lines)

**Implementation**:

1. Create `src/claudeutils/validation/memory_index.py`:
   - Port all functions: `collect_structural_headers()`, `collect_semantic_headers()`, `extract_index_entries()`, `extract_index_structure()`, `validate()`, `autofix_index()`
   - `validate(index_path: str, root: Path, autofix: bool = True) -> list[str]`
   - Keep all regex patterns: `SEMANTIC_HEADER`, `STRUCTURAL_HEADER`, `DOC_TITLE`, `FILE_SECTION`
   - Keep `INDEXED_GLOBS`, `EXEMPT_SECTIONS` constants
   - Preserve autofix behavior: fix placement/ordering/structural issues silently, report only non-autofixable errors
   - Preserve orphan detection (FR-5): semantic headers without index entries → ERROR
   - If module exceeds 350 lines: extract `autofix_index()` and collection functions (`collect_structural_headers`, `collect_semantic_headers`) to `memory_index_helpers.py`. Main module keeps `validate()`, `extract_index_entries()`, `extract_index_structure()`.

2. Create `tests/test_validation_memory_index.py`:
   - Test: valid index with matching headers → no errors
   - Test: orphan semantic header (not in index) → error (FR-5)
   - Test: orphan index entry (no matching header) → error
   - Test: duplicate index entries → error
   - Test: word count violation (outside 8-15 range) → error
   - Test: missing em-dash separator → error
   - Test: entry in wrong section → autofixed (no error if autofix=True)
   - Test: entries out of order → autofixed
   - Test: structural header entries → removed by autofix
   - Test: exempt sections preserved as-is
   - Test: autofix=False reports all issues as errors
   - Test: duplicate headers across files → error
   - Test: multiple autofix issues resolved in single pass (wrong section + out of order)

**Expected Outcome**: Memory index validator identical behavior including autofix.

**Success Criteria**: `pytest tests/test_validation_memory_index.py -q` passes, FR-3 and FR-5 verified.

**Phase 2 Checkpoint**: Run `pytest tests/test_validation_*.py -q` and `mypy src/claudeutils/validation/`. All must pass before proceeding.

---
