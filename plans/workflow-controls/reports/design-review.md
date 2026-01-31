# Design Review: Workflow Controls

**Reviewer:** Opus 4.5
**Document:** `plans/workflow-controls/design.md`
**Date:** 2026-01-31

---

## Verdict: NEEDS_REVISION

Two critical issues (hook API mismatch, `#resume` vs `#execute` overlap) and several high-priority items need addressing before planning.

---

## Critical Issues

### C1. UserPromptSubmit does not support matchers

The design says "UserPromptSubmit hook" with a Python script doing regex matching. The settings.json configuration shown in existing hooks uses `matcher` fields to filter events. However, per the official Claude Code hooks documentation, **UserPromptSubmit does not support matchers** -- it always fires on every occurrence. This is fine for the design's intent (the script does its own matching internally), but the settings.json entry must omit any `matcher` field. The design should explicitly note this to prevent confusion during implementation.

**Severity:** CRITICAL (implementation will work, but the design's framing of "matching strategy" could mislead the implementer into putting a matcher in settings.json, which would be silently ignored)

**Fix:** Add a note under "Matching Strategy" section: "Note: UserPromptSubmit does not support the `matcher` field in settings.json. The regex matching is performed inside the Python script itself, not by Claude Code's hook dispatch."

### C2. `#resume` overlaps with `#execute` for in-progress tasks

The design introduces `#resume` (`r`) as a separate mode, but the existing execute-rule.md already handles in-progress tasks: "If in-progress task exists: Resume work on that task." The design's shortcut table has both `x` (execute = "drive first pending task") and `r` (resume = "continue in-progress task"). This creates ambiguity:

- What does `x` do when there's an in-progress task? Skip it and start the next pending one? Or resume it?
- What does `r` do when there's no in-progress task? Error? Fall through to first pending?

The current execute-rule.md resolves this by having `#execute` check for in-progress first, then pending. The design splits this into two commands without specifying the edge cases.

**Severity:** CRITICAL (agents will receive both shortcuts and need unambiguous behavior)

**Fix:** Define the full decision matrix:
- `x` with in-progress task: resume it (same as current execute-rule behavior) OR error "use `r` to resume"
- `r` with no in-progress task: error "nothing in progress" OR fall through to first pending
- Document which approach was chosen and why

---

## High Priority Issues

### H1. Hook output JSON format needs specification

The design says the hook "emits `additionalContext` with expansion" but does not specify the exact JSON output format. Per the Claude Code docs, there are two valid approaches:

- Plain text stdout (simpler, shown in transcript)
- JSON with `hookSpecificOutput.additionalContext` (more discrete)

The design should specify which format to use. Recommendation: Use the JSON format with `hookSpecificOutput` since the expansion text is a behavioral directive, not conversational output. Example:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "User shortcut 'xc' expanded to: #execute --commit. ..."
  }
}
```

**Severity:** HIGH (implementer needs exact format to write the script)

### H2. STATUS display parsing is underspecified

The design says "STATUS display parses this from session.md" but doesn't specify:

- Who parses it -- the hook? The agent reading the fragment? A helper script?
- What happens when session.md doesn't exist or has no Pending Tasks section?
- What happens when task metadata is in the old format (no `| model | restart?` suffix)?

STATUS display is the universal tail, so it will be invoked frequently. Parsing failures need graceful degradation.

**Fix:** Specify:
- STATUS is displayed by the agent (not a script) -- it reads session.md and formats output
- Missing metadata fields use defaults: model=sonnet, restart=no
- If session.md missing or no pending tasks: display "No pending tasks."
- Old-format tasks (without metadata) display with defaults

### H3. Design vet agent scope exceeds stated purpose

The design includes a "design-vet agent" (`agent-core/agents/design-vet.md`) as a dedicated opus agent for design review. However:

- The existing `/design` skill already vets via an opus subagent (Step 5: "Delegate to opus subagent for review")
- The new design-vet agent would be a **separate** opus agent file, which means it has different context than an inline opus Task delegation
- The session.md pending tasks already list "Create design-vet-agent" as a separate deferred task

This design bundles the design-vet agent with workflow controls, but it's really a separate concern. The workflow-controls design should reference it as a dependency or future enhancement rather than including it as a deliverable.

**Fix:** Either (a) remove design-vet agent from this design's scope (it's already tracked as a separate pending task) and note it as a future enhancement, or (b) if keeping it, specify how it differs from the current inline opus vet in the `/design` skill and what triggers the switch.

### H4. Fragment file naming/renaming unclear

The design says to rewrite `execute-rule.md` and "rename conceptually to 'session continuation.'" It's ambiguous whether the file should be renamed (`session-continuation.md`) or just have its contents rewritten while keeping the filename. Since CLAUDE.md imports it via `@agent-core/fragments/execute-rule.md`, renaming the file requires updating all import references.

**Fix:** Explicitly state: either "rename file to `session-continuation.md` and update all `@` references" or "keep filename `execute-rule.md`, update contents only."

---

## Medium Priority Issues

### M1. `d:` and `p:` directives interact with skill invocation syntax

The tier 2 directive `d: text` uses a colon-space prefix. This is close to other colon-prefixed patterns in Claude Code (e.g., label syntax in YAML frontmatter). More importantly, the design doesn't specify what the hook outputs for tier 2 matches. For tier 1, the expansion is a behavioral directive. For tier 2, the "argument" (`text` in `d: text`) needs to be passed through. The hook output format for directives needs specification.

**Fix:** Add an example of tier 2 hook output. E.g., for `d: trade-offs of approach A vs B`:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "MODE: Discussion only. Analyze and discuss, do not execute or implement. User query: trade-offs of approach A vs B"
  }
}
```

### M2. `p:` (pending) directive has no validation

The `p: task description` directive records a pending task in session.md. But the design doesn't specify:
- Does the agent just add it to the Pending Tasks section?
- Does it use the new metadata format (`| model | restart?`)?
- What if the user provides incomplete metadata?
- Is this a hook-only expansion (the hook tells the agent what to do) or does it require a skill?

**Fix:** Specify the expected behavior: hook injects `additionalContext` instructing the agent to append the task to session.md Pending Tasks in the metadata format. Agent infers model/restart defaults if not specified.

### M3. handoff-haiku skill not mentioned for task metadata format update

The design mentions updating `handoff/SKILL.md` and `handoff-haiku/SKILL.md` for the task metadata convention, but only the "Files to Modify" section mentions `handoff-haiku`. The handoff-haiku skill has a completely different merge protocol (mechanical, no judgment). The metadata format update needs to work with its mechanical approach.

**Fix:** Confirm that handoff-haiku's mechanical merge will preserve the metadata format (it should, since it carries forward unresolved items verbatim). Note this explicitly.

### M4. Tail behavior for `/handoff` creates a behavioral change

The design says `/handoff` should display STATUS as its tail. Currently, `/handoff` ends with session size advice and model recommendations (lines 105-138 of SKILL.md). Adding STATUS display changes the output format. The design should clarify: does STATUS replace the current session size advice, or is it shown in addition?

**Fix:** Specify: STATUS display replaces the current post-handoff advice. The model recommendation is subsumed by the STATUS display's "Model: recommended model" field.

### M5. No `--commit` tail specified for design skill

The design says `/design` should "tail into handoff -> commit -> STATUS after crystallization + vet." But the existing design skill has no `--commit` flag concept. The implementation note says "Add universal tail" but doesn't specify the mechanism. Is this a new tail-call chain coded into the skill, or a flag?

**Fix:** Specify: After step 6 (Apply Fixes), add step 7 that invokes `/handoff --commit` as a tail-call. This chains naturally: design -> handoff -> commit -> STATUS.

---

## Low Priority Issues

### L1. Shortcut `ci` for `/commit` may be unexpected

`ci` traditionally means "check in" (from SVN/CVS era) or is used for "continuous integration." While it maps to `/commit` here, some users might expect `c` instead. The design chose `ci` (presumably to avoid single-letter `c` being too easy to accidentally trigger). This is a minor naming concern, not a blocker.

### L2. Testing strategy doesn't mention hook restart requirement

The testing strategy lists unit tests for the hook but doesn't mention that hook changes require session restart to take effect (per Claude Code docs: "Claude Code captures a snapshot of hooks at startup"). Testers need to restart after each hook modification.

### L3. SessionStart hook mentioned as "optional"

The design mentions "Optionally add SessionStart hook for status reminder reinforcement." This should be removed or committed to. Optional items in designs create ambiguity during planning. Either include it with rationale or cut it.

---

## Consistency Checks

### Checked: No conflicts found
- Shortcut table doesn't conflict with existing skill invocation patterns (`/` prefix)
- UserPromptSubmit hook coexists with existing PreToolUse and PostToolUse hooks in settings.json
- Task metadata format is backward-compatible (old tasks without metadata will work with defaults)
- The `#execute` hashmark convention doesn't conflict with Markdown heading syntax (only relevant in files, not in user prompts)

### Checked: workflows-terminology.md alignment
- The design's tail-call chain (handoff -> commit -> STATUS) aligns with the documented post-planning pattern
- The STATUS display replaces the current "Next: task" display in commit skill, which is consistent

---

## Summary of Required Fixes

| ID | Severity | Fix |
|----|----------|-----|
| C1 | CRITICAL | Note that UserPromptSubmit has no matcher support; matching is script-internal |
| C2 | CRITICAL | Define behavior matrix for `x` vs `r` with/without in-progress tasks |
| H1 | HIGH | Specify exact JSON output format for hook (recommend `hookSpecificOutput`) |
| H2 | HIGH | Specify who renders STATUS, error handling for missing/malformed session.md |
| H3 | HIGH | Remove design-vet agent from scope or justify inclusion |
| H4 | HIGH | Clarify whether execute-rule.md is renamed or just rewritten |
| M1 | MEDIUM | Add tier 2 hook output example |
| M2 | MEDIUM | Specify `p:` directive behavior and metadata handling |
| M3 | MEDIUM | Confirm handoff-haiku compatibility with metadata format |
| M4 | MEDIUM | Clarify STATUS vs existing session size advice in handoff |
| M5 | MEDIUM | Specify mechanism for design skill tail (Step 7: tail-call `/handoff --commit`) |
