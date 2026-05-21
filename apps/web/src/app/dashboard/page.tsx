"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { fetchFavorites, fetchTeamRatings, Favorite, PowerRating } from "@/lib/api";
import TeamCard from "@/components/TeamCard";
import Link from "next/link";

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [ratings, setRatings] = useState<Record<number, PowerRating | null>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
      return;
    }
    if (!user) return;

    fetchFavorites()
      .then(async (favs) => {
        setFavorites(favs);
        const ratingMap: Record<number, PowerRating | null> = {};
        for (const f of favs) {
          if (f.entity_type === "team") {
            try {
              const r = await fetchTeamRatings(f.entity_id, 2025);
              ratingMap[f.entity_id] = r.length > 0 ? r[r.length - 1] : null;
            } catch {
              ratingMap[f.entity_id] = null;
            }
          }
        }
        setRatings(ratingMap);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user, authLoading, router]);

  if (authLoading || !user) return <main className="mx-auto max-w-5xl px-4 py-8"><p className="text-steel-gray">Loading...</p></main>;

  return (
    <main className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>
        WELCOME BACK, {(user.first_name || "").toUpperCase()}
      </h1>
      <p className="text-steel-gray mb-8">Your personalized PrepRank dashboard</p>

      <section className="mb-8">
        <h2 className="text-xl font-bold mb-4" style={{ fontFamily: "var(--font-display)" }}>MY TEAMS</h2>
        {loading && <p className="text-steel-gray">Loading...</p>}
        {!loading && favorites.length === 0 && (
          <div className="rounded-lg border border-steel-gray/30 p-8 text-center">
            <p className="text-steel-gray mb-4">You haven&apos;t followed any teams yet.</p>
            <Link href="/rankings/football" className="inline-block rounded bg-crimson px-4 py-2 text-sm font-semibold text-white hover:bg-crimson/80">
              Browse Rankings
            </Link>
          </div>
        )}
        {!loading && favorites.length > 0 && (
          <div className="grid gap-3 md:grid-cols-2">
            {favorites.filter(f => f.entity_type === "team").map((f) => {
              const r = ratings[f.entity_id];
              return (
                <TeamCard
                  key={f.id}
                  teamId={f.entity_id}
                  schoolName={f.school_name || `Team #${f.entity_id}`}
                  rating={r?.power_rating}
                  rank={r?.rank_in_division ?? undefined}
                  division={f.division ?? undefined}
                  classification={f.classification ?? undefined}
                />
              );
            })}
          </div>
        )}
      </section>
    </main>
  );
}
