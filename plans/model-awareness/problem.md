# Model Self-Awareness Problem

**Date**: 2026-01-27
**Status**: Problem identified, design discussion needed

## Problem Statement

Model switches via CLI `/model` command are invisible to agents. This creates issues when:
1. User switches models mid-session for different task types
2. Agent needs to know which model handled previous work
3. Handoff needs to recommend appropriate model for next task
4. Session continuity requires model context

## Observed Behavior

User executed: `/model sonnet` (switching from opus)

**CLI output** (visible to user):
```
Set model to [1mDefault (claude-sonnet-4-5-20250929)[22m
```

**Agent visibility**: None - appears in transcript with `<local-command-stdout>` tag but treated as noise

**User expectation**: "I expected they were visible to agents" - model switches visible in CLI should be visible to agents

## Current Model Context

**SessionStart hook receives model**:
```json
{
  "session_id": "abc123",
  "model": "claude-sonnet-4-20250514",
  "source": "startup"
}
```

**Limitations**:
- Only fires once per session (at start)
- Mid-session `/model` switches don't re-fire SessionStart
- No dynamic model query API available
- Model info not in UserPromptSubmit or other hooks

## Session Leakage Risk

**Critical constraint**: Model context must NOT leak between sessions

**Scenarios**:
1. User works in session A with sonnet
2. Switches to session B (different project)
3. Session B should NOT see session A's model context

**Implication**: Any persistence mechanism must be session-scoped, not global

## Solutions Evaluated

### 1. System Message Injection
Model switch injects `<current-model>sonnet</current-model>` into next user message

**Pros**: Immediate visibility, no workflow change
**Cons**: Requires CLI modification, clutters user messages

### 2. Conversation Marker
`/model sonnet` generates visible message: `[Model switched to sonnet. Previous: opus.]`

**Pros**: Clear, auditable, simple
**Cons**: Adds noise to transcript, requires CLI change

### 3. Env Block Enhancement (Recommended)
Add model identity to existing env block:
```
<env>
Current model: claude-sonnet-4-5-20250929
Previous model: claude-opus-4-5-20251101
Model switches this session: 2
</env>
```

**Pros**: Already exists, no workflow change, always visible
**Cons**: Requires CLI modification, only visible at message boundaries

### 4. Handoff Protocol Requirement
Policy: Always `/handoff` before `/model` switch. Handoff captures `Model: X` in session.md.

**Pros**: No CLI changes, enforces clean state transitions
**Cons**: Workflow friction, doesn't help within-session model awareness

### 5. SessionStart Hook with Context Injection
Hook captures model at session start, injects via additionalContext:

```bash
#!/bin/bash
model=$(echo "$input" | jq -r '.model // "unknown"')
cat << EOF
{
  "additionalContext": "Current model: $model | Session: $session_id"
}
EOF
```

**Pros**: Uses existing hooks system, no CLI changes
**Cons**: Only fires at session start, doesn't track mid-session switches

## Proposed Hybrid Approach

**Combine multiple solutions**:

1. **SessionStart hook** - Capture initial model
2. **Handoff requirement** - Policy: `/handoff` before model switches
3. **Env block enhancement** - CLI injects model context (future)

**Rationale**:
- SessionStart covers most cases (one model per session)
- Handoff policy enforces clean transitions for multi-model sessions
- Env block provides comprehensive solution when implemented

## Design Discussion Topics

1. **Hook-based model tracking** - SessionStart captures model, UserPromptSubmit tracks switches
2. **CLI enhancement priority** - Is env block enhancement worth the engineering cost?
3. **Handoff policy enforcement** - Should `/model` command block without prior `/handoff`?
4. **Session isolation** - How to prevent cross-session model context leakage?
5. **Model switching patterns** - When/why do users switch models mid-session?

## Next Steps

- [ ] Design SessionStart hook for model capture
- [ ] Prototype env block enhancement approach
- [ ] Define handoff-before-model-switch policy
- [ ] Document model switching patterns and use cases
- [ ] Update CLAUDE.md with model awareness guidance

## Related Context

- Hook development: claude-code-guide agent findings
- Hook events: SessionStart, UserPromptSubmit, SubagentStart
- Settings: .claude/settings.json hooks configuration
- Environment variables: CLAUDE_PLUGIN_ROOT, CLAUDE_PROJECT_DIR
- Session isolation: JSONL transcripts per session ID

## Technical Details

**Available hook events**:
- SessionStart (has model field) - fires once per session
- UserPromptSubmit - fires per prompt, no model field
- SubagentStart - fires per subagent, has agent_type but not model

**Hook output format**:
```json
{
  "additionalContext": "Context injected into conversation",
  "systemMessage": "Message for Claude"
}
```

**Session scope**:
- Each session has unique session_id
- Transcripts: ~/.claude/projects/.../[session-id].jsonl
- Sessions isolated - no shared state
- Hooks execute per-session, outputs session-scoped
