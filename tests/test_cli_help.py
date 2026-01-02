"""Test CLI help text and inline documentation."""

import subprocess
import sys

import pytest

from claudeutils import cli


def test_collect_help_describes_purpose(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that collect help describes its purpose.

    When: claudeutils collect --help is called
    Then: Help text contains "all sessions" AND "recursively"
    """
    monkeypatch.setattr(sys, "argv", ["claudeutils", "collect", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        cli.main()
    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    help_text = captured.out
    assert "all sessions" in help_text, "Help text should mention 'all sessions'"
    assert "recursively" in help_text, "Help text should mention 'recursively'"


def test_analyze_help_lists_categories(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that analyze help lists feedback categories.

    When: claudeutils analyze --help is called
    Then: Help text contains "instructions", "corrections", "process"
    """
    monkeypatch.setattr(sys, "argv", ["claudeutils", "analyze", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        cli.main()
    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    help_text = captured.out
    assert "instructions" in help_text, "Help text should mention 'instructions'"
    assert "corrections" in help_text, "Help text should mention 'corrections'"
    assert "process" in help_text, "Help text should mention 'process'"


def test_rules_help_describes_filtering(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that rules help describes filtering behavior.

    When: claudeutils rules --help is called
    Then: Help text contains "Deduplicates" AND "questions" AND "length"
    """
    monkeypatch.setattr(sys, "argv", ["claudeutils", "rules", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        cli.main()
    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    help_text = captured.out
    assert "Deduplicates" in help_text, "Help text should mention 'Deduplicates'"
    assert "questions" in help_text, "Help text should mention 'questions'"
    assert "length" in help_text, "Help text should mention 'length'"


def test_main_help_shows_pipeline() -> None:
    """Test that main help shows the pipeline.

    When: claudeutils --help is called
    Then: Help text contains "collect" AND "analyze" AND "rules" AND "Pipeline"
    """
    result = subprocess.run(
        ["uv", "run", "claudeutils", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    help_text = result.stdout
    assert "collect" in help_text, "Help text should mention 'collect'"
    assert "analyze" in help_text, "Help text should mention 'analyze'"
    assert "rules" in help_text, "Help text should mention 'rules'"
    assert "Pipeline" in help_text, "Help text should mention 'Pipeline'"


def test_analyze_help_shows_stdin_usage(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that analyze help shows stdin usage.

    When: claudeutils analyze --help is called
    Then: Input argument help contains "stdin"
    """
    monkeypatch.setattr(sys, "argv", ["claudeutils", "analyze", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        cli.main()
    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    help_text = captured.out
    assert "stdin" in help_text, "Help text should mention 'stdin'"


def test_tokens_help_is_complete_and_accurate(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that tokens help text is complete and accurate.

    When: claudeutils tokens --help is called
    Then: Help contains model aliases, file arguments, json option, and examples
    """
    monkeypatch.setattr(sys, "argv", ["claudeutils", "tokens", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        cli.main()
    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    help_text = captured.out
    assert "Count tokens" in help_text, "Help text should mention 'Count tokens'"
    assert "haiku" in help_text, "Help text should list 'haiku' model"
    assert "sonnet" in help_text, "Help text should list 'sonnet' model"
    assert "opus" in help_text, "Help text should list 'opus' model"
    assert "FILE" in help_text, "Help text should mention 'FILE' argument"
    assert "--json" in help_text, "Help text should mention '--json' option"
    assert "ANTHROPIC_API_KEY" in help_text, (
        "Help text should mention API key requirement"
    )
    assert "Requires" in help_text, "Help text should mention requirement"
    assert "Examples:" in help_text, "Help text should include 'Examples:' section"
