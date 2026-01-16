# Plan: Add Token-Based File Size Checking

## Context

### Current State

**Line-based limits:**

- `scripts/check_line_limits.sh` enforces 400-line max for Python files in `src/` and
  `tests/`
- `justfile` has `check-lines` recipe that runs this script
- Line limit intended to prevent context bloat when agents read files

**Empirical data:**

- Total repo: 21,731 lines, 187,938 tokens (excluding uv.lock)
- Average token/line ratio: **8-10 tokens/line** (stable across file types)
- All Python files currently under 400-line limit
- Largest files by tokens:
  - plans/prompt-composer/sysprompt-integration/design.md: 6,235 tokens (595 lines, 10.5
    ratio)
  - tests/test_discovery.py: 3,288 tokens (280 lines, 11.7 ratio)
  - src/claudeutils/cli.py: 3,118 tokens (333 lines, 9.4 ratio)

### Problem Statement

Line count is a good proxy for file size, but:

1. Doesn't account for density (comments vs code, verbose vs terse)
2. Token count is what actually matters for agent context consumption
3. Need empirical data to determine appropriate thresholds

### Proposed Solution

**Option 2 (Hybrid approach):**

- Keep `just check-lines` as fast, offline, enforceable check (400 lines)
- Add `just check-tokens` as informational reporting tool
- Use token data to empirically determine if line limits need adjustment

---

## Implementation Plan

### Phase 1: Rename Existing Recipe

**Change in justfile:**

```diff
-check:
-    @echo "🔍 Running ruff and mypy..."
-    @ruff check
-    @mypy src tests
+check-lines:
+    @echo "📏 Checking line limits..."
+    @bash scripts/check_line_limits.sh

+check:
+    @echo "🔍 Running ruff and mypy..."
+    @ruff check
+    @mypy src tests
+    @just check-lines
```

**Impact:**

- `just check` now includes line limit validation
- Explicit `just check-lines` for targeted checking
- Backwards compatible (check still exists)

### Phase 2: Add Token Check Recipe

**New recipe in justfile:**

```just
check-tokens:
    @echo "🔢 Checking token counts (requires ANTHROPIC_API_KEY)..."
    @bash scripts/check_token_limits.sh
```

**New script: `scripts/check_token_limits.sh`**

```bash
#!/usr/bin/env bash
# Report token counts for versioned files (informational only)

set -euo pipefail

# Check for API key
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set, skipping token check"
    exit 0
fi

# Configuration
LIMIT=${1:-20}  # Default: show top 20
MODEL="sonnet"
EXCLUDE_PATTERNS="uv.lock"

echo "📊 Token analysis (top $LIMIT files by token count)"
echo ""

# Get all versioned text files, excluding patterns
git ls-files -z \
    | grep -zv "^${EXCLUDE_PATTERNS}$" \
    | xargs -0 file --mime-type \
    | grep 'text/' \
    | cut -d: -f1 \
    | while read -r file; do
        lines=$(wc -l < "$file" 2>/dev/null || echo 0)
        tokens=$(uv run claudeutils tokens "$MODEL" "$file" --json 2>/dev/null | jq -r '.files[0].count // 0')
        ratio=$(echo "scale=2; $tokens / $lines" | bc 2>/dev/null || echo "0")
        printf "%6d %6d %5s %s\n" "$lines" "$tokens" "$ratio" "$file"
    done \
    | sort -k2 -rn \
    | head -n "$LIMIT" \
    | awk 'BEGIN {printf "%-8s %-8s %-7s %s\n", "LINES", "TOKENS", "RATIO", "FILE"}
           {printf "%-8s %-8s %-7s %s\n", $1, $2, $3, $4}'

echo ""
echo "💡 Run 'just check-tokens N' to show top N files"
echo "💡 No threshold enforced (informational only)"

exit 0
```

**Features:**

- Shows top N files by token count (default 20)
- Includes lines, tokens, and ratio for each file
- Excludes uv.lock and other generated files
- Exit code 0 always (never fails builds)
- Gracefully handles missing API key

### Phase 3: Documentation Updates

**Update README.md Quick Command Reference:**

```diff
 # Development workflow
 just dev              # Format, check, and test (e2e tests skipped)
 just test ...         # Run pytest only, arguments are passed to pytest
 just test -m e2e      # Run e2e tests (requires ANTHROPIC_API_KEY)
 just check            # Run ruff + mypy only
+just check-lines      # Check Python files for 400-line limit
+just check-tokens     # Show token counts (requires ANTHROPIC_API_KEY)
 just format           # Auto-format code
```

**Update CLAUDE.md (if needed):**

- Add note about token checking for context awareness
- Reference empirical token/line ratio data

---

## Open Questions

### 1. Token Threshold

**Status:** ⚠️ NEEDS RESEARCH

**Question:** What token count indicates problematic context bloat?

**Empirical research needed:**

- At what file size do agents struggle with comprehension?
- Does it vary by file type (test vs source vs documentation)?
- Is there a "warning zone" before hard limit?

**Current approach:**

- No threshold enforced
- Gather empirical data from actual usage
- Revisit thresholds based on observed patterns

### 2. Scope

**Decision:** All text files

**Rationale:**

- Documentation/plans can also cause context bloat
- Token counting is fast enough with caching
- Provides complete picture of repository token usage

### 3. Output Format

**Decision:** KISS - Simple tabular format

```
LINES    TOKENS   RATIO   FILE
595      6235     10.47   plans/prompt-composer/design.md
333      3118      9.36   src/claudeutils/cli.py
```

No JSON, no color-coding, no fancy features. Just the data.

### 4. Integration with `just dev`

**Decision:** NOT a prerequisite for anything

- Informational only
- Manual invocation via `just check-tokens`
- Never blocks builds or development workflow

---

## Success Criteria

1. ✅ `just check-lines` runs existing line limit validation
2. ✅ `just check-tokens` reports token counts for all text files
3. ✅ Token check exits 0 always (informational only)
4. ✅ Token check handles missing API key gracefully
5. ✅ Output includes lines, tokens, and ratio
6. ✅ Documentation updated with new commands
7. ✅ Empirical data available to inform future threshold decisions

---

## Future Enhancements

**After gathering empirical data:**

1. **Add threshold warnings** (if patterns emerge):
   ```bash
   if [ "$tokens" -gt "$WARNING_THRESHOLD" ]; then
       echo "⚠️  $file: $tokens tokens (consider splitting)"
   fi
   ```

2. **Per-category thresholds**:
   - Source code: 2000 tokens
   - Tests: 3000 tokens
   - Documentation: 5000 tokens

3. **Integration with CI**:
   - Track token growth over time
   - Alert on significant increases
   - Suggest refactoring opportunities

4. **Token budget tracking**:
   - Show total tokens for common agent workflows
   - Estimate context consumption for typical operations

---

## Implementation Notes

### File Organization

- New script: `scripts/check_token_limits.sh`
- Modified: `justfile`
- Updated: `README.md`, possibly `CLAUDE.md`

### Dependencies

- Requires `uv run claudeutils tokens` command (already exists)
- Requires `jq` for JSON parsing
- Requires `bc` for ratio calculation
- Requires `ANTHROPIC_API_KEY` environment variable

### Testing

- Manually verify output format
- Test with missing API key
- Test with different LIMIT values
- Verify exclusion of uv.lock

### Rollout

1. Implement scripts and recipes
2. Run `just check-tokens` to establish baseline
3. Document findings in this plan or new analysis file
4. Use data to inform threshold decisions
5. Optionally add enforcement in Phase 2

---

## Analysis Questions to Answer

Once implemented, use `just check-tokens` to answer:

1. **Distribution:** What's the token count distribution across file types?
2. **Outliers:** Which files are significantly over average?
3. **Correlation:** Does token/line ratio vary by purpose (test vs source)?
4. **Trends:** Do certain patterns (complexity, abstractions) affect density?
5. **Thresholds:** What token count corresponds to "this file is too big"?

Document findings in `plans/analysis-token-thresholds.md` or similar.
