export function money(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  const n = typeof value === "number" ? value : parseFloat(value);
  if (Number.isNaN(n)) return String(value);
  return `Rs ${n.toLocaleString("en-PK", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function dateOnly(value: string | null | undefined): string {
  if (!value) return "—";
  return value.slice(0, 10);
}

export function yesNo(value: boolean | null | undefined): string {
  return value ? "Yes" : "No";
}

export function unitsBetween(
  last: string | null | undefined,
  next: string | null | undefined,
): string {
  const a = parseFloat(last ?? "0");
  const b = parseFloat(next ?? "0");
  if (Number.isNaN(a) || Number.isNaN(b)) return "—";
  return String(b - a);
}

/** Flatten DRF field-error details into a flat message map. */
export function fieldErrors(err: unknown): Record<string, string> {
  if (!(err instanceof Error)) return {};
  const details = (err as { details?: unknown }).details;
  if (!details || typeof details !== "object") return {};
  const out: Record<string, string> = {};
  for (const [key, val] of Object.entries(details as Record<string, unknown>)) {
    if (Array.isArray(val)) {
      out[key] = val.map(String).join(" ");
    } else if (typeof val === "string") {
      out[key] = val;
    } else if (val && typeof val === "object") {
      const nested = val as Record<string, unknown>;
      if ("detail" in nested) out[key] = String(nested.detail);
    }
  }
  return out;
}

export function errorMessage(err: unknown): string {
  if (err instanceof Error) return err.message;
  return "Something went wrong.";
}
