"""Tests for planstate aggregation module."""

from claudeutils.planstate.aggregation import TreeInfo, _parse_worktree_list


def test_parse_worktree_list_porcelain() -> None:
    """Parse git worktree list --porcelain output into TreeInfo objects."""
    porcelain = (
        "worktree /path/to/main\n"
        "branch refs/heads/main\n"
        "\n"
        "worktree /path/to/wt/slug\n"
        "branch refs/heads/slug\n"
        "\n"
    )

    result = _parse_worktree_list(porcelain)

    assert len(result) == 2
    assert result[0] == TreeInfo(path="/path/to/main", branch="main")
    assert result[1] == TreeInfo(path="/path/to/wt/slug", branch="slug")
