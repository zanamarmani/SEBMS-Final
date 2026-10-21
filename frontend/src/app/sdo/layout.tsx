"use client";

import AppShell from "@/components/AppShell";
import RoleGuard from "@/components/RoleGuard";

const NAV = [
  { href: "/sdo", label: "Dashboard" },
  { href: "/sdo/tariffs", label: "Tariffs" },
  { href: "/sdo/consumers", label: "Consumers" },
  { href: "/sdo/users", label: "Users" },
];

export default function SdoLayout({ children }: { children: React.ReactNode }) {
  return (
    <RoleGuard allow={["sdo"]}>
      <AppShell nav={NAV}>{children}</AppShell>
    </RoleGuard>
  );
}
