"""Tests for fuzzy matching engine."""

from claudeutils.when.fuzzy import score_match


def test_subsequence_match_scores_positive() -> None:
    """Subsequence matching scores positive for matches and exact > sparse."""
    # Subsequence found in order: positive score
    abc_sparse = score_match("abc", "aXbXc")
    assert isinstance(abc_sparse, float)
    assert abc_sparse > 0

    # No subsequence: zero or negative
    abc_missing = score_match("abc", "xyz")
    assert abc_missing <= 0

    # Exact match should score higher than sparse match
    abc_exact = score_match("abc", "abc")
    assert abc_exact > abc_sparse
