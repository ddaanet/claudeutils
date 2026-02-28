"""Tests for _recall check subcommand."""

from pathlib import Path

from click.testing import CliRunner

from claudeutils.cli import cli


def test_check_valid_artifact() -> None:
    """Check exits 0 when artifact has valid Entry Keys section with entries."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create artifact with valid Entry Keys section
        artifact_content = """# Recall Artifact: Test Job

## Entry Keys

when test entry one — some annotation
when test entry two
"""
        artifact_dir = Path("plans/test-job")
        artifact_dir.mkdir(parents=True)
        artifact_path = artifact_dir / "recall-artifact.md"
        artifact_path.write_text(artifact_content)

        result = runner.invoke(cli, ["_recall", "check", "test-job"])
        assert result.exit_code == 0
