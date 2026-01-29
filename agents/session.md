# Session Handoff: 2026-01-30

**Status:** Commit unification designed, ready for direct implementation

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

**Designed commit skill unification** (`plans/commit-unification/design.md`):
- Merge `/commit` + `/commit-context` into single `/commit` with `--context` flag
- Inline gitmoji selection (copy index to `commit/references/`, read directly)
- Keep `/handoff` invocation (complex skill, interruption is acceptable pause for session review)
- Keep `/gitmoji` and `/handoff` as standalone user-invocable skills (unchanged)
- Delete `commit-context/` entirely (code removal principle)
- **Key decisions:**
  - Copy gitmoji-index.txt (can't reliably cross-reference skills, file is small)
  - Don't inline handoff (6.5K skill too large, interruption is meaningful)
  - `--context` flag skips git discovery, uses conversation context

**Updated sync-to-parent justfile recipe:**
- Added stale symlink cleanup before sync loop
- Handles commit-context deletion and any future skill removals generically
- File: `agent-core/justfile` (already committed: 5d95c4b)

**Planning assessment:**
- Evaluated via `/plan-adhoc` Point 0 orchestration assessment
- Conclusion: **Implement directly** (orchestration overhead not justified)
- Rationale: ~4 files, all straightforward (copies + merge + delete), design complete, single session work

**Commits:**
- 5d95c4b: 🔧 Configure project-local tmpdir in .envrc (includes justfile update)

## Pending Tasks

**Commit skill unification implementation (direct execution):**
1. Copy `agent-core/skills/gitmoji/cache/gitmojis.txt` → `agent-core/skills/commit/references/gitmoji-index.txt`
2. Adapt `agent-core/skills/gitmoji/scripts/update-gitmoji-index.sh` → `agent-core/skills/commit/scripts/update-gitmoji-index.sh` (update output path)
3. Rewrite `agent-core/skills/commit/SKILL.md`:
   - Merge commit + commit-context content
   - Add `--context` flag handling (skip discovery when set)
   - Inline gitmoji step (read references/gitmoji-index.txt, semantic matching, prefix commit title)
   - Keep `/handoff` invocation (step 2)
   - Update frontmatter description (include `--context` trigger)
   - Target: ~3K words
4. Delete `agent-core/skills/commit-context/` directory entirely
5. Run `just sync-to-parent` in agent-core (removes stale commit-context symlink in claudeutils)
6. Test all flag combinations

**Reference files:**
- Design: `plans/commit-unification/design.md`
- Current `/commit`: `agent-core/skills/commit/SKILL.md` (4.8K)
- Current `/commit-context`: `agent-core/skills/commit-context/SKILL.md` (5.8K)
- Gitmoji index: `agent-core/skills/gitmoji/cache/gitmojis.txt` (3.7K, 78 entries)

**Config composition implementation (Phases 5-7 for configs):**
- See: agent-core/configs/README.md, plans/unification/STATUS.md

## Blockers / Gotchas

**Nested skill bug (#17351):**
- Skills invoking other skills via Skill tool cause context switch
- Workaround: inline the logic or read supporting files directly
- `/commit` unification inlines gitmoji, keeps `/handoff` (acceptable interruption)

**Config composition gap:**
- Native @file only works for markdown files
- Justfile/pyproject.toml need different import mechanism
- Base files organized but not yet consumable by projects
- Original compose.py design may still be needed for config files

**Agent-core template naming:**
- CLAUDE.md files in subdirectories auto-inject into context
- Template must be named CLAUDE.template.md to avoid this

**Branch state:**
- claudeutils: main branch (clean after commit 5d95c4b)
- agent-core: main branch (1 uncommitted change: justfile stale symlink cleanup)

## Next Steps

**Next session:** Execute commit skill unification (direct implementation, 6 steps above). Then `/vet` for review.

**Model recommendation:** Sonnet (merging skills, semantic work, appropriate for direct implementation)

## Recent Learnings

**Don't compose skills via Skill tool invocation:**
- Anti-pattern: Skill A invokes `/skill-b` via Skill tool for sub-operations
- Correct pattern: Inline the logic or copy supporting files into the calling skill's references/
- Rationale: Known bug (#17351) causes context switch; no official nested skill pattern exists
- Tradeoff: Duplication of small files (gitmoji index) is acceptable vs workflow interruption

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
