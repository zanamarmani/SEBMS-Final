"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { homeFor, useAuth } from "@/lib/auth";
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
    const allowed =
      user.is_superuser || (user.role !== null && allow.includes(user.role));
    if (!allowed) router.replace(homeFor(user));
  }, [status, user, allow, pathname, router]);

  if (status !== "ready" || !user) return <CenteredSpinner />;

  const allowed =
    user.is_superuser || (user.role !== null && allow.includes(user.role));
  if (!allowed) return <CenteredSpinner />;

  return <>{children}</>;
}
