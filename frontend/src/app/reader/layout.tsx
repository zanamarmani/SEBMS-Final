"use client";

import AppShell from "@/components/AppShell";
import RoleGuard from "@/components/RoleGuard";

const NAV = [{ href: "/reader", label: "Capture reading" }];

export default function ReaderLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <RoleGuard allow={["meter_reader", "office_staff", "sdo"]}>
      <AppShell nav={NAV}>{children}</AppShell>
    </RoleGuard>
  );
}
