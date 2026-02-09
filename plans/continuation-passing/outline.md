# Continuation Passing Design Outline

## Approach

Remove hardcoded tail-calls from skills and replace with continuation passing system. Three components: hook-based parsing, cooperative skill protocol, default exit continuation.

**Core insight:** Skills currently hardcode their exit (`/handoff --commit`). Continuation passing removes these hardcoded exits and implements the exit pattern as the default continuation. The hook always provides a continuation — either user-specified chain + default exit, or just default exit. Skills become simpler: do work → consume next continuation entry → tail-call it.

## Key Decisions

### Parsing layer: UserPromptSubmit hook

Hook parses continuation from user input before skill loads. Injects structured metadata via `additionalContext`. Maintains cooperative skill registry for validation.

**Why hook:** More reliable than LLM parsing within skill context. Centralized parsing logic. Hook fires before Claude processes input, so continuation metadata is available when skill loads.

**Alternative rejected: Fragment-only approach.** A CLAUDE.md fragment telling Claude to chain skills works for simple cases but is unreliable for structured continuations (FR-4) and provides no sub-agent isolation guarantee.

### Continuation transport: Explicit passing via Skill args

- First skill: reads continuation from `additionalContext` (hook-injected)
- Chained skills: receive continuation in Skill tool `args` parameter
- Format: structured suffix that skills can parse
- Each skill peels first entry, passes remainder

**Transport format:** Continuation is serialized as a suffix in the Skill tool's `args` parameter. Format: `[CONTINUATION: /skill1 arg1, /skill2 arg2]`. Each entry is a skill reference with optional args, comma-separated. Skills parse this suffix, extract first entry as next tail-call target, and pass the remainder (re-serialized) to the next skill's args.

**Why not rely on conversation context memory:** Context length degrades recall. Explicit passing is deterministic.

### Ephemeral continuation lifecycle (NFR-3)

Continuations exist only during execution. They are not persisted to session.md, learnings.md, or any agent memory file. Each continuation is constructed by the hook from user input, passed through the chain via args, and discarded when the chain completes or terminates on error. This prevents stale continuation state from leaking across sessions.

### Cooperative skill protocol: Continuation consumption

Skills no longer have hardcoded tail-calls. Instead, every cooperative skill ends with the same protocol:
- Read continuation (from `additionalContext` or Skill args)
- Consume first entry as tail-call target
- Pass remainder in Skill args to next skill

The hook ensures continuation is ALWAYS present (default exit appended). Skills never need fallback logic — there's always a next entry until the terminal skill.

**Protocol size:** ~5-8 lines per skill, replacing existing tail-call instructions (net change is small). Light coupling (NFR-1): skills understand the continuation protocol, not specific downstream skills.

### Default exit appending

Hook appends the terminal skill's default exit chain to any user continuation:

- Each cooperative skill declares `default-exit` in frontmatter (e.g., design: `["/handoff --commit", "/commit"]`)
- Hook reads the LAST skill's default exit and appends it
- Terminal skills (commit) declare empty default exit

**Examples:**
- `/design plans/foo` → continuation: `[handoff --commit, commit]` (design's default exit)
- `/design, /plan-adhoc` → continuation: `[plan-adhoc, handoff --commit, commit]` (plan-adhoc's default exit appended)
- `/handoff --commit` → continuation: `[commit]` (handoff's default exit)
- `/commit` → continuation: `[]` (terminal, no exit)

### Sub-agent isolation: Exclusion by convention + explicit prohibition

Skill protocol states: "Do NOT include continuation metadata in Task tool prompts." Natural isolation exists because Task tool prompts are explicitly constructed — continuation lives in main conversation context.

**Why convention not enforcement:** No mechanism to intercept Task tool prompts. Convention is sufficient given cooperative skills are first-party (we control the content).

### Termination invariant preserved

The exit pattern (`handoff → commit → STATUS`) is always present at the end of every continuation chain — the hook appends it. Satisfies the workflow-optimization decision. Chain always terminates with short STATUS display after commit.

## Parsing Format

### Prose (FR-1, FR-3, FR-5)

Delimiter: `, /` and connecting words (`then`, `and`, `finally`) before `/skill`.

**Prose-to-explicit translation (FR-5):** When user writes natural prose like "then plan it and orchestrate", the hook translates connecting words to explicit skill references by matching against the cooperative registry. "plan it" resolves to `/plan-adhoc` or `/plan-tdd` based on context keywords. Output is always explicit `{skill: "plan-adhoc"}` entries, never prose forwarded to the next skill.

**Empirical validation:** Before shipping FR-5 translation, test parsing accuracy against local session corpus (real user inputs from transcripts). Measure false positive rate (args misidentified as continuations) and false negative rate (continuations missed).

```
/design plans/foo, /plan-adhoc and /orchestrate
→ current: {skill: "design", args: "plans/foo"}
→ continuation: [{skill: "plan-adhoc", args: ""}, {skill: "orchestrate", args: ""}]
```

Disambiguation: match skill names against cooperative registry. `/path/to/file` won't match a registered skill name.

### Multi-line prose (FR-4, simplified)

Structured continuation via prose with list markers — no separate format needed:

```
/design plans/foo and
- /plan-adhoc design.md
- /orchestrate foo
```

Hook detects `and\n- /skill` pattern: the `and` keyword signals continuation, subsequent `- /skill args` lines are explicit continuation entries. Same registry validation as single-line prose.

**Note:** The original FR-4 example (`then:`, `finally:` markers with per-skill context) implies cross-session capabilities (model switching, session restart) that don't exist yet. Those are tracked in orchestrate-evolution. For now, multi-line list prose covers the realistic use cases within a single session.

## Architecture

```
User input: "/design plans/foo, /plan-adhoc and /orchestrate"
    │
    ▼
[UserPromptSubmit hook]
    │ Scan skill frontmatter for cooperative declarations
    │ Parse continuation from input
    │ Look up last skill's default-exit: orchestrate → [handoff --commit, commit]
    │ Build full chain: [plan-adhoc, orchestrate, handoff --commit, commit]
    │ Inject via additionalContext
    ▼
[Claude processes /design skill]
    │ Reads continuation from additionalContext
    │ Executes design work (including Task tool sub-agents)
    │ Sub-agents: NO continuation in prompts (FR-6)
    │ Consumes first entry, tail-calls: Skill("plan-adhoc", args="[CONTINUATION: /orchestrate, /handoff --commit, /commit]")
    ▼
[Claude processes /plan-adhoc skill]
    │ Reads continuation from args
    │ Executes planning work
    │ Consumes first entry, tail-calls: Skill("orchestrate", args="[CONTINUATION: /handoff --commit, /commit]")
    ▼
[Claude processes /orchestrate skill]
    │ Consumes first entry, tail-calls: Skill("handoff", args="--commit [CONTINUATION: /commit]")
    ▼
[Claude processes /handoff skill]
    │ Consumes first entry, tail-calls: Skill("commit")
    ▼
[Claude processes /commit skill]
    │ No continuation → terminal
    │ Displays short STATUS
    ▼
[Done]
```

## Cooperative Skill Registry

**Discovery via skill frontmatter (NFR-2).** Hook enumerates available skills from filesystem and config files. Skills self-declare continuation support in YAML frontmatter.

**Frontmatter schema:**
```yaml
continuation:
  cooperative: true
  default-exit: ["/handoff --commit", "/commit"]
```

**Discovery algorithm (3 sources):**

| Source | Discovery path | Files |
|--------|---------------|-------|
| Project-local | Glob `$CLAUDE_PROJECT_DIR/.claude/skills/**/SKILL.md` | Direct frontmatter scan |
| Enabled plugins | `~/.claude/settings.json` → `enabledPlugins` map → `~/.claude/plugins/installed_plugins.json` → resolve `installPath` → glob `<installPath>/skills/**/SKILL.md` | Respects enabled/disabled status and scope (user/project) |
| Built-in skills | Not discoverable (embedded in binary) | Small fallback list for any that need continuation support |

**Plugin scope filtering:** Plugin installs declare `scope: "user"` or `scope: "project"` with `projectPath`. Project settings override user settings for `enabledPlugins`.

**Performance:** ~30 lines Python. Read 3 config files + glob skill directories. Cache registry to temp file, check mtime on subsequent calls — negligible per-prompt overhead.

**Initial cooperative skills and their default exits:**
- `/design` → default-exit: `["/handoff --commit", "/commit"]`
- `/plan-adhoc` → default-exit: `["/handoff --commit", "/commit"]`
- `/plan-tdd` → default-exit: `["/handoff --commit", "/commit"]`
- `/orchestrate` → default-exit: `["/handoff --commit", "/commit"]`
- `/handoff` → default-exit: `["/commit"]`
- `/commit` → default-exit: `[]` (terminal, displays short STATUS)

**Hook behavior:** When user input contains multiple `/skill` references, hook validates each against registry. If first skill is non-cooperative, no injection (user chains manually). If cooperative, hook builds full continuation chain with last skill's default exit appended.

## Scope

**In:** FR-1 through FR-7, NFR-1 through NFR-3, C-1, C-2 (all core requirements)
**Out:** FR-8 (uncooperative wrapping — explicitly optional in requirements, deferred), cross-session continuation (not in requirements)
**Deferred:** Mid-chain error recovery (Requirements OQ-3), bidirectional context flow (not in requirements)

## Trade-offs

**Mid-chain session state:** No `/handoff` runs between chained skills, so partial progress is lost on failure. Acceptable for short chains (2-3 skills). Could add lightweight progress tracking later.

**Protocol overhead vs reliability:** ~5-8 lines per skill vs relying on LLM memory. Explicit protocol is more reliable and enables sub-agent isolation.

**Hook complexity:** Parsing logic in UserPromptSubmit hook adds complexity. Mitigated by keeping parser simple (delimiter detection + registry lookup).

## Open Questions

1. **Continuation delimiter edge cases:** What if skill args naturally contain `, /something`? Registry-based disambiguation handles registered skills but not arbitrary paths. (Requirements OQ-1: detecting skill content vs continuation content — registry lookup is primary mechanism; paths like `/plans/foo/bar` won't match registered skill names.) — Considered solid.

2. **Multi-line prose sufficiency:** List marker format (`and\n- /skill args`) is primary — explicit and unambiguous. Simple bare multi-line (`/skill\n/skill`) could be a secondary detection mode (all subsequent lines match registered skill) but deferred to avoid false positives from prose skill mentions.

3. **Error mid-chain:** Current design: stop chain on error (C-2). Chain terminates, remaining continuation is discarded (NFR-3 ephemeral). Future: configurable error handling — see pending task "error handling framework" which addresses this as the dual of skill/task composition (analogous to promise error handlers and nested exception handlers).

## Implementation Components

1. **Hook modification:** `userpromptsubmit-shortcuts.py` — add continuation parser alongside existing shortcut expansion. Parser detects multi-skill input, splits into current + continuation, scans skill frontmatter for cooperative declarations, appends default exit from last skill's frontmatter.
2. **Skill refactoring:** Remove hardcoded tail-call instructions from 5 cooperative skills (`/design`, `/plan-adhoc`, `/plan-tdd`, `/orchestrate`, `/handoff`). Replace with continuation protocol section (~5-8 lines): read continuation from args/additionalContext, consume first entry, tail-call with remainder.
3. **Skill frontmatter:** Add `continuation:` block to cooperative skill YAML frontmatter declaring `cooperative: true` and `default-exit` chain.
4. **Tests:**
   - Unit: Continuation parsing (prose delimiters, multi-line, edge cases with path-like args)
   - Unit: Frontmatter scanning (cooperative detection, default-exit extraction)
   - Unit: Continuation consumption (peel first entry, re-serialize remainder)
   - Unit: Default exit appending (last skill's exit, terminal detection)
   - Empirical: FR-5 prose-to-explicit accuracy against local session corpus
   - Integration: 2-skill chain end-to-end (hook parse → first skill → tail-call → second skill → default exit → STATUS)
5. **Documentation:** Fragment for continuation passing protocol (added to CLAUDE.md or skill development guide)

## Risk Assessment

- **Low:** Basic prose continuation (FR-1, FR-2, FR-3)
- **Low:** Multi-line prose (FR-4 simplified) — extends existing delimiter logic to newlines
- **Medium:** Sub-agent isolation relies on convention (FR-6, C-1)
- **Medium:** Skill refactoring — removing hardcoded tail-calls requires careful transition
- **Low:** Backward compatibility (hook always provides default exit = same behavior as today)
