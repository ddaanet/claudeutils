"""Context calculation for statusline display."""

import subprocess

from claudeutils.statusline.models import GitStatus


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

        return GitStatus(branch=branch, dirty=False)

    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not in a git repository or git not found
        return GitStatus(branch=None, dirty=False)
