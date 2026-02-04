# Vet Review: Task Prose Keys Implementation

**Scope**: Uncommitted changes replacing hash token system with prose key validation
**Date**: 2026-02-04T18:30:00Z

## Summary

Implementation successfully replaces hash token system (#PNDNG → #xK9f2) with prose key validation using task names as identifiers. Core functionality complete: validator detects duplicates within session.md, checks disjointness with learning keys, and integrates with precommit. Context recovery script updated to search by task name. All tests pass.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

**1. Outdated documentation in execute-rule.md**
   - Location: agent-core/fragments/execute-rule.md:78-80, 132-142
   - Problem: Documentation still describes old token system with `#PNDNG` placeholders and token generation during precommit. Lines 78-80 say "run `agent-core/bin/task-context.sh <token>`" and "Tokens are generated during precommit (`#PNDNG` → unique token)". Task format examples (lines 137-138) show hash tokens: `#xK9f2`, `#bQ7mN`. Field description (line 142) says "Token: 5-char base62 identifier (written as `#PNDNG` by handoff, replaced by precommit)".
   - Fix: Update documentation to reflect prose key system:
     - Line 78: Change `<token>` to `<task-name>`
     - Line 80: Replace entire description with explanation that task names serve as keys and context recovery uses `git log -S` to find introduction commit
     - Lines 132-142: Remove token field from examples and field descriptions, update format to match current session.md style (no hash tokens)
     - Line 28, 34, 36: Update STATUS display documentation to remove `[#token]` references

**2. Missing git history check validation**
   - Location: agent-core/bin/validate-tasks.py:144-150
   - Problem: Git history check (FR-3) implemented but not empirically validated. Requirements specify uniqueness check against git history for NEW tasks only. Implementation uses `git log -S` which is correct approach, but unclear if it properly handles merge commits (FR-6: "compare against before side of diff against all parents after first").
   - Fix: Need test case verifying merge commit handling. Create scenario with task name in parent branch, add different task with same name in feature branch, merge, verify validator detects collision.

**3. Context recovery script lacks usage documentation**
   - Location: agent-core/bin/task-context.sh:4-6
   - Problem: Usage message updated to say "task-name" but lacks concrete example of expected format. Old token format was unambiguous (#xK9f2), but task names have spaces and special characters. Users may be unsure whether to quote, how to handle case sensitivity.
   - Fix: Add example to usage message showing proper quoting: `task-context.sh 'Task prose keys'`. Line 5 already has placeholder for this.

### Minor Issues

**1. validator-consolidation requirements outdated**
   - Location: Referenced in grep output - plans/validator-consolidation/requirements.md:80
   - Note: Requirements doc still references task-token.py with description "Token expansion, will become key validation". Should be updated to reflect that validate-tasks.py now exists and task-token.py is deleted.

**2. No validation of task format compliance**
   - Location: agent-core/bin/validate-tasks.py:17 (TASK_PATTERN)
   - Note: Validator extracts task names using pattern but doesn't validate that task lines follow complete format: `- [ ] **Name** — description | model`. Missing `—` separator or description would silently pass. Not critical since malformed tasks fail at execution time, but early detection would be helpful.

**3. Learning key extraction skips first line hardcoded**
   - Location: agent-core/bin/validate-tasks.py:44-46
   - Note: Code comment says "exclude H1 document title" and uses `if i == 1: continue`. This assumes H1 is always line 1, which may not hold if learnings.md has frontmatter or leading blank lines. More robust: skip lines matching `^# ` pattern rather than hardcoding line number.

**4. Case sensitivity in task name comparison**
   - Location: agent-core/bin/validate-tasks.py:126, 137
   - Note: Task name comparison uses `.lower()` for case-insensitive matching, which is correct. However, git log -S (line 87) is case-sensitive by default. A task "Fix Bug" vs "fix bug" might not be detected as duplicate if one exists in history with different casing. Consider adding `--regexp-ignore-case` flag to git log command.

## Positive Observations

**Clean deletion of obsolete code**
- task-token.py completely removed rather than commented out or archived
- Follows project convention: "Delete obsolete code, don't archive it"

**Proper project root discovery**
- Uses CLAUDE.md as root marker (line 25), consistent with "Root marker for scripts" learning
- Avoids pitfall of using `agents/` directory which can exist in subdirectories

**Token-efficient validation**
- On-demand git history search (O(1) per new task) instead of loading all historical keys
- Fulfills NFR-3: "No loaded history"

**Error reporting quality**
- Clear error messages with line numbers and task names
- Duplicate detection reports first occurrence location (line 129-130)
- Exit code 1 on validation failure for precommit integration

**Empirical testing during implementation**
- Test runs show duplicate detection works correctly
- Learning key conflict detection validated
- Error handling for non-existent tasks confirmed

**Graceful degradation**
- Missing files return empty list rather than crashing (lines 109-110, 116-117)
- No staged changes case handled cleanly (line 79-80)

## Recommendations

**1. Add merge commit test**
Create test case validating FR-6 (merge commit handling). Current implementation may already handle this correctly since git diff --cached shows unified diff against all parents, but empirical validation would confirm.

**2. Consider format validation warnings**
Add optional check for complete task format compliance. Could be warning-level (non-blocking) to catch malformed task lines early without breaking workflow.

**3. Update handoff workflow documentation**
If handoff skill or related documentation mentions `#PNDNG` placeholder generation, update those references. Grep showed no handoff skill in `.claude/skills/` but found `agents/modules/src/handoff.semantic.md` and `agents/rules-handoff.md` which may need review.

## Next Steps

1. **REQUIRED:** Update execute-rule.md to remove all token system references (issue #1)
2. **REQUIRED:** Fix task-context.sh usage example to show quoting (issue #3)
3. **RECOMMENDED:** Add merge commit handling test (issue #2)
4. **OPTIONAL:** Update validator-consolidation requirements doc (minor issue #1)
5. **OPTIONAL:** Consider case-insensitive git log search (minor issue #4)
