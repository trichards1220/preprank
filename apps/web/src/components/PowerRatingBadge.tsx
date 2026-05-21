interface PowerRatingBadgeProps {
  rating: number;
  size?: "sm" | "md" | "lg";
}

function getRatingColor(rating: number): string {
  if (rating >= 14) return "bg-crimson";
  if (rating >= 12) return "bg-orange-600";
  if (rating >= 10) return "bg-yellow-600";
  if (rating >= 8) return "bg-blue-600";
  return "bg-steel-gray";
}

export default function PowerRatingBadge({ rating, size = "md" }: PowerRatingBadgeProps) {
  const sizeClasses = {
    sm: "w-10 h-10 text-xs",
    md: "w-14 h-14 text-sm",
    lg: "w-20 h-20 text-lg",
  };

  return (
    <div
      className={`${sizeClasses[size]} ${getRatingColor(rating)} rounded-full flex items-center justify-center font-bold text-white`}
    >
      {rating.toFixed(1)}
    </div>
  );
}
