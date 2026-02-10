# Worktree Integration Exploration Report

Comprehensive analysis of worktree-related integration points across the claudeutils codebase.

## Executive Summary

The worktree system is integrated across 5 recipe commands in justfile, Mode 5 behavior in execute-rule.md, session.md task tracking conventions, and handoff protocol rules. A critical gap exists: `focus-session.py` is referenced in session.md and used by `wt-task` recipe but does NOT exist in the codebase—the script was documented but never committed.

**Key finding:** Worktree operations require `dangerouslyDisableSandbox: true` because they write outside the project directory (`../claudeutils-<slug>/`).

---

## 1. Worktree Recipe Commands

### Location
`/Users/david/code/claudeutils/justfile` (lines 49-163)

### Five Recipes

**1. `wt-new name base="HEAD" session=""`** (lines 51-85)
- Creates git worktree for parallel work
- Path pattern: `../<repo-name>-<name>/`
- Branch pattern: `wt/<name>`
- Optional focused session.md pre-commit via git plumbing
- Submodule initialization: `git submodule update --init --reference`
- Creates `.venv`, allows direnv
- **Requires:** `dangerouslyDisableSandbox: true` (writes outside project)

**2. `wt-task name task_name base="HEAD"`** (lines 88-95)
- Wrapper around `wt-new` for single-task worktrees
- **CRITICAL GAP:** Calls `agent-core/bin/focus-session.py` which DOES NOT EXIST
- Script output → `tmp/focused-session-<name>.md` → passed to `wt-new`
- Cleans up temp session file after worktree creation

**3. `wt-ls`** (lines 97-99)
- Simple wrapper: `git worktree list`
- No special constraints

**4. `wt-rm name`** (lines 102-121)
- Removes worktree and cleans up branch
- Checks for uncommitted changes (warns user)
- `--force` flag required for worktrees with submodules
- Attempts `git branch -d`, falls back to user instruction for `-D`
- **Requires:** `dangerouslyDisableSandbox: true`

**5. `wt-merge name`** (lines 124-163)
- Two-phase merge: submodule first, then parent
- Auto-resolves agent-core + session.md conflicts (keeps ours)
- Fails if other conflicts remain
- **Requires:** `dangerouslyDisableSandbox: true`

### Common Patterns
- Repo name: `$(basename "$PWD")`
- Worktree directory: `../<repo-name>-<name>`
- Branch naming: `wt/<name>`
- bash_prolog execution context (set -euo pipefail, helper functions)

---

## 2. Mode 5: Worktree Setup (execute-rule.md)

### Location
`/Users/david/code/claudeutils/agent-core/fragments/execute-rule.md` (lines 108-167)

### Behavior Specification

**Triggers:**
- `wt` (no args) — set up parallel group
- `wt <task-name>` — branch off single named task

**Single-task flow (5 steps):**
1. Derive slug from task name (lowercase, hyphens, ≤30 chars)
2. Write focused session.md to `tmp/wt-<slug>-session.md` (local, no sandbox)
3. Create worktree: `just wt-new <slug> session=tmp/wt-<slug>-session.md`
4. Move task from Pending Tasks to Worktree Tasks in main session.md
5. Print launch command

**Parallel group flow (6 steps):**
1. Identify parallel group (STATUS detection logic)
2. For each task, derive slug
3. Write focused session.md to `tmp/wt-<slug>-session.md`
4. Create worktree: `just wt-new <slug> session=tmp/wt-<slug>-session.md`
5. Move tasks from Pending Tasks to Worktree Tasks
6. Print launch commands

**Focused session.md format:**
```markdown
# Session: Worktree — <task name>

**Status:** Focused worktree for parallel execution.

## Pending Tasks
- [ ] **<task name>** — <full metadata from original>
  - <plan info if applicable>

## Blockers / Gotchas
<only blockers relevant to this task>

## Reference Files
<only references relevant to this task>
```

**Output format:**
```
Worktrees ready:
  cd ../<repo>-<slug1> && claude    # <task name 1>
  cd ../<repo>-<slug2> && claude    # <task name 2>

After each completes: `hc` to handoff+commit, then return here.
Merge back: git merge wt/<slug>
Cleanup: just wt-rm <slug>
```

**Sandbox note:** Only `just wt-new` requires `dangerouslyDisableSandbox: true`.

---

## 3. Worktree Tasks Section (session.md conventions)

### Locations
- `agent-core/fragments/execute-rule.md` (lines 241-255)
- `agent-core/skills/handoff/references/template.md` (lines 24-28)

### Format Specification

**Section header:**
```markdown
## Worktree Tasks
```

**Task format:**
```markdown
- [ ] **Task Name** → `wt/<slug>` — original metadata
```

**Rules:**
1. Tasks move from Pending Tasks to Worktree Tasks when `wt` creates their worktree
2. `→ wt/<slug>` tracks which worktree holds the task
3. After merge + `wt-rm`, remove task from Worktree Tasks (move to Completed or delete)
4. Handoff preserves Worktree Tasks section as-is (not trimmed)

### STATUS Display Integration

**Worktree section in STATUS output (execute-rule.md lines 29-31):**
```
Worktree:
- <task name> → wt/<slug>
- <task name 2> → wt/<slug2>
```

**Display rules:**
- Only shown when worktree tasks exist in session.md
- Tasks in Worktree section are NOT shown in Pending
- Format shows task name and worktree slug for `wt-rm` reference

---

## 4. wt/ Branch Prefix Usage

### Grep Results (7 files)

**Core integration files:**
- `justfile` — `wt/<name>` branch naming convention
- `agent-core/fragments/execute-rule.md` — documentation and STATUS display
- `agent-core/skills/handoff/references/template.md` — Worktree Tasks format

**Plan files (design artifacts):**
- `plans/wt-merge-skill/outline.md` — design seed for future skill
- `plans/plugin-migration/runbook-phase-4.md` — references worktree branch
- `plans/plugin-migration/reports/explore-justfiles.md` — documentation

### Convention
All worktree branches use `wt/` prefix exclusively. No other branch naming patterns observed.

---

## 5. Missing Script: focus-session.py

### Status: **DOES NOT EXIST**

**Referenced in:**
- `agents/session.md` (line 119): Listed as "Worktree session context extraction script"
- `agents/session.md` (line 23): Described as created with capabilities
- `justfile` (line 93): Invoked by `wt-task` recipe

**Expected location:**
`agent-core/bin/focus-session.py`

**Documented capabilities:**
- Extracts task from session.md with plan context
- Handles 5+ document types: rca, requirements, design, problem, runbook/outline
- Auto-extracts relevant sections (executive summary, fix tasks, requirements, problem statements)
- Supports both `plans/name` and `Plan: name` reference formats

**Consequence:**
`just wt-task <name> "<task>"` recipe will fail at line 93 when attempting to execute non-existent script.

**Evidence from session.md (commit ff056c7):**
The script was created and tested in a previous session (2026-02-09) but the session.md entry suggests it may have been part of uncommitted work or lost during merge conflicts.

---

## 6. task-context.sh Script

### Location
`/Users/david/code/claudeutils/agent-core/bin/task-context.sh`

### Purpose
Recovers session.md from the git commit where a task was first introduced.

### Implementation (21 lines)
```bash
#!/usr/bin/env bash
set -euo pipefail

# Find oldest commit where task name's count changed (= introduction)
commit=$(git log --all -S "$task_name" --format=%H -- agents/session.md | tail -1)

if [[ -z "$commit" ]]; then
    echo "Error: task name '$task_name' not found in git history" >&2
    exit 1
fi

echo "# Context from $(git log -1 --format='%h %s' "$commit")" >&2
git show "$commit:agents/session.md"
```

### Usage Pattern
From `execute-rule.md` (lines 169-173):
> Before starting a pending task, run `agent-core/bin/task-context.sh '<task-name>'` to recover the session.md where it was introduced.

### Integration
- Task name serves as lookup key
- Uses `git log -S` to find introduction commit
- Outputs full session.md from that commit
- Error handling for missing task names

---

## 7. Skill Structural Conventions

Analyzed 3 representative skills: shelve, commit, handoff.

### Frontmatter Fields (YAML)

**Common fields across all skills:**
```yaml
description: <one-line description>
allowed-tools: <comma-separated list>
user-invocable: <true|false>
```

**Continuation-passing fields (commit, handoff only):**
```yaml
continuation:
  cooperative: true
  default-exit: [<skill-list>]
```

**Field variations:**
- `name:` field (handoff uses it, others don't—inconsistent)
- Bash tool permissions use precise patterns: `Bash(git add:*)`, `Bash(just precommit)`

### Allowed-Tools Patterns

**Shelve skill:**
- `Read, Write, Edit, Bash(mkdir:*), Bash(cp:*)`
- No continuation (terminal skill)

**Commit skill:**
- `Read, Skill, Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(just precommit), Bash(just test), Bash(just lint)`
- Continuation: cooperative, default-exit empty (customizable per invocation)

**Handoff skill:**
- `Read, Write, Edit, Bash(wc:*, agent-core/bin/learning-ages.py:*), Task, Skill`
- Continuation: cooperative, default-exit `["/commit"]`

**Orchestrate skill (header only):**
- `Task, Read, Write, Bash(git:*), Skill`
- Continuation: cooperative, default-exit `["/handoff --commit", "/commit"]`

### Step Structure

**All skills follow:**
1. Numbered sections (`## N. Section Name`)
2. Sub-steps use letters or prose headings
3. Prose gates merged with action steps (D+B hybrid pattern per RCA findings)
4. Every step opens with tool call (Read/Bash/Glob) to avoid execution mode skipping

**Critical pattern from commit.md (lines 89-91):**
```markdown
<!-- DESIGN RULE: Every step must open with a tool call (Read/Bash/Glob).
     Prose-only steps get skipped. See: plans/reflect-rca-prose-gates/outline.md
     Comment placement: after heading, before first prose content. -->
```

### Gate Patterns

**Commit skill (Step 1):**
- Gate A (Session freshness): Read `agents/session.md` → compare → escalate if stale
- Gate B (Vet checkpoint): List changed files → classify → check for vet report → escalate if missing
- Validation: Run precommit/test/lint based on flags

**Design note:** Gates are merged into action steps with anchoring tool calls. No standalone prose-only gate steps.

---

## 8. Integration Points for Recipe → Skill Migration

### High-Impact Changes

**1. Bash allowed-tools specifications:**
If worktree operations move to skills, `allowed-tools` needs:
- `Bash(git worktree:*)`
- `Bash(git submodule:*)`
- `Bash(git branch:*)`
- `Bash(just wt-new:*)` OR direct git operations
- `Bash(direnv:*)` for worktree setup

**2. Sandbox exemption handling:**
Skills cannot directly set `dangerouslyDisableSandbox: true` per tool call. Two options:
- Add worktree recipes to `permissions.allow` in settings.json
- Skill delegates to Bash with explicit sandbox disable instruction in prompt
- Skills invoke `just wt-*` recipes which already have proper configuration

**3. focus-session.py script creation:**
Must implement missing script before `wt-task` skill can work. Script needs:
- Parse session.md to extract task by name
- Load plan context from plan directory (rca, requirements, design, problem, runbook files)
- Format focused session.md per execute-rule.md specification
- Output to stdout for capture

**4. Session.md manipulation:**
Mode 5 requires editing main session.md to move tasks between sections:
- Move task from `## Pending Tasks` to `## Worktree Tasks`
- Add `→ wt/<slug>` tracking marker
- Skills need Write/Edit permissions for agents/session.md

**5. Continuation protocol:**
Worktree skills likely terminal (no default-exit), but should support cooperative continuation:
```yaml
continuation:
  cooperative: true
  default-exit: []
```

### Medium-Impact Changes

**6. STATUS display integration:**
If `wt` command moves from Mode 5 to skill:
- Need STATUS display logic duplicated or factored into shared utility
- execute-rule.md MODE 1 STATUS format must align with skill output
- Clipboard copy requires `dangerouslyDisableSandbox: true`

**7. Parallel detection logic:**
Mode 5 parallel group flow requires:
- Read session.md Pending Tasks
- Read agents/jobs.md for plan status
- Check Blockers/Gotchas for dependencies
- Model tier and restart flag analysis
- This logic currently prose-specified, needs implementation

**8. Error handling patterns:**
Recipes use bash error handling (`set -euo pipefail`, visible command echoing).
Skills use explicit tool call error propagation and prose escalation rules.

### Low-Impact Changes

**9. Documentation updates:**
- execute-rule.md Mode 5 section → update to reference skill invocation
- sandbox-exemptions.md → add worktree skill patterns
- Shortcut vocabulary (execute-rule.md lines 191-212) → `wt` entry already exists

**10. Template references:**
- `agent-core/skills/handoff/references/template.md` already has Worktree Tasks section
- No changes needed unless format evolves

---

## 9. Current Worktree State (from session.md)

### Active Worktrees
One active: `../claudeutils-vet-fix-agent` (branch: `wt/vet-fix-agent`)

### Stale Worktrees
Four stale worktrees mentioned in session.md Blockers (line 115):
- `wt/bash-git-prompt`
- `wt/continuation-passing` (merged in this session)
- `wt/markdown-test-corpus`
- `wt/memory-index-recall`

**Cleanup needed:** `just wt-rm <slug>` for each stale worktree.

### Worktree Tasks in Session
From session.md (lines 103-105):
```markdown
## Worktree Tasks

- [ ] **Evaluate plugin migration** → `wt/plugin-migration` — Symlink situation causing pain
  - Plan: plugin-migration | Status: planned
```

---

## 10. wt-merge-skill Design Outline

### Location
`/Users/david/code/claudeutils/plans/wt-merge-skill/outline.md`

### Key Decisions (15 lines)
- **Clean tree gate:** Fail on non-session-context dirty files
- **Session context allowed dirty:** session.md, jobs.md, learnings.md
- **Full ceremony pre-merge:** `/handoff, /commit` via continuation chain
- **`--commit` flag obsolete:** Continuation passing replaces tail-call hack
- **Auto-resolve session conflicts:** Deterministic merge (keep both sides)
- **Post-merge cleanup:** Remove worktree task from session.md, amend merge commit, `just wt-rm`
- **Dependency:** Blocked on continuation-passing (NOW UNBLOCKED per session.md)

**Status:** Requirements-level design seed. Not yet expanded to full runbook.

---

## 11. Related Pending Tasks (from session.md)

### Directly Related
- **Package wt-merge as skill** (line 97)
  - Plan: wt-merge-skill | Status: requirements
  - Now unblocked (continuation-passing merged)

- **Move worktrees into wt/ directory** (line 100)
  - Solves sandbox isolation
  - Would update skills and scripts

- **Clean up merged worktrees** (line 101)
  - Remove 4 stale worktrees

### Indirectly Related
- **Update tool-batching.md for Task tool parallelization** (line 88)
  - Task tool is used in worktree execution flow

- **Strengthen vet-fix-agent delegation pattern** (line 78)
  - Worktree execution uses vet-fix-agent for checkpoints

---

## 12. Key Patterns and Conventions

### Slug Derivation
- Source: task name (prose)
- Transform: lowercase, replace spaces with hyphens
- Constraint: ≤30 characters
- No implementation found (currently prose-specified in execute-rule.md)

### Branch Lifecycle
1. Create: `git worktree add <dir> -b wt/<name> <base>`
2. Work: commits to `wt/<name>` in worktree
3. Merge: `just wt-merge <name>` (two-phase: submodule → parent)
4. Cleanup: `just wt-rm <name>` removes worktree + branch

### Submodule Handling
- Worktree init: `git submodule update --init --reference <main-dir>`
- Branch creation: `git checkout -b wt/<name>` in agent-core submodule
- Merge: Fetch from worktree submodule, merge to main submodule, then commit pointer
- Critical: `--reference` avoids remote fetch for unpushed commits

### Session Context Files
Three files with special merge treatment:
1. `agents/session.md`
2. `agents/jobs.md`
3. `agents/learnings.md`

These are allowed dirty during wt-merge and have deterministic conflict resolution (keep both sides).

---

## 13. Cross-Codebase References

### Files Referencing Worktree Operations (19 total)

**Core implementation:**
- `justfile` (5 recipes)
- `agent-core/fragments/execute-rule.md` (Mode 5 specification)
- `agent-core/skills/handoff/references/template.md` (Worktree Tasks format)

**Documentation:**
- `.cache/just-help.txt` (recipe help)
- `agents/session.md` (completed work, pending tasks, reference files)
- `agents/jobs.md` (wt-merge-skill status)
- `agents/learnings.md` (Git worktree submodule gotchas, wt-merge empty submodule failure)

**Plan artifacts (plugin-migration):**
- 7 files in `plans/plugin-migration/` (runbook, steps, reports, design)
- Shows real-world usage of worktree system

**Design artifacts:**
- `plans/wt-merge-skill/outline.md` (design seed)

### Learnings Entries

**agents/learnings.md has 2 worktree-related entries:**

1. **Git worktree submodule gotchas** (lines ~143-148)
   - Unpushed submodule commits require `--reference` flag
   - `git worktree remove` requires `--force` with submodules
   - Symlinks work with relative paths

2. **wt-merge empty submodule failure** (lines ~237-243)
   - `git commit` with nothing staged exits 1, kills script
   - Guard pattern: `git diff --quiet --cached || git commit`
   - Recipe success ≠ task success (verify git state after)

---

## 14. Missing Pieces Summary

### Critical
1. **focus-session.py script** — Referenced but does not exist
   - Blocks `just wt-task` functionality
   - Session.md claims it was created (ff056c7) but not in repo

### Important
2. **Slug derivation implementation** — Prose-specified only
   - Mode 5 needs slug generation logic
   - Currently manual or implicit

3. **Parallel group detection** — Algorithm prose-specified
   - STATUS display requires implementation
   - Mode 5 parallel flow needs detection logic

### Nice-to-Have
4. **wt-merge-skill implementation** — Design seed exists, runbook planned
   - Blocked on continuation-passing (now unblocked)
   - Would replace `just wt-merge` with skill

---

## 15. Recommendations for Skill Migration

### Phase 1: Foundation
1. **Implement focus-session.py** — Unblocks wt-task functionality
2. **Factor slug derivation** — Shared utility for Mode 5 and future skills
3. **Factor parallel detection** — Shared logic for STATUS and Mode 5

### Phase 2: Skill Extraction
4. **Create wt-setup skill** — Mode 5 single-task and parallel flows
5. **Create wt-merge skill** — Per existing design outline
6. **Create wt-cleanup skill** — Wraps wt-rm with safety checks

### Phase 3: Integration
7. **Update execute-rule.md** — Mode 5 references skills instead of prose
8. **Update sandbox-exemptions.md** — Document skill permission patterns
9. **Test with real worktrees** — Validate skill-based workflow

### Considerations
- **Keep recipes as fallback** — Skills invoke `just wt-*` internally for reliability
- **Settings.json integration** — Add worktree patterns to `permissions.allow`
- **Error handling parity** — Match recipe robustness (submodule checks, dirty tree warnings)

---

## Appendix: File Paths

All paths relative to `/Users/david/code/claudeutils/`.

**Core files:**
- `justfile` — 5 worktree recipes
- `agent-core/fragments/execute-rule.md` — Mode 5 + task conventions
- `agent-core/skills/handoff/references/template.md` — Worktree Tasks format
- `agent-core/bin/task-context.sh` — Context recovery script (exists)
- `agent-core/bin/focus-session.py` — Focus extraction script (MISSING)

**Session tracking:**
- `agents/session.md` — Active worktrees, pending tasks, reference files
- `agents/jobs.md` — Plan lifecycle tracking
- `agents/learnings.md` — Worktree-related learnings

**Design artifacts:**
- `plans/wt-merge-skill/outline.md` — Skill design seed

**Example skills:**
- `agent-core/skills/shelve/SKILL.md` — Terminal skill pattern
- `agent-core/skills/commit/SKILL.md` — Continuation-passing pattern
- `agent-core/skills/handoff/SKILL.md` — Full ceremony pattern
- `agent-core/skills/orchestrate/SKILL.md` — Orchestration pattern
