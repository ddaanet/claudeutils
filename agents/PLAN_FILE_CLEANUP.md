# Plan: Complete Agent File Reorganization

**Status:** Ready for execution

**Goal:** Complete file renames and deletions from role/rules reorganization.

---

## Context

Opus designed a role/rules reorganization. Haiku created new role files but didn't rename rules files or delete old role files. This plan completes the cleanup.

---

## Changes Required

### Group A: Rename Rules Files

**Current state:** Rules files still use old naming convention
**Target state:** Rules files use `rules-` prefix

#### Step 1: Rename commit.md to rules-commit.md

**Command:**
```bash
mv agents/commit.md agents/rules-commit.md
```

**Verification:** `ls agents/rules-commit.md` exists

#### Step 2: Rename handoff.md to rules-handoff.md

**Command:**
```bash
mv agents/handoff.md agents/rules-handoff.md
```

**Verification:** `ls agents/rules-handoff.md` exists

**CHECKPOINT A:** Both rules files renamed. Awaiting approval.

---

### Group B: Delete Old Role Files

**Current state:** Old role files coexist with new role-* files
**Target state:** Only role-* files exist

#### Step 3: Delete old role files

**Command:**
```bash
rm agents/planning.md agents/code.md agents/lint.md agents/remember.md
```

**Verification:**
```bash
ls agents/planning.md 2>&1 | grep "No such file"
ls agents/code.md 2>&1 | grep "No such file"
ls agents/lint.md 2>&1 | grep "No such file"
ls agents/remember.md 2>&1 | grep "No such file"
```

**CHECKPOINT B:** Old files deleted. Awaiting approval.

---

### Group C: Verify References

#### Step 4: Verify AGENTS.md references are correct

**Check:** All role/rule file references in AGENTS.md point to existing files

**Command:**
```bash
grep -o 'agents/[a-z-]*\.md' AGENTS.md | sort -u | while read f; do
  if [ ! -f "$f" ]; then
    echo "Missing: $f"
  fi
done
```

**Expected output:** (empty - all files exist)

**CHECKPOINT C:** All references verified. **Complete.**

---

## Handoff Preparation

After completing this plan, prepare handoff document with:

### Session Summary

1. **Compliance failure resolved:**
   - Issue: Code role agent ran `just check` violating role constraint
   - Root cause: Plan instructed `just check` conflicting with role rules
   - Resolution: Added Plan Conflicts/Bugs sections to role-code.md

2. **Agent file reorganization completed:**
   - Created 6 role files (planning, code, lint, refactor, execute, remember)
   - Renamed 2 rules files (commit, handoff)
   - Deleted 4 old role files
   - Added role-based justfile recipes

3. **Inline help implementation completed:**
   - All 5 CLI help tests passing
   - Plan updated to use `just role-code` instead of `just check`
   - Line length issues resolved

### File Inventory

**Role files:**
- agents/role-planning.md - opus/sonnet test specification design
- agents/role-code.md - haiku TDD implementation
- agents/role-lint.md - haiku lint/type fixes
- agents/role-refactor.md - sonnet refactoring plans
- agents/role-execute.md - haiku plan execution
- agents/role-remember.md - opus documentation updates

**Rules files:**
- agents/rules-commit.md - git commit guidelines
- agents/rules-handoff.md - session handoff guidelines

**Old files removed:**
- agents/planning.md
- agents/code.md
- agents/lint.md
- agents/remember.md

### Next Agent Instructions

**Entry point:** Read `START.md` then `AGENTS.md`

**State:** All tests passing, lint passing, ready for new work

**Clean context slate:** This session resolved meta-issues (role definitions, compliance). Next agent should start fresh with task work.

---

## Implementation Notes

- Use bash commands directly (not Edit/Write tools) for file operations
- Verify each operation before proceeding to next
- If any verification fails, STOP and report
