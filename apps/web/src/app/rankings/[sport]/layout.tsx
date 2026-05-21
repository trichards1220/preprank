import type { Metadata } from "next";
import { sportNameFromSlug } from "@/lib/sports";

type Props = {
  params: Promise<{ sport: string }>;
  children: React.ReactNode;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { sport } = await params;
  const name = sportNameFromSlug(sport) || sport;
  return {
    title: `${name} Rankings | PrepRank`,
    description: `LHSAA ${name} power rankings for all divisions`,
    openGraph: {
      title: `${name} Rankings | PrepRank`,
      description: `LHSAA ${name} power rankings for all divisions`,
      siteName: "PrepRank",
      type: "website",
    },
    twitter: { card: "summary_large_image", title: `${name} Rankings | PrepRank` },
  };
}

export default function RankingsLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
