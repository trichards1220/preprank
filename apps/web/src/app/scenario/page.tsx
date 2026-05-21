"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import {
  fetchTeams, fetchGames, calculateScenario, calculateBestCase, calculateWorstCase,
  Team, Game, ScenarioResult,
} from "@/lib/api";
import StatBar from "@/components/StatBar";
import Link from "next/link";

interface LockedOutcome {
  game_id: number;
  winner_team_id: number;
}

export default function ScenarioBuilderPage() {
  const { isPremium } = useAuth();

  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null);
  const [games, setGames] = useState<Game[]>([]);
  const [locked, setLocked] = useState<Record<number, number>>({});
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [bestCase, setBestCase] = useState<ScenarioResult | null>(null);
  const [worstCase, setWorstCase] = useState<ScenarioResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [teamsLoading, setTeamsLoading] = useState(true);
  const [error, setError] = useState("");

  // Load teams
  useEffect(() => {
    fetchTeams({ sport: "Football", season_year: 2025 })
      .then((t) => {
        setTeams(t);
        if (t.length > 0) setSelectedTeamId(t[0].id);
      })
      .catch(() => {})
      .finally(() => setTeamsLoading(false));
  }, []);

  // Load games when team selected
  useEffect(() => {
    if (!selectedTeamId) return;
    fetchGames({ season_year: 2025, sport: "Football" })
      .then(setGames)
      .catch(() => setGames([]));
  }, [selectedTeamId]);

  const scheduledGames = games.filter((g) => g.status === "scheduled");
  const lockedCount = Object.keys(locked).length;

  const toggleOutcome = (gameId: number, winnerId: number) => {
    setLocked((prev) => {
      if (prev[gameId] === winnerId) {
        const next = { ...prev };
        delete next[gameId];
        return next;
      }
      return { ...prev, [gameId]: winnerId };
    });
    setResult(null);
  };

  const handleCalculate = async () => {
    if (!selectedTeamId || !isPremium) return;
    setLoading(true);
    setError("");
    try {
      const outcomes: LockedOutcome[] = Object.entries(locked).map(([gid, wid]) => ({
        game_id: Number(gid),
        winner_team_id: wid,
      }));
      const res = await calculateScenario(selectedTeamId, outcomes);
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Calculation failed");
    } finally {
      setLoading(false);
    }
  };

  const handleBestCase = async () => {
    if (!selectedTeamId || !isPremium) return;
    setLoading(true);
    try {
      const res = await calculateBestCase(selectedTeamId);
      setBestCase(res);
      setResult(res);
    } catch { } finally { setLoading(false); }
  };

  const handleWorstCase = async () => {
    if (!selectedTeamId || !isPremium) return;
    setLoading(true);
    try {
      const res = await calculateWorstCase(selectedTeamId);
      setWorstCase(res);
      setResult(res);
    } catch { } finally { setLoading(false); }
  };

  const handleReset = () => {
    setLocked({});
    setResult(null);
    setBestCase(null);
    setWorstCase(null);
  };

  return (
    <main className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-4xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>
        <span className="text-white">SCENARIO</span>
        <span className="text-crimson"> BUILDER</span>
      </h1>
      <p className="text-steel-gray mb-6">Toggle game outcomes and see how they affect your team&apos;s playoff chances.</p>

      {/* Premium gate */}
      {!isPremium && (
        <div className="rounded-lg border border-crimson/30 p-8 text-center mb-8">
          <h2 className="text-xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>PREMIUM FEATURE</h2>
          <p className="text-steel-gray mb-4">The Scenario Builder lets you explore &quot;what if&quot; scenarios for your team&apos;s season.</p>
          <Link href="/pricing" className="inline-block rounded bg-crimson px-6 py-3 font-semibold text-white hover:bg-crimson/80 transition-colors">
            Upgrade to Premium — $4.99/mo
          </Link>
        </div>
      )}

      {/* Team selector */}
      <div className="mb-6">
        <label className="block text-sm text-steel-gray mb-2">Select Your Team</label>
        <select
          value={selectedTeamId ?? ""}
          onChange={(e) => { setSelectedTeamId(Number(e.target.value)); handleReset(); }}
          disabled={!isPremium}
          className="rounded border border-steel-gray bg-charcoal px-4 py-2 text-white focus:border-crimson focus:outline-none w-full max-w-md disabled:opacity-50"
        >
          {teamsLoading && <option>Loading teams...</option>}
          {teams.map((t) => (
            <option key={t.id} value={t.id}>{t.school_name} ({t.division})</option>
          ))}
        </select>
      </div>

      {/* Quick actions */}
      {isPremium && (
        <div className="flex gap-3 mb-6 flex-wrap">
          <button onClick={handleBestCase} disabled={loading}
            className="rounded border border-green-600 px-4 py-2 text-sm text-green-500 hover:bg-green-600/10 transition-colors disabled:opacity-50">
            Best Case
          </button>
          <button onClick={handleWorstCase} disabled={loading}
            className="rounded border border-red-600 px-4 py-2 text-sm text-red-500 hover:bg-red-600/10 transition-colors disabled:opacity-50">
            Worst Case
          </button>
          <button onClick={handleReset}
            className="rounded border border-steel-gray px-4 py-2 text-sm text-steel-gray hover:text-white transition-colors">
            Reset
          </button>
          <button onClick={handleCalculate} disabled={loading || lockedCount === 0}
            className="rounded bg-crimson px-6 py-2 text-sm font-semibold text-white hover:bg-crimson/80 transition-colors disabled:opacity-50 ml-auto">
            {loading ? "Calculating..." : `Calculate (${lockedCount} locked)`}
          </button>
        </div>
      )}

      {error && <p className="text-crimson text-sm mb-4">{error}</p>}

      <div className="grid md:grid-cols-3 gap-6">
        {/* Game toggle board */}
        <div className="md:col-span-2">
          <h2 className="text-lg font-bold mb-3" style={{ fontFamily: "var(--font-display)" }}>
            REMAINING GAMES ({scheduledGames.length})
          </h2>
          {scheduledGames.length === 0 && (
            <p className="text-steel-gray text-sm">No scheduled games found. Games will appear here during the season.</p>
          )}
          <div className="space-y-2">
            {scheduledGames.map((g) => {
              const isTeamGame = g.home_team_id === selectedTeamId || g.away_team_id === selectedTeamId;
              const homeSelected = locked[g.id] === g.home_team_id;
              const awaySelected = locked[g.id] === g.away_team_id;

              return (
                <div key={g.id} className={`flex items-center gap-2 rounded-lg border p-3 ${isTeamGame ? "border-crimson/30 bg-crimson/5" : "border-steel-gray/20"}`}>
                  <button
                    onClick={() => isPremium && toggleOutcome(g.id, g.home_team_id)}
                    disabled={!isPremium}
                    className={`flex-1 rounded px-3 py-2 text-sm text-center transition-all ${
                      homeSelected ? "bg-green-600/20 border border-green-600 text-white" : "border border-transparent text-steel-gray hover:text-white"
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {g.home_team_name || `#${g.home_team_id}`}
                    {homeSelected && " \u2713"}
                  </button>
                  <span className="text-xs text-steel-gray">vs</span>
                  <button
                    onClick={() => isPremium && toggleOutcome(g.id, g.away_team_id)}
                    disabled={!isPremium}
                    className={`flex-1 rounded px-3 py-2 text-sm text-center transition-all ${
                      awaySelected ? "bg-green-600/20 border border-green-600 text-white" : "border border-transparent text-steel-gray hover:text-white"
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {g.away_team_name || `#${g.away_team_id}`}
                    {awaySelected && " \u2713"}
                  </button>
                  {!isPremium && (
                    <span className="text-steel-gray text-xs">\ud83d\udd12</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Results panel */}
        <div>
          <h2 className="text-lg font-bold mb-3" style={{ fontFamily: "var(--font-display)" }}>
            PROJECTIONS
          </h2>
          {result ? (
            <div className="rounded-lg border border-steel-gray/30 p-4 space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold" style={{ fontFamily: "var(--font-display)" }}>
                  {result.projected_rating.toFixed(2)}
                </div>
                <div className="text-sm text-steel-gray">Projected Rating</div>
              </div>
              <div className="grid grid-cols-2 gap-3 text-center">
                <div>
                  <div className="text-xl font-bold">#{Math.round(result.projected_rank)}</div>
                  <div className="text-xs text-steel-gray">Projected Rank</div>
                </div>
                <div>
                  <div className="text-xl font-bold">{result.projected_wins.toFixed(1)}-{result.projected_losses.toFixed(1)}</div>
                  <div className="text-xs text-steel-gray">Record</div>
                </div>
              </div>
              <StatBar label="Playoff Probability" value={result.playoff_probability} max={100} suffix="%" />
              <StatBar label="Championship" value={result.championship_probability} max={100} suffix="%" color="bg-yellow-600" />

              {/* Best/Worst comparison */}
              {bestCase && worstCase && (
                <div className="border-t border-steel-gray/30 pt-3 mt-3">
                  <div className="text-xs text-steel-gray mb-2">RANGE</div>
                  <div className="flex justify-between text-sm">
                    <span className="text-green-500">Best: #{Math.round(bestCase.projected_rank)}</span>
                    <span className="text-red-500">Worst: #{Math.round(worstCase.projected_rank)}</span>
                  </div>
                  <div className="flex justify-between text-sm mt-1">
                    <span className="text-green-500">{bestCase.playoff_probability.toFixed(0)}% playoff</span>
                    <span className="text-red-500">{worstCase.playoff_probability.toFixed(0)}% playoff</span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="rounded-lg border border-steel-gray/30 p-6 text-center">
              <p className="text-steel-gray text-sm">
                {isPremium ? "Toggle game outcomes and click Calculate to see projections." : "Upgrade to Premium to use the Scenario Builder."}
              </p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
