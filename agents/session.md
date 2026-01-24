# Session Handoff: 2026-01-24

**Status:** Agent-core submodule integrated; /tmp blocking hook implemented; CLAUDE.md communication rules updated

## Completed This Session

**Agent-core submodule integration:**
- Converted agent-core from direct copy to git submodule (commit: 7f5ae4f)
- Updated agent-core justfile: Added hooks syncing to sync-to-parent recipe (agent-core commit: 8424cdd)
- Removed install script (scripts/install-agent-core.sh), replaced with justfile workflow
- Submodule at commit 8424cdd (includes /tmp blocking hook + hooks sync)
- Final commit: 29c039f

**PreToolUse hook for /tmp blocking:**
- Implemented hook in agent-core: hooks/pretooluse-block-tmp.sh
- Blocks Write tool calls to /tmp/ and /private/tmp/ paths
- Returns JSON with permissionDecision: "deny" and error message
- Resolves Write tool path-based deny pattern limitation (discovered earlier)
- Hook not yet installed locally (requires `cd agent-core && just sync-to-parent`)

**CLAUDE.md communication rules enhanced:**
- Added token economy rule: Don't repeat file contents, use references (commit: 409a756)
- Added rule to avoid numbered lists unless sequencing matters (commit: 43666cb)
- Converted Communication Rules from numbered to bulleted list
- Converted Execute Rule workflow from numbered to bulleted list
- Rationale: Avoid renumbering churn when editing

## Pending Tasks

- [ ] **Apply review feedback to composition API runbook**
  - Restructure Cycles 2.1, 3.1, 4.1 to minimal implementations (happy path only)
  - Move features to later cycles for proper RED/GREEN sequencing
  - Fix CLI command naming (compose_cmd → compose or add @main.command(name='compose'))
  - Fix exit code mapping (FileNotFoundError should be exit 2, not 4)
  - Remove/fix invalid YAML anchor test (line 451-467)
  - Add implementation sequencing hints
  - Review report: plans/unification/consolidation/reports/runbook-review.md:586-748

- [ ] **Execute revised runbook** (AFTER FIXES)
  - Run prepare-runbook.py to generate execution artifacts
  - Use /orchestrate for TDD cycle execution
  - Follow strict RED-GREEN-REFACTOR discipline

## Blockers / Gotchas

**Runbook revision required before execution:**
- Current runbook violates TDD RED/GREEN discipline in 6/11 cycles (55%)
- Must restructure implementations to be incremental (not all-at-once)
- See review report: plans/unification/consolidation/reports/runbook-review.md

**Earlier context (TDD workflow):**
- TDD workflow enhanced with delegated review (commit: 9df24a1, aa054da)
- Composition API runbook created (commit: 64815ab)
- Review found violations, now needs fixes before execution

## Next Steps

Apply review feedback to composition API runbook (see plans/unification/consolidation/reports/runbook-review.md:586-748)

---

## Recent Learnings

**Communication efficiency (NEW):**
- Don't repeat file contents in responses (costs tokens)
- Use file references instead: path:line or just path
- Avoid numbered lists unless sequencing matters (causes renumbering churn when editing)
- User feedback: "It's expensive, if info is in a file, reference it"

**Agent-core submodule workflow:**
- Changes must be made in ~/code/claudeutils/agent-core/ (local working copy)
- Never modify ~/code/agent-core/ directly (submodule source repo)
- Sync workflow: Edit in agent-core → commit → update parent submodule reference
- Justfile sync-to-parent creates symlinks for skills, agents, hooks

**PreToolUse hook pattern for path validation:**
- Write tool doesn't support path-based deny patterns in settings.json
- Solution: PreToolUse hook with JSON input/output
- Hook reads tool_name and tool_input.file_path from JSON
- Returns permissionDecision: "deny" to block, empty JSON to allow
- Pattern applicable to other path-based restrictions

**TDD runbook patterns (prior session):**
- Delegated review catches RED/GREEN violations before execution
- Anti-pattern: Complete signatures in first cycle → tests pass immediately
- Correct: Minimal implementation in X.1, add features incrementally in X.2+
