"""Switchback plist generation using LaunchAgent."""

import plistlib
from datetime import UTC, datetime, timedelta
from pathlib import Path


def create_switchback_plist(plist_path: Path, switchback_time: int) -> None:
    """Create a macOS LaunchAgent plist for switchback scheduling.

    Args:
        plist_path: Path where plist file will be written
        switchback_time: Switchback time in seconds from now
    """
    # Calculate target time
    target_time = datetime.now(UTC) + timedelta(seconds=switchback_time)

    # Create plist structure
    plist_data = {
        "Label": "com.anthropic.claude.switchback",
        "ProgramArguments": ["/usr/local/bin/claudeutils", "account", "switchback"],
        "StartCalendarInterval": {
            "Month": target_time.month,
            "Day": target_time.day,
            "Hour": target_time.hour,
            "Minute": target_time.minute,
            "Second": target_time.second,
        },
    }

    # Write plist file
    with plist_path.open("wb") as f:
        plistlib.dump(plist_data, f)
