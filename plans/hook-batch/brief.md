# Brief: Hook Batch Task

**Source:** Discussion session 2026-02-20. Consolidates three existing hook tasks + new patterns discovered during context optimization analysis.

## Motivation

Multiple pending hook tasks share a restart requirement. Batching avoids repeated restart overhead. Also: context optimization analysis identified the UserPromptSubmit hook as a key enforcement mechanism for skill activation reliability and recipe-priority enforcement.

## Absorbs existing tasks

- **PostToolUse auto-format hook** — Run formatter on Write/Edit changed files
- **SessionStart status hook** — Health checks at session start (originally 5 features, scoped to 3)

## SessionStart hook (3 features, not 5)

| Feature | Implementation | Status |
|---|---|---|
| Dirty tree warning | `git status --porcelain` | Ready |
| Learnings health | `learning-ages.py --summary` (needs flag addition) | Ready |
| Stale worktree detection | `git worktree list` + age check | Ready |
| ~~Model tier display~~ | No platform API for model introspection | Blocked |
| ~~Tip rotation~~ | Tips file concept from original discussion but never created; content source TBD | Deferred |

learning-ages.py already exists at `agent-core/bin/learning-ages.py`. Add `--summary` flag for one-liner output suitable for hook injection.

## PreToolUse recipe-redirect hook

Informative hook paired with sandbox denylist. When agent attempts a raw command that has a project recipe, inject additionalContext redirecting to the proper CLI.

Pattern matches: `ln` → `just sync-to-parent`, `git worktree` → `claudeutils _worktree`, `git merge` → `claudeutils _worktree merge`.

Nice-to-have for UX (tells agent WHY command failed), not load-bearing (denylist is the enforcement).

## UserPromptSubmit hook improvements

Detailed plan at `plans/claude/cozy-growing-moth.md`. Summary:

1. **Line-based shortcut matching** — Shortcuts trigger on own line, not full-prompt-only
2. **Directive scope clarification** — d: and p: apply to prefixed section, not single line
3. **p: dual output** — Concise systemMessage like d: already has
4. **Implement q: and learn: directives** — Documented in execute-rule.md but not hooked
5. **b: directive** — Fourth member of b/d/p/q letter symmetry. Semantics TBD.
6. **Skill-editing guard** — Editing verbs + skill/agent → inject plugin-dev guide reminder
7. **CCG integration** — Platform capability questions → remind about claude-code-guide agent

## Skill activation research findings

- Skill activation uses pure LLM reasoning — no algorithmic matching
- Baseline activation rate ~20% with good descriptions
- "Forced eval hook" pattern (UserPromptSubmit injects evaluate-then-activate commitment) reaches 84%
- Scott Spence: https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably
- Current approach: targeted patterns (skill-editing guard, ccg) rather than general forced-eval. Measure first, generalize if needed.

## RCA: Skill trigger failure

During this session, "drop a brief" should have triggered `/brief` skill but agent started manual execution instead. Root cause analysis:

- **Surface:** Didn't invoke skill
- **Proximal:** Execution routing ("do it directly if feasible") preempted skill scanning
- **Structural:** Skill matching is attention-dependent (scan 40+ descriptions), execution routing is pattern-reinforced (fires on every interaction). Cheaper cognitive path wins.
- **Platform:** 20% baseline activation is a known limitation, not project-specific

Fix direction: UserPromptSubmit hook as mechanical enforcement (skill-editing guard, forced-eval pattern). Rule strengthening alone doesn't work — the rule is already clear ("BLOCKING REQUIREMENT").

## Communication rule change (already applied)

Removed AskUserQuestion directive from `agent-core/fragments/communication.md` (rule 5). Agent can now ask questions in plain text instead of being forced through AskUserQuestion tool.

## Dependencies

- Hook batch is a prerequisite for context-optimization (fragment demotion)
- Sandbox denylist is manual user configuration, not part of this task
- All hooks require session restart after deployment
- `just sync-to-parent` needed after hook file changes

## Model / execution

sonnet | restart required
