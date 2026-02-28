"""Artifact parser for recall Entry Keys section."""


def parse_trigger(entry_line: str) -> str:
    """Parse trigger string from entry line.

    Strips annotation (text after em dash), then detects operator (when/how). If
    entry lacks operator prefix, prepends "when".
    """
    # Strip annotation: split on first ' — ' and take left side
    base = entry_line.split(" — ")[0].strip()

    # Detect operator: check if first word (lowercased) is when/how
    first_word = base.split()[0].lower() if base.split() else ""
    if first_word in {"when", "how"}:
        return base

    # Bare trigger: prepend "when "
    return f"when {base}"


def parse_entry_keys_section(content: str) -> list[str] | None:
    """Parse Entry Keys section from artifact content.

    Returns list of entry lines from the Entry Keys section, or None if not
    found. Blank lines and comment lines (starting with #) are excluded.
    """
    lines = content.split("\n")

    heading_found = False
    for i, line in enumerate(lines):
        if line.strip() == "## Entry Keys":
            heading_found = True
            # Start collecting from the next line
            entries = []
            for entry_line in lines[i + 1 :]:
                stripped = entry_line.strip()
                if stripped and not stripped.startswith("#"):
                    entries.append(stripped)
            return entries if entries else []

    return None if not heading_found else []
