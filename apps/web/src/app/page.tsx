import Link from "next/link";
import TrendingTeams from "@/components/TrendingTeams";

const FEATURED_SPORTS = [
  { name: "Football", slug: "football", season: "fall" },
  { name: "Boys Basketball", slug: "boys-basketball", season: "winter" },
  { name: "Girls Basketball", slug: "girls-basketball", season: "winter" },
  { name: "Baseball", slug: "baseball", season: "spring" },
  { name: "Softball", slug: "softball", season: "spring" },
  { name: "Boys Soccer", slug: "boys-soccer", season: "spring" },
  { name: "Girls Soccer", slug: "girls-soccer", season: "spring" },
  { name: "Volleyball", slug: "volleyball", season: "fall" },
];

export default function Home() {
  return (
    <main>
      {/* Hero */}
      <section className="flex flex-col items-center justify-center py-24 px-4 text-center">
        <h1
          className="text-7xl md:text-8xl font-bold tracking-tight mb-4"
          style={{ fontFamily: "var(--font-display)" }}
        >
          <span className="text-white">PREP</span>
          <span className="text-crimson">/</span>
          <span className="text-white">RANK</span>
        </h1>
        <p className="text-xl text-steel-gray max-w-lg mb-8">
          Know Where You Stand. Before the Game is Played.
        </p>
        <div className="flex gap-4 flex-wrap justify-center">
          <Link
            href="/rankings/football"
            className="rounded bg-crimson px-6 py-3 font-semibold text-white transition-colors hover:bg-crimson/80"
            style={{ fontFamily: "var(--font-display)" }}
          >
            VIEW RANKINGS
          </Link>
          <Link
            href="/scores"
            className="rounded border border-steel-gray px-6 py-3 font-semibold text-white transition-colors hover:border-crimson"
            style={{ fontFamily: "var(--font-display)" }}
          >
            SCORES
          </Link>
        </div>
      </section>

      {/* Sports Grid */}
      <section className="mx-auto max-w-5xl px-4 pb-16">
        <h2
          className="text-2xl font-bold mb-6"
          style={{ fontFamily: "var(--font-display)" }}
        >
          POWER RANKINGS BY SPORT
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {FEATURED_SPORTS.map((sport) => (
            <Link
              key={sport.slug}
              href={`/rankings/${sport.slug}`}
              className="group rounded-lg border border-steel-gray/30 bg-charcoal p-6 text-center transition-all hover:border-crimson/50 hover:bg-crimson/5"
            >
              <div
                className="text-lg font-bold group-hover:text-crimson transition-colors"
                style={{ fontFamily: "var(--font-display)" }}
              >
                {sport.name}
              </div>
              <div className="text-sm text-steel-gray mt-1 capitalize">
                {sport.season} season
              </div>
            </Link>
          ))}
        </div>
      </section>

      <TrendingTeams />
    </main>
  );
}
