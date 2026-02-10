# Cycle 4.5

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 4
**Report Path**: `plans/worktree-skill/reports/cycle-4-5-notes.md`

---

## Cycle 4.5: D+B hybrid tool anchors and error communication polish

**RED:**
Every major step in the skill opens with a tool call mention. Scan all three modes for prose-only steps (steps with no Read, Write, Edit, Bash, or Skill mention). D+B hybrid pattern requires tool anchors to prevent execution mode from skipping prose gates.

Additionally, check error communication sections for resolution guidance. Error messages should tell user "what to do next" not just "what went wrong."

**GREEN:**
Review all three modes. For any step lacking a tool anchor, add one:

**Mode A:**
- Slug derivation (step 2): anchor with "Derive slug (use helper function or inline logic)..." — mention this is deterministic transformation
- Focused session generation (step 3): ensure "Generate focused session.md content" specifies the structure explicitly (acts as pseudo-tool guidance)

**Mode B:**
- Parallel detection prose (step 2): already anchored with Read at start, but ensure analysis description is imperative ("Check for shared plan directories...")
- Group iteration (step 4): "For each task in the parallel group, execute Mode A steps" — reference by heading (not a new tool anchor, but clear control flow)

**Mode C:**
- All steps already have tool anchors (Skill, Bash, Edit, Bash)

Polish error messages in Mode C to include resolution steps:
- Conflict errors: numbered list of "what to do" not just "conflicts exist"
- Precommit errors: explain that merge commit already exists (user amends, not re-merges)
- Include command examples in error guidance (literal `git add`, `git commit --amend --no-edit`)

Add a closing section after Mode C: `## Usage Notes`

Include:
- Slug derivation determinism: same task name always produces same slug
- Idempotent merge: safe to re-run `wt merge <slug>` after manual fixes
- Cleanup responsibility: user should `wt merge <slug>` after completing worktree work (not automatic)
- Parallel execution note: after `wt` creates multiple worktrees, each must be merged back individually

Ensure prose uses imperative/infinitive style throughout (command the agent, not describe what might happen).

---

**Expected Outcome**: GREEN verification, no regressions
**Stop/Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-4-5-notes.md

### Phase 5: Integration and Documentation (~4 cycles)

**Model:** haiku (mechanical wiring)
**Checkpoint:** light (vet-fix-agent)
**Depends on:** Phases 0-4 (CLI + SKILL.md implementation)

**Overview:** Wire worktree CLI into main command interface, update project configuration and documentation to reflect the new skill, and remove obsolete justfile recipes.

---
