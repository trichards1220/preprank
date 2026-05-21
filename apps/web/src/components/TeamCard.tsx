import Link from "next/link";
import PowerRatingBadge from "./PowerRatingBadge";

interface TeamCardProps {
  teamId: number;
  schoolName: string;
  record?: string;
  rating?: number;
  rank?: number;
  division?: string;
  classification?: string;
}

export default function TeamCard({
  teamId,
  schoolName,
  record,
  rating,
  rank,
  division,
  classification,
}: TeamCardProps) {
  return (
    <Link
      href={`/teams/${teamId}`}
      className="flex items-center gap-4 rounded-lg border border-steel-gray/30 bg-charcoal p-4 transition-colors hover:border-crimson/50"
    >
      {rating !== undefined && <PowerRatingBadge rating={rating} size="sm" />}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          {rank !== undefined && (
            <span className="text-crimson font-bold text-sm">#{rank}</span>
          )}
          <span className="font-semibold truncate">{schoolName}</span>
        </div>
        <div className="text-steel-gray text-sm flex gap-2">
          {division && <span>Div {division}</span>}
          {classification && <span>{classification}</span>}
          {record && <span>{record}</span>}
        </div>
      </div>
    </Link>
  );
}
