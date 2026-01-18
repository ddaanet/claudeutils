#!/bin/bash
# Build plan-specific agent from baseline agent + plan context
#
# Usage: build-plan-agent.sh <plan-name> <agent-name> <plan-context-file> <output-dir>
#
# Example:
#   build-plan-agent.sh phase2 phase2-task plans/unification/phase2-execution-plan.md .claude/agents
#
# This script creates a plan-specific agent by combining:
# 1. Baseline task-execute agent frontmatter and system prompt
# 2. Plan-specific context appended as additional sections
#
# The resulting agent can be used for executing plan steps with full plan context.
#
# IMPORTANT: Agents must be actual files in .claude/agents/, not symlinks.
# Claude Code scans .claude/agents/ at startup and doesn't follow symlinks.

set -e

if [ $# -ne 4 ]; then
    echo "Usage: $0 <plan-name> <agent-name> <plan-context-file> <output-dir>"
    echo ""
    echo "Arguments:"
    echo "  plan-name          - Human-readable plan name (e.g., 'phase2', 'feature-x')"
    echo "  agent-name         - Agent identifier (e.g., 'phase2-task', 'feature-x-execute')"
    echo "  plan-context-file  - Path to markdown file with plan context"
    echo "  output-dir         - Directory to write agent file"
    echo ""
    echo "Example:"
    echo "  $0 phase2 phase2-task plans/unification/phase2-execution-plan.md .claude/agents"
    exit 1
fi

PLAN_NAME="$1"
AGENT_NAME="$2"
PLAN_CONTEXT_FILE="$3"
OUTPUT_DIR="$4"

# Resolve paths
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
# agent-core is a sibling directory, not a subdirectory
BASELINE_AGENT="/Users/david/code/agent-core/agents/task-execute.md"

# Validate inputs
if [ ! -f "$BASELINE_AGENT" ]; then
    echo "ERROR: Baseline agent not found: $BASELINE_AGENT"
    exit 1
fi

if [ ! -f "$PLAN_CONTEXT_FILE" ]; then
    echo "ERROR: Plan context file not found: $PLAN_CONTEXT_FILE"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

OUTPUT_FILE="$OUTPUT_DIR/$AGENT_NAME.md"

echo "Building plan-specific agent..."
echo "  Plan: $PLAN_NAME"
echo "  Agent: $AGENT_NAME"
echo "  Baseline: $BASELINE_AGENT"
echo "  Context: $PLAN_CONTEXT_FILE"
echo "  Output: $OUTPUT_FILE"
echo ""

# Extract frontmatter from baseline (everything between first two --- markers)
# Then extract system prompt (everything after second ---)
# We'll replace the frontmatter with plan-specific version

# Step 1: Create plan-specific frontmatter
cat > "$OUTPUT_FILE" << FRONTMATTER_EOF
---
name: $AGENT_NAME
description: Use this agent to execute $PLAN_NAME steps. This agent specializes in executing tasks from the $PLAN_NAME plan with full plan context. Examples:

<example>
Context: Executing $PLAN_NAME step from plan
user: "Execute $PLAN_NAME step 1"
assistant: "I'll use the $AGENT_NAME agent to execute this step."
<commentary>
This step requires $PLAN_NAME context for proper execution.
</commentary>
</example>

<example>
Context: Running $PLAN_NAME task
user: "Run the next $PLAN_NAME task"
assistant: "I'll invoke the $AGENT_NAME agent."
<commentary>
The agent has full $PLAN_NAME plan context and can execute steps correctly.
</commentary>
</example>

model: inherit
color: cyan
tools: ["Read", "Write", "Bash", "Grep", "Glob"]
---

FRONTMATTER_EOF

# Step 2: Append baseline system prompt (skip frontmatter)
# Extract everything after the second --- marker
awk '/^---$/ {count++; next} count >= 2 {print}' "$BASELINE_AGENT" >> "$OUTPUT_FILE"

# Step 3: Append plan context separator
cat >> "$OUTPUT_FILE" << SEPARATOR_EOF

---

## PLAN CONTEXT: $PLAN_NAME

This section contains plan-specific context. The general task execution behavior above still applies, but with added plan knowledge.

SEPARATOR_EOF

# Step 4: Append plan context content
cat "$PLAN_CONTEXT_FILE" >> "$OUTPUT_FILE"

echo "✓ Created plan-specific agent: $OUTPUT_FILE"
echo ""
echo "To use this agent:"
echo "  1. Ensure it's in .claude/agents/ or symlinked"
echo "  2. Reference in task delegation: 'Use $AGENT_NAME agent to execute...'"
echo "  3. Agent will have full $PLAN_NAME context during execution"
