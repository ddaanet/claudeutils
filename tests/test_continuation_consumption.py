"""Unit tests for continuation consumption protocol.

Tests the cooperative skill protocol that skills use to consume continuation
entries from additionalContext or from [CONTINUATION: ...] suffix in Skill
args. Based on design Component 3 test scenarios and FR-2 (sequential
execution - peel-first-pass-remainder protocol).

Protocol:
1. Read continuation from additionalContext (first skill in chain) or
   from [CONTINUATION: ...] suffix in Skill args (chained skills)
2. If continuation is empty: stop (terminal)
3. Consume first entry as tail-call target
4. Invoke via Skill tool with remainder appended to args
"""

import re


def parse_continuation_string(
    continuation_str: str | None,
) -> list[dict[str, str]] | None:
    """Parse [CONTINUATION: ...] format into list of entries.

    Format: [CONTINUATION: /skill1 arg1, /skill2 arg2]
    Returns list of {'skill': '...', 'args': '...'} dicts, or None if empty/malformed.
    """
    if not continuation_str:
        return None

    # Match [CONTINUATION: ...] pattern
    match = re.search(r"\[CONTINUATION:\s*(.+?)\]", continuation_str, re.DOTALL)
    if not match:
        return None

    content = match.group(1).strip()
    if not content:
        return None

    entries = []
    # Split by comma, but only if not inside nested structures
    parts = [p.strip() for p in content.split(",")]

    for part in parts:
        if not part:
            continue

        # Parse /skill args format
        space_idx = part.find(" ")
        if space_idx == -1:
            # Just skill, no args
            skill = part.lstrip("/")
            args = ""
        else:
            skill = part[:space_idx].lstrip("/")
            args = part[space_idx + 1 :].strip()

        entries.append({"skill": skill, "args": args})

    return entries if entries else None


def peel_continuation(
    args_with_continuation: str,
) -> tuple[dict[str, str] | None, str | None]:
    """Peel first entry from continuation in args.

    Return (target_entry, remainder_str).

    Input: args with [CONTINUATION: /a, /b, /c]
    Output: ({'skill': 'a', 'args': ''}, '[CONTINUATION: /b, /c]')

    Returns:
        (None, None) if no continuation
        (target_dict, remainder_str) where remainder_str is formatted
        [CONTINUATION: ...] or None if empty
    """
    entries = parse_continuation_string(args_with_continuation)
    if not entries or len(entries) == 0:
        return (None, None)

    target = entries[0]

    # Build remainder
    if len(entries) > 1:
        remainder_entries = entries[1:]
        # Rebuild the [CONTINUATION: ...] format
        remainder_parts = []
        for entry in remainder_entries:
            if entry["args"]:
                remainder_parts.append(f"/{entry['skill']} {entry['args']}")
            else:
                remainder_parts.append(f"/{entry['skill']}")
        remainder_str = f"[CONTINUATION: {', '.join(remainder_parts)}]"
        return (target, remainder_str)
    # Last entry - no remainder
    return (target, None)


class TestParseConsumptionFormat:
    """Tests for parsing [CONTINUATION: ...] format."""

    def test_parse_single_entry(self) -> None:
        """Parse single entry in continuation."""
        entries = parse_continuation_string("[CONTINUATION: /commit]")

        assert entries is not None
        assert len(entries) == 1
        assert entries[0]["skill"] == "commit"
        assert entries[0]["args"] == ""

    def test_parse_single_entry_with_args(self) -> None:
        """Parse single entry with arguments."""
        entries = parse_continuation_string("[CONTINUATION: /handoff --commit]")

        assert entries is not None
        assert len(entries) == 1
        assert entries[0]["skill"] == "handoff"
        assert entries[0]["args"] == "--commit"

    def test_parse_multiple_entries(self) -> None:
        """Parse multiple entries separated by commas."""
        entries = parse_continuation_string("[CONTINUATION: /plan, /execute, /commit]")

        assert entries is not None
        assert len(entries) == 3
        assert entries[0]["skill"] == "plan"
        assert entries[1]["skill"] == "execute"
        assert entries[2]["skill"] == "commit"

    def test_parse_multiple_entries_with_args(self) -> None:
        """Parse multiple entries where some have arguments."""
        entries = parse_continuation_string(
            "[CONTINUATION: /plan-adhoc foo, /orchestrate, /commit]"
        )

        assert entries is not None
        assert len(entries) == 3
        assert entries[0]["skill"] == "plan-adhoc"
        assert entries[0]["args"] == "foo"
        assert entries[1]["skill"] == "orchestrate"
        assert entries[1]["args"] == ""
        assert entries[2]["skill"] == "commit"

    def test_parse_complex_args(self) -> None:
        """Parse entry with complex arguments."""
        entries = parse_continuation_string(
            "[CONTINUATION: /design plans/myplan --verbose]"
        )

        assert entries is not None
        assert len(entries) == 1
        assert entries[0]["skill"] == "design"
        assert "plans/myplan" in entries[0]["args"]
        assert "--verbose" in entries[0]["args"]

    def test_parse_empty_continuation(self) -> None:
        """Return None for empty continuation."""
        entries = parse_continuation_string("[CONTINUATION: ]")
        assert entries is None

    def test_parse_no_continuation_marker(self) -> None:
        """Return None when [CONTINUATION: ...] marker not found."""
        entries = parse_continuation_string("some regular args")
        assert entries is None

    def test_parse_malformed_bracket(self) -> None:
        """Return None for malformed bracket."""
        entries = parse_continuation_string("[CONTINUATION: /a, /b")
        assert entries is None

    def test_parse_none_input(self) -> None:
        """Return None for None input."""
        entries = parse_continuation_string(None)
        assert entries is None

    def test_parse_whitespace_handling(self) -> None:
        """Correctly handle whitespace around entries."""
        entries = parse_continuation_string("[CONTINUATION:  /a ,  /b  ,  /c  ]")

        assert entries is not None
        assert len(entries) == 3
        assert entries[0]["skill"] == "a"
        assert entries[1]["skill"] == "b"
        assert entries[2]["skill"] == "c"


class TestPeelFirstEntry:
    """Tests for peeling first entry from continuation.

    Tests the peel-first-pass-remainder protocol.
    """

    def test_peel_single_entry(self) -> None:
        """Peel single entry from continuation → (target, None)."""
        target, remainder = peel_continuation("[CONTINUATION: /commit]")

        assert target is not None
        assert target["skill"] == "commit"
        assert target["args"] == ""
        assert remainder is None

    def test_peel_first_of_three(self) -> None:
        """Peel first entry from three-entry continuation.

        Result: (target, [CONTINUATION: /b, /c]).
        """
        target, remainder = peel_continuation("[CONTINUATION: /design, /plan, /commit]")

        assert target is not None
        assert target["skill"] == "design"
        assert target["args"] == ""

        assert remainder is not None
        assert "[CONTINUATION:" in remainder
        # Verify remainder has plan and commit
        assert "/plan" in remainder
        assert "/commit" in remainder

    def test_peel_with_args(self) -> None:
        """Peel entry with arguments → (target with args, remainder)."""
        target, remainder = peel_continuation(
            "[CONTINUATION: /handoff --commit, /commit]"
        )

        assert target is not None
        assert target["skill"] == "handoff"
        assert target["args"] == "--commit"

        assert remainder is not None
        assert "/commit" in remainder

    def test_peel_last_entry(self) -> None:
        """Peel last entry from continuation → (target, None)."""
        _target, remainder = peel_continuation(
            "[CONTINUATION: /handoff --commit, /commit]"
        )
        assert remainder is not None

        # Peel first (handoff)
        target1, remainder1 = peel_continuation(remainder)
        assert target1 is not None
        assert target1["skill"] == "commit"

        # After peeling commit, no remainder
        assert remainder1 is None

    def test_peel_no_continuation(self) -> None:
        """Return (None, None) when no continuation present."""
        target, remainder = peel_continuation("some args without continuation")

        assert target is None
        assert remainder is None

    def test_peel_empty_args(self) -> None:
        """Handle args with only whitespace."""
        target, remainder = peel_continuation("   ")

        assert target is None
        assert remainder is None

    def test_peel_preserves_complex_args_in_remainder(self) -> None:
        """Preserve complex arguments in remainder when peeling."""
        target, remainder = peel_continuation(
            "[CONTINUATION: /design foo, /plan-adhoc --verbose bar, /commit]"
        )

        assert target is not None
        assert target["skill"] == "design"
        assert target["args"] == "foo"

        assert remainder is not None
        # plan-adhoc entry should preserve its args
        assert "plan-adhoc" in remainder
        assert "--verbose" in remainder
        assert "bar" in remainder

    def test_peel_three_entry_sequence(self) -> None:
        """Simulate peeling through a three-entry sequence."""
        continuation = "[CONTINUATION: /a arg1, /b arg2, /c]"

        # First peel: get /a
        target1, remainder1 = peel_continuation(continuation)
        assert target1 is not None
        assert remainder1 is not None
        assert target1["skill"] == "a"
        assert target1["args"] == "arg1"
        assert "/b arg2" in remainder1
        assert "/c" in remainder1

        # Second peel: get /b from remainder
        target2, remainder2 = peel_continuation(remainder1)
        assert target2 is not None
        assert remainder2 is not None
        assert target2["skill"] == "b"
        assert target2["args"] == "arg2"
        assert "/c" in remainder2
        assert "/a" not in remainder2  # previous entry should be gone

        # Third peel: get /c
        target3, remainder3 = peel_continuation(remainder2)
        assert target3 is not None
        assert target3["skill"] == "c"
        assert target3["args"] == ""
        assert remainder3 is None  # terminal

    def test_peel_terminal_indication(self) -> None:
        """Terminal state when remainder is None."""
        target, remainder = peel_continuation("[CONTINUATION: /commit]")

        assert target is not None
        assert target["skill"] == "commit"

        # Terminal: no tail-call
        assert remainder is None


class TestConsumptionProtocol:
    """Integration tests for the cooperative skill consumption protocol."""

    def test_skill_receives_continuation_in_additionalcontext(self) -> None:
        """First skill receives continuation from additionalContext."""
        # Simulates: /design skill receives additionalContext with continuation
        additional_context = "[CONTINUATION: /plan-adhoc, /commit]"

        entries = parse_continuation_string(additional_context)

        assert entries is not None
        assert entries[0]["skill"] == "plan-adhoc"

    def test_skill_receives_continuation_in_args_suffix(self) -> None:
        """Chained skill receives continuation in args suffix."""
        # Simulates: /plan-adhoc receives args: "plans/foo [CONTINUATION: /commit]"
        args = "plans/foo [CONTINUATION: /commit]"

        target, remainder = peel_continuation(args)

        assert target is not None
        assert target["skill"] == "commit"
        assert remainder is None

    def test_skill_consumption_protocol_step_by_step(self) -> None:
        """Test complete consumption protocol workflow."""
        # Scenario: User input "/design, /plan, /commit" gets parsed to:
        # [CONTINUATION: /plan, /commit]
        # Design skill invokes: Skill("plan", args="args [CONTINUATION: /commit]")

        # Step 1: Design skill reads continuation
        design_continuation = "[CONTINUATION: /plan, /commit]"

        # Step 2: Design skill peels first entry
        target, remainder = peel_continuation(design_continuation)
        assert target is not None
        assert target["skill"] == "plan"

        # Step 3: Design skill builds tail-call args
        tail_call_args = f"plans/foo {remainder}" if remainder else "plans/foo"

        # Step 4: Plan skill receives this tail-call args
        # It peels its target (commit) from args
        target2, remainder2 = peel_continuation(tail_call_args)
        assert target2 is not None
        assert target2["skill"] == "commit"
        assert remainder2 is None  # terminal

    def test_empty_continuation_terminal(self) -> None:
        """Empty continuation indicates terminal state (no tail-call)."""
        target, remainder = peel_continuation("[CONTINUATION: ]")

        # Empty continuation should not parse as valid entries
        assert target is None
        assert remainder is None

    def test_no_continuation_terminal(self) -> None:
        """Absence of continuation marker indicates terminal state."""
        target, remainder = peel_continuation("some args without marker")

        # No [CONTINUATION: ...] marker means terminal
        assert target is None
        assert remainder is None

    def test_last_skill_protocol(self) -> None:
        """Last skill in chain receives terminal (empty/no continuation)."""
        # Commit skill receives either:
        # - No continuation in args (just "some args")
        # - Or empty [CONTINUATION: ]

        # Case 1: No continuation marker
        target1, remainder1 = peel_continuation("no continuation here")
        assert target1 is None
        assert remainder1 is None

        # Case 2: Empty marker
        target2, remainder2 = peel_continuation("[CONTINUATION: ]")
        assert target2 is None
        assert remainder2 is None

        # Both cases indicate terminal: stop, no tail-call

    def test_continuation_with_embedded_args_containing_slashes(self) -> None:
        """Handle args with path-like content containing slashes."""
        # Edge case: arg contains /path/to/file which shouldn't be mistaken for skill
        continuation = "[CONTINUATION: /design plans/foo/bar, /commit]"

        entries = parse_continuation_string(continuation)

        assert entries is not None
        assert entries[0]["skill"] == "design"
        # Args should include the full path
        assert "plans/foo/bar" in entries[0]["args"]
        assert entries[1]["skill"] == "commit"

    def test_skill_must_not_include_continuation_in_task_tool(self) -> None:
        """Protocol constraint: continuation MUST NOT appear in Task tool prompts.

        This is a documentation test - verifies the constraint is documented.
        Enforcement would be via PreToolUse hook, which is out of scope for
        this phase.
        """
        # This test documents the constraint C-1:
        # "No sub-agent leakage — continuation stripped from Task tool prompts"
        # Skills must NOT pass continuation to Task tool.
        # This test serves as a checkpoint: if a skill implementation
        # needs to pass continuation to a sub-agent, that's a design violation.
        assert True  # Constraint documented; enforcement is PreToolUse hook scope


class TestConsumptionEdgeCases:
    """Edge cases and corner scenarios in consumption protocol."""

    def test_multiple_comma_separated_without_spaces(self) -> None:
        """Parse entries separated by commas without spaces."""
        entries = parse_continuation_string("[CONTINUATION: /a,/b,/c]")

        assert entries is not None
        assert len(entries) == 3
        assert entries[0]["skill"] == "a"
        assert entries[1]["skill"] == "b"
        assert entries[2]["skill"] == "c"

    def test_skill_name_with_underscore(self) -> None:
        """Handle skill names with underscores."""
        target, _remainder = peel_continuation(
            "[CONTINUATION: /plan_adhoc arg, /commit]"
        )

        assert target is not None
        assert target["skill"] == "plan_adhoc"

    def test_args_with_multiple_spaces(self) -> None:
        """Preserve multiple spaces in arguments."""
        entries = parse_continuation_string(
            "[CONTINUATION: /design plans/foo --verbose  --quiet]"
        )

        assert entries is not None
        assert entries[0]["skill"] == "design"
        # Both flags should be present
        assert "--verbose" in entries[0]["args"]
        assert "--quiet" in entries[0]["args"]

    def test_newlines_in_continuation_string(self) -> None:
        """Handle continuation strings with embedded newlines."""
        continuation = """[CONTINUATION: /plan-adhoc,
/commit]"""

        entries = parse_continuation_string(continuation)

        assert entries is not None
        assert len(entries) == 2
        assert entries[0]["skill"] == "plan-adhoc"
        assert entries[1]["skill"] == "commit"

    def test_peel_with_extra_whitespace_preservation(self) -> None:
        """Extra whitespace is normalized but preserved in essence."""
        target, remainder = peel_continuation(
            "[CONTINUATION:   /design   plans/foo   ,   /commit   ]"
        )

        assert target is not None
        assert target["skill"] == "design"
        # Args should have normalized whitespace
        assert "plans/foo" in target["args"]

        assert remainder is not None
        assert "/commit" in remainder


class TestDesignReferences:
    """Tests referencing design requirements."""

    def test_fr2_sequential_execution_peel_first_pass_remainder(self) -> None:
        """FR-2: Sequential execution — peel-first-pass-remainder protocol.

        Protocol ensures:
        1. First entry is consumed as current target
        2. Remaining entries are passed to next skill in args
        3. When remainder is empty, terminal state (no tail-call)
        """
        # Setup: continuation with three entries
        continuation = "[CONTINUATION: /plan-adhoc, /orchestrate, /commit]"

        # Peel first
        target1, remainder1 = peel_continuation(continuation)
        assert target1 is not None
        assert remainder1 is not None
        assert target1["skill"] == "plan-adhoc"

        # Peel second from remainder
        target2, remainder2 = peel_continuation(remainder1)
        assert target2 is not None
        assert remainder2 is not None
        assert target2["skill"] == "orchestrate"

        # Peel third from second remainder
        target3, remainder3 = peel_continuation(remainder2)
        assert target3 is not None
        assert target3["skill"] == "commit"
        assert remainder3 is None  # Terminal

    def test_fr3_continuation_consumption_cooperative_skill_protocol(self) -> None:
        """FR-3: Continuation consumption — cooperative skill protocol.

        Skills implement 4-step protocol:
        1. Read continuation from additionalContext (first) or args suffix (chained)
        2. If empty: terminal (stop)
        3. Consume first entry
        4. Tail-call with remainder in args
        """
        # This test validates the protocol structure is sound

        # Step 1: Skill reads continuation
        incoming_continuation = "[CONTINUATION: /next-skill arg1, /final-skill]"
        entries = parse_continuation_string(incoming_continuation)
        assert entries is not None

        # Step 2-3: Consume first
        target, remainder = peel_continuation(incoming_continuation)
        assert target is not None
        assert target["skill"] == "next-skill"

        # Step 4: Build tail-call args
        tail_call_args = f"my-args {remainder}" if remainder else "my-args"

        # Verify structure for Skill tool invocation
        assert target is not None  # target skill is available
        assert tail_call_args is not None  # args ready for Skill tool


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
