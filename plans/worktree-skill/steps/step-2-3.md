# Cycle 2.3

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 2
**Report Path**: `plans/worktree-skill/reports/cycle-2-3-notes.md`

---

## Cycle 2.3: Learnings conflict keep-both

**NFR-2: Deterministic learnings.md conflict resolution with append strategy.**

**RED: Test behavior**

Create test fixture with two learnings.md versions:
- **Ours:** Three learning entries with `## Title` headings: "Tool batching unsolved", "Scan triggers unnecessary tools", "Structural header dot syntax"
- **Theirs:** Same three entries plus new entry "## Vet-fix-agent confabulation from design docs"

Call `resolve_learnings_conflict(ours, theirs)` and assert:
- Result contains all four learning entries
- New entry appended at end (after "Structural header dot syntax")
- All entries preserve exact content (multi-paragraph text, code blocks, bullet lists)
- No duplication of shared entries

**Expected failure:** Function doesn't exist yet.

**GREEN: Implement behavior**

Create function `resolve_learnings_conflict(ours: str, theirs: str) -> str`:

**Algorithm hints:**
1. Parse both versions into learning entries: split on `## ` heading delimiter (regex `^## `, `re.MULTILINE`)
2. Extract heading text from each entry (first line after split, strip `## ` prefix)
3. Build set of ours headings for comparison
4. Identify new entries in theirs: headings present in theirs but not in ours
5. Append new entry content (full text from `## Title` to next `## ` or EOF) to ours
6. Return merged content with ours entries plus new theirs entries

**Approach notes:**
- Learnings.md is append-only, so theirs additions are always at the end
- No reordering needed: preserve ours order, append theirs new entries
- Handle edge case: preamble text before first `## ` heading (keep from ours, ignore from theirs)

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-2-3-notes.md

---
