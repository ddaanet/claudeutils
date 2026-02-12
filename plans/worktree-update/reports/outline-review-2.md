# Outline Review: worktree-update

**Artifact**: plans/worktree-update/outline.md
**Date**: 2026-02-12T00:00:00Z
**Mode**: review + fix-all

## Summary

The outline provides a comprehensive refactoring plan that aligns worktree Python CLI implementation with the justfile prototype. The approach correctly emphasizes skill-first architecture, worktree-based submodule handling, and sibling directory paths. All requirements from the task prompt are addressed with explicit implementation guidance.

**Overall Assessment**: Ready

## Requirements Traceability

No formal requirements.md file exists for this plan. Requirements extracted from task prompt:

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Sibling directory paths (`<repo>-wt/<slug>`) | Script changes → new command | Complete | Path computation logic specified |
| FR-2: Worktree-based submodule (`git -C agent-core worktree add`) | Script changes → new command | Complete | Replaces `--reference` approach |
| FR-3: Skill as primary interface | Architecture section | Complete | CLI hidden with `_` prefix |
| FR-4: Single implementation for shared logic | Architecture → Modules | Complete | `derive_slug`, `focus_session`, `wt_path` |
| FR-5: `focus-session` command | Script changes → Add focus-session | Complete | Replaces inline generation |
| FR-6: Source file conflict abort | Script changes → merge Phase 3 | Complete | Exit 1, manual resolution |
| FR-7: Learnings conflict keep-both | Script changes → merge Phase 3 | Complete | Append theirs-only lines |
| FR-8: CLI hidden from user help | Architecture → CLI | Complete | `_worktree` prefix convention |
| FR-9: Execute-rule.md markers | Execute-rule.md section | Complete | Slug-only format specified |
| FR-10: Settings.json permissions | Script changes → new command | Complete | Sandbox registration in scope |

**Traceability Assessment**: All requirements covered with implementation details

## Review Findings

### Critical Issues

None identified. All critical requirements (path handling, submodule approach, conflict resolution) are addressed with sufficient detail.

### Major Issues

1. **CLI signature ambiguity for focus-session**
   - Location: Script changes → Add `focus-session` command
   - Problem: Original text said "Input: ... (or stdin)" and "Output: ... (or to `--output` path)" suggesting flexible I/O, but no CLI signature specified
   - Fix: Added explicit CLI signature `claudeutils _worktree focus-session "<task-name>" <session-md-path>` with stdout output. Removed stdin/--output ambiguity. Mode A invocation updated to use stdout redirection.
   - **Status**: FIXED

2. **Missing capture instruction for `new` command output**
   - Location: Skill changes → Mode A → Step 5
   - Problem: Text says "CLI now outputs actual sibling path" but doesn't instruct to capture it
   - Fix: Added "Capture output to variable for next step" to Step 5
   - **Status**: FIXED

3. **Module refactoring approach unclear**
   - Location: Architecture → Modules
   - Problem: Listed functions as if creating from scratch, but most logic already exists in cli.py
   - Fix: Added note "Most functions already exist in cli.py but need refactoring: extract logic into functions, leave CLI commands as thin wrappers"
   - **Status**: FIXED

4. **Implementation sequence didn't start with refactoring**
   - Location: Implementation Sequence
   - Problem: Step 1 said "Add helper functions" but existing code needs refactoring first
   - Fix: Changed Step 1 to "Refactor existing CLI: extract logic from commands into helper functions"
   - **Status**: FIXED

5. **Missing CLI import details**
   - Location: Script changes → Register CLI
   - Problem: Said "Add `_worktree` group to main cli.py" but didn't specify import statement
   - Fix: Added explicit import and registration instructions
   - **Status**: FIXED

### Minor Issues

1. **Focus-session function signature inconsistency**
   - Location: Architecture → Modules
   - Problem: Listed parameter as `session_md_content` (string) but should be `session_md_path` (file path)
   - Fix: Changed to `focus_session(task_name, session_md_path)` with note "(reads file, returns string)"
   - **Status**: FIXED

2. **Launch command format missing comment**
   - Location: Skill changes → Mode A → Step 7
   - Problem: Text said "use actual path" but didn't include the `# <task-name>` comment shown in current skill
   - Fix: Added `# <task-name>` comment to launch command format
   - **Status**: FIXED

3. **Sandbox registration dedup not mentioned**
   - Location: Script changes → new command → Sandbox registration
   - Problem: Could add duplicate entries to `additionalDirectories` array
   - Fix: Added "(create key if missing, dedup if already present)" to registration logic
   - **Status**: FIXED

4. **JSON formatting not specified**
   - Location: Script changes → new command → Sandbox registration
   - Problem: JSON dump formatting unspecified (readability matters for settings files)
   - Fix: Added "with indent=2 for readability" to json.dump instruction
   - **Status**: FIXED

5. **Just availability check missing**
   - Location: Script changes → new command → Environment initialization
   - Problem: Could fail without clear message if `just` not installed
   - Fix: Added "Check for just availability: `subprocess.run(['just', '--version'], ...)` first"
   - **Status**: FIXED

6. **Clean-tree command duplication**
   - Location: Script changes → merge command → Phase 1
   - Problem: Described implementing clean tree validation logic inline, but `clean-tree` command already exists
   - Fix: Changed to "Use `claudeutils _worktree clean-tree` command (already implements exemption logic)"
   - **Status**: FIXED

7. **Repo name extraction not specified**
   - Location: Script changes → new command → Path computation
   - Problem: Container naming needs repo name but extraction method not stated
   - Fix: Added "Extract repo name: `Path.cwd().name` for container naming"
   - **Status**: FIXED

8. **Session handling clarity for branch reuse**
   - Location: Script changes → new command → Existing branch detection
   - Problem: "warn and ignore `--session`" rationale unclear
   - Fix: Added explanation "(branch reuse means session already committed)"
   - **Status**: FIXED

9. **Worktree registration parsing method**
   - Location: Script changes → rm command → Worktree registration probing
   - Problem: Said "grep <wt-path>" which is fragile
   - Fix: Changed to "Parse `git worktree list --porcelain`" with path matching
   - **Status**: FIXED

10. **Task extraction pattern too vague**
    - Location: Script changes → merge command → Phase 3 → session.md conflict
    - Problem: Used `grep -oP` with unclear regex
    - Fix: Changed to "parse for `- [ ] **<name>**` patterns" (implementation detail, clear intent)
    - **Status**: FIXED

11. **Merge commit conditional not stated**
    - Location: Script changes → merge command → Phase 3 → Commit merge
    - Problem: Should check for staged changes before committing (idempotency)
    - Fix: Added "(only if staged changes exist)" to commit instruction
    - **Status**: FIXED

12. **Source file abort cleanup not detailed**
    - Location: Script changes → merge command → Phase 3 → Source file conflicts
    - Problem: Cleanup command listed "agents/ src/ tests/" but should be general
    - Fix: Changed to `git clean -fd` (removes all untracked, not just specific dirs)
    - **Status**: FIXED

13. **Precommit failure guidance missing**
    - Location: Test updates → test_worktree_merge.py
    - Problem: Test coverage didn't mention Phase 4 guidance printing
    - Fix: Added "(guidance printed)" to Phase 4 test description
    - **Status**: FIXED

14. **Source conflict abort verification missing**
    - Location: Test updates → test_worktree_merge.py
    - Problem: Tests should verify merge abort behavior for source conflicts
    - Fix: Added "Source file conflict abort: verify merge aborted and working tree cleaned"
    - **Status**: FIXED

15. **Execute-rule.md status display not mentioned**
    - Location: Execute-rule.md marker convention
    - Problem: Only mentioned Worktree Tasks format, not status command display
    - Fix: Added bullet "Status display (#status command) to show slug only, not full path"
    - **Status**: FIXED

16. **Existing branch handling for submodule incomplete**
    - Location: Script changes → new command → Submodule worktree creation
    - Problem: Didn't remove obsolete `checkout -B` step
    - Fix: Added "Remove `checkout -B <slug>` step (worktree add already checks out the branch)"
    - **Status**: FIXED

17. **Mode B consolidation incomplete**
    - Location: Skill changes → Mode B
    - Problem: Step 5 description too brief
    - Fix: Added "print consolidated list with instructions" for clarity
    - **Status**: FIXED

18. **Implementation sequence test organization vague**
    - Location: Implementation Sequence → Step 10
    - Problem: Said "Update existing tests + add new test files" without separation
    - Fix: Split into Step 11 (update existing) and Step 12 (add new) for clarity
    - **Status**: FIXED

19. **Path output format not specified**
    - Location: Script changes → new command → Output
    - Problem: Relative vs absolute path not stated
    - Fix: Added "(absolute)" to "Print actual worktree path"
    - **Status**: FIXED

20. **Graceful degradation not in rm command list**
    - Location: Script changes → rm command
    - Problem: Branch-only cleanup mentioned in description but not in bullet list
    - Fix: Added bullet "Graceful degradation: Handle case where worktree directory doesn't exist"
    - **Status**: FIXED

## Fixes Applied

- focus-session CLI signature: stdout output, no stdin/--output options
- Mode A Step 5: added capture instruction for `new` output
- Architecture Modules: noted refactoring approach for existing code
- Implementation sequence: starts with refactoring existing code
- Register CLI: added import and registration details
- focus_session parameter: `session_md_path` not `session_md_content`
- Launch command: added `# <task-name>` comment
- Sandbox registration: added dedup instruction
- JSON formatting: specified indent=2
- Environment init: added just availability check
- Merge Phase 1: use existing clean-tree command
- Path computation: added repo name extraction
- Branch reuse: clarified session handling rationale
- Worktree probing: use --porcelain parsing not grep
- Task extraction: clarified pattern intent
- Merge commit: added conditional (staged changes check)
- Source conflict cleanup: generalized to `git clean -fd`
- Test coverage: added Phase 4 guidance and abort verification
- Execute-rule.md: added status display format
- Submodule creation: removed obsolete checkout step
- Mode B description: clarified Step 5 output
- Implementation sequence: separated test updates into two steps
- Path output: specified absolute path
- rm command: added graceful degradation bullet

## Positive Observations

- **Comprehensive scope coverage**: All 9 requirements plus execute-rule.md and settings.json addressed
- **Clear architecture separation**: Modules (logic), CLI (wrappers), Skill (primary), Justfile (fallback)
- **Explicit exit codes**: Merge command has well-defined exit code semantics (0, 1, 2)
- **Idempotency by design**: Merge ceremony can be safely retried after fixes
- **Test coverage plan**: Four test files with specific coverage areas listed
- **Conflict resolution strategy**: Deterministic for session files, manual for source files
- **Single implementation principle**: No duplication between skill and CLI (derive_slug, focus_session)
- **Submodule ordering**: Critical removal ordering (submodule first) explicitly called out
- **Clean tree enforcement**: Uses existing clean-tree command, maintains exemptions
- **Implementation sequence**: Logical progression from refactoring to new features to integration

## Recommendations

- **During implementation**: Verify `clean-tree` command output format is suitable for merge Phase 1 (exit code + stderr message)
- **Testing**: Consider integration test for full Mode A flow (slug → focus-session → new → session.md edit → launch)
- **Error messages**: Ensure all exit 1 and exit 2 conditions print clear guidance for recovery
- **Agent-core setup recipe**: Add this early in sequence (prerequisite for env init testing)
- **Sandbox permissions**: Test container registration in both main and worktree settings files
- **Branch reuse edge case**: Test behavior when branch exists but worktree doesn't (should reuse branch, create worktree)

---

**Ready for user presentation**: Yes
