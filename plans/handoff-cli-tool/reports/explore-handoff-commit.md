# Exploration: Handoff and Commit Skills — Mechanical Operations Analysis

## Summary

The `/handoff` and `/commit` skills handle a mix of judgment and mechanical operations. Handoff is primarily judgment-based (learnings analysis, context preservation decisions), while commit is mechanically intensive (git operations, gitmoji selection via embeddings). A CLI tool can extract mechanical operations: status computation, git state access, learning age analysis, and gitmoji selection via pre-computed embedding vectors. State caching on failure and continuation passing integration are key design patterns to preserve.

## Key Findings

### 1. Handoff Skill: `/agent-core/skills/handoff/SKILL.md`

**Judgment vs. Mechanical Split:**

| Task | Type | Details |
|------|------|---------|
| Gather context | Judgment | Review conversation for completed/pending tasks, identify blockers |
| Update session.md structure | Mechanical | Write 7 sections in fixed format, preserve carry-forward sections |
| Mark task status | Mechanical | Mark `[x]`, `[!]`, `[✗]`, `[–]` based on classification |
| Write learnings | Judgment | Decide what qualifies as learnings, formulate anti-pattern + correct pattern |
| Check invalidated learnings | Judgment | Assess whether prior learnings now false |
| Calculate learning ages | Mechanical | Run `agent-core/bin/learning-ages.py`, parse output |
| Check consolidation trigger | Mechanical | Compare file line count (≤150) + calculate days since consolidation |
| Update plan-archive.md | Mechanical | Append H2 heading + 2-4 sentence summary (after learnings written) |
| Trim completed tasks | Mechanical | Delete tasks if completed before conversation AND committed |
| Display STATUS | Mechanical | Format pending/worktree tasks per execute-rule.md MODE 1 |

**Mechanical Operations Extractable to CLI:**
- Learning age calculation (`learning-ages.py` already exists — computes git blame + active days)
- Consolidation trigger check (line count + consolidation date comparison)
- Learning invalidation detection (grep prior learnings against commit messages or file changes)
- Task status formatting for display
- Carry-forward section preservation validation (ensuring no data loss during merge)

**Key Operations:**
- `agent-core/bin/learning-ages.py` — Calculates git-active-day age per learning entry
  - Uses `git blame` to find line addition date
  - Uses `git log --since=<date>` to count unique commit dates
  - Detects last consolidation by searching for removed H2 headers in git log
  - Returns markdown report with age summary

### 2. Commit Skill: `/agent-core/skills/commit/SKILL.md`

**Judgment vs. Mechanical Split:**

| Task | Type | Details |
|------|------|---------|
| Vet gate (check vet reports exist) | Judgment | Decide if changes warrant vet, check for UNFIXABLE issues |
| Run precommit validation | Mechanical | `just precommit` (or `--test`, `--lint`) |
| Classify changed files | Judgment | Determine if changes are production artifacts, trivial vs non-trivial |
| Draft commit message | Judgment | Analyze semantics, write imperative-mood message |
| Select gitmoji | Mechanical/Semantic | Read index, match message semantics to emoji (can be automated) |
| Stage files | Mechanical | `git add <specific files>` |
| Create commit | Mechanical | `git commit -m "..."` with heredoc message |
| Verify clean tree | Mechanical | `git status --porcelain` check |
| Display STATUS | Mechanical | Format next pending task, show on clipboard |

**Mechanical Operations Extractable to CLI:**
- Gitmoji selection via embeddings (session.md mentions: "embeddings + cosine similarity over 78 pre-computed vectors")
- Running precommit validation (`just precommit`)
- Staging files (`git add`)
- Creating commits (`git commit`)
- Verifying git tree state (`git status --porcelain`)
- Identifying changed files (`git diff --name-only`)
- Submodule pointer detection and handling

**Gitmoji Index:**
- Location: `agent-core/skills/commit/references/gitmoji-index.txt` (78 entries)
- Format: `emoji - name - description` (e.g., `🐛 - bug - Fix a bug.`)
- Current approach: Skill reads index, applies semantic matching judgment
- CLI Opportunity: Pre-compute embeddings for each gitmoji description, store in `gitmoji-embeddings.json`, use cosine similarity to find best match
- Session.md specifies: "Gitmoji: embeddings + cosine similarity over 78 pre-computed vectors" (design decision already documented)

### 3. Handoff-Haiku Skill: `/agent-core/skills/handoff-haiku/SKILL.md`

**Mechanical-only operations:**
- Review conversation for completed/pending items
- Update session.md sections (REPLACE vs MERGE semantics)
- Preserve sections not touched
- Report completion with line count

**Different from full handoff:**
- NO learnings judgment (raw Session Notes section instead)
- NO learning age calculation
- NO consolidation checks
- NO plan-archive.md updates
- Mechanical merge-only (copy Pending, carry forward Blockers)

**CLI Extraction:** All operations are mechanical — ideal for CLI without judgment gates.

### 4. Learning Age Status Mechanism: `agent-core/bin/learning-ages.py`

**Already a mechanical standalone script:**

```python
# Calculates per-entry age
- Extract H2 headers from learnings.md (skip first 10 lines)
- For each header, use git blame to find commit date
- Calculate active days (unique commit dates) since addition
- Detect last consolidation by looking for removed H2 headers in git log
- Return markdown report

Key outputs:
- File lines: total line count
- Last consolidation: date + active days ago (or N/A)
- Total entries: count
- Entries ≥7 active days: count (consolidation trigger)
- Per-entry table: title | active days | addition date
```

**CLI Integration:** This script can be directly called by CLI tool, output parsed to check consolidation trigger (line count OR ≥14 active days).

### 5. State Caching on Failure

**Design Pattern from session.md:**

```
Handoff CLI tool inputs: status line, completed text, optional files, optional commit message with gitmoji
Cache on failure: inputs to state file, rerun without re-entering skill
```

**Implementation Strategy:**
- Before attempting handoff/commit, serialize inputs to `tmp/.handoff-state.json`:
  ```json
  {
    "status_line": "...",
    "completed_text": "...",
    "optional_files": [...],
    "optional_commit_message": "...",
    "gitmoji": "optional"
  }
  ```
- On failure (e.g., git conflict, precommit failure), state file persists
- On retry, CLI can reload state without re-prompting user
- On success, delete state file
- Agent can invoke CLI with `--load-state tmp/.handoff-state.json` to continue from saved inputs

### 6. Continuation Passing Integration

**From `agent-core/fragments/continuation-passing.md`:**

**Current chain:**
- `/handoff --commit` tail-calls `/commit` (hardcoded in skill YAML)
- `/commit` is terminal (no default-exit)

**New CLI Pattern:**
- Skill invokes: `claudeutils handoff [args] [CONTINUATION: /commit]`
- CLI executes handoff, returns status
- Skill reads return status, continues chain if needed
- Explicit continuation passing replaces hardcoded tail-calls

**Benefits:**
- Skill logic moves to CLI (mechanical)
- Agent retains judgment gates only
- Continuation can be parameterized (`--commit`, `--no-commit`)
- State caching at CLI boundary prevents re-work

### 7. Existing CLI Structure: Worktree Pattern

**From `src/claudeutils/worktree/cli.py`:**

**Pattern:**
```python
@click.group(name="_worktree")
def worktree() -> None:
    """Worktree commands."""

@worktree.command()
@click.option("--porcelain", is_flag=True)
def ls(*, porcelain: bool) -> None:
    """List worktrees and main tree."""
    # Implementation with subprocess calls
```

**Applicable to handoff/commit:**
- `_handoff` subcommand group
- `update-session` subcommand (mechanical update, carry-forward sections)
- `validate-learnings` subcommand (check invalidation)
- `learning-ages` subcommand (wrap learning-ages.py)
- `select-gitmoji` subcommand (embedding-based selection)

### 8. Gitmoji Selection via Embeddings

**Current in commit skill:**
- Reads 78-entry gitmoji index (small, efficient)
- Applies semantic judgment: direct alignment → secondary: urgency/scope

**CLI Enhancement:**
- Pre-compute embeddings for each gitmoji description using small embedding model (can use OpenAI, local sentence-transformers, or pre-computed vectors)
- Store in `agent-core/skills/commit/cache/gitmoji-embeddings.json`:
  ```json
  {
    "entries": [
      {"emoji": "🐛", "name": "bug", "description": "Fix a bug.", "embedding": [0.1, -0.2, ...]},
      ...
    ]
  }
  ```
- CLI tool `select-gitmoji <commit-message>` uses cosine similarity:
  - Embed the commit message
  - Compute cosine similarity to all 78 gitmoji embeddings
  - Return top match + confidence score
  - Skill can verify reasonableness (e.g., confidence > 0.7)

**Session.md design decision already present:**
> "Gitmoji: embeddings + cosine similarity over 78 pre-computed vectors"

This indicates the design is already settled — CLI tool should implement it.

## Patterns

### Session.md Structure Preservation

**Carry-forward rule:** Pending Tasks, Worktree Tasks sections are accumulated data. Do NOT rewrite.

**Mechanical validation for CLI:**
- Read current session.md, extract Pending Tasks section
- After updates, verify no items were lost
- Report if items were merged/deleted (helps agent debug)

### Split Between Judgment and Mechanical

**Handoff skill pattern:**
1. Agent: Gather context (judgment)
2. CLI: Update session.md (mechanical)
3. Agent: Review + approve changes (judgment)
4. CLI: Learning age check, consolidation trigger (mechanical)
5. Agent: Write learnings (judgment)
6. CLI: Update plan-archive, trim tasks (mechanical)

**Commit skill pattern:**
1. Agent: Vet gate check (judgment)
2. CLI: Run precommit (mechanical)
3. Agent: Draft message (judgment)
4. CLI: Gitmoji selection (mechanical via embeddings)
5. CLI: Git operations (mechanical)
6. CLI: Display STATUS (mechanical)

### Precommit-First Gate

Both skills use precommit validation as a gate before proceeding. From commit skill:
> "If precommit fails → STOP. Do not rationalize failures."

CLI should expose precommit validation as a reusable check that agents can call.

### State Caching Context

From session.md task description:
- Inputs: status line, completed text, optional files, optional commit message with gitmoji
- Outputs (conditional): learnings age status, precommit result, git status+diff, worktree ls
- Cache on failure: inputs to state file, rerun without re-entering skill

**Failure scenarios:**
- Git merge conflicts during commit
- Precommit validation failures (lint, tests)
- Missing vet reports (user must fix before retry)
- Network errors during gitmoji embedding lookup

**Recovery:** CLI maintains state file, agent can resume without re-entering skill logic.

## Gaps

1. **Embeddings Implementation:** Session.md specifies embeddings + cosine similarity, but no implementation exists yet. Requires:
   - Choice of embedding model (OpenAI API, sentence-transformers, or pre-computed vectors)
   - Pre-computed embedding cache (gitmoji-embeddings.json)
   - Cosine similarity computation (numpy or pure Python)
   - Embedding for user's commit message at runtime

2. **Learning Invalidation Detection:** No mechanism exists to detect when prior learnings become false after changes to enforcement or rules. Currently relies on agent judgment.

3. **Session.md Carry-Forward Validation:** No CLI check prevents accidental data loss when merging Pending Tasks. Could add `--verify-carry-forward` flag to validate preservation.

4. **Consolidated Continuation Passing:** Handoff currently hardcodes `--commit` flag. Explicit continuation passing (per continuation-passing.md) not yet implemented in handoff/commit skills.

5. **Submodule Handling:** Commit skill has submodule detection (show modified submodules), but no CLI tool exists to check/fix submodule state.

6. **Gitmoji Index Updates:** Script exists (`agent-core/skills/commit/scripts/update-gitmoji-index.sh`) but not integrated into CLI. Could be a separate `update-gitmoji` command.

## Recommendations for CLI Tool

**Phase 1: Core Mechanical Operations**
1. `claudeutils handoff update-session` — Update session.md with sections (REPLACE/MERGE semantics)
2. `claudeutils handoff learning-ages` — Wrap learning-ages.py, output age report
3. `claudeutils handoff consolidation-check` — Check trigger (line count + days since consolidation)
4. `claudeutils commit gitmoji-select` — Select emoji via embeddings (requires embedding implementation)
5. `claudeutils commit validate` — Run precommit checks, report result
6. `claudeutils commit create` — Stage files + create commit (wraps git operations)

**Phase 2: State Caching**
1. Add `--state-file` parameter to handoff + commit subcommands
2. Serialize inputs before attempting operations
3. On failure, leave state file; on success, delete it
4. Skill can invoke CLI with `--load-state` to continue from saved inputs

**Phase 3: Integration**
1. Implement embedding-based gitmoji selection (OpenAI embeddings or sentence-transformers)
2. Pre-compute and cache 78 gitmoji vectors
3. Add continuation passing support (explicit `[CONTINUATION: ...]` parameter)
4. Update handoff/commit skills to invoke CLI for mechanical operations

**Reference:** `src/claudeutils/worktree/cli.py` shows the pattern for subcommand groups and subprocess integration.

## Files Referenced

**Skills:**
- `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/skills/handoff/SKILL.md` (160 lines)
- `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/skills/commit/SKILL.md` (134 lines)
- `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/skills/handoff-haiku/SKILL.md` (122 lines)
- `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/skills/gitmoji/SKILL.md` (81 lines)

**Scripts & Indexes:**
- `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/bin/learning-ages.py` (220 lines)
- `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/skills/commit/references/gitmoji-index.txt` (78 entries)
- `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/skills/commit/scripts/update-gitmoji-index.sh`

**Decision Documents:**
- `/Users/david/code/claudeutils-wt/handoff-cli-tool/agents/decisions/workflow-optimization.md` (294 lines) — Handoff+commit chain, design workflow gates
- `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/fragments/commit-delegation.md` (298 lines) — Commit delegation pattern, orchestrator/agent split
- `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/fragments/continuation-passing.md` (140 lines) — Continuation passing protocol, cooperative skills
- `/Users/david/code/claudeutils-wt/handoff-cli-tool/agents/session.md` — Handoff CLI tool task specification (inputs/outputs/caching)

**Existing CLI Pattern:**
- `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/worktree/cli.py` (200+ lines) — Subcommand structure, mechanical operations pattern
