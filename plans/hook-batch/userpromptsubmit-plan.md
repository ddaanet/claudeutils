# UserPromptSubmit Hook Improvements

**Context:** Discussion about context optimization (fragment demotion from CLAUDE.md) identified the UserPromptSubmit hook as a key enforcement mechanism. Several improvements make the hook a stronger workflow correctness layer: line-based shortcut matching, skill-editing guard, directive refinements, and new directives.

**Files:**
- `agent-core/hooks/userpromptsubmit-shortcuts.py` (839 lines, main change)
- `agent-core/fragments/communication.md` (remove AskUserQuestion directive — already applied)

## Changes

### 1. Tier 1: Line-based shortcut matching

**Current:** `if prompt in COMMANDS` — entire prompt must be exactly the shortcut.
**Change:** Scan lines for shortcuts on their own line. A shortcut triggers when it appears as the sole content of any line (stripped), even within a larger prompt.

- Match: `s` on its own line within multi-line prompt → triggers status expansion
- No match: `s` embedded in a word or sentence → no trigger
- When triggered within larger prompt: inject expansion as additionalContext, full prompt passes through unchanged

Implementation: Replace line 772 check with line-scanning loop. First shortcut match wins.

### 2. Tier 2: Directive scope clarification

**Current:** `d:` and `p:` additionalContext doesn't clarify scope.
**Change:** Add scope note to both expansions: directive applies to the prefixed section (everything following the directive marker), not just one line. `d:` is often multiline.

Update `_DISCUSS_EXPANSION` and `_PENDING_EXPANSION` to append:
```
Scope: applies to all content following the directive prefix in this message.
```

### 3. Tier 2: p: dual output (match d: pattern)

**Current:** `p:` sends full expansion text to both additionalContext and systemMessage.
**Change:** Follow `d:` pattern — concise systemMessage, full expansion in additionalContext.

```python
# systemMessage (user sees):
'[PENDING] Capture task, do not execute.'

# additionalContext (agent sees):
# Full _PENDING_EXPANSION text
```

### 4. Tier 2: Implement missing q: and learn: directives

Documented in execute-rule.md but not implemented in hook.

**q: (quick question)**
```python
_QUICK_EXPANSION = (
    '[QUICK] Terse response, no ceremony.\n'
    '\n'
    'Answer directly. No preamble, no follow-up suggestions, '
    'no "let me know if you need more."'
)
```
Dual output: systemMessage `'[QUICK] Terse response.'`, full in additionalContext.

**learn: (add learning)**
```python
_LEARN_EXPANSION = (
    '[LEARN] Append to agents/learnings.md.\n'
    '\n'
    'Format: H2 title (activity at decision point) → '
    'Anti-pattern → Correct pattern → Rationale.\n'
    'Check line count after appending.'
)
```
Dual output: systemMessage `'[LEARN] Append to learnings.'`, full in additionalContext.

Add to DIRECTIVES dict with aliases: `'q'`, `'quick'`, `'learn'`.

### 5. Tier 2: New b: directive

**Open question:** What does `b:` mean? Fourth member of b/d/p/q letter symmetry (mirror-letter set). Semantics TBD.

Placeholder — if `b:` = brainstorm, expansion would be:
```python
_BRAINSTORM_EXPANSION = (
    '[BRAINSTORM] Generate options, do not converge.\n'
    '\n'
    'Explore possibilities. List alternatives without evaluating. '
    'Diverge first, converge later. No recommendations yet.'
)
```

**Needs user input before implementing.**

### 6. Skill-editing guard pattern

New Tier 2.5: pattern-based context injection (not a directive, fires on content match).

**Pattern:** editing verbs + skill/agent reference
```python
EDIT_SKILL_PATTERN = re.compile(
    r'(fix|edit|update|improve|change|modify|rewrite|refactor)'
    r'.*\b(skill|agent)\b'
    r'|'
    r'\b(skill|agent)\b'
    r'.*(fix|edit|update|improve|change|modify|rewrite|refactor)',
    re.IGNORECASE
)
```

Also match editing verbs + `/<skill-name>` (user denotes skills with slash prefix):
```python
EDIT_SLASH_PATTERN = re.compile(
    r'(fix|edit|update|improve|change|modify|rewrite|refactor)'
    r'.*(/\w+)',
    re.IGNORECASE
)
```

**Injection:** additionalContext only (no systemMessage — invisible to user):
```
Load /plugin-dev:skill-development before editing skill files.
Load /plugin-dev:agent-development before editing agent files.
Skill descriptions require "This skill should be used when..." format.
```

Detection: after Tier 2 directives, before Tier 3 continuation. Fires alongside other tiers (additive, not exclusive).

### 7. CCG (claude-code-guide) integration

When user asks about Claude Code platform capabilities, inject reminder about claude-code-guide agent.

**Pattern:** questions about hooks, skills, settings, MCP, slash commands, IDE integration
```python
CCG_PATTERN = re.compile(
    r'\b(hook|hooks|PreToolUse|PostToolUse|SessionStart|UserPromptSubmit'
    r'|mcp.?server|slash.?command|settings\.json|\.claude/|plugin\.json'
    r'|keybinding|IDE.?integration|agent.?sdk)\b',
    re.IGNORECASE
)
```

**Injection:** additionalContext only:
```
Platform question detected. Use claude-code-guide agent (Task subagent_type="claude-code-guide") for authoritative Claude Code documentation.
```

Fires alongside other patterns (additive).

## Execution order in main()

```
1. Tier 1: Line-based shortcut matching (first match wins, returns)
2. Tier 2: Directive scan (first directive match wins, returns)
3. Tier 2.5: Pattern guards (skill-editing, ccg) — additive, collect all matches
4. Tier 3: Continuation parsing
5. Combine Tier 2.5 + Tier 3 results if both match, output
6. No match: silent pass-through
```

Note: Tier 2.5 doesn't return early — it collects context that combines with Tier 3 or outputs alone.

## Testing

- Existing shortcuts still work (exact match on own line)
- `s` within multi-line prompt triggers status
- `d: topic\nmultiline content` injects discussion framework
- `p: task name` shows concise systemMessage, full additionalContext
- `q: how does X work` injects quick-response mode
- `learn: pattern about Y` injects learning format
- `fix the commit skill` injects skill-dev reminder
- `update /design description` injects skill-dev reminder
- `how do hooks work` injects ccg reminder
- Continuation chaining still works
- Code fences still excluded from directive scanning
- No false positives on `d:` in prose (e.g., "the d: drive")
