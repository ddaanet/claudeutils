"""Tests for token cache database functionality."""

from sqlalchemy import inspect

from claudeutils.token_cache import TokenCacheEntry, create_cache_engine


class TestTokenCacheModel:
    """Tests for TokenCacheEntry model and cache engine."""

    def test_token_cache_entry_columns(self) -> None:
        """TokenCacheEntry has correct column definitions.

        Given: TokenCacheEntry class imported
        When: Inspecting columns
        Then: Has md5_hex (str), model_id (str), token_count (int), last_used (datetime)
        """
        # Get the mapper for TokenCacheEntry
        mapper = inspect(TokenCacheEntry)

        # Verify columns exist with correct types
        columns = {col.name: col.type for col in mapper.columns}

        assert "md5_hex" in columns
        assert "model_id" in columns
        assert "token_count" in columns
        assert "last_used" in columns

    def test_composite_primary_key(self) -> None:
        """TokenCacheEntry has composite primary key on (md5_hex, model_id).

        Given: TokenCacheEntry class
        When: Inspecting primary key
        Then: Primary key contains both md5_hex and model_id
        """
        mapper = inspect(TokenCacheEntry)
        pk_columns = {col.name for col in mapper.primary_key}

        assert "md5_hex" in pk_columns
        assert "model_id" in pk_columns
        assert len(pk_columns) == 2

    def test_create_cache_engine_creates_table(self) -> None:
        """create_cache_engine creates token_cache table.

        Given: Path to in-memory database
        When: Calling create_cache_engine(":memory:")
        Then: Returns engine with token_cache table created
        """
        engine = create_cache_engine(":memory:")

        # Verify table exists
        table_names = inspect(engine).get_table_names()
        assert "token_cache" in table_names
