# Continuation Passing Design

## Problem

Skills hardcode their exit tail-calls (e.g., `/design` always invokes `/handoff --commit`). This creates rigid chains that users cannot compose. A user wanting `/design, /plan-adhoc and /orchestrate` must manually invoke each skill sequentially across session restarts.

**Goal:** Replace hardcoded tail-calls with a continuation passing system where:
- Users specify chains in natural prose
- Skills consume the next continuation entry and tail-call it
- Default exits are appended automatically (backward compatible)
- Sub-agents never see continuation metadata

## Requirements

**Source:** `plans/continuation-passing/requirements.md`

**Functional:**
- FR-1: Prose continuation syntax — addressed by hook parser (delimiter detection + registry lookup)
- FR-2: Sequential execution — addressed by peel-first-pass-remainder protocol
- FR-3: Continuation consumption — addressed by cooperative skill protocol
- FR-4: Structured continuation (multi-line) — addressed by `and\n- /skill` list marker detection
- FR-5: Prose-to-explicit translation — addressed by registry matching with empirical validation
- FR-6: Sub-agent isolation — addressed by convention + explicit prohibition in skill protocol
- FR-7: Cooperative skill protocol — addressed by frontmatter declaration + consumption protocol

**Non-functional:**
- NFR-1: Light cooperation — skills understand protocol, not specific downstream skills
- NFR-2: Context list for cooperation detection — frontmatter scanning + registry cache
- NFR-3: Ephemeral continuations — passed through execution, never persisted

**Constraints:**
- C-1: No sub-agent leakage — continuation stripped from Task tool prompts
- C-2: Explicit stop — empty continuation = terminal (no tail-call)

**Out of scope:**
- FR-8: Uncooperative skill wrapping (explicitly optional in requirements)
- Cross-session continuation (not in requirements, tracked in orchestrate-evolution)
- Mid-chain error recovery (deferred to error handling framework design)

## Architecture

### System Overview

```
User input: "/design plans/foo, /plan-adhoc and /orchestrate"
    │
    ▼
[UserPromptSubmit hook — userpromptsubmit-shortcuts.py]
    │ 1. Detect multi-skill input (registry lookup)
    │ 2. Split: current skill + continuation entries
    │ 3. Look up last skill's default-exit from frontmatter
    │ 4. Build full chain: [plan-adhoc, orchestrate, handoff --commit, commit]
    │ 5. Inject via additionalContext (JSON structure)
    ▼
[Claude processes /design skill]
    │ Reads continuation from additionalContext
    │ Executes design work (sub-agents: NO continuation)
    │ Consumes first entry → tail-call: Skill("plan-adhoc", args="... [CONTINUATION: /orchestrate, /handoff --commit, /commit]")
    ▼
[Claude processes /plan-adhoc skill]
    │ Reads continuation from Skill args suffix
    │ Consumes first entry → tail-call: Skill("orchestrate", args="... [CONTINUATION: /handoff --commit, /commit]")
    ▼
[Claude processes /orchestrate skill]
    │ Consumes first entry → tail-call: Skill("handoff", args="--commit [CONTINUATION: /commit]")
    ▼
[Claude processes /handoff skill]
    │ Consumes first entry → tail-call: Skill("commit")
    ▼
[Claude processes /commit skill]
    │ Empty continuation → terminal
    │ Displays STATUS
    ▼
[Done]
```

### Three Components

**1. Hook parser** — Parses user input, builds continuation chain, injects via `additionalContext`

**2. Cooperative skill protocol** — ~5-8 lines per skill replacing hardcoded tail-calls. Read continuation → consume first → tail-call with remainder.

**3. Skill frontmatter declarations** — `continuation.cooperative: true` and `continuation.default-exit: [...]` in YAML frontmatter.

## Key Design Decisions

### D-1: Hook as parsing layer

**Decision:** UserPromptSubmit hook handles all continuation parsing centrally.

**Rationale:** More reliable than LLM parsing within skill context. Centralized logic. Hook fires before Claude processes input, so continuation metadata is available when skill loads. Existing `userpromptsubmit-shortcuts.py` is the natural extension point.

**Alternative rejected:** Fragment-only approach (CLAUDE.md instruction telling Claude to chain). Works for simple cases but unreliable for structured continuations (FR-4) and provides no sub-agent isolation guarantee.

### D-2: Explicit passing via Skill args

**Decision:** Continuation is serialized as a suffix in the Skill tool's `args` parameter.

**Format:** `[CONTINUATION: /skill1 arg1, /skill2 arg2]`

- Bracket-delimited to distinguish from regular args
- Each entry: skill reference with optional args, comma-separated
- Skills parse this suffix, extract first entry, pass remainder

**First invocation:** Continuation comes from `additionalContext` (hook-injected). Subsequent invocations: continuation comes from `args` suffix.

**Rationale:** Context length degrades recall. Explicit passing is deterministic. The `args` parameter is the natural transport — it's already how skills receive user input.

**Alternative considered:** JSON format for transport. Rejected: adds parsing complexity, escaping overhead. The comma-separated format within brackets is sufficient — skill args rarely contain `, /skillname` patterns, and registry-based disambiguation resolves ambiguity.

### D-3: Default exit appending

**Decision:** Hook appends the terminal skill's default exit chain to any user continuation. Skills never need fallback logic.

**Mechanism:**
- Each cooperative skill declares `default-exit` in frontmatter
- Hook reads the LAST skill in the user's chain (or the only skill if solo invocation)
- Last skill's `default-exit` entries are appended to the continuation

**Examples:**

| User input | Last skill | Default exit | Full continuation |
|------------|-----------|--------------|-------------------|
| `/design plans/foo` | design | `[/handoff --commit, /commit]` | `[/handoff --commit, /commit]` |
| `/design, /plan-adhoc` | plan-adhoc | `[/handoff --commit, /commit]` | `[/plan-adhoc, /handoff --commit, /commit]` |
| `/handoff --commit` | handoff | `[/commit]` | `[/commit]` |
| `/commit` | commit | `[]` | `[]` (terminal) |

**Backward compatibility:** Solo skill invocations (the common case) get exactly the same exit behavior as today's hardcoded tail-calls. No user-visible change.

### D-4: Ephemeral continuation lifecycle

**Decision:** Continuations exist only during execution. Never persisted to session.md, learnings.md, or any agent memory file.

**Lifecycle:**
1. Constructed by hook from user input
2. Passed through chain via `additionalContext` → `args`
3. Discarded when chain completes (empty continuation) or terminates on error

**Rationale:** Prevents stale continuation state leaking across sessions. Continuations are execution-time constructs, not session state.

### D-5: Sub-agent isolation by convention

**Decision:** Continuation directives excluded from sub-agent prompts by explicit prohibition in the cooperative skill protocol.

**Mechanism:** Each cooperative skill's continuation protocol section states: "Do NOT include continuation metadata in Task tool prompts." Natural isolation exists because Task tool prompts are explicitly constructed strings — continuation lives in main conversation context, not in prompt construction logic.

**Enforcement feasibility:** A PreToolUse hook could detect `[CONTINUATION:` in Task tool prompts and block. Deferred — convention is sufficient for first-party skills.

**Risk:** Medium. Mitigated by:
- All cooperative skills are first-party (we control content)
- Continuation is read from `additionalContext`/`args`, not from conversation memory
- Skills construct Task prompts explicitly — no accidental inclusion path

### D-6: Parsing strategy

**Decision:** Three parsing modes, progressively complex.

**Mode 1 — Single skill (no continuation):**
Input contains exactly one `/skill` reference (or no `/` prefix at all). Hook passes through unchanged. Default exit appended via `additionalContext`.

**Mode 2 — Inline prose (FR-1, FR-3):**
Multiple `/skill` references on one line, separated by `, /` or connecting words (`and`, `then`, `finally`) before `/skill`.

```
/design plans/foo, /plan-adhoc and /orchestrate
→ current: {skill: "design", args: "plans/foo"}
→ continuation: [{skill: "plan-adhoc"}, {skill: "orchestrate"}]
```

**Mode 3 — Multi-line list (FR-4):**
Pattern: `and\n- /skill args` — the `and` keyword on the first line signals continuation, subsequent `- /skill` lines are entries.

```
/design plans/foo and
- /plan-adhoc design.md
- /orchestrate foo
→ current: {skill: "design", args: "plans/foo"}
→ continuation: [{skill: "plan-adhoc", args: "design.md"}, {skill: "orchestrate", args: "foo"}]
```

**Disambiguation:** Detected skill references validated against cooperative registry. `/plans/foo/bar` won't match any registered skill name. Only registered cooperative skills are recognized as continuation entries.

### D-7: Prose-to-explicit translation (FR-5)

**Decision:** Hook translates connecting prose to explicit skill references by matching against cooperative registry.

**Scope:** Limited to explicit `/skill` references with connecting words. Full natural language resolution (e.g., "then plan it") deferred.

**Rationale:** The review recommended limiting initial scope to explicit references. Natural language skill resolution ("plan it" → `/plan-adhoc`) requires fuzzy matching against skill descriptions, increasing false positive risk. Explicit `/skill` references are unambiguous.

**Empirical validation:** Before shipping, test parsing accuracy against local session corpus (real user inputs from `~/.claude/projects/` transcripts). Measure false positive rate (regular args misidentified as continuations) and false negative rate (explicit continuations missed).

**Validation protocol:**
1. Extract unique user prompts containing `/` from session transcripts
2. Run parser against each, capture parsed continuation
3. Manual review: classify each parse as correct/false-positive/false-negative
4. Target: 0% false positives (args misidentified), <5% false negatives (missed continuations)
5. False negatives are acceptable (user retypes) — false positives corrupt skill args

## Cooperative Skill Protocol

### Frontmatter Schema

Each cooperative skill adds to its YAML frontmatter:

```yaml
continuation:
  cooperative: true
  default-exit: ["/handoff --commit", "/commit"]
```

**Fields:**
- `cooperative: true` — Skill understands continuation passing protocol
- `default-exit` — Ordered list of skill invocations appended when this skill is terminal in user's chain. Empty list `[]` for terminal skills (e.g., `/commit`).

### Initial Cooperative Skills

| Skill | Default Exit | Notes |
|-------|-------------|-------|
| `/design` | `["/handoff --commit", "/commit"]` | Current hardcoded exit |
| `/plan-adhoc` | `["/handoff --commit", "/commit"]` | Current hardcoded exit |
| `/plan-tdd` | `["/handoff --commit", "/commit"]` | Current hardcoded exit |
| `/orchestrate` | `["/handoff --commit", "/commit"]` | Current hardcoded exit |
| `/handoff` | `["/commit"]` | Only when `--commit` flag present |
| `/commit` | `[]` | Terminal, displays STATUS |

### Consumption Protocol

Replace each skill's hardcoded tail-call section with this protocol (~5-8 lines):

```markdown
## Continuation

As the **final action** of this skill:

1. Read continuation from `additionalContext` (first skill in chain) or from `[CONTINUATION: ...]` suffix in Skill args (chained skills)
2. If continuation is empty: stop (terminal)
3. Consume first entry as tail-call target
4. Invoke via Skill tool: `Skill(skill: "<target>", args: "<target-args> [CONTINUATION: <remainder>]")`

**CRITICAL:** Do NOT include continuation metadata in Task tool prompts. Continuation is for main-agent skill chaining only.
```

**Net change per skill:** Remove ~3-10 lines of hardcoded tail-call logic, add ~5-8 lines of continuation protocol. Approximately neutral line count.

### Handoff --commit Special Case

The `/handoff` skill's default exit (`["/commit"]`) only applies when `--commit` flag is present. Without `--commit`, handoff is terminal.

**Hook behavior:** When parsing `/handoff` (without `--commit`), hook treats it as terminal — no default exit appended. When parsing `/handoff --commit`, hook appends `["/commit"]`.

**Implementation:** Hook checks if skill args contain `--commit` flag for the handoff skill specifically. This is the only skill with flag-dependent default exit.

## Hook Implementation

### Integration with userpromptsubmit-shortcuts.py

Continuation parsing extends the existing hook. Processing order:

1. **Tier 1: Exact match shortcuts** (`s`, `x`, `xc`, etc.) — unchanged
2. **Tier 2: Directive shortcuts** (`d:`, `p:`) — unchanged
3. **NEW — Tier 3: Continuation parsing** — if input contains `/skill` reference matching cooperative registry

Tier 3 fires when Tiers 1 and 2 don't match. Non-skill input passes through silently (existing behavior preserved).

### Continuation Parser Logic

```
Input: user prompt string
Output: additionalContext JSON with continuation metadata (or no output for non-skill input)

1. Scan input for /word patterns
2. Match each against cooperative skill registry
3. If no registered skills found → pass through (exit 0)
4. If exactly one skill → Mode 1 (single skill, append default exit)
5. If multiple skills → Mode 2/3 (split into current + continuation)
6. Look up last skill's default-exit from registry
7. Append default-exit entries to continuation
8. Emit additionalContext JSON
```

### additionalContext Format

```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "[CONTINUATION-PASSING]\nCurrent: /design plans/foo\nContinuation: /plan-adhoc, /orchestrate, /handoff --commit, /commit\n\nAfter completing the current skill, invoke the NEXT continuation entry via Skill tool:\n  Skill(skill: \"plan-adhoc\", args: \"[CONTINUATION: /orchestrate, /handoff --commit, /commit]\")\n\nDo NOT include continuation metadata in Task tool prompts."
  }
}
```

**Format choice:** Prose with structured prefix, not raw JSON. Claude processes natural language instructions more reliably than parsing embedded JSON. The `[CONTINUATION-PASSING]` marker enables skills to detect continuation context.

**Single-skill case (Mode 1):** For solo invocations (e.g., `/design plans/foo`), the hook emits continuation with just the default exit:

```
[CONTINUATION-PASSING]
Current: /design plans/foo
Continuation: /handoff --commit, /commit

After completing the current skill, invoke the NEXT continuation entry via Skill tool:
  Skill(skill: "handoff", args: "--commit [CONTINUATION: /commit]")

Do NOT include continuation metadata in Task tool prompts.
```

This replaces the hardcoded tail-call that was previously in the skill itself.

### Cooperative Skill Registry

**Discovery algorithm (3 sources):**

| Source | Discovery path | Files scanned |
|--------|---------------|---------------|
| Project-local | Glob `$CLAUDE_PROJECT_DIR/.claude/skills/**/SKILL.md` | Direct frontmatter scan |
| Enabled plugins | `~/.claude/settings.json` → `enabledPlugins` → `~/.claude/plugins/installed_plugins.json` → `installPath` → glob `<installPath>/skills/**/SKILL.md` | Respects enabled/disabled + scope |
| Built-in skills | Not discoverable (embedded in binary) | Small fallback list |

**Plugin scope filtering:** Installed plugins declare `scope: "user"` or `scope: "project"` with `projectPath`. Project-level settings (`$CLAUDE_PROJECT_DIR/.claude/settings.json`) can override user-level `enabledPlugins`. Hook checks both.

**Cache strategy:** Registry cached to `$TMPDIR/continuation-registry-<hash>.json` where `<hash>` is derived from scanned paths. Cache invalidated when any skill file mtime changes. Expected overhead: <50ms first call, <5ms cached.

**Built-in fallback list:** For skills embedded in Claude Code binary that cannot be discovered via filesystem:
```python
BUILTIN_SKILLS = {
    # Add any built-in skills that need continuation support
    # Currently none known — all cooperative skills are project-local or plugin-based
}
```

### Edge Cases

**Skill args containing `/path`:** The pattern `/word` only matches if `word` is in the cooperative registry. Path arguments like `/plans/foo/bar` contain slashes but `plans` is not a registered skill → not treated as continuation.

**Connecting words in args:** "design and implement" — `and` followed by `implement` which is not a registered skill → treated as regular args, not continuation delimiter.

**Empty continuation after consumption:** Last skill in chain receives `[CONTINUATION: ]` (empty) or no continuation suffix → terminal, no tail-call.

**Non-cooperative skill in chain:** `/design, /some-unknown-skill` — `some-unknown-skill` not in registry → hook ignores it. Only registered cooperative skills form continuation entries. Non-cooperative references remain as regular prose in the user's message.

## Implementation Plan

### Component 1: Hook Modification

**File:** `agent-core/hooks/userpromptsubmit-shortcuts.py`

**Changes:**
- Add cooperative registry builder (scan frontmatter from 3 sources)
- Add continuation parser (Modes 1-3)
- Add Tier 3 processing after existing Tier 1/2
- Add registry cache logic

**Size estimate:** ~120-150 lines added to existing ~100-line script. Consider extracting continuation parsing into separate module (`agent-core/hooks/continuation_parser.py`) if complexity warrants.

### Component 2: Skill Frontmatter

**Files:** 6 SKILL.md files

**Changes per skill:**
- Add `continuation:` block to YAML frontmatter
- Add `Skill` to `allowed-tools` if not present (needed for tail-call)

### Component 3: Skill Refactoring

**Files:** 5 SKILL.md files (all except `/commit` which is already terminal)

**Changes per skill:**
- Remove hardcoded tail-call section (e.g., "CRITICAL: As the final action, invoke `/handoff --commit`")
- Add continuation protocol section (~5-8 lines)
- Remove any intermediate instructions about specific next skills

**Affected skills and their current tail-call locations:**
- `/design` — C.5 "Handoff and Commit" section
- `/plan-adhoc` — Tier 1/2/3 tail-call instructions
- `/plan-tdd` — Phase 5 tail-call instructions
- `/orchestrate` — End of execution tail-call
- `/handoff` — "Tail-Call: --commit Flag" section

### Component 4: Tests

**Unit tests (continuation parser):**
- Single skill: `/design plans/foo` → continuation = default exit only
- Inline prose: `/design, /plan-adhoc` → correct split
- Multi-line: `and\n- /skill` pattern → correct entries
- Path args: `/design /plans/foo/bar` → path not treated as skill
- Connecting words in args: "design and implement" → not a continuation
- Flag handling: `/handoff --commit` → default exit includes `/commit`
- Unknown skill: `/design, /nonexistent` → nonexistent ignored
- Terminal skill: `/commit` → empty continuation

**Unit tests (registry):**
- Frontmatter scanning: extract cooperative + default-exit
- Non-cooperative skills: `cooperative: false` or missing → excluded
- Cache invalidation: mtime change triggers rebuild

**Unit tests (consumption):**
- Peel first entry from `[CONTINUATION: /a, /b, /c]` → target: `/a`, remainder: `[CONTINUATION: /b, /c]`
- Last entry: `[CONTINUATION: /commit]` → target: `/commit`, remainder: empty
- Empty: no `[CONTINUATION:]` → terminal

**Integration test:**
- 2-skill chain: hook parse → first skill reads additionalContext → tail-call → second skill reads args → terminal

**Empirical validation (FR-5):**
- Extract user prompts from session corpus
- Run parser, measure false positive/negative rates
- Target: 0% false positives, <5% false negatives

### Component 5: Documentation

**New fragment:** `agent-core/fragments/continuation-passing.md` — protocol reference for skill developers.

**Updates:**
- `agents/decisions/workflow-optimization.md` — add continuation passing decision
- Skill development guide (`plugin-dev:skill-development`) — mention continuation frontmatter

## Migration Strategy

### Transition Safety

The design ensures backward compatibility at every step:

1. **Hook addition:** New Tier 3 only fires when Tiers 1/2 don't match AND input contains registered skills. Existing shortcuts unchanged.

2. **Frontmatter addition:** Adding `continuation:` to YAML doesn't affect skill loading or existing behavior. Skills work identically with or without this metadata.

3. **Skill refactoring:** Replace hardcoded tail-calls with continuation protocol. The hook always provides default exit, so solo skill invocations produce identical behavior to current hardcoded exits.

**Rollback:** Remove Tier 3 from hook → skills fall back to no continuation in args/additionalContext → continuation protocol section is a no-op (no continuation to consume) → skills terminate without tail-call. Users would need to manually chain skills (current behavior). Frontmatter is inert without the hook.

### Ordering

Recommended implementation order:
1. Frontmatter additions (safe, inert without hook)
2. Continuation protocol in skills (safe, no-op without hook injecting continuations)
3. Hook implementation (activates the system)
4. Tests
5. Documentation
6. Empirical validation (FR-5)

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agents/decisions/workflow-optimization.md` — handoff tail-call pattern, existing workflow decisions
- `agents/decisions/workflow-core.md` — weak orchestrator pattern, TDD workflow integration
- `agent-core/hooks/userpromptsubmit-shortcuts.py` — existing hook to extend
- `agent-core/fragments/claude-config-layout.md` — hook configuration patterns (already in CLAUDE.md)
- `plans/continuation-passing/reports/explore-skill-chaining.md` — exploration results

**Skill files to modify:**
- `agent-core/skills/design/SKILL.md`
- `agent-core/skills/plan-adhoc/SKILL.md`
- `agent-core/skills/plan-tdd/SKILL.md`
- `agent-core/skills/orchestrate/SKILL.md`
- `agent-core/skills/handoff/SKILL.md`
- `agent-core/skills/commit/SKILL.md`

**Context7 references:** None needed — all components are project-internal.

## Next Steps

Route to `/plan-adhoc` for runbook creation. General workflow (not TDD) — this is infrastructure/refactoring work modifying hook scripts and skill definitions.

**Skill-loading directive:** Load `plugin-dev:skill-development` before planning (skill frontmatter modifications).

**Execution model directive:** Skill file edits (SKILL.md modifications) require sonnet — interpreting design intent for protocol text, not mechanical edits.
