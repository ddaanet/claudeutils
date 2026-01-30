# Vet Review: Commit Skill Unification (Uncommitted Changes in agent-core)

**Scope**: Uncommitted changes in agent-core submodule (git diff HEAD)
**Date**: 2026-01-30T16:45:30Z

## Summary

This changeset implements the commit skill unification design, merging `/commit` and `/commit-context` into a single `/commit` skill with a `--context` flag. The implementation successfully inlines gitmoji selection, eliminates the nested skill invocation bug, and removes the obsolete commit-context skill entirely. The changes are well-executed and align with the design specification.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Handoff still invokes /handoff skill despite design claiming to avoid nested skill bug**
   - Location: skills/commit/SKILL.md:131
   - Problem: The design document (line 59-65) claims to "keep `/handoff` invocation" as an "acceptable interruption," but this directly contradicts the stated goal of fixing the nested skill bug (#17351). The commit skill will still cause a context switch requiring user "continue" when it invokes `/handoff` via Skill tool.
   - Suggestion: Either (a) inline the handoff logic similar to gitmoji, or (b) update the design rationale to acknowledge that the nested skill bug is only *partially* fixed (gitmoji no longer interrupts, but handoff still does). The current state is inconsistent with "fix nested skill interruption bug."

2. **Design document diverges from implementation on handoff inlining**
   - Location: plans/commit-unification/design.md:15-16, 59-65
   - Problem: Design line 15-16 states "Inline handoff execution" under Requirements but then Decision #2 (line 59-65) reverses this to "Keep `/handoff` invocation." This creates ambiguity about whether the requirement was changed or the implementation deviated.
   - Suggestion: Update the design document's Requirements section (line 15-16) to match the actual decision: "Keep `/handoff` invocation (acceptable interruption point)."

3. **Missing handoff-protocol.md reference file mentioned in design**
   - Location: plans/commit-unification/design.md:36
   - Problem: Design shows `references/handoff-protocol.md` in the proposed directory structure, but this file was never created (since handoff wasn't inlined). The design and implementation diverged here.
   - Suggestion: Update design.md line 36 to remove the handoff-protocol.md reference, keeping only gitmoji-index.txt in the references/ structure.

### Minor Issues

1. **Inconsistent "Context Gathering" section title after --context flag addition**
   - Location: skills/commit/SKILL.md:174
   - Note: Section titled "Context Gathering" now has qualifier "(Non-Context Mode)" which is accurate but makes the section title misleading. Consider renaming to "Discovery Mode Context Gathering" or "Git Discovery (Non-Context Mode)" for clarity.

2. **Git diff HEAD note is slightly misleading**
   - Location: skills/commit/SKILL.md:182
   - Note: Comment says "git diff HEAD separately - already included in `git status -vv` output" but `git status -vv` shows staged diffs, not the full HEAD diff. This is technically correct (you don't need `git diff HEAD` *separately* since `git status -vv` shows both staged and unstaged), but the phrasing could be clearer: "git diff HEAD separately - staged/unstaged diffs shown in git status -vv output."

3. **Update script references skills/gitmoji pattern that may confuse future maintainers**
   - Location: skills/commit/scripts/update-gitmoji-index.sh:1-30
   - Note: The script is well-adapted and correctly outputs to references/gitmoji-index.txt. However, there's no comment indicating this was copied/adapted from skills/gitmoji/scripts/. Consider adding a header comment: "# Adapted from skills/gitmoji/scripts/update-gitmoji-index.sh" for maintainability.

## Positive Observations

- **Complete deletion of obsolete skill**: The commit-context directory is fully removed (verified with `ls -la`), following the code removal principle correctly. No archive, no comments, clean deletion.

- **Perfect gitmoji index copy**: The gitmoji-index.txt file is byte-for-byte identical to the source (verified with `diff`), containing all 78 entries including the custom compress and robot emojis.

- **Well-structured flag documentation**: The unified skill clearly documents all flag combinations (--context, --test, --lint, --no-gitmoji) with usage examples and TDD workflow patterns.

- **Inline gitmoji protocol is concise and clear**: The inlined gitmoji selection (lines 140-147) is well-executed - reads the reference file, does semantic matching, prefixes commit title. This eliminates the nested skill invocation without losing functionality.

- **Token-efficient bash references**: Multiple mentions of the `/token-efficient-bash` skill pattern show good adherence to project token economy principles.

- **Validation-first execution order**: Pre-commit validation happens before git discovery, failing fast if tests/lint fail before producing verbose git output. This is excellent token efficiency.

## Recommendations

1. **Clarify the nested skill bug fix scope**: Decide whether to (a) inline handoff logic to fully fix the nested skill bug, or (b) update all documentation (design, commit message, session.md) to reflect that the bug is *partially* fixed (gitmoji interruption eliminated, handoff interruption kept as acceptable). The current state presents this as a full fix when it's partial.

2. **Update design document retroactively**: Since the design document is the source of truth for implementation decisions, update it to match the actual implementation (remove handoff-protocol.md from structure diagram, clarify requirement vs decision on handoff).

3. **Add maintenance comments to copied files**: Both gitmoji-index.txt and update-gitmoji-index.sh are copies from the gitmoji skill. Add header comments indicating source and update procedure to prevent future confusion.

4. **Consider /handoff inlining for consistency**: The handoff skill is larger (6.5K) than gitmoji, but the primary operation (updating session.md with completed work) could be extracted to a much simpler inline protocol. The full skill includes examples and extensive guidance, but the core execution is straightforward. This would fully resolve the nested skill bug rather than working around it.

## Next Steps

1. **Fix design/implementation alignment**: Update design.md to match implementation (remove handoff-protocol.md, clarify Requirements vs Decisions)
2. **Clarify nested skill bug fix scope**: Update commit message, session.md, and any documentation to reflect partial fix vs full fix
3. **Add source attribution comments**: Update gitmoji-index.txt and update-gitmoji-index.sh with "Copied from skills/gitmoji/" headers
4. **Test all flag combinations**: Run the test strategy from design.md (lines 127-133) to verify functionality
5. **Run just sync-to-parent**: Execute in agent-core to clean up stale commit-context symlink in claudeutils (per session.md task list)
