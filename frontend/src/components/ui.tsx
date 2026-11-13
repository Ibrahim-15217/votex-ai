import type { ReactNode } from "react";

import { AlertTriangleIcon, CheckCircleIcon, InboxIcon } from "./icons";
import type { IncidentStatus, Priority } from "../lib/api";
import { indicatorKindLabel, statusLabel } from "../lib/format";
import { useI18n, type TranslationKey } from "../lib/i18n";

export function cn(...values: Array<string | false | null | undefined>): string {
  return values.filter(Boolean).join(" ");
}

export const inputClass =
  "w-full rounded-lg border border-line bg-void/60 px-3.5 py-2.5 text-sm text-text placeholder:text-muted/80 transition focus:border-brand/60 focus:bg-void/80 focus:outline-none focus:ring-2 focus:ring-brand/20";

export const selectClass =
  "w-full appearance-none rounded-lg border border-line bg-void/60 px-3.5 py-2.5 text-sm text-text transition focus:border-brand/60 focus:bg-void/80 focus:outline-none focus:ring-2 focus:ring-brand/20";

export const labelClass =
  "mb-1.5 block text-[10px] font-semibold uppercase tracking-[0.14em] text-muted";

export const btnPrimary =
  "inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-brand to-brand-2 px-4 py-2.5 text-sm font-semibold text-void shadow-glow transition hover:brightness-110 active:translate-y-px disabled:cursor-not-allowed disabled:opacity-60";

export const btnGhost =
  "inline-flex items-center justify-center gap-2 rounded-lg border border-line bg-surface/60 px-4 py-2.5 text-sm font-medium text-text transition hover:border-brand/40 hover:bg-surface-2 disabled:cursor-not-allowed disabled:opacity-60";

export const btnSubtle =
  "inline-flex items-center justify-center gap-1.5 rounded-md border border-line/80 bg-void/40 px-2.5 py-1.5 text-[11px] font-medium text-muted transition hover:border-brand/40 hover:text-text disabled:cursor-not-allowed disabled:opacity-60";

const statusTones: Record<string, string> = {
  submitted: "border-line bg-surface-2/80 text-muted",
  under_review: "border-brand/25 bg-brand/10 text-brand",
  assigned: "border-violet/25 bg-violet/10 text-violet",
  investigating: "border-brand-2/25 bg-brand-2/10 text-brand-2",
  escalated: "border-warning/25 bg-warning/10 text-warning",
  contained: "border-success/25 bg-success/10 text-success",
  remediated: "border-success/30 bg-success/10 text-success",
  recovered: "border-success/30 bg-success/10 text-success",
  closed: "border-line bg-surface/70 text-muted",
};

const priorityTones: Record<Priority, string> = {
  low: "border-line bg-surface-2/70 text-muted",
  medium: "border-brand/25 bg-brand/10 text-brand",
  high: "border-warning/25 bg-warning/10 text-warning",
  critical: "border-critical/30 bg-critical/10 text-critical",
};

export function StatusPill({ status }: { status: IncidentStatus | string }) {
  const { t } = useI18n();
  const known = status in statusTones;
  const label = known ? t(`status.${status}` as TranslationKey) : statusLabel(status);

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[10.5px] font-medium",
        statusTones[status] ?? "border-line bg-surface-2 text-muted",
      )}
    >
      <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-current" />
      {label}
    </span>
  );
}

export function PriorityPill({ priority }: { priority: Priority }) {
  const { t } = useI18n();

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-[10.5px] font-semibold",
        priorityTones[priority],
      )}
    >
      {t(`priority.${priority}` as TranslationKey)}
    </span>
  );
}

const kindTones: Record<string, string> = {
  url: "border-brand/30 bg-brand/10 text-brand",
  domain: "border-violet/30 bg-violet/10 text-violet",
  ipv4: "border-brand-2/30 bg-brand-2/10 text-brand-2",
  sha256: "border-warning/30 bg-warning/10 text-warning",
  md5: "border-line bg-surface-2/70 text-muted",
};

export function IndicatorKindPill({ kind, className }: { kind: string; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex shrink-0 items-center rounded border px-1.5 py-0.5 font-mono text-[9px] font-semibold uppercase tracking-[0.06em]",
        kindTones[kind] ?? "border-line bg-surface-2/70 text-muted",
        className,
      )}
    >
      {indicatorKindLabel(kind)}
    </span>
  );
}

export function RiskScore({ score }: { score: number | null }) {
  const { t } = useI18n();

  if (score === null || score === undefined) {
    return <span className="font-mono text-xs text-muted">{t("common.pending")}</span>;
  }
  const tone =
    score >= 85 ? "text-critical" : score >= 70 ? "text-warning" : score >= 50 ? "text-brand" : "text-success";
  const bar =
    score >= 85 ? "bg-critical" : score >= 70 ? "bg-warning" : score >= 50 ? "bg-brand" : "bg-success";
  return (
    <span className="inline-flex items-center gap-2">
      <span className={cn("font-mono text-xs font-semibold", tone)}>{score.toFixed(1)}</span>
      <span className="h-1.5 w-12 overflow-hidden rounded-full bg-surface-2">
        <span className={cn("block h-full rounded-full", bar)} style={{ width: `${Math.min(score, 100)}%` }} />
      </span>
    </span>
  );
}

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <section
      className={cn(
        "min-w-0 rounded-xl border border-line/80 bg-surface/50 shadow-panel backdrop-blur-sm",
        className,
      )}
    >
      {children}
    </section>
  );
}

export function CardHeader({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-3 border-b border-line/70 px-5 py-4">
      <div>
        <h2 className="text-sm font-semibold text-text">{title}</h2>
        {description && <p className="mt-0.5 text-[11.5px] text-muted">{description}</p>}
      </div>
      {action}
    </div>
  );
}

export function Spinner({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-r-transparent",
        className,
      )}
      aria-hidden="true"
    />
  );
}

export function EmptyState({
  title,
  body,
  action,
}: {
  title: string;
  body: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 px-6 py-14 text-center">
      <span className="grid h-11 w-11 place-items-center rounded-xl border border-line bg-surface-2/60 text-muted">
        <InboxIcon className="h-5 w-5" />
      </span>
      <div>
        <p className="text-sm font-semibold text-text">{title}</p>
        <p className="mx-auto mt-1 max-w-sm text-xs leading-relaxed text-muted">{body}</p>
      </div>
      {action}
    </div>
  );
}

export function ErrorState({
  title,
  body,
  action,
}: {
  title: string;
  body: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 px-6 py-14 text-center">
      <span className="grid h-11 w-11 place-items-center rounded-xl border border-danger/25 bg-danger/10 text-danger">
        <AlertTriangleIcon className="h-5 w-5" />
      </span>
      <div>
        <p className="text-sm font-semibold text-text">{title}</p>
        <p className="mx-auto mt-1 max-w-sm text-xs leading-relaxed text-muted">{body}</p>
      </div>
      {action}
    </div>
  );
}

export function EnglishOnlyBadge({ className }: { className?: string }) {
  const { t } = useI18n();

  return (
    <span
      title={t("common.englishOnly")}
      className={cn(
        "inline-flex items-center rounded-full border border-line bg-surface/60 px-2.5 py-1 text-[10px] font-medium text-muted",
        className,
      )}
    >
      {t("common.englishOnlyBadge")}
    </span>
  );
}

export function Notice({
  tone = "error",
  children,
}: {
  tone?: "error" | "success" | "info";
  children: ReactNode;
}) {
  const tones = {
    error: "border-danger/25 bg-danger/[0.08] text-danger",
    success: "border-success/25 bg-success/[0.08] text-success",
    info: "border-brand/25 bg-brand/[0.08] text-brand",
  };
  return (
    <p
      role={tone === "error" ? "alert" : "status"}
      className={cn("rounded-lg border px-3 py-2.5 text-[11.5px] leading-relaxed", tones[tone])}
    >
      {children}
    </p>
  );
}

export function VerifiedPill({ valid }: { valid: boolean }) {
  return valid ? (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-success/30 bg-success/10 px-2.5 py-1 text-[11px] font-semibold text-success">
      <CheckCircleIcon className="h-3.5 w-3.5" />
      Chain verified
    </span>
  ) : (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-danger/30 bg-danger/10 px-2.5 py-1 text-[11px] font-semibold text-danger">
      <AlertTriangleIcon className="h-3.5 w-3.5" />
      Verification failed
    </span>
  );
}

export function PageHeader({
  title,
  description,
  actions,
  badge,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
  badge?: ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div className="min-w-0">
        <h1 className="text-2xl font-semibold tracking-tight text-text sm:text-[1.7rem]">{title}</h1>
        {description && <p className="mt-1.5 max-w-2xl text-sm leading-relaxed text-muted">{description}</p>}
        {badge && <div className="mt-2.5 flex flex-wrap items-center gap-2">{badge}</div>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}
