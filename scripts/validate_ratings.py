"""Validate the power rating engine against the 2025 LHSAA published data.

We can't fully replicate ratings without game-by-game results (who played whom).
But we CAN validate mathematical consistency:

1. Decompose each published rating into result_points + non-result components
2. Check that the implied opponent contribution is within theoretical bounds
3. Cross-check strength_factor against implied opponent quality
4. Flag any ratings that are mathematically inconsistent with the LHSAA formula
"""

import csv
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent / "data" / "seed" / "2025_football_power_ratings_final.csv"


def validate():
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)

    print(f"Loaded {len(rows)} teams from 2025 football power ratings\n")

    # --- Validation 1: Result Points Decomposition ---
    # power_rating = (wins * 10 + play_up_total + opp_wins_total) / games
    # So: avg_non_result = power_rating - (wins / games * 10)
    # This is avg(play_up + opp_wins) per game
    # Bounds: play_up >= 0, opp_wins in [0, 10]
    # So avg_non_result should be in [0, ~16] (max play_up ~6 + opp_wins 10)

    print("=" * 80)
    print("VALIDATION 1: Decompose ratings into result + non-result components")
    print("=" * 80)
    print(f"{'School':<40} {'Div':>4} {'Sel':>11} {'W-L':>5} {'Published':>9} "
          f"{'Avg Result':>10} {'Avg Non-R':>9} {'Flag':>6}")
    print("-" * 80)

    flagged = []
    all_non_result = []

    for row in rows:
        school = row["school"]
        wins = int(row["wins"])
        losses = int(row["losses"])
        games = wins + losses
        published_rating = float(row["power_rating"])
        strength = float(row["strength_factor"])
        division = row["division"]
        select_status = row["select_status"]

        if games == 0:
            continue

        avg_result = (wins * 10) / games
        avg_non_result = published_rating - avg_result
        all_non_result.append(avg_non_result)

        flag = ""
        # Non-result component should be >= 0 (play-up + opp wins are both >= 0)
        if avg_non_result < -0.05:
            flag = "LOW"
        # Non-result component shouldn't exceed ~16 (max play-up ~6 + max opp wins 10)
        elif avg_non_result > 16.05:
            flag = "HIGH"

        if flag:
            flagged.append((school, division, select_status, wins, losses,
                           published_rating, avg_result, avg_non_result, strength, flag))
            print(f"{school:<40} {division:>4} {select_status:>11} {wins}-{losses:>2} "
                  f"{published_rating:>9.2f} {avg_result:>10.2f} {avg_non_result:>9.2f} {flag:>6}")

    if not flagged:
        print("  No flags — all ratings are within theoretical bounds.")

    print(f"\nNon-result component stats across {len(all_non_result)} teams:")
    print(f"  Min:  {min(all_non_result):.2f}")
    print(f"  Max:  {max(all_non_result):.2f}")
    print(f"  Mean: {sum(all_non_result)/len(all_non_result):.2f}")

    # --- Validation 2: Strength Factor vs Opponent Quality ---
    # strength_factor = (sum_opp_class_rank + sum_opp_wins) / games
    # opp_wins_component = sum(opp_wins_i / opp_games_i * 10) / games
    # These are related but not identical. Strength factor includes class rank.
    # We expect: higher strength factor → higher non-result component (generally)

    print("\n" + "=" * 80)
    print("VALIDATION 2: Strength factor correlation with non-result component")
    print("=" * 80)

    # Compute correlation
    strengths = []
    non_results = []
    for row in rows:
        wins = int(row["wins"])
        losses = int(row["losses"])
        games = wins + losses
        if games == 0:
            continue
        published_rating = float(row["power_rating"])
        strength = float(row["strength_factor"])
        avg_result = (wins * 10) / games
        avg_nr = published_rating - avg_result
        strengths.append(strength)
        non_results.append(avg_nr)

    n = len(strengths)
    mean_s = sum(strengths) / n
    mean_nr = sum(non_results) / n
    cov = sum((s - mean_s) * (nr - mean_nr) for s, nr in zip(strengths, non_results)) / n
    std_s = (sum((s - mean_s) ** 2 for s in strengths) / n) ** 0.5
    std_nr = (sum((nr - mean_nr) ** 2 for nr in non_results) / n) ** 0.5
    correlation = cov / (std_s * std_nr) if std_s > 0 and std_nr > 0 else 0

    print(f"Pearson correlation: {correlation:.4f}")
    print("  (Expected: positive correlation, typically 0.5-0.9)")
    if correlation < 0.3:
        print("  WARNING: Low correlation — possible data issue or formula mismatch")
    elif correlation > 0.5:
        print("  GOOD: Strong positive correlation confirms formula alignment")

    # --- Validation 3: Winless/Undefeated Team Checks ---
    # Winless teams: rating = avg(play_up + opp_wins) per game
    #   Their rating IS the avg non-result component
    #   This should roughly correlate with strength_factor
    # Undefeated teams: rating = 10 + avg(play_up + opp_wins)

    print("\n" + "=" * 80)
    print("VALIDATION 3: Winless team ratings (pure opponent quality measure)")
    print("=" * 80)
    print(f"{'School':<40} {'Div':>4} {'Sel':>11} {'Record':>7} {'Rating':>7} "
          f"{'Strength':>9} {'Implied Avg Opp Wins':>20}")
    print("-" * 80)

    for row in rows:
        wins = int(row["wins"])
        losses = int(row["losses"])
        if wins != 0:
            continue
        games = wins + losses
        if games == 0:
            continue
        published_rating = float(row["power_rating"])
        strength = float(row["strength_factor"])
        school = row["school"]
        division = row["division"]
        select_status = row["select_status"]

        # For winless teams: rating = avg(play_up + opp_wins) per game
        # If all opponents are same division/class, play_up = 0
        # So rating ≈ avg opp_wins_pts = avg(opp_wins/opp_games * 10)
        # strength_factor = (sum_opp_class + sum_opp_wins) / games
        # If avg opp class rank ≈ 3 (middle), then avg opp wins ≈ strength - 3
        # Implied avg opp win pct ≈ rating / 10 (if no play-up)

        print(f"{school:<40} {division:>4} {select_status:>11} {wins}-{losses:>2}   "
              f"{published_rating:>7.2f} {strength:>9.2f} "
              f"{published_rating:>20.2f}")

    print("\n" + "=" * 80)
    print("VALIDATION 4: Undefeated team ratings (10 + opponent quality)")
    print("=" * 80)
    print(f"{'School':<40} {'Div':>4} {'Sel':>11} {'Record':>7} {'Rating':>7} "
          f"{'Strength':>9} {'Opp Quality':>12}")
    print("-" * 80)

    for row in rows:
        wins = int(row["wins"])
        losses = int(row["losses"])
        games = wins + losses
        if games == 0 or losses != 0:
            continue
        published_rating = float(row["power_rating"])
        strength = float(row["strength_factor"])
        school = row["school"]
        division = row["division"]
        select_status = row["select_status"]

        opp_quality = published_rating - 10.0

        print(f"{school:<40} {division:>4} {select_status:>11} {wins}-{losses:>2}   "
              f"{published_rating:>7.2f} {strength:>9.2f} {opp_quality:>12.2f}")

    # --- Validation 5: Cross-bracket comparison ---
    print("\n" + "=" * 80)
    print("VALIDATION 5: Bracket summary statistics")
    print("=" * 80)
    print(f"{'Bracket':<25} {'Teams':>5} {'Avg Rating':>11} {'Min':>7} {'Max':>7} "
          f"{'Avg SF':>7}")
    print("-" * 80)

    brackets: dict[str, list] = {}
    for row in rows:
        key = f"Div {row['division']} {row['select_status']}"
        brackets.setdefault(key, []).append(row)

    for bracket, team_rows in sorted(brackets.items()):
        ratings = [float(r["power_rating"]) for r in team_rows]
        sfs = [float(r["strength_factor"]) for r in team_rows]
        print(f"{bracket:<25} {len(team_rows):>5} {sum(ratings)/len(ratings):>11.2f} "
              f"{min(ratings):>7.2f} {max(ratings):>7.2f} {sum(sfs)/len(sfs):>7.2f}")

    # --- Summary ---
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total teams validated: {len(rows)}")
    print(f"Ratings outside theoretical bounds: {len(flagged)}")
    print(f"Strength factor correlation: {correlation:.4f}")
    if not flagged and correlation > 0.5:
        print("\nVERDICT: Data is mathematically consistent with the LHSAA formula.")
        print("To fully validate computed vs published ratings, we need game-by-game")
        print("results (who played whom, scores). The CSV only has aggregate records.")
        print("\nNext step: Scrape or obtain game schedules/results for 2025 football,")
        print("then run calculate_all_power_ratings() and compare output to published data.")
    else:
        print("\nWARNING: Some inconsistencies detected. Review flagged items above.")


if __name__ == "__main__":
    validate()
