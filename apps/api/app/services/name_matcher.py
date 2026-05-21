"""Fuzzy school name matching for score ingestion.

LHSAA score pages may use different name formats than our database.
Examples: "Central - B.R." vs "Central Baton Rouge", "St. Aug" vs "St. Augustine"
"""
from __future__ import annotations
from difflib import SequenceMatcher


def normalize_name(name: str) -> str:
    """Normalize a school name for matching."""
    name = name.strip()
    # Common abbreviations
    replacements = {
        "St.": "Saint",
        "Mt.": "Mount",
        "Shrev.": "Shreveport",
        "B.R.": "Baton Rouge",
        "N.O.": "New Orleans",
        "Lk.": "Lake",
    }
    for abbr, full in replacements.items():
        name = name.replace(abbr, full)
    return name.lower().strip()


def find_best_match(
    query: str,
    candidates: dict[str, int],
    threshold: float = 0.6,
) -> int | None:
    """Find the best matching school name from candidates.

    Args:
        query: The name to match (from external source)
        candidates: Dict of {school_name: school_id}
        threshold: Minimum similarity ratio (0-1)

    Returns:
        school_id of best match, or None if no match above threshold
    """
    query_norm = normalize_name(query)
    best_score = 0.0
    best_id = None

    for name, school_id in candidates.items():
        name_norm = normalize_name(name)
        # Try exact match first
        if query_norm == name_norm:
            return school_id
        # Fuzzy match
        score = SequenceMatcher(None, query_norm, name_norm).ratio()
        if score > best_score and score >= threshold:
            best_score = score
            best_id = school_id

    return best_id
