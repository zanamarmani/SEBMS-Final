"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { homeFor, useAuth } from "@/lib/auth";
import { CenteredSpinner } from "@/components/ui";

export default function LandingPage() {
  const { user, status } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (status === "ready" && user && (user.role || user.is_superuser)) {
      router.replace(homeFor(user));
    }
  }, [status, user, router]);

  if (status === "loading") return <CenteredSpinner />;

  if (user) {
    return (
      <main className="flex min-h-screen items-center justify-center p-6">
        <div className="w-full max-w-md rounded-lg border border-gray-200 bg-white p-6 text-center shadow-sm">
          <h1 className="text-lg font-semibold text-gray-900">
            Signed in as {user.email}
          </h1>
          {user.role || user.is_superuser ? (
            <p className="mt-2 text-sm text-gray-500">
              Redirecting to your dashboard…
            </p>
          ) : (
            <p className="mt-3 text-sm text-amber-700">
              This account has no role assigned. Ask the administrator to
              assign one.
            </p>
          )}
          <Link
            href="/"
            className="mt-4 inline-block text-sm font-medium text-blue-600 hover:underline"
          >
            Continue
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 p-6">
      <div className="text-center">
        <span className="rounded-md bg-blue-600 px-3 py-1.5 text-lg font-bold text-white">
          SEBMS
        </span>
        <h1 className="mt-4 text-2xl font-semibold text-gray-900">
          Smart Electricity Billing Management System
        </h1>
        <p className="mx-auto mt-2 max-w-xl text-sm text-gray-500">
          Headless API + role-based dashboards for SDOs, office staff, meter
          readers and consumers — tariffs, meter readings, bill generation,
          approvals and online payments.
        </p>
      </div>
      <div className="flex gap-3">
        <Link
          href="/login"
          className="rounded-md bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
        >
          Login
        </Link>
        <Link
          href="/register"
          className="rounded-md border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Consumer registration
        </Link>
      </div>
      <div className="grid max-w-3xl gap-3 text-left sm:grid-cols-2 md:grid-cols-4">
        {[
          ["SDO", "Tariffs, approvals, users, stats"],
          ["Office", "Meters, readings, bills, payments"],
          ["Meter reader", "Capture readings with photos"],
          ["Consumer", "Bills & instant mock payments"],
        ].map(([title, desc]) => (
          <div
            key={title}
            className="rounded-lg border border-gray-200 bg-white p-3"
          >
            <p className="text-sm font-semibold text-gray-900">{title}</p>
            <p className="mt-1 text-xs text-gray-500">{desc}</p>
          </div>
        ))}
      </div>
    </main>
  );
}
