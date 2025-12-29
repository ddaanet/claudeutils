"""CLI handler for tokens subcommand."""

# ruff: noqa: T201 - print statements are expected in CLI code
import json
import sys
from pathlib import Path

import platformdirs
from anthropic import Anthropic

from claudeutils.tokens import (
    TokenCount,
    calculate_total,
    count_tokens_for_file,
    resolve_model_alias,
)


def handle_tokens(model: str, files: list[str], *, json_output: bool = False) -> None:
    """Handle the tokens subcommand.

    Args:
        model: Model to use for token counting
        files: File paths to count tokens for
        json_output: Whether to output JSON format
    """
    if not files:
        print("Error: at least one file is required", file=sys.stderr)
        sys.exit(1)

    file_paths = files

    for filepath_str in file_paths:
        filepath = Path(filepath_str)
        if not filepath.exists():
            print(f"Error: {filepath_str} file not found", file=sys.stderr)
            sys.exit(1)

    client = Anthropic()
    cache_dir = Path(platformdirs.user_cache_dir("claudeutils"))
    resolved_model = resolve_model_alias(model, client, cache_dir)

    if json_output:
        results = []
        for filepath_str in file_paths:
            filepath = Path(filepath_str)
            count = count_tokens_for_file(filepath, resolved_model)
            results.append(TokenCount(path=str(filepath), count=count))
        total = calculate_total(results)
        output = {
            "model": resolved_model,
            "files": [{"path": r.path, "count": r.count} for r in results],
            "total": total,
        }
        print(json.dumps(output))
    else:
        print(f"Using model: {resolved_model}")
        results = []
        for filepath_str in file_paths:
            filepath = Path(filepath_str)
            count = count_tokens_for_file(filepath, resolved_model)
            results.append(TokenCount(path=filepath_str, count=count))
            print(f"{filepath_str}: {count} tokens")
        if len(results) > 1:
            total = calculate_total(results)
            print(f"Total: {total} tokens")
