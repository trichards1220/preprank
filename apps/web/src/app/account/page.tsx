"use client";

import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";

export default function AccountPage() {
  const { user, loading, isPremium, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  if (loading || !user) return <main className="mx-auto max-w-3xl px-4 py-8"><p className="text-steel-gray">Loading...</p></main>;

  const tierLabels: Record<string, string> = {
    free: "Free",
    premium_monthly: "Premium Monthly ($4.99/mo)",
    season_pass: "Season Pass ($14.99/season)",
    annual: "Annual ($29.99/yr)",
  };

  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-3xl font-bold mb-8" style={{ fontFamily: "var(--font-display)" }}>MY ACCOUNT</h1>

      <section className="rounded-lg border border-steel-gray/30 p-6 mb-6">
        <h2 className="text-lg font-bold mb-4" style={{ fontFamily: "var(--font-display)" }}>PROFILE</h2>
        <div className="space-y-2 text-sm">
          <div><span className="text-steel-gray">Name:</span> {user.first_name} {user.last_name}</div>
          <div><span className="text-steel-gray">Email:</span> {user.email}</div>
        </div>
      </section>

      <section className="rounded-lg border border-steel-gray/30 p-6 mb-6">
        <h2 className="text-lg font-bold mb-4" style={{ fontFamily: "var(--font-display)" }}>SUBSCRIPTION</h2>
        <div className="flex items-center gap-4 mb-4">
          <span className={`inline-block rounded px-3 py-1 text-sm font-bold ${isPremium ? "bg-crimson text-white" : "bg-steel-gray/30 text-steel-gray"}`}>
            {tierLabels[user.subscription_tier] || user.subscription_tier}
          </span>
          {user.subscription_expires && (
            <span className="text-sm text-steel-gray">
              Expires: {new Date(user.subscription_expires).toLocaleDateString()}
            </span>
          )}
        </div>
        {!isPremium && (
          <Link href="/pricing" className="inline-block rounded bg-crimson px-4 py-2 text-sm font-semibold text-white hover:bg-crimson/80 transition-colors">
            Upgrade to Premium
          </Link>
        )}
      </section>

      <button onClick={() => { logout(); router.push("/"); }}
        className="rounded border border-steel-gray px-4 py-2 text-sm text-steel-gray hover:text-crimson hover:border-crimson transition-colors">
        Log Out
      </button>
    </main>
  );
}
