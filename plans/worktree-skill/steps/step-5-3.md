# Cycle 5.3

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 5
**Report Path**: `plans/worktree-skill/reports/cycle-5-3-notes.md`

---

## Cycle 5.3: sandbox-exemptions.md Worktree Patterns

**RED — Specify the behavior to verify:**

The `agent-core/fragments/sandbox-exemptions.md` file does not yet document worktree-specific sandbox bypass requirements. Agents invoking `_worktree new` need guidance on when sandbox bypass is required.

**Test expectations:**
- Section exists documenting worktree sandbox requirements
- Explains that `wt/` inside project root eliminates most sandbox bypass needs
- Documents exceptions: `uv sync` (network + filesystem for package downloads) and `direnv allow` (writes outside project)
- Notes that skill invokes these with `dangerouslyDisableSandbox: true`

**GREEN — Implement to make tests pass:**

Add a worktree-specific section to `sandbox-exemptions.md` documenting the directory location change (inside project root) and the remaining operations that require sandbox bypass (environment setup: `uv sync` and `direnv allow`).

**Approach:**
- Add new section: "### Worktree Operations"
- Explain directory location eliminates most bypass needs
- List exceptions: environment initialization steps in new worktrees
- Clarify that skill handles sandbox bypass, CLI itself is agnostic

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-5-3-notes.md

---
