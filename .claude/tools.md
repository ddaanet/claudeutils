# Claude System Tools

## Tool groups

### Orchestration

```json
            "Task",
            "TaskOutput",
```

### Read

```json
            "Glob",
            "Grep",
            "Read",
```

### Make changes

```json
            "Bash",
            "Edit",
            "Write",
            "NotebookEdit",
            "KillShell",
```

### Plan

```json
            "ExitPlanMode",
            "EnterPlanMode",
            "TodoWrite",
```

### Information

```json
            "WebFetch",
            "WebSearch",
            "AskUserQuestion",
            "Skill",
```

## No tool

```shell
claude --disallowed-tools "Task,TaskOutput,Glob,Grep,Read,Bash,Edit,Write,NotebookEdit,KillShell,ExitPlanMode,EnterPlanMode,TodoWrite,WebFetch,WebSearch,AskUserQuestion,Skill"
```

```json
{
    "permissions": {
        "deny": [
            "Task",
            "TaskOutput",
            "Glob",
            "Grep",
            "Read",
            "Bash",
            "Edit",
            "Write",
            "NotebookEdit",
            "KillShell",
            "ExitPlanMode",
            "EnterPlanMode",
            "TodoWrite",
            "WebFetch",
            "WebSearch",
            "AskUserQuestion",
            "Skill"
       ]
    }
}
```

## Design and planning

```shell
claude --disallowed-tools "NotebookEdit,ExitPlanMode,EnterPlanMode,WebFetch,WebSearch,mcp__plugin_context7_context7__resolve-library-id,mcp__plugin_context7_context7__get-library-docs,Skill"
```

```json
{
    "permissions": {
        "deny": [
            "NotebookEdit",
            "ExitPlanMode",
            "EnterPlanMode",
            "WebFetch",
            "WebSearch",
            "mcp__plugin_context7_context7__resolve-library-id",
            "mcp__plugin_context7_context7__get-library-docs",
            "Skill",
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
            "NotebookEdit",
            "WebFetch",
            "TodoWrite",
            "WebSearch",
            "KillShell",
            "AskUserQuestion",
            "Skill",
            "EnterPlanMode"
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
            "EnterPlanMode"
        ]
    }
}
```



## Conversational

```json
{
    "permissions": {
        "deny": [
            "EnterPlanMode"
            "ExitPlanMode",
            "NotebookEdit",
            "Skill",
        ]
    }
}
```
