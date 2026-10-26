"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { homeFor, useAuth } from "@/lib/auth";
import { canAccessRoles } from "@/lib/routing";
import type { Role } from "@/lib/types";
import { CenteredSpinner } from "./ui";

export default function RoleGuard({
  allow,
  children,
}: {
  allow: Role[];
  children: React.ReactNode;
}) {
  const { user, status } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (status !== "ready") return;
    if (!user) {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
      return;
    }
    const allowed = canAccessRoles(user, allow);
    if (!allowed) router.replace(homeFor(user));
  }, [status, user, allow, pathname, router]);

  if (status !== "ready" || !user) return <CenteredSpinner />;

  const allowed = canAccessRoles(user, allow);
  if (!allowed) return <CenteredSpinner />;

  return <>{children}</>;
}
