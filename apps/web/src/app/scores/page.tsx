"use client";

import { useEffect, useState } from "react";
import { fetchGames, Game } from "@/lib/api";
import GameCard from "@/components/GameCard";

export default function ScoreboardPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sport, setSport] = useState("Football");

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchGames({ season_year: 2025, sport })
      .then(setGames)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [sport]);

  const SPORTS = ["Football", "Boys Basketball", "Girls Basketball", "Baseball", "Softball", "Boys Soccer", "Girls Soccer", "Volleyball"];

  // Group by week
  const byWeek: Record<number, Game[]> = {};
  for (const g of games) {
    const wk = g.week_number ?? 0;
    (byWeek[wk] ??= []).push(g);
  }
  const weeks = Object.keys(byWeek).map(Number).sort((a, b) => b - a);

  return (
    <main className="mx-auto max-w-5xl px-4 py-8">
      <h1
        className="mb-6 text-4xl font-bold tracking-tight"
        style={{ fontFamily: "var(--font-display)" }}
      >
        <span className="text-white">SCORE</span>
        <span className="text-crimson">BOARD</span>
      </h1>

      <div className="mb-6 flex items-center gap-4 flex-wrap">
        <select
          value={sport}
          onChange={(e) => setSport(e.target.value)}
          className="rounded border border-steel-gray bg-charcoal px-3 py-2 text-white focus:border-crimson focus:outline-none"
        >
          {SPORTS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <span className="text-steel-gray text-sm">2025 Season</span>
      </div>

      {loading && <p className="text-steel-gray">Loading scores...</p>}
      {error && <p className="text-crimson">Error: {error}</p>}

      {!loading && !error && games.length === 0 && (
        <div className="rounded-lg border border-steel-gray/30 p-8 text-center">
          <p className="text-lg text-steel-gray mb-2">No game results recorded yet</p>
          <p className="text-sm text-steel-gray/70">
            Game results will appear here once the season begins and scores are reported.
          </p>
        </div>
      )}

      {!loading && !error && weeks.map((wk) => (
        <section key={wk} className="mb-8">
          <h2
            className="text-lg font-bold mb-3 text-steel-gray"
            style={{ fontFamily: "var(--font-display)" }}
          >
            {wk > 0 ? `WEEK ${wk}` : "UNSCHEDULED"}
          </h2>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {byWeek[wk].map((g) => (
              <GameCard key={g.id} game={g} />
            ))}
          </div>
        </section>
      ))}
    </main>
  );
}
