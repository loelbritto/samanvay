/** Two separate channels form one S. They align without joining or merging. */
export function BrandMark({
  size = 40,
  className = "",
}: {
  size?: number;
  className?: string;
}) {
  return (
    <svg
      className={"brand-mark " + className}
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M74 17H43C26.4 17 13 30.4 13 47V53H46V41H26.5C29 33.9 35.4 29 43 29H74a6 6 0 0 0 0-12Z"
        fill="currentColor"
      />
      <path
        d="M26 83H57C73.6 83 87 69.6 87 53V47H54V59H73.5C71 66.1 64.6 71 57 71H26a6 6 0 0 0 0 12Z"
        fill="currentColor"
      />
    </svg>
  );
}

export function Brand({ tagline = true }: { tagline?: boolean }) {
  return (
    <span className="brand-lockup">
      <BrandMark />
      <span className="brand-wordmark">
        samanvay
        <span className="brand-period" aria-hidden="true">
          .
        </span>
        {tagline && <small>Clarity. Accountability. Together.</small>}
      </span>
    </span>
  );
}
