interface StatBarProps {
  label: string;
  value: number;
  max: number;
  suffix?: string;
  color?: string;
}

export default function StatBar({
  label,
  value,
  max,
  suffix = "",
  color = "bg-crimson",
}: StatBarProps) {
  const pct = max > 0 ? Math.min((value / max) * 100, 100) : 0;

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-steel-gray">{label}</span>
        <span className="font-mono">
          {value.toFixed(1)}{suffix}
        </span>
      </div>
      <div className="h-2 w-full rounded-full bg-steel-gray/20">
        <div
          className={`h-2 rounded-full ${color} transition-all`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
