# Claude Code System Prompt Catalog

Reference extraction from Claude Code system prompt (v2.0.75). These modules preserve
all instruction categories for potential inclusion in role prompts.

---

## Section Index

| Section                    | Conditional On           | Module File                             | Integration Status         |
| -------------------------- | ------------------------ | --------------------------------------- | -------------------------- |
| Identity/CLI context       | -                        | `identity.sysprompt.md`                 | NEW                        |
| Security policy            | -                        | (external variable)                     | Defer                      |
| URL restrictions           | -                        | `security.sysprompt.md`                 | NEW                        |
| Help/feedback              | -                        | `help-feedback.sysprompt.md`            | Interactive only           |
| Documentation lookup       | Task tool                | `documentation-lookup.sysprompt.md`     | Interactive only           |
| Tone and style             | OUTPUT_STYLE_CONFIG=null | `tone-style.sysprompt.md`               | Partially in communication |
| Professional objectivity   | OUTPUT_STYLE_CONFIG=null | `professional-objectivity.sysprompt.md` | Add to communication       |
| Planning without timelines | OUTPUT_STYLE_CONFIG=null | `planning-no-timelines.sysprompt.md`    | Add to planning roles      |
| Task management            | TodoWrite tool           | `todowrite.sysprompt.md`                | → todowrite.tool.md        |
| Asking questions           | AskUserQuestion tool     | `askuser.sysprompt.md`                  | → askuser.tool.md          |
| User hooks                 | -                        | `user-hooks.sysprompt.md`               | Context module             |
| Doing tasks                | OUTPUT_STYLE_CONFIG      | `doing-tasks.sysprompt.md`              | Multiple modules           |
| System reminders           | -                        | `system-reminders.sysprompt.md`         | Context module             |
| Tool usage policy          | Various tools            | `tool-policy.sysprompt.md`              | → tool modules             |

---

## Conditional Variables

The system prompt uses JavaScript template conditionals:

```javascript
${OUTPUT_STYLE_CONFIG !== null ? "custom style" : "default instructions"}
${AVAILABLE_TOOLS_SET.has(TOOL_NAME) ? "tool instructions" : ""}
```

**OUTPUT_STYLE_CONFIG**: When null, default instructions apply (tone, style, doing
tasks). When set, custom output style replaces these sections.

**AVAILABLE_TOOLS_SET**: Determines which tool-specific sections to include.

---

## Scope Analysis: Main Prompt vs Task Agent

Task agent prompt is a **minimal replacement** for the main system prompt. Rules NOT in
Task agent are effectively "interactive-only" in default Claude Code.

| Pattern                  | Main Prompt | Task Agent | Scope Decision                             |
| ------------------------ | ----------- | ---------- | ------------------------------------------ |
| Hooks                    | ✓           | ✗          | Interactive-only                           |
| System-reminder handling | ✓           | ✗          | Core (reminders ARE injected everywhere)   |
| Professional objectivity | ✓           | ✗          | Conversational roles only                  |
| Over-engineering         | ✓           | ✗          | Code roles (useful despite absence)        |
| OWASP security           | ✓           | ✗          | Code roles (useful despite absence)        |
| Read before modify       | ✓           | ✗          | All task roles (omission may be oversight) |
| Emoji: avoid             | ✓           | ✓          | **Core**                                   |
| File creation            | ✓           | ✓          | **Core**                                   |
| Documentation files      | implicit    | ✓          | Task agent MORE specific                   |
| Absolute paths           | ✗           | ✓          | Task agent only                            |

---

## Integration Notes

### Core (Both Prompts)

- Emoji: avoid
- File creation restrictions
- System reminders handling (reminders injected everywhere)

### Tool-Conditional

- TodoWrite → extensive instructions with examples
- AskUserQuestion → question framing, no time estimates
- Task/Explore agents → delegation patterns
- Read/Edit/Write → file operation mechanics
- Bash → specialized tools preference, communication restrictions
- WebFetch → redirect handling

### Conversational Roles Only

- Professional objectivity (planning, refactor, remember)

### Code Roles

- Over-engineering avoidance
- OWASP security
- Read before modify

### Interactive Only

- Hooks handling (orchestrated may not have hooks)
- Help/feedback
- Documentation lookup
