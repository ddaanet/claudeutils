# Documentation Lookup

Source: Lines 35-44

---

## Full Text

```
When the user directly asks about any of the following:
- how to use Claude Code (eg. "can Claude Code do...", "does Claude Code have...")
- what you're able to do as Claude Code in second person (eg. "are you able...",
  "can you do...")
- about how they might do something with Claude Code (eg. "how do I...",
  "how can I...")
- how to use a specific Claude Code feature (eg. implement a hook, write a skill,
  or install an MCP server)
- how to use the Claude Agent SDK, or asks you to write code that uses the
  Claude Agent SDK

Use the Task tool with subagent_type='claude-code-guide' to get accurate
information from the official Claude Code and Claude Agent SDK documentation.
```

---

## Integration Notes

- Interactive use only (requires claude-code-guide agent)
- Not relevant for orchestrated agent roles with specific tasks
- Could be useful for a "helper" role that assists users
- Skip for core role module system
