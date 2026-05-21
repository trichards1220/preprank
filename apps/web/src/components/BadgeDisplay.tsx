import type { Badge } from "@/lib/api";

const BADGE_ICONS: Record<string, string> = {
  perfect_week: "\uD83C\uDFC6", sharp_eye: "\uD83C\uDFAF", upset_caller: "\uD83D\uDD2E", streak_3: "\uD83D\uDD25",
};

export default function BadgeDisplay({ badges }: { badges: Badge[] }) {
  if (badges.length === 0) return <p className="text-sm text-steel-gray">No badges earned yet. Make picks to start earning!</p>;
  return (
    <div className="flex flex-wrap gap-3">
      {badges.map((b) => (
        <div key={b.id} className="rounded-lg border border-steel-gray/30 p-3 text-center min-w-[100px]">
          <div className="text-2xl mb-1">{BADGE_ICONS[b.badge_type] || "\uD83C\uDFC5"}</div>
          <div className="text-xs font-bold">{b.badge_name}</div>
          {b.description && <div className="text-xs text-steel-gray mt-1">{b.description}</div>}
        </div>
      ))}
    </div>
  );
}
