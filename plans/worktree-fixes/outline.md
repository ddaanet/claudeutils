# Worktree Fixes — Design Outline

## Approach

Fix 5 worktree issues across slug derivation, precommit validation, session merge, and task automation. Introduce shared task-block parsing infrastructure used by both merge conflict resolution (FR-4) and session task movement (FR-6).

## Key Decisions

**Shared task-block parser.** FR-4 (merge) and FR-6 (task movement) both need to extract multi-line task blocks from session.md. A single `extract_task_blocks()` function parses `- [ ] **Name** ...` lines plus indented continuation lines. Lives in a new `session.py` module alongside session editing functions: `move_task_to_worktree()`, `remove_worktree_task()`, and `find_section()` for section boundary detection.

**Validation at both creation and commit.** Q-1 answer: `derive_slug()` validates task name format (fail-fast at creation time), AND precommit validates all task names in session.md (catch-all for manual edits). Defense in depth — neither alone is sufficient.

**MERGE_HEAD detection for commit.** FR-5 fix: check `git rev-parse MERGE_HEAD` to detect active merge, always commit when merge was initiated. Replaces checking `git diff --cached --quiet` which misses empty-diff merges.

**Session editing in CLI, not skill.** FR-6 moves task movement from agent skill steps to Python CLI commands. `new --task` writes main-repo session.md; `rm` removes worktree task entry. Skill steps become no-ops or are removed.

## Phase Structure

**Phase execution order:** Phase 0 → Phase 1 → Phase 2 → Phase 3. Phases 0-2 are TDD (independent of each other but execute sequentially). Phase 3 is general (skill update after all code lands).

### Phase Boundaries & Dependencies

| Phase | FRs | Type | Rationale |
|-------|-----|------|-----------|
| 0: Task name constraints | FR-1, FR-2 | TDD | Validation infrastructure: slug derivation must be lossless before merge (FR-4) and automation (FR-6) rely on it. Precommit validation ensures all task names conform. Foundation phase. |
| 1: Merge fixes | FR-4, FR-5 | TDD | Merge infrastructure separate from validation: task-block parsing applies to existing names. MERGE_HEAD detection independent of name format. Can execute after Phase 0 establishes validation. |
| 2: Session automation | FR-6 | TDD | Builds on Phase 1 task-block parser. Separate phase because it touches different execution paths (CLI commands, not merge). Task movement uses parser from Phase 1, validation from Phase 0. |
| 3: Skill update | — | General | Update SKILL.md after all CLI automation lands. Remove manual session.md editing steps that are now automated. |

## Acceptance Criteria Mapping

**Phase 0 deliverables:**
- FR-1.1: `derive_slug()` lossless round-tripping (test with valid names)
- FR-1.2: Remove `max_length` parameter from `derive_slug()`
- FR-1.3: `focus_session()` pattern matching works (test with constrained names)
- FR-1.4: `validate_task_name()` function exists and rejects invalid characters
- FR-2.1: Precommit scans Pending Tasks and Worktree Tasks sections
- FR-2.2: Precommit rejects forbidden characters (backticks, colons, slashes, etc.)
- FR-2.3: Clear error message from precommit with task name and character
- FR-2.4: Integration with `just precommit`

**Phase 1 deliverables:**
- FR-4.1: `extract_task_blocks()` captures full multi-line task blocks
- FR-4.2: `_resolve_session_md_conflict()` inserts blocks with proper blank line separation
- FR-4.3: Existing task detection by name (not full line match)
- FR-5.1: MERGE_HEAD detection always creates merge commit when merge initiated
- FR-5.2: `git branch -d` succeeds after merge (branch reachable from HEAD)
- FR-5.3: No behavior change for non-empty merges

**Phase 2 deliverables:**
- FR-6.1: `new --task` moves task from Pending to Worktree with `→ <slug>` marker
- FR-6.2: `new --task` preserves full task block (continuation lines)
- FR-6.3: `rm` removes task from Worktree Tasks only if task was removed on the merged branch
- FR-6.4: Idempotent operations (re-run doesn't corrupt)

**Phase 3 deliverables:**
- Remove manual session.md editing steps from SKILL.md (Mode A step 4, Mode B step 4, Mode C step 3 — these were task movement operations now automated by the CLI in Phase 2)
- Document that session.md task movement is now automated by CLI

## Scope Boundaries

**In scope:**
- `src/claudeutils/worktree/cli.py` — derive_slug, new, rm commands
- `src/claudeutils/worktree/merge.py` — _resolve_session_md_conflict, _phase4
- `src/claudeutils/worktree/session.py` — NEW: task-block parsing, session editing
- `src/claudeutils/validation/tasks.py` — NEW: format validation
- `tests/test_worktree_cli.py` — slug derivation, CLI command tests
- `tests/test_worktree_merge.py` — merge conflict resolution, MERGE_HEAD commit tests
- `tests/test_worktree_session.py` — NEW: task-block parsing, session editing tests
- `tests/test_validation_tasks.py` — NEW: task name format validation tests
- `agent-core/skills/worktree/SKILL.md` — Remove manual session.md editing steps (Mode A step 4, Mode B step 4, Mode C step 3) now automated by CLI

**Out of scope:**
- Mode B (parallel group) changes
- learnings.md/jobs.md merge changes
- Slug format changes (hyphens in slugs remain)
- Task autocomplete/suggestion

## Open Questions

- Q-1 (Resolved): Should `derive_slug` validate task name format and reject invalid names, or is that only precommit's job?
  - **Resolution**: Validate in both `derive_slug()` (fail-fast at creation time) and precommit (catch manual edits). Defense in depth approach documented in Key Decisions section.
