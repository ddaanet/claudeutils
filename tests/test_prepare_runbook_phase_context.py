"""Tests for extract_phase_preambles (RC-3 phase context extraction)."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

extract_phase_preambles = _mod.extract_phase_preambles


class TestPhaseContext:
    """extract_phase_preambles extracts per-phase preamble text."""

    def test_extract_phase_preambles(self) -> None:
        """All phases returned; empty string when no preamble."""
        content = (
            "### Phase 1: Core behavior (type: tdd, model: sonnet)\n\n"
            "RC-1 fix. Prerequisites: foo module exists.\n\n"
            "**Constraints:** No backward-incompatible changes.\n\n"
            "## Cycle 1.1: Test thing\n\n"
            "### Phase 2: Infrastructure (type: general)\n\n"
            "Setup database connections. Verify connectivity.\n\n"
            "## Step 2.1: Configure DB\n\n"
            "### Phase 3: Cleanup (type: tdd, model: sonnet)\n\n"
            "## Cycle 3.1: Clean state\n"
        )

        result = extract_phase_preambles(content)

        assert set(result.keys()) == {1, 2, 3}
        assert "RC-1 fix" in result[1]
        assert "Constraints" in result[1]
        assert "Setup database connections" in result[2]
        assert result[3] == ""
        assert "### Phase 1:" not in result[1]
        assert "## Cycle 1.1:" not in result[1]
