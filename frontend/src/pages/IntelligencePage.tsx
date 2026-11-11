import { useEffect, useMemo, useState, type ReactNode } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  DownloadIcon,
  FilterIcon,
  InboxIcon,
  NetworkIcon,
  SearchIcon,
  ShieldCheckIcon,
} from "../components/icons";
import {
  Card,
  CardHeader,
  EmptyState,
  IndicatorKindPill,
  Notice,
  PageHeader,
  RiskScore,
  Spinner,
  StatusPill,
  btnPrimary,
  btnSubtle,
  cn,
} from "../components/ui";
import {
  api,
  downloadCsv,
  type IndicatorDetail,
  type IndicatorKind,
  type IndicatorPage,
} from "../lib/api";
import { formatDateTime, relativeTime } from "../lib/format";
import { useI18n } from "../lib/i18n";

const KIND_FILTERS: Array<{ value: IndicatorKind | "all"; label: string }> = [
  { value: "all", label: "All kinds" },
  { value: "url", label: "URLs" },
  { value: "domain", label: "Domains" },
  { value: "ipv4", label: "IPv4" },
  { value: "sha256", label: "SHA-256" },
  { value: "md5", label: "MD5" },
];

const SOURCE_LABELS: Record<string, string> = {
  reported_url: "Reported URL",
  description: "Report text",
  evidence: "Evidence",
};

const PAGE_SIZE = 20;

export default function IntelligencePage() {
  const { user } = useAuth();
  const { t } = useI18n();
  const isAnalyst = user?.role === "admin" || user?.role === "analyst";
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get("q") ?? "";

  const [query, setQuery] = useState(initialQuery);
  const [debounced, setDebounced] = useState(initialQuery.trim());
  const [kind, setKind] = useState<IndicatorKind | "all">("all");
  const [page, setPage] = useState(1);
  const [data, setData] = useState<IndicatorPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<IndicatorDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(query.trim()), 260);
    return () => window.clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    setQuery(initialQuery);
    setDebounced(initialQuery.trim());
    setPage(1);
  }, [initialQuery]);

  useEffect(() => {
    if (!isAnalyst) {
      setLoading(false);
      return;
    }
    let active = true;
    setLoading(true);
    setError(null);

    api
      .indicators({
        q: debounced || undefined,
        kind: kind === "all" ? undefined : kind,
        page,
        page_size: PAGE_SIZE,
      })
      .then((value) => {
        if (!active) return;
        setData(value);
        setSelectedId((current) =>
          current && value.items.some((item) => item.id === current) ? current : value.items[0]?.id ?? null,
        );
      })
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : "Could not load indicators.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [debounced, kind, page, isAnalyst]);

  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      return;
    }
    let active = true;
    setDetailLoading(true);
    setDetail(null);

    api
      .indicator(selectedId)
      .then((value) => {
        if (active) setDetail(value);
      })
      .catch(() => {
        if (active) setDetail(null);
      })
      .finally(() => {
        if (active) setDetailLoading(false);
      });

    return () => {
      active = false;
    };
  }, [selectedId]);

  const kindCounts = data?.by_kind ?? {};
  const totalIndicators = useMemo(
    () => Object.values(kindCounts).reduce((sum, value) => sum + value, 0),
    [kindCounts],
  );
  const totalPages = Math.max(1, Math.ceil((data?.total ?? 0) / PAGE_SIZE));

  async function handleExport() {
    setExporting(true);
    setFeedback(null);
    try {
      const params = new URLSearchParams();
      if (debounced) params.set("q", debounced);
      if (kind !== "all") params.set("kind", kind);
      const suffix = params.toString();
      const filename = await downloadCsv(
        `/indicators/export${suffix ? `?${suffix}` : ""}`,
        "votex-indicators.csv",
      );
      setFeedback(`Exported ${filename}. The export is permission-checked and recorded on the audit chain.`);
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
          eyebrow="Phase 3 · Threat intelligence"
          title="Indicator intelligence"
          description="Correlation is available to administrators and analysts in the response team."
        />
        <Notice tone="info">
          Your role can report incidents and follow the case you submitted. Ask an analyst in your organisation for the
          correlated intelligence view.
        </Notice>
      </div>
    );
  }

  return (
    <div className="animate-rise space-y-5">
      <PageHeader
        eyebrow="Phase 3 · Correlation live"
        title="Indicator intelligence"
        description="Deterministic correlation of URLs, domains, IP addresses and file hashes across your organisation. Extraction never visits a link, and every result stays inside your tenant."
        actions={
          <button
            type="button"
            onClick={() => void handleExport()}
            className={btnPrimary}
            disabled={exporting || (data?.total ?? 0) === 0}
          >
            {exporting ? <Spinner className="h-4 w-4" /> : <DownloadIcon className="h-4 w-4" />}
            Export CSV
          </button>
        }
      />

      <p className="rounded-lg border border-line/70 bg-surface/40 px-3.5 py-2.5 text-[10.5px] leading-relaxed text-muted">
        {t("common.englishOnly")}
      </p>

      {feedback && <Notice tone="success">{feedback}</Notice>}
      {error && <Notice>{error}</Notice>}

      <div className="grid gap-3 sm:grid-cols-3">
        <SummaryTile
          icon={<NetworkIcon className="h-4 w-4" />}
          label="Indicators in tenant"
          value={String(totalIndicators)}
          note="Deduplicated across every case"
          tone="text-brand"
        />
        <SummaryTile
          icon={<SearchIcon className="h-4 w-4" />}
          label="Matching filter"
          value={String(data?.total ?? 0)}
          note={debounced ? `Search: “${debounced}”` : "All indicator values"}
          tone="text-violet"
        />
        <SummaryTile
          icon={<ShieldCheckIcon className="h-4 w-4" />}
          label="Scope"
          value="Tenant"
          note="Cross-organisation matches are never exposed"
          tone="text-success"
        />
      </div>

      <Card>
        <div className="space-y-3 px-4 py-3.5 sm:px-5">
          <div className="flex items-center gap-2.5 rounded-lg border border-line bg-void/60 px-3 py-2 transition focus-within:border-brand/60 focus-within:ring-2 focus-within:ring-brand/20">
            <SearchIcon className="h-4 w-4 shrink-0 text-muted/80" />
            <input
              value={query}
              onChange={(event) => {
                setQuery(event.target.value);
                setPage(1);
              }}
              placeholder="Search a domain, URL, IP address or file hash…"
              className="w-full bg-transparent font-mono text-[12px] text-text placeholder:font-sans placeholder:text-muted/80 focus:outline-none"
              maxLength={160}
              aria-label="Search indicators"
            />
            {query && (
              <button
                type="button"
                onClick={() => {
                  setQuery("");
                  setPage(1);
                }}
                className="shrink-0 text-[10px] font-medium text-muted transition hover:text-text"
              >
                Clear
              </button>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-1.5">
            <span className="mr-1 inline-flex items-center gap-1.5 text-[9.5px] font-semibold uppercase tracking-[0.14em] text-muted/80">
              <FilterIcon className="h-3 w-3" />
              Kind
            </span>
            {KIND_FILTERS.map((filter) => {
              const count = filter.value === "all" ? totalIndicators : kindCounts[filter.value] ?? 0;
              const active = kind === filter.value;
              return (
                <button
                  key={filter.value}
                  type="button"
                  onClick={() => {
                    setKind(filter.value);
                    setPage(1);
                  }}
                  aria-pressed={active}
                  className={cn(
                    "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10.5px] font-medium transition",
                    active
                      ? "border-brand/35 bg-brand/12 text-brand"
                      : "border-line bg-void/40 text-muted hover:border-brand/25 hover:text-text",
                  )}
                >
                  {filter.label}
                  <span className={cn("font-mono text-[9px]", active ? "text-brand/80" : "text-muted/80")}>
                    {count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.05fr)_minmax(0,1fr)]">
        <Card className="overflow-hidden">
          <CardHeader
            title="Indicator index"
            description="Busiest indicators first. Counts reflect linked incidents in your organisation."
            action={
              <span className="rounded-full border border-line bg-void/40 px-2 py-0.5 font-mono text-[10px] text-muted">
                {data?.total ?? 0}
              </span>
            }
          />

          {loading ? (
            <div className="space-y-2 px-4 py-4">
              {[0, 1, 2, 3, 4].map((row) => (
                <div key={row} className="h-[68px] animate-pulse rounded-lg bg-surface-2/50" />
              ))}
            </div>
          ) : !data || data.items.length === 0 ? (
            <EmptyState
              title="No indicators match this filter"
              body="Indicators are extracted automatically when a report is submitted, re-analysed or given evidence. Try a broader search."
            />
          ) : (
            <ul className="divide-y divide-line/50">
              {data.items.map((item) => {
                const selected = item.id === selectedId;
                return (
                  <li key={item.id}>
                    <button
                      type="button"
                      onClick={() => setSelectedId(item.id)}
                      className={cn(
                        "w-full border-l-2 px-4 py-3 text-left transition sm:px-5",
                        selected
                          ? "border-l-brand bg-brand/[0.06]"
                          : "border-l-transparent hover:bg-surface-2/40",
                      )}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <IndicatorKindPill kind={item.kind} />
                        <span
                          className={cn(
                            "inline-flex items-center gap-1 rounded-full border px-1.5 py-0.5 text-[9.5px] font-medium",
                            item.incident_count > 1
                              ? "border-warning/25 bg-warning/10 text-warning"
                              : "border-line bg-surface-2/60 text-muted",
                          )}
                        >
                          <InboxIcon className="h-2.5 w-2.5" />
                          {item.incident_count} incident{item.incident_count === 1 ? "" : "s"}
                        </span>
                      </div>
                      <p className="mt-1.5 truncate font-mono text-[10.5px] leading-relaxed text-text/85" title={item.display_value}>
                        {item.display_value}
                      </p>
                      <p className="mt-1 flex flex-wrap items-center gap-x-1.5 text-[9.5px] text-muted/80">
                        <span>Last seen {relativeTime(item.last_seen_at)}</span>
                        {item.example_incident_reference && (
                          <>
                            <span className="text-muted/80">·</span>
                            <span className="font-mono text-brand/70">{item.example_incident_reference}</span>
                          </>
                        )}
                      </p>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}

          <div className="flex items-center justify-between gap-2 border-t border-line/70 px-4 py-3">
            <span className="text-[10px] text-muted/80">
              Page {data?.page ?? 1} of {totalPages}
            </span>
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => setPage((value) => Math.max(1, value - 1))}
                disabled={page <= 1 || loading}
                className={btnSubtle}
                aria-label="Previous page"
              >
                <ChevronLeftIcon className="h-3.5 w-3.5" />
                Previous
              </button>
              <button
                type="button"
                onClick={() => setPage((value) => Math.min(totalPages, value + 1))}
                disabled={page >= totalPages || loading}
                className={btnSubtle}
                aria-label="Next page"
              >
                Next
                <ChevronRightIcon className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </Card>

        <IndicatorDetailPanel
          detail={detail}
          loading={detailLoading}
          hasSelection={selectedId !== null}
        />
      </div>
    </div>
  );
}

function IndicatorDetailPanel({
  detail,
  loading,
  hasSelection,
}: {
  detail: IndicatorDetail | null;
  loading: boolean;
  hasSelection: boolean;
}) {
  if (!hasSelection) {
    return (
      <Card>
        <EmptyState
          title="Select an indicator"
          body="Choose a row to see every incident linked to that URL, domain, IP address or file hash."
        />
      </Card>
    );
  }

  if (loading || !detail) {
    return (
      <Card>
        <div className="flex min-h-[240px] items-center justify-center gap-2.5 text-xs text-muted">
          <Spinner className="text-brand" />
          Loading correlated cases
        </div>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader
        title="Linked incidents"
        description="Every visible case in your organisation that shares this exact, normalised value."
        action={
          <span className="rounded-full border border-brand/25 bg-brand/[0.08] px-2 py-0.5 font-mono text-[10px] text-brand">
            {detail.incidents.length} linked
          </span>
        }
      />

      <div className="border-b border-line/70 px-5 py-4">
        <div className="flex flex-wrap items-center gap-2">
          <IndicatorKindPill kind={detail.kind} />
          <span className="text-[9.5px] uppercase tracking-[0.12em] text-muted/80">
            indicator #{detail.id}
          </span>
        </div>
        <p className="mt-2.5 break-all rounded-lg border border-line/70 bg-void/50 px-3 py-2.5 font-mono text-[11px] leading-relaxed text-text/90">
          {detail.value}
        </p>
        <dl className="mt-3 grid grid-cols-2 gap-3 text-[10px]">
          <div>
            <dt className="text-[8.5px] font-semibold uppercase tracking-[0.14em] text-muted/80">First seen</dt>
            <dd className="mt-0.5 text-text/85">{formatDateTime(detail.first_seen_at)}</dd>
          </div>
          <div>
            <dt className="text-[8.5px] font-semibold uppercase tracking-[0.14em] text-muted/80">Last seen</dt>
            <dd className="mt-0.5 text-text/85">{formatDateTime(detail.last_seen_at)}</dd>
          </div>
        </dl>
      </div>

      {detail.incidents.length === 0 ? (
        <p className="px-5 py-8 text-center text-[11px] text-muted/80">
          This indicator is no longer linked to a visible incident.
        </p>
      ) : (
        <ul className="divide-y divide-line/50">
          {detail.incidents.map((incident) => (
            <li key={incident.id}>
              <Link to={`/incidents/${incident.id}`} className="block px-5 py-3.5 transition hover:bg-surface-2/40">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-mono text-[10px] text-brand/90">{incident.reference}</span>
                  <span className="inline-flex items-center gap-1.5 text-[9px] text-muted/80">
                    {SOURCE_LABELS[incident.link_source] ?? incident.link_source}
                    <span className="text-muted/80">·</span>
                    {relativeTime(incident.first_seen_at)}
                  </span>
                </div>
                <p className="mt-1 line-clamp-1 text-[11.5px] font-medium text-text/90">{incident.title}</p>
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  <StatusPill status={incident.status} />
                  <RiskScore score={incident.risk_score} />
                  <span className="text-[9.5px] text-muted/80">
                    {incident.assignee_name ? `Owner ${incident.assignee_name}` : "Unassigned"}
                  </span>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}

      <div className="flex flex-wrap items-center gap-2 border-t border-line/70 bg-void/30 px-5 py-2.5">
        <ShieldCheckIcon className="h-3.5 w-3.5 text-success/80" />
        <p className="text-[9.5px] leading-relaxed text-muted/80">
          Matching uses normalised values from the same tenant. Reporters only ever see their own reports.
        </p>
      </div>
    </Card>
  );
}

function SummaryTile({
  icon,
  label,
  value,
  note,
  tone,
}: {
  icon: ReactNode;
  label: string;
  value: string;
  note: string;
  tone: string;
}) {
  return (
    <div className="rounded-xl border border-line/80 bg-surface/50 p-4 shadow-panel backdrop-blur-sm">
      <div className="flex items-center justify-between gap-2">
        <span className={cn("grid h-8 w-8 place-items-center rounded-lg border border-line bg-void/50", tone)}>{icon}</span>
        <span className="text-[9px] font-semibold uppercase tracking-[0.14em] text-muted/80">{label}</span>
      </div>
      <p className={cn("mt-3 font-mono text-2xl font-semibold leading-none", tone)}>{value}</p>
      <p className="mt-1.5 line-clamp-2 text-[10px] leading-relaxed text-muted/80">{note}</p>
    </div>
  );
}
