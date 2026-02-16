"""Aggregation module for planstate.

Parsing and combining planning artifacts.
"""

from typing import NamedTuple


class TreeInfo(NamedTuple):
    """Information about a git worktree."""

    path: str
    branch: str


def _parse_worktree_list(output: str) -> list[TreeInfo]:
    """Parse git worktree list --porcelain output into TreeInfo objects.

    Args:
        output: git worktree list --porcelain format output

    Returns:
        List of TreeInfo objects with path and branch fields.
        Branch ref is stripped of "refs/heads/" prefix.
    """
    result = []
    lines = output.split("\n")

    current_path = None
    current_branch = None

    for line in lines:
        if line.startswith("worktree "):
            current_path = line[len("worktree ") :]
        elif line.startswith("branch "):
            ref = line[len("branch ") :]
            # Strip "refs/heads/" prefix
            if ref.startswith("refs/heads/"):
                current_branch = ref[len("refs/heads/") :]
            else:
                current_branch = ref
        elif line == "" and current_path is not None and current_branch is not None:
            result.append(TreeInfo(path=current_path, branch=current_branch))
            current_path = None
            current_branch = None

    return result
