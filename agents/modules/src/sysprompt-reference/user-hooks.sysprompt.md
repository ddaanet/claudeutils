# User Hooks

Source: Line 111

---

## Full Text

```
Users may configure 'hooks', shell commands that execute in response to events
like tool calls, in settings. Treat feedback from hooks, including
<user-prompt-submit-hook>, as coming from the user. If you get blocked by a hook,
determine if you can adjust your actions in response to the blocked message. If
not, ask the user to check their hooks configuration.
```

---

## Key Behaviors

1. Hooks = shell commands on events
2. Treat hook feedback as user input
3. If blocked: try to adjust actions
4. If can't adjust: ask user to check hooks config

---

## Integration Notes

- May not apply to orchestrated roles (hooks may be disabled)
- Could add as context module for interactive use
- <user-prompt-submit-hook> is specific hook type
