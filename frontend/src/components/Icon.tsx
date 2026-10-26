import type { CSSProperties } from "react";
const paths: Record<string, string> = {
  bolt: "m13 2-9 12h7l-1 8 10-12h-7l1-8Z",
  dashboard: "M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z",
  users:
    "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M16 3a4 4 0 0 1 0 8 M22 21v-2a4 4 0 0 0-3-3.87 M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0",
  bill: "M6 3h12v18l-3-2-3 2-3-2-3 2V3Z M9 7h6 M9 11h6 M9 15h3",
  meter: "M4 18a9 9 0 1 1 16 0 M12 12l5-5 M5 18h14 M12 5v2 M5 10l2 1",
  tariff: "M4 7h16 M4 17h16 M8 4v6 M16 14v6",
  arrow: "M5 12h14 m-6-6 6 6-6 6",
  menu: "M4 6h16 M4 12h16 M4 18h16",
  close: "m6 6 12 12 M6 18 18 6",
  logout: "M9 4H4v16h5 M10 12h11 m-4-4 4 4-4 4",
  check: "m5 12 4 4L19 6",
  download: "M12 3v12 m-5-5 5 5 5-5 M4 17v4h16v-4",
  shield: "m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z m-4 9 3 3 5-6",
};
export default function Icon({
  name,
  size = 20,
  style,
  className = "",
}: {
  name: string;
  size?: number;
  style?: CSSProperties;
  className?: string;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={className}
      style={style}
    >
      <path d={paths[name] || paths.bill} />
    </svg>
  );
}
