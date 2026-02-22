"""Tests for orchestrator plan generation (RC-4 fix)."""

import importlib.util
from pathlib import Path

import pytest

from tests.pytest_helpers import setup_baseline_agents, setup_git_repo

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

assemble_phase_files = _mod.assemble_phase_files
extract_phase_models = _mod.extract_phase_models
parse_frontmatter = _mod.parse_frontmatter
extract_sections = _mod.extract_sections
extract_cycles = _mod.extract_cycles
validate_and_create = _mod.validate_and_create


class TestOrchestratorPlan:
    """PHASE_BOUNDARY entries include source phase file paths."""

    def test_orchestrator_plan_includes_phase_file_paths(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """PHASE_BOUNDARY entries contain source phase file paths."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        plan_dir = tmp_path / "plans" / "test-job"
        plan_dir.mkdir(parents=True)

        phase1 = plan_dir / "runbook-phase-1.md"
        phase1.write_text(
            "### Phase 1: Setup (type: general, model: sonnet)\n\n"
            "## Step 1.1: First step\n\nStep content."
        )

        phase2 = plan_dir / "runbook-phase-2.md"
        phase2.write_text(
            "### Phase 2: TDD (type: tdd, model: sonnet)\n\n"
            "## Cycle 2.1: First cycle\n\n"
            "**RED Phase:**\nWrite test.\n"
            "**GREEN Phase:**\nImplement it.\n"
            "**Stop/Error Conditions:** STOP if unexpected."
        )

        content, _ = assemble_phase_files(plan_dir)
        assert content is not None

        metadata, body = parse_frontmatter(content)
        metadata["type"] = "mixed"
        sections = extract_sections(body)
        cycles = extract_cycles(body)
        phase_models = extract_phase_models(body)

        orch_path = tmp_path / "plans" / "test-job" / "orchestrator-plan.md"
        steps_dir = tmp_path / "plans" / "test-job" / "steps"
        agent_path = tmp_path / ".claude" / "agents" / "test-job-task.md"

        result = validate_and_create(
            plan_dir / "runbook.md",
            sections,
            "test-job",
            agent_path,
            steps_dir,
            orch_path,
            metadata,
            cycles,
            phase_models,
            phase_dir=str(plan_dir),
        )

        assert result is True
        orch_content = orch_path.read_text()

        assert f"Phase file: {plan_dir}/runbook-phase-1.md" in orch_content, (
            f"Expected phase 1 file path in orchestrator. Got:\n{orch_content}"
        )
        assert f"Phase file: {plan_dir}/runbook-phase-2.md" in orch_content, (
            f"Expected phase 2 file path in orchestrator. Got:\n{orch_content}"
        )
