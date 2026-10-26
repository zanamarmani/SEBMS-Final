"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/lib/auth";
import Icon from "./Icon";
export interface NavLink {
  href: string;
  label: string;
}
const icons: Record<string, string> = {
  Dashboard: "dashboard",
  Home: "dashboard",
  Tariffs: "tariff",
  Consumers: "users",
  Users: "users",
  Meters: "meter",
  Readings: "meter",
  Bills: "bill",
  Payments: "bill",
};
export default function AppShell({
  nav,
  children,
}: {
  nav: NavLink[];
  children: React.ReactNode;
}) {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const activeHref = nav
    .filter((i) => pathname === i.href || pathname.startsWith(i.href + "/"))
    .sort((a, b) => b.href.length - a.href.length)[0]?.href;
  const current = nav.find((i) => i.href === activeHref)?.label || "Workspace";
  const role = user?.role?.replaceAll("_", " ") || "Administrator";
  async function signOut() {
    await logout();
    router.replace("/login");
  }
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      {open && (
        <button
          className="nav-scrim"
          aria-label="Close navigation"
          onClick={() => setOpen(false)}
        />
      )}
      <aside
        className={`app-sidebar ${open ? "is-open" : ""}`}
        id="workspace-navigation"
      >
        <Link href={nav[0]?.href || "/"} className="brand">
          <span className="brand-mark">
            <Icon name="bolt" size={24} />
          </span>
          <span>
            SEBMS<small>ENERGY MANAGEMENT</small>
          </span>
        </Link>
        <button
          className="mobile-close"
          aria-label="Close navigation"
          onClick={() => setOpen(false)}
        >
          <Icon name="close" />
        </button>
        <p className="nav-caption">WORKSPACE</p>
        <nav aria-label="Main navigation">
          {nav.map((item) => (
            <Link
              href={item.href}
              key={item.href}
              aria-current={activeHref === item.href ? "page" : undefined}
              onClick={() => setOpen(false)}
              className={`nav-item ${activeHref === item.href ? "active" : ""}`}
            >
              <Icon name={icons[item.label] || "dashboard"} />
              {item.label}
              {activeHref === item.href && <span className="nav-dot" />}
            </Link>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-note">
            <Icon name="shield" />
            <strong>
              Your daily operations,
              <br />
              all in one place.
            </strong>
            <p>From meter readings to billing, stay in control.</p>
          </div>
          <div className="sidebar-version">
            <span className="status-dot" /> Electricity management
          </div>
        </div>
      </aside>
      <div className="app-workspace">
        <header className="workspace-header">
          <div className="flex items-center gap-3">
            <button
              className="mobile-menu"
              aria-label="Open navigation"
              aria-expanded={open}
              aria-controls="workspace-navigation"
              onClick={() => setOpen(!open)}
            >
              <Icon name="menu" />
            </button>
            <div className="breadcrumb">
              Workspace <span>/</span> <strong>{current}</strong>
            </div>
          </div>
          <div className="account-area">
            <div className="account-avatar">
              {user?.email?.[0]?.toUpperCase() || "S"}
            </div>
            <div className="account-meta">
              <strong>{user?.email}</strong>
              <span>{role}</span>
            </div>
            <button
              className="logout-button"
              onClick={() => void signOut()}
              aria-label="Sign out"
              title="Sign out"
            >
              <Icon name="logout" />
            </button>
          </div>
        </header>
        <main id="main-content" className="workspace-main">
          {children}
        </main>
        <footer className="workspace-footer">
          SEBMS <span>Smart electricity. Clearer operations.</span>
        </footer>
      </div>
    </div>
  );
}
