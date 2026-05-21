"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchContests, PickemContest } from "@/lib/api";

export default function PickemHubPage() {
  const [contests, setContests] = useState<PickemContest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchContests({ season_year: 2025 })
      .then(setContests)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const open = contests.filter((c) => c.status === "open");
  const scored = contests.filter((c) => c.status === "scored" || c.status === "closed");

  return (
    <main className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-4xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>
        <span className="text-white">PICK</span>
        <span className="text-crimson">&apos;EM</span>
      </h1>
      <p className="text-steel-gray mb-8">Predict game outcomes. Compete against your school. Earn badges.</p>

      {loading && <p className="text-steel-gray">Loading contests...</p>}

      {!loading && open.length > 0 && (
        <section className="mb-8">
          <h2 className="text-xl font-bold mb-4" style={{ fontFamily: "var(--font-display)" }}>OPEN CONTESTS</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {open.map((c) => (
              <Link key={c.id} href={`/pickem/${c.id}`}
                className="rounded-lg border border-crimson/50 bg-crimson/5 p-6 hover:bg-crimson/10 transition-colors">
                <div className="font-bold text-lg" style={{ fontFamily: "var(--font-display)" }}>{c.title}</div>
                <div className="text-sm text-steel-gray mt-1">{c.game_count} games &middot; Week {c.week_number}</div>
                <div className="mt-3 text-sm text-crimson font-semibold">Make Your Picks &rarr;</div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {!loading && scored.length > 0 && (
        <section className="mb-8">
          <h2 className="text-xl font-bold mb-4" style={{ fontFamily: "var(--font-display)" }}>RESULTS</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {scored.map((c) => (
              <Link key={c.id} href={`/pickem/${c.id}`}
                className="rounded-lg border border-steel-gray/30 p-6 hover:border-steel-gray transition-colors">
                <div className="font-bold" style={{ fontFamily: "var(--font-display)" }}>{c.title}</div>
                <div className="text-sm text-steel-gray mt-1">{c.game_count} games &middot; Scored</div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {!loading && contests.length === 0 && (
        <div className="rounded-lg border border-steel-gray/30 p-8 text-center">
          <p className="text-lg text-steel-gray mb-2">No contests yet this season</p>
          <p className="text-sm text-steel-gray/70">Pick&apos;em contests will open each week once game schedules are posted.</p>
        </div>
      )}

      <div className="mt-8">
        <Link href="/pickem/leaderboard" className="text-crimson hover:underline font-semibold text-sm">View Leaderboards &rarr;</Link>
      </div>
    </main>
  );
}
