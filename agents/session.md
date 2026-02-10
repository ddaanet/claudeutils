# Session Handoff: 2026-02-10

**Status:** RCA complete. Worktree task finished — ready to merge back.

## Completed This Session

**RCA: classifyHandoffIfNeeded crash:**
- Analyzed 26 sessions, 238 total failures across v2.1.27–v2.1.38 (current)
- Key finding: **foreground** (`run_in_background=false`) Task calls fail 100% of the time; **background** (`run_in_background=true`) calls succeed 100%
- Root cause: `ReferenceError: classifyHandoffIfNeeded is not defined` in Claude Code's internal SubagentStop processing — missing function in compiled binary
- Severity: Low (cosmetic) — agents complete all work before error fires, only status reporting wrong
- Corrected two incorrect learnings in agents/learnings.md (prior session claimed background agents crash too — opposite is true)
- RCA report: `tmp/rca-classifyHandoff.md`
- GitHub issues: #22087, #22544 (open, unfixed)

## Pending Tasks

(none — worktree task complete)

## Next Steps

Merge worktree back to dev: `just wt-merge rca-background-crash`

---
*Handoff by Opus. Focused worktree RCA complete.*
