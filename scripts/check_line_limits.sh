#!/usr/bin/env bash
# Check that source files do not exceed 400 lines

set -euo pipefail

MAX_LINES=400
EXIT_CODE=0

# Find all Python source files (excluding venv and hidden directories)
while IFS= read -r -d '' file; do
    line_count=$(wc -l < "$file")
    if [ "$line_count" -gt "$MAX_LINES" ]; then
        echo "❌ $file: $line_count lines (exceeds $MAX_LINES line limit)"
        EXIT_CODE=1
    fi
done < <(find src tests -type f -name "*.py" -print0 2>/dev/null)

# Find all markdown files in agents/decisions/ directory
while IFS= read -r -d '' file; do
    line_count=$(wc -l < "$file")
    if [ "$line_count" -gt "$MAX_LINES" ]; then
        echo "❌ $file: $line_count lines (exceeds $MAX_LINES line limit)"
        EXIT_CODE=1
    fi
done < <(find agents/decisions -type f -name "*.md" -print0 2>/dev/null)

exit "$EXIT_CODE"
