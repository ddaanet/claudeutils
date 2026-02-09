# Vet Review: Phase 1 Runbook

**Scope**: Phase 1 runbook completeness, correctness, and executability
**Date**: 2026-02-09T00:00:00Z

## Summary

Phase 1 runbook defines hook implementation for continuation passing system. The plan is well-structured with 4 steps (registry builder, parser, integration, caching) and clear success criteria. Implementation approach is sound, but has several issues requiring fixes before execution.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Step 1.1: Plugin discovery implementation requires missing dependencies**
   - Location: lines 41-43
   - Problem: Runbook states "Read `~/.claude/settings.json` → `enabledPlugins`" and "Read `~/.claude/plugins/installed_plugins.json`" but design Section "Cooperative Skill Registry" only describes the algorithm — doesn't specify error handling or structure for these files
   - Impact: Implementer must reverse-engineer JSON structure from Claude Code internals without documentation
   - Fix: Add concrete examples of `settings.json` structure (enabledPlugins field), `installed_plugins.json` structure (installPath, scope, projectPath fields), and how scope filtering works
   - Suggestion: Include sample JSON structures in step or reference exploration report if it has examples

2. **Step 1.2: Mode ambiguity when both patterns match**
   - Location: lines 199 (Unexpected Result Handling)
   - Problem: States "Ambiguous parse (multiple interpretations) → prefer Mode 2 over Mode 3" but doesn't define what "ambiguous" means. Input like `/design foo and\n- /plan-adhoc` could match both Mode 2 (connecting word `and`) and Mode 3 (`and\n- /skill` pattern)
   - Fix: Specify exact precedence order: Mode 3 must check for `and\n- ` pattern first (more specific), then Mode 2 checks for inline connecting words. Make this explicit in parser implementation section.

3. **Step 1.2: Default exit appending logic incomplete for edge case**
   - Location: lines 156-176 (Default exit appending section)
   - Problem: Design D-3 and handoff special case (line 249-252 in design.md) state "/handoff without --commit is terminal" but Step 1.2 default exit examples don't show how parser handles `/handoff` in the middle of a chain. Example: `/design, /handoff, /commit` — should `/handoff` (without flag) consume default exit of `/commit` or be terminal?
   - Clarification needed: If `/handoff` appears mid-chain without `--commit`, does it:
     - A) Block continuation (chain becomes `/design` → `/handoff` [terminal])
     - B) Pass through (`/handoff` has no default-exit but user-specified `/commit` continues)
   - Fix: Add explicit rule and test case for `/handoff` mid-chain behavior

4. **Step 1.3: Missing continuation format for empty continuation**
   - Location: lines 290 (Unexpected Result Handling)
   - Problem: States "Empty continuation after parsing → emit terminal continuation (empty string)" but integration code doesn't show what this looks like in `additionalContext` format
   - Fix: Add example showing terminal case output (e.g., when user types just `/commit`)

### Minor Issues

1. **Step 1.1: Success criteria mismatch with cooperative skills count**
   - Location: line 91
   - Note: States "Registry contains all 6 cooperative skills" but design Section "Initial Cooperative Skills" (lines 217-226) lists 6 skills, and 5 need refactoring per Component 3 (lines 371-374). Mismatch isn't an error but could confuse: are there 5 or 6 skills total? Clarify that `/commit` is cooperative but already terminal.

2. **Step 1.2: Validation scenario 6 flag handling is vague**
   - Location: line 207
   - Note: "Flag handling: `/handoff --commit` → default exit includes `/commit`" is a test case but doesn't specify whether this tests PARSING (does parser detect `--commit`?) or DEFAULT EXIT LOOKUP (does registry return correct exit for handoff+flag combo?). Registry structure in Step 1.1 doesn't show how flag-dependent default-exit is stored.

3. **Step 1.3: Integration code uses undefined variable `continuation_entries`**
   - Location: lines 245-262 (integration code block)
   - Note: Line 261 uses `continuation_entries[1:]` to get remainder, but this assumes `continuation_entries` is a list. Earlier code (lines 245-248) builds it as a list of strings. Correct, but line 262's args string-building for first Skill call uses `parsed['continuation'][0].get('args', '')` — inconsistency between using `continuation_entries` (formatted strings) vs `parsed['continuation']` (dict entries). Not wrong but potentially confusing.

4. **Step 1.4: Cache path hash algorithm not specified**
   - Location: line 319
   - Note: "Hash derived from: scanned paths" but doesn't say what hashing algorithm. MD5? SHA256? Just concatenate paths? For cache isolation, different projects scanning same plugin paths should have different caches. Consider including project directory in hash input.

5. **Phase Checkpoint: Test commands use `echo` with JSON containing newlines**
   - Location: lines 416-424
   - Note: Mode 3 test uses `echo '{"prompt": "/design plans/foo and\n- /plan-adhoc\n- /orchestrate"}'` — shell `echo` may not preserve literal `\n`. Better to use `printf` or heredoc, or specify this is pseudo-code and actual test must construct JSON properly.

## Positive Observations

- Clear separation of concerns: registry builder → parser → integration → caching
- Comprehensive validation scenarios in Step 1.2 (8 test cases align with design Component 4)
- Error handling specified at each step (malformed YAML, missing files, corrupted cache)
- Design references (D-1, D-6, D-7) correctly cited in context sections
- Expected Outcome and Success Criteria defined for every step
- Unexpected Result Handling anticipates edge cases (ambiguity, malformed input, cache failures)
- Phase checkpoint provides concrete manual verification commands
- Target file and current size noted upfront (105 lines → ~225-255 lines with additions)

## Recommendations

1. **Before execution**: Examine `~/.claude/settings.json` and `~/.claude/plugins/installed_plugins.json` structure (if available) and add concrete JSON examples to Step 1.1. If structure is unknown, flag this as a prerequisite investigation task.

2. **Parser mode precedence**: Add explicit rule to Step 1.2: "Mode detection order: (1) Check Mode 3 pattern (`and\n- /skill`), (2) Check Mode 2 pattern (inline `, /` or connecting words). First match wins."

3. **Mid-chain handoff rule**: Clarify in Step 1.2 whether `/handoff` without `--commit` mid-chain terminates the chain or allows continuation. Add test case to validation list.

4. **Terminal continuation example**: Show what `additionalContext` looks like when user types `/commit` (empty continuation case).

5. **Cache hash**: Specify hash algorithm in Step 1.4 (suggest: SHA256 of concatenated sorted paths + project directory).

## Next Steps

1. Address Major Issues #1-4 (add JSON structure examples, mode precedence, mid-chain handoff rule, terminal continuation format)
2. Optionally address Minor Issues #2, #4, #5 (flag handling test clarity, cache hash spec, checkpoint test command format)
3. Verify no missing design decision coverage by cross-referencing D-1 through D-7
4. Proceed to implementation

---

**Review complete.** Phase 1 runbook is executable with minor fixes. No fundamental design misalignments detected.
