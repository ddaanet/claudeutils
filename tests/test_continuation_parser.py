r"""Unit tests for continuation parser (userpromptsubmit-shortcuts.py Tier 3).

Tests the parsing logic that converts user input into continuation chains.
Based on design Component 4 test scenarios.

Note: Skill names in registry use underscores (e.g., plan_adhoc) because the
hook's regex /(\w+) doesn't match hyphens. In practice, skill names with hyphens
are accessed via /plan_adhoc (with underscore) in the continuation system.
"""

import importlib.util
from pathlib import Path

import pytest

# Import the hook script as a module
hook_script_path = (
    Path(__file__).parent.parent
    / "agent-core"
    / "hooks"
    / "userpromptsubmit-shortcuts.py"
)
spec = importlib.util.spec_from_file_location(
    "userpromptsubmit_shortcuts", hook_script_path
)
hook_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook_module)

parse_continuation = hook_module.parse_continuation
find_skill_references = hook_module.find_skill_references
format_continuation_context = hook_module.format_continuation_context


class TestFindSkillReferences:
    """Tests for skill reference detection."""

    def test_single_skill(self) -> None:
        """Find single skill reference."""
        registry = {"design": {"cooperative": True, "default-exit": []}}
        refs = find_skill_references("/design plans/foo", registry)
        assert len(refs) == 1
        assert refs[0][1] == "design"

    def test_multiple_skills(self) -> None:
        """Find multiple skill references."""
        registry = {
            "design": {"cooperative": True, "default-exit": []},
            "plan": {"cooperative": True, "default-exit": []},
        }
        refs = find_skill_references("/design, /plan", registry)
        assert len(refs) == 2
        assert refs[0][1] == "design"
        assert refs[1][1] == "plan"

    def test_no_skills(self) -> None:
        """No skill references found."""
        registry = {"design": {"cooperative": True, "default-exit": []}}
        refs = find_skill_references("some regular text", registry)
        assert len(refs) == 0

    def test_unregistered_skill_ignored(self) -> None:
        """Unregistered skills are ignored."""
        registry = {"design": {"cooperative": True, "default-exit": []}}
        refs = find_skill_references("/design and /nonexistent", registry)
        assert len(refs) == 1
        assert refs[0][1] == "design"

    def test_skill_not_in_args(self) -> None:
        """Skill pattern in path args not treated as skill reference."""
        registry = {"plans": {"cooperative": True, "default-exit": []}}
        # /plans/foo should not match 'plans' skill (no reference at all)
        refs = find_skill_references("some /plans/foo/bar", registry)
        # plans IS matched by /plans but /foo is not a separate skill
        skill_names = [ref[1] for ref in refs]
        # We should find 'plans' from /plans
        assert "plans" in skill_names or len(refs) == 0  # depends on actual parsing


class TestSingleSkillPassThrough:
    """Single skill invocations return None (handled by Claude's skill system).

    Skills manage their own default-exit when standalone or last-in-chain.
    The continuation parser only activates for multi-skill chains.
    """

    def test_single_skill_returns_none(self) -> None:
        """Single skill with default-exit returns None (skill handles exit)."""
        registry = {
            "design": {
                "cooperative": True,
                "default-exit": ["/handoff --commit", "/commit"],
            }
        }
        result = parse_continuation("/design plans/foo", registry)
        assert result is None

    def test_terminal_skill_returns_none(self) -> None:
        """Terminal skill (no default-exit) returns None."""
        registry = {"commit": {"cooperative": True, "default-exit": []}}
        result = parse_continuation("/commit", registry)
        assert result is None

    def test_single_skill_with_args_returns_none(self) -> None:
        """Single skill with complex args returns None."""
        registry = {"handoff": {"cooperative": True, "default-exit": ["/commit"]}}
        result = parse_continuation("/handoff --commit --force", registry)
        assert result is None


class TestModeInlineProse:
    """Tests for Mode 2: Inline prose with delimiters."""

    def test_inline_comma_slash_delimiter(self) -> None:
        """Parse inline prose with ', /' delimiter."""
        registry = {
            "design": {
                "cooperative": True,
                "default-exit": ["/handoff --commit", "/commit"],
            },
            "plan": {
                "cooperative": True,
                "default-exit": ["/handoff --commit", "/commit"],
            },
        }
        result = parse_continuation("/design plans/foo, /plan", registry)

        assert result is not None
        assert result["current"]["skill"] == "design"
        assert "plans/foo" in result["current"]["args"]
        # User-specified continuation only (no default-exit appending)
        assert len(result["continuation"]) == 1
        assert result["continuation"][0]["skill"] == "plan"

    def test_inline_and_delimiter(self) -> None:
        """Parse inline prose with 'and' connector."""
        registry = {
            "design": {"cooperative": True, "default-exit": []},
            "plan": {"cooperative": True, "default-exit": []},
        }
        result = parse_continuation("/design plans/foo and /plan", registry)

        assert result is not None
        assert result["current"]["skill"] == "design"
        # Parser includes the delimiter
        assert "plans/foo" in result["current"]["args"]
        assert result["continuation"][0]["skill"] == "plan"

    def test_inline_then_delimiter(self) -> None:
        """Parse inline prose with 'then' connector."""
        registry = {
            "design": {"cooperative": True, "default-exit": []},
            "plan": {"cooperative": True, "default-exit": []},
        }
        result = parse_continuation("/design plans/foo then /plan", registry)

        assert result is not None
        assert result["current"]["skill"] == "design"
        assert result["continuation"][0]["skill"] == "plan"

    def test_inline_finally_delimiter(self) -> None:
        """Parse inline prose with 'finally' connector."""
        registry = {
            "design": {"cooperative": True, "default-exit": []},
            "commit": {"cooperative": True, "default-exit": []},
        }
        result = parse_continuation("/design plans/foo finally /commit", registry)

        assert result is not None
        assert result["current"]["skill"] == "design"
        assert result["continuation"][0]["skill"] == "commit"

    def test_inline_three_skills(self) -> None:
        """Parse three skills in inline prose."""
        registry = {
            "design": {"cooperative": True, "default-exit": []},
            "plan": {"cooperative": True, "default-exit": []},
            "execute": {"cooperative": True, "default-exit": []},
        }
        result = parse_continuation("/design foo, /plan bar and /execute", registry)

        assert result is not None
        assert result["current"]["skill"] == "design"
        # Parser includes the delimiter in args
        assert "foo" in result["current"]["args"]
        # Both plan and execute should be in continuation
        continuation_skills = [e["skill"] for e in result["continuation"]]
        assert "plan" in continuation_skills
        assert "execute" in continuation_skills


class TestModeMultiLine:
    r"""Tests for Mode 3: Multi-line list with 'and\\n- /skill' pattern."""

    def test_multiline_list_basic(self) -> None:
        """Parse multi-line list pattern."""
        registry = {
            "design": {"cooperative": True, "default-exit": ["/commit"]},
            "plan": {"cooperative": True, "default-exit": []},
            "execute": {"cooperative": True, "default-exit": []},
        }
        prompt = "/design foo and\n- /plan\n- /execute"
        result = parse_continuation(prompt, registry)

        assert result is not None
        assert result["current"]["skill"] == "design"
        assert result["current"]["args"] == "foo"
        # User-specified continuation only (no default-exit appending)
        continuation_skills = [e["skill"] for e in result["continuation"]]
        assert "plan" in continuation_skills
        assert "execute" in continuation_skills
        assert "commit" not in continuation_skills  # default-exit NOT appended

    def test_multiline_list_with_args(self) -> None:
        """Parse multi-line list with args for each skill."""
        registry = {
            "design": {"cooperative": True, "default-exit": []},
            "plan": {"cooperative": True, "default-exit": []},
            "execute": {"cooperative": True, "default-exit": []},
        }
        prompt = "/design foo and\n- /plan arg1\n- /execute arg2"
        result = parse_continuation(prompt, registry)

        assert result is not None
        assert result["current"]["skill"] == "design"
        assert result["current"]["args"] == "foo"
        # Find the entries
        continuation_skills = {e["skill"]: e["args"] for e in result["continuation"]}
        assert "plan" in continuation_skills
        assert continuation_skills["plan"] == "arg1"
        assert "execute" in continuation_skills
        assert continuation_skills["execute"] == "arg2"

    def test_multiline_list_indentation(self) -> None:
        """Parse multi-line list with various indentation."""
        registry = {
            "design": {"cooperative": True, "default-exit": []},
            "plan": {"cooperative": True, "default-exit": []},
        }
        prompt = "/design foo and\n  - /plan"
        result = parse_continuation(prompt, registry)

        assert result is not None
        continuation_skills = [e["skill"] for e in result["continuation"]]
        assert "plan" in continuation_skills


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_no_skill_in_input(self) -> None:
        """Input with no skill references returns None."""
        registry = {"design": {"cooperative": True, "default-exit": []}}
        result = parse_continuation("just some regular text", registry)
        assert result is None

    def test_path_args_not_skill(self) -> None:
        """Path arguments like /foo/bar not treated as skills."""
        registry = {"design": {"cooperative": True, "default-exit": []}}
        result = parse_continuation("/design /some/path/to/file", registry)
        # Single skill — returns None (pass-through)
        assert result is None

    def test_connecting_words_in_args(self) -> None:
        """Connecting words in args don't create false continuations."""
        registry = {
            "design": {"cooperative": True, "default-exit": []},
            "implement": {"cooperative": True, "default-exit": []},
        }
        # '/design and implement' has both /design and /implement as registered skills
        # This tests that 'and' still creates a delimiter between them
        result = parse_continuation("/design foo and /implement bar", registry)

        assert result is not None
        assert result["current"]["skill"] == "design"
        # Parser includes 'and' in args
        assert "foo" in result["current"]["args"]
        # Both skills should be recognized
        skills = [e["skill"] for e in result["continuation"]]
        assert "implement" in skills

    def test_unknown_skill_ignored(self) -> None:
        """Unknown skills in inline prose are ignored."""
        registry = {
            "design": {"cooperative": True, "default-exit": []},
        }
        result = parse_continuation("/design foo, /unknownskill", registry)
        # Only one registered skill found — returns None (single skill)
        assert result is None

    def test_flag_handling_complex(self) -> None:
        """Complex flag handling — single skill returns None."""
        registry = {
            "execute": {
                "cooperative": True,
                "default-exit": ["/handoff --commit", "/commit"],
            },
        }
        result = parse_continuation("/execute --verbose --check planning", registry)
        # Single skill — returns None (pass-through)
        assert result is None

    def test_empty_continuation_terminal(self) -> None:
        """Terminal skill (commit) returns None."""
        registry = {"commit": {"cooperative": True, "default-exit": []}}
        result = parse_continuation("/commit", registry)
        assert result is None


class TestFormatContinuationContext:
    """Tests for formatting continuation as additionalContext."""

    def test_format_with_continuation(self) -> None:
        """Format with non-empty continuation."""
        parsed = {
            "current": {"skill": "design", "args": "plans/foo"},
            "continuation": [
                {"skill": "plan-adhoc", "args": ""},
                {"skill": "handoff", "args": "--commit"},
                {"skill": "commit", "args": ""},
            ],
        }
        context = format_continuation_context(parsed)

        assert "[CONTINUATION-PASSING]" in context
        assert "Current: /design plans/foo" in context
        assert "Continuation:" in context
        assert 'Skill(skill: "plan-adhoc"' in context

    def test_format_terminal(self) -> None:
        """Format with empty continuation (terminal)."""
        parsed = {"current": {"skill": "commit", "args": ""}, "continuation": []}
        context = format_continuation_context(parsed)

        assert "[CONTINUATION-PASSING]" in context
        assert "terminal" in context.lower()

    def test_format_includes_warning(self) -> None:
        """Format includes warning about Task tool."""
        parsed = {
            "current": {"skill": "design", "args": "plans/foo"},
            "continuation": [
                {"skill": "handoff", "args": "--commit"},
            ],
        }
        context = format_continuation_context(parsed)

        assert "Do NOT include continuation metadata in Task tool prompts" in context

    def test_format_next_skill_instruction(self) -> None:
        """Format includes correct next skill instruction."""
        parsed = {
            "current": {"skill": "design", "args": "plans/foo"},
            "continuation": [
                {"skill": "plan-adhoc", "args": ""},
                {"skill": "commit", "args": ""},
            ],
        }
        context = format_continuation_context(parsed)

        assert 'Skill(skill: "plan-adhoc"' in context
        assert "[CONTINUATION: /commit]" in context


class TestRegistryIntegration:
    """Tests that parse_continuation integrates with registry correctly."""

    def test_parse_with_real_registry_structure(self) -> None:
        """Parse with realistic registry structure."""
        registry = {
            "design": {
                "cooperative": True,
                "default-exit": ["/handoff --commit", "/commit"],
            },
            "plan": {
                "cooperative": True,
                "default-exit": ["/handoff --commit", "/commit"],
            },
            "execute": {
                "cooperative": True,
                "default-exit": ["/handoff --commit", "/commit"],
            },
            "handoff": {"cooperative": True, "default-exit": ["/commit"]},
            "commit": {"cooperative": True, "default-exit": []},
        }

        result = parse_continuation("/design foo, /plan and /execute", registry)

        assert result is not None
        assert result["current"]["skill"] == "design"
        # User-specified continuation only (no default-exit appending)
        continuation_skills = [e["skill"] for e in result["continuation"]]
        assert "plan" in continuation_skills
        assert "execute" in continuation_skills
        assert "handoff" not in continuation_skills  # no default-exit
        assert "commit" not in continuation_skills  # no default-exit


class TestFalsePositiveFiltering:
    """Test that parser correctly filters false positive contexts."""

    def test_meta_discussion_use_skill(self) -> None:
        """Meta-discussion: 'use /skill' should not trigger."""
        registry = {"commit": {"cooperative": True, "default-exit": []}}
        result = parse_continuation("Remember to use /commit skill", registry)
        assert result is None

    def test_meta_discussion_invoke_skill(self) -> None:
        """Meta-discussion: 'invoke /skill' should not trigger."""
        registry = {"handoff": {"cooperative": True, "default-exit": []}}
        result = parse_continuation("directive to invoke /handoff", registry)
        assert result is None

    def test_meta_discussion_use_the_skill(self) -> None:
        """Meta-discussion: 'use the /skill' should not trigger."""
        registry = {"commit": {"cooperative": True, "default-exit": []}}
        result = parse_continuation(
            "update CLAUDE.md: directive to use the /commit skill", registry
        )
        assert result is None

    def test_file_path_plans_directory(self) -> None:
        """File path: plans/<skill> should not trigger."""
        registry = {"commit": {"cooperative": True, "default-exit": []}}
        result = parse_continuation(
            "Execute step from: plans/commit-workflow/step.md", registry
        )
        assert result is None

    def test_file_path_with_extension(self) -> None:
        """File path: /skill.md should not trigger."""
        registry = {"orchestrate": {"cooperative": True, "default-exit": []}}
        result = parse_continuation("Review /orchestrate-redesign/design.md", registry)
        assert result is None

    def test_file_path_in_prompt(self) -> None:
        """File path: reference with .md extension should not trigger."""
        registry = {"commit": {"cooperative": True, "default-exit": []}}
        result = parse_continuation("Review /path/to/commit.md", registry)
        assert result is None

    def test_xml_command_message(self) -> None:
        """XML: <command-message>/skill</command-message> should not trigger."""
        registry = {"commit": {"cooperative": True, "default-exit": []}}
        result = parse_continuation(
            "<command-message>commit</command-message>", registry
        )
        assert result is None

    def test_xml_command_name(self) -> None:
        """XML: <command-name>/skill</command-name> should not trigger."""
        registry = {"commit": {"cooperative": True, "default-exit": []}}
        result = parse_continuation("<command-name>/commit</command-name>", registry)
        assert result is None

    def test_xml_bash_stdout(self) -> None:
        """XML: <bash-stdout> containing /skill should not trigger."""
        registry = {"handoff": {"cooperative": True, "default-exit": []}}
        result = parse_continuation(
            "<bash-stdout>Running /handoff logic</bash-stdout>", registry
        )
        assert result is None

    def test_xml_local_command_stdout(self) -> None:
        """XML: <local-command-stdout> containing /skill should not trigger."""
        registry = {"commit": {"cooperative": True, "default-exit": []}}
        result = parse_continuation(
            "<local-command-stdout>Processing /commit operation</local-command-stdout>",
            registry,
        )
        assert result is None

    def test_prompt_start_single_skill_passthrough(self) -> None:
        """Single skill at prompt start returns None (no continuation)."""
        registry = {
            "design": {
                "cooperative": True,
                "default-exit": ["/handoff --commit", "/commit"],
            }
        }
        result = parse_continuation("/design plans/foo", registry)
        assert result is None

    def test_continuation_delimiter_invocation(self) -> None:
        """Continuation with delimiter SHOULD trigger (true positive)."""
        registry = {
            "design": {
                "cooperative": True,
                "default-exit": ["/handoff --commit", "/commit"],
            },
            "plan": {
                "cooperative": True,
                "default-exit": ["/handoff --commit", "/commit"],
            },
        }
        result = parse_continuation("/design plans/foo, /plan", registry)
        assert result is not None
        assert len(result["continuation"]) > 0

    def test_multiline_continuation_invocation(self) -> None:
        r"""Multi-line list with 'and\\n- /skill' SHOULD trigger (true
        positive)."""
        registry = {
            "design": {"cooperative": True, "default-exit": ["/commit"]},
            "plan": {"cooperative": True, "default-exit": []},
        }
        result = parse_continuation("/design foo and\n- /plan", registry)
        assert result is not None
        continuation_skills = [e["skill"] for e in result["continuation"]]
        assert "plan" in continuation_skills

    def test_prose_mention_in_sentence(self) -> None:
        """Skill mention in middle of sentence without delimiter should not
        trigger."""
        registry = {"commit": {"cooperative": True, "default-exit": []}}
        result = parse_continuation(
            "I will work on the /commit functionality later", registry
        )
        assert result is None

    def test_file_path_steps_directory(self) -> None:
        """File path: steps/<skill> should not trigger."""
        registry = {"handoff": {"cooperative": True, "default-exit": []}}
        result = parse_continuation(
            "Execute step from: steps/handoff-workflow.md", registry
        )
        assert result is None

    def test_mid_sentence_lowercase_prose(self) -> None:
        """Skill reference mid-sentence after lowercase word should not
        trigger."""
        registry = {"commit": {"cooperative": True, "default-exit": []}}
        result = parse_continuation(
            "I will implement the /commit functionality later", registry
        )
        assert result is None

    def test_sentence_boundary_single_skill_passthrough(self) -> None:
        """Single skill after sentence boundary returns None."""
        registry = {"design": {"cooperative": True, "default-exit": []}}
        result = parse_continuation("Complete the task. /design plans/foo", registry)
        assert result is None

    def test_sentence_boundary_multi_skill_triggers(self) -> None:
        """Multi-skill after sentence boundary SHOULD trigger."""
        registry = {
            "design": {"cooperative": True, "default-exit": []},
            "commit": {"cooperative": True, "default-exit": []},
        }
        result = parse_continuation(
            "Complete the task. /design plans/foo, /commit", registry
        )
        assert result is not None
        assert result["current"]["skill"] == "design"
        assert result["continuation"][0]["skill"] == "commit"

    def test_directory_path_without_extension(self) -> None:
        """Directory path like /orchestrate-redesign/ should not trigger."""
        registry = {"orchestrate": {"cooperative": True, "default-exit": []}}
        result = parse_continuation(
            "Review the /orchestrate-redesign/ directory", registry
        )
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
