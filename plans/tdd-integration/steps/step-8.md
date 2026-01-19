# Step 8

**Plan**: `plans/tdd-integration/runbook.md`
**Common Context**: See plan file for context

---

## Step 8: pytest-md integration

**Objective**: Integrate agent-core into pytest-md via submodule and remove old files

**Script Evaluation**: Medium script (~75 lines, mostly sequential operations)

**Execution Model**: Sonnet

**Working Directory**: Execute from claudeutils root (script handles directory changes via cd)

**Tool Usage**:
- Use Bash for all git operations, directory changes, file operations
- This step uses bash file operations (not Read/Write tools) because it's git/submodule work
- Never suppress errors with `|| true` or `2>/dev/null` except where explicitly intended

**Implementation**:

```bash
#!/usr/bin/env bash
# Integrate agent-core into pytest-md

set -e  # Exit on error

# Verify pytest-md directory exists
PYTEST_MD_DIR="$HOME/code/pytest-md"
if [[ ! -d "$PYTEST_MD_DIR" ]]; then
  echo "ERROR: pytest-md directory not found at $PYTEST_MD_DIR"
  exit 1
fi

cd "$PYTEST_MD_DIR"

# Add agent-core as submodule (if not already added)
if [[ ! -d agent-core ]]; then
  echo "Adding agent-core submodule..."
  git submodule add ../agent-core agent-core
else
  echo "✓ agent-core submodule already exists"
fi

# Initialize submodule (if needed)
git submodule update --init --recursive

# Verify agent-core sync recipe exists
if [[ ! -f agent-core/Makefile ]] && [[ ! -f agent-core/justfile ]]; then
  echo "WARNING: No sync recipe found in agent-core (expected Makefile or justfile)"
fi

# Run sync recipe if exists (install skills/agents)
if [[ -f agent-core/justfile ]]; then
  echo "Running agent-core sync recipe..."
  just -f agent-core/justfile sync
elif [[ -f agent-core/Makefile ]]; then
  echo "Running agent-core sync recipe..."
  make -C agent-core sync
else
  echo "SKIP: No sync recipe found - manual installation may be required"
fi

# Backup old skills (before removal)
if [[ -d .claude/skills ]] && [[ -n "$(ls -A .claude/skills 2>/dev/null)" ]]; then
  echo "Backing up old skills..."
  mkdir -p .backup/skills
  cp -r .claude/skills/* .backup/skills/
  echo "✓ Old skills backed up to .backup/skills/"

  # Remove old skills
  echo "Removing old project-specific skills..."
  rm -rf .claude/skills/*
  echo "✓ Old skills removed"
else
  echo "ℹ No skills to backup (directory empty or missing)"
fi

# Backup old agents (before removal)
if [[ -d .claude/agents ]] && [[ -n "$(ls -A .claude/agents 2>/dev/null)" ]]; then
  echo "Backing up old agents..."
  mkdir -p .backup/agents
  cp -r .claude/agents/* .backup/agents/
  echo "✓ Old agents backed up to .backup/agents/"

  # Remove old agents
  echo "Removing old project-specific agents..."
  rm -rf .claude/agents/*
  echo "✓ Old agents removed"
else
  echo "ℹ No agents to backup (directory empty or missing)"
fi

# Verify integration
echo ""
echo "Integration summary:"
echo "  Submodule: $(git submodule status agent-core | awk '{print $2, $1}')"
echo "  Old skills backed up: .backup/skills/"
echo "  Old agents backed up: .backup/agents/"
echo ""
echo "✓ pytest-md integration complete"
echo ""
echo "Next steps:"
echo "  1. Review .backup/ directory for any project-specific customizations"
echo "  2. Verify agent-core skills/agents are accessible"
echo "  3. Test TDD workflow with pytest-md project"
```

**Expected Outcome**:
- agent-core submodule added to pytest-md
- Submodule initialized and updated
- Sync recipe executed (skills/agents installed)
- Old skills backed up and removed
- Old agents backed up and removed
- Integration verified

**Unexpected Result Handling**:
- If pytest-md directory missing: STOP - verify path is correct
- If submodule add fails: Check if already exists, continue
- If sync recipe missing: Skip sync step, document manual installation needed
- If backup fails: Continue but warn user

**Error Conditions**:
- pytest-md not found → STOP and report
- Git operation fails → STOP and report
- Permission denied → STOP and report

**Validation**:
- Submodule exists: `git submodule status agent-core` in pytest-md
- Submodule initialized: `test -f agent-core/README.md` in pytest-md
- Old files backed up: `test -d .backup/skills` in pytest-md
- Old files removed: `test -z "$(ls -A .claude/skills)"` in pytest-md

**Success Criteria**:
- agent-core submodule added and initialized
- Old skills and agents backed up
- Old skills and agents removed
- Integration verified via git submodule status

**Report Path**: `plans/tdd-integration/reports/step-8-report.md`

---
