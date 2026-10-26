"use client";

import AppShell from "@/components/AppShell";
import RoleGuard from "@/components/RoleGuard";

const NAV = [
  { href: "/office", label: "Home" },
  { href: "/office/consumers", label: "Consumers" },
  { href: "/office/meters", label: "Meters" },
  { href: "/office/readings", label: "Readings" },
  { href: "/office/bills", label: "Bills" },
  { href: "/office/payments", label: "Payments" },
];

export default function OfficeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <RoleGuard allow={["office_staff"]}>
      <AppShell nav={NAV}>{children}</AppShell>
    </RoleGuard>
  );
}
