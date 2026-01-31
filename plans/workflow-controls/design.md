# Workflow Controls

**Problem:** No default behavior for listing pending tasks. Agents pattern-match ambiguous prompts ("next?") to execute-rule and start working. No shortcut system for common commands. Workflow skills lack a universal termination pattern.

**Mode:** General (infrastructure, workflow tooling)
**Downstream:** `/plan-adhoc`

---

## Requirements

### Functional

- **Three session continuation modes** with distinct triggers:
  - STATUS (default): list pending tasks with metadata, wait for instruction
  - EXECUTE: drive first pending task to completion, stop
  - EXECUTE+COMMIT: execute, then handoff → commit
- **Shortcut system** via UserPromptSubmit hook for common commands
- **Universal tail behavior**: all workflow skills end with status display

### Non-Functional

- Shortcuts must not add perceptible latency (command hook, not prompt hook)
- Zero false positives on shortcut matching
- Fragment defines vocabulary for inline use (agent understands shortcuts in natural language)
- Hook provides mechanical expansion for standalone use (reliable, no LLM interpretation needed)

### Out of Scope

- IDE integration for shortcuts
- Custom per-project shortcut definitions
- Shortcut for `/design` crystallization trigger (natural language "go" works fine)
- Design vet agent (tracked separately as pending task — `create design-vet-agent`)

---

## Architecture

### Two-Layer Shortcut System

**Layer 1: UserPromptSubmit hook** — mechanical expansion for standalone shortcuts.
Fires on every user prompt. Python script does regex matching internally. If match found, emits `additionalContext` with expansion. Original prompt passes through unchanged.

**Note:** UserPromptSubmit does not support the `matcher` field in settings.json — it always fires on every prompt. All matching logic lives inside the Python script, not in Claude Code's hook dispatch.

**Layer 2: Fragment** — vocabulary table the agent reads from CLAUDE.md context.
Agent understands shortcuts when used inline in natural language ("then hc" in a sentence). No hook needed — agent infers from the table.

Both layers are needed. The hook is the fast/reliable path for bare shortcuts. The fragment is the understanding layer for inline use.

### Two Tiers of Shortcuts

**Tier 1 — Commands** (exact match, entire message):

| Input | Expansion | Semantics |
|-------|-----------|-----------|
| `s` | #status | List tasks with metadata, wait |
| `x` | #execute | Smart: resume in-progress OR start first pending |
| `xc` | #execute --commit | Execute → handoff → commit → status |
| `r` | #resume | Strict: continue in-progress only (error if nothing in-progress) |
| `h` | /handoff | Update session.md → status |
| `hc` | /handoff --commit | Handoff → commit → status |
| `ci` | /commit | Commit → status |

**`x` vs `r` behavior matrix:**

| State | `x` (#execute) | `r` (#resume) |
|-------|-----------------|----------------|
| In-progress task exists | Resume it | Resume it |
| No in-progress, pending exists | Start first pending | Error: "Nothing in progress" |
| No tasks at all | "No pending tasks" | Error: "Nothing in progress" |

`x` is the general-purpose "do the next thing." `r` is strict resume-only — use when you explicitly want to continue interrupted work and would rather error than accidentally start something new.

**Tier 2 — Directives** (colon prefix, `^shortcut:\s`):

| Input | Semantics |
|-------|-----------|
| `d: <text>` | Discussion mode — analyze, don't execute or implement |
| `p: <text>` | Record pending task — append to session.md Pending Tasks, don't execute |

`p:` behavior: Hook injects directive. Agent appends task to session.md Pending Tasks section using metadata format. Agent infers model/restart defaults if not specified by user. Example: `p: fix login bug` → agent adds `- [ ] **Fix login bug** — | sonnet` to session.md.

**Not in shortcut system** (natural language, Claude already understands):
- `y`, `yes`, `g`, `go`, `continue` — confirmation/proceed
- These don't need hook expansion

### Matching Strategy

```
Tier 1: ^shortcut$ (exact match, entire stripped message)
Tier 2: ^shortcut:\s (colon prefix, rest is argument/context)
No match: exit 0 silently (pass through)
```

The colon in tier 2 prevents false positives: `d: trade-offs` matches, `do you think...` does not. One extra character, zero ambiguity.

**Note:** All matching is performed inside the hook script. UserPromptSubmit does not support Claude Code's `matcher` field — it is always invoked on every prompt submission.

### Hook Output Format

The hook outputs JSON with `hookSpecificOutput.additionalContext` (discrete context injection, not shown in transcript):

**Tier 1 example** (`x`):
```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "[SHORTCUT: #execute] Smart execute: if an in-progress task exists, resume it. Otherwise start the first pending task from session.md. Drive to completion, then stop."
  }
}
```

**Tier 2 example** (`d: trade-offs of approach A vs B`):
```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "[DIRECTIVE: DISCUSS] Discussion mode. Analyze and discuss only — do not execute, implement, or invoke workflow skills. The user's topic follows in their message."
  }
}
```

**No match:** Exit 0 with no output (silent pass-through).

### Universal Tail Behavior

All workflow skills terminate with the same sequence:

```
[skill work] → handoff → commit → STATUS display
```

**STATUS display** is rendered by the agent (not a script). The agent reads session.md Pending Tasks section and formats output:

```
Next: <first pending task name>
  `<command to start it>`
  Model: <recommended model> | Restart: <yes/no>

Pending:
- <task 2 name> (<model if non-default>)
- <task 3 name>
- ...
```

**Graceful degradation:**
- Missing session.md or no Pending Tasks section → "No pending tasks."
- Tasks in old format (no metadata) → display with defaults (model=sonnet, restart=no)
- Missing model field → default to sonnet
- Missing restart field → default to no

Skills affected:
- `/commit` — already shows next task; update to full STATUS format
- `/handoff` — add STATUS as default tail, replacing current session size advice (model recommendation subsumed by STATUS display's "Model:" field). When `--commit` specified, skip STATUS (commit shows it)
- `/design` — after step 6 (Apply Fixes), add step 7: tail-call `/handoff --commit`. Chains: design → handoff → commit → STATUS
- `/plan-adhoc`, `/plan-tdd` — already tail into handoff → commit; STATUS comes from commit

### Session.md Task Metadata Convention

Extend task notation to carry metadata for STATUS display:

```markdown
## Pending Tasks
- [ ] **Implement ambient awareness** — `/plan-adhoc plans/ambient-awareness/design.md` | sonnet | no restart
- [ ] **Design runbook identifiers** — `/design plans/runbook-identifiers/problem.md` | opus
```

Format: `- [ ] **Name** — \`command\` | model | restart?`

Restart field is optional (omit = no). Model field defaults to sonnet if omitted.

The STATUS display reads this from session.md. The handoff skill (and handoff-haiku) writes it in this format. handoff-haiku's mechanical merge preserves metadata verbatim since it carries forward unresolved items unchanged.

---

## Key Design Decisions

### Command hook over prompt hook for shortcuts
**Decision:** Python command hook, not LLM prompt hook.
**Rationale:** Shortcut matching is deterministic regex — no LLM reasoning needed. Command hooks are faster (no API call), cheaper (no tokens), and more predictable. Prompt hooks add latency to every single user message.

### Colon convention for directives over sigil prefix
**Decision:** `d: text` over `.d text`.
**Rationale:** The colon reads naturally ("discuss: trade-offs"), is familiar from label syntax, and disambiguates from natural language without a foreign sigil. The period convention (`.x`) was considered but doesn't read as naturally for directive-with-argument patterns.

### No sigil for command shortcuts
**Decision:** Bare `x`, `s`, `hc` etc. with exact match.
**Rationale:** These are standalone messages — the user types nothing else. Exact match has zero false-positive risk for single/two-character strings as entire messages. Adding a sigil (`.x`) penalizes the common case to prevent a non-existent collision.

### Fragment + hook (two layers) over hook-only
**Decision:** Both layers.
**Rationale:** The hook handles standalone use reliably. But users naturally embed shortcuts in prose ("design this then hc"). The hook can't match that (not exact match), but the agent can interpret it from the vocabulary table in the fragment. Two layers, complementary purposes.

### STATUS as universal tail over explicit flags
**Decision:** Every terminal workflow action ends with STATUS display by default.
**Rationale:** Eliminates `--status` flag proliferation. The user always knows where they stand. If a skill chains into commit, commit shows STATUS. If handoff doesn't chain into commit, handoff shows STATUS directly. One invariant, no flags.

### `x` as smart execute, `r` as strict resume
**Decision:** `x` checks in-progress first (resume if found, else start pending). `r` errors if nothing in-progress.
**Rationale:** `x` is the general "do the next thing" — it should always make progress. `r` is for when you specifically want to continue interrupted work and would rather error than accidentally start a new task. Distinct intents, distinct commands.

### Keep `execute-rule.md` filename
**Decision:** Rewrite contents of `execute-rule.md` in place. Do not rename file.
**Rationale:** CLAUDE.md imports via `@agent-core/fragments/execute-rule.md`. Renaming requires updating all import references across projects that use agent-core as a submodule. The content change is what matters, not the filename.

---

## Implementation Notes

### Files to Create

**`agent-core/hooks/userpromptsubmit-shortcuts.py`**
UserPromptSubmit hook script. Reads JSON from stdin, extracts `prompt` field. Tier 1: exact match against command table. Tier 2: regex `^(\w+):\s` against directive table. On match: output JSON with `hookSpecificOutput.additionalContext`. On no match: exit 0 silently. Script must be fast (no imports beyond stdlib json/re/sys).

### Files to Modify

**`agent-core/fragments/execute-rule.md`** — Rewrite contents
Define four modes: STATUS (default), EXECUTE (`#execute`, `x`), EXECUTE+COMMIT (`#execute --commit`, `xc`), RESUME (`#resume`, `r`). Include shortcut vocabulary table (both tiers). Define STATUS display format. Specify: ambiguous prompts ("next?", "what's next?", startup) default to STATUS. Include `x` vs `r` behavior matrix.

**`agent-core/skills/commit/SKILL.md`** — Update post-commit section
Lines 185-200: Replace bare "Next: task" with full STATUS format. Agent reads session.md task metadata. Display model, restart status, remaining pending tasks. Graceful degradation for old-format tasks.

**`agent-core/skills/handoff/SKILL.md`** — Add STATUS tail
After handoff completes (session.md updated), display STATUS listing as final output. This replaces the current post-handoff session size advice — model recommendation is subsumed by STATUS display's "Model:" field. When `--commit` specified, skip STATUS (commit shows it after committing).

**`agent-core/skills/handoff-haiku/SKILL.md`** — Task metadata format
When writing Pending Tasks section, use metadata convention. Mechanical merge preserves metadata format verbatim (no judgment needed — carry forward unchanged).

**`agent-core/skills/design/SKILL.md`** — Add step 7: tail-call
After step 6 (Apply Fixes), add step 7: invoke `/handoff --commit` as tail-call. Chains: design → handoff → commit → STATUS.

**`.claude/settings.json`** — Add UserPromptSubmit hook
Add hook entry pointing to `agent-core/hooks/userpromptsubmit-shortcuts.py`. No `matcher` field (UserPromptSubmit doesn't support it).

### Testing Strategy

- Test shortcut hook with sample JSON inputs (each shortcut, each directive, non-matching messages)
- Test STATUS display format parsing from session.md (with metadata, without metadata, missing file)
- Test tail behavior chain: design → handoff → commit → status
- Test inline shortcut comprehension: agent understands "then hc" in prose
- Test no-match: regular messages pass through without hook interference
- **Note:** Hook changes require session restart to take effect — test by restarting Claude Code after each hook modification

---

## Dependencies

**Before this work:**
- None (standalone infrastructure improvement)

**After this work:**
- All future session.md entries should use task metadata convention
- All new workflow skills should tail into handoff → commit → status
- Design vet agent (separate pending task) should follow artifact-return pattern established here
