"""Unit tests for continuation registry builder.

Tests the registry building logic that scans skills and extracts cooperation
metadata from userpromptsubmit-shortcuts.py. Based on design Component 2 test
scenarios.
"""

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch

# Import the hook script as a module
hook_script_path = (
    Path(__file__).parent.parent
    / "agent-core"
    / "hooks"
    / "userpromptsubmit-shortcuts.py"
)
spec = importlib.util.spec_from_file_location(
    "userpromptsubmit_shortcuts", hook_script_path
)
assert spec is not None
assert spec.loader is not None
hook_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook_module)

extract_frontmatter = hook_module.extract_frontmatter
build_registry = hook_module.build_registry
get_cached_registry = hook_module.get_cached_registry
save_registry_cache = hook_module.save_registry_cache
get_cache_path = hook_module.get_cache_path
scan_skill_files = hook_module.scan_skill_files
get_enabled_plugins = hook_module.get_enabled_plugins
get_plugin_install_path = hook_module.get_plugin_install_path


class TestExtractFrontmatter:
    """Tests for frontmatter extraction from SKILL.md files."""

    def test_extract_valid_frontmatter(self, tmp_path: Path) -> None:
        """Extract valid YAML frontmatter from SKILL.md."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: design
continuation:
  cooperative: true
  default-exit:
    - /handoff --commit
    - /commit
---

# Design Skill
Description here.
""")

        frontmatter = extract_frontmatter(skill_file)

        assert frontmatter is not None
        assert frontmatter["name"] == "design"
        assert frontmatter["continuation"]["cooperative"] is True
        assert len(frontmatter["continuation"]["default-exit"]) == 2

    def test_extract_cooperative_false(self, tmp_path: Path) -> None:
        """Extract frontmatter with cooperative: false."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: experimental
continuation:
  cooperative: false
---

# Experimental Skill
""")

        frontmatter = extract_frontmatter(skill_file)

        assert frontmatter is not None
        assert frontmatter["continuation"]["cooperative"] is False

    def test_extract_no_frontmatter(self, tmp_path: Path) -> None:
        """Return None when SKILL.md has no frontmatter."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""# Design Skill

No frontmatter here.
""")

        frontmatter = extract_frontmatter(skill_file)

        assert frontmatter is None

    def test_extract_malformed_yaml(self, tmp_path: Path) -> None:
        """Return None when frontmatter is malformed YAML."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: design
continuation:
  cooperative: true
  default-exit: [invalid yaml: content
---

Content
""")

        frontmatter = extract_frontmatter(skill_file)

        assert frontmatter is None

    def test_extract_empty_continuation_block(self, tmp_path: Path) -> None:
        """Extract frontmatter with empty continuation block."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: design
continuation: {}
---

Content
""")

        frontmatter = extract_frontmatter(skill_file)

        assert frontmatter is not None
        assert frontmatter["continuation"] == {}


class TestScanSkillFiles:
    """Tests for skill file discovery."""

    def test_scan_finds_nested_skills(self, tmp_path: Path) -> None:
        """Scan finds SKILL.md files in nested directories."""
        # Create nested skill files
        (tmp_path / "design" / "nested").mkdir(parents=True)
        (tmp_path / "design" / "nested" / "SKILL.md").write_text("---\n---")

        (tmp_path / "plan").mkdir(parents=True)
        (tmp_path / "plan" / "SKILL.md").write_text("---\n---")

        files = scan_skill_files(tmp_path)

        assert len(files) == 2
        assert any("design" in str(f) for f in files)
        assert any("plan" in str(f) for f in files)

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        """Scan returns empty list for directory with no SKILL.md."""
        files = scan_skill_files(tmp_path)

        assert files == []

    def test_scan_nonexistent_directory(self, tmp_path: Path) -> None:
        """Scan returns empty list for nonexistent directory."""
        nonexistent = tmp_path / "does_not_exist"
        files = scan_skill_files(nonexistent)

        assert files == []


class TestCachePath:
    """Tests for cache path generation."""

    def test_cache_path_deterministic(self) -> None:
        """Same inputs produce same cache path."""
        paths = ["/skill/design/SKILL.md", "/skill/plan/SKILL.md"]
        project_dir = "/project"

        path1 = get_cache_path(paths, project_dir)
        path2 = get_cache_path(paths, project_dir)

        assert path1 == path2

    def test_cache_path_order_invariant(self) -> None:
        """Different order of paths produces same cache path."""
        paths1 = ["/skill/design/SKILL.md", "/skill/plan/SKILL.md"]
        paths2 = ["/skill/plan/SKILL.md", "/skill/design/SKILL.md"]
        project_dir = "/project"

        path1 = get_cache_path(paths1, project_dir)
        path2 = get_cache_path(paths2, project_dir)

        assert path1 == path2

    def test_cache_path_includes_hash(self) -> None:
        """Cache path includes hash component."""
        paths = ["/skill/design/SKILL.md"]
        project_dir = "/project"

        cache_path = get_cache_path(paths, project_dir)

        # Should be in TMPDIR and contain 'continuation-registry'
        assert "continuation-registry" in str(cache_path)


class TestRegistryCaching:
    """Tests for registry caching mechanism."""

    def test_save_and_load_cache(self, tmp_path: Path) -> None:
        """Save and load cache successfully."""
        # Create actual skill file that won't be modified
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("---\nname: design\n---")

        cache_path = tmp_path / "test_cache.json"
        registry = {
            "design": {
                "cooperative": True,
                "default-exit": ["/handoff --commit", "/commit"],
            }
        }
        paths = [str(skill_file)]

        save_registry_cache(registry, paths, cache_path)
        loaded = get_cached_registry(cache_path)

        assert loaded is not None
        assert loaded == registry

    def test_cache_invalidation_on_mtime(self, tmp_path: Path) -> None:
        """Cache invalidates when source file modified."""
        # Create a source skill file
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("---\nname: test\n---")

        cache_path = tmp_path / "cache.json"
        registry = {"test": {"cooperative": True, "default-exit": []}}
        paths = [str(skill_file)]

        # Save cache
        save_registry_cache(registry, paths, cache_path)

        # Verify cache is valid
        assert get_cached_registry(cache_path) is not None

        # Modify source file (advance mtime)
        time.sleep(0.01)
        skill_file.write_text("---\nname: test\nversion: 2\n---")

        # Cache should be invalidated
        assert get_cached_registry(cache_path) is None

    def test_cache_invalidation_on_deletion(self, tmp_path: Path) -> None:
        """Cache invalidates when source file deleted."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("---\nname: test\n---")

        cache_path = tmp_path / "cache.json"
        registry = {"test": {"cooperative": True, "default-exit": []}}
        paths = [str(skill_file)]

        # Save cache
        save_registry_cache(registry, paths, cache_path)

        # Delete source file
        skill_file.unlink()

        # Cache should be invalidated
        assert get_cached_registry(cache_path) is None

    def test_cache_missing_file(self, tmp_path: Path) -> None:
        """Get cache returns None for missing cache file."""
        cache_path = tmp_path / "nonexistent.json"

        loaded = get_cached_registry(cache_path)

        assert loaded is None

    def test_cache_malformed_json(self, tmp_path: Path) -> None:
        """Get cache returns None for malformed JSON."""
        cache_path = tmp_path / "cache.json"
        cache_path.write_text("{ invalid json }")

        loaded = get_cached_registry(cache_path)

        assert loaded is None

    def test_cache_missing_fields(self, tmp_path: Path) -> None:
        """Get cache returns None if required fields missing."""
        cache_path = tmp_path / "cache.json"
        cache_path.write_text(
            json.dumps(
                {
                    "registry": {},
                    # Missing 'paths' and 'timestamp'
                }
            )
        )

        loaded = get_cached_registry(cache_path)

        assert loaded is None


class TestBuildRegistry:
    """Tests for registry building (integration)."""

    def test_build_registry_cooperative_only(self, tmp_path: Path) -> None:
        """Build registry includes only cooperative skills."""
        skills_path = tmp_path / ".claude" / "skills"
        skills_path.mkdir(parents=True)

        # Cooperative skill
        (skills_path / "design").mkdir()
        (skills_path / "design" / "SKILL.md").write_text("""---
name: design
continuation:
  cooperative: true
  default-exit:
    - /handoff --commit
    - /commit
---
""")

        # Non-cooperative skill
        (skills_path / "experimental").mkdir()
        (skills_path / "experimental" / "SKILL.md").write_text("""---
name: experimental
continuation:
  cooperative: false
---
""")

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            # Clear cache to force rebuild
            cache_path = get_cache_path(
                [
                    str(skills_path / "design" / "SKILL.md"),
                    str(skills_path / "experimental" / "SKILL.md"),
                ],
                str(tmp_path),
            )
            if cache_path.exists():
                cache_path.unlink()

            registry = build_registry()

        assert "design" in registry
        assert registry["design"]["cooperative"] is True
        assert "experimental" not in registry

    def test_build_registry_missing_continuation_block(self, tmp_path: Path) -> None:
        """Skills without continuation block are excluded."""
        skills_path = tmp_path / ".claude" / "skills"
        skills_path.mkdir(parents=True)

        # Skill with no continuation block
        (skills_path / "legacy").mkdir()
        (skills_path / "legacy" / "SKILL.md").write_text("""---
name: legacy
---
""")

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            cache_path = get_cache_path(
                [str(skills_path / "legacy" / "SKILL.md")], str(tmp_path)
            )
            if cache_path.exists():
                cache_path.unlink()

            registry = build_registry()

        assert "legacy" not in registry

    def test_build_registry_empty_default_exit(self, tmp_path: Path) -> None:
        """Registry includes skills with empty default-exit."""
        skills_path = tmp_path / ".claude" / "skills"
        skills_path.mkdir(parents=True)

        (skills_path / "commit").mkdir()
        (skills_path / "commit" / "SKILL.md").write_text("""---
name: commit
continuation:
  cooperative: true
  default-exit: []
---
""")

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            cache_path = get_cache_path(
                [str(skills_path / "commit" / "SKILL.md")], str(tmp_path)
            )
            if cache_path.exists():
                cache_path.unlink()

            registry = build_registry()

        assert "commit" in registry
        assert registry["commit"]["default-exit"] == []

    def test_build_registry_no_project_dir(self) -> None:
        """Build registry returns empty dict when CLAUDE_PROJECT_DIR not set."""
        with patch.dict(os.environ, {}, clear=True):
            if "CLAUDE_PROJECT_DIR" in os.environ:
                del os.environ["CLAUDE_PROJECT_DIR"]

            registry = build_registry()

        assert registry == {}

    def test_build_registry_uses_cache(
        self, tmp_path: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """Build registry uses cache on second call (when files unchanged)."""
        skills_path = tmp_path / ".claude" / "skills"
        skills_path.mkdir(parents=True)

        (skills_path / "design").mkdir()
        (skills_path / "design" / "SKILL.md").write_text("""---
name: design
continuation:
  cooperative: true
  default-exit: []
---
""")

        # Set TMPDIR to tmp_path so cache is written where we can control it
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        monkeypatch.setenv("TMPDIR", str(cache_dir))

        # First call - builds registry
        registry1 = build_registry()

        # Verify it has the design skill
        assert "design" in registry1
        assert registry1["design"]["cooperative"] is True

        # Second call WITHOUT modifying files - should use cache
        registry2 = build_registry()

        # Registry should be identical (from cache)
        assert registry2 == registry1
        assert "design" in registry2
        assert registry2["design"]["cooperative"] is True

    def test_build_registry_extracts_name_from_directory(self, tmp_path: Path) -> None:
        """Build registry uses directory name when 'name' field missing."""
        skills_path = tmp_path / ".claude" / "skills"
        skills_path.mkdir(parents=True)

        (skills_path / "myskill").mkdir()
        (skills_path / "myskill" / "SKILL.md").write_text("""---
continuation:
  cooperative: true
  default-exit: []
---
""")

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
            cache_path = get_cache_path(
                [str(skills_path / "myskill" / "SKILL.md")], str(tmp_path)
            )
            if cache_path.exists():
                cache_path.unlink()

            registry = build_registry()

        assert "myskill" in registry


class TestPluginSkillDiscovery:
    """Tests for plugin skill discovery."""

    def test_get_enabled_plugins_no_settings(self, tmp_path: Path) -> None:
        """Get enabled plugins returns empty list when settings don't exist."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            plugins = get_enabled_plugins()

        assert plugins == []

    def test_get_enabled_plugins_from_settings(self, tmp_path: Path) -> None:
        """Get enabled plugins reads from settings.json."""
        settings_file = tmp_path / ".claude" / "settings.json"
        settings_file.parent.mkdir(parents=True)
        settings_file.write_text(json.dumps({"enabledPlugins": ["plugin1", "plugin2"]}))

        with patch("pathlib.Path.home", return_value=tmp_path):
            plugins = get_enabled_plugins()

        assert "plugin1" in plugins
        assert "plugin2" in plugins

    def test_get_plugin_install_path_not_found(self, tmp_path: Path) -> None:
        """Get plugin install path returns None if plugin not in list.

        Tests behavior when plugin is not found in installed_plugins.json.
        """
        installed_file = tmp_path / ".claude" / "plugins" / "installed_plugins.json"
        installed_file.parent.mkdir(parents=True)
        installed_file.write_text(json.dumps({}))

        with patch("pathlib.Path.home", return_value=tmp_path):
            path = get_plugin_install_path("nonexistent", "/project")

        assert path is None

    def test_get_plugin_install_path_scope_filtering(self, tmp_path: Path) -> None:
        """Get plugin install path respects project scope."""
        installed_file = tmp_path / ".claude" / "plugins" / "installed_plugins.json"
        installed_file.parent.mkdir(parents=True)
        installed_file.write_text(
            json.dumps(
                {
                    "myplugin": {
                        "installPath": "/install/path",
                        "scope": "project",
                        "projectPath": "/other/project",
                    }
                }
            )
        )

        with patch("pathlib.Path.home", return_value=tmp_path):
            path = get_plugin_install_path("myplugin", "/my/project")

        # Should be None because projectPath doesn't match
        assert path is None

    def test_get_plugin_install_path_user_scope(self, tmp_path: Path) -> None:
        """Get plugin install path for user-scoped plugin."""
        installed_file = tmp_path / ".claude" / "plugins" / "installed_plugins.json"
        installed_file.parent.mkdir(parents=True)
        installed_file.write_text(
            json.dumps({"myplugin": {"installPath": "/install/path", "scope": "user"}})
        )

        with patch("pathlib.Path.home", return_value=tmp_path):
            path = get_plugin_install_path("myplugin", "/any/project")

        assert path == "/install/path"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
