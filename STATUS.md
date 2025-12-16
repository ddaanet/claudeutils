# Project Status: Claude Code Feedback Extractor

**Last Updated:** 2025-12-16
**Session:** fluffy-cuddling-forest
**Phase:** Planning Complete - Ready for Implementation

## Current State

### Completed
- ✅ Explored Claude Code conversation history storage structure
- ✅ Identified data sources and entry formats
- ✅ Designed two-subcommand CLI architecture
- ✅ Created comprehensive TDD test plan (50+ test cases)
- ✅ Defined Pydantic data models with validation
- ✅ Extracted real sample data for tests

### Files Created
- `/Users/david/.claude/plans/fluffy-cuddling-forest.md` - Main plan file
- `/Users/david/code/claudeutils/PLAN.md` - Copy in project directory
- `/Users/david/code/claudeutils/USER_FEEDBACK_SESSION.md` - Collated user feedback
- `/Users/david/code/claudeutils/RESEARCH_FINDINGS.md` - Technical findings
- `/Users/david/code/claudeutils/STATUS.md` - This file

### Files to Create (Implementation)
- `main.py` - Core implementation (~120 lines)
- `test_main.py` - Pytest test suite (~200 lines)
- `pyproject.toml` - uv project config (~15 lines)

## Next Steps

### Step 1: Path Encoding & Session Discovery
**Functions to implement:**
- `encode_project_path(project_dir: str) -> str`
- `get_project_history_dir(project_dir: str) -> Path`
- `list_top_level_sessions(project_dir: str) -> list[SessionInfo]`

**Tests:** 10 test cases covering path encoding, session discovery, sorting

### Step 2: Trivial Filter
**Functions to implement:**
- `is_trivial(text: str) -> bool`

**Tests:** 9 test cases covering patterns, edge cases, case sensitivity

### Step 3: Message Parsing
**Functions to implement:**
- `extract_feedback_from_entry(entry: dict) -> FeedbackItem | None`

**Tests:** 9 test cases covering all feedback types, validation errors

### Step 4: Recursive Processing
**Functions to implement:**
- `find_sub_agent_sessions(session_file: Path) -> list[str]`
- `extract_feedback_recursively(session_id: str, project_dir: str) -> list[FeedbackItem]`

**Tests:** 6 test cases covering recursion, cycle detection, missing files

### Step 5: CLI Subcommands
**Functions to implement:**
- `main()` with subparsers for `list` and `extract`

**Tests:** 18 test cases covering both subcommands, error handling, integration

## Dependencies

```bash
uv add pytest pydantic
```

## CLI Usage (Planned)

```bash
# List all sessions in current project
python main.py list

# List sessions from specific project
python main.py list --project /path/to/project

# Extract feedback from session (by prefix)
python main.py extract e12d203f

# Extract with output to file
python main.py extract e12d203f --output feedback.json
```

## Key Design Decisions

1. **Pydantic BaseModel:** Type safety and validation instead of dataclasses
2. **Optional fields:** `agent_id`, `slug`, `tool_use_id` as Optional[str] instead of context dict
3. **Recursive processing:** Follow agent references to extract all feedback
4. **Two subcommands:** `list` for discovery, `extract` for extraction
5. **Test-first approach:** Write all tests before implementation

## Test Data Available

Real samples from conversation history:
- `SAMPLE_USER_MESSAGE` - Substantive user feedback
- `SAMPLE_TOOL_DENIAL_MAIN` - Tool denial in main session
- `SAMPLE_TOOL_DENIAL_SUBAGENT` - Tool denial in sub-agent with full context
- `SAMPLE_TRIVIAL` - Trivial message to filter out
- `SAMPLE_INTERRUPTION` - Request interruption

All samples in PLAN.md under "Test Data" section.

## Context for Next Session

**Goal:** Extract user feedback from Claude Code conversation history for retrospective analysis.

**Approach:** TDD with pytest, natural language test specifications first, then implementation.

**Current project:** `/Users/david/code/claudeutils`

**Start with:** Step 1 - Path encoding & session discovery tests and implementation.
