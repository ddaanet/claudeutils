"""Tests for claudeutils data models."""

import pytest
from pydantic import ValidationError

from claudeutils.models import SessionInfo


def test_session_info_creation() -> None:
    """Create SessionInfo with required fields and correct types."""
    info = SessionInfo(
        session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
        title="Design a python script",
        timestamp="2025-12-16T08:39:26.932Z",
    )
    assert info.session_id == "e12d203f-ca65-44f0-9976-cb10b74514c1"
    assert info.title == "Design a python script"
    assert info.timestamp == "2025-12-16T08:39:26.932Z"


def test_session_info_validation() -> None:
    """Validate types with Pydantic."""
    with pytest.raises(ValidationError):
        # Intentionally pass wrong types to test Pydantic validation
        SessionInfo(session_id=123, title="foo", timestamp="bar")  # type: ignore[arg-type]
