**⚠ UNREVIEWED — Agent-drafted from session.md task descriptions. Validate before design.**

# Health Check UPS Fallback

Add UserPromptSubmit fallback for session health check when SessionStart hook did not fire.

## Requirements

### Functional Requirements

**FR-1: UPS health check fallback**
When SessionStart hook (`agent-core/hooks/sessionstart-health.sh`) did not execute (e.g., after `/clear`, on hook failure), the first UserPromptSubmit invocation runs the health check instead.
- Acceptance: `/clear` then user message → UPS hook detects missing SessionStart flag and runs health check
- Acceptance: Normal session (SessionStart fired) → UPS hook skips health check (no double-run)
- Acceptance: Health check results appear in `additionalContext` (same output as SessionStart)

### Constraints

**C-1: Flag-file coordination**
Use existing flag-file pattern from `stop-health-fallback.sh` — SessionStart writes a flag, UPS checks for it.

**C-2: UPS budget**
UPS hook already runs `userpromptsubmit-shortcuts.py` on every message. Health check fallback must not add measurable latency on the normal path (flag-file check only).

### Out of Scope

- Fixing SessionStart hook reliability (separate root cause)
- Modifying Stop hook fallback (`stop-health-fallback.sh`) — this adds a parallel UPS fallback

### Skill Dependencies (for /design)

- Load `plugin-dev:hook-development` before design (UPS hook modification)
