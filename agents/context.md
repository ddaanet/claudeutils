# Context

**Archive:** Previous context archived to [2026-01-07-bug4-complete.md](archive/2026-01-07-bug4-complete.md)

---

## Current State

**Branch:** `markdown`

**Current work:** Markdown Formatter Migration - Ready for Implementation

**Status:** Survey complete, ready to implement remark-cli migration

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

---

## Handoff

**Ready for implementation:** remark-cli migration

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

---

## Blockers

**None currently.** Survey complete, ready for migration implementation.
