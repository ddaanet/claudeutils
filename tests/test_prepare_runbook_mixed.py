"""Tests for assemble_phase_files phase header injection (RC-3 fix)."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

assemble_phase_files = _mod.assemble_phase_files


class TestPhaseNumbering:
    """Phase header injection in assemble_phase_files."""

    def test_assembly_injects_phase_headers_when_absent(self, tmp_path: Path) -> None:
        """Headers injected from filenames when absent from phase files."""
        phase1 = tmp_path / "runbook-phase-1.md"
        phase1.write_text("## Step 1.1: Do thing\n\nStep content.")

        phase2 = tmp_path / "runbook-phase-2.md"
        phase2.write_text(
            "## Cycle 2.1: Test thing\n\n"
            "**RED Phase:**\nTest.\n"
            "**GREEN Phase:**\nImpl.\n"
            "**Stop/Error Conditions:** STOP if unexpected."
        )

        phase3 = tmp_path / "runbook-phase-3.md"
        phase3.write_text("## Step 3.1: Final thing\n\nFinal content.")

        content, _ = assemble_phase_files(tmp_path)

        assert content is not None
        assert "### Phase 1:" in content
        assert "### Phase 2:" in content
        assert "### Phase 3:" in content

        p1_pos = content.index("### Phase 1:")
        p2_pos = content.index("### Phase 2:")
        p3_pos = content.index("### Phase 3:")
        assert p1_pos < p2_pos < p3_pos
