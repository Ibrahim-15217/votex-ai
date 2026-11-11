import type { ReactNode } from "react";

import { EyeOffIcon } from "./icons";
import { cn } from "./ui";
import type { DashboardCount, TrendPoint } from "../lib/api";
import { formatDay, formatShortDate } from "../lib/format";

const DEFAULT_TONES = [
  "bg-brand",
  "bg-violet",
  "bg-brand-2",
  "bg-warning",
  "bg-success",
  "bg-critical",
  "bg-muted/60",
];

const SEVERITY_TONES: Record<string, string> = {
  high_risk: "bg-critical",
  suspicious: "bg-warning",
  benign: "bg-success",
  unclassified: "bg-muted/50",
};

export function SuppressedChip({ label = "k < 5" }: { label?: string }) {
  return (
    <span className="inline-flex items-center gap-1 rounded border border-line/80 bg-surface-2/60 px-1.5 py-0.5 text-[9px] font-medium uppercase tracking-[0.08em] text-muted/80">
      <EyeOffIcon className="h-2.5 w-2.5" />
      {label}
    </span>
  );
}

export function SuppressionNote({
  suppressed,
  threshold,
}: {
  suppressed: number;
  threshold: number;
}) {
  return (
    <div className="flex items-start gap-2.5 rounded-lg border border-violet/20 bg-violet/[0.05] px-3.5 py-2.5">
      <EyeOffIcon className="mt-0.5 h-4 w-4 shrink-0 text-violet/90" />
      <p className="text-[10.5px] leading-relaxed text-muted">
        <span className="font-semibold text-violet/90">k ≥ {threshold} suppression active.</span>{" "}
        {suppressed > 0
          ? `${suppressed} small cell${suppressed === 1 ? "" : "s"} hidden before the response reaches this browser.`
          : "Cells below the threshold will be hidden before the response reaches this browser."}{" "}
        Suppressed values are never included in CSV exports.
      </p>
    </div>
  );
}

export function TrendChart({ points, tone = "brand" }: { points: TrendPoint[]; tone?: "brand" | "violet" }) {
  if (points.length === 0) {
    return <p className="px-5 py-10 text-center text-xs text-muted">No trend data yet.</p>;
  }

  const max = Math.max(
    1,
    ...points.map((point) => point.total ?? 0),
    ...points.map((point) => point.high_risk ?? 0),
  );
  const peak = points.reduce<TrendPoint | null>((best, point) => {
    if (point.total === null) return best;
    if (!best || (best.total ?? 0) < point.total) return point;
    return best;
  }, null);

  const fromClass = tone === "violet" ? "from-violet/80 to-violet/30" : "from-brand/80 to-brand/25";
  const hoverFrom = tone === "violet" ? "group-hover:from-violet" : "group-hover:from-brand";

  const labelIndexes = [0, Math.floor((points.length - 1) / 4), Math.floor((points.length - 1) / 2), Math.floor(((points.length - 1) * 3) / 4), points.length - 1];

  return (
    <div className="px-5 py-4">
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[9.5px] text-muted/80">
          <span className="inline-flex items-center gap-1.5">
            <span className={cn("h-2 w-2 rounded-sm", tone === "violet" ? "bg-violet" : "bg-brand")} />
            Incidents
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-sm bg-critical" />
            High risk
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-sm border border-dashed border-line bg-surface-2/60" />
            Suppressed
          </span>
        </div>
        {peak && peak.total !== null && peak.total > 0 && (
          <span className="font-mono text-[9.5px] text-muted/80">
            peak {peak.total} · {formatShortDate(peak.date)}
          </span>
        )}
      </div>

      <div className="flex h-[132px] items-end gap-[3px]" role="img" aria-label="Daily incident trend for the last 30 days">
        {points.map((point) => {
          const hidden = point.total === null;
          const total = point.total ?? 0;
          const highRisk = point.high_risk ?? 0;
          const title = hidden
            ? `${formatDay(point.date)} · suppressed (k < 5)`
            : `${formatDay(point.date)} · ${total} incident${total === 1 ? "" : "s"}${highRisk ? `, ${highRisk} high risk` : ""}`;

          return (
            <div key={point.date} className="group relative flex h-full flex-1 items-end justify-center" title={title}>
              {hidden ? (
                <span
                  className="w-full max-w-[13px] rounded-sm border border-dashed border-line bg-surface-2/40"
                  style={{ height: 6 }}
                />
              ) : (
                <span
                  className={cn(
                    "relative w-full max-w-[13px] overflow-hidden rounded-sm bg-gradient-to-t transition-colors",
                    fromClass,
                    hoverFrom,
                  )}
                  style={{ height: `${Math.max(3, (total / max) * 100)}%` }}
                >
                  {highRisk > 0 && total > 0 && (
                    <span
                      className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-critical to-critical/60"
                      style={{ height: `${Math.min(100, (highRisk / total) * 100)}%` }}
                    />
                  )}
                </span>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-2 flex justify-between border-t border-line/50 pt-2 font-mono text-[8.5px] text-muted/80">
        {labelIndexes.map((index, position) => (
          <span key={`${index}-${position}`}>{formatShortDate(points[index]?.date ?? null)}</span>
        ))}
      </div>
      <p className="mt-1.5 text-[9px] text-muted/80">Rolling 30 days, UTC. Hover a bar for the daily count.</p>
    </div>
  );
}

export function SeveritySplit({ items }: { items: DashboardCount[] }) {
  const visible = items.filter((item) => item.suppressed || (item.count ?? 0) > 0);
  const total = items.reduce((sum, item) => sum + (item.count ?? 0), 0);

  if (visible.length === 0 || total === 0) {
    return <p className="px-5 py-8 text-center text-xs text-muted">Severity breakdown appears once incidents are analysed.</p>;
  }

  return (
    <div className="px-5 py-4">
      <div className="flex h-3 w-full overflow-hidden rounded-full border border-line/60 bg-surface-2/50">
        {items.map((item) => {
          if (item.suppressed || !item.count) return null;
          return (
            <span
              key={item.key}
              className={cn("h-full", SEVERITY_TONES[item.key] ?? "bg-muted/50")}
              style={{ width: `${(item.count / total) * 100}%` }}
              title={`${item.label}: ${item.count}`}
            />
          );
        })}
      </div>
      <ul className="mt-3.5 grid grid-cols-2 gap-2">
        {items.map((item) => (
          <li key={item.key} className="flex items-center justify-between gap-2 rounded-md border border-line/60 bg-void/30 px-2.5 py-1.5">
            <span className="flex min-w-0 items-center gap-1.5 text-[10px] text-muted">
              <span className={cn("h-1.5 w-1.5 shrink-0 rounded-full", SEVERITY_TONES[item.key] ?? "bg-muted/50")} />
              <span className="truncate">{item.label}</span>
            </span>
            {item.suppressed ? (
              <SuppressedChip label="hidden" />
            ) : (
              <span className="font-mono text-[10.5px] font-semibold text-text/90">{item.count ?? 0}</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function BarList({
  items,
  tones,
  emptyLabel = "No data in this window yet.",
  formatValue,
}: {
  items: DashboardCount[];
  tones?: Record<string, string>;
  emptyLabel?: string;
  formatValue?: (item: DashboardCount) => ReactNode;
}) {
  const visible = items.filter((item) => item.suppressed || (item.count ?? 0) > 0);
  const max = Math.max(1, ...items.map((item) => item.count ?? 0));

  if (visible.length === 0) {
    return <p className="px-5 py-8 text-center text-xs text-muted/80">{emptyLabel}</p>;
  }

  return (
    <ul className="space-y-2.5 px-5 py-4">
      {visible.map((item, index) => (
        <li key={item.key} className="group">
          <div className="flex items-center justify-between gap-3">
            <span className="truncate text-[11px] font-medium text-text/85">{item.label}</span>
            {item.suppressed ? (
              <SuppressedChip />
            ) : formatValue ? (
              formatValue(item)
            ) : (
              <span className="font-mono text-[10.5px] text-muted">{item.count ?? 0}</span>
            )}
          </div>
          <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-surface-2/70">
            {item.suppressed ? (
              <span className="block h-full w-2/5 rounded-full border border-dashed border-line bg-surface-2/50" />
            ) : (
              <span
                className={cn("block h-full rounded-full transition-[width] duration-500", tones?.[item.key] ?? DEFAULT_TONES[index % DEFAULT_TONES.length])}
                style={{ width: `${Math.max(((item.count ?? 0) / max) * 100, 3)}%` }}
              />
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
