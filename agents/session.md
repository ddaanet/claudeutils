# Session Handoff: 2026-03-10

**Status:** Fix applied, pending commit.

## Completed This Session

**Fix prose routing bias:**
- Three routing gates fixed in /design skill: Simple→/inline, Moderate+agentic-prose→/inline, sufficiency gate prose hard gate
- Inline Phase 4a rewritten: artifact-type review routing per `review-requirement.md`, two dispatch patterns (fix-capable vs report-only)
- Corrector template renamed to review-dispatch-template, recall context changed to artifact reference (not inlined)
- Runbook step template review references updated to canonical `review-requirement.md`
- Session.md header fixed (worktree format vs validator mismatch — data fix, code fix deferred)
- Skill-reviewer found 1 major (Continuation mapping gap) + 2 minor (filename mismatch, criteria parenthetical), all fixed

**Files changed (all in agent-core submodule):**
- `skills/design/SKILL.md` — routing + continuation
- `skills/design/references/write-outline.md` — sufficiency gate
- `skills/inline/SKILL.md` — Phase 4a review dispatch
- `skills/inline/references/review-dispatch-template.md` — renamed, recall fix
- `skills/runbook/references/general-patterns.md` — routing reference
- `skills/runbook/references/examples.md` — routing reference

## In-tree Tasks

- [x] **Fix prose routing bias** — `/design` | opus
  - Note: Agent routes prose-only work to /runbook when cross-file scope feels large, despite sufficiency gate. Same class as "design ceremony continues after uncertainty resolves." Brief: `plans/pipeline-review-protocol/brief.md` (Recurrent Failure Mode section). Schedule after session-cli-tool merges to main
- [ ] **Review prose routing** — `/deliverable-review plans/pipeline-review-protocol` | opus | restart

## Blockers / Gotchas

**Worktree session.md header format bug:**
- `session.py:307` produces `# Session: Worktree — {name}` but validator expects `# Session Handoff: YYYY-MM-DD`. Data-fixed this session. Code fix (validator or session.py) is separate behavioral change — not in scope here.

## Next Steps

Branch work complete. Deliverable review remains as separate task.
