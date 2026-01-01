"""CLI handler for tokens subcommand."""

# ruff: noqa: T201 - print statements are expected in CLI code
import json
import sys
from pathlib import Path

import platformdirs
from anthropic import Anthropic, AuthenticationError

from claudeutils.exceptions import (
    ApiAuthenticationError,
    ApiRateLimitError,
    ClaudeUtilsError,
)
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
    try:
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

        results = []
        for filepath_str in file_paths:
            filepath = Path(filepath_str)
            count = count_tokens_for_file(filepath, resolved_model, client)
            results.append(TokenCount(path=str(filepath), count=count))

        if json_output:
            total = calculate_total(results)
            output = {
                "model": resolved_model,
                "files": [{"path": r.path, "count": r.count} for r in results],
                "total": total,
            }
            print(json.dumps(output))
        else:
            print(f"Using model: {resolved_model}")
            for i, result in enumerate(results):
                print(f"{file_paths[i]}: {result.count} tokens")
            if len(results) > 1:
                total = calculate_total(results)
                print(f"Total: {total} tokens")
    except (AuthenticationError, ApiAuthenticationError, TypeError) as e:
        if isinstance(e, TypeError) and "authentication method" not in str(e).lower():
            raise
        print(f"Error: Authentication failed. {e}", file=sys.stderr)
        print("Please set ANTHROPIC_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)
    except ApiRateLimitError as e:
        print(f"Error: Rate limit exceeded. {e}", file=sys.stderr)
        sys.exit(1)
    except ClaudeUtilsError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
