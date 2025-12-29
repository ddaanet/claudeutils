"""Unit tests for token counting functionality."""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from claudeutils.tokens import count_tokens_for_file, resolve_model_alias


class TestCountTokensForFile:
    """Tests for count_tokens_for_file function."""

    def test_count_tokens_for_simple_text(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Count tokens for a simple text file.

        Given: File with content "Hello world", model="sonnet"
        When: count_tokens_for_file(path, model) called
        Then: Returns integer token count > 0
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Mock Anthropic client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.input_tokens = 5
        mock_client.messages.count_tokens.return_value = mock_response

        # Patch the Anthropic client initialization
        monkeypatch.setattr(
            "claudeutils.tokens.Anthropic",
            Mock(return_value=mock_client),
        )

        # Call function
        result = count_tokens_for_file(test_file, "sonnet")

        # Verify
        assert isinstance(result, int)
        assert result > 0
        assert result == 5

    def test_count_tokens_for_markdown_with_code_blocks(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Count tokens for markdown file with code blocks.

        Given: File with markdown content including code block, model="opus"
        When: count_tokens_for_file(path, model) called
        Then: Returns token count reflecting full content
        """
        # Create test file with markdown and code block
        test_file = tmp_path / "test.md"
        content = """# Title

Some text here.

```python
def hello():
    print("world")
```

More text."""
        test_file.write_text(content)

        # Mock Anthropic client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.input_tokens = 42
        mock_client.messages.count_tokens.return_value = mock_response

        # Patch the Anthropic client initialization
        monkeypatch.setattr(
            "claudeutils.tokens.Anthropic",
            Mock(return_value=mock_client),
        )

        # Call function
        result = count_tokens_for_file(test_file, "opus")

        # Verify
        assert isinstance(result, int)
        assert result == 42

    def test_handle_empty_file(self, tmp_path: Path) -> None:
        """Handle empty files without API call.

        Given: Empty file, model="haiku"
        When: count_tokens_for_file(path, model) called
        Then: Returns 0
        """
        # Create empty test file
        test_file = tmp_path / "empty.md"
        test_file.write_text("")

        # Call function
        result = count_tokens_for_file(test_file, "haiku")

        assert result == 0


class TestResolveModelAlias:
    """Tests for resolve_model_alias function."""

    def test_pass_anthropic_aliases_through_unchanged(self, tmp_path: Path) -> None:
        """Pass Anthropic aliases through unchanged.

        Given: model="claude-sonnet-4-5" (official Anthropic alias)
        When: resolve_model_alias(model, client, cache_dir) called
        Then: Returns same ID unchanged (no API call, no cache check)
        """
        # Setup
        mock_client = Mock()
        cache_dir = tmp_path / "cache"

        # Call function
        result = resolve_model_alias("claude-sonnet-4-5", mock_client, cache_dir)

        # Verify
        assert result == "claude-sonnet-4-5"
        # Ensure no API calls were made
        mock_client.models.list.assert_not_called()

    def test_resolve_unversioned_alias_from_fresh_cache(self, tmp_path: Path) -> None:
        """Resolve unversioned alias from fresh cache.

        Given: Cache file exists with valid models list (created < 24h ago),
               includes `claude-haiku-4-5-20251001` and `claude-3-5-haiku-20241022`,
               model="haiku"
        When: resolve_model_alias(model, client, cache_dir) called
        Then: Returns `claude-haiku-4-5-20251001` from cache (no API call)
        """
        # Setup cache file
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        cache_file = cache_dir / "models_cache.json"

        cache_data = {
            "fetched_at": "2025-12-29T10:30:00Z",
            "models": [
                {
                    "id": "claude-haiku-4-5-20251001",
                    "created_at": "2025-10-01T00:00:00Z",
                },
                {
                    "id": "claude-3-5-haiku-20241022",
                    "created_at": "2024-10-22T00:00:00Z",
                },
            ],
        }
        cache_file.write_text(json.dumps(cache_data))

        # Mock client
        mock_client = Mock()

        # Call function
        result = resolve_model_alias("haiku", mock_client, cache_dir)

        # Verify - should return latest haiku model from cache
        assert result == "claude-haiku-4-5-20251001"
        # Ensure no API calls were made
        mock_client.models.list.assert_not_called()

    def test_resolve_unversioned_alias_with_cache_miss(self, tmp_path: Path) -> None:
        """Resolve unversioned alias with cache miss.

        Given: No cache file exists, mock API returns models list, model="sonnet"
        When: resolve_model_alias(model, client, cache_dir) called
        Then: Queries API, writes cache, returns latest sonnet model ID
        """
        # Setup: no cache file
        cache_dir = tmp_path / "cache"

        # Mock client with models list response
        mock_client = Mock()
        mock_models = [
            Mock(
                id="claude-sonnet-4-5-20250929",
                created_at=datetime.fromisoformat("2025-09-29T00:00:00Z"),
            ),
            Mock(
                id="claude-sonnet-4-5-20250915",
                created_at=datetime.fromisoformat("2025-09-15T00:00:00Z"),
            ),
        ]
        mock_client.models.list.return_value = mock_models

        # Call function
        result = resolve_model_alias("sonnet", mock_client, cache_dir)

        # Verify - should return latest sonnet model
        assert result == "claude-sonnet-4-5-20250929"
        # Verify API was called
        mock_client.models.list.assert_called_once()
        # Verify cache was written
        cache_file = cache_dir / "models_cache.json"
        assert cache_file.exists()

    def test_resolve_with_expired_cache(self, tmp_path: Path) -> None:
        """Resolve with expired cache.

        Given: Cache file exists but created > 24h ago, model="opus"
        When: resolve_model_alias(model, client, cache_dir) called
        Then: Ignores stale cache, queries API, updates cache
        """
        # Setup: create old cache file
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        cache_file = cache_dir / "models_cache.json"

        # Create cache with models older than 24h
        cache_data = {
            "fetched_at": "2025-12-27T10:30:00Z",
            "models": [
                {
                    "id": "claude-opus-4-20250228",
                    "created_at": "2025-02-28T00:00:00Z",
                },
            ],
        }
        cache_file.write_text(json.dumps(cache_data))

        # Make cache file's mtime > 24h old
        old_time = time.time() - (25 * 3600)  # 25 hours ago
        cache_file.touch()
        os.utime(cache_file, (old_time, old_time))

        # Mock client with new models
        mock_client = Mock()
        mock_models = [
            Mock(
                id="claude-opus-4-5-20251101",
                created_at=datetime.fromisoformat("2025-11-01T00:00:00Z"),
            ),
        ]
        mock_client.models.list.return_value = mock_models

        # Call function
        result = resolve_model_alias("opus", mock_client, cache_dir)

        # Verify - should return new opus model
        assert result == "claude-opus-4-5-20251101"
        # Verify API was called
        mock_client.models.list.assert_called_once()

    def test_handle_corrupted_cache_file(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Handle corrupted cache file.

        Given: Cache file exists but contains invalid JSON, model="haiku"
        When: resolve_model_alias(model, client, cache_dir) called
        Then: Treats as cache miss, queries API, overwrites corrupted cache
        """
        # Setup: create corrupted cache file
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        cache_file = cache_dir / "models_cache.json"

        # Write invalid JSON
        cache_file.write_text("{invalid json}")

        # Mock client with models
        mock_client = Mock()
        mock_models = [
            Mock(
                id="claude-haiku-4-5-20251001",
                created_at=datetime.fromisoformat("2025-10-01T00:00:00Z"),
            ),
        ]
        mock_client.models.list.return_value = mock_models

        # Call function
        result = resolve_model_alias("haiku", mock_client, cache_dir)

        # Verify warning was logged
        assert "Corrupted cache file" in caplog.text
        assert str(cache_file) in caplog.text

        # Verify - should return haiku model from API
        assert result == "claude-haiku-4-5-20251001"
        # Verify API was called
        mock_client.models.list.assert_called_once()
        # Verify cache was overwritten
        cached = json.loads(cache_file.read_text())
        assert cached["models"][0]["id"] == "claude-haiku-4-5-20251001"

    def test_create_cache_directory_if_missing(self, tmp_path: Path) -> None:
        """Create cache directory if missing.

        Given: Cache directory does not exist, model="sonnet"
        When: resolve_model_alias(model, client, cache_dir) called
        Then: Cache directory is created, cache file written successfully
        """
        # Setup: cache directory doesn't exist
        cache_dir = tmp_path / "nonexistent" / "nested" / "cache"

        # Mock client with models
        mock_client = Mock()
        mock_models = [
            Mock(
                id="claude-sonnet-4-5-20250929",
                created_at=datetime.fromisoformat("2025-09-29T00:00:00Z"),
            ),
        ]
        mock_client.models.list.return_value = mock_models

        # Call function
        result = resolve_model_alias("sonnet", mock_client, cache_dir)

        # Verify - should return sonnet model
        assert result == "claude-sonnet-4-5-20250929"
        # Verify cache directory was created
        assert cache_dir.exists()
        # Verify cache file was written
        cache_file = cache_dir / "models_cache.json"
        assert cache_file.exists()
