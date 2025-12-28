# Code Quality Module

---
author_model: claude-opus-4-5-20251101
semantic_type: workflow
expansion_sensitivity: medium
target_rules:
  strong: 6-8
  standard: 10-14
  weak: 14-18
---

## Semantic Intent

Code should be type-safe, well-tested, and free of noise. Files should stay small.
Documentation should explain why, not what.

---

## Critical (Tier 1)

### Type Safety

Full mypy strict mode required. All parameters and return types annotated. No `Any`
unless justified with comment. Use specific error codes for ignores:
`# type: ignore[arg-type]` not blanket `# type: ignore`.

### File Size Limits

Files SHOULD NOT exceed 300 lines. Files MUST NOT exceed 400 lines. When approaching 300
lines, plan to split before continuing.

---

## Important (Tier 2)

### Testing Standards

- All tests in `tests/` directory
- Use pytest parametrization for similar cases
- Test names describe what they verify
- Compare objects directly: `assert result == expected_obj`
- Factor repeated setup into plain helpers (not fixtures)
- Keep tests concise

### Code Style (Deslop)

Omit noise that doesn't aid comprehension:

- No excessive blank lines (max 1 between logical sections)
- No obvious comments (`# increment counter` before `counter += 1`)
- No redundant docstrings on private helpers with clear names
- Keep public interface docstrings compact

### Documentation Quality

Comments explain WHY, not WHAT. Remove comments that restate the code. Docstrings for
public interfaces only. Docstring should not exceed implementation length.

---

## Preferred (Tier 3)

### Function Structure

If a function requires internal section comments to navigate, extract sections into
smaller functions. Each function should do one thing.

### Lint Compliance

Address lint issues properly rather than suppressing them. Prefer architectural fixes
over `# noqa`. If suppression required, include explanation with reference.
