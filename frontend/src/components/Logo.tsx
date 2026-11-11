export function Logo() {
  return (
    <a href="/" className="group inline-flex items-center gap-3" aria-label="Votex AI home">
      <span className="relative grid h-10 w-10 place-items-center rounded-xl border border-brand/30 bg-brand/10 text-brand shadow-[0_0_26px_rgba(34,211,238,0.18)] transition group-hover:border-brand/60">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.5}
          strokeLinecap="round"
          strokeLinejoin="round"
          className="h-5 w-5"
          aria-hidden="true"
        >
          <path d="M12 3 5 6v5.2c0 4.2 2.7 7.9 7 9.8 4.3-1.9 7-5.6 7-9.8V6l-7-3Z" />
          <path d="M9.2 11.8h5.6M12 9v5.6" />
        </svg>
        <span className="absolute -right-1 -top-1 h-2 w-2 rounded-full bg-brand shadow-[0_0_10px_rgba(34,211,238,0.9)]" />
      </span>
      <span className="leading-none">
        <span className="block text-[15px] font-semibold tracking-[0.24em] text-text">VOTEX AI</span>
        <span className="mt-1.5 block text-[9px] font-medium uppercase tracking-[0.22em] text-muted">
          Electoral Cybersecurity
        </span>
      </span>
    </a>
  );
}
