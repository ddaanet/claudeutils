# Recall Artifact: Task Lifecycle

## How to End Workflow With Handoff And Commit

**Source:** `agents/decisions/workflow-optimization.md`
**Relevance:** Establishes that all tiers must end with `/handoff --commit`. The carry-forward rule in handoff is where command staleness propagates.

Always tail-call `/handoff --commit`. Anti-pattern: skip handoff because "no session restart needed." Handoff is about context preservation, not just restart.

## How to Chain Multiple Skills Together

**Source:** `agents/decisions/workflow-optimization.md`
**Relevance:** CPS default-exit already chains `/handoff --commit → /commit` for cooperative skills. Session-level continuation display complements (not replaces) CPS.

Hook parses multi-skill chains. Skills own default-exit at runtime. Sub-agent isolation: continuation metadata never reaches sub-agents.

## When Handoff Includes Commit Flag

**Source:** `agents/decisions/workflow-optimization.md`
**Relevance:** session.md reflects post-commit state when `--commit` flag used. Commands written during handoff must reflect the NEXT action, not the completed one.

## When Tracking Worktree Tasks In Session

**Source:** `agents/decisions/workflow-advanced.md`
**Relevance:** Inline `→ slug` marker pattern. Tasks with worktrees have different display in STATUS. Command derivation must handle both in-tree and worktree tasks.

## _derive_next_action() mapping

**Source:** `src/claudeutils/planstate/inference.py` lines 81-87
**Relevance:** The authoritative planstate → command mapping. Already used by `_worktree ls` CLI output.

```python
_NEXT_ACTION_TEMPLATES = {
    "requirements": "/design plans/{plan_name}/requirements.md",
    "designed": "/runbook plans/{plan_name}/design.md",
    "planned": "agent-core/bin/prepare-runbook.py plans/{plan_name}",
    "ready": "/orchestrate {plan_name}",
    "review-pending": "/deliverable-review plans/{plan_name}",
}
```
