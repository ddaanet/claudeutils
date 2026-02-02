# Claude Code Configuration

Personal scripts and configuration for Claude Code CLI.

## Components

- **claude-account.sh** - Account switcher between Pro (OAuth) and API modes
- **statusline-command.sh** - Custom statusline showing account mode, limits, and context usage

## Installation

```bash
just install
```

This creates a symlink at `~/bin/claude-account` pointing to the script.

## Usage

```bash
claude-account status    # Show current mode and limits
claude-account api       # Switch to API mode (only if at limit)
claude-account api!      # Force switch to API mode
claude-account plan      # Switch back to Pro/Plan mode
```

## Directory Structure

```
.
├── CLAUDE.md              # Agent instructions for this tool
├── README.md              # This file
├── design-decisions.md    # Implementation details and rationale
├── justfile               # Build/install recipes
├── claude-account.sh      # Account switcher script
└── statusline-command.sh  # Statusline script
```

## Configuration

Scripts expect these files in `~/.claude/`:
- `api-key` - Anthropic API key (chmod 600)
- `openrouter-key` - OpenRouter API key (chmod 600, optional)
- `account-mode` - Current mode ("plan" or "api")
- `account-config.json` - Provider selection ("anthropic" or "openrouter")
- `settings.local.json` - Local settings overrides (gitignored)

## Documentation

- **design-decisions.md** - Complete implementation details, authentication mechanism, OpenRouter integration, statusline design
- **CLAUDE.md** - Concise agent instructions (references design-decisions.md for full context)
- **../agents/openrouter-reference.md** - OpenRouter configuration and troubleshooting reference
