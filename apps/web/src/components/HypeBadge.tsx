interface HypeBadgeProps {
  score: number;
  label: string;
  size?: "sm" | "md";
}

const HYPE_STYLES: Record<string, { icon: string; color: string }> = {
  "ON FIRE": { icon: "\u{1F525}", color: "text-orange-500" },
  "SURGING": { icon: "\u{1F4C8}", color: "text-green-500" },
  "STEADY": { icon: "\u27A1\uFE0F", color: "text-blue-400" },
  "COOLING": { icon: "\u{1F4C9}", color: "text-yellow-500" },
  "ICE COLD": { icon: "\u2744\uFE0F", color: "text-blue-300" },
};

export default function HypeBadge({ score, label, size = "md" }: HypeBadgeProps) {
  const style = HYPE_STYLES[label] || HYPE_STYLES["STEADY"];

  if (size === "sm") {
    return (
      <span className={`inline-flex items-center gap-1 text-xs ${style.color}`}>
        <span>{style.icon}</span>
        <span className="font-bold">{Math.round(score)}</span>
      </span>
    );
  }

  return (
    <div className={`inline-flex items-center gap-2 rounded-full border border-steel-gray/30 px-3 py-1 ${style.color}`}>
      <span className="text-lg">{style.icon}</span>
      <div>
        <div className="text-xs font-bold">{label}</div>
        <div className="text-xs">{Math.round(score)} hype</div>
      </div>
    </div>
  );
}
