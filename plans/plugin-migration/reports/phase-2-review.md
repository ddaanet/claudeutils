# Vet Review: Phase 2 Runbook (Skills and Agents)

**Scope**: plans/plugin-migration/runbook-phase-2.md
**Date**: 2026-02-07T23:45:00Z

## Summary

Phase 2 runbook covers agent/skill structure verification and creation of `/edify:init` and `/edify:update` skills. The runbook has clear step structure with inline verification commands. Found issues with skill content specification completeness, validation criteria misalignment, and missing design alignment details.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Incomplete skill content specification**
   - Location: Step 2.3, "Skill content structure" section (lines 137-165)
   - Problem: The specification provides high-level sections (Purpose, When to Use, Behavior, etc.) but lacks the actual procedural content that the skill should contain. A skill is executable instructions for Claude to follow, not just documentation structure. The runbook doesn't specify WHAT actions the skill tells Claude to perform (e.g., "Run `test -d agent-core/` to detect mode", "Create directory with `mkdir -p agents`", "Copy template from X to Y").
   - Fix: Add a "Procedure" subsection after "Behavior" that specifies the concrete steps Claude should execute when the skill is invoked. Include specific bash commands, file operations, and decision logic. The skill should read like a mini-runbook, not a README.

2. **Same issue for /edify:update skill**
   - Location: Step 2.4, "Skill content structure" section (lines 221-249)
   - Problem: Same structural specification without procedural content. The skill needs concrete "do this, then this" instructions, not just behavioral descriptions.
   - Fix: Add procedural steps similar to Step 2.3 fix above. Include version comparison logic, file copy commands (for consumer mode), and version marker update steps.

3. **Skill count validation inconsistency**
   - Location: Step 2.2 checkpoint (line 291)
   - Problem: Validation expects 18 total skills (16 existing + 2 new), but Step 2.1 validates 14 agents. The design document states "16 skills symlinked via `just sync-to-parent`" (design.md line 10, outline.md line 10). The checkpoint should validate the correct expected count.
   - Fix: Verify the current skill count in agent-core/skills/. If 16 is correct, change validation to `[ "$skill_count" -eq 18 ]`. If different, update both the design reference citation and the validation logic to match reality.

4. **Missing YAML frontmatter validation detail**
   - Location: Steps 2.3 and 2.4, "Validation" sections
   - Problem: "YAML frontmatter is valid" is vague. What constitutes valid? The runbook should specify what to check: required fields (name, description, version), correct `name` value (`edify:init` / `edify:update`), version format, no YAML syntax errors.
   - Fix: Expand validation criteria to: "YAML frontmatter contains required fields (name, description, version), name matches `edify:init` / `edify:update`, version follows semver format (1.0.0), no YAML parse errors when loaded."

5. **Consumer mode handling incomplete**
   - Location: Step 2.3 (lines 162-164) and Step 2.4 (lines 241-244)
   - Problem: The runbook specifies "Add TODO markers" for consumer mode but doesn't specify WHERE in the skill content to add them or what the exact marker text should be. Design decision D-7 defers consumer mode but doesn't provide a standard TODO format.
   - Fix: Specify exact location and format, e.g., "In the Behavior section, add a subsection '### Consumer Mode (Deferred)' with text: 'Consumer mode fragment copying not yet implemented. See design decision D-7. Dev mode (submodule) implementation only.'"

### Minor Issues

1. **Ambiguous "skill invokable" test**
   - Location: Step 2.3 Success Criteria (line 189), Step 2.4 Success Criteria (line 272)
   - Note: "Skill invokable via `/edify:init` command" is not testable without restarting Claude Code and manually trying the command. The checkpoint should clarify this is a manual post-restart test, not an inline bash verification.
   - Suggestion: Change to "Skill discoverable after restart (manual test: restart Claude, run `/help`, verify skill appears)"

2. **Missing design reference for skill discovery**
   - Location: Steps 2.3 and 2.4, "Design References" sections
   - Note: Both steps reference components and decisions but don't reference the auto-discovery mechanism (Component 1, design.md lines 105-106: "Auto-discovery handles skills, agents, and hooks from conventional directory locations... `skills/*/SKILL.md`").
   - Suggestion: Add "Component 1: Plugin auto-discovery (skills/*/SKILL.md pattern)" to Design References for both steps.

3. **Idempotency guarantees section placement**
   - Location: Step 2.3 (lines 159-165)
   - Note: The "Idempotency guarantees" subsection in skill content structure is good for `/edify:init` (which is idempotent by design) but not needed for `/edify:update` (which is explicitly a sync/overwrite operation). Step 2.4 doesn't include this subsection, which is correct, but the asymmetry isn't explained.
   - Suggestion: Add a note in Step 2.3 explaining why idempotency matters for init but not update: "Init scaffolds missing pieces (safe to re-run); update overwrites (explicit sync action)."

4. **Unclear "clear temp file" instruction**
   - Location: Step 2.4, Version marker update subsection (line 247)
   - Note: "Clear temp file: `tmp/.edify-version-checked`" — should this be part of the skill's procedure? Or is this describing what the skill should do when invoked? The phrasing is ambiguous (sounds like a manual instruction to the implementer, not skill content).
   - Suggestion: Rephrase to "Skill removes temp file `tmp/.edify-version-checked` to reset once-per-session gate after version update."

5. **Checkpoint manual test lacks detail**
   - Location: Phase 2 Checkpoint, manual test section (lines 298-301)
   - Note: The manual test says "Run: claude --plugin-dir ./agent-core" but doesn't specify what to do if Claude is already running. Should the user exit first? The checkpoint should clarify the restart requirement.
   - Suggestion: Change to "1. Exit current Claude Code session\n2. Restart: `claude --plugin-dir ./agent-core`\n3. Verify `/edify:init` and `/edify:update` in `/help` output"

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

1. **Add procedural content to skill specifications**: Steps 2.3 and 2.4 should include a "Procedure" subsection with concrete bash commands and file operations that the skill instructs Claude to execute. Use the pattern from existing skills in agent-core/skills/ as a reference.

2. **Verify skill count accuracy**: Before execution, run `find agent-core/skills -mindepth 1 -maxdepth 1 -type d | wc -l` to confirm the baseline is 16 (as stated in design) or update references if different.

3. **Standardize TODO marker format**: Create a consistent format for consumer mode deferral markers across all skills (and future components). Add this to design.md as a mini-decision or implementation note.

4. **Add skill content examples**: Consider adding a reference to an existing simple skill (e.g., `/token-efficient-bash`) as a template for skill structure. This would help the implementer understand the level of procedural detail needed.

5. **Clarify checkpoint restart timing**: The checkpoint manual test should explicitly state when to restart (after all verification commands pass) and what to do if skills don't appear (check plugin.json exists, verify directory structure).

## Next Steps

1. Fix Major Issue #1: Add procedural content to Step 2.3 skill specification
2. Fix Major Issue #2: Add procedural content to Step 2.4 skill specification
3. Fix Major Issue #3: Verify skill count and update checkpoint validation
4. Fix Major Issue #4: Expand YAML frontmatter validation criteria
5. Fix Major Issue #5: Specify TODO marker format and placement
6. Address minor issues (reword ambiguous tests, add missing references, clarify instructions)
7. After fixes: re-review for completeness
8. Proceed to Phase 3 planning (Hook Migration)
