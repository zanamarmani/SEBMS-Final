"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth";
import { Button } from "./ui";

export interface NavLink {
  href: string;
  label: string;
}

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

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <header className="flex items-center justify-between border-b border-gray-200 bg-white px-4 py-2.5">
        <div className="flex items-center gap-3">
          <span className="rounded-md bg-blue-600 px-2 py-1 text-sm font-bold text-white">
            SEBMS
          </span>
          <span className="hidden text-sm text-gray-500 sm:inline">
            Electricity Billing Management
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="max-w-[180px] truncate text-sm text-gray-600">
            {user?.email}
          </span>
          <Button variant="secondary" onClick={() => void handleLogout()}>
            Logout
          </Button>
        </div>
      </header>
      <div className="flex flex-1">
        <aside className="w-52 shrink-0 border-r border-gray-200 bg-white p-3">
          <nav className="flex flex-col gap-1">
            {nav.map((item) => {
              const active =
                item.href === pathname || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={
                    active
                      ? "rounded-md bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700"
                      : "rounded-md px-3 py-2 text-sm text-gray-600 hover:bg-gray-50"
                  }
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </aside>
        <main className="flex-1 p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
