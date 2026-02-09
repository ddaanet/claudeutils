## Problem

The Bash tool sandbox note instructs the model:

> When you see evidence of sandbox-caused failure: IMMEDIATELY retry with `dangerouslyDisableSandbox: true` (don't ask, just do it) [...] This will prompt the user for permission

This is **ask-by-default** behavior disguised as deny-by-default. The flow is:

1. Command hits sandbox restriction
2. Model auto-retries with `dangerouslyDisableSandbox: true`
3. User sees a permission confirmation prompt
4. User reflexively clicks "allow" to unblock the agent

The result is permission prompt spam for what should be legitimate denials.

## Why this matters

Users who configure `permissions.allow` + `dangerouslyDisableSandbox: true` for commands that legitimately need sandbox bypass (writing to `.claude/`, symlink management, etc.) never hit this retry path. The auto-retry only fires on **unexpected** sandbox denials — which are exactly the cases that should be denied, not prompted.

## Proposed solution

**Deny-by-default:** Sandbox denial should stop the agent, not trigger auto-retry.

- Sandbox denial → agent stops (no retry, no permission prompt)
- Agent explains what failed and why
- User decides: adjust sandbox config, or explicitly ask agent to retry with bypass

**Optional recovery:** A Stop hook could detect sandbox denial patterns and offer structured recovery options, without the model auto-escalating.

## Speculation on current design intent

The auto-retry was likely added to prevent the agent from looping on sandbox-denied Bash calls (fail → retry → fail → retry). Stopping the agent on denial achieves the same goal without ask-by-default behavior.

## Related

- #10089 — Add setting to block `dangerouslyDisableSandbox` parameter entirely
- The sandbox enforcement is runtime — the prompt note is behavioral guidance only. Changing the guidance doesn't weaken actual sandboxing.
