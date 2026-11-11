import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { IncidentTable } from "../components/IncidentTable";
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  InboxIcon,
  PlusIcon,
  RefreshIcon,
  SearchIcon,
} from "../components/icons";
import {
  Card,
  EmptyState,
  Notice,
  PageHeader,
  Spinner,
  btnGhost,
  btnPrimary,
  inputClass,
  selectClass,
} from "../components/ui";
import { api, type IncidentPage } from "../lib/api";
import { useI18n, type TranslationKey } from "../lib/i18n";

const statusValues = [
  "",
  "submitted",
  "under_review",
  "assigned",
  "investigating",
  "escalated",
  "contained",
  "remediated",
  "recovered",
  "closed",
];

const priorityValues = ["", "critical", "high", "medium", "low"];

export default function IncidentsPage() {
  const { user } = useAuth();
  const { t } = useI18n();
  const [data, setData] = useState<IncidentPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [assignedToMe, setAssignedToMe] = useState(false);
  const [page, setPage] = useState(1);
  const [reloadKey, setReloadKey] = useState(0);

  const isAnalyst = user?.role === "admin" || user?.role === "analyst";

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearch(query.trim());
      setPage(1);
    }, 300);
    return () => window.clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    api
      .incidents({
        search: search || undefined,
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
        assigned_to_me: isAnalyst ? assignedToMe : undefined,
        page,
        page_size: 15,
      })
      .then((value) => {
        if (active) setData(value);
      })
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : t("common.loadError"));
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [search, statusFilter, priorityFilter, assignedToMe, page, isAnalyst, reloadKey, t]);

  const total = data?.total ?? 0;
  const pageSize = data?.page_size ?? 15;
  const from = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const filtersActive = Boolean(search || statusFilter || priorityFilter || assignedToMe);

  function resetFilters() {
    setQuery("");
    setSearch("");
    setStatusFilter("");
    setPriorityFilter("");
    setAssignedToMe(false);
    setPage(1);
  }

  const optionLabel = (value: string) => {
    if (!value) return t("common.allStatuses");
    return t(`status.${value}` as TranslationKey);
  };

  const priorityLabel = (value: string) => {
    if (!value) return t("common.allPriorities");
    return t(`priority.${value}` as TranslationKey);
  };

  return (
    <div className="animate-rise space-y-5">
      <PageHeader
        eyebrow={t("queue.eyebrow")}
        title={t("queue.title")}
        description={isAnalyst ? t("queue.descriptionAnalyst") : t("queue.descriptionReporter")}
        actions={
          <>
            <button
              type="button"
              onClick={() => setReloadKey((value) => value + 1)}
              className={btnGhost}
              disabled={loading}
            >
              <RefreshIcon className="h-4 w-4" />
              {t("common.refresh")}
            </button>
            <Link to="/report" className={btnPrimary}>
              <PlusIcon className="h-4 w-4" />
              {t("queue.reportIncident")}
            </Link>
          </>
        }
      />

      <Card>
        <div className="flex flex-wrap items-center gap-2.5 border-b border-line/70 px-4 py-3.5">
          <div className="relative min-w-[220px] flex-1">
            <SearchIcon
              aria-hidden="true"
              className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted"
            />
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={t("queue.searchPlaceholder")}
              className={`${inputClass} pl-9`}
              aria-label={t("queue.searchLabel")}
            />
          </div>

          <select
            value={statusFilter}
            onChange={(event) => {
              setStatusFilter(event.target.value);
              setPage(1);
            }}
            className={`${selectClass} w-auto min-w-[150px]`}
            aria-label={t("queue.filterStatus")}
          >
            {statusValues.map((value) => (
              <option key={value || "all"} value={value}>
                {optionLabel(value)}
              </option>
            ))}
          </select>

          <select
            value={priorityFilter}
            onChange={(event) => {
              setPriorityFilter(event.target.value);
              setPage(1);
            }}
            className={`${selectClass} w-auto min-w-[150px]`}
            aria-label={t("queue.filterPriority")}
          >
            {priorityValues.map((value) => (
              <option key={value || "all"} value={value}>
                {priorityLabel(value)}
              </option>
            ))}
          </select>

          {isAnalyst && (
            <label className="inline-flex min-h-[42px] cursor-pointer items-center gap-2 rounded-lg border border-line bg-void/40 px-3 py-2.5 text-[11.5px] text-muted transition hover:text-text">
              <input
                type="checkbox"
                checked={assignedToMe}
                onChange={(event) => {
                  setAssignedToMe(event.target.checked);
                  setPage(1);
                }}
                className="h-4 w-4 accent-brand"
              />
              {t("queue.assignedToMe")}
            </label>
          )}

          {filtersActive && (
            <button
              type="button"
              onClick={resetFilters}
              className="min-h-[42px] rounded text-[11px] font-medium text-brand hover:text-brand/80"
            >
              {t("queue.clearFilters")}
            </button>
          )}
        </div>

        {error && (
          <div className="px-4 py-3">
            <Notice>{error}</Notice>
          </div>
        )}

        {loading && !data ? (
          <div className="space-y-2 p-4" aria-busy="true" aria-label={t("common.loading")}>
            {[0, 1, 2, 3, 4].map((row) => (
              <div key={row} className="h-14 animate-pulse rounded-lg bg-surface-2/60" />
            ))}
          </div>
        ) : data && data.items.length > 0 ? (
          <IncidentTable incidents={data.items} showReporter={!isAnalyst} />
        ) : (
          <EmptyState
            title={filtersActive ? t("queue.noMatchTitle") : t("queue.emptyTitle")}
            body={filtersActive ? t("queue.noMatchBody") : t("queue.emptyBody")}
            action={
              filtersActive ? (
                <button type="button" onClick={resetFilters} className={btnGhost}>
                  {t("queue.clearFilters")}
                </button>
              ) : (
                <Link to="/report" className={btnPrimary}>
                  <PlusIcon className="h-4 w-4" />
                  {t("queue.reportIncident")}
                </Link>
              )
            }
          />
        )}

        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line/70 px-4 py-3">
          <p className="inline-flex items-center gap-2 text-[10.5px] text-muted" aria-live="polite">
            <InboxIcon aria-hidden="true" className="h-3.5 w-3.5" />
            {loading ? (
              <>
                <Spinner className="text-brand" /> {t("queue.updating")}
              </>
            ) : (
              t("queue.showing", { from, to, total })
            )}
          </p>

          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={() => setPage((value) => Math.max(1, value - 1))}
              disabled={page <= 1 || loading}
              className="inline-flex min-h-[32px] items-center gap-1 rounded-md border border-line bg-void/40 px-2.5 py-1.5 text-[11px] text-muted transition hover:text-text disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeftIcon aria-hidden="true" className="h-3.5 w-3.5" />
              {t("common.previous")}
            </button>
            <span className="px-2 font-mono text-[10.5px] text-muted">
              {page} / {totalPages}
            </span>
            <button
              type="button"
              onClick={() => setPage((value) => Math.min(totalPages, value + 1))}
              disabled={page >= totalPages || loading}
              className="inline-flex min-h-[32px] items-center gap-1 rounded-md border border-line bg-void/40 px-2.5 py-1.5 text-[11px] text-muted transition hover:text-text disabled:cursor-not-allowed disabled:opacity-40"
            >
              {t("common.next")}
              <ChevronRightIcon aria-hidden="true" className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
}
