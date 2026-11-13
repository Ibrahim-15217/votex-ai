import { useEffect, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { IncidentTable } from "../components/IncidentTable";
import {
  ActivityIcon,
  AlertTriangleIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  DatabaseIcon,
  InboxIcon,
  LockIcon,
  NetworkIcon,
  PlusIcon,
  ShieldCheckIcon,
  UsersIcon,
} from "../components/icons";
import {
  Card,
  CardHeader,
  Notice,
  PageHeader,
  Spinner,
  StatusPill,
  VerifiedPill,
  cn,
} from "../components/ui";
import { api, type AuditVerifyResult, type IncidentListItem, type IncidentStats } from "../lib/api";
import { shortHash } from "../lib/format";
import { useI18n, type TranslationKey } from "../lib/i18n";

const pipeline = [
  "submitted",
  "under_review",
  "assigned",
  "investigating",
  "escalated",
  "contained",
  "closed",
];

const barTones: Record<string, string> = {
  submitted: "bg-muted/60",
  under_review: "bg-brand",
  assigned: "bg-violet",
  investigating: "bg-brand-2",
  escalated: "bg-warning",
  contained: "bg-success",
  remediated: "bg-success",
  recovered: "bg-success",
  closed: "bg-muted/40",
};

const pipelineSteps: Array<{ label: TranslationKey; body: TranslationKey }> = [
  { label: "overview.stepReport", body: "overview.stepReportBody" },
  { label: "overview.stepTriage", body: "overview.stepTriageBody" },
  { label: "overview.stepRespond", body: "overview.stepRespondBody" },
  { label: "overview.stepAi", body: "overview.stepAiBody" },
  { label: "overview.stepCorrelation", body: "overview.stepCorrelationBody" },
  { label: "overview.stepAudit", body: "overview.stepAuditBody" },
];

const evidenceRows: Array<{
  icon: ReactNode;
  title: TranslationKey;
  body: TranslationKey;
}> = [
  {
    icon: <DatabaseIcon className="h-4 w-4" />,
    title: "overview.privacy1Title",
    body: "overview.privacy1Body",
  },
  {
    icon: <LockIcon className="h-4 w-4" />,
    title: "overview.privacy2Title",
    body: "overview.privacy2Body",
  },
  {
    icon: <NetworkIcon className="h-4 w-4" />,
    title: "overview.privacy3Title",
    body: "overview.privacy3Body",
  },
  {
    icon: <ActivityIcon className="h-4 w-4" />,
    title: "overview.privacy4Title",
    body: "overview.privacy4Body",
  },
];

function greetingKey(): TranslationKey {
  const hour = new Date().getHours();
  if (hour < 12) return "greeting.morning";
  if (hour < 17) return "greeting.afternoon";
  return "greeting.evening";
}

export default function OverviewPage() {
  const { user } = useAuth();
  const { t } = useI18n();
  const [stats, setStats] = useState<IncidentStats | null>(null);
  const [recent, setRecent] = useState<IncidentListItem[]>([]);
  const [verification, setVerification] = useState<AuditVerifyResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [verificationError, setVerificationError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const isAnalyst = user?.role === "admin" || user?.role === "analyst";

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    setVerificationError(null);

    const tasks: Promise<unknown>[] = [
      api.stats().then((value) => active && setStats(value)),
      api.incidents({ page_size: 5 }).then((page) => active && setRecent(page.items)),
    ];
    if (isAnalyst) {
      tasks.push(
        api
          .verifyAudit()
          .then((value) => active && setVerification(value))
          .catch((err: unknown) => {
            if (active) {
              setVerificationError(
                err instanceof Error ? err.message : t("overview.auditUnavailable"),
              );
            }
          }),
      );
    }

    Promise.all(tasks)
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : t("common.loadError"));
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [isAnalyst, t, reloadKey]);

  const firstName = user?.full_name.split(" ")[0] ?? "";

  return (
    <div className="animate-rise space-y-6">
      <PageHeader
        title={`${t(greetingKey())}, ${firstName}`}
        description={t("overview.description")}
        actions={
          <>
            <Link
              to="/incidents"
              className="inline-flex min-h-[42px] items-center gap-2 rounded-lg border border-line bg-surface/60 px-4 py-2.5 text-sm font-medium text-text transition hover:border-brand/40 hover:bg-surface-2"
            >
              <InboxIcon aria-hidden="true" className="h-4 w-4" />
              {t("overview.openQueue")}
            </Link>
            <Link
              to="/report"
              className="inline-flex min-h-[42px] items-center gap-2 rounded-lg bg-gradient-to-r from-brand to-brand-2 px-4 py-2.5 text-sm font-semibold text-void shadow-glow transition hover:brightness-110"
            >
              <PlusIcon aria-hidden="true" className="h-4 w-4" />
              {t("overview.reportIncident")}
            </Link>
          </>
        }
      />

      {error && <Notice>{error}</Notice>}

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          icon={<InboxIcon className="h-4 w-4" />}
          label={t("overview.statOpen")}
          value={stats ? String(stats.open) : "—"}
          note={
            stats
              ? t("overview.statOpenNote", { count: stats.last_7_days })
              : error
                ? t("common.unavailable")
                : t("overview.statOpenLoading")
          }
          tone="text-brand"
        />
        <StatCard
          icon={<AlertTriangleIcon className="h-4 w-4" />}
          label={t("overview.statCritical")}
          value={stats ? String(stats.critical) : "—"}
          note={t("overview.statCriticalNote")}
          tone="text-critical"
        />
        <StatCard
          icon={<UsersIcon className="h-4 w-4" />}
          label={t("overview.statAwaiting")}
          value={stats ? String(stats.unassigned) : "—"}
          note={t("overview.statAwaitingNote")}
          tone="text-warning"
        />
        <StatCard
          icon={<ShieldCheckIcon className="h-4 w-4" />}
          label={t("overview.statAudit")}
          value={
            verification
              ? verification.valid
                ? t("overview.statAuditValid")
                : t("overview.statAuditBroken")
              : isAnalyst
                ? "—"
                : t("overview.statAuditLimited")
          }
          note={
            verification
              ? t("overview.statAuditEntries", { count: verification.entries_checked })
              : isAnalyst
                ? verificationError
                  ? t("common.unavailable")
                  : t("overview.statAuditVerifying")
                : t("overview.statAuditAnalystOnly")
          }
          tone={
            verification
              ? verification.valid
                ? "text-success"
                : "text-danger"
              : verificationError
                ? "text-danger"
                : "text-muted"
          }
        />
      </div>

      {verificationError && (
        <div
          role="alert"
          className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-warning/25 bg-warning/[0.08] px-3 py-2.5 text-[11.5px] leading-relaxed text-warning"
        >
          <span>{t("overview.auditUnavailable")}</span>
          <button
            type="button"
            onClick={() => setReloadKey((value) => value + 1)}
            className="font-semibold underline underline-offset-2 transition hover:text-warning/80"
          >
            {t("common.retry")}
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
        <Card>
          <CardHeader
            title={t("overview.recentTitle")}
            description={t("overview.recentDescription")}
            action={
              <Link
                to="/incidents"
                className="inline-flex items-center gap-1.5 text-[11px] font-medium text-brand transition hover:text-brand/80"
              >
                {t("overview.viewAll")}
                <ArrowRightIcon aria-hidden="true" className="h-3.5 w-3.5" />
              </Link>
            }
          />
          {loading && recent.length === 0 ? (
            <div className="space-y-3 px-5 py-6" aria-busy="true" aria-label={t("common.loading")}>
              {[0, 1, 2].map((row) => (
                <div key={row} className="h-12 animate-pulse rounded-lg bg-surface-2/60" />
              ))}
            </div>
          ) : error && recent.length === 0 ? (
            <div className="px-5 py-10 text-center text-xs text-muted">{t("common.loadError")}</div>
          ) : recent.length === 0 ? (
            <div className="px-5 py-10 text-center text-xs text-muted">
              {t("overview.noIncidents")}{" "}
              <Link to="/report" className="text-brand hover:underline">
                {t("overview.reportFirst")}
              </Link>
            </div>
          ) : (
            <IncidentTable incidents={recent} showReporter={!isAnalyst} />
          )}
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader
              title={t("overview.statusTitle")}
              description={t("overview.statusDescription")}
            />
            <div className="space-y-2.5 px-5 py-4">
              {stats && stats.total > 0 ? (
                pipeline
                  .filter((status) => (stats.by_status[status] ?? 0) > 0)
                  .map((status) => {
                    const count = stats.by_status[status] ?? 0;
                    const max = Math.max(...Object.values(stats.by_status), 1);
                    return (
                      <div key={status} className="flex items-center gap-3">
                        <span className="w-28 shrink-0">
                          <StatusPill status={status} />
                        </span>
                        <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-surface-2">
                          <span
                            className={cn("block h-full rounded-full", barTones[status] ?? "bg-brand")}
                            style={{ width: `${Math.max((count / max) * 100, 4)}%` }}
                          />
                        </span>
                        <span className="w-5 text-right font-mono text-[10.5px] text-muted">
                          {count}
                        </span>
                      </div>
                    );
                  })
              ) : (
                <p className="py-6 text-center text-xs text-muted">{t("overview.countersEmpty")}</p>
              )}
              {stats && stats.average_risk !== null && (
                <div className="mt-4 flex items-center justify-between border-t border-line/60 pt-3 text-[11px]">
                  <span className="text-muted">{t("overview.meanRisk")}</span>
                  <span className="font-mono font-semibold text-text">
                    {stats.average_risk.toFixed(1)} / 100
                  </span>
                </div>
              )}
            </div>
          </Card>

          <Card>
            <CardHeader
              title={t("overview.auditTitle")}
              description={t("overview.auditDescription")}
              action={verification ? <VerifiedPill valid={verification.valid} /> : undefined}
            />
            <div className="px-5 py-4">
              {isAnalyst ? (
                verification ? (
                  <>
                    <p className="text-[11.5px] leading-relaxed text-muted">{verification.message}</p>
                    <dl className="mt-3 space-y-2 text-[10.5px]">
                      <div className="flex items-center justify-between gap-3">
                        <dt className="text-muted">{t("overview.entriesChecked")}</dt>
                        <dd className="font-mono text-text">{verification.entries_checked}</dd>
                      </div>
                      <div className="flex items-center justify-between gap-3">
                        <dt className="text-muted">{t("overview.latestHash")}</dt>
                        <dd
                          className="font-mono text-brand"
                          title={verification.latest_hash ?? ""}
                        >
                          {shortHash(verification.latest_hash)}
                        </dd>
                      </div>
                    </dl>
                    <Link
                      to="/audit"
                      className="mt-4 inline-flex items-center gap-1.5 text-[11px] font-medium text-brand transition hover:text-brand/80"
                    >
                      {t("overview.inspectChain")}
                      <ArrowRightIcon aria-hidden="true" className="h-3.5 w-3.5" />
                    </Link>
                  </>
                ) : verificationError ? (
                  <div className="py-3">
                    <p className="text-[11.5px] leading-relaxed text-muted">
                      {t("overview.auditUnavailable")}
                    </p>
                    <button
                      type="button"
                      onClick={() => setReloadKey((value) => value + 1)}
                      className="mt-2 rounded text-[11px] font-semibold text-brand transition hover:text-brand/80"
                    >
                      {t("common.retry")}
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 py-4 text-[11.5px] text-muted">
                    <Spinner className="text-brand" />
                    {t("overview.recomputing")}
                  </div>
                )
              ) : (
                <p className="py-3 text-[11.5px] leading-relaxed text-muted">
                  {t("overview.auditReporterNote")}
                </p>
              )}
            </div>
          </Card>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1.35fr)_minmax(0,1fr)]">
        <Card>
          <CardHeader
            title={t("overview.pipelineTitle")}
            description={t("overview.pipelineDescription")}
          />
          <ol className="grid gap-2 px-5 py-4 sm:grid-cols-3">
            {pipelineSteps.map((step) => (
              <li
                key={step.label}
                className="rounded-lg border border-success/20 bg-success/[0.04] px-3 py-3"
              >
                <span className="inline-flex items-center gap-1.5 text-[10px] font-semibold text-success">
                  <CheckCircleIcon aria-hidden="true" className="h-3.5 w-3.5" />
                  {t("overview.pipelineLive")}
                </span>
                <p className="mt-1.5 text-xs font-semibold text-text">{t(step.label)}</p>
                <p className="mt-0.5 text-[10.5px] leading-relaxed text-muted">{t(step.body)}</p>
              </li>
            ))}
          </ol>
        </Card>

        <Card>
          <CardHeader
            title={t("overview.privacyTitle")}
            description={t("overview.privacyDescription")}
          />
          <ul className="divide-y divide-line/50">
            {evidenceRows.map((row) => (
              <EvidenceRow
                key={row.title}
                icon={row.icon}
                title={t(row.title)}
                body={t(row.body)}
              />
            ))}
          </ul>
        </Card>
      </div>
    </div>
  );
}

function StatCard({
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
        <span
          aria-hidden="true"
          className={cn("grid h-8 w-8 place-items-center rounded-lg border border-line bg-void/50", tone)}
        >
          {icon}
        </span>
        <span className="text-[9.5px] font-semibold uppercase tracking-[0.14em] text-muted">
          {label}
        </span>
      </div>
      <p className={cn("mt-3 font-mono text-2xl font-semibold leading-none", tone)}>{value}</p>
      <p className="mt-1.5 text-[10.5px] leading-relaxed text-muted">{note}</p>
    </div>
  );
}

function EvidenceRow({ icon, title, body }: { icon: ReactNode; title: string; body: string }) {
  return (
    <li className="flex gap-3 px-5 py-3.5">
      <span
        aria-hidden="true"
        className="mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-lg border border-line bg-void/50 text-brand"
      >
        {icon}
      </span>
      <div>
        <p className="text-xs font-semibold text-text">{title}</p>
        <p className="mt-0.5 text-[10.5px] leading-relaxed text-muted">{body}</p>
      </div>
    </li>
  );
}
