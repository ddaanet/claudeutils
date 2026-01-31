# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

**Tool batching enforcement is an unsolved problem:**
- Documentation (tool-batching.md fragment) doesn't reliably change behavior
- Direct interactive guidance is often ignored
- Hookify rules add per-tool-call context bloat (session bloat)
- Cost-benefit unclear: planning tokens for batching may exceed cached re-read savings
- Pending exploration: contextual block with contract (batch-level hook rules)

**Cycle numbering causes renumbering churn in runbooks:**
- Anti-pattern: Sequential numeric cycle IDs (0.1, 1.1, 2.1) with validation that rejects gaps
- Issue: Omitting phases during runbook creation triggers validation errors, requires cascading renumbering (cycle IDs, report paths, cross-references - 10+ edits per gap)
- Root cause: prepare-runbook.py enforces sequential numbering but document order already defines execution sequence - numbers are redundant labels
- Correct pattern: Either (1) relax validation to allow gaps, (2) use semantic identifiers (skill-style names), or (3) auto-number during extraction
- Rationale: Same principle as CLAUDE.md token economy: "Avoid numbered lists - causes renumbering churn when edited"
- Example: Design has R0-R4 with R3 omitted → runbook uses R0,R1,R2,R4 → validation fails "Gap 2→4" → manual renumber R4→R3
- See: plans/runbook-identifiers/problem.md for full analysis and solution options

**Heredocs broken in sandbox mode — SOLVED:**
- Root cause: zsh uses `TMPPREFIX` (not `TMPDIR`) for heredoc temp files. Default `/tmp/zsh` is outside sandbox allowlist
- Fix: `export TMPPREFIX="${TMPDIR:-/tmp}/zsh"` in agent-core/configs/claude-env.sh (sourced by .envrc)
- Upstream issue: Claude Code sandbox sets TMPDIR but not TMPPREFIX for zsh — should be reported
