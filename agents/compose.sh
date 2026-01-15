#!/bin/bash
# agents/compose.sh
# Generates AGENTS.md from fragments defined in compose.yaml

FRAGMENTS=(
  "../agent-core/fragments/AGENTS-framework.md"
  "../agent-core/fragments/communication.md"
  "../agent-core/fragments/delegation.md"
  "../agent-core/fragments/tool-batching.md"
  "../agent-core/fragments/roles-rules-skills.md"
  "../agent-core/fragments/hashtags.md"
)

OUTPUT="AGENTS.md"

# Clear output
> "$OUTPUT"

# Concatenate fragments
for fragment in "${FRAGMENTS[@]}"; do
  if [ -f "$fragment" ]; then
    cat "$fragment" >> "$OUTPUT"
    echo "" >> "$OUTPUT"  # Blank line between fragments
  else
    echo "ERROR: Fragment not found: $fragment" >&2
    exit 1
  fi
done

echo "Generated $OUTPUT from ${#FRAGMENTS[@]} fragments"
