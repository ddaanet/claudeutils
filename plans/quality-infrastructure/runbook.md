---
name: quality-infrastructure
model: sonnet
---

# Quality Infrastructure Reform

**Context**: Rename agent infrastructure (FR-3), restructure deslop fragment (FR-1), add code density decisions (FR-2).
**Design**: plans/quality-infrastructure/outline.md
**Requirements**: plans/quality-infrastructure/requirements.md
**Status**: Ready
**Created**: 2026-02-21

---

## Weak Orchestrator Metadata

**Total Steps**: 6 (Phase 1) + inline (Phases 2-3)

**Execution Model**:
- Step 1.1: Sonnet (git mv + taxonomy embed into agent definition)
- Step 1.2: Opus (agent definition internal reference updates — architectural artifacts)
- Step 1.3: Haiku (file deletion — mechanical)
- Step 1.4: Opus (skill/fragment content updates — architectural artifacts)
- Step 1.5: Opus (cross-codebase reference updates — includes architectural artifacts)
- Step 1.6: Haiku (symlink sync + grep verification — bash operations)
- Phase 2: Inline (orchestrator-direct)
- Phase 3: Inline (orchestrator-direct)

**Step Dependencies**: sequential (1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6 → checkpoint → restart → Phase 2 → Phase 3 → final checkpoint)

**Error Escalation**:
- Haiku → Sonnet: Unexpected git errors, symlink resolution failures
- Sonnet/Opus → User: Missing files, ambiguous references, scope uncertainty
- Any → User: Grep for old names finds references in unexpected production locations

**Report Locations**: plans/quality-infrastructure/reports/

**Success Criteria**: All agent/skill/fragment renames applied; all reference files updated per terminology table; grep for old names returns zero hits in production files (agent-core/, agents/, .claude/, CLAUDE.md); deslop.md deleted and content redistributed; 5 code density entries in cli.md with memory-index triggers.

**Prerequisites**:
- All 17 agent definitions exist in agent-core/agents/ (✓ verified)
- All 8 plan-specific detritus files exist in .claude/agents/ (✓ verified)
- vet-taxonomy.md exists for embed (✓ verified, 63 lines)
- communication.md exists for prose merge (✓ verified, 7 lines)
- cli.md exists for decision entries (✓ verified)
- justfile has sync-to-parent target (✓ verified)

**Session Boundary**: Session restart required between Phase 1 and Phase 2 — agent definitions load at session start.

---

## Common Context

**Requirements:**
- FR-1: Split deslop.md — prose rules → communication.md (ambient), code rules stay in project-conventions skill (pipeline-only). Delete deslop.md.
- FR-2: Add 5 grounded code density decisions to agents/decisions/cli.md + memory-index triggers.
- FR-3: Rename 11 agents (6 review/correct + 5 execution), delete vet-agent (deprecated, D-1), embed vet-taxonomy in corrector (D-2), delete 8 plan-specific detritus, rename skill dir + fragment. Update all reference files.

**Scope boundaries:**
- IN: 10 agent renames, 1 deprecation (delete), 1 taxonomy embed, 8 plan-specific deletions, ~37 reference updates, deslop restructuring, 5 code density entries, symlink regeneration
- OUT: Context optimization (review-requirement.md demotion), project-conventions restructuring beyond code deslop, new agent definitions, codebase sweep (FR-4), prepare-runbook.py crew- prefix changes

**Key Constraints:**
- Git mv for renames (preserves blame history)
- Atomic rename: all references updated before symlink sync
- Session restart after Phase 1 (agent definitions load at session start)
- vet-agent DELETED per D-1 (zero active call sites), not renamed
- vet-taxonomy.md content embedded in corrector.md per D-2, then deleted
- vet-requirement.md is NOT in CLAUDE.md @-references — loaded by agents, not main session

**Terminology Table:**

| Old | New |
|-----|-----|
| vet-fix-agent | corrector |
| design-vet-agent | design-corrector |
| outline-review-agent | outline-corrector |
| runbook-outline-review-agent | runbook-outline-corrector |
| plan-reviewer | runbook-corrector |
| review-tdd-process | tdd-auditor |
| quiet-task | artisan |
| quiet-explore | scout |
| tdd-task | test-driver |
| runbook-simplification-agent | runbook-simplifier |
| test-hooks | hooks-tester |
| vet-requirement | review-requirement |
| /vet (skill) | /review (skill) |
| "vet report" | "review report" |
| "vet-fix report" | "correction" |
| "vetting" | "review/correction" |

**Project Paths:**
- Agent definitions: agent-core/agents/
- Skills: agent-core/skills/
- Fragments: agent-core/fragments/
- Decisions: agents/decisions/
- Plan-specific detritus: .claude/agents/ (standalone files, not symlinks)
- Symlink sync: `cd agent-core && just sync-to-parent`

---

### Phase 1: Agent Rename — FR-3 (type: general)

## Step 1.1: Rename agent definition files and embed taxonomy

**Objective**: Git mv all 11 agent files to new names, embed vet-taxonomy.md content into corrector.md, delete vet-agent.md and vet-taxonomy.md.

**Execution Model**: Sonnet

**Implementation**:

1. Git mv 6 review/correct agents (in agent-core/agents/):
   - vet-fix-agent.md → corrector.md
   - design-vet-agent.md → design-corrector.md
   - outline-review-agent.md → outline-corrector.md
   - runbook-outline-review-agent.md → runbook-outline-corrector.md
   - plan-reviewer.md → runbook-corrector.md
   - review-tdd-process.md → tdd-auditor.md

2. Git mv 5 execution agents (in agent-core/agents/):
   - quiet-task.md → artisan.md
   - quiet-explore.md → scout.md
   - tdd-task.md → test-driver.md
   - runbook-simplification-agent.md → runbook-simplifier.md
   - test-hooks.md → hooks-tester.md

3. Embed taxonomy: Read vet-taxonomy.md (63 lines: status table, subcategory codes, investigation format, deferred items template). Read corrector.md. Find the "Status taxonomy" reference or the section that references vet-taxonomy.md. Replace the reference with the full taxonomy content inline. Preserve the taxonomy's heading structure within corrector.md.

4. Git rm vet-taxonomy.md (content now embedded in corrector.md).

5. Git rm vet-agent.md (deprecated per D-1: zero active call sites — exploration report confirms no production delegation).

**Expected Outcome**: 11 renamed files, 2 deleted files, taxonomy content embedded in corrector.md.

**Error Conditions**:
- Git mv fails → STOP, verify source file exists at expected path
- Taxonomy embed location unclear in corrector.md → Read full file, search for "taxonomy" or "vet-taxonomy" reference, place near existing status/classification content

**Validation**: `ls agent-core/agents/corrector.md design-corrector.md outline-corrector.md runbook-outline-corrector.md runbook-corrector.md tdd-auditor.md artisan.md scout.md test-driver.md runbook-simplifier.md hooks-tester.md` succeeds. `ls agent-core/agents/vet-agent.md agent-core/agents/vet-taxonomy.md` fails (deleted). `grep -c "UNFIXABLE Subcategory Codes" agent-core/agents/corrector.md` returns 1.

---

## Step 1.2: Update agent internal references

**Objective**: Update name: frontmatter and all cross-references within renamed agent definitions.

**Execution Model**: Opus

**Prerequisite**: Read each agent file fully before editing — understand cross-reference targets and frontmatter structure.

**Implementation**:

1. Update `name:` frontmatter in all 11 renamed agents to match new filename (sans .md):
   - corrector.md → `name: corrector`
   - design-corrector.md → `name: design-corrector`
   - outline-corrector.md → `name: outline-corrector`
   - runbook-outline-corrector.md → `name: runbook-outline-corrector`
   - runbook-corrector.md → `name: runbook-corrector`
   - tdd-auditor.md → `name: tdd-auditor`
   - artisan.md → `name: artisan`
   - scout.md → `name: scout`
   - test-driver.md → `name: test-driver`
   - runbook-simplifier.md → `name: runbook-simplifier`
   - hooks-tester.md → `name: hooks-tester`

2. Update `description:` frontmatter to use new terminology where applicable (e.g., "Vet review agent" → "Review agent", "quiet task" → "artisan").

3. Apply full terminology table from Common Context within each agent's body text:
   - Cross-agent references (e.g., tdd-auditor referencing corrector instead of vet-fix-agent)
   - Process terminology ("vetting" → "review/correction", "vet report" → "review report")
   - Other agent references (quiet-task → artisan, plan-reviewer → runbook-corrector, etc.)

4. Update `skills:` frontmatter if any agent references renamed skills (vet → review).

**Expected Outcome**: All 11 agent definitions use new names in frontmatter and body. No old-name references within agent-core/agents/.

**Error Conditions**:
- Agent has unexpected frontmatter format → STOP, examine and adapt
- Cross-reference target ambiguous → use terminology table as authoritative source

**Validation**: `grep -rl "vet-fix-agent\|design-vet-agent\|outline-review-agent\|runbook-outline-review-agent\|plan-reviewer\|review-tdd-process\|quiet-task\|quiet-explore\|tdd-task\|runbook-simplification-agent\|test-hooks" agent-core/agents/` returns zero files (excluding this runbook and reports).

---

## Step 1.3: Delete plan-specific detritus

**Objective**: Remove 8 standalone plan-specific agent files from .claude/agents/.

**Execution Model**: Haiku

**Implementation**:

Git rm these 8 files from .claude/agents/:
- error-handling-task.md
- pushback-task.md
- runbook-quality-gates-task.md
- when-recall-task.md
- workflow-rca-fixes-task.md
- worktree-merge-data-loss-task.md
- worktree-merge-resilience-task.md
- workwoods-task.md

**CRITICAL**: Verify each file is a standalone file (not a symlink) before deleting. Symlinks point to agent-core/ and must NOT be deleted — they're managed by `just sync-to-parent`. Check with `ls -la .claude/agents/` first.

**Expected Outcome**: 8 standalone files removed. All symlinks remain intact.

**Error Conditions**:
- File not found → Warn, continue (may already be deleted)
- File is a symlink → STOP, do NOT delete — symlinks managed separately

**Validation**: `ls -la .claude/agents/` shows only symlinks (→ agent-core/) plus hook-batch-task.md. No other standalone *-task.md files.

---

## Step 1.4: Rename skill directory and fragment

**Objective**: Rename vet skill to review, rename vet-requirement fragment to review-requirement, update internal content of both.

**Execution Model**: Opus

**Prerequisite**: Read SKILL.md and review-requirement.md fully before editing.

**Implementation**:

1. `git mv agent-core/skills/vet/ agent-core/skills/review/`

2. Update agent-core/skills/review/SKILL.md:
   - Frontmatter: `name: vet` → `name: review`
   - Update description to use "review" language
   - Apply full terminology table throughout body text:
     - vet-fix-agent → corrector
     - vet-agent → remove or update (deprecated per D-1)
     - All other old names → new names per table
   - Remove vet-taxonomy.md reference (now embedded in corrector.md)

3. `git mv agent-core/fragments/vet-requirement.md agent-core/fragments/review-requirement.md`

4. Update review-requirement.md content:
   - Title: "Vet Requirement" → "Review Requirement"
   - Rule text: "delegate to `vet-fix-agent`" → "delegate to `corrector`"
   - Routing table: vet-fix-agent → corrector, design-vet-agent → design-corrector
   - Process description: "vet" → "review", "vetting" → "review/correction"
   - Template: vet-fix-agent → corrector throughout
   - Remove reference to "agent-core/agents/vet-taxonomy.md" — note taxonomy is now in corrector.md
   - "vet-fix report" → "correction"
   - Section heading "Vet Requirement" → "Review Requirement", "Vet process" → "Review process"
   - Preserve semantic meaning — only change terminology, not behavior

**Expected Outcome**: Skill directory at agent-core/skills/review/ with updated SKILL.md. Fragment at agent-core/fragments/review-requirement.md with updated content. No references to old names within either file.

**Error Conditions**:
- Git mv fails on directory → Try `mkdir -p` target then mv individual files
- Content update ambiguous (e.g., "vet" in a general English context vs agent name) → Change only when "vet" refers to the review process/agent, not general English usage

**Validation**: `ls agent-core/skills/review/SKILL.md` succeeds. `ls agent-core/fragments/review-requirement.md` succeeds. `grep "vet-fix-agent" agent-core/skills/review/SKILL.md agent-core/fragments/review-requirement.md` returns zero hits.

---

## Step 1.5: Update references across codebase

**Objective**: Update all files outside agent-core/agents/ that reference old agent/skill/fragment names. Apply terminology propagation.

**Execution Model**: Opus

**Prerequisite**: Read terminology table from Common Context. Agent internal references were handled in Step 1.2. This step covers everything else.

**Implementation**:

Apply terminology table substitutions across these categories. For each file: read, apply all applicable substitutions, write.

**1. Skills (7+ files):**
- agent-core/skills/commit/SKILL.md — vet-requirement → review-requirement
- agent-core/skills/runbook/SKILL.md — quiet-task→artisan, tdd-task→test-driver, vet-fix-agent→corrector, plan-reviewer→runbook-corrector, runbook-simplification-agent→runbook-simplifier, quiet-explore→scout, test-hooks→hooks-tester, outline-review-agent→outline-corrector, runbook-outline-review-agent→runbook-outline-corrector
- agent-core/skills/design/SKILL.md — design-vet-agent→design-corrector
- agent-core/skills/deliverable-review/SKILL.md — vet-fix-agent→corrector
- agent-core/skills/orchestrate/SKILL.md — vet-fix-agent→corrector, quiet-task→artisan, tdd-task→test-driver, plan-reviewer→runbook-corrector, runbook-simplification-agent→runbook-simplifier, quiet-explore→scout
- agent-core/skills/doc-writing/SKILL.md — vet references → review
- agent-core/skills/plugin-dev-validation/SKILL.md — vet references → review
- agent-core/skills/review-plan/SKILL.md — plan-reviewer→runbook-corrector (if referenced)
- agent-core/skills/memory-index/SKILL.md — vet references → review

**2. Decision files (6 files):**
- agents/decisions/pipeline-contracts.md — vet-fix-agent→corrector, plan-reviewer→runbook-corrector, vet-requirement→review-requirement
- agents/decisions/operational-practices.md — vet delegation→review delegation
- agents/decisions/workflow-optimization.md — quiet-task→artisan, vet references→review
- agents/decisions/workflow-advanced.md — vet delegation references
- agents/decisions/project-config.md — agent configuration names
- agents/decisions/orchestration-execution.md — vet-fix-agent→corrector, vet-requirement→review-requirement

**3. Docs (2 files):**
- agent-core/docs/tdd-workflow.md — vet references→review
- agent-core/docs/general-workflow.md — remove vet-agent recommendation (deprecated per D-1), vet-fix-agent→corrector, plan-reviewer→runbook-corrector

**4. Other agent-core (2 files):**
- agent-core/README.md — agent inventory: update all renamed agent names, remove vet-agent, remove vet-taxonomy
- agent-core/bin/focus-session.py — vet reference→review

**5. Memory index:**
- agents/memory-index.md — update /when triggers referencing old names

**6. Session files:**
- agents/session.md — update task descriptions referencing old names
- agents/learnings.md — update vet references in learnings entries

**7. Rules:**
- .claude/rules/plugin-dev-validation.md — vet reference→review

**8. CLAUDE.md:**
- No changes needed for FR-3 — vet-requirement.md is NOT in CLAUDE.md @-references
- deslop.md removal happens in Phase 2e (not this step)

**9. Terminology propagation in ALL files touched above:**
- "vet report" → "review report"
- "vet-fix report" → "correction"
- "vetting" → "review/correction"
- "vet delegation" → "review delegation"

**Scope note**: Files in plans/ are historical records — do NOT update references in plans/ reports, requirements, or outlines. Only update production files (agent-core/, agents/, .claude/, CLAUDE.md).

**Expected Outcome**: All production files updated. No stale references to old names outside plans/.

**Error Conditions**:
- Old name in unexpected context → Distinguish: reference to agent/skill (update) vs descriptive historical prose (leave)
- File modified by concurrent worktree → STOP, report conflict

**Validation**: `grep -rl "vet-fix-agent\|design-vet-agent\|outline-review-agent\|runbook-outline-review-agent\|plan-reviewer\|review-tdd-process\|quiet-task\|quiet-explore\|tdd-task\|runbook-simplification-agent\|test-hooks\|vet-agent\|vet-taxonomy\|vet-requirement" --include="*.md" --include="*.py" agent-core/ agents/decisions/ agents/memory-index.md agents/session.md agents/learnings.md .claude/rules/ CLAUDE.md` returns zero files.

---

## Step 1.6: Sync symlinks and verify

**Objective**: Remove stale symlinks, regenerate correct ones, final verification grep.

**Execution Model**: Haiku

**Implementation**:

1. Remove stale symlinks in .claude/agents/ pointing to old names (now non-existent targets):
   - vet-fix-agent.md, design-vet-agent.md, outline-review-agent.md, runbook-outline-review-agent.md, plan-reviewer.md, review-tdd-process.md
   - quiet-task.md, quiet-explore.md, tdd-task.md, runbook-simplification-agent.md, test-hooks.md
   - Note: vet-agent.md symlink if present (source file deleted in 1.1)

2. Remove stale symlink in .claude/skills/:
   - vet → (old target, now renamed to review)

3. Run: `cd agent-core && just sync-to-parent` to regenerate all symlinks from agent-core/ to .claude/.

4. Verify new symlinks exist and resolve:
   - .claude/agents/ should contain symlinks: corrector.md, design-corrector.md, outline-corrector.md, runbook-outline-corrector.md, runbook-corrector.md, tdd-auditor.md, artisan.md, scout.md, test-driver.md, runbook-simplifier.md, hooks-tester.md (plus unchanged: refactor.md, brainstorm-name.md, remember-task.md, memory-refactor.md, hook-batch-task.md)
   - .claude/skills/ should contain review/ (not vet/)

5. Final verification — grep for ALL old names across production directories:
   ```
   grep -rl "vet-fix-agent\|design-vet-agent\|outline-review-agent\|runbook-outline-review-agent\|plan-reviewer\|review-tdd-process\|quiet-task\|quiet-explore\|tdd-task\|runbook-simplification-agent\|test-hooks\|vet-agent\|vet-taxonomy\|vet-requirement" --include="*.md" --include="*.py" --include="*.json" agent-core/ agents/decisions/ agents/memory-index.md agents/session.md agents/learnings.md .claude/ CLAUDE.md
   ```
   Expected: zero files. If any found: list them and STOP.

**Expected Outcome**: All symlinks valid, pointing to renamed files. Zero stale references in production files.

**Error Conditions**:
- sync-to-parent fails → STOP, examine justfile and error output
- Stale references found → List files and STOP for manual review
- Broken symlinks remain → STOP, check agent-core paths match .claude targets

**Validation**: `find .claude/agents/ -type l -exec test ! -e {} \; -print` returns nothing (no broken symlinks). `find .claude/skills/ -type l -exec test ! -e {} \; -print` returns nothing. Final grep returns zero hits.

---

### Light Checkpoint: Phase 1 Complete

1. **Fix**: Run `just dev` from project root. If any checks fail, diagnose and fix. Commit when passing.
2. **Functional**: Verify renames are real (files exist at new paths, content is updated) — not just filesystem moves with stale content.
3. **Commit**: `git add -A && git commit` with rename summary.
4. **Session restart required** — agent definitions load at session start. New session must use new agent names.

---

### Phase 2: Deslop Restructuring — FR-1 (type: inline)

**2a. Merge prose deslop rules into communication.md:**
- Read agent-core/fragments/deslop.md — extract the 5 prose rules (### Prose section):
  1. State information directly — no hedging, framing, or preamble
  2. Answer immediately — skip acknowledgments and transitions
  3. Reference, never recap — assume the reader has context
  4. Let results speak — no framing around output that's already visible
  5. Commit to your answer — no hedging qualifiers after delivering it
- Add as new subsection `### Prose Quality` in agent-core/fragments/communication.md after the existing 5 numbered rules
- Rules only — strip all ❌/✅ examples (ambient context must be lean)
- Discard principle line ("Slop is the gap between what's expressed and what needed expressing. Deslopping is precision — cutting to the signal, not to the bone.")

**2b. Update project-conventions skill:**
- Read agent-core/skills/project-conventions/SKILL.md
- Remove prose deslop section if present (content now in communication.md, which is ambient/always-loaded)
- Add missing code rule: "Expose fields directly until access control needed" (from deslop.md line 40-42, missing from project-conventions)
- Keep: code quality section, token economy rules, tmp directory rules

**2c. Add skills: frontmatter to code-producing agents:**
- Read agent-core/agents/artisan.md: add `skills: ["project-conventions"]` to YAML frontmatter (or append to existing skills list)
- Read agent-core/agents/test-driver.md: add `skills: ["project-conventions"]` to YAML frontmatter (or append to existing skills list)

**2d. Remove inline code quality duplication from artisan:**
- Read agent-core/agents/artisan.md — find the "Code Quality" section containing rules about docstrings, comments, banners, abstractions, guards, fields, requirements
- Remove the entire "Code Quality" section — this content is now injected via the project-conventions skill added in 2c

**2e. Cleanup — remove deslop.md and stale references:**
- Edit CLAUDE.md: remove the `@agent-core/fragments/deslop.md` line
- `git rm agent-core/fragments/deslop.md`
- Update remaining "deslop" references (update terminology or remove as context dictates):
  - agent-core/README.md — update fragment inventory (remove deslop.md entry)
  - agent-core/skills/memory-index/SKILL.md — update if references deslop fragment
  - agents/memory-index.md — update /when triggers if referencing deslop
  - agents/decisions/operational-practices.md — update deslop references to point to communication.md and project-conventions
  - agents/session.md — update or remove deslop task references (historical context may be kept but updated)

---

### Phase 3: Code Density Decisions — FR-2 (type: inline)

**3a. Add 5 entries to agents/decisions/cli.md:**
- Read plans/reports/code-density-grounding.md for grounded content
- Each entry: general principle first, project instance second (per /ground framing rule)
- Add under appropriate section in cli.md (create new section if needed):

  1. **When Checking Expected State** — Decision: Boolean returns for normal program states, not exceptions. Project: `_git_ok(*args) -> bool` for exit-code checks.
  2. **When Terminating On Error** — Decision: Consolidate display and exit into single call. Project: `_fail(msg, code=1) -> Never`.
  3. **When Formatter Expands Code** — Decision: 5+ lines after opinionated formatting signals abstraction need. Extract helper with default kwargs.
  4. **When Choosing Exception Type** — Decision: Custom exception classes for exceptional events, not ValueError. Lint satisfaction via proper design (custom class), not circumvention (intermediate variable).
  5. **When Structuring Error Handling** — Decision: Context collection at failure site, display at top level. Layers don't overlap.

**3b. Add /when triggers to agents/memory-index.md:**
- Read agents/memory-index.md to match existing trigger format
- Add 5 new triggers under the `agents/decisions/cli.md` section:
  - When checking expected state → `.When Checking Expected State`
  - When terminating on error → `.When Terminating On Error`
  - When formatter expands code → `.When Formatter Expands Code`
  - When choosing exception type → `.When Choosing Exception Type`
  - When structuring error handling → `.When Structuring Error Handling`

---

### Full Checkpoint: All Phases Complete

1. **Fix**: Run `just dev`. Diagnose and fix any failures. Commit.
2. **Vet**: Delegate to corrector (formerly vet-fix-agent) for accumulated changes review. Scope IN: all 3 FRs. Scope OUT: FR-4 codebase sweep, context optimization, prepare-runbook.py updates. Apply all fixes. Commit.
3. **Functional**: Verify:
   - Grep for old names in production files returns zero hits
   - communication.md has 5 new prose rules
   - project-conventions has "Expose fields directly" rule
   - artisan.md and test-driver.md have `skills: ["project-conventions"]`
   - artisan.md has no "Code Quality" section
   - deslop.md deleted, CLAUDE.md @-reference removed
   - cli.md has 5 new decision entries
   - memory-index.md has 5 new /when triggers
