import type { ReactNode } from "react";

export function Icon({ name, size = 20 }: { name: string; size?: number }) {
  const paths: Record<string, ReactNode> = {
    overview: (
      <>
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </>
    ),
    cases: (
      <>
        <path d="M8 5H5v16h14V5h-3M9 3h6v4H9zM8 12h8M8 16h6" />
      </>
    ),
    institutions: (
      <>
        <path d="M3 21h18M5 21V8h14v13M3 8l9-5 9 5M9 11v6m6-6v6" />
      </>
    ),
    coordination: (
      <>
        <rect x="2" y="4" width="8" height="8" rx="2" />
        <rect x="14" y="12" width="8" height="8" rx="2" />
        <path d="M14 6h4v6M6 12v6h8" />
      </>
    ),
    reports: (
      <>
        <path d="M5 3h10l4 4v14H5zM14 3v5h5M8 17v-3m4 3v-6m4 6v-4" />
      </>
    ),
    notifications: (
      <>
        <path d="M18 8a6 6 0 00-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" />
      </>
    ),
    settings: (
      <>
        <circle cx="12" cy="12" r="3" />
        <path d="M12 2v3m0 14v3M2 12h3m14 0h3M5 5l2 2m10 10l2 2M5 19l2-2M17 7l2-2" />
      </>
    ),
    arrow: <path d="M5 12h14m-5-5l5 5-5 5" />,
    info: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 11v6m0-10v1" />
      </>
    ),
    clock: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v5l3 2" />
      </>
    ),
    check: <path d="M5 12l4 4L19 6" />,
    search: (
      <>
        <circle cx="10" cy="10" r="6" />
        <path d="M15 15l6 6" />
      </>
    ),
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name] ?? paths.info}
    </svg>
  );
}
