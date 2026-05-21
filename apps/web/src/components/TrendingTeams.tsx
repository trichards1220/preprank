"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchTrendingTeams, HypeScore } from "@/lib/api";
import HypeBadge from "./HypeBadge";

export default function TrendingTeams() {
  const [teams, setTeams] = useState<HypeScore[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrendingTeams(2025)
      .then(setTeams)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading || teams.length === 0) return null;

  return (
    <section className="mx-auto max-w-5xl px-4 pb-16">
      <h2 className="text-2xl font-bold mb-6" style={{ fontFamily: "var(--font-display)" }}>
        TRENDING TEAMS
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {teams.slice(0, 6).map((t) => (
          <Link
            key={t.team_id}
            href={`/teams/${t.team_id}`}
            className="flex items-center justify-between rounded-lg border border-steel-gray/30 p-4 hover:border-crimson/50 transition-colors"
          >
            <div>
              <div className="font-semibold">{t.school_name}</div>
              <div className="text-sm text-steel-gray">
                Div {t.division}
                {t.power_rating && ` \u00B7 ${t.power_rating.toFixed(2)} rating`}
              </div>
            </div>
            <HypeBadge score={t.hype_score} label={t.hype_label} size="sm" />
          </Link>
        ))}
      </div>
    </section>
  );
}
