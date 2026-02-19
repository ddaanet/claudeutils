# Outline: Handoff CLI Tool

**Task:** Mechanical handoff+commit pipeline in CLI, following the worktree CLI pattern.

## Approach

New `handoff/` subpackage under `src/claudeutils/` exposed as `claudeutils _handoff` command group. Consolidates 5-10 separate Bash calls (git status, git diff, precommit, git add, git commit, learning-ages.py, _worktree ls) into structured commands with JSON output. Agent retains all judgment (what to write in session.md, learnings, commit message drafting). CLI handles mechanical execution and diagnostic gathering.

**Inputs to the CLI pipeline (FR-1):** The agent passes these to `_handoff commit` after completing its judgment work: commit message (drafted by agent), optional file list, optional gitmoji. Status line and completed text are session.md content — the agent writes them directly via Edit/Write, then calls CLI for the commit mechanical operations. The CLI does not receive status line or completed text as arguments.

**Outputs from CLI pipeline (FR-2):** Conditional on operation — `_handoff info` returns learnings age status + git status/diff + worktree ls; `_handoff commit` returns precommit result + commit hash.

## Commands

### `_handoff info`
Gather all diagnostic context in a single call. Returns JSON:
- Learning age report (wraps `learning-ages.py`)
- Consolidation trigger status (line count + active days)
- Git status (porcelain)
- Git diff stat (staged + unstaged)
- Worktree list (wraps `_worktree ls --porcelain`)

Agent calls this once, gets everything needed for judgment decisions.

### `_handoff gitmoji "commit message text"`
Select gitmoji via pre-computed embeddings + cosine similarity.
- Load 78 pre-computed gitmoji embedding vectors from JSON cache
- Embed commit message at runtime
- Cosine similarity ranking, return top match
- Output: `emoji\tname\tscore` (tab-separated for parsing)
- Fallback: keyword-based matching if embedding unavailable

### `_handoff commit --message "msg" [--files f1 f2 ...] [--gitmoji EMOJI]`
Execute commit pipeline:
1. Cache inputs to state file before attempting (enables resume on failure)
2. Run `just precommit`
3. Stage specified files (`git add`)
4. Prefix message with gitmoji if provided
5. Create commit (`git commit` with heredoc)
6. Verify clean tree
- Output: JSON `{hash, precommit_passed, precommit_output, git_status}`
- On success: delete state file
- On failure: leave state file populated, exit with semantic code

`git_status` in the success response contains porcelain output post-commit, satisfying the FR-2 requirement for conditional git status output from the commit pipeline.

### `_handoff resume [--state-file PATH]`
Replay commit from cached state:
- Load inputs from `tmp/.handoff-state.json`
- Re-execute commit pipeline from failure point
- Success: delete state file, return result
- Failure: update state file with new error

## Key Decisions

### D-1: Embedding approach for gitmoji

**Problem:** Need to match arbitrary commit messages to gitmoji categories without an LLM call. Task spec says "embeddings + cosine similarity over 78 pre-computed vectors." (Note: exploration confirms 77 entries in current gitmoji files — verify actual count before generating embeddings cache; "78" may include a locally-added entry.)

**Two-tier approach:**
- **Pre-computed vectors:** Generate offline using OpenAI `text-embedding-3-small` (one-time script, stored as JSON). Cheap ($0.02/M tokens), ~1536 dims × 78 entries = ~120KB file.
- **Runtime embedding:** Same model embeds the commit message. Single API call (~100ms).
- **Offline fallback:** Keyword-based scoring for environments without OpenAI key. Maps common verbs (fix, add, remove, refactor, test, docs) to gitmoji categories via hand-curated synonym groups. If no keyword matches, return the most general gitmoji (`✨ - sparkles`) as default rather than failing.

**Why not TF-IDF only:** Commit messages use different vocabulary than gitmoji descriptions ("Fix authentication null pointer" vs "Fix a bug"). Word overlap is poor. Neural embeddings capture semantic similarity.

**Why not sentence-transformers:** Heavy dependency (torch, transformers). Overkill for 78 categories.

**Dependency:** `openai>=1.0` (optional — offline fallback works without it). Pure Python cosine similarity (no numpy for 78 vectors).

### D-2: State caching

- Location: `tmp/.handoff-state.json`
- Contents: `{message, files, gitmoji, timestamp, last_error, step_reached}`
- `step_reached` values: `"precommit"`, `"stage"`, `"commit"`, `"verify"` — `resume` starts from the failed step
- Created on commit pipeline failure (precommit fail, git error)
- `resume` reads and replays from `step_reached`
- Success: file deleted
- Agent doesn't re-enter handoff skill on retry — calls `_handoff resume` directly

### D-3: Output format

Commands with structured results return JSON to stdout. Simple single-value commands use tab-separated output (matching worktree pattern). Errors always go to stderr. Semantic exit codes (0=success, 1=error, 2=guard/validation, 3=conflict).

| Command | Output format | Rationale |
|---------|---------------|-----------|
| `_handoff info` | JSON | Multi-field result |
| `_handoff gitmoji` | `emoji\tname\tscore` (tab-separated) | Simple single match, matches worktree tab-sep convention |
| `_handoff commit` | JSON | Multi-field result including precommit output |
| `_handoff resume` | JSON | Same as commit |

### D-4: Session.md stays in skill

CLI does NOT write session.md. Agent writes session.md via Edit/Write (judgment about content, structure, carry-forward). CLI only provides diagnostic info (learning ages, git status) and executes commits.

### D-5: Package structure

```
src/claudeutils/handoff/
├── __init__.py
├── cli.py            # Click command group (_handoff)
├── commit.py         # Commit pipeline + state caching
├── context.py        # Diagnostic info gathering (info command)
├── gitmoji.py        # Embedding-based selection + keyword fallback
└── data/
    └── gitmoji-embeddings.json   # Pre-computed vectors (generated offline, shipped with package)

src/claudeutils/cli.py            # MODIFIED: add_command(handoff) registration

scripts/
└── generate-gitmoji-embeddings.py  # One-time vector generation (dev-only, not shipped)
```

`generate-gitmoji-embeddings.py` runs once during development to populate `gitmoji-embeddings.json`. It is not invoked at runtime and not distributed. It reads `agent-core/skills/gitmoji/cache/gitmojis.txt`, calls OpenAI embeddings API, and writes the JSON cache.

## Open Questions

1. **OpenAI as optional dependency?** Adding `openai` to `[project.optional-dependencies]` keeps the core package lightweight. The offline keyword fallback ensures the tool works without it. **Recommendation:** Use optional dependency. The project currently has no heavy runtime deps (6 packages, no numpy); keeping `openai` optional preserves that. Keyword fallback plus a shipped pre-computed cache means runtime embedding is needed only for novel commit messages not covered by the keyword set. Confirm with user if runtime embedding quality matters vs. pure offline operation.

2. **Embedding cache location:** `src/claudeutils/handoff/data/` (shipped with package) vs `agent-core/skills/commit/cache/` (co-located with gitmoji index)? **Recommendation:** `src/claudeutils/handoff/data/` — package data is portable across installs. The gitmoji index in agent-core is the *source*; the embeddings cache is a *derived artifact* suited to the package. When the gitmoji index updates, regenerate the cache via `scripts/generate-gitmoji-embeddings.py`.

3. **Submodule commit handling:** Should `_handoff commit` handle the agent-core submodule commit flow? **Decision:** No — submodule handling requires judgment about what changed and whether the change warrants a pointer bump. This stays in the skill. `_handoff commit` operates on the parent repo only. Skill remains responsible for detecting modified submodules and deciding whether to commit them first.

## Scope

**IN:**
- `handoff/` subpackage with 4 CLI commands
- Gitmoji embedding infrastructure (pre-compute script + runtime selection)
- State caching for commit retry
- Tests (CliRunner pattern, mock git repos)
- Registration in main `cli.py`

**OUT:**
- Skill modifications (handoff/commit skills updated in separate task)
- Consolidation delegation (already exists in skill)
- Session.md writing logic (stays in skill)
