from ai.utils.text_utils import TextUtils


def test_levenshtein_distance_correctness() -> None:
    # Test identical strings
    assert TextUtils.levenshtein_distance("kitten", "kitten") == 0
    assert TextUtils.levenshtein_distance("", "") == 0

    # Test empty strings
    assert TextUtils.levenshtein_distance("abc", "") == 3
    assert TextUtils.levenshtein_distance("", "xyz") == 3

    # Test substitutions
    assert TextUtils.levenshtein_distance("kitten", "sitten") == 1

    # Test insertions
    assert TextUtils.levenshtein_distance("kit", "kitten") == 3

    # Test deletions
    assert TextUtils.levenshtein_distance("kitten", "kit") == 3

    # Test complex edits
    assert TextUtils.levenshtein_distance("kitten", "sitting") == 3
    assert TextUtils.levenshtein_distance("flaw", "lawn") == 2


def test_levenshtein_distance_caching_and_symmetry() -> None:
    # Warm up cache
    d1 = TextUtils.levenshtein_distance("monkey", "donkey")
    assert d1 == 1

    # Verify symmetry uses the same cache/logic and returns correct value
    d2 = TextUtils.levenshtein_distance("donkey", "monkey")
    assert d2 == 1

    # Inspect cache stats
    stats = TextUtils._levenshtein_cached.cache_info()
    assert stats.hits >= 1
