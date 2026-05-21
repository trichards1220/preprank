import Link from "next/link";

interface PremiumLockProps {
  children: React.ReactNode;
  locked: boolean;
}

export default function PremiumLock({ children, locked }: PremiumLockProps) {
  if (!locked) return <>{children}</>;

  return (
    <div className="relative">
      <div className="blur-sm pointer-events-none select-none">{children}</div>
      <div className="absolute inset-0 flex items-center justify-center bg-charcoal/60 rounded-lg">
        <div className="text-center p-6">
          <div className="text-2xl mb-2">&#128274;</div>
          <p className="font-bold mb-1" style={{ fontFamily: "var(--font-display)" }}>PREMIUM FEATURE</p>
          <p className="text-sm text-steel-gray mb-4">
            Upgrade to see projections, predictions, and playoff probabilities
          </p>
          <Link
            href="/pricing"
            className="inline-block rounded bg-crimson px-6 py-2 font-semibold text-white hover:bg-crimson/80 transition-colors"
          >
            Upgrade to Premium
          </Link>
        </div>
      </div>
    </div>
  );
}
