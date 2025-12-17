# Step 3 Tests: Message Parsing

## Objective

Implement `extract_feedback_from_entry(entry: dict) -> FeedbackItem | None` to parse Claude Code conversation entries and extract non-trivial user feedback.

## Test Cases (9 tests)

### 1. Test: Non-user message returns None
**Given:** Entry with `type="assistant"`
**When:** `extract_feedback_from_entry()` is called
**Then:** Returns `None`

### 2. Test: Trivial user message returns None
**Given:** User message with content "resume"
**When:** `extract_feedback_from_entry()` is called
**Then:** Returns `None`

### 3. Test: Substantive user message returns FeedbackItem
**Given:** User message "Design a python script"
**When:** `extract_feedback_from_entry()` is called
**Then:** Returns FeedbackItem with:
- `feedback_type == FeedbackType.MESSAGE`
- `timestamp` equals entry timestamp
- `session_id` equals entry sessionId
- `content` equals message content string
- `agent_id == None` (not in entry)
- `slug == None` (not in entry)

### 4. Test: Tool denial (main session)
**Given:** Entry with tool_result containing `is_error: true` and no agentId
**When:** `extract_feedback_from_entry()` is called
**Then:** Returns FeedbackItem with:
- `feedback_type == FeedbackType.TOOL_DENIAL`
- `tool_use_id` equals content[0].tool_use_id
- `content` equals denial error message
- `agent_id == None`

### 5. Test: Tool denial (sub-agent)
**Given:** Entry with tool_result, `is_error: true`, `agentId: "a6755ed"`, `slug: "fluffy-cuddling-forest"`
**When:** `extract_feedback_from_entry()` is called
**Then:** Returns FeedbackItem with:
- `feedback_type == FeedbackType.TOOL_DENIAL`
- `agent_id == "a6755ed"`
- `slug == "fluffy-cuddling-forest"`
- `content` contains full denial message

### 6. Test: Request interruption
**Given:** User message containing "[Request interrupted"
**When:** `extract_feedback_from_entry()` is called
**Then:** Returns FeedbackItem with:
- `feedback_type == FeedbackType.INTERRUPTION`
- `content` contains "[Request interrupted"

### 7. Test: Missing sessionId
**Given:** User message without `sessionId` field
**When:** `extract_feedback_from_entry()` is called
**Then:** Returns FeedbackItem with `session_id == ""`

### 8. Test: Malformed content (empty list)
**Given:** Tool denial with empty content array
**When:** `extract_feedback_from_entry()` is called
**Then:** Returns `None`

### 9. Test: Pydantic validation error
**Given:** Entry with invalid timestamp format
**When:** `extract_feedback_from_entry()` is called
**Then:** Raises `ValidationError`

## Sample Data

All test data from PLAN.md section "Test Data".
