"""Scraper for LHSAA power rating PDF files.

LHSAA publishes final power rating PDFs on lhsaa.org for each sport season.
Confirmed available: 2022, 2023, 2024, 2025 football power ratings (Select & Non-Select).

This module:
1. Downloads PDF files from LHSAA website
2. Extracts tabular power rating data using pdfplumber
3. Parses into structured records for database seeding

Typical PDF structure (football):
- Header with classification, division, select/non-select
- Columns: Rank, School, Record, Power Rating, Strength Factor
- One table per division/classification grouping
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import httpx
import pdfplumber


@dataclass
class ParsedPowerRating:
    school_name: str
    classification: str
    division: int
    select: bool
    season_year: int
    rank: int
    wins: int
    losses: int
    power_rating: float
    strength_factor: float


LHSAA_BASE_URL = "https://www.lhsaa.org"


async def download_pdf(url: str, save_path: Path) -> Path:
    """Download a PDF from the given URL and save locally."""
    save_path.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        save_path.write_bytes(response.content)
    return save_path


def parse_record(record_str: str) -> tuple[int, int]:
    """Parse a record string like '8-2' into (wins, losses)."""
    match = re.match(r"(\d+)\s*-\s*(\d+)", record_str.strip())
    if not match:
        return 0, 0
    return int(match.group(1)), int(match.group(2))


def detect_header_info(text: str) -> tuple[str, int, bool]:
    """Extract classification, division, and select status from page/section header text.

    Returns:
        (classification, division, is_select)
    """
    classification = "5A"
    division = 1
    is_select = False

    class_match = re.search(r"(Class\s+)?([1-5]A)", text, re.IGNORECASE)
    if class_match:
        classification = class_match.group(2).upper()

    div_match = re.search(r"Division\s+(\w+)", text, re.IGNORECASE)
    if div_match:
        div_str = div_match.group(1)
        roman_map = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5}
        division = roman_map.get(div_str.upper(), int(div_str) if div_str.isdigit() else 1)

    if re.search(r"\bselect\b", text, re.IGNORECASE):
        is_select = True

    return classification, division, is_select


def extract_power_ratings(pdf_path: Path, season_year: int) -> list[ParsedPowerRating]:
    """Extract power rating data from an LHSAA PDF file.

    Args:
        pdf_path: Path to the downloaded PDF.
        season_year: The season year (e.g. 2024).

    Returns:
        List of parsed power rating records.
    """
    results: list[ParsedPowerRating] = []

    with pdfplumber.open(pdf_path) as pdf:
        current_class = "5A"
        current_div = 1
        current_select = False

        for page in pdf.pages:
            page_text = page.extract_text() or ""

            # Check for header info on this page
            if any(kw in page_text.upper() for kw in ["CLASS", "DIVISION", "POWER"]):
                current_class, current_div, current_select = detect_header_info(page_text)

            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 4:
                        continue

                    # Skip header rows
                    cleaned = [str(cell).strip() if cell else "" for cell in row]
                    if any(h in cleaned[0].upper() for h in ["RANK", "RK", "#", "SCHOOL"]):
                        continue

                    # Try to parse: Rank, School, Record, Power Rating, [Strength Factor]
                    try:
                        rank_str = cleaned[0]
                        if not rank_str.isdigit():
                            continue

                        rank = int(rank_str)
                        school_name = cleaned[1]
                        wins, losses = parse_record(cleaned[2])
                        power_rating = float(cleaned[3])
                        strength_factor = float(cleaned[4]) if len(cleaned) > 4 and cleaned[4] else 0.0

                        results.append(ParsedPowerRating(
                            school_name=school_name,
                            classification=current_class,
                            division=current_div,
                            select=current_select,
                            season_year=season_year,
                            rank=rank,
                            wins=wins,
                            losses=losses,
                            power_rating=power_rating,
                            strength_factor=strength_factor,
                        ))
                    except (ValueError, IndexError):
                        continue

    return results
