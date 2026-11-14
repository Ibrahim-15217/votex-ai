import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import {
  AlertTriangleIcon,
  CheckCircleIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CopyIcon,
  LockIcon,
  RefreshIcon,
  ShieldCheckIcon,
} from "../components/icons";
import {
  Card,
  CardHeader,
  EmptyState,
  EnglishOnlyBadge,
  ErrorState,
  Notice,
  PageHeader,
  Spinner,
  VerifiedPill,
  btnGhost,
  btnPrimary,
  selectClass,
} from "../components/ui";
import { api, type AuditPage as AuditPageData, type AuditVerifyResult } from "../lib/api";
import { formatDateTime, humanise, shortHash } from "../lib/format";

const actionOptions = [
  ["", "All actions"],
  ["auth.login", "Sign in"],
  ["auth.login_failed", "Failed sign in"],
  ["incident.created", "Incident created"],
  ["incident.status_changed", "Status changed"],
  ["incident.assigned", "Incident assigned"],
  ["incident.priority_changed", "Priority changed"],
  ["incident.comment_added", "Note added"],
  ["incident.response_recorded", "Response recorded"],
  ["incident.analysed", "AI analysis recorded"],
  ["evidence.uploaded", "Evidence uploaded"],
  ["evidence.downloaded", "Evidence downloaded"],
  ["intelligence.exported", "Intelligence exported"],
];

export default function AuditPage() {
  const { user } = useAuth();
  const isAnalyst = user?.role === "admin" || user?.role === "analyst";

  const [data, setData] = useState<AuditPageData | null>(null);
  const [verification, setVerification] = useState<AuditVerifyResult | null>(null);
  const [verificationError, setVerificationError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [actionFilter, setActionFilter] = useState("");
  const [page, setPage] = useState(1);
  const [copied, setCopied] = useState<number | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!isAnalyst) return;
    let active = true;
    setLoading(true);
    setError(null);

    api
      .audit({ action: actionFilter || undefined, page, page_size: 25 })
      .then((value) => {
        if (active) setData(value);
      })
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : "Could not load the audit chain.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [isAnalyst, actionFilter, page, reloadKey]);

  useEffect(() => {
    if (!isAnalyst) return;
    let active = true;
    setVerificationError(null);
    api
      .verifyAudit()
      .then((value) => {
        if (active) setVerification(value);
      })
      .catch((err: unknown) => {
        if (active) {
          setVerificationError(
            err instanceof Error ? err.message : "The audit chain could not be verified.",
          );
        }
      });
    return () => {
      active = false;
    };
  }, [isAnalyst, reloadKey]);

  async function verifyNow() {
    setVerifying(true);
    setError(null);
    setNotice(null);
    setVerificationError(null);
    try {
      const result = await api.verifyAudit();
      setVerification(result);
      setNotice(
        result.valid
          ? `Chain verified across ${result.entries_checked} entries.`
          : `Verification failed at entry ${result.first_invalid_id}.`,
      );
    } catch (err) {
      setVerificationError(err instanceof Error ? err.message : "Verification failed.");
    } finally {
      setVerifying(false);
    }
  }

  async function copyHash(hash: string, id: number) {
    try {
      await navigator.clipboard.writeText(hash);
      setCopied(id);
      window.setTimeout(() => setCopied(null), 1600);
    } catch {
      setCopied(null);
    }
  }

  if (!isAnalyst) {
    return (
      <div className="animate-rise space-y-4">
        <PageHeader title="Audit trail" description="The audit chain is available to administrators and analysts." />
        <Notice>
          Your role can submit and follow reports, but cannot browse the organisation audit trail. Your actions are still recorded there.
        </Notice>
        <Link to="/incidents" className={btnGhost}>
          Back to my incidents
        </Link>
      </div>
    );
  }

  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / (data?.page_size ?? 25)));

  return (
    <div className="animate-rise space-y-5">
      <PageHeader
        title="Audit trail"
        description="Every authentication, incident change and evidence access is chained with SHA-256. Verification recomputes the full chain from genesis."
        badge={<EnglishOnlyBadge />}
        actions={
          <>
            <button type="button" onClick={() => setReloadKey((value) => value + 1)} className={btnGhost} disabled={loading}>
              <RefreshIcon className="h-4 w-4" />
              Refresh
            </button>
            <button type="button" onClick={() => void verifyNow()} className={btnPrimary} disabled={verifying}>
              {verifying ? <Spinner /> : <ShieldCheckIcon className="h-4 w-4" />}
              {verifying ? "Recomputing…" : "Verify chain"}
            </button>
          </>
        }
      />

      {error && <Notice>{error}</Notice>}
      {notice && (
        <Notice tone={verification?.valid ? "success" : "error"}>{notice}</Notice>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1.35fr)_minmax(0,1fr)]">
        <Card>
          <CardHeader
            title="Chain status"
            description="A single altered, removed or reordered entry breaks verification."
            action={verification ? <VerifiedPill valid={verification.valid} /> : undefined}
          />
          <div className="px-5 py-4">
            {verification ? (
              <>
                <div className="flex items-start gap-3">
                  <span
                    className={
                      verification.valid
                        ? "mt-0.5 grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-success/25 bg-success/10 text-success"
                        : "mt-0.5 grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-danger/25 bg-danger/10 text-danger"
                    }
                  >
                    {verification.valid ? <CheckCircleIcon className="h-5 w-5" /> : <AlertTriangleIcon className="h-5 w-5" />}
                  </span>
                  <div>
                    <p className="text-xs font-semibold text-text">
                      {verification.valid ? "The record is intact" : "The record has been altered"}
                    </p>
                    <p className="mt-0.5 text-[11px] leading-relaxed text-muted">{verification.message}</p>
                  </div>
                </div>
                <dl className="mt-4 grid grid-cols-2 gap-3 border-t border-line/60 pt-3 text-[10.5px]">
                  <div>
                    <dt className="text-muted/80">Entries checked</dt>
                    <dd className="mt-0.5 font-mono text-text">{verification.entries_checked}</dd>
                  </div>
                  <div>
                    <dt className="text-muted/80">Checked at</dt>
                    <dd className="mt-0.5 text-text">{formatDateTime(verification.checked_at)}</dd>
                  </div>
                  <div className="col-span-2">
                    <dt className="text-muted/80">Latest entry hash</dt>
                    <dd className="mt-0.5 break-all font-mono text-[9.5px] text-brand/90">{verification.latest_hash ?? "—"}</dd>
                  </div>
                  {!verification.valid && verification.first_invalid_id !== null && (
                    <div className="col-span-2">
                      <dt className="text-muted/80">First invalid entry</dt>
                      <dd className="mt-0.5 font-mono text-danger">#{verification.first_invalid_id}</dd>
                    </div>
                  )}
                </dl>
              </>
            ) : verificationError ? (
              <div className="flex flex-col items-start gap-3 py-2">
                <div className="flex items-start gap-3">
                  <span className="mt-0.5 grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-danger/25 bg-danger/10 text-danger">
                    <AlertTriangleIcon className="h-5 w-5" />
                  </span>
                  <div>
                    <p className="text-xs font-semibold text-text">Verification unavailable</p>
                    <p className="mt-0.5 text-[11px] leading-relaxed text-muted">
                      {verificationError}
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setReloadKey((value) => value + 1)}
                  className={btnGhost}
                >
                  <RefreshIcon className="h-4 w-4" />
                  Try again
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2 py-6 text-xs text-muted">
                <Spinner className="text-brand" />
                Verifying the chain
              </div>
            )}
          </div>
        </Card>

        <Card>
          <CardHeader title="What verification checks" description="A single altered, removed or reordered entry breaks the chain." />
          <ul className="divide-y divide-line/50">
            <li className="px-5 py-3 text-[10.5px] leading-relaxed text-muted">
              <span className="font-semibold text-text">Genesis link.</span> The first entry points at 64 zeroes. Every later entry stores the previous entry hash.
            </li>
            <li className="px-5 py-3 text-[10.5px] leading-relaxed text-muted">
              <span className="font-semibold text-text">Content binding.</span> The hash covers the actor, action, resource, detail, timestamp and previous hash.
            </li>
            <li className="px-5 py-3 text-[10.5px] leading-relaxed text-muted">
              <span className="font-semibold text-text">Append-only.</span> Entries are written once; corrections are recorded as new entries, never edits.
            </li>
            <li className="px-5 py-3 text-[10.5px] leading-relaxed text-muted">
              <span className="font-semibold text-text">Evidence access.</span> Every download writes both a timeline event and an audit entry.
            </li>
          </ul>
          <div className="border-t border-line/60 px-5 py-3">
            <p className="inline-flex items-center gap-1.5 text-[10px] text-muted/80">
              <LockIcon className="h-3.5 w-3.5 text-brand/70" />
              Organisation-scoped browsing · full-chain verification
            </p>
          </div>
        </Card>
      </div>

      <Card>
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line/70 px-4 py-3.5">
          <div>
            <h2 className="text-sm font-semibold text-text">Audit entries</h2>
            <p className="mt-0.5 text-[10.5px] text-muted">Newest first, scoped to your organisation.</p>
          </div>
          <select
            value={actionFilter}
            onChange={(event) => {
              setActionFilter(event.target.value);
              setPage(1);
            }}
            className={`${selectClass} w-auto min-w-[180px]`}
            aria-label="Filter audit actions"
          >
            {actionOptions.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {loading && !data ? (
          <div className="space-y-2 p-4">
            {[0, 1, 2, 3, 4].map((row) => (
              <div key={row} className="h-12 animate-pulse rounded-lg bg-surface-2/60" />
            ))}
          </div>
        ) : data && data.items.length > 0 ? (
          <div
            className="overflow-x-auto focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/40"
            tabIndex={0}
            role="region"
            aria-label="Audit entries"
          >
            <table className="w-full min-w-[860px] text-left">
              <thead>
                <tr className="border-b border-line/70 text-[9.5px] uppercase tracking-[0.14em] text-muted/80">
                  <th className="px-4 py-2.5 font-semibold">#</th>
                  <th className="px-3 py-2.5 font-semibold">When</th>
                  <th className="px-3 py-2.5 font-semibold">Action</th>
                  <th className="px-3 py-2.5 font-semibold">Actor</th>
                  <th className="px-3 py-2.5 font-semibold">Resource</th>
                  <th className="px-4 py-2.5 font-semibold">Hash link</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line/50">
                {data.items.map((entry) => (
                  <tr key={entry.id} className="transition hover:bg-surface-2/30">
                    <td className="px-4 py-3 font-mono text-[10px] text-muted/80">{entry.id}</td>
                    <td className="px-3 py-3 text-[10.5px] text-muted">
                      <span className="block">{formatDateTime(entry.created_at)}</span>
                      <span className="mt-0.5 block font-mono text-[9px] text-muted/80">{entry.created_at.slice(11, 19)}Z</span>
                    </td>
                    <td className="px-3 py-3">
                      <span className="block font-mono text-[10.5px] text-brand/90">{entry.action}</span>
                      <span className="mt-0.5 block text-[9.5px] text-muted/80">{detailSummary(entry.detail)}</span>
                    </td>
                    <td className="px-3 py-3 text-[10.5px] text-muted">{entry.actor_email ?? "system"}</td>
                    <td className="px-3 py-3 font-mono text-[9.5px] text-muted/80">
                      {entry.resource_type ?? "—"}
                      {entry.resource_id && <span className="block text-muted/80">{entry.resource_id.slice(0, 8)}…</span>}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        type="button"
                        onClick={() => void copyHash(entry.entry_hash, entry.id)}
                        title={`Previous: ${entry.prev_hash}\nEntry: ${entry.entry_hash}`}
                        className="group inline-flex items-center gap-1 rounded border border-line/70 bg-void/40 px-1.5 py-1 font-mono text-[9px] text-muted/80 transition hover:border-brand/40 hover:text-brand"
                      >
                        <CopyIcon className="h-2.5 w-2.5" />
                        {shortHash(entry.prev_hash, 5)}
                        <span className="text-muted/80">→</span>
                        {copied === entry.id ? "copied" : shortHash(entry.entry_hash, 6)}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : error ? (
          <ErrorState
            title="Audit entries unavailable"
            body={error}
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
        ) : (
          <EmptyState title="No audit entries match this filter" body="Clear the action filter to see the full organisation history." />
        )}

        {!(error && !data) && (
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line/70 px-4 py-3">
          <p className="text-[10.5px] text-muted/80">
            {total} matching entr{total === 1 ? "y" : "ies"} · page {page} of {totalPages}
          </p>
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={() => setPage((value) => Math.max(1, value - 1))}
              disabled={page <= 1 || loading}
              className="inline-flex items-center gap-1 rounded-md border border-line bg-void/40 px-2.5 py-1.5 text-[11px] text-muted transition hover:text-text disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeftIcon className="h-3.5 w-3.5" />
              Previous
            </button>
            <button
              type="button"
              onClick={() => setPage((value) => Math.min(totalPages, value + 1))}
              disabled={page >= totalPages || loading}
              className="inline-flex items-center gap-1 rounded-md border border-line bg-void/40 px-2.5 py-1.5 text-[11px] text-muted transition hover:text-text disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next
              <ChevronRightIcon className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
        )}
      </Card>
    </div>
  );
}

function detailSummary(detail: Record<string, unknown>): string {
  const parts: string[] = [];
  if (typeof detail.reference === "string") parts.push(detail.reference);
  if (typeof detail.status === "string") parts.push(`→ ${humanise(detail.status)}`);
  if (typeof detail.filename === "string") parts.push(detail.filename);
  if (typeof detail.action_type === "string") parts.push(humanise(detail.action_type));
  if (typeof detail.role === "string") parts.push(humanise(detail.role));
  return parts.length > 0 ? parts.join(" · ") : "recorded";
}
