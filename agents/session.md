# Session Handoff: 2026-01-30

**Status:** Work complete, ready to commit

## Completed This Session

**Markdown documentation cleanup:**
- Fixed broken reference in agents/decisions/architecture.md:603 (plans/formatter-comparison.md no longer exists)
- Updated ROADMAP.md to mark Markdown Formatter Survey as complete (✅ 2026-01-07)
- Verified remark-cli migration complete (.remarkrc.json, .remarkignore, justfile updated)
- Reviewed markdown branch (157 commits behind, all valuable work already merged to main)

**Project-local tmpdir configuration:**
- Updated .envrc to use project-local `tmp/claude/` directory
- Added CLAUDE_CODE_TMPDIR override to prevent `/tmp/claude-501/cwd-*` errors
- Aligns with CLAUDE.md tmp-directory.md fragment (project-local tmp/, not system /tmp/)
- Changed `watch_file ~/.env` to `watch_file .env` (local project file)
- Changed `dotenv` to `dotenv_if_exists` (conditional loading)
- Directory auto-created on direnv load

**Diagnosed nested skill interruption bug:**
- `/commit` invokes `/gitmoji` and `/handoff` via Skill tool, causing context switches requiring user "continue"
- Confirmed as known bug (GitHub #17351): nested skill invocation doesn't return to calling skill context
- Claude Code docs have no pattern for skill composition — inline is the workaround
- Explored skill structure via Task agent (Explore subagent) - found all skills symlinked to agent-core

**Imported handoff-haiku fix context from ../home repo (8398772):**
- Explored ../home commits (8eb2ebe, 2079274, 49eff39) to understand handoff-lite fixes
- Created import design: plans/handoff-haiku-import/design.md
- Copied 3 plan documents: transcript.md (root cause analysis), design.md (5 fixes), design-review.md (APPROVE WITH CHANGES)
- Added 4 learnings to Recent Learnings
- Fixed symlinks: removed stale handoff-lite, created handoff-haiku
- Files: plans/handoff-lite-issue/transcript.md, plans/handoff-lite-fixes/design.md, plans/handoff-lite-fixes/design-review.md

**Reevaluated vet review with handoff-haiku context (8398772):**
- Read vet review: plans/commit-unification/reports/vet-review.md (identified design/implementation misalignment)
- Created reevaluation: plans/commit-unification/reports/vet-reevaluation.md
- Key finding: Handoff-haiku Fix 1 pattern supersedes commit-unification inline approach
- Resolution: REMOVE handoff from commit entirely (don't inline, don't invoke - decouple)
- Rationale: Handoff-haiku established separation of concerns as superior to inlining

**Revised commit-unification design (8398772):**
- Updated plans/commit-unification/design.md to apply handoff-haiku Fix 1 pattern
- Changed Problem #3 from "nested skill bug" to "handoff coupling"
- Updated Requirements: "Remove handoff from commit skill" (was "Inline handoff execution")
- Removed handoff-protocol.md from structure diagram
- Rewrote Decision #2: "Remove handoff step entirely" with handoff-haiku rationale
- Updated execution flow: removed handoff step, renumbered to 4 steps, added session.md staging

**Implemented commit-unification in agent-core (7f6a14f):**
- Created commit/references/gitmoji-index.txt (copy from gitmoji/cache/, 78 entries)
- Created commit/scripts/update-gitmoji-index.sh (adapted from gitmoji/scripts/, executable)
- Rewrote commit/SKILL.md: 189 lines, merged commit + commit-context
  - Added --context flag (skip discovery when you know what changed)
  - Inlined gitmoji selection (Step 3 reads references/gitmoji-index.txt)
  - Removed handoff step, added note: "Run `/handoff` separately before committing"
  - Added session.md/plans/ staging guidance (Step 4)
  - All flags documented: --context, --test, --lint, --no-gitmoji
- Deleted commit-context/ directory entirely
- Skill review (plugin-dev:skill-reviewer): PRODUCTION-READY

**Committed all work (d5b9169):**
- Commit 8398772: Import handoff-haiku context, revise design (claudeutils)
- Commit 7f6a14f: Unify commit skills (agent-core)
- Commit d5b9169: Update agent-core submodule 018d631→7f6a14f (claudeutils)

**Updated plan-adhoc and plan-tdd skills for direct prepare-runbook.py invocation:**
- Changed all `python3 agent-core/bin/prepare-runbook.py` to `agent-core/bin/prepare-runbook.py` (relies on shebang)
- Updated allowed-tools in both skills: added `agent-core/bin/prepare-runbook.py` to Bash permits
- Removed `python3:*` from plan-adhoc allowed-tools (no longer needed)
- Added allowed-tools field to plan-tdd frontmatter
- Rationale: Enables sandbox exemption configuration for prepare-runbook.py specifically (impossible with python3 prefix)
- Files modified in agent-core:
  - skills/plan-adhoc/SKILL.md (3 occurrences changed, frontmatter updated)
  - skills/plan-tdd/SKILL.md (2 occurrences changed, frontmatter added)

## Pending Tasks

None - all work complete.

## Blockers / Gotchas

None.

## Next Steps

Ready for new work. Suggest starting fresh session.

## Recent Learnings

**Don't compose skills via Skill tool invocation:**
- Anti-pattern: Skill A invokes `/skill-b` via Skill tool for sub-operations
- Correct pattern: Inline the logic or copy supporting files into the calling skill's references/
- Rationale: Known bug (#17351) causes context switch; no official nested skill pattern exists
- Tradeoff: Duplication of small files (gitmoji index) is acceptable vs workflow interruption

**Skill Model Constraints Must Be Enforced:**
- Anti-pattern: Agent invoked handoff-lite (Haiku-only) from Sonnet
- Correct pattern: Name encodes constraint (handoff-haiku), `user-invocable: false`, differentiated descriptions
- Design fix: `plans/handoff-lite-fixes/design.md`

**Template Ambiguity: Replace vs Augment:**
- Anti-pattern: "Use this template" without merge semantics
- Correct pattern: Explicit PRESERVE/ADD/REPLACE instructions per section
- Design fix: Partial template showing only sections being replaced/added

**Skill Delegation Ambiguity:**
- Anti-pattern: commit-context says "Run `/handoff`" — unclear who invokes
- Correct pattern: Decouple entirely. Commit = commit. Handoff = handoff. Two commands.

**Skill Description Overlap Causes Misrouting:**
- Anti-pattern: Two skills sharing trigger phrases ("handoff", "end session")
- Correct pattern: Internal/model-specific skills have no user-facing triggers, lead with constraints
- `user-invocable: false` for internal skills

**Orchestration assessment (Point 0) prevents unnecessary runbooks:**
- Anti-pattern: Creating runbooks for tasks that should be implemented directly
- Correct pattern: Evaluate orchestration overhead vs direct implementation (design complete? <6 files? single session?)
- Rationale: Runbooks add overhead (prep scripts, step files, orchestrator) - only justified for complex/long/parallel work
- Example: Commit unification is ~4 files + merge, design complete → implement directly

**Checkpoint process for runbooks:**
- Anti-pattern: All-at-once vetting after full runbook execution OR vetting every single step
- Correct pattern: Two-step checkpoints at natural boundaries
- Rationale: Balances early issue detection with cost efficiency

**Presentation vs behavior in TDD:**
- Anti-pattern: Writing RED-GREEN cycles for help text wording, error message phrasing
- Correct pattern: Test behavior, defer presentation quality to vet checkpoints
- Rationale: Presentation tests are brittle and self-evident

**Agent-core project-independence pattern:**
- Anti-pattern: Hardcode project-specific paths in agent-core skills
- Correct pattern: Delegate project-specific routing to project-level config files
- Rationale: Skills should be opinionated about patterns but flexible about project structure

**Native @file obsoletes custom composition tooling:**
- Discovery: Claude Code natively supports `@path/to/file.md` references with recursive inclusion
- Pattern: Use @file for shared fragments, keep project-specific content inline

**Delete obsolete code, don't archive:**
- Anti-pattern: Moving obsolete code to archive/, old/, or commenting it out
- Correct pattern: Delete completely - git history is the archive
- Rationale: Dead code creates maintenance burden

**Broken documentation references:**
- Anti-pattern: Leaving references to deleted files in documentation (creates confusion)
- Correct pattern: Update references when deleting documented work - replace with summary or git history note
- Rationale: Broken references waste time and undermine documentation credibility
- Example: architecture.md referenced plans/formatter-comparison.md (deleted), replaced with evaluation summary

**Quiet agent pattern for delegation:**
- Anti-pattern: Agents return verbose output to orchestrator context
- Correct pattern: Agents write detailed reports to files, return only filename (success) or structured error (failure)
- Rationale: Prevents context pollution, detailed logs available in files when needed
- Example: vet-agent writes review to tmp/ or plans/*/reports/, returns just filename
