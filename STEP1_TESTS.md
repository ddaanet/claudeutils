# Coding Agent Task: Step 1 - Path & Session Discovery (TDD)

## Mission

Implement Step 1 of the Claude Code feedback extraction tool using **strict Test-Driven Development**:
- Write ONE test
- Run it and see it FAIL (Red)
- Implement minimal code to make it PASS (Green)
- Refactor if needed
- Repeat for next test

**STOP after completing all Step 1 tests.** Do not proceed to Step 2.

---

## Project Context

**Location:** `/Users/david/code/claudeutils`

**Reference documents (READ THESE FIRST):**
- `PLAN.md` - Full 5-step implementation plan with all requirements
- `RESEARCH_FINDINGS.md` - Claude Code history storage format and schema
- `STATUS.md` - Current project status (planning complete, ready for Step 1)
- `README.md` - Project overview and data model

**Key facts from research:**
- History location: `~/.claude/projects/[ENCODED-PATH]/*.jsonl`
- Path encoding: `/Users/david/code/foo` → `-Users-david-code-foo`
- Top-level sessions: UUID-pattern files (e.g., `e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl`)
- Sub-agents: `agent-[id].jsonl` files (handled in Step 4, not now)

**Existing files:**
- `main.py` - Empty or minimal, your implementation goes here
- `pyproject.toml` - Dependencies configured (pytest, pydantic)

---

## Step 1 Functions to Implement

### 1. `encode_project_path(project_dir: str) -> str`
Converts absolute path to Claude history encoding format.

### 2. `get_project_history_dir(project_dir: str) -> Path`
Returns Path to `~/.claude/projects/[ENCODED-PATH]/`.

### 3. `SessionInfo` (Pydantic BaseModel)
Data model with fields: `session_id`, `title`, `timestamp`.

### 4. `list_top_level_sessions(project_dir: str) -> list[SessionInfo]`
Discovers UUID-named session files, extracts titles, sorts by timestamp.

---

## TDD Test Sequence (16 Tests)

Follow this EXACT sequence. For each test:
1. Write the test in `test_main.py`
2. Run `pytest test_main.py::{test_name} -v`
3. See it FAIL
4. Implement minimal code in `main.py` to make it pass
5. Run test again - should PASS
6. Move to next test

### Group A: Path Encoding (Tests 1-4)

#### Test 1: `test_encode_project_path_basic`
```python
def test_encode_project_path_basic():
    """Standard project path encoding"""
    assert encode_project_path("/Users/david/code/foo") == "-Users-david-code-foo"
    assert encode_project_path("/home/user/project") == "-home-user-project"
```
**Implementation hint:** `project_dir.replace('/', '-')`

#### Test 2: `test_encode_project_path_root`
```python
def test_encode_project_path_root():
    """Root path edge case"""
    assert encode_project_path("/") == "-"
```

#### Test 3: `test_encode_project_path_rejects_relative`
```python
def test_encode_project_path_rejects_relative():
    """Must be absolute path starting with /"""
    with pytest.raises(ValueError, match="absolute"):
        encode_project_path("relative/path")
```
**Implementation hint:** `if not os.path.isabs(project_dir): raise ValueError(...)`

#### Test 4: `test_encode_project_path_trailing_slash`
```python
def test_encode_project_path_trailing_slash():
    """Trailing slash should not affect output"""
    assert encode_project_path("/Users/david/code/foo/") == "-Users-david-code-foo"
```
**Implementation hint:** `.rstrip('/')` before replacing

---

### Group B: History Directory (Tests 5-7)

#### Test 5: `test_get_project_history_dir_basic`
```python
def test_get_project_history_dir_basic():
    """Standard path construction"""
    result = get_project_history_dir("/Users/david/code/foo")
    expected = Path.home() / ".claude" / "projects" / "-Users-david-code-foo"
    assert result == expected
```
**Implementation hint:** `return Path.home() / ".claude" / "projects" / encode_project_path(project_dir)`

#### Test 6: `test_get_project_history_dir_returns_path`
```python
def test_get_project_history_dir_returns_path():
    """Must return Path object, not string"""
    result = get_project_history_dir("/Users/david/code/foo")
    assert isinstance(result, Path)
```

#### Test 7: `test_get_project_history_dir_uses_encoding`
```python
def test_get_project_history_dir_uses_encoding():
    """Encoded portion must match encode_project_path() output"""
    project = "/home/user/project"
    result = get_project_history_dir(project)
    encoded = encode_project_path(project)
    assert result.name == encoded
```

---

### Group C: SessionInfo Model (Tests 8-9)

#### Test 8: `test_session_info_creation`
```python
def test_session_info_creation():
    """SessionInfo must have required fields with correct types"""
    info = SessionInfo(
        session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
        title="Design a python script",
        timestamp="2025-12-16T08:39:26.932Z"
    )
    assert info.session_id == "e12d203f-ca65-44f0-9976-cb10b74514c1"
    assert info.title == "Design a python script"
    assert info.timestamp == "2025-12-16T08:39:26.932Z"
```
**Implementation hint:**
```python
class SessionInfo(BaseModel):
    session_id: str
    title: str
    timestamp: str
```

#### Test 9: `test_session_info_validation`
```python
def test_session_info_validation():
    """Pydantic must validate types"""
    with pytest.raises(ValidationError):
        SessionInfo(session_id=123, title="foo", timestamp="bar")
```

---

### Group D: Session Discovery (Tests 10-16)

**Setup fixture (add this before tests):**
```python
import pytest
from pathlib import Path

@pytest.fixture
def temp_project_dir(tmp_path, monkeypatch):
    """Creates temporary project and history directories"""
    project = tmp_path / "myproject"
    project.mkdir()

    history_dir = tmp_path / ".claude" / "projects" / "-tmp-myproject"
    history_dir.mkdir(parents=True)

    def mock_get_history(proj):
        return history_dir

    monkeypatch.setattr("main.get_project_history_dir", mock_get_history)

    return project, history_dir
```

#### Test 10: `test_list_sessions_basic_discovery`
```python
def test_list_sessions_basic_discovery(temp_project_dir):
    """Discovers all UUID-named session files"""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"First"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )
    (history_dir / "a1b2c3d4-1234-5678-9abc-def012345678.jsonl").write_text(
        '{"type":"user","message":{"content":"Second"},"timestamp":"2025-12-16T11:00:00.000Z","sessionId":"a1b2c3d4-1234-5678-9abc-def012345678"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert len(sessions) == 2
```
**Implementation hints:**
- List `*.jsonl` files in history dir
- Filter by UUID regex: `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$`
- Parse first line with `json.loads()`
- Extract session_id from filename (remove `.jsonl`)

#### Test 11: `test_list_sessions_filters_agents`
```python
def test_list_sessions_filters_agents(temp_project_dir):
    """Excludes agent-*.jsonl files"""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"Main"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )
    (history_dir / "agent-a6755ed.jsonl").write_text(
        '{"type":"user","message":{"content":"Agent"},"timestamp":"2025-12-16T10:05:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert len(sessions) == 1
    assert sessions[0].session_id == "e12d203f-ca65-44f0-9976-cb10b74514c1"
```

#### Test 12: `test_list_sessions_sorted_by_timestamp`
```python
def test_list_sessions_sorted_by_timestamp(temp_project_dir):
    """Most recent session first"""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"Middle"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )
    (history_dir / "a1b2c3d4-1234-5678-9abc-def012345678.jsonl").write_text(
        '{"type":"user","message":{"content":"Latest"},"timestamp":"2025-12-16T12:00:00.000Z","sessionId":"a1b2c3d4-1234-5678-9abc-def012345678"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert sessions[0].title == "Latest"
    assert sessions[1].title == "Middle"
```
**Implementation hint:** `sessions.sort(key=lambda s: s.timestamp, reverse=True)`

#### Test 13: `test_list_sessions_extracts_title_from_string_content`
```python
def test_list_sessions_extracts_title_from_string_content(temp_project_dir):
    """Handles content as string"""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"Design a python script"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert sessions[0].title == "Design a python script"
```
**Implementation hint:** Check `isinstance(content, str)`, if so use directly

#### Test 14: `test_list_sessions_extracts_title_from_array_content`
```python
def test_list_sessions_extracts_title_from_array_content(temp_project_dir):
    """Handles content as array with text blocks"""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":[{"type":"text","text":"Help me with this"}]},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert sessions[0].title == "Help me with this"
```
**Implementation hint:** If list, find first dict with `type=="text"` and extract `text` field

#### Test 15: `test_list_sessions_truncates_long_titles`
```python
def test_list_sessions_truncates_long_titles(temp_project_dir):
    """Titles longer than 80 chars get truncated with ..."""
    project, history_dir = temp_project_dir

    long_text = "A" * 100
    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        f'{{"type":"user","message":{{"content":"{long_text}"}},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert len(sessions[0].title) == 80
    assert sessions[0].title == ("A" * 77 + "...")
```
**Implementation hint:** `if len(text) > 80: text = text[:77] + "..."`

#### Test 16: `test_list_sessions_handles_newlines_in_title`
```python
def test_list_sessions_handles_newlines_in_title(temp_project_dir):
    """Multi-line messages have newlines replaced with spaces"""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"Line one\\nLine two"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert sessions[0].title == "Line one Line two"
```
**Implementation hint:** `text.replace('\n', ' ')`

---

## Implementation Structure

**main.py should contain:**
```python
from pathlib import Path
from pydantic import BaseModel
import json
import re
import os

class SessionInfo(BaseModel):
    session_id: str
    title: str
    timestamp: str

def encode_project_path(project_dir: str) -> str:
    # TODO: Implement
    pass

def get_project_history_dir(project_dir: str) -> Path:
    # TODO: Implement
    pass

def extract_content_text(content) -> str:
    """Helper: Extract text from string or array content"""
    # TODO: Implement
    pass

def format_title(text: str) -> str:
    """Helper: Handle newlines and truncation"""
    # TODO: Implement
    pass

def list_top_level_sessions(project_dir: str) -> list[SessionInfo]:
    # TODO: Implement
    pass
```

**test_main.py should contain:**
```python
import pytest
from pathlib import Path
from pydantic import ValidationError
from main import (
    encode_project_path,
    get_project_history_dir,
    SessionInfo,
    list_top_level_sessions
)

# Tests go here...
```

---

## Success Criteria

✅ All 16 tests written and passing
✅ Each test followed Red-Green-Refactor cycle
✅ Run `pytest test_main.py -v` shows 16 passed
✅ Code is minimal and focused on making tests pass

---

## After Completion

**STOP HERE.** Do not proceed to Step 2. Report completion:
- Number of tests passing
- Any issues encountered
- Confirmation that Step 1 is complete

Next session will handle Step 2 (trivial filter implementation).
