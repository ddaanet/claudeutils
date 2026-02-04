"""Tests for switchback plist generation."""

import plistlib
from pathlib import Path

from claudeutils.account import create_switchback_plist


def test_create_switchback_plist(tmp_path: Path) -> None:
    """Test that create_switchback_plist() generates a valid plist file."""
    # Create switchback plist at temp location
    plist_path = tmp_path / "test.plist"
    switchback_time = 3600  # 1 hour from now

    create_switchback_plist(plist_path, switchback_time)

    # Verify plist file was created
    assert plist_path.exists()

    # Verify plist can be loaded and has correct structure
    with plist_path.open("rb") as f:
        plist_data = plistlib.load(f)

    # Verify required plist keys
    assert "Label" in plist_data
    assert "ProgramArguments" in plist_data
    assert "StartCalendarInterval" in plist_data

    # Verify calendar interval is a dict with expected time fields
    calendar_interval = plist_data["StartCalendarInterval"]
    assert isinstance(calendar_interval, dict)
    assert "Hour" in calendar_interval
    assert "Minute" in calendar_interval
    assert "Second" in calendar_interval


def test_create_switchback_plist_includes_month_day(tmp_path: Path) -> None:
    """Test that create_switchback_plist() includes Month and Day fields.

    Verifies StartCalendarInterval dict contains Month and Day keys.
    """
    # Create switchback plist at temp location
    plist_path = tmp_path / "test.plist"
    switchback_time = 3600  # 1 hour from now

    create_switchback_plist(plist_path, switchback_time)

    # Verify plist file was created
    assert plist_path.exists()

    # Load and verify plist structure
    with plist_path.open("rb") as f:
        plist_data = plistlib.load(f)

    # Verify Month and Day fields are present in StartCalendarInterval
    calendar_interval = plist_data["StartCalendarInterval"]
    assert "Month" in calendar_interval, "Month not in StartCalendarInterval"
    assert "Day" in calendar_interval, "Day not in StartCalendarInterval"
