# Session: Worktree — Fix initial status in new wt

**Status:** Investigation complete — bug was already fixed, no code changes needed.

## Completed This Session

- [x] **Fix initial status in new wt reporting incorrect reset instruction** — Investigated and confirmed already fixed

## Investigation Trace

**Symptom:** New worktree sessions displayed "Note: Session says to reset session.md first (git checkout -- agents/session.md), stage all (git add -A), then /commit before executing the task."

**Root cause:** Focused session.md template in `agent-core/fragments/execute-rule.md` MODE 5 had:
```
**Status:** Parallel worktree session. First: reset session.md (`git checkout -- agents/session.md`), stage all (`git add -A`), then `/commit`. Then execute task.
```
Claude read this Status line as an instruction and followed it.

**Fix:** Agent-core commit `49e9d45` changed template to:
```
**Status:** Focused worktree for parallel execution.
```

**Verified clean:** Searched hooks, skills, fragments, scripts — no other source generates the message. It was purely Claude interpreting the old Status line. The fix in `49e9d45` was the complete resolution.

**Timeline:** Fix (`49e9d45`) was applied before this worktree was created (parent `0fd1d83` already pointed to it). This worktree was filed for investigation; the fix preceded the investigation.
