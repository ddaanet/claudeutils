"""Token counting functionality using Anthropic API."""

import logging
from datetime import UTC, datetime
from pathlib import Path

from anthropic import Anthropic, APIError, AuthenticationError, RateLimitError
from pydantic import BaseModel

from claudeutils.exceptions import (
    ApiAuthenticationError,
    ApiRateLimitError,
    ModelResolutionError,
)

logger = logging.getLogger(__name__)


class ModelInfo(BaseModel):
    """Model information stored in cache."""

    id: str
    created_at: datetime


class CacheData(BaseModel):
    """Cache file structure."""

    fetched_at: datetime
    models: list[ModelInfo]


class TokenCount(BaseModel):
    """Token count for a single file."""

    path: str
    count: int


def resolve_model_alias(model: str, client: Anthropic, cache_dir: Path) -> str:
    """Resolve model alias to full model ID.

    If model starts with "claude-", return unchanged (official Anthropic alias).
    Otherwise, resolve via API or cache.

    Args:
        model: Model alias or ID to resolve
        client: Anthropic API client
        cache_dir: Directory for caching model lists

    Returns:
        Resolved full model ID
    """
    if model.startswith("claude-"):
        return model

    # Try to load from cache if it's fresh (< 24 hours old)
    cache_file = cache_dir / "models_cache.json"
    cache_ttl_hours = 24
    if cache_file.exists():
        # Check if cache is still fresh
        mtime = cache_file.stat().st_mtime
        age_seconds = datetime.now(tz=UTC).timestamp() - mtime
        if age_seconds < cache_ttl_hours * 3600:
            try:
                cache_data = CacheData.model_validate_json(cache_file.read_text())
                models = cache_data.models

                # Filter models containing the alias (case-insensitive)
                matching_models = [m for m in models if model.lower() in m.id.lower()]

                if matching_models:
                    # Sort by created_at descending and return latest
                    matching_models.sort(key=lambda m: m.created_at, reverse=True)
                    return matching_models[0].id
            except ValueError as e:
                logger.warning(
                    "Corrupted cache file at %s, will refresh from API: %s",
                    cache_file,
                    e,
                )

    # Cache miss or expired - query API
    try:
        models_response = client.models.list()
    except APIError as e:
        raise ModelResolutionError(model) from e

    # Convert API response to dict format
    models_list = [
        ModelInfo(
            id=model_obj.id,
            created_at=model_obj.created_at,
        )
        for model_obj in models_response
    ]

    # Write cache
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_to_write = CacheData(fetched_at=datetime.now(tz=UTC), models=models_list)
    cache_file.write_text(cache_to_write.model_dump_json())

    # Filter for matching models
    matching_models = [m for m in models_list if model.lower() in m.id.lower()]

    if matching_models:
        matching_models.sort(key=lambda m: m.created_at, reverse=True)
        return matching_models[0].id

    return model


def count_tokens_for_file(path: Path, model: str) -> int:
    """Count tokens in a file using Anthropic API.

    Args:
        path: Path to the file to count tokens for
        model: Model to use for token counting

    Returns:
        Number of tokens in the file
    """
    content = path.read_text()

    if not content:
        return 0

    client = Anthropic()
    try:
        response = client.messages.count_tokens(
            model=model,
            messages=[{"role": "user", "content": content}],
        )
    except AuthenticationError as e:
        raise ApiAuthenticationError from e
    except RateLimitError as e:
        raise ApiRateLimitError from e

    return response.input_tokens


def count_tokens_for_files(paths: list[Path], model: str) -> list[TokenCount]:
    """Count tokens in multiple files using Anthropic API.

    Args:
        paths: List of paths to count tokens for
        model: Model to use for token counting

    Returns:
        List of TokenCount objects with per-file counts
    """
    results = []
    for path in paths:
        count = count_tokens_for_file(path, model)
        results.append(TokenCount(path=str(path), count=count))
    return results


def calculate_total(results: list[TokenCount]) -> int:
    """Calculate total tokens across multiple file results.

    Args:
        results: List of TokenCount objects

    Returns:
        Sum of all token counts
    """
    return sum(result.count for result in results)
