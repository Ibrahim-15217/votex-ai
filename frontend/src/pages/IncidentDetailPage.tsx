import { useEffect, useState, type ChangeEvent, type FormEvent, type ReactNode } from "react";
import { Link, useLocation, useParams } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { AIAnalysisPanel } from "../components/AIAnalysisPanel";
import { RelatedIncidentsPanel } from "../components/RelatedIncidentsPanel";
import {
  ActivityIcon,
  AlertTriangleIcon,
  ArrowLeftIcon,
  CheckCircleIcon,
  ClockIcon,
  CopyIcon,
  DownloadIcon,
  FileTextIcon,
  LockIcon,
  PlusIcon,
  RefreshIcon,
  ShieldCheckIcon,
  UploadIcon,
  UsersIcon,
} from "../components/icons";
import {
  Card,
  CardHeader,
  EnglishOnlyBadge,
  Notice,
  PriorityPill,
  RiskScore,
  Spinner,
  StatusPill,
  cn,
  btnPrimary,
  btnSubtle,
  inputClass,
  labelClass,
  selectClass,
} from "../components/ui";
import {
  api,
  downloadEvidence,
  type EvidenceItem,
  type IncidentDetail,
  type IncidentEvent,
  type IncidentStatus,
  type Priority,
  type UserSummary,
} from "../lib/api";
import {
  categoryLabel,
  channelLabel,
  evidenceKind,
  formatBytes,
  formatDateTime,
  humanise,
  relativeTime,
  shortHash,
  statusLabel,
} from "../lib/format";
import { useI18n } from "../lib/i18n";

const allowedTransitions: Record<IncidentStatus, IncidentStatus[]> = {
  submitted: ["under_review", "closed"],
  under_review: ["assigned", "investigating", "closed"],
  assigned: ["investigating", "under_review", "closed"],
  investigating: ["escalated", "contained", "closed"],
  escalated: ["investigating", "contained", "closed"],
  contained: ["remediated", "closed"],
  remediated: ["recovered", "closed"],
  recovered: ["closed"],
  closed: [],
};

const actionTypes = [
  ["warning_issued", "Public or staff warning issued"],
  ["takedown_requested", "Takedown requested"],
  ["containment", "Containment applied"],
  ["monitoring", "Monitoring increased"],
  ["escalation", "Escalated to another authority"],
  ["other", "Other response action"],
];

const priorities: Priority[] = ["low", "medium", "high", "critical"];

type Feedback = { tone: "success" | "error"; message: string };

export default function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const { t } = useI18n();
  const location = useLocation();
  const isAnalyst = user?.role === "admin" || user?.role === "analyst";
  const created = location.state as { created?: boolean; reference?: string } | null;

  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<Feedback | null>(null);

  const [comment, setComment] = useState("");
  const [actionType, setActionType] = useState("warning_issued");
  const [actionNote, setActionNote] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [fileKey, setFileKey] = useState(0);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let active = true;
    setLoading(true);
    setError(null);

    api
      .incident(id)
      .then((value) => {
        if (active) setIncident(value);
      })
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : "Could not load this incident.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    if (isAnalyst) {
      api
        .users()
        .then((value) => {
          if (active) setUsers(value.filter((member) => member.role !== "reporter"));
        })
        .catch(() => undefined);
    }

    return () => {
      active = false;
    };
  }, [id, isAnalyst]);

  async function refresh(message: string, tone: "success" | "error" = "success") {
    if (!id) return;
    const updated = await api.incident(id);
    setIncident(updated);
    setFeedback({ tone, message });
  }

  async function guarded(key: string, work: () => Promise<string>) {
    setBusy(key);
    setFeedback(null);
    try {
      const message = await work();
      await refresh(message);
    } catch (err) {
      setFeedback({ tone: "error", message: err instanceof Error ? err.message : "Action failed." });
    } finally {
      setBusy(null);
    }
  }

  function handleAssign(value: string) {
    if (!incident || !value) return;
    void guarded("assign", async () => {
      await api.assign(incident.id, Number(value));
      return "Assignment updated and recorded on the timeline.";
    });
  }

  function handleStatus(value: string) {
    if (!incident || !value) return;
    void guarded("status", async () => {
      await api.setStatus(incident.id, value as IncidentStatus);
      return `Incident moved to ${statusLabel(value)}.`;
    });
  }

  function handlePriority(priority: Priority) {
    if (!incident || incident.priority === priority) return;
    void guarded("priority", async () => {
      await api.setPriority(incident.id, priority);
      return `Priority set to ${priority}.`;
    });
  }

  function handleAnalyse() {
    if (!incident) return;
    void guarded("analyse", async () => {
      await api.analyzeIncident(incident.id);
      return "AI analysis re-run and appended to the audit trail.";
    });
  }

  function handleComment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!incident || comment.trim().length < 2) return;
    const message = comment.trim();
    void guarded("comment", async () => {
      await api.addComment(incident.id, message);
      setComment("");
      return "Note added to the investigation timeline.";
    });
  }

  function handleAction(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!incident || actionNote.trim().length < 3) return;
    const note = actionNote.trim();
    void guarded("action", async () => {
      await api.addAction(incident.id, actionType, note);
      setActionNote("");
      return "Response action recorded and audited.";
    });
  }

  function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!incident || !file) return;
    const selected = file;
    void guarded("evidence", async () => {
      await api.uploadEvidence(incident.id, selected);
      setFile(null);
      setFileKey((value) => value + 1);
      return "Evidence validated, hashed and stored. Every download will be audited.";
    });
  }

  async function handleDownload(evidence: EvidenceItem) {
    if (!incident) return;
    setBusy(`download-${evidence.id}`);
    setFeedback(null);
    try {
      const result = await downloadEvidence(incident.id, evidence.id);
      const updated = await api.incident(incident.id);
      setIncident(updated);
      setFeedback({
        tone: "success",
        message: `Downloaded ${result.filename}. SHA-256 ${shortHash(result.sha256, 12)}. Access written to the audit chain.`,
      });
    } catch (err) {
      setFeedback({ tone: "error", message: err instanceof Error ? err.message : "Download failed." });
    } finally {
      setBusy(null);
    }
  }

  async function copyHash(hash: string, key: string) {
    try {
      await navigator.clipboard.writeText(hash);
      setCopied(key);
      window.setTimeout(() => setCopied(null), 1600);
    } catch {
      setCopied(null);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center gap-3 text-sm text-muted">
        <Spinner className="text-brand" />
        {t("detail.loading")}
      </div>
    );
  }

  if (error || !incident) {
    return (
      <div className="space-y-4">
        <Link to="/incidents" className="inline-flex items-center gap-2 text-xs text-muted transition hover:text-text">
          <ArrowLeftIcon className="h-4 w-4" />
          {t("detail.backToQueue")}
        </Link>
        <Notice>{error ?? t("detail.notFound")}</Notice>
        <p className="text-[11px] text-muted">
          Records outside your organisation, or reports submitted by another reporter, are hidden by design.
        </p>
      </div>
    );
  }

  const transitions = allowedTransitions[incident.status];
  const assignable = users.length > 0 ? users : incident.assignee ? [incident.assignee] : [];

  return (
    <div className="animate-rise space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link to="/incidents" className="inline-flex items-center gap-2 text-xs text-muted transition hover:text-text">
          <ArrowLeftIcon className="h-4 w-4" />
          {t("detail.backToQueue")}
        </Link>
        <button
          type="button"
          onClick={() => {
            void refresh("Incident refreshed.");
          }}
          className={btnSubtle}
          disabled={busy === "refresh"}
        >
          <RefreshIcon className={cn("h-3.5 w-3.5", busy === "refresh" && "animate-spin")} />
          Refresh
        </button>
      </div>

      {created?.created && (
        <div
          role="status"
          className="flex gap-3 rounded-xl border border-success/25 bg-success/[0.06] px-4 py-3.5"
        >
          <CheckCircleIcon aria-hidden="true" className="mt-0.5 h-5 w-5 shrink-0 text-success" />
          <div>
            <p className="text-sm font-semibold text-success">{t("detail.createdTitle")}</p>
            <p className="mt-0.5 text-[11.5px] leading-relaxed text-muted">
              {t("detail.createdBody", { reference: created.reference ?? incident.reference })}
            </p>
          </div>
        </div>
      )}

      <header className="rounded-xl border border-line/80 bg-surface/50 p-5 shadow-panel backdrop-blur-sm sm:p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-[11px] text-brand/90">{incident.reference}</span>
              <span className="text-muted/80">/</span>
              <span className="text-[10.5px] uppercase tracking-[0.12em] text-muted/80">
                {categoryLabel(incident.category)}
              </span>
            </div>
            <h1 className="mt-2 max-w-3xl text-xl font-semibold leading-tight tracking-tight text-text sm:text-2xl">
              {incident.title}
            </h1>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <StatusPill status={incident.status} />
              <PriorityPill priority={incident.priority} />
              <span className="inline-flex items-center gap-1.5 rounded-full border border-line bg-void/40 px-2 py-0.5 text-[10.5px] text-muted">
                <ClockIcon className="h-3 w-3" />
                Updated {relativeTime(incident.updated_at)}
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-full border border-line bg-void/40 px-2 py-0.5 text-[10.5px] text-muted">
                <FileTextIcon className="h-3 w-3" />
                {incident.evidence_count} evidence file{incident.evidence_count === 1 ? "" : "s"}
              </span>
              <EnglishOnlyBadge />
            </div>
          </div>

          <div className="rounded-lg border border-line bg-void/40 px-4 py-3">
            <p className="text-[9px] font-semibold uppercase tracking-[0.16em] text-muted/80">Risk score</p>
            <div className="mt-1.5">
              <RiskScore score={incident.risk_score} />
            </div>
            <p className="mt-1 text-[9.5px] text-muted/80">
              {incident.risk_score === null
                ? "Awaiting AI triage"
                : incident.analysis
                  ? `${Math.round(incident.analysis.confidence * 100)}% model confidence`
                  : "Analysed baseline"}
            </p>
          </div>
        </div>

        <dl className="mt-5 grid gap-3 border-t border-line/70 pt-4 text-[10.5px] sm:grid-cols-2 lg:grid-cols-4">
          <Meta label="Reported by" value={incident.reporter.full_name} />
          <Meta label="Assigned to" value={incident.assignee?.full_name ?? "Unassigned"} tone={incident.assignee ? undefined : "text-warning/90"} />
          <Meta label="Opened" value={formatDateTime(incident.created_at)} />
          <Meta label="Channel" value={channelLabel(incident.channel)} />
          <Meta label="State" value={incident.state ?? "Not specified"} />
          <Meta label="Classification" value={incident.classification ? humanise(incident.classification) : "Pending"} />
          <Meta
            label="Reported URL"
            value={incident.reported_url ?? "None supplied"}
            mono={Boolean(incident.reported_url)}
            span2={Boolean(incident.reported_url)}
          />
          {incident.closed_at && <Meta label="Closed" value={formatDateTime(incident.closed_at)} />}
        </dl>
        {incident.reported_url && (
          <p className="mt-3 inline-flex items-center gap-1.5 rounded-md border border-warning/20 bg-warning/[0.06] px-2.5 py-1.5 text-[10px] text-warning/90">
            <AlertTriangleIcon className="h-3.5 w-3.5" />
            Do not visit the reported URL. It is stored as untrusted evidence.
          </p>
        )}
      </header>

      {feedback && <Notice tone={feedback.tone}>{feedback.message}</Notice>}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.65fr)_minmax(0,1fr)]">
        <div className="space-y-4">
          <AIAnalysisPanel
            analysis={incident.analysis}
            aiStatus={incident.ai_status}
            canAnalyse={isAnalyst}
            busy={busy === "analyse"}
            onAnalyse={handleAnalyse}
          />

          <RelatedIncidentsPanel incidentId={incident.id} refreshToken={incident.updated_at} />

          <Card>
            <CardHeader title="Report description" description="Submitted by the reporter, preserved verbatim in the timeline." />
            <p className="whitespace-pre-wrap px-5 py-4 text-[12.5px] leading-relaxed text-text/90">
              {incident.description}
            </p>
          </Card>

          <Card>
            <CardHeader
              title="Investigation timeline"
              description="Append-only events visible to everyone with access to this case."
              action={
                <span className="rounded-full border border-line bg-void/40 px-2 py-0.5 font-mono text-[10px] text-muted">
                  {incident.events.length} events
                </span>
              }
            />
            <ol className="relative space-y-0 px-5 py-2">
              {[...incident.events].reverse().map((event, index, list) => (
                <TimelineEvent key={event.id} event={event} last={index === list.length - 1} />
              ))}
            </ol>
          </Card>

          <Card>
            <CardHeader title="Add an investigation note" description="Visible to everyone with access to this incident." />
            <form onSubmit={handleComment} className="space-y-3 px-5 py-4">
              <textarea
                value={comment}
                onChange={(event) => setComment(event.target.value)}
                rows={3}
                placeholder="What did you verify? What did you rule out? Do not paste credentials or voter data."
                className={`${inputClass} resize-y leading-relaxed`}
                maxLength={4000}
              />
              <div className="flex items-center justify-between gap-3">
                <span className="text-[10px] text-muted/80">{comment.length} / 4,000</span>
                <button type="submit" className={btnPrimary} disabled={busy === "comment" || comment.trim().length < 2}>
                  {busy === "comment" ? <Spinner /> : <PlusIcon className="h-4 w-4" />}
                  Add note
                </button>
              </div>
            </form>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader
              title={isAnalyst ? "Triage controls" : "Case status"}
              description={isAnalyst ? "Changes are validated, logged and audited." : "Your report is read-only while the response team investigates."}
            />

            {isAnalyst ? (
              <div className="space-y-4 px-5 py-4">
                <div>
                  <label htmlFor="assignee" className={labelClass}>
                    Assigned analyst
                  </label>
                  <select
                    id="assignee"
                    value={incident.assignee?.id ?? ""}
                    onChange={(event) => handleAssign(event.target.value)}
                    className={selectClass}
                    disabled={busy === "assign" || assignable.length === 0}
                  >
                    <option value="" disabled>
                      {incident.assignee ? "Select to reassign" : "Unassigned — choose an analyst"}
                    </option>
                    {assignable.map((member) => (
                      <option key={member.id} value={member.id}>
                        {member.full_name} · {member.role}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="lifecycle" className={labelClass}>
                    Lifecycle
                  </label>
                  <select
                    id="lifecycle"
                    value=""
                    onChange={(event) => handleStatus(event.target.value)}
                    className={selectClass}
                    disabled={busy === "status" || transitions.length === 0}
                  >
                    <option value="" disabled>
                      {transitions.length === 0 ? "Case closed" : "Move to next stage…"}
                    </option>
                    {transitions.map((status) => (
                      <option key={status} value={status}>
                        {statusLabel(status)}
                      </option>
                    ))}
                  </select>
                  <p className="mt-1 text-[9.5px] leading-relaxed text-muted/80">
                    Allowed next stages only. Invalid transitions are rejected by the API.
                  </p>
                </div>

                <div>
                  <span className={labelClass}>Priority</span>
                  <div className="grid grid-cols-4 gap-1.5">
                    {priorities.map((priority) => (
                      <button
                        key={priority}
                        type="button"
                        onClick={() => handlePriority(priority)}
                        disabled={busy === "priority"}
                        className={cn(
                          "rounded-md border px-1.5 py-1.5 text-[10px] font-semibold capitalize transition",
                          incident.priority === priority
                            ? "border-brand/40 bg-brand/15 text-brand"
                            : "border-line bg-void/40 text-muted hover:border-brand/30 hover:text-text",
                        )}
                      >
                        {priority}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="rounded-lg border border-line/70 bg-void/30 px-3 py-2.5">
                  <p className="inline-flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted/80">
                    <ActivityIcon className="h-3.5 w-3.5 text-brand" />
                    AI triage
                  </p>
                  <div className="mt-1.5 space-y-1 text-[10.5px]">
                    <div className="flex items-center justify-between">
                      <span className="text-muted">Status</span>
                      <span className="font-mono text-text/90">{incident.ai_status}</span>
                    </div>
                    {incident.analysis && (
                      <>
                        <div className="flex items-center justify-between">
                          <span className="text-muted">Model</span>
                          <span className="font-mono text-text/90">{incident.analysis.model_version}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-muted">Confidence</span>
                          <span className="font-mono text-text/90">
                            {Math.round(incident.analysis.confidence * 100)}%
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                  <p className="mt-1.5 text-[9.5px] leading-relaxed text-muted/80">
                    Advisory only. Re-running creates a new stored result; earlier runs stay in the case record.
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-3 px-5 py-4 text-[11.5px] leading-relaxed text-muted">
                <p>
                  Your report is <span className="font-semibold text-text">{statusLabel(incident.status)}</span> and assigned to{" "}
                  <span className="font-semibold text-text">{incident.assignee?.full_name ?? "the response desk"}</span>.
                </p>
                <p className="flex gap-2">
                  <LockIcon className="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand/70" />
                  Only you and your organisation's response team can read this case. Other reporters cannot see it.
                </p>
                <p className="flex gap-2">
                  <ShieldCheckIcon className="mt-0.5 h-3.5 w-3.5 shrink-0 text-success/80" />
                  Every status change and response action is recorded on the tamper-evident audit chain.
                </p>
              </div>
            )}
          </Card>

          {isAnalyst && (
            <Card>
              <CardHeader title="Record a response action" description="Containment, takedowns and warnings are part of the record." />
              <form onSubmit={handleAction} className="space-y-3 px-5 py-4">
                <div>
                  <label htmlFor="action-type" className={labelClass}>
                    Action type
                  </label>
                  <select
                    id="action-type"
                    value={actionType}
                    onChange={(event) => setActionType(event.target.value)}
                    className={selectClass}
                  >
                    {actionTypes.map(([value, text]) => (
                      <option key={value} value={value}>
                        {text}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="action-note" className={labelClass}>
                    What was done?
                  </label>
                  <textarea
                    id="action-note"
                    value={actionNote}
                    onChange={(event) => setActionNote(event.target.value)}
                    rows={3}
                    minLength={3}
                    maxLength={2000}
                    placeholder="Describe the action, the channel used and the outcome."
                    className={`${inputClass} resize-y leading-relaxed`}
                  />
                </div>
                <button type="submit" className={btnPrimary} disabled={busy === "action" || actionNote.trim().length < 3}>
                  {busy === "action" ? <Spinner /> : <ShieldCheckIcon className="h-4 w-4" />}
                  Record action
                </button>
              </form>
            </Card>
          )}

          <Card>
            <CardHeader
              title="Evidence vault"
              description="Validated, hashed and access-logged."
              action={
                <span className="rounded-full border border-line bg-void/40 px-2 py-0.5 font-mono text-[10px] text-muted">
                  {incident.evidence.length}
                </span>
              }
            />
            <div className="divide-y divide-line/50">
              {incident.evidence.length === 0 ? (
                <p className="px-5 py-5 text-center text-[11px] text-muted/80">No evidence attached yet.</p>
              ) : (
                incident.evidence.map((item) => (
                  <div key={item.id} className="px-5 py-3.5">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex min-w-0 gap-2.5">
                        <span className="mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-md border border-line bg-void/50 text-brand">
                          <FileTextIcon className="h-4 w-4" />
                        </span>
                        <div className="min-w-0">
                          <p className="truncate text-[11.5px] font-medium text-text">{item.original_filename}</p>
                          <p className="mt-0.5 text-[10px] text-muted/80">
                            {evidenceKind(item.content_type)} · {formatBytes(item.size_bytes)} · {item.uploader.full_name}
                          </p>
                          <button
                            type="button"
                            onClick={() => void copyHash(item.sha256, item.id)}
                            title={item.sha256}
                            className="mt-1 inline-flex items-center gap-1 rounded border border-line/70 bg-void/40 px-1.5 py-0.5 font-mono text-[9.5px] text-muted/80 transition hover:border-brand/40 hover:text-brand"
                          >
                            <CopyIcon className="h-2.5 w-2.5" />
                            {copied === item.id ? "Copied hash" : `SHA-256 ${shortHash(item.sha256, 8)}`}
                          </button>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => void handleDownload(item)}
                        disabled={busy === `download-${item.id}`}
                        className={btnSubtle}
                        aria-label={`Download ${item.original_filename}`}
                      >
                        {busy === `download-${item.id}` ? <Spinner className="h-3 w-3" /> : <DownloadIcon className="h-3.5 w-3.5" />}
                        Download
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>

            <form onSubmit={handleUpload} className="space-y-2 border-t border-line/70 px-5 py-4">
              <label htmlFor="evidence-file" className={labelClass}>
                Attach evidence
              </label>
              <input
                key={fileKey}
                id="evidence-file"
                type="file"
                accept=".png,.jpg,.jpeg,.webp,.pdf,.txt,.eml,image/png,image/jpeg,image/webp,application/pdf,text/plain,message/rfc822"
                onChange={(event: ChangeEvent<HTMLInputElement>) => setFile(event.target.files?.[0] ?? null)}
                className="block w-full cursor-pointer rounded-lg border border-line bg-void/40 px-3 py-2 text-[10.5px] text-muted file:mr-3 file:cursor-pointer file:rounded-md file:border-0 file:bg-brand/15 file:px-2.5 file:py-1.5 file:text-[10.5px] file:font-semibold file:text-brand hover:border-brand/30"
              />
              <p className="text-[9.5px] leading-relaxed text-muted/80">
                PNG, JPEG, WebP, PDF, TXT or EML · 10 MB max. File type and content are checked before storage.
              </p>
              <button type="submit" className={btnGhostSmall} disabled={!file || busy === "evidence"}>
                {busy === "evidence" ? <Spinner className="h-3.5 w-3.5" /> : <UploadIcon className="h-3.5 w-3.5" />}
                Upload and hash
              </button>
            </form>
          </Card>

          <Card>
            <CardHeader title="Record integrity" />
            <div className="space-y-2 px-5 py-4 text-[10px] leading-relaxed text-muted/80">
              <p className="flex gap-2">
                <CheckCircleIcon className="mt-0.5 h-3.5 w-3.5 shrink-0 text-success/80" />
                Every action on this page writes an append-only audit entry linked by SHA-256 to the previous entry.
              </p>
              <p className="flex gap-2">
                <UsersIcon className="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand/70" />
                Tenant isolation is enforced by the service, not only in this interface.
              </p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function Meta({
  label,
  value,
  mono = false,
  tone,
  span2 = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
  tone?: string;
  span2?: boolean;
}) {
  return (
    <div className={span2 ? "sm:col-span-2" : undefined}>
      <dt className="text-[9px] font-semibold uppercase tracking-[0.14em] text-muted/80">{label}</dt>
      <dd className={cn("mt-1 break-words text-[11.5px] text-text/90", mono && "font-mono text-[10.5px]", tone)}>
        {value}
      </dd>
    </div>
  );
}

function TimelineEvent({ event, last }: { event: IncidentEvent; last: boolean }) {
  const meta = event.metadata ?? {};
  const chips: string[] = [];
  if (typeof meta.status === "string") chips.push(`→ ${statusLabel(meta.status)}`);
  if (typeof meta.action_type === "string") chips.push(humanise(meta.action_type));
  if (typeof meta.sha256 === "string") chips.push(`SHA-256 ${shortHash(meta.sha256, 6)}`);

  return (
    <li className="relative flex gap-3 py-3">
      {!last && <span aria-hidden="true" className="absolute left-[13px] top-9 h-[calc(100%-1.75rem)] w-px bg-line/80" />}
      <span className="relative z-10 mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-full border border-line bg-surface text-muted">
        <EventIcon type={event.event_type} />
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
          <p className="text-[11px] font-semibold text-text">
            {humanise(event.event_type)}
            {event.actor && <span className="font-normal text-muted"> · {event.actor.full_name}</span>}
          </p>
          <span className="font-mono text-[9.5px] text-muted/80" title={formatDateTime(event.created_at)}>
            {relativeTime(event.created_at)}
          </span>
        </div>
        <p className="mt-1 whitespace-pre-wrap text-[11.5px] leading-relaxed text-muted">{event.message}</p>
        {chips.length > 0 && (
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {chips.map((chip) => (
              <span key={chip} className="rounded border border-line/70 bg-void/40 px-1.5 py-0.5 font-mono text-[9px] text-muted/80">
                {chip}
              </span>
            ))}
          </div>
        )}
      </div>
    </li>
  );
}

function EventIcon({ type }: { type: string }): ReactNode {
  if (type === "created") return <PlusIcon className="h-3.5 w-3.5" />;
  if (type === "assigned") return <UsersIcon className="h-3.5 w-3.5" />;
  if (type === "comment") return <FileTextIcon className="h-3.5 w-3.5" />;
  if (type === "response_action") return <ShieldCheckIcon className="h-3.5 w-3.5" />;
  if (type === "evidence_added") return <UploadIcon className="h-3.5 w-3.5" />;
  if (type === "evidence_accessed") return <DownloadIcon className="h-3.5 w-3.5" />;
  return <ActivityIcon className="h-3.5 w-3.5" />;
}

const btnGhostSmall =
  "inline-flex items-center justify-center gap-1.5 rounded-md border border-line bg-surface/60 px-3 py-1.5 text-[10.5px] font-medium text-text transition hover:border-brand/40 hover:bg-surface-2 disabled:cursor-not-allowed disabled:opacity-50";
