"""Test account module structure and imports."""

import claudeutils.account


def test_account_module_importable() -> None:
    """Account module should be importable."""
    assert claudeutils.account is not None
