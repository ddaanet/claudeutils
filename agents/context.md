# Context

**Archive:** Previous context archived to [2026-01-07-bug4-complete.md](archive/2026-01-07-bug4-complete.md)

---

## Current State

**Branch:** `markdown`

**Current work:** Line Limit Refactoring - Tests Pass, Complexity Issues Remain

**Status:** Refactoring complete, all tests passing (315/315). Complexity violations present in refactored modules.

### Formatter Survey Results

**Survey completed:** 2026-01-07 (3 parallel research agents + practical testing)

**Candidates evaluated:**
1. **Prettier** - Popular formatter, but has idempotency bugs and YAML frontmatter issues
2. **markdownlint-cli2** - Linter only, not a formatter (ruled out)
3. **remark-cli** - ✅ **RECOMMENDED** - 100% CommonMark compliant, idempotent, highly configurable

**Deliverable:** `plans/formatter-comparison.md` (comprehensive 350+ line analysis)

**Test results:**
- Test corpus created: `tmp/test-remark.md` (12 test sections, 150+ lines)
- Prettier: Idempotent on corpus, but has documented bugs in production
- remark-cli: Idempotent on corpus, handles all edge cases correctly

**Dependencies installed:**
```bash
# Already in node_modules
remark-cli
remark-gfm
remark-frontmatter
remark-preset-lint-consistent
```

### Line Limit Refactoring (2026-01-22)

**Completed:** Refactored large markdown.py module into focused, well-typed modules

**Changes made:**
1. **Module split** - Created 4 new modules:
   - `markdown_block_fixes.py` (98 lines) - Code block fixes
   - `markdown_inline_fixes.py` (179 lines) - Inline backtick handling
   - `markdown_list_fixes.py` (352 lines) - List-related fixes
   - `markdown_parsing.py` (276 lines) - Segment parsing
   - `markdown.py` reduced from 976 to 125 lines

2. **Fixed configuration issues:**
   - Removed deprecated `[ruff]` section from agent-core/fragments/ruff.toml
   - Fixed mypy type annotations (11 errors fixed)
   - Fixed test imports (2 files)

3. **Updated inner fence behavior:**
   - Changed to upgrade ALL blocks with inner fences to 4 backticks (not just markdown)
   - Handles typical Claude output discussing code blocks
   - Updated 5 tests to reflect new behavior
   - Removed error-raising for inner fences (now auto-fixed)

**Test results:**
- ✅ All 315 tests passing (`just test`)
- ✅ All 154 markdown tests passing
- ✅ Mypy clean
- ⚠️ Complexity violations (`just dev`):
  - C901 (too complex): 5 functions
  - PLR0912 (too many branches): 3 functions
  - PLR0915 (too many statements): 2 functions
  - PLR0911 (too many returns): 1 function
- ⚠️ Minor issues: E501 line length (5 lines), D205 docstring format (1 line)

**Files modified:**
- src/claudeutils/markdown.py (refactored)
- src/claudeutils/markdown_block_fixes.py (new)
- src/claudeutils/markdown_inline_fixes.py (new)
- src/claudeutils/markdown_list_fixes.py (new)
- src/claudeutils/markdown_parsing.py (new)
- tests/test_markdown.py (2 tests updated)
- tests/test_markdown_block.py (1 test updated)
- tests/test_markdown_parsing.py (1 test updated)
- tests/test_cli_markdown.py (1 test updated)
- agent-core/fragments/ruff.toml (fixed)

---

## Handoff

**⚠️ STOP: Do not execute tasks below unless user explicitly requests it.**

These tasks are documented for context and planning. Wait for explicit instruction ("continue", "proceed", "start", etc.) before delegating or executing.

---

**Immediate next:** Address complexity violations (required for `just dev` to pass)

**Complexity violations:**
- `markdown_block_fixes.py::fix_markdown_code_blocks` - C901(14>10), PLR0912(17>12), PLR0915(54>50)
- `markdown_inline_fixes.py::escape_inline_backticks` - C901(14>10)
- `markdown_list_fixes.py::fix_metadata_blocks` - C901(13>10), PLR0912(13>12)
- `markdown_list_fixes.py::fix_warning_lines` - C901(22>10), PLR0911(9>6)
- `markdown_parsing.py::parse_segments` - C901(27>10), PLR0912(31>12), PLR0915(90>50)

**Options:**
1. Refactor complex functions (break into smaller helpers)
2. Add `# noqa` comments to suppress (not recommended for new code)
3. Adjust complexity thresholds in ruff config (last resort)

**Minor issues (can defer):**
- E501 line length: 5 lines across 3 files
- D205 docstring format: 1 line in markdown_list_fixes.py

**Or proceed to:** Markdown formatter migration (remark-cli) - complexity violations can be addressed later

**Implementation tasks (for haiku):**

1. **Create `.remarkrc.json` config** (configuration provided in comparison doc)
2. **Update `package.json` scripts:**
   - Add `format:md` script for formatting
   - Add `format:md:check` script for CI
3. **Create `.remarkignore`** (exclude node_modules, vendor, etc.)
4. **Test formatting on project markdown files:**
   - Run `remark . -o --quiet`
   - Verify `git diff` shows acceptable changes
   - Ensure no corruption of nested code blocks, YAML frontmatter, inline code
5. **Update justfile** (if dprint used there)
6. **Optional: Remove dprint** (if present and no longer needed)
7. **Commit migration** with clear commit message

**Reference documents:**
- `plans/formatter-comparison.md` - Full analysis and migration path
- `tmp/.remarkrc.json` - Example config (tested)
- `tmp/test-remark.md` - Formatted test corpus

**Key configuration (from comparison doc):**
```json
{
  "settings": {
    "bullet": "*",
    "fence": "`",
    "fences": true,
    "rule": "*",
    "emphasis": "*",
    "strong": "*",
    "incrementListMarker": true,
    "listItemIndent": "one"
  },
  "plugins": [
    "remark-gfm",
    "remark-frontmatter",
    "remark-preset-lint-consistent"
  ]
}
```

**Critical verification steps:**
- Check agents/*.md files preserve structure
- Check AGENTS.md table formatting
- Check nested code blocks in any docs
- Verify YAML frontmatter unchanged (if any files have it)

**Previous work (archived):**
- Bug #4: Inline Code Span Protection - Fixed and committed (482eacf) ✅
- Bugs #1-#3: All fixed and verified ✅

---

## Recent Decisions

**2026-01-07: Markdown Formatter Selection**
- **Decision:** Migrate to remark-cli for markdown formatting
- **Rationale:**
  - Prettier has documented idempotency bugs (empty sub-bullets, mid-word underscores, unstable lists)
  - Prettier has YAML frontmatter issues (strips comments, wraps long lists incorrectly)
  - markdownlint-cli2 is a linter, not a formatter
  - remark-cli: 100% CommonMark compliant, idempotent, highly configurable
- **Testing:** Both Prettier and remark-cli tested with comprehensive corpus, both passed
- **Production concerns:** Prettier's known bugs in production scenarios outweigh test success
- **Configuration:** 17+ formatting options in remark vs 2 in Prettier (better control)
- **Next step:** Implement migration (tasks documented in Handoff section)

**2026-01-06: Inline Code Span Protection Strategy** (archived to Bug #4)
- Protect only 1-2 backtick spans (`` `code` ``, ``` ``code`` ```)
- Escape 3+ backtick spans (`````python`, treated as fence markers)
- Rationale: Matches intent to escape potential fence markers while preserving actual inline code

**2026-01-06: Bugs #1/#2/#3 Root Cause** (archived)
- All three bugs caused by missing recursive parsing in `parse_segments()`
- Solution: Recursive parsing for ```markdown blocks (lines 224-268)

**2026-01-13: Model Selection for Delegation**
- **Decision:** Use haiku for execution tasks, opus only for architecture/planning
- **Rationale:**
  - Orchestrator made expensive mistake using opus for simple file operations
  - Cost impact: Session cost $4.46+ due to wrong model selection
  - Haiku is sufficient for straightforward execution tasks like file operations
  - Opus should be reserved for complex planning and architectural decisions
- **Implementation:** Update delegation principle in AGENTS.md to reflect this rule

---

## Blockers

**None currently.** Survey complete, ready for migration implementation.
