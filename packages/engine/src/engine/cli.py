"""CLI for running PrepRank simulations.

Usage:
    python -m engine.cli simulate --sport football --season 2025 --week 5
    python -m engine.cli ratings --sport football --season 2025 --week 11
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import psycopg2
from engine.types import (
    TeamRecord, GameResult, GameStatus,
    ScheduledGame, SimulationConfig,
)
from engine.power_rating import calculate_all_ratings
from engine.monte_carlo import run_simulation

DIVISION_TO_CLASSIFICATION = {"I": "5A", "II": "4A", "III": "3A", "IV": "2A", "V": "1A"}


def get_db_url() -> str:
    return os.environ.get("DATABASE_URL", "postgresql://preprank:preprank@127.0.0.1:5432/preprank")


def load_teams(cur, sport_name: str, season_year: int) -> dict[int, TeamRecord]:
    cur.execute("""
        SELECT t.id, s.name, t.division, s.classification
        FROM teams t JOIN schools s ON t.school_id = s.id
        JOIN sports sp ON t.sport_id = sp.id
        WHERE sp.name = %s AND t.season_year = %s
    """, (sport_name, season_year))
    teams = {}
    for row in cur.fetchall():
        tid, name, div, cls = row
        if cls is None:
            cls = DIVISION_TO_CLASSIFICATION.get(div, "5A")
        teams[tid] = TeamRecord(team_id=tid, school_name=name, division=div, classification=cls)
    return teams


def load_played_games(cur, sport_name: str, season_year: int, up_to_week: int | None = None) -> list[GameResult]:
    sql = """
        SELECT g.id, g.home_team_id, g.away_team_id, g.home_score, g.away_score,
               g.status, g.week_number
        FROM games g JOIN sports sp ON g.sport_id = sp.id
        WHERE sp.name = %s AND g.season_year = %s AND g.status IN ('final', 'forfeit')
    """
    params: list = [sport_name, season_year]
    if up_to_week is not None:
        sql += " AND g.week_number <= %s"
        params.append(up_to_week)
    cur.execute(sql, params)
    games = []
    for row in cur.fetchall():
        gid, h, a, hs, as_, status, wk = row
        games.append(GameResult(
            game_id=gid, home_team_id=h, away_team_id=a,
            home_score=hs, away_score=as_,
            status=GameStatus(status),
            is_forfeit=(status == "forfeit"),
            week_number=wk,
        ))
    return games


def load_remaining_games(cur, sport_name: str, season_year: int, after_week: int) -> list[ScheduledGame]:
    cur.execute("""
        SELECT g.id, g.home_team_id, g.away_team_id, g.week_number
        FROM games g JOIN sports sp ON g.sport_id = sp.id
        WHERE sp.name = %s AND g.season_year = %s AND g.status = 'scheduled'
          AND g.week_number > %s
    """, (sport_name, season_year, after_week))
    return [
        ScheduledGame(game_id=r[0], home_team_id=r[1], away_team_id=r[2], week_number=r[3])
        for r in cur.fetchall()
    ]


def cmd_ratings(args):
    conn = psycopg2.connect(get_db_url())
    cur = conn.cursor()
    try:
        teams = load_teams(cur, args.sport.title(), args.season)
        games = load_played_games(cur, args.sport.title(), args.season, args.week)
        print(f"Loaded {len(teams)} teams, {len(games)} games")
        result = calculate_all_ratings(teams, games)
        by_div: dict[str, list] = {}
        for t in result.values():
            by_div.setdefault(t.division, []).append(t)
        for div in sorted(by_div):
            print(f"\n=== Division {div} ===")
            ranked = sorted(by_div[div], key=lambda x: -x.power_rating)
            for i, t in enumerate(ranked, 1):
                print(f"  {i:>3}. {t.school_name:<30} {t.power_rating:>6.2f}  (SoS: {t.strength_factor:.2f})")
    finally:
        conn.close()


def cmd_simulate(args):
    conn = psycopg2.connect(get_db_url())
    cur = conn.cursor()
    try:
        sport = args.sport.title()
        teams = load_teams(cur, sport, args.season)
        played = load_played_games(cur, sport, args.season, args.week)
        remaining = load_remaining_games(cur, sport, args.season, args.week)
        print(f"Loaded {len(teams)} teams, {len(played)} played, {len(remaining)} remaining")
        config = SimulationConfig(
            sport_name=sport, season_year=args.season, week_number=args.week,
            num_runs=args.runs, playoff_spots=args.playoff_spots,
        )
        print(f"Running {config.num_runs} simulations...")
        start = time.time()
        projections = run_simulation(teams, played, remaining, config)
        elapsed = time.time() - start
        print(f"Completed in {elapsed:.1f}s\n")
        by_div: dict[str, list] = {}
        for tid, proj in projections.items():
            div = teams[tid].division
            by_div.setdefault(div, []).append((teams[tid], proj))
        for div in sorted(by_div):
            print(f"=== Division {div} ===")
            ranked = sorted(by_div[div], key=lambda x: -x[1].projected_rating_mean)
            for i, (t, p) in enumerate(ranked, 1):
                print(f"  {i:>3}. {t.school_name:<25} "
                      f"Rating: {p.projected_rating_mean:>6.2f} "
                      f"[{p.projected_rating_p10:.1f}-{p.projected_rating_p90:.1f}]  "
                      f"Playoff: {p.playoff_probability:>5.1f}%  "
                      f"W-L: {p.projected_wins_mean:.1f}-{p.projected_losses_mean:.1f}")
            print()
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(prog="engine", description="PrepRank Engine CLI")
    sub = parser.add_subparsers(dest="command")
    p_rate = sub.add_parser("ratings", help="Calculate power ratings")
    p_rate.add_argument("--sport", required=True)
    p_rate.add_argument("--season", type=int, required=True)
    p_rate.add_argument("--week", type=int, default=None)
    p_sim = sub.add_parser("simulate", help="Run Monte Carlo simulation")
    p_sim.add_argument("--sport", required=True)
    p_sim.add_argument("--season", type=int, required=True)
    p_sim.add_argument("--week", type=int, required=True)
    p_sim.add_argument("--runs", type=int, default=10000)
    p_sim.add_argument("--playoff-spots", type=int, default=8)
    args = parser.parse_args()
    if args.command == "ratings":
        cmd_ratings(args)
    elif args.command == "simulate":
        cmd_simulate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
