# Cycle 4.3

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 4
**Report Path**: `plans/worktree-skill/reports/cycle-4-3-notes.md`

---

## Cycle 4.3: Mode B implementation (parallel group detection)

**RED:**
Skill contains Mode B prose for parallel group worktree creation. Mode B handles `wt` invocation with no arguments. The section describes parallel detection logic and multi-task setup.

Test by reading the skill file. Mode B section should have steps covering:
1. Read session.md and jobs.md
2. Analyze Pending Tasks for parallel group (prose detection logic)
3. If no parallel group: report "No independent parallel group detected" and stop
4. For each task in group: execute Mode A flow
5. Print all launch commands together

Parallel detection criteria should be explicit:
- No shared plan directory between tasks
- No logical dependency (check Blockers/Gotchas mentions)
- Compatible model tier (all sonnet, or all same tier)
- No restart requirement

**GREEN:**
Write Mode B section with tool-anchored steps. Open with Read tools:
- "Read `agents/session.md` and `agents/jobs.md`..." (tool anchor)

Describe parallel group detection as prose analysis (not scripted). Explain each criterion clearly:
- "Examine each pending task's plan directory (if specified). Tasks with different plan directories OR no plan directory are potentially independent."
- "Check Blockers/Gotchas section for logical dependencies between tasks. If Task B mentions Task A, they cannot run parallel."
- "Verify model compatibility. Tasks requiring different model tiers (haiku vs opus) cannot be batched. Tasks with no model specified default to sonnet."
- "Check restart flag. Tasks requiring restart cannot be batched with others."

Specify that the largest independent group should be selected (prefer batching 3 tasks over batching 2 if both groups exist).

If no group found (all tasks have dependencies): output message and stop. Do not create any worktrees.

If group found: "For each task in the parallel group, execute Mode A steps 1-7." Reference Mode A by heading to avoid repetition.

After all worktrees created, print consolidated launch commands:

```
Worktrees ready:
  cd wt/<slug1> && claude    # <task name 1>
  cd wt/<slug2> && claude    # <task name 2>
  ...

After each completes: `hc` to handoff+commit, then return here.
Merge back: `wt merge <slug>` (uses skill)
```

---

**Expected Outcome**: GREEN verification, no regressions
**Stop/Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-4-3-notes.md

---
