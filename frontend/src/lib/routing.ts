import type { User } from "./types";

export function homeFor(user: User | null): string {
  if (!user) return "/login";
  if (user.is_superuser || user.role === "sdo") return "/sdo";
  if (user.role === "office_staff") return "/office";
  if (user.role === "meter_reader") return "/reader";
  if (user.role === "consumer") return "/consumer";
  return "/";
}

export function loginDestination(user: User, next: string | null): string {
  const home = homeFor(user);
  // Only restore a local destination inside this identity's own workspace.
  if (next && !next.includes("\\") && !/[\u0000-\u001f]/.test(next)) {
    const path = next.split(/[?#]/, 1)[0];
    if (path === home || path.startsWith(home + "/")) return next;
  }
  return home;
}

export function canAccessRoles(user: User, allow: readonly string[]): boolean {
  if (user.is_superuser) return allow.includes("sdo");
  return user.role !== null && allow.includes(user.role);
}
