# Precommit Validation Infrastructure

**Summary:**
The precommit validation infrastructure is a multi-layer system combining CLI validators (in `claudeutils.validation`), justfile recipes, shell scripts, and Makefile targets. Entry points are the `just precommit` recipe and `claudeutils validate` CLI command, which orchestrate checks for session.md task names, learnings identifiers, decision file structure, jobs.md consistency, memory index alignment, file line limits, and code formatting.

## Validation Entry Points

### Primary Entry Points

1. **`just precommit` recipe** — `/Users/david/code/claudeutils-wt/worktree-fixes/justfile` (lines 22-33)
   - Orchestrates all precommit checks
   - Runs: `sync`, `claudeutils validate`, `gmake check`, `run-checks`, pytest, `run-line-limits`
   - Fails if any subprocess fails
   - Skipped tests cause failure: `grep -q "skipped"` blocks merge

2. **`claudeutils validate` CLI command** — `/Users/david/code/claudeutils/src/claudeutils/cli.py` (line 147)
   - Entry: `claudeutils validate` (with optional subcommand)
   - Delegates to `/Users/david/code/claudeutils/src/claudeutils/validation/cli.py`

3. **Agent-core precommit stub** — `/Users/david/code/claudeutils-wt/worktree-fixes/agent-core/justfile` (lines 100-101)
   - No-op: `@echo "✓ Precommit OK"`
   - Agent-core is documentation only

4. **Makefile cache check** — `/Users/david/code/claudeutils-wt/worktree-fixes/agent-core/Makefile` (line 21-22)
   - Target: `check` (runs `gmake -q all`)
   - Verifies cached justfile help is up-to-date
   - Exits 1 if stale, forces `just cache` rebuild

## Validation Checks by Category

### 1. Task Name Validation (session.md)

**Module:** `/Users/david/code/claudeutils/src/claudeutils/validation/tasks.py`

**Checks:**
- Format: `- [ ] **Task Name** —` (case-insensitive state: space, x, or >)
- Uniqueness within session.md (case-insensitive, case-preserving first occurrence)
- Disjointness with learning keys (no overlap with `## Headers` in learnings.md)
- Git history search for new tasks (prevents task name reuse)
- Merge commit handling (compares against both parents, constraint C-1)

**Key Functions:**
- `extract_task_names(lines)` → list of (line_number, task_name)
- `extract_learning_keys(lines)` → set of learning key strings
- `get_new_tasks(session_path)` → list of task names new to current commit
- `check_history(task_name)` → bool: exists in git history
- `validate(session_path, learnings_path, root)` → list[str] of errors

**Error Messages Example:**
```
  line 5: duplicate task name (first at line 2): **Task Name**
  line 7: task name conflicts with learning key: **Task Name**
  new task name exists in git history: **Task Name**
```

**Constraints Enforced:**
- C-1 (Merge commit constraint): A task is "new" only if absent from ALL parents (not just HEAD)
- Octopus merge detection: Exits 1 if >2 parents (requires augmentation)

### 2. Learnings File Validation

**Module:** `/Users/david/code/claudeutils/src/claudeutils/validation/learnings.py`

**Checks:**
- Title format: `## Title` (markdown header, 2nd level)
- Max word count: 5 words per title (configurable, default MAX_WORDS = 5)
- Uniqueness: no duplicate titles (case-insensitive)
- Non-empty: titles must have content

**Key Functions:**
- `extract_titles(lines)` → list of (line_number, title_text) from lines 11+ (skips 10-line preamble)
- `validate(path, root, max_words=5)` → list[str] of errors

**Error Messages Example:**
```
  line 42: title has 8 words (max 5): ## Behavioral triggers beat passive knowledge
  line 55: duplicate title (first at line 28): ## Design phase output optimization
```

### 3. Decision Files Validation

**Module:** `/Users/david/code/claudeutils/src/claudeutils/validation/decision_files.py`

**Checks:**
- Detects sections with no direct content (only sub-headings)
- Requires organizational sections to be marked with `.` prefix
- Content threshold: ≤2 substantive lines before first sub-heading → organizational
- Applies to: `agents/decisions/*.md` (configurable glob)

**Key Functions:**
- `parse_heading(line)` → (level, title, is_structural) | None
- `analyze_file(filepath)` → list of (line_number, heading_title, level)
- `validate(root)` → list[str] of errors

**Error Messages Example:**
```
  agents/decisions/workflow-core.md:15: section 'Planning Patterns' has no direct content
    Action required:
    A) Mark structural: '## .Planning Patterns'
    B) Add substantive content before sub-headings
```

**Hard Error:** No autofix (agent decides: add prefix or add content)

### 4. Jobs File Validation

**Module:** `/Users/david/code/claudeutils/src/claudeutils/validation/jobs.py`

**Checks:**
- Plans listed in jobs.md have corresponding directories or files in plans/
- All plan directories/files in plans/ are listed in jobs.md (except complete plans)
- Plans with status 'complete' are exempt from directory existence check
- Parses jobs.md Plans table: `| plan-name | status | notes |`

**Key Functions:**
- `parse_jobs_md(jobs_path)` → dict[plan_name, status]
- `get_plans_directories(plans_dir)` → set[plan_names]
- `validate(root)` → list[str] of errors

**Error Messages Example:**
```
Plan 'worktree-fixes' exists in plans/ but not in jobs.md
Plan 'workflow-fixes' in jobs.md (status: designed) but not found in plans/
```

**Scope:**
- Skips `plans/claude/` (gitignored, ephemeral plan-mode files)
- Skips `plans/README.md`
- Includes plan directories and .md file stems

### 5. Memory Index Validation

**Module:** `/Users/david/code/claudeutils/src/claudeutils/validation/memory_index.py`

**Checks:**
- All semantic headers (##+ not starting with .) have index entries
- All index entries match at least one semantic header
- No duplicate index entries
- Em-dash format: "Key — description"
- Word count: 8-15 words for entries (preamble lines exempt)
- Entries not pointing to structural sections
- Correct file section (autofixable)
- File order within sections (autofixable)

**Key Functions:**
- `extract_index_entries(index_path, root)` → dict[key_lower, (line_num, entry, section_name)]
- `validate(index_path, root, autofix=True)` → list[str] of errors
- Calls helpers: `check_duplicate_entries`, `check_em_dash_and_word_count`, `check_entry_placement`, `check_entry_sorting`, `check_structural_entries`, `check_orphan_entries`

**Autofix Capability:**
- Enabled by default in precommit
- Fixes: section placement, ordering, structural section cleanup
- Reports summary to stderr: "Autofixed X placement and Y ordering issues"

**Error Messages Example:**
```
  Duplicate header 'Planning as orchestratable DAG' found in multiple files:
    agents/decisions/workflow-core.md:156 (## level)
    agents/decisions/workflow-optimization.md:89 (## level)
  agents/decisions/pipeline-contracts.md:45: orphan semantic header 'Tier assessment' has no memory-index.md entry
```

### 6. File Line Limits

**Script:** `/Users/david/code/claudeutils-wt/worktree-fixes/scripts/check_line_limits.sh`

**Checks:**
- Python source files (src/, tests/) must not exceed 400 lines
- Markdown files in agents/decisions/ must not exceed 400 lines

**Error Messages Example:**
```
❌ src/claudeutils/validation/tasks.py: 310 lines (exceeds 400 line limit)
```

### 7. Code Style Checks

**Inline in justfile recipe `run-checks` function** (lines 576-580):
- `ruff check -q` — Linting
- `docformatter -c` — Docstring validation
- `mypy` — Type checking

**Error reporting:** Uses `report` function to capture and display output only if non-empty

### 8. Code Formatting

**Just recipe `format`** (lines 356-380):
- `ruff check --fix-only --diff` — Auto-fixable lint issues
- `ruff format --diff` — Code formatting
- `docformatter --diff` — Docstring formatting
- Collects modified files and reports summary

### 9. Pytest (Test Execution)

**In precommit recipe** (lines 29-31):
- Runs `pytest -q`
- Fails if any tests are skipped: grep for "skipped" text

## How New Validators Get Added

### Addition Process

1. **Create validation module** in `/Users/david/code/claudeutils/src/claudeutils/validation/`
   - File name: `<validator_name>.py`
   - Export function: `validate(... root: Path) -> list[str]`
   - Returns empty list if no errors, error strings otherwise

2. **Import in CLI** — `/Users/david/code/claudeutils/src/claudeutils/validation/cli.py`
   - Add import: `from claudeutils.validation.<module> import validate as validate_<name>`
   - Add to `_run_all_validators()` function:
     ```python
     _run_validator(
         "<validator_name>",
         validate_<name>,
         all_errors,
         # ... args to validator
     )
     ```
   - Register subcommand (optional):
     ```python
     @validate.command()
     def <name>() -> None:
         """Validate <thing>."""
         root = find_project_root(Path.cwd())
         errors = validate_<name>(root)
         # ... handle errors
     ```

3. **Integrate with precommit** — `/Users/david/code/claudeutils-wt/worktree-fixes/justfile`
   - If CLI-based: already runs via `claudeutils validate`
   - If script-based: add to `run-checks` or create new script
   - Add to recipe sequence in `precommit` (lines 25-32)

4. **Update cache** (if applicable)
   - Run `just cache` to rebuild help documentation

### Integration Points

- **CLI validators:** Automatically run via `claudeutils validate` (no changes needed to justfile)
- **Script validators:** Add to `run-checks` function or create new shell script
- **Custom checks:** Add directly to justfile recipe

## Session.md Format Validation

### Task Line Format

**Pattern:** `^- \[[ x>]\] \*\*(.+?)\*\* —`

**Examples (valid):**
```markdown
- [ ] **Task Name** — description | model
- [x] **Completed Task** — `command`
- [>] **In Progress** — notes
```

**Constraints:**
- Task name must be in bold: `**name**`
- Em-dash separator: ` — ` (space-em-dash-space)
- State: space (pending), x (completed), > (in-progress)
- No colons allowed in task names (would break parsing in learnings uniqueness check)

### New Task Detection in Merges

**Merge Constraint (C-1):**
- During merge commit: compares task list against BOTH parents
- A task is "new" only if present in current but absent from both parent1 AND parent2
- Prevents false positives when merging branches that independently added same task

**Implementation:** `get_new_tasks()` in tasks.py
- Regular commits: compare against HEAD only
- Merge commits: get both parents via `git rev-parse MERGE_HEAD` and `git rev-parse HEAD`
- Octopus merges (>2 parents): exits 1 with error message

## Validator Error Handling

### Pattern

**`_run_validator` function** (lines 16-33 in cli.py):
```python
def _run_validator(name, validator_func, all_errors, *args):
    try:
        errors = validator_func(*args)
        if errors:
            all_errors[name] = errors
    except (ValueError, FileNotFoundError, OSError) as e:
        all_errors[name] = [f"Error: {e}"]
```

**Behavior:**
- Catches exceptions for individual validators
- Collects errors by validator name
- Continues running all validators even if one fails
- Displays all errors at end with validator name header

### Error Reporting

**Format in CLI** (lines 84-89):
```
Error (validator_name):
  error message 1
  error message 2
Error (other_validator):
  another error
```

## Key Files Summary

| File | Purpose | Checks |
|------|---------|--------|
| `/Users/david/code/claudeutils/src/claudeutils/validation/cli.py` | Validator orchestration | N/A (delegates) |
| `/Users/david/code/claudeutils/src/claudeutils/validation/tasks.py` | Task name validation | Uniqueness, disjointness, history, merge handling |
| `/Users/david/code/claudeutils/src/claudeutils/validation/learnings.py` | Learning titles validation | Format, word count, uniqueness |
| `/Users/david/code/claudeutils/src/claudeutils/validation/decision_files.py` | Decision file structure | Organizational section markers |
| `/Users/david/code/claudeutils/src/claudeutils/validation/jobs.py` | Jobs.md consistency | Plan directory matching |
| `/Users/david/code/claudeutils/src/claudeutils/validation/memory_index.py` | Memory index alignment | Header-entry matching, sorting, autofix |
| `/Users/david/code/claudeutils/src/claudeutils/validation/common.py` | Shared utilities | Project root detection |
| `/Users/david/code/claudeutils-wt/worktree-fixes/justfile` | Precommit recipe orchestration | Calls: validate, checks, tests, line limits |
| `/Users/david/code/claudeutils-wt/worktree-fixes/scripts/check_line_limits.sh` | File line validation | 400-line limit for .py and agents/decisions/*.md |
| `/Users/david/code/claudeutils-wt/worktree-fixes/agent-core/Makefile` | Cache management | Justfile help output freshness |

## Precommit Execution Order

1. `sync` — Sync Python environment
2. `claudeutils validate` — All validators run (tasks, learnings, memory-index, decision-files, jobs)
3. `gmake -C agent-core check` — Verify cached justfile help is current
4. `run-checks` — ruff check, docformatter, mypy
5. `pytest -q` — Run tests (fail if any skipped)
6. `run-line-limits` — Check 400-line limit
7. `report-end-safe` — Print success/failure summary

**Exit Behavior:** First failure causes immediate exit (set -e), stops precommit chain

## Patterns for Task Name Constraints

### Current Constraints

1. **No special characters** — Task names are used as:
   - Git branch names (via `wt-new` recipe)
   - Search keys in `git log -S` (grep pattern matching)
   - Session.md parsing (regex: `\*\*(.+?)\*\*`)
   - Learning key disjointness check (case-insensitive match)

2. **No colons** — Parsing error in precommit metadata format: `Task Name — description | model`
   - Colon would break the `|` delimiter parsing

3. **Alphanumeric + spaces** — Recommended range: `[a-zA-Z0-9 ]`
   - Slug derivation (justfile line 63): `slug="{{name}}"`
   - Used directly as git branch name (no transformation)

4. **Lossy slug transformation** — Current pattern uses direct name as slug
   - Spaces → hyphens in git operations
   - Special characters → truncated or removed
   - Potential information loss: "Upstream plugin-dev: document \`skills:\` frontmatter" → truncated

### Validation Gap

**Issue:** No precommit validator currently enforces task name format constraints
- Only checks: uniqueness, disjointness, history
- Does NOT check: character set, reserved words, branch name validity

**Potential FR-1 Implementation:**
- Add character set validation in `tasks.py`
- Reject: special characters, colons, backticks, paths with slashes
- Validate: can be used as git branch name
- Call: `git check-ref-format --branch`

## Glossary

**Autofix:** Validator automatically fixes certain issues (memory-index placement/ordering only)
- Enabled by default in precommit
- Disabled for hard errors (decision-files, tasks, learnings, jobs)

**Constraint C-1:** Merge commit constraint for new task detection
- Tasks are "new" only if absent from BOTH parents
- Prevents false positives in worktree merges

**Hard Error:** Cannot be autofixed, requires agent decision
- Example: decision-files organizational section missing prefix or content

**Structural Section:** Decision file section marked with `.` prefix (e.g., `## .Planning`)
- Organizational grouping only, no direct content expected

## Validation Coverage Status

### Fully Validated

- Session.md task names (uniqueness, disjointness, history, merge handling)
- Learnings.md titles (format, word count, uniqueness)
- Decision files (organizational section markers)
- Jobs.md (plan directory matching)
- Memory index (header-entry alignment, sorting, autofix)
- File line limits (400 lines for .py and agents/decisions/*.md)
- Code style (ruff, mypy, docformatter)

### Partially Validated (Gaps Identified)

- Task name format (no character set validation for branch name safety)
- Session.md file structure (format validated per-task, not overall structure)
- Precommit skip detection (only checks test output for "skipped" keyword, not parametrization)

### Not Validated

- Session.md section headers (Pending Tasks, Worktree Tasks, etc. structure not checked)
- Metadata parsing (model, restart flags not validated)
- Blocking/Gotchas sections (free-form, no validation)
- Continuation lines in task metadata (session merge loses continuation)
