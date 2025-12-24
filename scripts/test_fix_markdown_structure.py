from fix_markdown_structure import (
    fix_dunder_references,
    fix_metadata_blocks,
    fix_nested_lists,
    fix_numbered_list_spacing,
    fix_warning_lines,
    process_lines,
)


def test_fix_dunder_references_existing() -> None:
    input_line = "## Minimal __init__.py\n"
    expected = "## Minimal `__init__.py`\n"
    assert fix_dunder_references(input_line) == expected


def test_fix_dunder_references_single() -> None:
    input_line = "# __name__\n"
    expected = "# `__name__`\n"
    assert fix_dunder_references(input_line) == expected


def test_fix_dunder_references_mixed() -> None:
    heading = "## About __init__.py\n"
    assert fix_dunder_references(heading) == "## About `__init__.py`\n"
    non_heading = "The __init__.py file\n"
    assert fix_dunder_references(non_heading) == non_heading


def test_fix_dunder_references_idempotent() -> None:
    input_line = "## Minimal `__init__.py`\n"
    assert fix_dunder_references(input_line) == input_line


def test_fix_metadata_blocks_existing() -> None:
    input_lines = [
        "**File:** `agents/role-planning.md`\n",
        "**Model:** Opus or Sonnet\n",
        "**Entry Point:** User requests feature design\n",
        "\n",
        "**Purpose:** Design test specifications\n",
    ]
    expected_lines = [
        "- **File:** `agents/role-planning.md`\n",
        "- **Model:** Opus or Sonnet\n",
        "- **Entry Point:** User requests feature design\n",
        "\n",
        "**Purpose:** Design test specifications\n",
    ]
    assert fix_metadata_blocks(input_lines) == expected_lines


def test_fix_metadata_blocks_single() -> None:
    input_lines = ["**Purpose:** Design test specifications\n", "\n"]
    assert fix_metadata_blocks(input_lines) == input_lines


def test_fix_metadata_blocks_first_prompt() -> None:
    """Test design document first prompt metadata block formatting."""
    input_lines = [
        "# Design Document\n",
        "\n",
        "**Status**: Design complete, awaiting implementation planning\n",
        "**Last Updated**: 2025-12-21\n",
        "**Design Authority**: Opus (claude-opus-4-5-20251101)\n",
        "\n",
        "---\n",
    ]
    expected_lines = [
        "# Design Document\n",
        "\n",
        "- **Status**: Design complete, awaiting implementation planning\n",
        "- **Last Updated**: 2025-12-21\n",
        "- **Design Authority**: Opus (claude-opus-4-5-20251101)\n",
        "\n",
        "---\n",
    ]
    assert fix_metadata_blocks(input_lines) == expected_lines


def test_fix_metadata_blocks_mixed() -> None:
    input_lines = [
        "Some text\n",
        "**File:** role.md\n",
        "**Model:** Sonnet\n",
        "\n",
        "More text\n",
    ]
    expected_lines = [
        "Some text\n",
        "- **File:** role.md\n",
        "- **Model:** Sonnet\n",
        "\n",
        "More text\n",
    ]
    assert fix_metadata_blocks(input_lines) == expected_lines


def test_fix_metadata_blocks_idempotent() -> None:
    input_lines = [
        "- **File:** role.md\n",
        "- **Model:** Sonnet\n",
        "\n",
    ]
    assert fix_metadata_blocks(input_lines) == input_lines


def test_fix_warning_lines_existing() -> None:
    input_lines = [
        "⚠️ STOP at every checkpoint\n",
        "⚠️ DO NOT proceed past checkpoint\n",
        "⚠️ Report completion status\n",
    ]
    expected_lines = [
        "- ⚠️ STOP at every checkpoint\n",
        "- ⚠️ DO NOT proceed past checkpoint\n",
        "- ⚠️ Report completion status\n",
    ]
    assert fix_warning_lines(input_lines) == expected_lines


def test_fix_warning_lines_single() -> None:
    input_lines = ["⚠️ STOP at every checkpoint\n", "\n"]
    assert fix_warning_lines(input_lines) == input_lines


def test_fix_warning_lines_mixed() -> None:
    input_lines = [
        "Some text\n",
        "⚠️ Warning one\n",
        "⚠️ Warning two\n",
        "\n",
        "More text\n",
    ]
    expected_lines = [
        "Some text\n",
        "- ⚠️ Warning one\n",
        "- ⚠️ Warning two\n",
        "\n",
        "More text\n",
    ]
    assert fix_warning_lines(input_lines) == expected_lines


def test_fix_warning_lines_idempotent() -> None:
    input_lines = [
        "- ⚠️ Warning one\n",
        "- ⚠️ Warning two\n",
    ]
    assert fix_warning_lines(input_lines) == input_lines


def test_fix_warning_lines_options() -> None:
    input_lines = [
        "Option A: Refactor ...\n",
        "Option B: Code ...\n",
        "Option C: New ...\n",
    ]
    expected_lines = [
        "- Option A: Refactor ...\n",
        "- Option B: Code ...\n",
        "- Option C: New ...\n",
    ]
    assert fix_warning_lines(input_lines) == expected_lines


def test_fix_nested_lists_existing() -> None:
    input_lines = ["2. Parent:\n", "   a. Child 1\n", "   b. Child 2\n"]
    expected_lines = ["2. Parent:\n", "   1. Child 1\n", "   2. Child 2\n"]
    assert fix_nested_lists(input_lines) == expected_lines


def test_fix_nested_lists_single() -> None:
    input_lines = ["   a. Child 1\n"]
    expected_lines = ["   1. Child 1\n"]
    assert fix_nested_lists(input_lines) == expected_lines


def test_fix_nested_lists_mixed() -> None:
    input_lines = [
        "1. Parent:\n",
        "   a. Child 1\n",
        "   Regular text\n",
        "   b. Child 2\n",
    ]
    expected_lines = [
        "1. Parent:\n",
        "   1. Child 1\n",
        "   Regular text\n",
        "   2. Child 2\n",
    ]
    assert fix_nested_lists(input_lines) == expected_lines


def test_fix_nested_lists_idempotent() -> None:
    input_lines = ["2. Parent:\n", "   1. Child 1\n", "   2. Child 2\n"]
    assert fix_nested_lists(input_lines) == input_lines


def test_fix_numbered_list_spacing_existing() -> None:
    input_lines = [
        "**Execution phase:**\n",
        "4. Batch reads\n",
    ]
    expected_lines = [
        "**Execution phase:**\n",
        "\n",
        "4. Batch reads\n",
    ]
    assert fix_numbered_list_spacing(input_lines) == expected_lines


def test_fix_numbered_list_spacing_idempotent() -> None:
    input_lines = [
        "**Execution phase:**\n",
        "\n",
        "4. Batch reads\n",
    ]
    assert fix_numbered_list_spacing(input_lines) == input_lines


def test_process_lines_integration() -> None:
    input_lines = [
        "## About __init__.py\n",
        "**File:** agents/role.md\n",
        "**Model:** Sonnet\n",
        "\n",
        "⚠️ Warning one\n",
        "⚠️ Warning two\n",
        "1. Parent:\n",
        "   a. Child 1\n",
        "   b. Child 2\n",
        "**Phase:**\n",
        "1. Execute\n",
    ]
    expected_lines = [
        "## About `__init__.py`\n",
        "- **File:** agents/role.md\n",
        "- **Model:** Sonnet\n",
        "\n",
        "- ⚠️ Warning one\n",
        "- ⚠️ Warning two\n",
        "1. Parent:\n",
        "   1. Child 1\n",
        "   2. Child 2\n",
        "**Phase:**\n",
        "\n",
        "1. Execute\n",
    ]
    assert process_lines(input_lines) == expected_lines


def test_process_lines_workflow_example() -> None:
    """Real world example: workflow with nested lists and stop instructions."""
    input_lines = [
        "**Workflow:**\n",
        "1. Read plan\n",
        "2. For each test:\n",
        "   a. Write\n",
        "   e. Refactor\n",
        "3. At checkpoint:\n",
        "   - Run `just role-code`\n",
        "   - STOP\n",
    ]
    expected_lines = [
        "**Workflow:**\n",
        "\n",
        "1. Read plan\n",
        "2. For each test:\n",
        "   1. Write\n",
        "   5. Refactor\n",
        "3. At checkpoint:\n",
        "   - Run `just role-code`\n",
        "   - STOP\n",
    ]
    assert process_lines(input_lines) == expected_lines


def test_process_lines_plan_conflict_example() -> None:
    """Real world example: plan conflict handling with numbered list."""
    input_lines = [
        "**Plan Conflict Handling (New):**\n",
        "If plan instructs you to run a conflicting command:\n",
        "1. Do not execute it\n",
    ]
    expected_lines = [
        "**Plan Conflict Handling (New):**\n",
        "If plan instructs you to run a conflicting command:\n",
        "\n",
        "1. Do not execute it\n",
    ]
    assert process_lines(input_lines) == expected_lines


def test_fix_numbered_list_spacing_agents_tier2_case() -> None:
    """Real AGENTS.md case - don't add blanks within numbered list with continuations."""
    input_lines = [
        "#### Tier 2 - Important\n",
        "\n",
        "4. **Load skills proactively:** Read skill files before operations (e.g., read\n",
        "   `agents/rules-commit.md` before `git commit`)\n",
        "5. **Stop at boundaries:** Complete assigned task then stop (no scope creep)\n",
        "6. **Be explicit:** Ask clarifying questions if requirements unclear\n",
    ]
    result = fix_numbered_list_spacing(input_lines)
    assert result == input_lines


def test_fix_numbered_list_spacing_design_keywords_case() -> None:
    """DESIGN_DECISIONS.md Keywords - don't add blank after label before set literal."""
    input_lines = [
        "**Keywords:**\n",
        '{"y", "n", "k", "g", "ok", "go", "yes", "no", "continue", "proceed", "sure", "okay", "resume"}\n',
    ]
    result = fix_numbered_list_spacing(input_lines)
    assert result == input_lines
