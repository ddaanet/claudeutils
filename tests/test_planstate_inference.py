"""Tests for planstate inference module."""

from pathlib import Path

from claudeutils.planstate import infer_state, list_plans


def test_empty_directory_not_a_plan(tmp_path: Path) -> None:
    """Empty directories should not be treated as plans."""
    plans_dir = tmp_path / "plans"
    plans_dir.mkdir()
    empty_plan = plans_dir / "empty"
    empty_plan.mkdir()

    result = infer_state(empty_plan)
    assert result is None

    plans = list_plans(plans_dir)
    assert plans == []
