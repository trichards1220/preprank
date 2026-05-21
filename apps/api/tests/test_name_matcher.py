from app.services.name_matcher import normalize_name, find_best_match


def test_normalize_abbreviations():
    assert "saint" in normalize_name("St. Augustine")
    assert "baton rouge" in normalize_name("Central - B.R.")
    assert "shreveport" in normalize_name("Northwood - Shrev.")


def test_exact_match():
    candidates = {"Ruston": 1, "Neville": 2}
    assert find_best_match("Ruston", candidates) == 1


def test_fuzzy_match():
    candidates = {"Central - B.R.": 1, "Ruston": 2}
    assert find_best_match("Central Baton Rouge", candidates) == 1


def test_no_match_below_threshold():
    candidates = {"Ruston": 1, "Neville": 2}
    assert find_best_match("ZZZZZZ", candidates) is None


def test_abbreviation_match():
    candidates = {"Northwood - Shrev.": 1}
    result = find_best_match("Northwood Shreveport", candidates)
    assert result == 1
