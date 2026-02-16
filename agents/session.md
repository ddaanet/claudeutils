# Session Handoff: 2026-02-16

**Status:** Pretool hook cd pattern implemented and vetted. Ready to merge.

## Completed This Session

**Pretool hook cd pattern (FR-1, FR-3, security analysis):**
- `agent-core/hooks/submodule-safety.py` — replaced exact-match `restore_patterns` list with `_is_cd_to_root()` regex. Allows `cd <root> && <cmd>` while rejecting `;`, `||`, path traversal, partial matches
- `tests/test_submodule_safety.py` — 17 parametrized test cases (10 allowed, 7 blocked). Factored from individual functions to `@pytest.mark.parametrize` for signal density
- `agent-core/fragments/claude-config-layout.md` — documented cd && exception in hook enforcement section
- `plans/pretool-hook-cd-pattern/requirements.md` — requirements + inline security analysis with attack vector table
- Vet reviews: sonnet (section banners removed) + opus (no issues) — `plans/pretool-hook-cd-pattern/reports/`

**Security verdict:** `cd <root> &&` preserves hook invariant — commands execute from project root. Only `&&` allowed (not `;` or `||`). Exact path match prevents traversal. Agent-generated strings only, no user-controlled injection surface.

## Pending Tasks

- [ ] **Simplify when-resolve CLI** — Accept single argument with when/how prefix instead of two args, update skill prose | sonnet

## Next Steps

Merge worktree to main. Task complete — this is a focused worktree.

---
*Handoff by Sonnet. Learnings file at 101/80 lines — consider `/remember` on main.*
