# Refactoring Plan: CLI Complexity Reduction

**Goal:** Fix ruff complexity violations in `src/claudeutils/cli.py:54` (main function)

**Current violations:**
- C901: Complexity 22 > 10
- PLR0912: Branches 28 > 12
- PLR0915: Statements 93 > 50

**Strategy:** Extract each subcommand handler into a dedicated function. Main becomes a thin dispatcher.

**Target Agent:** Haiku

---

## Phase 1: Extract `list` Command Handler

### Step 1: Create `handle_list()` function

**Action:** Add function before `main()`

**Implementation:**
1. Read `src/claudeutils/cli.py` → $current_code
2. Add new function at line 53 (before `main`):

```python
def handle_list(project: str) -> None:
    """Handle the list subcommand.

    Args:
        project: Project directory path
    """
    sessions = list_top_level_sessions(project)
    if not sessions:
        print("No sessions found")
    else:
        for session in sessions:
            prefix = session.session_id[:8]
            print(f"[{prefix}] {session.title}")
```

3. In `main()`, replace lines 109-116 with:

```python
    if args.command == "list":
        handle_list(args.project)
```

**Verification:** Run `just test tests/test_cli_list.py` - **MUST pass**

**Does NOT require:** Other command handlers, new tests

---

## Phase 2: Extract `extract` Command Handler

### Step 2: Create `handle_extract()` function

**Action:** Add function after `handle_list()`

**Implementation:**
1. Read `src/claudeutils/cli.py` → $current_code
2. Add new function after `handle_list()`:

```python
def handle_extract(session_prefix: str, project: str, output: str | None) -> None:
    """Handle the extract subcommand.

    Args:
        session_prefix: Session ID or prefix to extract from
        project: Project directory path
        output: Optional output file path
    """
    try:
        session_id = find_session_by_prefix(session_prefix, project)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    feedback = extract_feedback_recursively(session_id, project)
    json_output = json.dumps([item.model_dump(mode="json") for item in feedback])
    if output:
        Path(output).write_text(json_output)
    else:
        print(json_output)
```

3. In `main()`, replace lines 117-129 with:

```python
    elif args.command == "extract":
        handle_extract(args.session_prefix, args.project, args.output)
```

**Verification:** Run `just test tests/test_cli_extract.py` - **MUST pass**

**Does NOT require:** collect, analyze, rules handlers

---

## Phase 3: Extract `collect` Command Handler

### Step 3: Create `handle_collect()` function

**Action:** Add function after `handle_extract()`

**Implementation:**
1. Read `src/claudeutils/cli.py` → $current_code
2. Add new function after `handle_extract()`:

```python
def handle_collect(project: str, output: str | None) -> None:
    """Handle the collect subcommand.

    Args:
        project: Project directory path
        output: Optional output file path
    """
    sessions = list_top_level_sessions(project)
    all_feedback = []
    for session in sessions:
        try:
            feedback = extract_feedback_recursively(session.session_id, project)
            all_feedback.extend(feedback)
        except (ValueError, OSError, RuntimeError) as e:
            print(
                f"Warning: Failed to extract from {session.session_id}: {e}",
                file=sys.stderr,
            )
            continue

    json_output = json.dumps([item.model_dump(mode="json") for item in all_feedback])
    if output:
        Path(output).write_text(json_output)
    else:
        print(json_output)
```

3. In `main()`, replace lines 130-152 with:

```python
    elif args.command == "collect":
        handle_collect(args.project, args.output)
```

**Verification:** Run `just test tests/test_cli_collect.py` - **MUST pass**

**Does NOT require:** analyze, rules handlers

---

## Phase 4: Extract `analyze` Command Handler

### Step 4: Create `handle_analyze()` function

**Action:** Add function after `handle_collect()`

**Implementation:**
1. Read `src/claudeutils/cli.py` → $current_code
2. Add new function after `handle_collect()`:

```python
def handle_analyze(input_path: str, output_format: str) -> None:
    """Handle the analyze subcommand.

    Args:
        input_path: Input JSON file path (or '-' for stdin)
        output_format: Output format ('text' or 'json')
    """
    # Load feedback from file or stdin
    if input_path == "-":
        json_text = sys.stdin.read()
    else:
        json_text = Path(input_path).read_text()

    feedback_data = json.loads(json_text)
    items = [FeedbackItem.model_validate(item) for item in feedback_data]

    # Filter and categorize
    filtered_items = filter_feedback(items)
    categories: dict[str, int] = {}
    for item in filtered_items:
        category = categorize_feedback(item)
        categories[category] = categories.get(category, 0) + 1

    # Output results
    if output_format == "json":
        output = {
            "total": len(items),
            "filtered": len(filtered_items),
            "categories": categories,
        }
        print(json.dumps(output))
    else:
        print(f"total: {len(items)}")
        print(f"filtered: {len(filtered_items)}")
        print("categories:")
        for category, count in categories.items():
            print(f"  {category}: {count}")
```

3. In `main()`, replace lines 153-183 with:

```python
    elif args.command == "analyze":
        handle_analyze(args.input, args.format)
```

**Verification:** Run `just test tests/test_cli_analyze.py` - **MUST pass**

**Does NOT require:** rules handler

---

## Phase 5: Extract `rules` Command Handler

### Step 5: Create `handle_rules()` function

**Action:** Add function after `handle_analyze()`

**Implementation:**
1. Read `src/claudeutils/cli.py` → $current_code
2. Add new function after `handle_analyze()`:

```python
def handle_rules(input_path: str, min_length: int, output_format: str) -> None:
    """Handle the rules subcommand.

    Args:
        input_path: Input JSON file path (or '-' for stdin)
        min_length: Minimum content length for rule-worthy items
        output_format: Output format ('text' or 'json')
    """
    # Load feedback from file or stdin
    if input_path == "-":
        json_text = sys.stdin.read()
    else:
        json_text = Path(input_path).read_text()

    feedback_data = json.loads(json_text)
    items = [FeedbackItem.model_validate(item) for item in feedback_data]

    # Filter noise and apply stricter rules
    filtered_items = filter_feedback(items)
    rule_items = [
        item
        for item in filtered_items
        if not (
            # Question check
            (
                item.content.lower().startswith("how ")
                or item.content.lower().startswith("claude code:")
            )
            # Length check (min configurable, max 1000)
            or len(item.content) < min_length
            or len(item.content) > 1000
        )
    ]

    # Sort by timestamp and deduplicate by prefix
    rule_items.sort(key=lambda x: x.timestamp)
    seen_prefixes: set[str] = set()
    deduped_items = []
    for item in rule_items:
        prefix = item.content[:100].lower()
        if prefix not in seen_prefixes:
            seen_prefixes.add(prefix)
            deduped_items.append(item)

    # Output results
    if output_format == "json":
        output = [
            {
                "index": i + 1,
                "timestamp": item.timestamp,
                "session_id": item.session_id,
                "content": item.content,
            }
            for i, item in enumerate(deduped_items)
        ]
        print(json.dumps(output))
    else:
        for i, item in enumerate(deduped_items, 1):
            print(f"{i}. {item.content}")
```

3. In `main()`, replace lines 184-235 with:

```python
    elif args.command == "rules":
        handle_rules(args.input, args.min_length, args.format)
```

**Verification:** Run `just test tests/test_cli_rules.py` - **MUST pass**

**⏸ CHECKPOINT:** Run `just dev` - **ALL tests MUST pass**. Run `just check` - if it fails, **STOP** (do NOT fix lint errors). User final review.

---

## Expected Outcome

**After refactoring:**
- `main()` reduces to ~50 lines (argparse setup + 5 dispatch calls)
- Complexity: 22 → ~5 (linear dispatch)
- Branches: 28 → 5 (one per command)
- Statements: 93 → ~45 (argparse only)
- **MUST** pass `just check` without violations

**Handler functions:**
- `handle_list()` - ~10 lines
- `handle_extract()` - ~15 lines
- `handle_collect()` - ~22 lines
- `handle_analyze()` - ~30 lines
- `handle_rules()` - ~55 lines

All handlers are simple, focused, and under complexity limits.

---

## Checkpoint Summary

| After Phase | Action |
|-------------|--------|
| Phase 5 | Run `just dev` - **ALL tests pass**, stop if `just check` fails |

**CRITICAL:** If `just check` fails, **STOP immediately**. Do NOT attempt to fix lint errors. Wait for user guidance.
