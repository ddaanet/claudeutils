# Design Review: Worktree Skill

**Design Document**: plans/worktree-skill/design.md
**Review Date**: 2026-02-10
**Reviewer**: design-vet-agent (opus)

## Summary

The design specifies a `claudeutils _worktree` CLI subcommand and `/worktree` SKILL.md replacing 5 justfile recipes. It covers CLI specification, three-phase merge flow with submodule resolution, deterministic session file conflict resolution, and skill orchestration. The design is architecturally sound with clear separation between CLI (deterministic git operations) and skill (ceremony, session manipulation).

**Overall Assessment**: Needs Minor Changes

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **Git plumbing pre-commit missing temp index isolation**
   - Problem: The `new --session` flow described git index operations (read-tree, update-index, write-tree) without specifying a temp index file. Running these against the main index would corrupt the working tree's staging area.
   - Impact: Implementing as written would produce a bug where `_worktree new --session` modifies the parent repo's index.
   - Fix Applied: Added `GIT_INDEX_FILE=<tmpfile>` environment variable for all index operations, `--index-output=<tmpfile>` for read-tree, and cleanup step. Explicit commit message added to `commit-tree`.

2. **Merge Phase 3 step 2 cross-reference error**
   - Problem: Step 2 said "commit with message and exit (see step 6)" — step 6 is "Output merge commit hash," not the commit action. A clean merge still needs commit (step 4) and precommit (step 5) before output.
   - Impact: Implementer could skip precommit validation for clean merges, violating NFR-4.
   - Fix Applied: Changed to "proceed to step 4 (commit)" — correct forward reference.

3. **`rm` subcommand assumed worktree directory always exists**
   - Problem: Step 1 was "Validate `wt/<slug>/` exists" as a hard requirement. After a failed merge or manual cleanup, the directory may not exist but the branch still needs cleanup.
   - Impact: Branch-only cleanup would fail, leaving orphaned branches.
   - Fix Applied: Made directory existence a conditional check. Worktree removal only runs if directory exists; branch deletion always runs.

### Minor Issues

1. **Testing scenario table: misleading "fast-forward" description**
   - Problem: Table entry said "Submodule merge (fast-forward)" with assertion "No merge commit created, pointer updated." But Phase 2 doesn't have a separate fast-forward path — the ancestry check (step 4) detects when local already includes worktree changes and skips entirely.
   - Fix Applied: Renamed to "Submodule merge (already included)" with assertion "Ancestry check detects local includes worktree changes, merge skipped."

2. **Status ordering includes `outlined` not in canonical progression**
   - Problem: The jobs.md conflict resolution algorithm listed `outlined` in the status ordering, but `agents/jobs.md` canonical progression is `requirements -> designed -> planned -> complete` (four statuses, no `outlined`).
   - Fix Applied: Added explanatory note acknowledging the discrepancy and recommending the planner update `agents/jobs.md` to document `outlined` as valid.

3. **FR-7 traceability reference pointed to non-existent "Migration" section**
   - Problem: FR-7 said "addressed by Migration" but no section with that heading exists. The relevant content is under "Documentation Updates" > "Justfile recipe deletion."
   - Fix Applied: Updated to "addressed by Documentation Updates (Justfile recipe deletion)."

4. **Learnings conflict resolution described two competing approaches**
   - Problem: Primary algorithm used conflict marker parsing (split on `<<<<<<<`, `=======`, `>>>>>>>`), then offered a "simpler alternative" using append. For an append-only file, marker parsing is fragile and unnecessary.
   - Fix Applied: Promoted the append strategy to primary algorithm. Parse by `## ` headings, diff on title, append new entries. Removed marker-based approach.

5. **Mode B (parallel group) missing "no group found" handling**
   - Problem: If prose analysis finds no independent parallel group (all tasks have dependencies), the flow had no termination path — it would proceed to "for each task in group" with an empty group.
   - Fix Applied: Added step 3: "If no parallel group found: report and stop."

6. **Missing test scenario for `new --session` pre-commit**
   - Problem: The git plumbing session pre-commit is the most complex part of `new` but had no corresponding test scenario in the critical scenarios table.
   - Fix Applied: Added "New with --session pre-commit" scenario to test_worktree_cli with assertions on worktree HEAD content and main index integrity.

7. **Mode C merge ceremony missing error handling for handoff/commit failure**
   - Problem: Steps 1-2 were "Invoke handoff+commit, wait for completion" with no error path. If handoff or commit fails, proceeding to merge would violate clean-tree requirement.
   - Fix Applied: Added explicit error handling: if handoff or commit fails, stop and report. Added separate handling for merge exit code 1 (conflicts/precommit) vs exit code 0 (success).

## Requirements Alignment

**Requirements Source:** inline (design.md Requirements section)

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | yes | CLI Specification (6 subcommands fully specified) |
| FR-2 | yes | Merge Flow Phase 2 (ancestry check, fetch, merge, verify) |
| FR-3 | yes | Conflict Resolution: Session Files (task extraction algorithm) |
| FR-4 | yes | Conflict Resolution: Source Code (take-ours + precommit gate) |
| FR-5 | yes | Skill Design (3 modes, frontmatter, slug derivation) |
| FR-6 | yes | Documentation Updates (execute-rule.md, sandbox-exemptions.md) |
| FR-7 | yes | Documentation Updates: Justfile recipe deletion |
| FR-8 | yes | Testing Strategy (11 critical scenarios, integration-first) |
| NFR-1 | yes | D-8 + Phase 2/3 idempotency checks |
| NFR-2 | yes | Conflict Resolution section (all session files deterministic) |
| NFR-3 | yes | Phase 2 step 8 uses `git commit -m`, not /commit skill |
| NFR-4 | yes | Phase 3 step 5 (mandatory precommit gate) |
| NFR-5 | yes | Package structure, Click registration, error to stderr |

**Gaps:** None. All requirements traced to design elements.

## Positive Observations

- **Clean CLI/skill boundary** (D-5): CLI handles deterministic git operations, skill handles ceremony and session manipulation. This makes the CLI fully testable with real git repos while keeping workflow coordination in the skill where it belongs.
- **Idempotent merge design** (D-8): Each phase checks current state before acting. Phase 2 skips if submodule already merged, Phase 3 detects in-progress merges. This handles the common case of interrupted merges gracefully.
- **Session conflict resolution algorithm** (FR-3): The task extraction approach directly addresses the known defect (blind `--ours` losing worktree-side tasks). The regex-based approach is deterministic and testable.
- **Submodule merge ordering** (D-7): Pre-merging the submodule before parent merge ensures the agent-core conflict in Phase 3 can be safely resolved with `checkout --ours`. This is the correct ordering learned from prior merge failures.
- **Directory inside project root** (D-1): Moving from `../<repo>-<slug>` to `wt/<slug>` eliminates sandbox bypass for most operations. Practical improvement that simplifies the implementation.
- **Thorough testing strategy**: 11 critical scenarios covering merge, conflicts, idempotency, debris cleanup, and task recovery. Integration-first with real git repos matches project conventions.
- **Comprehensive design decisions**: 10 numbered decisions with clear rationale. Each decision maps to a specific requirement or constraint.

## Recommendations

- The planner should update `agents/jobs.md` to include `outlined` in the canonical status progression, since it exists in practice and the conflict resolution algorithm depends on it.
- Consider adding a test scenario for the `add-commit` idempotency (stdin message + nothing staged = no-op). This is mentioned in D-10 but not in the test table.
- The submodule branch creation in `new` (step 5: `git checkout -b <slug>` in agent-core) should clarify what happens if the branch already exists in the submodule (e.g., from a previous partial creation). Adding `|| true` or a check would improve robustness.

## Next Steps

1. Proceed to `/plan-tdd plans/worktree-skill/design.md` for TDD runbook creation
2. Load `plugin-dev:skill-development` before writing SKILL.md phase
