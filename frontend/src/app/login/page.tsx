"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import { CenteredSpinner, Button, Field, Input, Alert } from "@/components/ui";
import { homeFor, useAuth } from "@/lib/auth";

function LoginForm() {
  const { user, status, login } = useAuth();
  const router = useRouter();
  const search = useSearchParams();
  const next = search.get("next");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const destination = user ? next || homeFor(user) : "/login";

  useEffect(() => {
    if (status === "ready" && user) router.replace(destination);
  }, [status, user, destination, router]);

  if (status === "loading") return <CenteredSpinner />;

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const me = await login(email.trim(), password);
      router.replace(next || homeFor(me));
    } catch (err) {
      setError(
        err instanceof Error && err.message
          ? err.message
          : "Login failed.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-sm rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-5 text-center">
          <span className="rounded-md bg-blue-600 px-2 py-1 text-sm font-bold text-white">
            SEBMS
          </span>
          <h1 className="mt-3 text-lg font-semibold text-gray-900">
            Sign in
          </h1>
        </div>
        <form onSubmit={(e) => void submit(e)} className="space-y-4">
          {error && <Alert>{error}</Alert>}
          <Field label="Email" required>
            <Input
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </Field>
          <Field label="Password" required>
            <Input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </Field>
          <Button type="submit" loading={busy} className="w-full">
            Login
          </Button>
        </form>
        <p className="mt-4 text-center text-xs text-gray-500">
          New consumer?{" "}
          <Link
            href="/register"
            className="font-medium text-blue-600 hover:underline"
          >
            Register here
          </Link>
        </p>
      </div>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<CenteredSpinner />}>
      <LoginForm />
    </Suspense>
  );
}
