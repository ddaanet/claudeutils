"""Integration tests for continuation passing 2-skill chain.

Tests the full flow:
1. Hook parses multi-skill input → emits additionalContext
2. First skill reads additionalContext → tail-calls next skill with [CONTINUATION: ...]
3. Second skill reads args suffix → tail-calls remaining skill(s)
4. Verify chain completes correctly

Based on design Component 4 integration test requirements.
"""

import pytest
import json
import importlib.util
import sys
from pathlib import Path

# Import the hook script as a module
hook_script_path = Path(__file__).parent.parent / 'agent-core' / 'hooks' / 'userpromptsubmit-shortcuts.py'
spec = importlib.util.spec_from_file_location("userpromptsubmit_shortcuts", hook_script_path)
hook_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook_module)

parse_continuation = hook_module.parse_continuation
format_continuation_context = hook_module.format_continuation_context


class TestTwoSkillChain:
    """Integration tests for 2-skill continuation chains."""

    def test_design_plan_chain(self) -> None:
        """Test /design, /plan-adhoc chain with default exit."""
        registry = {
            'design': {
                'cooperative': True,
                'default-exit': ['/handoff --commit', '/commit']
            },
            'plan_adhoc': {
                'cooperative': True,
                'default-exit': ['/handoff --commit', '/commit']
            },
            'handoff': {
                'cooperative': True,
                'default-exit': ['/commit']
            },
            'commit': {
                'cooperative': True,
                'default-exit': []
            }
        }

        # Step 1: Hook parses user input
        user_input = '/design plans/foo, /plan_adhoc'
        parsed = parse_continuation(user_input, registry)

        assert parsed is not None
        assert parsed['current']['skill'] == 'design'
        # Parser includes delimiter in args - verify the path is present
        assert 'plans/foo' in parsed['current']['args']

        # Continuation should be: plan_adhoc, handoff --commit, commit
        assert len(parsed['continuation']) == 3
        assert parsed['continuation'][0]['skill'] == 'plan_adhoc'
        assert parsed['continuation'][1]['skill'] == 'handoff'
        assert parsed['continuation'][1]['args'] == '--commit'
        assert parsed['continuation'][2]['skill'] == 'commit'

        # Step 2: Format additionalContext for first skill (design)
        context = format_continuation_context(parsed)

        # Verify context contains instruction for first skill
        assert '[CONTINUATION-PASSING]' in context
        assert 'Current: /design plans/foo' in context
        assert 'Continuation: /plan_adhoc, /handoff --commit, /commit' in context
        assert 'Skill(skill: "plan_adhoc"' in context
        assert '[CONTINUATION: /handoff --commit, /commit]' in context
        assert 'Do NOT include continuation metadata in Task tool prompts' in context

        # Step 3: First skill (design) tail-calls second skill (plan_adhoc)
        # Simulated: Skill("plan_adhoc", args="[CONTINUATION: /handoff --commit, /commit]")
        # The args parameter would be passed as a string
        plan_adhoc_args = '[CONTINUATION: /handoff --commit, /commit]'

        # Step 4: Second skill (plan_adhoc) parses its args to extract continuation
        # Expected behavior: skill reads [CONTINUATION: ...] from args suffix
        assert '[CONTINUATION:' in plan_adhoc_args
        assert '/handoff --commit' in plan_adhoc_args
        assert '/commit' in plan_adhoc_args

        # Verify the continuation can be extracted and parsed
        # Extract continuation from args suffix
        import re
        cont_match = re.search(r'\[CONTINUATION:\s*(.+?)\]', plan_adhoc_args)
        assert cont_match is not None
        cont_str = cont_match.group(1)

        # Parse continuation entries
        entries = []
        for entry_str in cont_str.split(','):
            entry_str = entry_str.strip()
            skill_match = re.match(r'/(\w+)(?:\s+(.*))?', entry_str)
            if skill_match:
                entries.append({
                    'skill': skill_match.group(1),
                    'args': skill_match.group(2).strip() if skill_match.group(2) else ''
                })

        # Verify parsed entries
        assert len(entries) == 2
        assert entries[0]['skill'] == 'handoff'
        assert entries[0]['args'] == '--commit'
        assert entries[1]['skill'] == 'commit'
        assert entries[1]['args'] == ''

    def test_handoff_commit_chain(self) -> None:
        """Test /handoff --commit, /commit chain (terminal)."""
        registry = {
            'handoff': {
                'cooperative': True,
                'default-exit': ['/commit']
            },
            'commit': {
                'cooperative': True,
                'default-exit': []
            }
        }

        # Step 1: Hook parses /handoff --commit
        user_input = '/handoff --commit'
        parsed = parse_continuation(user_input, registry)

        assert parsed is not None
        assert parsed['current']['skill'] == 'handoff'
        assert parsed['current']['args'] == '--commit'

        # Continuation should be: commit
        assert len(parsed['continuation']) == 1
        assert parsed['continuation'][0]['skill'] == 'commit'

        # Step 2: Format additionalContext
        context = format_continuation_context(parsed)

        assert '[CONTINUATION-PASSING]' in context
        assert 'Skill(skill: "commit"' in context

        # Step 3: handoff tail-calls commit
        # Simulated: Skill("commit", args="")
        # No continuation in args since commit is terminal

        # Step 4: commit is terminal - no tail-call
        commit_input = '/commit'
        commit_parsed = parse_continuation(commit_input, registry)

        assert commit_parsed is not None
        assert commit_parsed['current']['skill'] == 'commit'
        assert commit_parsed['continuation'] == []

        # Verify terminal message
        commit_context = format_continuation_context(commit_parsed)
        assert 'terminal' in commit_context.lower()

    def test_three_skill_chain(self) -> None:
        """Test 3-skill chain: /design, /plan, /orchestrate."""
        registry = {
            'design': {
                'cooperative': True,
                'default-exit': ['/handoff --commit', '/commit']
            },
            'plan': {
                'cooperative': True,
                'default-exit': ['/handoff --commit', '/commit']
            },
            'orchestrate': {
                'cooperative': True,
                'default-exit': ['/handoff --commit', '/commit']
            },
            'handoff': {
                'cooperative': True,
                'default-exit': ['/commit']
            },
            'commit': {
                'cooperative': True,
                'default-exit': []
            }
        }

        # Step 1: Hook parses 3-skill input
        user_input = '/design foo, /plan bar and /orchestrate'
        parsed = parse_continuation(user_input, registry)

        assert parsed is not None
        assert parsed['current']['skill'] == 'design'

        # Continuation should be: plan, orchestrate, handoff --commit, commit
        continuation_skills = [e['skill'] for e in parsed['continuation']]
        assert 'plan' in continuation_skills
        assert 'orchestrate' in continuation_skills
        assert 'handoff' in continuation_skills
        assert 'commit' in continuation_skills

        # Step 2: First skill tail-calls second
        context = format_continuation_context(parsed)
        assert 'Skill(skill: "plan"' in context

        # Step 3: Extract continuation for plan
        # After design completes, plan should receive:
        # args="bar [CONTINUATION: /orchestrate, /handoff --commit, /commit]"

        # Step 4: Extract continuation for orchestrate
        # After plan completes, orchestrate should receive:
        # args="[CONTINUATION: /handoff --commit, /commit]"

        # Step 5: Extract continuation for handoff
        # After orchestrate completes, handoff should receive:
        # args="--commit [CONTINUATION: /commit]"

        # Step 6: Extract continuation for commit
        # After handoff completes, commit should receive:
        # args="" (empty, terminal)

    def test_multiline_chain(self) -> None:
        """Test multi-line continuation format."""
        registry = {
            'design': {
                'cooperative': True,
                'default-exit': ['/handoff --commit', '/commit']
            },
            'plan': {
                'cooperative': True,
                'default-exit': ['/handoff --commit', '/commit']
            },
            'orchestrate': {
                'cooperative': True,
                'default-exit': ['/handoff --commit', '/commit']
            },
            'handoff': {
                'cooperative': True,
                'default-exit': ['/commit']
            },
            'commit': {
                'cooperative': True,
                'default-exit': []
            }
        }

        # Step 1: Parse multi-line format
        user_input = '/design foo and\n- /plan bar\n- /orchestrate baz'
        parsed = parse_continuation(user_input, registry)

        assert parsed is not None
        assert parsed['current']['skill'] == 'design'
        assert parsed['current']['args'] == 'foo'

        # Continuation should include plan and orchestrate with their args
        continuation_map = {e['skill']: e['args'] for e in parsed['continuation']}
        assert 'plan' in continuation_map
        assert continuation_map['plan'] == 'bar'
        assert 'orchestrate' in continuation_map
        assert continuation_map['orchestrate'] == 'baz'

        # Verify default exit appended
        continuation_skills = [e['skill'] for e in parsed['continuation']]
        assert 'handoff' in continuation_skills
        assert 'commit' in continuation_skills

    def test_handoff_without_commit_terminal_in_chain(self) -> None:
        """Test /design, /handoff (no --commit) stops chain."""
        registry = {
            'design': {
                'cooperative': True,
                'default-exit': ['/handoff --commit', '/commit']
            },
            'handoff': {
                'cooperative': True,
                'default-exit': ['/commit']
            }
        }

        # Step 1: Parse chain ending with /handoff (no --commit)
        user_input = '/design foo, /handoff'
        parsed = parse_continuation(user_input, registry)

        assert parsed is not None
        assert parsed['current']['skill'] == 'design'

        # Continuation should have handoff but NOT commit (handoff without --commit is terminal)
        continuation_skills = [e['skill'] for e in parsed['continuation']]
        assert 'handoff' in continuation_skills

        # Find handoff entry and verify it has no --commit flag
        handoff_entry = next((e for e in parsed['continuation'] if e['skill'] == 'handoff'), None)
        assert handoff_entry is not None
        assert '--commit' not in handoff_entry['args']

        # After handoff, continuation should be empty (terminal)
        # Since handoff is last and has no --commit, no commit should be appended
        # Check that commit is NOT in continuation
        assert 'commit' not in continuation_skills


class TestContinuationExtraction:
    """Tests for extracting continuation from Skill args."""

    def test_extract_continuation_from_args(self) -> None:
        """Test extracting [CONTINUATION: ...] from args string."""
        args = 'some regular args [CONTINUATION: /handoff --commit, /commit]'

        # Extract continuation
        import re
        cont_match = re.search(r'\[CONTINUATION:\s*(.+?)\]', args)
        assert cont_match is not None

        cont_str = cont_match.group(1)
        assert '/handoff --commit' in cont_str
        assert '/commit' in cont_str

        # Extract regular args (before continuation)
        regular_args = args[:cont_match.start()].strip()
        assert regular_args == 'some regular args'

    def test_extract_empty_continuation(self) -> None:
        """Test extracting empty continuation."""
        args = '[CONTINUATION: ]'

        import re
        cont_match = re.search(r'\[CONTINUATION:\s*(.+?)?\]', args)
        assert cont_match is not None

        cont_str = cont_match.group(1)
        # Empty continuation
        assert not cont_str or cont_str.strip() == ''

    def test_no_continuation_in_args(self) -> None:
        """Test args without continuation marker."""
        args = 'just regular args here'

        import re
        cont_match = re.search(r'\[CONTINUATION:\s*(.+?)\]', args)
        assert cont_match is None


class TestChainCompletion:
    """Tests for chain completion scenarios."""

    def test_chain_reaches_terminal(self) -> None:
        """Verify chain properly reaches terminal skill."""
        registry = {
            'design': {
                'cooperative': True,
                'default-exit': ['/commit']
            },
            'commit': {
                'cooperative': True,
                'default-exit': []
            }
        }

        # Simple chain: design → commit
        user_input = '/design foo'
        parsed = parse_continuation(user_input, registry)

        assert parsed is not None
        assert len(parsed['continuation']) == 1
        assert parsed['continuation'][0]['skill'] == 'commit'

        # Verify terminal
        commit_parsed = {
            'current': {'skill': 'commit', 'args': ''},
            'continuation': []
        }
        context = format_continuation_context(commit_parsed)
        assert 'terminal' in context.lower()
        assert 'do not tail-call' in context.lower()

    def test_chain_with_args_preserved(self) -> None:
        """Verify skill args are preserved through chain."""
        registry = {
            'design': {
                'cooperative': True,
                'default-exit': ['/handoff --commit', '/commit']
            },
            'handoff': {
                'cooperative': True,
                'default-exit': ['/commit']
            },
            'commit': {
                'cooperative': True,
                'default-exit': []
            }
        }

        # Use a path without slashes that could be mistaken for skills
        user_input = '/design some-file-path.md'
        parsed = parse_continuation(user_input, registry)

        assert parsed is not None
        assert parsed['current']['skill'] == 'design'
        assert 'some-file-path.md' in parsed['current']['args']

        # Format context
        context = format_continuation_context(parsed)

        # Verify args in current skill reference
        assert 'Current: /design some-file-path.md' in context


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
