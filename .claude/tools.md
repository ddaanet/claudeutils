# Claude System Tools

```json
{
    "permissions": {
        "deny": [
            "Task",
            "TaskOutput",
            "Bash",
            "Glob",
            "Grep",
            "ExitPlanMode",
            "Read",
            "Edit",
            "Write",
            "NotebookEdit",
            "WebFetch",
            "TodoWrite",
            "WebSearch",
            "KillShell",
            "AskUserQuestion",
            "Skill",
            "EnterPlanMode",
            "mcp__plugin_context7_context7__resolve-library-id",
            "mcp__plugin_context7_context7__get-library-docs",
        ]
    }
}
```

## File read/write only

```json
{
    "permissions": {
        "deny": [
            "Task",
            "TaskOutput",
            "Bash",
            "ExitPlanMode",
            "Read",
            "NotebookEdit",
            "WebFetch",
            "TodoWrite",
            "WebSearch",
            "KillShell",
            "AskUserQuestion",
            "Skill",
            "EnterPlanMode",
        ]
    }
}
```

## Code role

```json
{
    "permissions": {
        "deny": [
            "Task",
            "TaskOutput",
            "ExitPlanMode",
            "NotebookEdit",
            "KillShell",
            "Skill",
            "EnterPlanMode",
        ]
    }
}
```
