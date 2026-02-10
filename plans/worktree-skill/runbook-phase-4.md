### Phase 4: SKILL.md (orchestration)

**Model:** opus (workflow artifact authoring)
**Files:** `agent-core/skills/worktree/SKILL.md`
**Depends on:** Phases 0-3 (all CLI implementation)
**Checkpoint:** Full with design-vet-agent (workflow artifact requires opus review)

**Prerequisites:**
- Load `plugin-dev:skill-development` before starting (imperative/infinitive style guide)
- Review design decisions D-5 (CLI/skill boundary), D-9 (no plan-specific agent)
- Understand D+B hybrid pattern (every skill step opens with tool call)

**Context:** The CLI implementation is complete. This phase creates the `/worktree` skill that orchestrates the ceremony: session.md manipulation, handoff/commit chain, parallel detection, merge coordination, and error communication. The skill is the user interface; the CLI is the implementation.

---

## Cycle 4.1: Frontmatter and file structure

**RED:**
Test YAML frontmatter validates. Create empty skill file `agent-core/skills/worktree/SKILL.md` with only frontmatter YAML. Run `python3 -c 'import yaml; yaml.safe_load(open("agent-core/skills/worktree/SKILL.md").read().split("---")[1])'` — should parse without errors.

Expected frontmatter fields:
- `name: worktree` (skill identifier)
- `description:` multi-line text mentioning invocation triggers: "create a worktree", "set up parallel work", "merge a worktree", "branch off a task", `wt` shortcut
- `allowed-tools:` list including Read, Write, Edit, `Bash(claudeutils _worktree:*)`, `Bash(just precommit)`, `Bash(git status:*)`, `Bash(git worktree:*)`, Skill
- `user-invocable: true`
- `continuation:` block with `cooperative: true` and `default-exit: []` (empty array for no tail calls)

**GREEN:**
Create `agent-core/skills/worktree/SKILL.md` with frontmatter block following YAML multi-line syntax for description. Use `>-` for folded scalar (preserves single newlines, folds long lines).

Describe the skill's purpose clearly: manages worktree lifecycle from creation through merge cleanup. Mention all invocation patterns user might say. Include behavioral triggers: "create", "set up", "merge", "branch off", plus literal shortcut `wt`.

Specify allowed-tools comprehensively. Use wildcard patterns where appropriate (`claudeutils _worktree:*` covers all subcommands). Include Skill tool for potential `/handoff --commit` invocation.

Set continuation cooperative mode with empty default-exit (skill completes inline, no tail calls by default).

After frontmatter, add H2 section headers for the three modes: `## Mode A: Single Task`, `## Mode B: Parallel Group`, `## Mode C: Merge Ceremony`. Leave sections empty for now.

---

## Cycle 4.2: Mode A implementation (single-task worktree)

**RED:**
Skill contains Mode A prose that describes single-task worktree creation flow. Mode A should handle `wt <task-name>` invocation pattern. The prose should read as imperative instructions.

Test by reading the skill file. Mode A section should have numbered steps covering:
1. Read session.md to locate task
2. Derive slug from task name (lowercase, hyphens, 30 char max)
3. Generate focused session.md content (minimal scope)
4. Write focused session to `tmp/wt-<slug>-session.md`
5. Invoke CLI: `claudeutils _worktree new <slug> --session tmp/wt-<slug>-session.md`
6. Edit session.md: move task from Pending Tasks to Worktree Tasks with `→ wt/<slug>` marker
7. Print launch command for user

Each step should open with a tool mention (D+B hybrid anchor). Example: "Read `agents/session.md` to locate the task by name."

**GREEN:**
Write Mode A section with imperative prose. Begin each major step with explicit tool usage:
- "Read `agents/session.md`..." (tool anchor)
- "Derive slug..." (prose explanation of transform)
- "Generate focused session.md content..." (describe minimal format)
- "Write to `tmp/wt-<slug>-session.md`..." (tool anchor)
- "Invoke: `claudeutils _worktree new <slug> --session tmp/wt-<slug>-session.md`" (tool anchor with bash)
- "Edit `agents/session.md`..." (tool anchor)

Describe focused session.md format: minimal session scoped to single task with only relevant blockers/references. Provide template structure:

```markdown
# Session: Worktree — <task name>

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **<task name>** — <full metadata from original>

## Blockers / Gotchas

<only blockers relevant to this task>

## Reference Files

<only references relevant to this task>
```

For the session.md edit step, specify exact transformation: locate task in Pending Tasks section, extract full task block (including continuation lines), create Worktree Tasks section if not exists, append task with `→ wt/<slug>` marker.

End with user output: `cd wt/<slug> && claude    # <task name>`

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

## Cycle 4.4: Mode C implementation (merge ceremony)

**RED:**
Skill contains Mode C prose for merge ceremony orchestration. Mode C handles `wt merge <slug>` invocation pattern. The section describes handoff → commit → merge → cleanup flow with error handling.

Test by reading the skill file. Mode C section should have steps covering:
1. Invoke `/handoff --commit` (ceremony before merge)
2. Wait for commit completion, stop if handoff/commit fails
3. Invoke CLI merge: `claudeutils _worktree merge <slug>`
4. Handle merge exit codes (0 success, 1 conflicts/precommit failure, 2 error)
5. On success: edit session.md to remove task from Worktree Tasks
6. On success: invoke cleanup `claudeutils _worktree rm <slug>`
7. On failure: report error with resolution guidance

**GREEN:**
Write Mode C section with skill invocation anchor:
- "Invoke `/handoff --commit` to ensure clean tree and session context committed." (tool anchor: Skill tool)

Explain the ceremony requirement: merge needs clean tree, handoff ensures session.md reflects current state, commit creates sync point.

After handoff+commit: "If handoff or commit fails, STOP. Merge requires clean tree. Resolve handoff/commit issues before retrying merge."

Invoke merge with bash anchor:
- "Invoke: `claudeutils _worktree merge <slug>`" (tool anchor)

Parse exit code and handle three cases:

**Exit 0 (success):**
- "Edit `agents/session.md`: Remove task from Worktree Tasks section (match on `→ wt/<slug>` marker)." (tool anchor)
- "Invoke: `claudeutils _worktree rm <slug>`" (tool anchor)
- Output: "Merged and cleaned up wt/<slug>. Task complete."

**Exit 1 (conflicts or precommit failure):**
Read stderr from merge command. Parse for conflict indicators or precommit failure messages.

If conflicts: list conflicted files, provide resolution guidance:
```
Conflicts detected:
  <file list from stderr>

Resolution steps:
1. For session files: conflicts should be auto-resolved (report as bug)
2. For source files: manually resolve conflicts, then `git add <files>`
3. Re-run: `wt merge <slug>` (idempotent, resumes from conflict state)
```

If precommit failure: show which checks failed, provide guidance:
```
Precommit failed after merge:
  <check names from stderr>

Resolution steps:
1. Fix reported issues (merge commit is already created)
2. Stage fixes: `git add <files>`
3. Amend merge commit: `git commit --amend --no-edit`
4. Re-run precommit: `just precommit`
5. After passing: `wt merge <slug>` to continue cleanup
```

**Exit 2 (error):**
Report stderr as-is. Generic error handling: "Merge command error. Review output above and resolve before retrying."

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
