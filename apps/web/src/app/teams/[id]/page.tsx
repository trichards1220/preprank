"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  fetchTeam, fetchTeamRatings, fetchTeamProjections,
  fetchGames, fetchFavorites, addFavorite, removeFavorite,
  fetchTeamHype,
  Team, PowerRating, TeamProjection, Game, HypeScore as HypeScoreType,
} from "@/lib/api";
import ShareButton from "@/components/ShareButton";
import HypeBadge from "@/components/HypeBadge";
import { useAuth } from "@/lib/auth";
import PowerRatingBadge from "@/components/PowerRatingBadge";
import StatBar from "@/components/StatBar";
import GameCard from "@/components/GameCard";

export default function TeamDetailPage() {
  const params = useParams();
  const teamId = Number(params.id);
  const { user, isPremium } = useAuth();

  const [team, setTeam] = useState<Team | null>(null);
  const [ratings, setRatings] = useState<PowerRating[]>([]);
  const [projection, setProjection] = useState<TeamProjection | null>(null);
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hype, setHype] = useState<HypeScoreType | null>(null);
  const [isFavorite, setIsFavorite] = useState(false);
  const [favoriteId, setFavoriteId] = useState<number | null>(null);

  useEffect(() => {
    if (!teamId) return;
    setLoading(true);
    Promise.all([
      fetchTeam(teamId),
      fetchTeamRatings(teamId, 2025),
      fetchTeamProjections(teamId),
      fetchGames({ season_year: 2025, sport: "Football", team_id: teamId }).catch(() => []),
      fetchTeamHype(teamId),
    ])
      .then(([t, r, p, g, h]) => {
        setTeam(t);
        setRatings(r);
        setProjection(p);
        setGames(g);
        setHype(h);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));

    if (user) {
      fetchFavorites().then((favs) => {
        const fav = favs.find(f => f.entity_type === "team" && f.entity_id === teamId);
        if (fav) { setIsFavorite(true); setFavoriteId(fav.id); }
      }).catch(() => {});
    }
  }, [teamId, user]);

  const toggleFavorite = async () => {
    if (!user) return;
    if (isFavorite && favoriteId) {
      await removeFavorite(favoriteId);
      setIsFavorite(false);
      setFavoriteId(null);
    } else {
      const fav = await addFavorite("team", teamId);
      setIsFavorite(true);
      setFavoriteId(fav.id);
    }
  };

  if (loading) return <main className="mx-auto max-w-5xl px-4 py-8"><p className="text-steel-gray">Loading...</p></main>;
  if (error || !team) return <main className="mx-auto max-w-5xl px-4 py-8"><p className="text-crimson">Error: {error || "Team not found"}</p></main>;

  const latestRating = ratings.length > 0 ? ratings[ratings.length - 1] : null;

  return (
    <main className="mx-auto max-w-5xl px-4 py-8">
      {/* Header */}
      <div className="flex items-start gap-6 mb-8">
        {latestRating && (
          <PowerRatingBadge rating={latestRating.power_rating} size="lg" />
        )}
        <div className="flex-1">
          <div className="flex items-center gap-4">
            <h1
              className="text-4xl font-bold tracking-tight"
              style={{ fontFamily: "var(--font-display)" }}
            >
              {team.school_name}
            </h1>
            {user && (
              <button
                onClick={toggleFavorite}
                className={`rounded px-3 py-1.5 text-sm font-medium transition-colors border ${
                  isFavorite
                    ? "border-crimson text-crimson hover:bg-crimson/10"
                    : "border-steel-gray text-steel-gray hover:border-crimson hover:text-crimson"
                }`}
              >
                {isFavorite ? "Following" : "Follow"}
              </button>
            )}
            <ShareButton
              title={`${team.school_name} | PrepRank`}
              text={`Check out ${team.school_name}'s power rating on PrepRank`}
              url={`${typeof window !== "undefined" ? window.location.origin : ""}/teams/${teamId}`}
            />
          </div>
          <div className="flex gap-3 mt-2 text-steel-gray">
            <span>Division {team.division}</span>
            <span>&middot;</span>
            <span>{team.sport_name}</span>
            <span>&middot;</span>
            <span>{team.season_year}</span>
          </div>
          {latestRating && (
            <div className="mt-2 text-sm text-steel-gray">
              Ranked #{latestRating.rank_in_division} in Division {team.division}
              {" · "}SoS: {latestRating.strength_factor?.toFixed(2) ?? "N/A"}
            </div>
          )}
          {hype && (
            <div className="mt-2">
              <HypeBadge score={hype.hype_score} label={hype.hype_label} />
            </div>
          )}
        </div>
      </div>

      {/* Projections — premium users see full data */}
      {projection && isPremium && (
        <section className="mb-8 rounded-lg border border-steel-gray/30 p-6">
          <h2
            className="text-xl font-bold mb-4"
            style={{ fontFamily: "var(--font-display)" }}
          >
            PROJECTIONS
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold">{projection.projected_rating_mean.toFixed(2)}</div>
              <div className="text-sm text-steel-gray">Projected Rating</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{projection.projected_wins_mean.toFixed(1)}-{projection.projected_losses_mean.toFixed(1)}</div>
              <div className="text-sm text-steel-gray">Projected Record</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-crimson">{projection.playoff_probability.toFixed(1)}%</div>
              <div className="text-sm text-steel-gray">Playoff Probability</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{projection.championship_probability.toFixed(1)}%</div>
              <div className="text-sm text-steel-gray">Championship</div>
            </div>
          </div>
          <div className="space-y-2">
            <StatBar label="Playoff Probability" value={projection.playoff_probability} max={100} suffix="%" />
            <StatBar label="Rating Range" value={projection.projected_rating_p90 - projection.projected_rating_p10} max={10} suffix=" pts spread" color="bg-blue-600" />
          </div>
        </section>
      )}

      {/* Schedule */}
      <section className="mb-8">
        <h2
          className="text-xl font-bold mb-4"
          style={{ fontFamily: "var(--font-display)" }}
        >
          SCHEDULE
        </h2>
        {games.length === 0 ? (
          <p className="text-steel-gray">No games scheduled yet for this season.</p>
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {games.map((g) => (
              <GameCard key={g.id} game={g} />
            ))}
          </div>
        )}
      </section>

      {/* Small premium teaser — below everything else, not prominent */}
      {projection && !isPremium && (
        <div className="mt-4 flex items-center gap-3 text-sm text-steel-gray">
          <span>Want projections and playoff probabilities?</span>
          <a href="/pricing" className="text-crimson hover:underline">
            Learn about Premium
          </a>
        </div>
      )}
    </main>
  );
}
