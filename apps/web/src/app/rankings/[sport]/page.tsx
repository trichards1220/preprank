"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { fetchRankings, RankedTeam } from "@/lib/api";
import { sportNameFromSlug, FOOTBALL_WEEK_COUNT } from "@/lib/sports";
import RankingsTable from "@/components/RankingsTable";

const DIVISIONS = [
  { value: "", label: "All Divisions" },
  { value: "I", label: "Division I (5A)" },
  { value: "II", label: "Division II (4A)" },
  { value: "III", label: "Division III (3A)" },
  { value: "IV", label: "Division IV (2A)" },
  { value: "V", label: "Division V (1A)" },
];

export default function RankingsSportPage() {
  const params = useParams();
  const slug = params.sport as string;
  const sportName = sportNameFromSlug(slug);

  const [allRankings, setAllRankings] = useState<RankedTeam[]>([]);
  const [division, setDivision] = useState("");
  const [selectStatus, setSelectStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sportName) return;
    setLoading(true);
    setError(null);
    fetchRankings(sportName, 2025, FOOTBALL_WEEK_COUNT, division || undefined)
      .then(setAllRankings)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [sportName, division]);

  // Client-side filter for select status, then re-rank sequentially
  const rankings = (() => {
    let filtered = allRankings;
    if (selectStatus) {
      filtered = allRankings.filter((r) => r.select_status === selectStatus);
    }
    return filtered.map((r, i) => ({ ...r, rank: i + 1 }));
  })();

  if (!sportName) {
    return (
      <main className="mx-auto max-w-5xl px-4 py-8">
        <p className="text-crimson">Unknown sport: {slug}</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-5xl px-4 py-8">
      <h1
        className="mb-6 text-4xl font-bold tracking-tight"
        style={{ fontFamily: "var(--font-display)" }}
      >
        <span className="text-white">{sportName.toUpperCase()}</span>
        <span className="text-crimson"> RANKINGS</span>
      </h1>

      <div className="mb-6 flex items-center gap-4 flex-wrap">
        <select
          value={division}
          onChange={(e) => setDivision(e.target.value)}
          className="rounded border border-steel-gray bg-charcoal px-3 py-2 text-white focus:border-crimson focus:outline-none"
        >
          {DIVISIONS.map((d) => (
            <option key={d.value} value={d.value}>{d.label}</option>
          ))}
        </select>
        <select
          value={selectStatus}
          onChange={(e) => setSelectStatus(e.target.value)}
          className="rounded border border-steel-gray bg-charcoal px-3 py-2 text-white focus:border-crimson focus:outline-none"
        >
          <option value="">All Schools</option>
          <option value="Select">Select</option>
          <option value="Non-Select">Non-Select</option>
        </select>
        <span className="text-steel-gray text-sm">
          2025 Season &middot; Final
          {rankings.length > 0 && ` · ${rankings.length} teams`}
        </span>
      </div>

      {loading && <p className="text-steel-gray">Loading rankings...</p>}
      {error && <p className="text-crimson">Error: {error}</p>}
      {!loading && !error && <RankingsTable rankings={rankings} />}
    </main>
  );
}
