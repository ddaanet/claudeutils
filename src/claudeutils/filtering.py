"""Filtering and categorization functions for feedback analysis."""


def is_noise(content: str) -> bool:
    """Detect if content is noise (command output, system messages, etc)."""
    if "<command-name>" in content:
        return True
    if "<bash-stdout>" in content or "<bash-input>" in content:
        return True
    if "Caveat:" in content or "Warmup" in content or "<tool_use_error>" in content:
        return True
    return len(content) < 10
