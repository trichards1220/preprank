"""Scrape LHSAA power rating PDFs and output structured CSV.

LHSAA publishes final power rating PDFs on lhsaa.org for each sport season.
Confirmed available: 2022, 2023, 2024, 2025 football power ratings (Select & Non-Select).

Usage:
    python -m scripts.scrape_lhsaa_pdf --url <pdf_url> --year 2025 --output data/seed/output.csv
    python -m scripts.scrape_lhsaa_pdf --file data/pdfs/2024_football.pdf --year 2024

Output CSV format matches seed data:
    rank,school,power_rating,strength_factor,wins,losses,district,division,select_status,season_year
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import httpx
import pdfplumber


@dataclass
class ParsedPowerRating:
    rank: int
    school_name: str
    power_rating: float
    strength_factor: float
    wins: int
    losses: int
    district: int | None
    division: str  # "I", "II", "III", "IV"
    select_status: str  # "Select" or "Non-Select"
    season_year: int


def download_pdf(url: str, save_path: Path) -> Path:
    """Download a PDF from the given URL."""
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(follow_redirects=True, timeout=30.0) as client:
        response = client.get(url)
        response.raise_for_status()
        save_path.write_bytes(response.content)
    print(f"Downloaded: {save_path}")
    return save_path


def parse_record(record_str: str) -> tuple[int, int]:
    """Parse a record string like '8-2' into (wins, losses)."""
    match = re.match(r"(\d+)\s*-\s*(\d+)", record_str.strip())
    if not match:
        return 0, 0
    return int(match.group(1)), int(match.group(2))


def detect_header_info(text: str) -> tuple[str, str]:
    """Extract division and select status from page/section header text.

    Returns:
        (division_roman, select_status)
    """
    division = "I"
    select_status = "Non-Select"

    # Look for division in roman numerals
    div_match = re.search(r"Division\s+(I{1,3}V?|IV|V)", text, re.IGNORECASE)
    if div_match:
        division = div_match.group(1).upper()
    else:
        # Try numeric
        div_num_match = re.search(r"Division\s+(\d)", text, re.IGNORECASE)
        if div_num_match:
            num_to_roman = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            division = num_to_roman.get(div_num_match.group(1), "I")

    if re.search(r"\bselect\b", text, re.IGNORECASE):
        # Distinguish "Non-Select" from "Select"
        if re.search(r"\bnon[\s-]?select\b", text, re.IGNORECASE):
            select_status = "Non-Select"
        else:
            select_status = "Select"

    return division, select_status


def extract_power_ratings(pdf_path: Path, season_year: int) -> list[ParsedPowerRating]:
    """Extract power rating data from an LHSAA PDF file."""
    results: list[ParsedPowerRating] = []

    with pdfplumber.open(pdf_path) as pdf:
        current_div = "I"
        current_select = "Non-Select"

        for page in pdf.pages:
            page_text = page.extract_text() or ""

            if any(kw in page_text.upper() for kw in ["DIVISION", "SELECT", "POWER"]):
                current_div, current_select = detect_header_info(page_text)

            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 4:
                        continue

                    cleaned = [str(cell).strip() if cell else "" for cell in row]

                    # Skip header rows
                    if any(h in cleaned[0].upper() for h in ["RANK", "RK", "#", "SCHOOL"]):
                        continue

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
                            rank=rank,
                            school_name=school_name,
                            power_rating=power_rating,
                            strength_factor=strength_factor,
                            wins=wins,
                            losses=losses,
                            district=None,
                            division=current_div,
                            select_status=current_select,
                            season_year=season_year,
                        ))
                    except (ValueError, IndexError):
                        continue

    return results


def write_csv(ratings: list[ParsedPowerRating], output_path: Path):
    """Write parsed ratings to CSV in the standard seed format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "rank", "school", "power_rating", "strength_factor",
            "wins", "losses", "district", "division", "select_status", "season_year",
        ])
        for r in ratings:
            writer.writerow([
                r.rank, r.school_name, r.power_rating, r.strength_factor,
                r.wins, r.losses, r.district or "", r.division, r.select_status, r.season_year,
            ])
    print(f"Wrote {len(ratings)} records to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Scrape LHSAA power rating PDFs")
    parser.add_argument("--url", help="URL of the PDF to download and parse")
    parser.add_argument("--file", help="Path to a local PDF file to parse")
    parser.add_argument("--year", type=int, required=True, help="Season year")
    parser.add_argument("--output", default=None, help="Output CSV path (default: data/seed/<year>_football_power_ratings.csv)")
    args = parser.parse_args()

    if not args.url and not args.file:
        print("Error: provide either --url or --file", file=sys.stderr)
        sys.exit(1)

    if args.url:
        pdf_path = Path(f"data/pdfs/{args.year}_football_power_ratings.pdf")
        download_pdf(args.url, pdf_path)
    else:
        pdf_path = Path(args.file)

    ratings = extract_power_ratings(pdf_path, args.year)
    print(f"Extracted {len(ratings)} power ratings from {pdf_path.name}")

    output_path = Path(args.output) if args.output else Path(f"data/seed/{args.year}_football_power_ratings.csv")
    write_csv(ratings, output_path)


if __name__ == "__main__":
    main()
