# Source Code Exploration: Gitmoji and Package Structure

**Date:** 2026-02-19

## Summary

The `claudeutils` package is a CLI tool for managing Claude Code sessions with 8 major subcommands organized as Click command groups across separate modules. The codebase uses Pydantic for validation and Click for CLI, with 127 test files testing 8 core packages. No embedding or cosine similarity code exists in the main codebase; gitmoji data is pre-computed and stored in text files within agent-core skills. The package has no numpy or sklearn dependencies.

---

## Key Findings

### 1. Package Structure (`src/claudeutils/`)

**Root Level Modules** (27 Python files at `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/`):

- `__init__.py` — Version export via importlib.metadata
- `cli.py` — Main entry point with 7 top-level commands + 8 subcommand groups
- `models.py` — Pydantic data models (FeedbackType enum, SessionInfo, FeedbackItem)
- `paths.py` — Path encoding for Claude history directories
- `exceptions.py` — Custom exception definitions
- `parsing.py` — Markdown/text parsing utilities
- `extraction.py` — Feedback extraction from sessions
- `filtering.py` — Feedback filtering and categorization
- `discovery.py` — Session listing and discovery
- `markdown.py` — Markdown processing orchestration
- `markdown_*.py` — Specialized markdown fixers (3 files: block_fixes, inline_fixes, list_fixes)
- `markdown_parsing.py` — Markdown parsing utilities
- `compose.py` — YAML-based fragment composition
- `tokens.py` — Token counting via Anthropic API
- `tokens_cli.py` — CLI wrapper for token counting
- `validation/` — Session and project validation (subpackage, 8 modules)
- `account/` — Account/credential management (subpackage, 5 modules)
- `model/` — Model selection and config (subpackage, 3 modules)
- `worktree/` — Git worktree operations (subpackage, 7 modules)
- `recall/` — Memory index recall analysis (subpackage, 7 modules)
- `statusline/` — Status line generation (subpackage, 5 modules)
- `when/` — Memory index fuzzy search (subpackage, 5 modules)
- `planstate/` — Plan state inference (subpackage, 4 modules)

**Total Python source files:** 88 in src/

### 2. CLI Entry Points

**Main command group** (`cli.py:main`):
- Entry point: `claudeutils = "claudeutils.cli:main"`
- Root help: "Extract feedback from Claude Code sessions"

**Top-level commands in `cli.py`:**
1. `list` — List top-level sessions
2. `extract` — Extract feedback from single session (by prefix)
3. `collect` — Batch collect feedback from all sessions
4. `analyze` — Analyze and categorize feedback
5. `rules` — Extract rule-worthy feedback items
6. `tokens` — Count tokens via Anthropic API
7. `compose` — Compose markdown from YAML config
8. `markdown` — Process markdown files

**Subcommand groups** (added via `cli.add_command()`):
- `account` — Account status, plan mode management
- `model` — Model selection and configuration
- `recall` — Memory index recall analysis
- `statusline` — Session status line generation
- `validate` — Project validation (learnings, memory-index, tasks, decisions, planstate, session-refs, session-structure)
- `when_cmd` — Fuzzy memory index search ("when"/"how" directives)
- `worktree` — Git worktree operations (ls, new, rm, merge, focus-session)

### 3. Gitmoji Data and Files

**Gitmoji data locations:**

| Path | File Count | Size | Content |
|------|------------|------|---------|
| `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/skills/gitmoji/cache/gitmojis.txt` | 1 | 77 lines | All 77 pre-computed gitmoji entries (emoji - name - description) |
| `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/skills/commit/references/gitmoji-index.txt` | 1 | 77 lines | Identical to gitmojis.txt |

**Gitmoji Format (example):**
```
🎨 - art - Improve structure / format of the code.
⚡️ - zap - Improve performance.
🔥 - fire - Remove code or files.
...
🤖 - robot - Add or update agent skills, instructions, or guidance
```

**Gitmoji Update Scripts:**
- `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/skills/gitmoji/scripts/update-gitmoji-index.sh`
- `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/skills/commit/scripts/update-gitmoji-index.sh`

**Embedding References:**
- Session note in `agents/session.md` line 12: "Gitmoji: embeddings + cosine similarity over 78 pre-computed vectors"
- No embedding vectors or cosine similarity code exists in src/ yet (design phase)

### 4. Data Models

**Core Pydantic Models** (`models.py`):
```python
FeedbackType(StrEnum):
  - TOOL_DENIAL
  - INTERRUPTION
  - MESSAGE

SessionInfo(BaseModel):
  - session_id: str
  - title: str
  - timestamp: str

FeedbackItem(BaseModel):
  - timestamp: str
  - session_id: str
  - feedback_type: FeedbackType
  - content: str
  - agent_id: str | None
  - slug: str | None
  - tool_use_id: str | None
```

### 5. Tests Directory Structure

**Test Organization** (`/Users/david/code/claudeutils-wt/handoff-cli-tool/tests/`):
- Total: 127 Python test files
- Fixture files: `conftest.py`, `fixtures/`, `fixtures_worktree.py`, `pytest_helpers.py`
- Manual tests: `manual/` directory
- Test categories:
  - CLI tests: `test_cli_*.py` (10+ files testing main CLI commands)
  - Account tests: `test_account_*.py` (5 files)
  - Validation tests: `test_validation_*.py`, `test_planstate_*.py`, `test_worktree_*.py`
  - Parsing/extraction: `test_parsing.py`, `test_extraction_*.py`, `test_recall_*.py`
  - Markdown: `test_markdown_*.py` (3 files)
  - Segments/composition: `test_segments.py`, `test_compose.py`
  - Worktree operations: `test_worktree_*.py` (7+ files for merge, validation, errors)
  - Special: `test_when_fuzzy.py` (memory index fuzzy search)

**Test markers:**
- `e2e` — End-to-end tests requiring API credentials (marked with `pytest.mark.e2e`, excluded by default in `pyproject.toml`)

### 6. Dependencies

**Runtime dependencies** (`pyproject.toml` lines 7-14):
```python
"anthropic>=0.75.0"      # Anthropic API client (for token counting)
"click>=8.3.1"           # CLI framework
"platformdirs>=4.5.1"    # Platform-specific directory discovery
"pydantic>=2.0"          # Data validation
"pyyaml>=6.0"            # YAML config parsing
"socksio>=1.0.0"         # SOCKS proxy support
```

**Development dependencies** (dev group):
- mypy, ruff (linting/type checking)
- pytest, pytest-mock, pytest-markdown-report (testing)
- types-pyyaml (type stubs)

**Notable absences:**
- No numpy, scipy, or scikit-learn (no numerical computing)
- No embedding libraries (sentence-transformers, openai embeddings, etc.)
- No existing vector similarity code

### 7. Scripts Directory

**Location:** `/Users/david/code/claudeutils-wt/handoff-cli-tool/scripts/`

**Contents:**
| File | Purpose |
|------|---------|
| `check_line_limits.sh` | Validate line length limits in codebase |
| `scrape-validation.py` | Extract validation rules/patterns (17.6 KB) |

### 8. Skills Directory

**Location:** `/Users/david/code/claudeutils-wt/handoff-cli-tool/skills/`

**Contents:**
- `skill-shelf.md` (1.78 KB) — Catalog of available skills

Note: Primary skills are in `agent-core/skills/` (agent-core is a git submodule)

### 9. Code Organization Patterns

**Subpackage Pattern (repeated across 8 packages):**
```
package/
  __init__.py        # Public API exports
  cli.py            # Click command group(s)
  models.py         # Pydantic models (if needed)
  validation.py     # Core logic (naming varies)
  helpers.py        # Utilities
```

**CLI Pattern (all Click-based):**
- `@click.group()` for command groups
- `@click.command()` for individual commands
- `@click.option()` / `@click.argument()` for parameters
- Commands added via `cli.add_command(group)` in main

**Data Flow Pattern:**
1. Extract from session JSON
2. Filter/categorize using Pydantic models
3. Output as JSON or markdown
4. Optional write to file

### 10. Search Results

**Embedding/Cosine/Vector Search:**
- No matches in `src/` directory (confirmed via grep)
- Only reference: session note mentioning planned embeddings

**Gitmoji References:**
- No gitmoji code in `src/`
- Data files only: agent-core skills (pre-computed 77-entry list)
- No selection/similarity logic implemented

---

## Patterns & Architecture

**Design Principles:**
1. **Modular subpackages** — Each domain (account, validation, worktree) is isolated with its own CLI, models, and logic
2. **Pydantic-first validation** — All data models use Pydantic for runtime validation and serialization
3. **Click CLI framework** — Consistent CLI interface across all subcommands
4. **Composition-based output** — Markdown generation via YAML-driven fragment composition
5. **Session-centric** — All features revolve around Claude session JSONL files stored in `~/.claude/projects/[encoded-path]/`

**Testing Strategy:**
- Pytest with fixtures for session/worktree setup
- 127 test files covering all major modules
- E2E tests marked separately and excluded by default
- Helpers and manual test support

**Dependency Philosophy:**
- Minimal runtime dependencies (6 packages)
- API-driven where possible (Anthropic for token counting)
- No heavy numerical libraries

---

## Gaps & Unresolved Questions

1. **Gitmoji embeddings** — Planned in session.md ("embeddings + cosine similarity over 78 pre-computed vectors") but not yet implemented
2. **Embedding library choice** — Not specified; candidates: sentence-transformers, openai, anthropic embeddings, or custom vectors
3. **Vector storage** — Whether to compute on-demand or pre-cache vectors in data files
4. **Similarity threshold** — No documented criteria for "close enough" gitmoji match
5. **Integration point** — Unknown which CLI command or skill will use gitmoji selection
6. **Alternative commands** — No existing `/gitmoji` or gitmoji-related CLI commands in src/

---

## File References

**Absolute paths for key files:**

| Module | Primary Files |
|--------|---------------|
| CLI Core | `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/cli.py` |
| Models | `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/models.py` |
| Paths | `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/paths.py` |
| Worktree | `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/worktree/cli.py` |
| Validation | `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/validation/cli.py` |
| Account | `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/account/cli.py` |
| Recall | `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/recall/cli.py` |
| When | `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/when/cli.py` |
| Statusline | `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/statusline/cli.py` |
| Config | `/Users/david/code/claudeutils-wt/handoff-cli-tool/pyproject.toml` |
| Gitmoji Data | `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/skills/gitmoji/cache/gitmojis.txt` |
| Tests | `/Users/david/code/claudeutils-wt/handoff-cli-tool/tests/` (127 files) |
