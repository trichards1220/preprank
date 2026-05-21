import type { Metadata } from "next";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

type Props = {
  params: Promise<{ id: string }>;
  children: React.ReactNode;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  try {
    const res = await fetch(`${API_BASE}/api/v1/teams/${id}`, { cache: "no-store" });
    if (!res.ok) return { title: "Team | PrepRank" };
    const team = await res.json();
    return {
      title: `${team.school_name} | PrepRank`,
      description: `${team.school_name} power ratings, schedule, and predictions`,
      openGraph: {
        title: `${team.school_name} | PrepRank`,
        description: `Division ${team.division} \u00B7 ${team.sport_name}`,
        images: [`${API_BASE}/api/v1/share/team/${id}/image`],
        siteName: "PrepRank",
        type: "website",
      },
      twitter: {
        card: "summary_large_image",
        title: `${team.school_name} | PrepRank`,
        images: [`${API_BASE}/api/v1/share/team/${id}/image`],
      },
    };
  } catch {
    return { title: "Team | PrepRank" };
  }
}

export default function TeamLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
