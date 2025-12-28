# Claude CLI wrapper

To best optimize context, roles can have associated allowed and disallowed tools list
(--allowed-tools, --disallowed-tools) mcp config, and system prompt.

Tools that are entirely disallowed do not contribute to the context.

Examples:

- code agents follow a precise plan, they do not need TodoWrite and its long associated
  prompts.
- code, refactor, lint, etc. do not need web access.
- role-specific bash constraints can be enforced by the permission system
