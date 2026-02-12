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


def test_boundary_bonuses_applied() -> None:
    """Boundary bonuses applied for matches after whitespace/delimiters."""
    # Whitespace boundary bonus: 'ab' in "a b" has whitespace boundary on 'b'
    whitespace_bonus = score_match("ab", "a b")

    # No boundary bonus: 'ab' in "axb" has no boundary bonuses
    no_bonus = score_match("ab", "axb")

    # Whitespace boundary should score higher (bonusBoundaryWhite=10)
    assert whitespace_bonus > no_bonus

    # Delimiter boundary bonus: 'ab' in "a/b" has delimiter boundary on 'b'
    delimiter_bonus = score_match("ab", "a/b")

    # No boundary bonus: 'ab' in "axb" has no boundary bonuses
    no_bonus2 = score_match("ab", "axb")

    # Delimiter boundary should score higher (bonusBoundaryDelimiter=9)
    assert delimiter_bonus > no_bonus2

    # Whitespace boundary score > delimiter boundary score
    # (both have one boundary bonus, but whitespace=10 > delimiter=9)
    assert whitespace_bonus > delimiter_bonus


def test_consecutive_match_bonus() -> None:
    """Consecutive matched characters score higher due to consecutive bonus."""
    # Consecutive match: "mock" in "mock patching" has consecutive characters
    consecutive = score_match("mock", "mock patching")

    # Separated match: "mock" in "mXoXcXk" has no consecutive characters
    separated = score_match("mock", "mXoXcXk")

    # Consecutive should score higher
    assert consecutive > separated

    # Consecutive bonus: 4 per consecutive char after first
    # i=1: 16*2 (first char) = 32
    # i=2: 32 + 16 + 4 (consecutive) = 52
    ab_exact = score_match("ab", "ab")
    assert ab_exact == 52


def test_gap_penalties_reduce_score() -> None:
    """Gap penalties reduce score based on gap length and position."""
    # Shorter gap scores higher than longer gap
    short_gap = score_match("ac", "abc")
    long_gap = score_match("ac", "aXXXXc")

    assert short_gap > long_gap

    # Gap penalties: starting gap (first unmatched) = -3, each additional = -1
    single_gap = score_match("ac", "aXc")
    double_gap = score_match("ac", "aXXc")

    assert single_gap > double_gap
