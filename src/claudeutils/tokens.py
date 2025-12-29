"""Token counting functionality using Anthropic API."""

from pathlib import Path

from anthropic import Anthropic


def count_tokens_for_file(path: Path, model: str) -> int:
    """Count tokens in a file using Anthropic API.

    Args:
        path: Path to the file to count tokens for
        model: Model to use for token counting

    Returns:
        Number of tokens in the file
    """
    content = path.read_text()

    if not content:
        return 0

    client = Anthropic()
    response = client.messages.count_tokens(
        model=model,
        messages=[{"role": "user", "content": content}],
    )

    return response.input_tokens
