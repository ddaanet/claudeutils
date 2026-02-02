# Shell-to-Python Migration Learnings

Learnings from migrating shell-based claude-account/statusline tools to Python implementation.

---

## Code Duplication is Divergence Risk

**Context:** statusline-command.sh had duplicate `validate_state()`, `check_api_in_claude_env()` functions

**Anti-pattern:** Copying functions between scripts instead of extracting to shared library

**Solution:** Extract to shared lib, single source of truth

**Outcome:** Eliminated by Python rewrite with proper module structure

---

## Simple is Better

**Anti-pattern:** Elaborate symlink resolution, conditional time display, complex logic for simple tasks

**Correct:** Hard-code path when known, just display what you got, avoid over-engineering

**Example:** Statusline originally had complex timestamp formatting logic, simplified to direct display

---

## Python for Structured Data (Reinforced x3)

**Lesson:** Don't use grep/sed/awk for structured data manipulation

**Context:**
- LaunchAgent plist: `grep/sed` → `plistlib` for XML plist
- Config files: Shell string parsing → Python YAML/JSON parsing
- Full rewrite of shell tools to Python for maintainability

**Rationale:**
- Type safety with Pydantic models
- Structured validation
- Easier testing
- Better error messages

---

## Environment Variables Must Respect User Config

**Anti-pattern:** Hard-coding configuration paths in scripts

**Correct:** Respect user-configured environment variables like `LITELLM_CONFIG`

**Example:** LiteLLM config location should be configurable, not assumed

---

## Strict Validation Over Warnings

**Anti-pattern:** Warn about configuration issues but allow execution to continue

**Correct:** Config is single source of truth; strict validation with clear errors

**Rationale:**
- Fail fast on misconfiguration
- Clear error messages guide user to fix
- Prevent runtime issues from bad config

---

## Minor Issues Are Important

**User feedback:** "fix minor issues, they are important"

**Lesson:** Small bugs, inconsistencies, and edge cases deserve proper fixes, not workarounds

**Context:** Various small issues in shell implementation (timezone handling, exit codes, validation edge cases) accumulated technical debt
