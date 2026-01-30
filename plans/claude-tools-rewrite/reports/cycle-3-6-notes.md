# Cycle 3.6: LaunchAgent plist generation

## Status: GREEN_VERIFIED

## Execution Details

**Test Command:**
```bash
pytest tests/test_account_switchback.py::test_create_switchback_plist -xvs
```

**RED Phase Result:**
FAIL as expected - ImportError: cannot import name 'create_switchback_plist' from 'claudeutils.account'

**GREEN Phase Result:**
PASS - Function implemented with full plist structure support

**Regression Check:**
306/306 passed - No regressions

**Refactoring:**
- Fixed lint error DTZ005: Added UTC timezone to datetime.now() call
- Fixed lint error PTH123: Changed open() to Path.open() in both implementation and test
- Lint reformatted file (import order)
- Precommit passed with no quality warnings

## Files Modified

- src/claudeutils/account/switchback.py (created)
- src/claudeutils/account/__init__.py (added create_switchback_plist export)
- tests/test_account_switchback.py (created with test_create_switchback_plist test)

## Implementation Details

**create_switchback_plist(plist_path, switchback_time):**
- Calculates target time by adding switchback_time (seconds) to current UTC time
- Creates plist structure with Label, ProgramArguments, and StartCalendarInterval
- Uses plistlib.dump() to write binary plist file
- StartCalendarInterval contains Hour, Minute, Second fields extracted from target time

**Test Coverage:**
- Verifies plist file is created at specified path
- Validates plist can be loaded as binary plist
- Checks for required keys (Label, ProgramArguments, StartCalendarInterval)
- Verifies StartCalendarInterval is a dict with Hour, Minute, Second fields

## Design Decisions

1. **UTC timezone** - Using datetime.now(UTC) for timezone-aware calculation (lint requirement)
2. **Path.open()** - Using pathlib Path.open() for consistency with project lint rules
3. **Minimal plist structure** - Only essential fields for LaunchAgent scheduling
4. **Direct time extraction** - Use target_time hour/minute/second directly from calculated datetime

## Stop Condition

None - Cycle completed successfully without encountering any stop conditions.
