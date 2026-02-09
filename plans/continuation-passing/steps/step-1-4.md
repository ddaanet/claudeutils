# Step 1.4

**Plan**: `plans/continuation-passing/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.4: Add Registry Caching (NFR-2)

**Objective:** Cache registry to temp file with mtime-based invalidation.

**Execution Model:** Sonnet

**Implementation:**

**Cache strategy:**
- Cache file: `$TMPDIR/continuation-registry-<hash>.json`
- Hash algorithm: SHA256 of concatenated sorted paths + project directory
  - Input: `sorted(skill_file_paths) + [CLAUDE_PROJECT_DIR]`
  - Output: first 16 chars of SHA256 hex digest
  - Example: `continuation-registry-a1b2c3d4e5f6g7h8.json`
- Invalidation: Any skill file mtime > cache mtime → rebuild

**Cache structure:**
```json
{
    "paths": [
        "/path/to/.claude/skills/design/SKILL.md",
        "/path/to/.claude/skills/plan-adhoc/SKILL.md",
        ...
    ],
    "registry": {
        "design": {"cooperative": true, "default_exit": [...]},
        ...
    },
    "timestamp": 1707350000
}
```

**Caching logic:**

```python
def get_cached_registry() -> Optional[dict]:
    """Load registry from cache if valid."""
    cache_path = get_cache_path()
    if not cache_path.exists():
        return None

    cache_data = json.loads(cache_path.read_text())

    # Check if any source file modified since cache
    for path in cache_data['paths']:
        if Path(path).stat().st_mtime > cache_data['timestamp']:
            return None  # Invalidated

    return cache_data['registry']

def save_registry_cache(registry: dict, paths: list) -> None:
    """Save registry to cache."""
    cache_path = get_cache_path()
    cache_data = {
        'paths': paths,
        'registry': registry,
        'timestamp': time.time()
    }
    cache_path.write_text(json.dumps(cache_data))
```

**Integration with Step 1.1:**

Modify `build_registry()` to check cache first:
```python
def build_registry() -> dict:
    cached = get_cached_registry()
    if cached is not None:
        return cached

    # Build from scratch (Step 1.1 logic)
    registry, paths = discover_and_parse()
    save_registry_cache(registry, paths)
    return registry
```

**Performance target:** <50ms first call, <5ms cached (NFR-2).

**Expected Outcome:**

Registry loads from cache on subsequent calls. Cache invalidates when skill files modified.

**Unexpected Result Handling:**
- Cache file corrupted → delete cache, rebuild
- Cache directory not writable → skip caching, build on every call (degraded mode)
- Hash collision (unlikely) → acceptable (just rebuilds unnecessarily)

**Validation:**
- First call builds registry and writes cache
- Second call loads from cache (<5ms)
- Modifying skill file invalidates cache
- Next call after invalidation rebuilds

**Success Criteria:**
- Cache file created at expected path
- Subsequent calls use cache (verify via timing or log)
- mtime-based invalidation works correctly
- Degraded mode works if caching unavailable

**Report Path:** `plans/continuation-passing/reports/step-1-4-execution.md`

---
