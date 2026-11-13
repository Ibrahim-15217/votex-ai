import { useEffect, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import {
  ActivityIcon,
  AlertTriangleIcon,
  ClockIcon,
  DownloadIcon,
  GlobeIcon,
  InboxIcon,
  LayersIcon,
  LockIcon,
  NetworkIcon,
  RefreshIcon,
  ShieldCheckIcon,
  UsersIcon,
} from "../components/icons";
import {
  BarList,
  SeveritySplit,
  SuppressedChip,
  SuppressionNote,
  TrendChart,
} from "../components/charts";
import {
  Card,
  CardHeader,
  EnglishOnlyBadge,
  ErrorState,
  IndicatorKindPill,
  Notice,
  PageHeader,
  Spinner,
  cn,
  btnGhost,
  btnPrimary,
} from "../components/ui";
import { api, downloadCsv, type DashboardResponse } from "../lib/api";
import { formatDateTime, formatHours } from "../lib/format";

const CATEGORY_TONES: Record<string, string> = {
  phishing: "bg-brand",
  fake_portal: "bg-violet",
  impersonation: "bg-brand-2",
  payment_fraud: "bg-warning",
  malware: "bg-critical",
  fake_result: "bg-success",
  other: "bg-muted/60",
};

const CHANNEL_TONES: Record<string, string> = {
  email: "bg-brand",
  sms: "bg-violet",
  whatsapp: "bg-success",
  web_form: "bg-brand-2",
  phone: "bg-warning",
  other: "bg-muted/60",
};

const STATUS_TONES: Record<string, string> = {
  submitted: "bg-muted/50",
  under_review: "bg-brand",
  assigned: "bg-violet",
  investigating: "bg-brand-2",
  escalated: "bg-warning",
  contained: "bg-success",
  remediated: "bg-success",
  recovered: "bg-success",
  closed: "bg-muted/30",
};

export default function DashboardsPage() {
  const { user } = useAuth();
  const isAnalyst = user?.role === "admin" || user?.role === "analyst";
  const isAdmin = user?.role === "admin";

  const [tab, setTab] = useState<"organisation" | "national">("organisation");
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!isAnalyst) {
      setLoading(false);
      return;
    }
    if (tab === "national" && !isAdmin) return;

    let active = true;
    setLoading(true);
    setError(null);

    const request = tab === "national" ? api.nationalDashboard() : api.organisationDashboard();
    request
      .then((value) => {
        if (active) setData(value);
      })
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : "Could not load this dashboard.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [tab, isAdmin, isAnalyst, reloadKey]);

  const summary = data?.summary;
  const national = data?.scope === "national";

  async function handleExport() {
    setExporting(true);
    setFeedback(null);
    try {
      const filename = await downloadCsv(
        `/dashboards/${tab}/export`,
        `votex-${tab}-dashboard.csv`,
      );
      setFeedback(`Exported ${filename}. Suppressed cells are blank in the file, and the export is recorded on the audit chain.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed.");
    } finally {
      setExporting(false);
    }
  }

  if (!isAnalyst) {
    return (
      <div className="animate-rise space-y-4">
        <PageHeader
          title="Threat dashboards"
          description="Aggregate dashboards are available to administrators and analysts in the response team."
        />
        <Notice tone="info">
          Your role can report incidents and follow the case you submitted. Ask an analyst in your organisation for the
          aggregate threat picture.
        </Notice>
      </div>
    );
  }

  return (
    <div className="animate-rise space-y-5">
      <PageHeader
        title="Threat dashboards"
        description="One organisation view with exact counts, and a national view where every small cell is suppressed before any count is returned."
        badge={<EnglishOnlyBadge />}
        actions={
          <>
            <button
              type="button"
              onClick={() => setReloadKey((value) => value + 1)}
              className={btnGhost}
              disabled={loading}
            >
              <RefreshIcon className={cn("h-4 w-4", loading && "animate-spin")} />
              Refresh
            </button>
            <button
              type="button"
              onClick={() => void handleExport()}
              className={btnPrimary}
              disabled={exporting || !data}
            >
              {exporting ? <Spinner className="h-4 w-4" /> : <DownloadIcon className="h-4 w-4" />}
              Export CSV
            </button>
          </>
        }
      />

      <div
        role="tablist"
        aria-label="Dashboard scope"
        className="inline-flex flex-wrap items-center gap-1 rounded-xl border border-line/80 bg-surface/50 p-1"
      >
        <ScopeTab
          active={tab === "organisation"}
          onClick={() => setTab("organisation")}
          icon={<LayersIcon className="h-3.5 w-3.5" />}
          label="My organisation"
          hint={data?.organisation?.name ?? user?.organisation.name}
        />
        <ScopeTab
          active={tab === "national"}
          onClick={() => isAdmin && setTab("national")}
          icon={isAdmin ? <GlobeIcon className="h-3.5 w-3.5" /> : <LockIcon className="h-3.5 w-3.5" />}
          label="National picture"
          hint={isAdmin ? "Admin only · k ≥ 5" : "Admin access only"}
          disabled={!isAdmin}
        />
      </div>

      {feedback && <Notice tone="success">{feedback}</Notice>}
      {error && <Notice>{error}</Notice>}

      {national && summary && (
        <SuppressionNote suppressed={summary.suppressed_cells} threshold={summary.k_threshold} />
      )}

      {loading && !data ? (
        <DashboardSkeleton />
      ) : !data || !summary ? (
        <Card>
          <ErrorState
            title="Dashboard unavailable"
            body={error ?? "The aggregate view could not be loaded."}
            action={
              <button
                type="button"
                onClick={() => setReloadKey((value) => value + 1)}
                className={btnGhost}
              >
                <RefreshIcon className="h-4 w-4" />
                Try again
              </button>
            }
          />
        </Card>
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <StatTile
              icon={<InboxIcon className="h-4 w-4" />}
              label={national ? "Incidents nationally" : "Incidents in scope"}
              value={summary.total === null ? <SuppressedChip label="hidden" /> : summary.total}
              note={national ? "Synthetic reports across all tenants" : "Every report in your organisation"}
              tone="text-brand"
            />
            <StatTile
              icon={<ActivityIcon className="h-4 w-4" />}
              label="Open cases"
              value={summary.open === null ? <SuppressedChip label="hidden" /> : summary.open}
              note="Not yet closed"
              tone="text-violet"
            />
            <StatTile
              icon={<AlertTriangleIcon className="h-4 w-4" />}
              label="High-risk open"
              value={summary.high_risk === null ? <SuppressedChip label="hidden" /> : summary.high_risk}
              note="Risk score ≥ 65 and still open"
              tone="text-critical"
            />
            <StatTile
              icon={<NetworkIcon className="h-4 w-4" />}
              label="Correlated cases"
              value={summary.linked_incidents === null ? <SuppressedChip label="hidden" /> : summary.linked_incidents}
              note="Share at least one indicator"
              tone="text-warning"
            />
          </div>

          <div className="grid gap-px overflow-hidden rounded-xl border border-line/80 bg-line/50 sm:grid-cols-2 xl:grid-cols-4">
            <Metric
              icon={<NetworkIcon className="h-3.5 w-3.5" />}
              label="Shared indicators"
              value={summary.shared_indicators === null ? <SuppressedChip label="hidden" /> : summary.shared_indicators}
              hint="Used by 2 or more incidents"
            />
            <Metric
              icon={<ActivityIcon className="h-3.5 w-3.5" />}
              label="Mean risk score"
              value={summary.mean_risk === null ? "—" : summary.mean_risk.toFixed(1)}
              hint="Analysed cases only"
            />
            <Metric
              icon={<ClockIcon className="h-3.5 w-3.5" />}
              label="Mean resolution"
              value={formatHours(summary.mean_resolution_hours)}
              hint="Closed cases only"
            />
            <Metric
              icon={national ? <UsersIcon className="h-3.5 w-3.5" /> : <ShieldCheckIcon className="h-3.5 w-3.5" />}
              label={national ? "Organisations" : "k-anonymity"}
              value={national ? summary.organisations ?? "—" : `k ≥ ${summary.k_threshold}`}
              hint={national ? "Tenants contributing to the picture" : "Applied to national aggregates"}
            />
          </div>

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.7fr)_minmax(0,1fr)]">
            <Card>
              <CardHeader
                title="Incident trend"
                description="Daily intake and the high-risk share over the last 30 days."
                action={
                  <span className="font-mono text-[9.5px] text-muted/80">
                    {formatDateTime(data.generated_at)}
                  </span>
                }
              />
              <TrendChart points={data.trend} tone={national ? "violet" : "brand"} />
            </Card>

            <Card>
              <CardHeader title="Severity mix" description="Risk bands from the hybrid engine." />
              <SeveritySplit items={data.severity} />
            </Card>
          </div>

          <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
            <Card>
              <CardHeader title="Categories" description="What the public is reporting." />
              <BarList items={data.categories} tones={CATEGORY_TONES} />
            </Card>
            <Card>
              <CardHeader title="Reported channels" description="Where the contact started." />
              <BarList items={data.channels} tones={CHANNEL_TONES} />
            </Card>
            <Card>
              <CardHeader title="States" description="Geographic spread of synthetic reports." />
              <BarList items={data.states} emptyLabel="No state metadata yet." />
            </Card>
          </div>

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)]">
            <Card>
              <CardHeader
                title="Surging indicators"
                description={
                  national
                    ? `Only indicators linked to at least ${summary.k_threshold} incidents are shown.`
                    : "Indicators linked to two or more incidents in your organisation."
                }
                action={
                  <Link
                    to="/intelligence"
                    className="inline-flex items-center gap-1.5 text-[10.5px] font-medium text-brand/90 transition hover:text-brand"
                  >
                    Investigate
                    <NetworkIcon className="h-3.5 w-3.5" />
                  </Link>
                }
              />
              {data.top_indicators.length === 0 ? (
                <p className="px-5 py-8 text-center text-[11px] leading-relaxed text-muted/80">
                  No indicator is shared yet. Correlation grows automatically as new reports and evidence reuse a
                  domain, URL, IP address or file hash.
                </p>
              ) : (
                <ul className="divide-y divide-line/50">
                  {data.top_indicators.map((item, index) => (
                    <li key={`${item.kind}-${index}-${item.display_value}`} className="px-5 py-3">
                      <div className="flex items-center justify-between gap-3">
                        <div className="flex min-w-0 items-center gap-2">
                          <IndicatorKindPill kind={item.kind} />
                          <Link
                            to={`/intelligence?q=${encodeURIComponent(item.display_value)}`}
                            className="truncate font-mono text-[10.5px] text-text/85 transition hover:text-brand"
                            title={item.display_value}
                          >
                            {item.display_value}
                          </Link>
                        </div>
                        <span className="inline-flex shrink-0 items-center gap-1 rounded-full border border-warning/25 bg-warning/10 px-1.5 py-0.5 text-[9.5px] font-medium text-warning">
                          {item.incident_count} links
                        </span>
                      </div>
                      <div className="mt-1.5 flex items-center gap-2">
                        <span className="h-1 flex-1 overflow-hidden rounded-full bg-surface-2">
                          <span
                            className="block h-full rounded-full bg-gradient-to-r from-brand to-violet"
                            style={{
                              width: `${Math.max((item.incident_count / Math.max(1, data.top_indicators[0].incident_count)) * 100, 6)}%`,
                            }}
                          />
                        </span>
                        <span className="text-[9px] text-muted/80">
                          {national
                            ? `${item.organisation_count} organisation${item.organisation_count === 1 ? "" : "s"}`
                            : "same tenant"}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Card>
              <CardHeader title="Response pipeline" description="Lifecycle state across visible incidents." />
              <BarList items={data.statuses} tones={STATUS_TONES} />
            </Card>
          </div>

          <div className="flex flex-wrap items-center gap-2 rounded-xl border border-line/70 bg-surface/40 px-4 py-3">
            <ShieldCheckIcon className="h-4 w-4 text-success/80" />
            <p className="text-[10px] leading-relaxed text-muted/80">
              Privacy rules are applied before any figure is returned. {national
                ? "National cells smaller than k = 5 are withheld and left blank in CSV exports."
                : "Organisation counts are exact and visible only to your tenant."}
            </p>
          </div>
        </>
      )}
    </div>
  );
}

function ScopeTab({
  active,
  onClick,
  icon,
  label,
  hint,
  disabled = false,
}: {
  active: boolean;
  onClick: () => void;
  icon: ReactNode;
  label: string;
  hint?: string;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "flex items-center gap-2.5 rounded-lg border px-3 py-2 text-left transition",
        active
          ? "border-brand/30 bg-brand/10 text-brand"
          : "border-transparent text-muted hover:border-line hover:bg-surface-2/50 hover:text-text",
        disabled && "cursor-not-allowed opacity-60 hover:border-transparent hover:bg-transparent hover:text-muted",
      )}
    >
      <span className={cn("grid h-6 w-6 place-items-center rounded-md border", active ? "border-brand/25 bg-brand/10" : "border-line bg-void/40")}>
        {icon}
      </span>
      <span>
        <span className="block text-[11.5px] font-semibold">{label}</span>
        {hint && <span className="block text-[9px] font-normal text-muted/80">{hint}</span>}
      </span>
    </button>
  );
}

function StatTile({
  icon,
  label,
  value,
  note,
  tone,
}: {
  icon: ReactNode;
  label: string;
  value: ReactNode;
  note: string;
  tone: string;
}) {
  return (
    <div className="rounded-xl border border-line/80 bg-surface/50 p-4 shadow-panel backdrop-blur-sm">
      <div className="flex items-center justify-between gap-2">
        <span className={cn("grid h-8 w-8 place-items-center rounded-lg border border-line bg-void/50", tone)}>{icon}</span>
        <span className="text-right text-[9px] font-semibold uppercase tracking-[0.14em] text-muted/80">{label}</span>
      </div>
      <div className={cn("mt-3 flex min-h-[1.6rem] items-center font-mono text-2xl font-semibold leading-none", tone)}>
        {value}
      </div>
      <p className="mt-1.5 text-[10px] leading-relaxed text-muted/80">{note}</p>
    </div>
  );
}

function Metric({
  icon,
  label,
  value,
  hint,
}: {
  icon: ReactNode;
  label: string;
  value: ReactNode;
  hint: string;
}) {
  return (
    <div className="bg-surface/60 px-4 py-3">
      <p className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.13em] text-muted/80">
        <span className="text-brand/70">{icon}</span>
        {label}
      </p>
      <p className="mt-1.5 font-mono text-lg font-semibold leading-none text-text">{value}</p>
      <p className="mt-1 text-[9px] leading-relaxed text-muted/80">{hint}</p>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {[0, 1, 2, 3].map((row) => (
          <div key={row} className="h-[118px] animate-pulse rounded-xl border border-line/60 bg-surface/40" />
        ))}
      </div>
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.7fr)_minmax(0,1fr)]">
        <div className="h-[280px] animate-pulse rounded-xl border border-line/60 bg-surface/40" />
        <div className="h-[280px] animate-pulse rounded-xl border border-line/60 bg-surface/40" />
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        {[0, 1, 2].map((row) => (
          <div key={row} className="h-[240px] animate-pulse rounded-xl border border-line/60 bg-surface/40" />
        ))}
      </div>
    </div>
  );
}
