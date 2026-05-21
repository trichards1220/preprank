"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { fetchContest, fetchContestGames, fetchMyPicks, submitPicks, PickemContest, PickemGame } from "@/lib/api";
import PickemCard from "@/components/PickemCard";
import Link from "next/link";

export default function ContestDetailPage() {
  const params = useParams();
  const contestId = Number(params.contestId);
  const { user } = useAuth();

  const [contest, setContest] = useState<PickemContest | null>(null);
  const [games, setGames] = useState<PickemGame[]>([]);
  const [myPicks, setMyPicks] = useState<Record<number, number>>({});
  const [results, setResults] = useState<Record<number, { is_correct: boolean | null }>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!contestId) return;
    Promise.all([fetchContest(contestId), fetchContestGames(contestId)])
      .then(([c, g]) => { setContest(c); setGames(g); })
      .catch(() => {})
      .finally(() => setLoading(false));

    if (user) {
      fetchMyPicks(contestId).then((entries) => {
        const picks: Record<number, number> = {};
        const res: Record<number, { is_correct: boolean | null }> = {};
        for (const e of entries) {
          picks[e.game_id] = e.picked_team_id;
          res[e.game_id] = { is_correct: e.is_correct };
        }
        setMyPicks(picks);
        setResults(res);
      }).catch(() => {});
    }
  }, [contestId, user]);

  const handlePick = (gameId: number, teamId: number) => {
    setMyPicks((prev) => ({ ...prev, [gameId]: teamId }));
  };

  const handleSubmit = async () => {
    if (!user) { setMessage("Log in to save your picks"); return; }
    const picks = Object.entries(myPicks).map(([gid, tid]) => ({ game_id: Number(gid), picked_team_id: tid }));
    if (picks.length === 0) { setMessage("Make at least one pick"); return; }
    setSubmitting(true); setMessage("");
    try {
      await submitPicks(contestId, picks);
      setMessage("Picks saved!");
    } catch (e: unknown) {
      setMessage(e instanceof Error ? e.message : "Failed to save picks");
    } finally { setSubmitting(false); }
  };

  if (loading) return <main className="mx-auto max-w-5xl px-4 py-8"><p className="text-steel-gray">Loading...</p></main>;
  if (!contest) return <main className="mx-auto max-w-5xl px-4 py-8"><p className="text-crimson">Contest not found</p></main>;

  const isOpen = contest.status === "open";
  const isScored = contest.status === "scored" || contest.status === "closed";
  const picksCount = Object.keys(myPicks).length;

  return (
    <main className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-3xl font-bold mb-1" style={{ fontFamily: "var(--font-display)" }}>{contest.title}</h1>
      <div className="text-steel-gray text-sm mb-6">
        {contest.game_count} games &middot; {isOpen ? "Open for picks" : isScored ? "Scored" : contest.status}
        {isOpen && picksCount > 0 && ` \u00B7 ${picksCount} picks made`}
      </div>

      <div className="grid gap-4 md:grid-cols-2 mb-6">
        {games.map((g) => (
          <PickemCard key={g.game_id} game={g} pickedTeamId={myPicks[g.game_id] ?? null}
            onPick={handlePick} locked={!isOpen} result={results[g.game_id]} />
        ))}
      </div>

      {isOpen && (
        <div className="flex items-center gap-4">
          {user ? (
            <button onClick={handleSubmit} disabled={submitting || picksCount === 0}
              className="rounded bg-crimson px-6 py-3 font-semibold text-white hover:bg-crimson/80 transition-colors disabled:opacity-50">
              {submitting ? "Saving..." : `Submit ${picksCount} Pick${picksCount !== 1 ? "s" : ""}`}
            </button>
          ) : (
            <Link href="/login" className="rounded bg-crimson px-6 py-3 font-semibold text-white hover:bg-crimson/80 transition-colors">
              Log In to Save Picks
            </Link>
          )}
          {message && <span className={`text-sm ${message.includes("saved") ? "text-green-500" : "text-crimson"}`}>{message}</span>}
        </div>
      )}

      {isScored && (
        <Link href="/pickem/leaderboard" className="text-crimson hover:underline text-sm font-semibold">View Leaderboard &rarr;</Link>
      )}
    </main>
  );
}
