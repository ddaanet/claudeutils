"""Context calculation for statusline display."""

import json
import subprocess
from pathlib import Path

from claudeutils.statusline.models import GitStatus, ThinkingState


def get_git_status() -> GitStatus:
    """Detect if in git repository and return branch name.

    Returns:
        GitStatus with branch name and dirty status.
        Returns branch=None if not in a git repository.
    """
    try:
        # Check if we're in a git repository
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            check=True,
            capture_output=True,
            text=True,
        )

        # Get the current branch name
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            check=True,
            capture_output=True,
            text=True,
        )

        branch = result.stdout.strip()

        # Check for dirty working tree
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )

        dirty = bool(status_result.stdout.strip())

        return GitStatus(branch=branch, dirty=dirty)

    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not in a git repository or git not found
        return GitStatus(branch=None, dirty=False)


def get_thinking_state() -> ThinkingState:
    """Read thinking state from ~/.claude/settings.json.

    Returns:
        ThinkingState with enabled flag from alwaysThinkingEnabled field.
        Returns enabled=False if settings file doesn't exist or can't be parsed.
    """
    try:
        settings_path = Path.home() / ".claude" / "settings.json"
        with settings_path.open() as f:
            settings = json.load(f)
        enabled = settings.get("alwaysThinkingEnabled", False)
        return ThinkingState(enabled=enabled)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # Settings file not found or can't be parsed
        return ThinkingState(enabled=False)
