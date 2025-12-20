"""Test CLI help text and inline documentation."""

import subprocess


def test_collect_help_describes_purpose() -> None:
    """Test that collect help describes its purpose.

    When: claudeutils collect --help is called
    Then: Help text contains "all sessions" AND "recursively"
    """
    result = subprocess.run(
        ["uv", "run", "claudeutils", "collect", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    help_text = result.stdout
    assert "all sessions" in help_text, "Help text should mention 'all sessions'"
    assert "recursively" in help_text, "Help text should mention 'recursively'"


def test_analyze_help_lists_categories() -> None:
    """Test that analyze help lists feedback categories.

    When: claudeutils analyze --help is called
    Then: Help text contains "instructions", "corrections", "process"
    """
    result = subprocess.run(
        ["uv", "run", "claudeutils", "analyze", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    help_text = result.stdout
    assert "instructions" in help_text, "Help text should mention 'instructions'"
    assert "corrections" in help_text, "Help text should mention 'corrections'"
    assert "process" in help_text, "Help text should mention 'process'"


def test_rules_help_describes_filtering() -> None:
    """Test that rules help describes filtering behavior.

    When: claudeutils rules --help is called
    Then: Help text contains "Deduplicates" AND "questions" AND "length"
    """
    result = subprocess.run(
        ["uv", "run", "claudeutils", "rules", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    help_text = result.stdout
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


def test_analyze_help_shows_stdin_usage() -> None:
    """Test that analyze help shows stdin usage.

    When: claudeutils analyze --help is called
    Then: Input argument help contains "stdin"
    """
    result = subprocess.run(
        ["uv", "run", "claudeutils", "analyze", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    help_text = result.stdout
    assert "stdin" in help_text, "Help text should mention 'stdin'"
