# Step 1

**Plan**: `plans/reflect-rca-parity-iterations/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1: Add WIP-Only Restriction to Commit Skill Flags

**Objective:** Clarify that `--test` and `--lint` flags in commit skill are exclusively for WIP commits during TDD execution, not for bypassing validation in final commits.

**Design Reference:** DD-3 (design lines 95-106)

**Current State:**
- File: `agent-core/skills/commit/SKILL.md`
- Flags section (around lines 19-40) documents `--test` and `--lint` with usage examples
- No explicit restriction on when these flags can be used
- An agent can legitimately choose `--test` mode for what it judges as test-only work, bypassing line limits

**Changes Required:**

1. **Locate Flags section** (search for "## Flags" or "Validation level" heading):
   - Update `--test` description: Add "(TDD GREEN phase WIP commits only)"
   - Update `--lint` description: Add "(Post-lint WIP commits only)"
   - After flag descriptions: Insert "**Scope:** WIP commits only. All feature/fix commits must use full `just precommit`."

2. **Locate TDD workflow pattern section** (search for "TDD workflow pattern"):
   - Current text: "After GREEN phase: `/commit --test` for WIP commit"
   - Update to: "After GREEN phase: `/commit --test` for WIP commit (bypasses lint/complexity, test-only validation)"
   - Add below: "After REFACTOR complete: `/commit` for final amend (full precommit required, no flags)"

**Expected Outcome:**
- Flags section explicitly states "WIP commits only" scope restriction
- TDD workflow pattern emphasizes final commits require full precommit
- No functional change to flag behavior — only documentation clarity

**Implementation:**
```
Edit agent-core/skills/commit/SKILL.md:
- Locate Flags section, update --test and --lint descriptions with WIP qualifiers
- After flag descriptions: Insert scope restriction line
- Locate TDD workflow pattern section, update with explicit bypass note and final commit requirement
```

**Validation:**
- Read updated file, verify changes match DD-3 intent: "WIP commits only, final commits require full precommit"
- Verify no unintended changes to other sections (commit message style, execution steps)

**Success Criteria:**
- Flags section includes "WIP commits only" restriction
- TDD workflow pattern distinguishes WIP commits (flags OK) from final commits (full precommit required)
- File structure unchanged (headings, examples preserved)

**Error Conditions:**
- If file structure changed unexpectedly → escalate to sonnet for review
- If DD-3 language ambiguous → re-read design lines 95-106 for exact wording

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-1-execution.md`

---
