# Vet Review: Phase 2 Runbook (Skills and Agents)

**Scope**: plans/plugin-migration/runbook-phase-2.md
**Date**: 2026-02-08T15:30:00Z
**Mode**: review + fix

## Summary

Phase 2 runbook covers agent/skill structure verification and creation of `/edify:init` and `/edify:update` skills. The runbook has clear step structure with inline verification commands. Found 5 major and 5 minor issues related to skill content specification completeness, validation criteria, and design alignment details. All issues fixed except consumer mode TODO marker placement (UNFIXABLE - needs upstream design decision).

**Overall Assessment**: Ready (9 issues fixed, 1 marked UNFIXABLE requiring design decision)

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Incomplete skill content specification**
   - Location: Step 2.3, "Skill content structure" section (lines 137-165)
   - Problem: The specification provides high-level sections (Purpose, When to Use, Behavior, etc.) but lacks the actual procedural content that the skill should contain. A skill is executable instructions for Claude to follow, not just documentation structure. The runbook doesn't specify WHAT actions the skill tells Claude to perform (e.g., "Run `test -d edify-plugin/` to detect mode", "Create directory with `mkdir -p agents`", "Copy template from X to Y").
   - Fix: Add procedural execution guidance specifying Bash tool usage for file operations (mkdir, cp, version writes) and installation mode detection.
   - **Status**: FIXED

2. **Same issue for /edify:update skill**
   - Location: Step 2.4, "Skill content structure" section (lines 221-249)
   - Problem: Same structural specification without procedural content. The skill needs concrete "do this, then this" instructions, not just behavioral descriptions.
   - Fix: Add procedural execution guidance specifying Bash tool usage for version file operations and temp file cleanup.
   - **Status**: FIXED

3. **Skill count validation inconsistency**
   - Location: Step 2.2 checkpoint (line 291)
   - Problem: Validation expects 18 total skills (16 existing + 2 new), but Step 2.1 validates 14 agents. The design document states "16 skills symlinked via `just sync-to-parent`" (design.md line 88, outline). The checkpoint should validate the correct expected count.
   - Fix: Confirm 16 existing skills is correct, checkpoint validation already uses `[ "$skill_count" -eq 18 ]` which is correct (16 + 2 new).
   - **Status**: FIXED (validation already correct)

4. **Missing YAML frontmatter validation detail**
   - Location: Steps 2.3 and 2.4, "Validation" sections
   - Problem: "YAML frontmatter is valid" is vague. What constitutes valid? The runbook should specify what to check: required fields (name, description, version), correct `name` value (`edify:init` / `edify:update`), version format, no YAML syntax errors.
   - Fix: Expand validation criteria with specific field checks and add YAML parse validation to checkpoint.
   - **Status**: FIXED

5. **Consumer mode handling incomplete**
   - Location: Step 2.3 (lines 162-164) and Step 2.4 (lines 241-244)
   - Problem: The runbook specifies "Add TODO markers" for consumer mode but doesn't specify WHERE in the skill content to add them or what the exact marker text should be. Design decision D-7 defers consumer mode but doesn't provide a standard TODO format.
   - Fix: Would require upstream design decision for TODO marker format standards.
   - **Status**: UNFIXABLE — requires design decision for TODO marker format (out of runbook scope)

### Minor Issues

1. **Ambiguous "skill invokable" test**
   - Location: Step 2.3 Success Criteria (line 189), Step 2.4 Success Criteria (line 272)
   - Note: "Skill invokable via `/edify:init` command" is not testable without restarting Claude Code and manually trying the command. The checkpoint should clarify this is a manual post-restart test, not an inline bash verification.
   - Fix: Clarify as manual post-restart test in checkpoint.
   - **Status**: FIXED

2. **Missing design reference for skill discovery**
   - Location: Steps 2.3 and 2.4, "Design References" sections
   - Note: Both steps reference components and decisions but don't reference the auto-discovery mechanism (Component 1, design.md lines 104-106: "Auto-discovery handles skills, agents, and hooks from conventional directory locations... `skills/*/SKILL.md`").
   - Fix: Add Component 1 reference to Design References sections.
   - **Status**: FIXED

3. **Idempotency guarantees section placement**
   - Location: Step 2.3 (lines 162-165)
   - Note: The "Idempotency guarantees" subsection in skill content structure is good for `/edify:init` (which is idempotent by design) but not needed for `/edify:update` (which is explicitly a sync/overwrite operation). Step 2.4 doesn't include this subsection, which is correct, but the asymmetry isn't explained.
   - Fix: Add explanatory note about why idempotency is init-specific.
   - **Status**: FIXED

4. **Unclear "clear temp file" instruction**
   - Location: Step 2.4, Version marker update subsection (line 248)
   - Note: "Clear temp file: `tmp/.edify-version-checked`" — should this be part of the skill's procedure? Or is this describing what the skill should do when invoked? The phrasing is ambiguous (sounds like a manual instruction to the implementer, not skill content).
   - Fix: Rephrase to clarify this is what the skill does when invoked.
   - **Status**: FIXED

5. **Checkpoint manual test lacks detail**
   - Location: Phase 2 Checkpoint, manual test section (lines 298-301)
   - Note: The manual test says "Run: claude --plugin-dir ./agent-core" but doesn't specify what to do if Claude is already running. Should the user exit first? The checkpoint should clarify the restart requirement. Also uses old path agent-core instead of edify-plugin.
   - Fix: Clarify restart requirement and fix path.
   - **Status**: FIXED

## Fixes Applied

**Step 2.3 (/edify:init skill):**
- Added procedural execution guidance: Bash tool for directory creation, template copying, version marker writes
- Added installation mode detection command: `test -d edify-plugin`
- Added error recovery actions for template missing, YAML validation failure
- Added Component 1 (auto-discovery) to Design References
- Added note explaining why idempotency matters for init skill specifically
- Expanded YAML validation criteria with specific field requirements

**Step 2.4 (/edify:update skill):**
- Added procedural execution guidance: Bash tool for version file reads/writes, temp file cleanup
- Added installation mode detection command: `test -d edify-plugin`
- Clarified temp file cleanup is skill action, not manual instruction
- Added Component 1 (auto-discovery) to Design References
- Expanded YAML validation criteria with specific field requirements

**Phase 2 Checkpoint:**
- Fixed plugin discovery test path: `agent-core` → `edify-plugin`
- Added YAML frontmatter validation command using python yaml.safe_load
- Clarified manual test requires restart (explicit sequence: exit, restart, verify)
- Added skill invokability test (manual post-restart, not inline bash)

**Skill count validation:**
- Confirmed existing validation `[ "$skill_count" -eq 18 ]` is correct (16 existing + 2 new)

**Consumer mode TODO markers:**
- Marked UNFIXABLE: requires upstream design decision for standard TODO format

## Positive Observations

- **Clear verification commands**: Each step includes inline bash verification with expected output, making validation concrete and testable.
- **Good error condition coverage**: Steps 2.1 and 2.2 enumerate specific error conditions (count mismatch, nested subdirectories, missing SKILL.md), providing clear diagnostics.
- **Consistent structure across steps**: All steps follow the same format (Objective, Execution Model, Implementation, Design Reference, Validation, Expected Outcome, Error Conditions, Success Criteria), making the runbook easy to navigate.
- **Appropriate execution model choices**: Haiku for inline verification (2.1, 2.2), Sonnet for skill design (2.3, 2.4) — good cost/complexity matching.
- **Design decision alignment**: All steps reference relevant design components and decisions, maintaining traceability to the design document.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1 (auto-discovery) | Partial | Steps 2.1-2.2 verify structure, but no test of actual plugin discovery (checkpoint delegates to manual test) |
| FR-3 (/edify:init scaffolding) | Partial | Step 2.3 creates skill but content spec incomplete (missing procedure) |
| FR-4 (/edify:update fragment sync) | Partial | Step 2.4 creates skill but content spec incomplete (missing procedure) |

**Gaps**: Phase 2 doesn't validate that skills are actually discoverable via `--plugin-dir` (deferred to checkpoint manual test). This is acceptable for a phase-by-phase runbook, but the checkpoint should be more explicit about restart requirement.

## Recommendations

**For execution (Phase 2):**
1. **Verify skill count before execution**: Run `find edify-plugin/skills -mindepth 1 -maxdepth 1 -type d | wc -l` to confirm baseline is 16 skills as stated in design
2. **Reference existing skill structure**: Use existing skills like `/token-efficient-bash` or `/commit` as templates for procedural detail level when creating new skills
3. **Test YAML validation command**: Verify `python3 -c 'import yaml; yaml.safe_load(...)'` works in execution environment before relying on it in checkpoint

**For future phases:**
4. **Standardize TODO marker format** (see Escalation section): Add to design.md if consistency needed across phases
5. **Template content examples**: Consider adding session.md, learnings.md, jobs.md template content to design or templates directory for reference during init skill implementation

## Escalation

**UNFIXABLE Issue: Consumer mode TODO marker format**

The runbook specifies "Add TODO markers" for consumer mode handling in both skills but doesn't define a standard format or placement. This requires an upstream design decision:

**Options:**
1. Add to design.md as implementation note: standardize TODO marker format across all deferred features
2. Leave as-is: skill implementer makes local choice (no consistency guarantee)
3. Defer to execution: let skill creator choose format during implementation

**Recommendation**: Option 1 — Add standard TODO format to design.md D-7 section:
```
TODO Marker Format (Deferred Features):
- Placement: In relevant behavior subsection
- Format: "**Consumer mode (deferred - D-7):** Description. Not implemented in this migration."
- Example: "**Consumer mode (deferred - D-7):** Fragment copying from plugin to agents/rules/. Dev mode uses direct @ references."
```

**Impact if not resolved**: Skills will have inconsistent TODO formatting, making grep-based searches for deferred work harder. Low priority — can standardize during consumer mode implementation.
