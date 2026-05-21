"use client";

import { useEffect, useState } from "react";
import { fetchIndividualLeaderboard, fetchSchoolLeaderboard, LeaderboardRow, SchoolLeaderboardRow } from "@/lib/api";
import LeaderboardTable from "@/components/LeaderboardTable";

export default function LeaderboardPage() {
  const [tab, setTab] = useState<"individual" | "school">("individual");
  const [individual, setIndividual] = useState<LeaderboardRow[]>([]);
  const [schools, setSchools] = useState<SchoolLeaderboardRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchIndividualLeaderboard({ season_year: 2025 }),
      fetchSchoolLeaderboard({ season_year: 2025 }),
    ]).then(([ind, sch]) => { setIndividual(ind); setSchools(sch); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-3xl font-bold mb-6" style={{ fontFamily: "var(--font-display)" }}>
        <span className="text-white">LEADER</span><span className="text-crimson">BOARD</span>
      </h1>
      <div className="flex gap-2 mb-6">
        <button onClick={() => setTab("individual")}
          className={`rounded px-4 py-2 text-sm font-semibold transition-colors ${tab === "individual" ? "bg-crimson text-white" : "bg-steel-gray/20 text-steel-gray hover:text-white"}`}>
          Individual
        </button>
        <button onClick={() => setTab("school")}
          className={`rounded px-4 py-2 text-sm font-semibold transition-colors ${tab === "school" ? "bg-crimson text-white" : "bg-steel-gray/20 text-steel-gray hover:text-white"}`}>
          School vs School
        </button>
      </div>
      {loading && <p className="text-steel-gray">Loading...</p>}
      {!loading && tab === "individual" && <LeaderboardTable type="individual" rows={individual} />}
      {!loading && tab === "school" && <LeaderboardTable type="school" rows={schools} />}
    </main>
  );
}
