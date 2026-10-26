"use client";

import Link from "next/link";
import Icon from "@/components/Icon";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { homeFor, useAuth } from "@/lib/auth";
import { CenteredSpinner } from "@/components/ui";

export default function LandingPage() {
  const apkUrl = process.env.NEXT_PUBLIC_SCANNER_APK_URL;
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
              This account has no role assigned. Ask the administrator to assign
              one.
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
    <main className="public-page">
      <header className="public-nav">
        <Link href="/" className="brand">
          <span className="brand-mark">
            <Icon name="bolt" size={24} />
          </span>
          <span>
            SEBMS<small>ENERGY MANAGEMENT</small>
          </span>
        </Link>
        <nav className="public-nav-links" aria-label="Public navigation">
          <a href="#features">Platform</a>
          <a href="#scanner">Meter scanner</a>
          <Link href="/login" className="secondary-link">
            Sign in <Icon name="arrow" size={15} />
          </Link>
        </nav>
      </header>
      <section className="hero">
        <div>
          <p className="page-eyebrow">A smarter way to manage electricity</p>
          <h1>
            Less paperwork.
            <br />
            More clarity.
            <br />
            <em>Better energy.</em>
          </h1>
          <p className="hero-description">
            Bring your meter readings, consumers and electricity bills together.
            One connected workspace for your team and the people you serve.
          </p>
          <div className="hero-actions">
            <Link href="/login" className="primary-link">
              Open your dashboard <Icon name="arrow" size={17} />
            </Link>
            <Link href="/register" className="secondary-link">
              Register as a consumer
            </Link>
          </div>
          <p className="hero-note">
            <Icon name="shield" size={15} /> Dedicated access for every role in
            your team
          </p>
        </div>
        <div
          className="energy-art"
          role="img"
          aria-label="Illustration of a smart electricity meter"
        >
          <div className="meter-illustration">
            <div className="meter-brand">
              SEBMS <Icon name="bolt" size={16} />
            </div>
            <div className="meter-screen">
              00000<small>kWh</small>
            </div>
            <div className="meter-dial">
              <Icon name="bolt" size={27} />
            </div>
            <div className="meter-bottom">SMART ELECTRICITY METER</div>
          </div>
          <div className="art-chip first">
            <Icon name="check" /> Clear, accurate readings
          </div>
          <div className="art-chip second">
            <Icon name="bill" /> From readings to billing
          </div>
        </div>
      </section>
      <section className="section-container" id="features">
        <p className="page-eyebrow">One platform. Every role.</p>
        <h2 className="page-heading">Built around the way you work.</h2>
        <p className="page-description">
          The right tools for each person, from the field to the office.
        </p>
        <div className="feature-grid">
          {[
            [
              "dashboard",
              "SDO workspace",
              "Review consumer applications, manage tariffs and oversee your team.",
            ],
            [
              "bill",
              "Office operations",
              "Organize meters, import readings, generate bills and track payments.",
            ],
            [
              "meter",
              "Meter readers",
              "Capture meter readings and photos in the field with the Android scanner.",
            ],
            [
              "users",
              "Consumer portal",
              "Check your electricity bills, payment history and account details.",
            ],
          ].map(([icon, title, description]) => (
            <article className="feature-card" key={title}>
              <Icon name={icon} size={27} />
              <h3>{title}</h3>
              <p>{description}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="section-container" id="scanner">
        <div className="scanner-panel">
          <div>
            <p className="page-eyebrow">SEBMS for Android</p>
            <h2>
              Your fieldwork,
              <br />
              without the paperwork.
            </h2>
            <p>
              Capture a meter reading, verify the details and sync it with
              SEBMS. Download the Android meter scanner and sign in with your
              assigned reader account.
            </p>
          </div>
          <div className="scanner-download">
            {apkUrl ? (
              <a className="primary-link" href={apkUrl}>
                <Icon name="download" size={18} /> Download Android APK
              </a>
            ) : (
              <p>Android download coming soon</p>
            )}
            <p>
              For Android devices. Install the APK after downloading. Your SDO
              provides your reader account.
            </p>
          </div>
        </div>
      </section>
      <footer className="public-footer">
        <span>SEBMS · Smart Electricity Billing Management</span>
        <span>Connected readings. Clearer billing.</span>
      </footer>
    </main>
  );
}
