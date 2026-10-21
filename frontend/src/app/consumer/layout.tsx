"use client";

import AppShell from "@/components/AppShell";
import RoleGuard from "@/components/RoleGuard";

const NAV = [{ href: "/consumer", label: "My dashboard" }];

export default function ConsumerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <RoleGuard allow={["consumer"]}>
      <AppShell nav={NAV}>{children}</AppShell>
    </RoleGuard>
  );
}
