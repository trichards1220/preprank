"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(email, password, firstName, lastName);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-[80vh] items-center justify-center px-4">
      <div className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-center mb-8" style={{ fontFamily: "var(--font-display)" }}>
          CREATE ACCOUNT
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <p className="text-crimson text-sm text-center">{error}</p>}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-steel-gray mb-1">First Name</label>
              <input type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)}
                className="w-full rounded border border-steel-gray bg-charcoal px-4 py-3 text-white focus:border-crimson focus:outline-none" required />
            </div>
            <div>
              <label className="block text-sm text-steel-gray mb-1">Last Name</label>
              <input type="text" value={lastName} onChange={(e) => setLastName(e.target.value)}
                className="w-full rounded border border-steel-gray bg-charcoal px-4 py-3 text-white focus:border-crimson focus:outline-none" required />
            </div>
          </div>
          <div>
            <label className="block text-sm text-steel-gray mb-1">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded border border-steel-gray bg-charcoal px-4 py-3 text-white focus:border-crimson focus:outline-none" required />
          </div>
          <div>
            <label className="block text-sm text-steel-gray mb-1">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded border border-steel-gray bg-charcoal px-4 py-3 text-white focus:border-crimson focus:outline-none" required minLength={8} />
            <p className="text-xs text-steel-gray mt-1">Minimum 8 characters</p>
          </div>
          <button type="submit" disabled={loading}
            className="w-full rounded bg-crimson py-3 font-semibold text-white hover:bg-crimson/80 transition-colors disabled:opacity-50">
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-steel-gray">
          Already have an account?{" "}
          <Link href="/login" className="text-crimson hover:underline">Log in</Link>
        </p>
      </div>
    </main>
  );
}
