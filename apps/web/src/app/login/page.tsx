"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-[80vh] items-center justify-center px-4">
      <div className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-center mb-8" style={{ fontFamily: "var(--font-display)" }}>
          LOG IN
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <p className="text-crimson text-sm text-center">{error}</p>}
          <div>
            <label className="block text-sm text-steel-gray mb-1">Email</label>
            <input
              type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded border border-steel-gray bg-charcoal px-4 py-3 text-white focus:border-crimson focus:outline-none"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-steel-gray mb-1">Password</label>
            <input
              type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded border border-steel-gray bg-charcoal px-4 py-3 text-white focus:border-crimson focus:outline-none"
              required
            />
          </div>
          <button
            type="submit" disabled={loading}
            className="w-full rounded bg-crimson py-3 font-semibold text-white hover:bg-crimson/80 transition-colors disabled:opacity-50"
          >
            {loading ? "Logging in..." : "Log In"}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-steel-gray">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-crimson hover:underline">Sign up</Link>
        </p>
      </div>
    </main>
  );
}
