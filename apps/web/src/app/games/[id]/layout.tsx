import type { Metadata } from "next";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

type Props = {
  params: Promise<{ id: string }>;
  children: React.ReactNode;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  try {
    const res = await fetch(`${API_BASE}/api/v1/games/${id}`, { cache: "no-store" });
    if (!res.ok) return { title: "Game | PrepRank" };
    const game = await res.json();
    const title = `${game.home_team_name || "Home"} vs ${game.away_team_name || "Away"} | PrepRank`;
    return {
      title,
      openGraph: {
        title,
        images: [`${API_BASE}/api/v1/share/game/${id}/image`],
        siteName: "PrepRank",
        type: "website",
      },
      twitter: { card: "summary_large_image", title, images: [`${API_BASE}/api/v1/share/game/${id}/image`] },
    };
  } catch {
    return { title: "Game | PrepRank" };
  }
}

export default function GameLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
