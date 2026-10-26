"use client";

import Link from "next/link";
import Icon from "@/components/Icon";
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
        err instanceof Error && err.message ? err.message : "Login failed.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <aside className="auth-story">
        <Link href="/" className="brand">
          <span className="brand-mark">
            <Icon name="bolt" size={24} />
          </span>
          <span>
            SEBMS<small>ENERGY MANAGEMENT</small>
          </span>
        </Link>
        <div>
          <p
            className="page-eyebrow"
            style={{ color: "#6bd7c4", marginBottom: 20 }}
          >
            Your connected workspace
          </p>
          <h2>
            Clarity for your team.
            <br />
            <em>Confidence in every bill.</em>
          </h2>
          <p>
            Manage your daily electricity operations with readings, billing and
            consumer information in one place.
          </p>
        </div>
        <div className="auth-story-footer">
          Smart Electricity Billing Management System
        </div>
      </aside>
      <div className="auth-form-side">
        <div className="auth-form">
          <Link href="/" className="brand auth-mobile-brand">
            <span className="brand-mark">
              <Icon name="bolt" />
            </span>
            <span>
              SEBMS<small>ENERGY MANAGEMENT</small>
            </span>
          </Link>
          <p className="page-eyebrow">Welcome back</p>
          <h1>Sign in to your workspace</h1>
          <p className="auth-intro">
            Enter your account details to continue to your dashboard.
          </p>
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
              Sign in to dashboard
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
          <Link href="/" className="auth-home">
            ← Back to home
          </Link>
        </div>
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
