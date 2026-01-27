# Session Handoff: Model Self-Awareness Design

**Date**: 2026-01-27
**Status**: Problem diagnosed, design discussion ready

## Completed This Session

**Model visibility problem identified:**
- CLI `/model` command switches are invisible to agents
- User expectation: "I expected they were visible to agents" - misalignment discovered
- Output appears in transcript with `<local-command-stdout>` tag but treated as noise
- Session continuity requires model context for handoffs and task routing

**Research completed:**
- claude-code-guide agent researched hooks API and session isolation
- SessionStart hook receives model field (fires once per session)
- No mid-session model switch detection mechanism exists
- Env block enhancement proposed as recommended solution

**Problem documentation:**
- Created plans/model-awareness/problem.md with complete analysis
- Documented: observed behavior, current limitations, session leakage risks, 5 solution options
- Hybrid approach proposed: SessionStart hook + handoff policy + env block enhancement
- Commit: 5270149 (✨ Add markdown composition API with TDD methodology)

## Pending Tasks

- [ ] **Design SessionStart hook for model capture** (IMMEDIATE)
  - Implement bash script: inject-model-context.sh
  - Hook captures model from SessionStart input JSON
  - Output format: additionalContext with model, session_id, source
  - Location: .claude/plugins/model-awareness/hooks/
  - Test: Verify context injection at session start

- [ ] **Prototype env block enhancement** (EXPLORATORY)
  - Research: Can CLI inject dynamic content into env block?
  - Design: Model history tracking across session lifecycle
  - Format: Current model, previous model, switch count
  - Session isolation: Ensure no cross-session leakage

- [ ] **Define handoff-before-model-switch policy** (POLICY)
  - Rule: Always execute `/handoff` before `/model` switch
  - Rationale: Ensures clean state transitions, captures work context
  - Document in: CLAUDE.md Communication Rules section
  - Enforcement: Manual policy vs CLI blocking (decision needed)

- [ ] **Document model switching patterns** (RESEARCH)
  - When: Users switch models mid-session (design→planning→execution)
  - Why: Different models for different complexity levels
  - Frequency: How common is multi-model single-session work?
  - Use cases: Collect real-world patterns from usage

## Blockers / Gotchas

**Session leakage risk** (CRITICAL):
- Any persistence mechanism must be session-scoped, not global
- User switches between projects/sessions - must NOT see previous model context
- Hook outputs are session-scoped (safe) but file writes are not (dangerous)
- Solution: Use additionalContext (ephemeral) not file writes (persistent)

**SessionStart limitation**:
- Only fires once per session (at startup)
- Mid-session `/model` switches don't re-fire SessionStart
- Partial solution: Captures initial model, misses switches

## Design Discussion Topics

### 1. SessionStart Hook Implementation

**Proposed hook structure:**
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/inject-model-context.sh"
          }
        ]
      }
    ]
  }
}
```

**Script implementation:**
```bash
#!/bin/bash
set -euo pipefail

input=$(cat)
model=$(echo "$input" | jq -r '.model // "unknown"')
session_id=$(echo "$input" | jq -r '.session_id')
source=$(echo "$input" | jq -r '.source')

cat << EOF
{
  "additionalContext": "Current model: $model | Session: $session_id | Source: $source"
}
EOF
```

**Benefits:**
- Captures initial model at session start
- No CLI changes required
- Uses existing hooks infrastructure
- Session-scoped (no leakage)

**Limitations:**
- Doesn't track mid-session model switches
- One-time injection only
- Requires hooks enabled

### 2. Env Block Enhancement (Future)

**Proposed enhancement to CLI:**
Add model context to existing `<env>` block:
```
<env>
Working directory: /Users/david/code/claudeutils
Platform: darwin
Current model: claude-sonnet-4-5-20250929
Previous model: claude-opus-4-5-20251101
Model switches: 2
</env>
```

**Benefits:**
- Always visible to agents
- Updates on every message boundary
- Tracks model history within session
- No workflow changes needed

**Challenges:**
- Requires CLI modification (engineering cost)
- Need to track model history in session state
- Must ensure session isolation

### 3. Handoff Policy Enforcement

**Proposed policy**: Always `/handoff` before `/model` switch

**Two enforcement levels:**
1. **Manual policy** (document in CLAUDE.md)
   - Trust users to follow guideline
   - Lower friction, relies on discipline
   - Fails silently if violated

2. **CLI blocking** (modify `/model` command)
   - `/model` checks if handoff completed since last work
   - Prompts user: "Create handoff before switching? (y/n)"
   - Higher friction, enforces policy

**Questions:**
- Which enforcement level appropriate?
- How to detect "work since last handoff"?
- Should policy be configurable per-project?

### 4. Model Switching Patterns

**Research needed:**
- **Frequency**: How often do users switch models mid-session?
- **Use cases**: What tasks trigger model switches?
- **Patterns**: Common sequences (opus→sonnet, sonnet→haiku, etc.)?
- **Duration**: How long between switches?

**Hypothesis**:
- Common pattern: Design (opus) → Planning (sonnet) → Execution (haiku)
- Less common: Mid-task switches for troubleshooting
- Rare: Frequent back-and-forth between models

**Data sources**:
- User interviews
- Session transcript analysis
- Usage telemetry (if available)

## Implementation Strategy

**Phase 1: Quick win** (haiku/sonnet, 1-2 hours)
- Implement SessionStart hook with inject-model-context.sh
- Test in local project
- Document in CLAUDE.md
- Limitations: Only captures initial model, not switches

**Phase 2: Policy definition** (sonnet, 30 minutes)
- Document handoff-before-model-switch policy in CLAUDE.md
- Add to Communication Rules section
- Manual enforcement initially
- Gather data on compliance

**Phase 3: Research and design** (opus, 2-3 hours)
- Research env block enhancement feasibility
- Prototype implementation approach
- Document model switching patterns from usage
- Decision: Proceed with env block or rely on hook+policy?

**Phase 4: Full implementation** (sonnet/haiku, varies by approach)
- If env block: CLI modification, testing, rollout
- If hook+policy: Monitoring, refinement, enforcement decision
- Update all documentation

## Technical Details

**Available hook events:**
- SessionStart (has model field, fires once)
- UserPromptSubmit (fires per prompt, no model field)
- SubagentStart (fires per subagent, has agent_type)

**Hook input format (SessionStart)**:
```json
{
  "session_id": "abc123",
  "hook_event_name": "SessionStart",
  "source": "startup|resume|clear|compact",
  "model": "claude-sonnet-4-20250514",
  "agent_type": "name-if-run-with-agent-flag"
}
```

**Hook output format**:
```json
{
  "additionalContext": "Text injected into conversation",
  "systemMessage": "Message for Claude (optional)"
}
```

**Session isolation:**
- Each session: unique session_id
- Transcripts: ~/.claude/projects/.../[session-id].jsonl
- Hooks execute per-session, outputs session-scoped
- File writes cross sessions (dangerous for context)

## Related Files

**Problem documentation:**
- plans/model-awareness/problem.md - Complete problem analysis

**Hook development resources:**
- plugin-dev:hook-development skill loaded - full hook API reference
- Hook events: SessionStart, UserPromptSubmit, SubagentStop, PreToolUse, PostToolUse
- Hook types: command (bash scripts) vs prompt (LLM-driven)

**Research findings:**
- claude-code-guide agent output in this session
- Hook configuration formats (plugin vs settings)
- Environment variables: CLAUDE_PLUGIN_ROOT, CLAUDE_PROJECT_DIR, CLAUDE_ENV_FILE

## Next Steps

**Immediate**: Implement SessionStart hook as quick win (Phase 1)

**Short-term**: Define and document handoff policy (Phase 2)

**Medium-term**: Research env block enhancement and model switching patterns (Phase 3)

**Success criteria**:
- Agents aware of initial model at session start
- Handoff policy reduces mid-session model confusion
- Model switching patterns documented for product decisions
- Full solution (hook+policy or env block) deployed and validated
