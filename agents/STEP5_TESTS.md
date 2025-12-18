# Step 5 Tests: CLI Subcommands

## Objective

Implement CLI interface with two subcommands:
- `list` - Display top-level sessions with titles
- `extract` - Extract feedback recursively from a session

## TDD Iteration Rules

**CRITICAL:** Each test must require writing NEW code. If a test passes without adding code, the test sequence is wrong.

**Enforcement:**
1. Write test N
2. Run it - must FAIL
3. Write MINIMAL code to pass test N only
4. Test N passes, but test N+1 must still fail
5. Move to test N+1

---

## CLI Interface Design

### Command Structure

```bash
claudeutils list [--project PATH]
claudeutils extract SESSION_PREFIX [--project PATH] [--output FILE]
```

### Implementation Notes

Use `argparse` for CLI parsing:
- Main parser with subcommands
- Default project: current working directory (`os.getcwd()`)
- Session prefix matching: partial UUID match from start

---

## Test Cases (18 tests)

### Group A: CLI Setup & Argument Parsing (Tests 1-3)

#### Test 1: `test_cli_no_args_shows_usage`
**Given:** CLI invoked with no arguments
**When:** `main()` is called with `sys.argv = ["claudeutils"]`
**Then:** Exits with code 2 (argparse default) or shows help message

**Implementation scope:**
- Create ArgumentParser with description
- Add subparsers for "list" and "extract"
- Parser requires subcommand (no subcommand = error)
- Does NOT require: actual command implementation

**Implementation hint:**
```python
import argparse

def main() -> None:
    parser = argparse.ArgumentParser(description="Extract feedback from Claude Code sessions")
    subparsers = parser.add_subparsers(dest="command", required=True)
    # Add subcommands (next tests)
    args = parser.parse_args()
```

---

#### Test 2: `test_list_command_default_project`
**Given:** Current working directory is `/tmp/test-project`
**When:** CLI invoked with `["claudeutils", "list"]`
**Then:** Calls `list_top_level_sessions("/tmp/test-project")`

**Implementation scope:**
- Add "list" subparser
- Add optional `--project` argument
- If `--project` not provided, use `os.getcwd()`
- Call existing `list_top_level_sessions()` function
- Does NOT require: output formatting

**Implementation hint:**
```python
list_parser = subparsers.add_parser("list", help="List top-level sessions")
list_parser.add_argument("--project", default=os.getcwd(), help="Project directory")
```

---

#### Test 3: `test_list_command_with_project_flag`
**Given:** User specifies `--project /custom/path`
**When:** CLI invoked with `["claudeutils", "list", "--project", "/custom/path"]`
**Then:** Calls `list_top_level_sessions("/custom/path")`

**Implementation scope:**
- Parse `--project` argument value
- Pass to `list_top_level_sessions()`
- Does NOT require: output formatting, error handling

---

### Group B: List Command Output (Tests 4-8)

#### Test 4: `test_list_output_format`
**Given:** History with one session:
- `session_id`: "e12d203f-ca65-44f0-9976-cb10b74514c1"
- `title`: "Design a python script"
- `timestamp`: "2025-12-16T08:39:26.932Z"

**When:** `list` command is run
**Then:** Prints to stdout: `[e12d203f] Design a python script`

**Implementation scope:**
- Format output as `[{first_8_chars}] {title}`
- Use `print()` to output to stdout
- Does NOT require: sorting, multiple items, error handling

**Fixture data:**
```python
# Mock list_top_level_sessions to return:
[SessionInfo(
    session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
    title="Design a python script",
    timestamp="2025-12-16T08:39:26.932Z"
)]
```

---

#### Test 5: `test_list_sorted_by_timestamp`
**Given:** History with 3 sessions with different timestamps:
1. "2025-12-16T10:00:00.000Z" - "Third session"
2. "2025-12-16T08:00:00.000Z" - "First session"
3. "2025-12-16T09:00:00.000Z" - "Second session"

**When:** `list` command is run
**Then:** Output shows sessions in order: Third, Second, First (most recent first)

**Implementation scope:**
- Iterate over SessionInfo list (already sorted by `list_top_level_sessions`)
- Print each in order
- Does NOT require: no sessions handling, truncation

**Note:** `list_top_level_sessions()` already returns sorted list, so this verifies end-to-end behavior.

---

#### Test 6: `test_list_long_title_truncated`
**Given:** Session with title longer than 80 characters:
- title: "This is a very long title that exceeds the eighty character limit and should be truncated with ellipsis"

**When:** `list` command is run
**Then:** Output truncates to 80 chars with "..." at end

**Implementation scope:**
- No new code needed (handled by `format_title()` in `list_top_level_sessions`)
- Test verifies integration

**Note:** `format_title()` from Step 1 already handles this. Test verifies CLI integration.

---

#### Test 7: `test_list_no_sessions_message`
**Given:** History directory exists but contains no session files
**When:** `list` command is run
**Then:** Prints "No sessions found" to stdout

**Implementation scope:**
- Check if `list_top_level_sessions()` returns empty list
- Print message if empty
- Does NOT require: stderr output, error codes

```python
if not sessions:
    print("No sessions found")
```

---

#### Test 8: `test_list_nonexistent_project_error`
**Given:** Project directory `/nonexistent/path` does not exist
**When:** `list` command is run with `--project /nonexistent/path`
**Then:** No error (returns empty list, prints "No sessions found")

**Implementation scope:**
- No new code needed
- Verify graceful handling when history dir doesn't exist

**Note:** `list_top_level_sessions()` returns `[]` for non-existent dirs (handled in Step 1).

---

### Group C: Extract Command - Basic Setup (Tests 9-11)

#### Test 9: `test_extract_command_basic`
**Given:** Session "e12d203f-ca65-44f0-9976-cb10b74514c1" exists with 1 feedback item
**When:** CLI invoked with `["claudeutils", "extract", "e12d203f"]`
**Then:** Outputs JSON array to stdout

**Implementation scope:**
- Add "extract" subparser
- Add positional `session_prefix` argument
- Add optional `--project` argument (default: `os.getcwd()`)
- Add optional `--output` argument
- Find matching session by prefix
- Call `extract_feedback_recursively()`
- Convert FeedbackItem list to JSON
- Print to stdout

**Implementation hint:**
```python
extract_parser = subparsers.add_parser("extract", help="Extract feedback from session")
extract_parser.add_argument("session_prefix", help="Session ID or prefix")
extract_parser.add_argument("--project", default=os.getcwd())
extract_parser.add_argument("--output", help="Output file path")
```

---

#### Test 10: `test_extract_with_output_flag`
**Given:** Session exists with 1 feedback item
**When:** CLI invoked with `["claudeutils", "extract", "e12d203f", "--output", "feedback.json"]`
**Then:** Writes JSON array to file `feedback.json` (not stdout)

**Implementation scope:**
- Check if `--output` is provided
- If yes, write to file using `Path.write_text()`
- If no, print to stdout
- Does NOT require: error handling, file permissions

```python
if args.output:
    Path(args.output).write_text(json_output)
else:
    print(json_output)
```

---

#### Test 11: `test_extract_with_project_flag`
**Given:** Session exists in `/custom/path`
**When:** CLI invoked with `["claudeutils", "extract", "abc123", "--project", "/custom/path"]`
**Then:** Calls `extract_feedback_recursively()` with `/custom/path` as project_dir

**Implementation scope:**
- Pass `args.project` to extraction function
- Does NOT require: new logic (just wiring)

---

### Group D: Extract Command - Session Matching (Tests 12-15)

#### Test 12: `test_extract_full_session_id`
**Given:** Session "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl" exists
**When:** CLI invoked with full ID: `["claudeutils", "extract", "e12d203f-ca65-44f0-9976-cb10b74514c1"]`
**Then:** Finds session successfully and extracts feedback

**Implementation scope:**
- Implement session matching logic
- List all UUID session files in history dir
- Check if filename (without .jsonl) starts with prefix
- Return matching session ID

**Function to implement:**
```python
def find_session_by_prefix(prefix: str, project_dir: str) -> str:
    """Find session ID matching the given prefix.

    Raises:
        ValueError: If no session or multiple sessions match
    """
```

---

#### Test 13: `test_extract_partial_prefix`
**Given:** Session "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl" exists
**When:** CLI invoked with prefix: `["claudeutils", "extract", "e12d203f"]`
**Then:** Matches session and extracts feedback

**Implementation scope:**
- Use same matching logic as Test 12
- Match on prefix from start of session ID
- Does NOT require: fuzzy matching, substring matching

---

#### Test 14: `test_extract_ambiguous_prefix`
**Given:** Two sessions exist:
- "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl"
- "e12d203f-aaaa-bbbb-cccc-dddddddddddd.jsonl"

**When:** CLI invoked with: `["claudeutils", "extract", "e12d203f"]`
**Then:** Prints error to stderr: "Multiple sessions match prefix 'e12d203f'" and exits with code 1

**Implementation scope:**
- In `find_session_by_prefix()`, collect all matches
- If len(matches) > 1, raise ValueError with message
- Catch in main() and print to stderr
- Use `sys.exit(1)` for error exit

```python
if len(matches) > 1:
    raise ValueError(f"Multiple sessions match prefix '{prefix}'")
```

---

#### Test 15: `test_extract_no_matching_session`
**Given:** History has sessions but none match prefix "zzzzzzz"
**When:** CLI invoked with: `["claudeutils", "extract", "zzzzzzz"]`
**Then:** Prints error to stderr: "No session found with prefix 'zzzzzzz'" and exits with code 1

**Implementation scope:**
- In `find_session_by_prefix()`, check if matches is empty
- If len(matches) == 0, raise ValueError with message
- Handle in main() similar to Test 14

```python
if len(matches) == 0:
    raise ValueError(f"No session found with prefix '{prefix}'")
```

---

### Group E: Extract Command - JSON Output & Integration (Tests 16-18)

#### Test 16: `test_extract_json_format_valid`
**Given:** Session with 2 feedback items
**When:** `extract` command is run
**Then:** Output is valid JSON array that can be parsed with `json.loads()`

**Implementation scope:**
- Use `json.dumps()` to serialize feedback items
- Convert Pydantic models to dicts using `.model_dump()`
- Does NOT require: pretty printing, custom formatting

```python
feedback = extract_feedback_recursively(session_id, project_dir)
json_output = json.dumps([item.model_dump() for item in feedback])
```

---

#### Test 17: `test_extract_json_includes_all_fields`
**Given:** Session with 1 FeedbackItem containing all fields:
- timestamp, session_id, feedback_type, content, agent_id, slug, tool_use_id

**When:** `extract` command is run
**Then:** JSON output includes all fields (even None values)

**Implementation scope:**
- Ensure `model_dump()` includes all fields
- Use `model_dump(mode='json')` for proper serialization
- Does NOT require: field filtering, custom serialization

**Fixture data:**
```python
FeedbackItem(
    timestamp="2025-12-16T08:43:43.872Z",
    session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
    feedback_type=FeedbackType.TOOL_DENIAL,
    content="Request denied",
    agent_id="a6755ed",
    slug="test-slug",
    tool_use_id="toolu_123"
)
```

---

#### Test 18: `test_extract_recursive_integration`
**Given:** Session with nested structure:
- Main session "main-123" with 1 message
- Agent "a1" (child of main-123) with 1 message
- Agent "a2" (child of a1) with 1 message

**When:** `extract` command is run with "main-123"
**Then:** JSON output contains 3 feedback items from all levels

**Implementation scope:**
- No new code needed
- Integration test verifying end-to-end flow
- Uses existing `extract_feedback_recursively()` from Step 4

**Fixture data:**
Create full session files with agent hierarchy (reuse Step 4 fixture approach).

---

## Helper Functions

### `find_session_by_prefix(prefix: str, project_dir: str) -> str`

Finds session ID matching the given prefix.

**Algorithm:**
1. Get history directory
2. List all UUID-named `.jsonl` files
3. Filter files where `session_id.startswith(prefix)`
4. If 0 matches: raise ValueError
5. If >1 matches: raise ValueError
6. If 1 match: return session_id

**Signature:**
```python
def find_session_by_prefix(prefix: str, project_dir: str) -> str:
    """Find unique session ID matching prefix.

    Args:
        prefix: Session ID prefix to match
        project_dir: Project directory path

    Returns:
        Full session ID

    Raises:
        ValueError: If 0 or >1 sessions match prefix
    """
```

---

## Test Fixture Template

### CLI Testing with Mocking

```python
import sys
from unittest.mock import patch

def test_list_command_default_project(monkeypatch, tmp_path):
    """Test list uses current directory by default."""
    # Mock cwd
    monkeypatch.setattr("os.getcwd", lambda: str(tmp_path))

    # Mock list_top_level_sessions to verify it's called correctly
    called_with = []
    def mock_list(project_dir):
        called_with.append(project_dir)
        return []

    monkeypatch.setattr("main.list_top_level_sessions", mock_list)

    # Mock sys.argv
    monkeypatch.setattr("sys.argv", ["claudeutils", "list"])

    # Run main
    main()

    # Verify
    assert called_with == [str(tmp_path)]
```

### Capturing stdout

```python
from io import StringIO

def test_list_output_format(capsys, monkeypatch):
    """Test list output formatting."""
    # Mock list_top_level_sessions
    def mock_list(project_dir):
        return [SessionInfo(
            session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
            title="Test session",
            timestamp="2025-12-16T10:00:00.000Z"
        )]

    monkeypatch.setattr("main.list_top_level_sessions", mock_list)
    monkeypatch.setattr("sys.argv", ["claudeutils", "list"])

    # Run main
    main()

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "[e12d203f] Test session\n"
```

---

## Implementation Order Summary

**Tests 1-3:** CLI setup and argument parsing
- Create ArgumentParser
- Add subparsers for list/extract
- Parse --project flag

**Tests 4-8:** List command output
- Format output as `[prefix] title`
- Handle empty results
- Verify sorting (integration test)

**Tests 9-11:** Extract command basics
- Add extract subparser
- Add --output flag
- Wire up to existing extraction function

**Tests 12-15:** Session matching
- Implement `find_session_by_prefix()`
- Handle error cases (no match, multiple matches)
- Error messages to stderr

**Tests 16-18:** JSON output and integration
- Serialize FeedbackItem to JSON
- Verify all fields included
- End-to-end integration test

---

## Reusable Functions (From Previous Steps)

These functions are already implemented and tested:
- `get_project_history_dir(project_dir: str) -> Path` - Get history directory
- `list_top_level_sessions(project_dir: str) -> list[SessionInfo]` - List sessions
- `extract_feedback_recursively(session_id: str, project_dir: str) -> list[FeedbackItem]` - Extract feedback

---

## Success Criteria

✅ All 18 tests pass in sequence
✅ Each test initially fails before implementation
✅ Implementing test N does NOT make test N+1 pass
✅ `pytest test_main.py -k "test_cli" -v` → 18 passed
✅ CLI can be invoked: `python -m claudeutils list`
✅ CLI can be invoked: `python -m claudeutils extract <prefix>`

---

## Installation & Entry Point

After implementation, add to `pyproject.toml`:

```toml
[project.scripts]
claudeutils = "claudeutils.main:main"
```

This allows running as: `claudeutils list` instead of `python -m claudeutils.main list`

---

## Common TDD Violations to Avoid

❌ **Implementing both list and extract in Test 1** - Only parser setup needed
❌ **Adding output formatting before Test 4** - Tests 1-3 don't need it
❌ **Implementing session matching in Test 9** - Not needed until Test 12
❌ **Handling all error cases upfront** - Add error handling when tests require it

✅ **Correct approach:**
- Test 1 → Basic parser with subcommands
- Test 2 → Add list subparser, default project
- Test 3 → Parse --project flag
- Test 4 → Add output formatting
- ...incrementally add features
