# Plan: CLI Inline Help Enhancement

**Status:** Ready for implementation

**Goal:** Enhance argparse help text so agents can use CLI without README.

---

## Help Text Specifications

### Main Parser

```python
parser = argparse.ArgumentParser(
    description="Extract feedback from Claude Code sessions",
    epilog="Pipeline: collect -> analyze -> rules. Use collect to gather all feedback, analyze to filter and categorize, rules to extract actionable items.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
```

### collect Parser

```python
collect_parser = subparsers.add_parser(
    "collect",
    help="Batch collect feedback from all sessions",
    description="Extract feedback from all sessions recursively, including sub-agents. Outputs JSON array of FeedbackItem objects.",
)
```

### analyze Parser

```python
analyze_parser = subparsers.add_parser(
    "analyze",
    help="Analyze feedback items",
    description="""Filter noise and categorize feedback items.

Categories:
  instructions  - Directives (don't, never, always, must, should)
  corrections   - Fixes (no, wrong, incorrect, fix, error)
  process       - Workflow (plan, next step, before, after)
  code_review   - Quality (review, refactor, improve, clarity)
  preferences   - Other substantive feedback

Noise filtered: command output, bash stdout, system messages, short messages (<10 chars).""",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
analyze_parser.add_argument(
    "--input", required=True, help="Input JSON file, or '-' for stdin"
)
```

### rules Parser

```python
rules_parser = subparsers.add_parser(
    "rules",
    help="Extract rule-worthy feedback items",
    description="""Extract actionable, rule-worthy feedback items.

Applies stricter filters than analyze:
  - Removes questions (starting with "How " or "claude code:")
  - Removes long items (>1000 chars)
  - Removes short items (<min-length, default 20 chars)
  - Deduplicates by first 100 characters

Output is sorted chronologically.""",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
rules_parser.add_argument(
    "--input", required=True, help="Input JSON file, or '-' for stdin"
)
```

---

## Feature: Enhanced Argparse Help

### Group A: Command Descriptions (Tests 1-3)

#### Test 1: `test_collect_help_describes_purpose`

**Given:** CLI with `--help` flag
**When:** `claudeutils collect --help` called
**Then:** Help text contains "all sessions" AND "recursively"

**Requires:** Update collect parser with description above
**Does NOT require:** Examples, epilog

#### Test 2: `test_analyze_help_lists_categories`

**Given:** CLI with `--help` flag
**When:** `claudeutils analyze --help` called
**Then:** Help text contains "instructions", "corrections", "process"

**Requires:** Update analyze parser with description above
**Does NOT require:** Filtering details in test assertion

#### Test 3: `test_rules_help_describes_filtering`

**Given:** CLI with `--help` flag
**When:** `claudeutils rules --help` called
**Then:** Help text contains "Deduplicates" AND "questions" AND "length"

**Requires:** Update rules parser with description above
**Does NOT require:** Examples

**CHECKPOINT A:** Run `just test -k test_help` (must pass). Run `just check` - if it fails, STOP. User review.

---

### Group B: Pipeline Context (Tests 4-5)

#### Test 4: `test_main_help_shows_pipeline`

**Given:** CLI with `--help` flag
**When:** `claudeutils --help` called
**Then:** Help text contains "collect" AND "analyze" AND "rules" AND "Pipeline"

**Requires:** Update main parser with epilog above
**Does NOT require:** Individual command epilogs

#### Test 5: `test_analyze_help_shows_stdin_usage`

**Given:** CLI with `--help` flag
**When:** `claudeutils analyze --help` called
**Then:** Input argument help contains "stdin"

**Requires:** Update `--input` help text as shown above
**Does NOT require:** Examples in epilog

**CHECKPOINT B:** Run `just test -k test_help` (must pass). Run `just check` - if it fails, STOP. **Complete.**

---

## Implementation Summary

All changes in `src/claudeutils/cli.py`:

1. Add `epilog` and `formatter_class` to main parser
2. Add `description` to collect parser
3. Add `description` and `formatter_class` to analyze parser
4. Add `description` and `formatter_class` to rules parser
5. Update `--input` help text for analyze and rules

Test file: `tests/test_cli_help.py`
