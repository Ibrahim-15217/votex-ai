import { useEffect, useMemo, useState, type ReactNode } from "react";

import { useAuth } from "../auth/AuthContext";
import {
  AlertTriangleIcon,
  CheckCircleIcon,
  ChevronRightIcon,
  ClipboardIcon,
  ClockIcon,
  FileTextIcon,
  PlayIcon,
  PlusIcon,
  RefreshIcon,
  ShieldCheckIcon,
  TargetIcon,
} from "../components/icons";
import {
  Card,
  CardHeader,
  EmptyState,
  Notice,
  PageHeader,
  Spinner,
  btnGhost,
  btnPrimary,
  btnSubtle,
  cn,
  inputClass,
  labelClass,
  selectClass,
} from "../components/ui";
import {
  api,
  type AssessmentCreatePayload,
  type AssessmentDetail,
  type AssessmentListItem,
  type ExerciseDetail,
  type ExerciseListItem,
  type ExerciseTask,
  type ExerciseTaskStatus,
  type FindingSeverity,
  type FindingUpdatePayload,
  type ReadinessBand,
  type RemediationStatus,
  type ResilienceControl,
  type ResilienceFinding,
  type ResilienceQuestionnaire,
  type ResilienceSummary,
} from "../lib/api";
import { formatDateTime } from "../lib/format";
import { useI18n } from "../lib/i18n";

const CATEGORY_ORDER = [
  "governance",
  "identity",
  "network",
  "data",
  "response",
  "people",
] as const;

const CATEGORY_LABELS: Record<string, string> = {
  governance: "Governance & planning",
  identity: "Identity & access",
  network: "Network & email",
  data: "Data protection",
  response: "Response & recovery",
  people: "People & awareness",
};

const BAND_META: Record<
  ReadinessBand,
  { label: string; ring: string; text: string; chip: string; dot: string }
> = {
  fragile: {
    label: "Fragile",
    ring: "#F87171",
    text: "text-danger",
    chip: "border-danger/30 bg-danger/10 text-danger",
    dot: "bg-danger",
  },
  developing: {
    label: "Developing",
    ring: "#FBBF24",
    text: "text-warning",
    chip: "border-warning/30 bg-warning/10 text-warning",
    dot: "bg-warning",
  },
  resilient: {
    label: "Resilient",
    ring: "#34D399",
    text: "text-success",
    chip: "border-success/30 bg-success/10 text-success",
    dot: "bg-success",
  },
};

const SEVERITY_META: Record<
  FindingSeverity,
  { label: string; chip: string; dot: string }
> = {
  critical: {
    label: "Critical",
    chip: "border-critical/30 bg-critical/10 text-critical",
    dot: "bg-critical",
  },
  high: {
    label: "High",
    chip: "border-warning/30 bg-warning/10 text-warning",
    dot: "bg-warning",
  },
  medium: {
    label: "Medium",
    chip: "border-brand/30 bg-brand/10 text-brand",
    dot: "bg-brand",
  },
  low: {
    label: "Low",
    chip: "border-line bg-surface-2/70 text-muted",
    dot: "bg-muted",
  },
};

const REMEDIATION_LABELS: Record<RemediationStatus, string> = {
  open: "Open",
  in_progress: "In progress",
  resolved: "Resolved",
  accepted: "Accepted risk",
};

const REMEDIATION_TONES: Record<RemediationStatus, string> = {
  open: "border-line bg-surface-2/70 text-muted",
  in_progress: "border-brand/25 bg-brand/10 text-brand",
  resolved: "border-success/30 bg-success/10 text-success",
  accepted: "border-violet/25 bg-violet/10 text-violet",
};

const TASK_STATUS_LABELS: Record<ExerciseTaskStatus, string> = {
  pending: "Pending",
  in_progress: "In progress",
  done: "Done",
  skipped: "Skipped",
};

const GRADE_META: Record<
  ExerciseDetail["performance"]["grade"],
  { label: string; chip: string }
> = {
  ready: {
    label: "Ready",
    chip: "border-success/30 bg-success/10 text-success",
  },
  developing: {
    label: "Developing",
    chip: "border-warning/30 bg-warning/10 text-warning",
  },
  needs_review: {
    label: "Needs review",
    chip: "border-danger/30 bg-danger/10 text-danger",
  },
};

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  return rest ? `${minutes}m ${rest}s` : `${minutes}m`;
}

function scoreTone(score: number): string {
  if (score >= 70) return "text-success";
  if (score >= 40) return "text-warning";
  return "text-danger";
}

function BandPill({ band }: { band: ReadinessBand }) {
  const meta = BAND_META[band];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10.5px] font-semibold",
        meta.chip,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", meta.dot)} />
      {meta.label}
    </span>
  );
}

function SeverityPill({ severity }: { severity: FindingSeverity }) {
  const meta = SEVERITY_META[severity];
  return (
    <span
      className={cn(
        "inline-flex shrink-0 items-center gap-1.5 rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.05em]",
        meta.chip,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", meta.dot)} />
      {meta.label}
    </span>
  );
}

function ScoreRing({
  score,
  band,
  size = 104,
}: {
  score: number;
  band: ReadinessBand;
  size?: number;
}) {
  const meta = BAND_META[band];
  const degrees = Math.max(0, Math.min(100, score)) * 3.6;

  return (
    <div
      className="relative grid shrink-0 place-items-center"
      style={{ width: size, height: size }}
      role="img"
      aria-label={`Readiness score ${score.toFixed(1)} out of 100, ${meta.label}`}
    >
      <div
        aria-hidden="true"
        className="absolute inset-0 rounded-full"
        style={{
          background: `conic-gradient(${meta.ring} ${degrees}deg, #1C2C46 ${degrees}deg)`,
        }}
      />
      <div aria-hidden="true" className="absolute inset-[7px] rounded-full bg-surface" />
      <div className="relative text-center">
        <div className={cn("font-mono text-2xl font-semibold leading-none", meta.text)}>
          {score.toFixed(1)}
        </div>
        <div className="mt-1 text-[9px] uppercase tracking-[0.18em] text-muted">of 100</div>
      </div>
    </div>
  );
}

function MaturityDots({ value }: { value: number }) {
  return (
    <span className="inline-flex items-center gap-1" aria-hidden="true">
      {[0, 1, 2, 3, 4].map((step) => (
        <span
          key={step}
          className={cn(
            "h-1.5 w-1.5 rounded-full",
            step <= value
              ? value >= 3
                ? "bg-success"
                : value === 2
                  ? "bg-warning"
                  : "bg-danger"
              : "bg-line",
          )}
        />
      ))}
    </span>
  );
}

function SummaryTile({
  icon,
  label,
  value,
  hint,
  tone = "text-text",
}: {
  icon: ReactNode;
  label: string;
  value: ReactNode;
  hint?: string;
  tone?: string;
}) {
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[9.5px] font-semibold uppercase tracking-[0.16em] text-muted">
            {label}
          </p>
          <p className={cn("mt-2 font-mono text-xl font-semibold leading-none", tone)}>{value}</p>
          {hint && <p className="mt-1.5 text-[10.5px] leading-relaxed text-muted">{hint}</p>}
        </div>
        <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg border border-line bg-surface-2/60 text-muted">
          {icon}
        </span>
      </div>
    </Card>
  );
}

export default function ResiliencePage() {
  const { user } = useAuth();
  const { t } = useI18n();
  const isAnalyst = user?.role === "admin" || user?.role === "analyst";

  const [tab, setTab] = useState<"assessments" | "exercises">("assessments");
  const [questionnaire, setQuestionnaire] = useState<ResilienceQuestionnaire | null>(null);
  const [summary, setSummary] = useState<ResilienceSummary | null>(null);
  const [assessments, setAssessments] = useState<AssessmentListItem[]>([]);
  const [assessment, setAssessment] = useState<AssessmentDetail | null>(null);
  const [exercises, setExercises] = useState<ExerciseListItem[]>([]);
  const [exercise, setExercise] = useState<ExerciseDetail | null>(null);
  const [selectedAssessment, setSelectedAssessment] = useState<string | null>(null);
  const [selectedExercise, setSelectedExercise] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!isAnalyst) {
      setLoading(false);
      return;
    }

    let active = true;
    setLoading(true);
    setError(null);

    Promise.all([
      api.resilienceQuestionnaire(),
      api.resilienceSummary(),
      api.resilienceAssessments(),
      api.exercises(),
    ])
      .then(([questionnaireValue, summaryValue, assessmentList, exerciseList]) => {
        if (!active) return;
        setQuestionnaire(questionnaireValue);
        setSummary(summaryValue);
        setAssessments(assessmentList);
        setExercises(exerciseList);
        setSelectedAssessment((current) =>
          current && assessmentList.some((item) => item.id === current)
            ? current
            : (assessmentList[0]?.id ?? null),
        );
        setSelectedExercise((current) =>
          current && exerciseList.some((item) => item.id === current)
            ? current
            : (exerciseList[0]?.id ?? null),
        );
      })
      .catch((err: unknown) => {
        if (active) {
          setError(err instanceof Error ? err.message : "Could not load the resilience workspace.");
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [isAnalyst, reloadKey]);

  useEffect(() => {
    if (!selectedAssessment) {
      setAssessment(null);
      return;
    }

    let active = true;
    setDetailLoading(true);
    api
      .resilienceAssessment(selectedAssessment)
      .then((value) => {
        if (active) setAssessment(value);
      })
      .catch((err: unknown) => {
        if (active) {
          setError(err instanceof Error ? err.message : "Could not load this assessment.");
        }
      })
      .finally(() => {
        if (active) setDetailLoading(false);
      });

    return () => {
      active = false;
    };
  }, [selectedAssessment, reloadKey]);

  useEffect(() => {
    if (!selectedExercise) {
      setExercise(null);
      return;
    }

    let active = true;
    setDetailLoading(true);
    api
      .exercise(selectedExercise)
      .then((value) => {
        if (active) setExercise(value);
      })
      .catch((err: unknown) => {
        if (active) {
          setError(err instanceof Error ? err.message : "Could not load this exercise.");
        }
      })
      .finally(() => {
        if (active) setDetailLoading(false);
      });

    return () => {
      active = false;
    };
  }, [selectedExercise, reloadKey]);

  async function refreshLists() {
    const [summaryValue, assessmentList, exerciseList] = await Promise.all([
      api.resilienceSummary(),
      api.resilienceAssessments(),
      api.exercises(),
    ]);
    setSummary(summaryValue);
    setAssessments(assessmentList);
    setExercises(exerciseList);
  }

  async function handleCreateAssessment(payload: AssessmentCreatePayload) {
    setBusy(true);
    setError(null);
    setFeedback(null);
    try {
      const created = await api.createResilienceAssessment(payload);
      setAssessment(created);
      setSelectedAssessment(created.id);
      setShowForm(false);
      setFeedback(
        `Assessment scored ${created.score.toFixed(1)}/100 (${created.band}). ` +
          `${created.total_findings} findings were opened for the remaining gaps.`,
      );
      await refreshLists();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not score this assessment.");
    } finally {
      setBusy(false);
    }
  }

  async function handleFindingSave(
    finding: ResilienceFinding,
    payload: FindingUpdatePayload,
  ) {
    setBusy(true);
    setError(null);
    setFeedback(null);
    try {
      const updated = await api.updateResilienceFinding(finding.id, payload);
      setAssessment(updated);
      setFeedback(`Remediation for "${finding.title}" was recorded on the audit chain.`);
      await refreshLists();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update this finding.");
    } finally {
      setBusy(false);
    }
  }

  async function handleStartExercise() {
    setBusy(true);
    setError(null);
    setFeedback(null);
    try {
      const created = await api.createExercise();
      setExercise(created);
      setSelectedExercise(created.id);
      setTab("exercises");
      setFeedback("A fresh synthetic exercise was started. No real system was contacted.");
      await refreshLists();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not start the exercise.");
    } finally {
      setBusy(false);
    }
  }

  async function handleTaskSave(
    task: ExerciseTask,
    status: ExerciseTaskStatus,
    notes: string,
  ) {
    if (!exercise) return;
    setBusy(true);
    setError(null);
    setFeedback(null);
    try {
      const updated = await api.updateExerciseTask(exercise.id, task.id, {
        status,
        notes: notes || null,
      });
      setExercise(updated);
      setFeedback(`Task ${task.sequence} recorded as ${TASK_STATUS_LABELS[status].toLowerCase()}.`);
      await refreshLists();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not record this task.");
    } finally {
      setBusy(false);
    }
  }

  async function handleCompleteExercise() {
    if (!exercise) return;
    setBusy(true);
    setError(null);
    setFeedback(null);
    try {
      const updated = await api.completeExercise(exercise.id);
      setExercise(updated);
      setFeedback(
        `Exercise closed with a ${updated.performance.grade.replace("_", " ")} grade. ` +
          "The after-action record is read-only.",
      );
      await refreshLists();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not complete the exercise.");
    } finally {
      setBusy(false);
    }
  }

  const latest = summary?.latest ?? null;
  const completedExercises = exercises.filter((item) => item.status === "completed").length;
  const unresolvedTasks = exercise
    ? exercise.tasks.filter((task) => task.status === "pending" || task.status === "in_progress").length
    : 0;

  if (!isAnalyst) {
    return (
      <div className="animate-rise space-y-4">
        <PageHeader
          eyebrow="Phase 5 · Readiness"
          title="Resilience & simulation"
          description="Organisational readiness and exercise records are available to administrators and analysts."
        />
        <Notice tone="info">
          Your role can report incidents and follow the case you submitted. Ask an analyst in your
          organisation for the readiness picture.
        </Notice>
      </div>
    );
  }

  return (
    <div className="animate-rise space-y-5">
      <PageHeader
        eyebrow="Phase 5 · Readiness"
        title="Resilience & simulation"
        description="Score organisational readiness against a fixed 12-control questionnaire, track remediation, and rehearse a synthetic phishing triage without touching a real system."
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
              onClick={() => void handleStartExercise()}
              className={btnPrimary}
              disabled={busy}
            >
              {busy ? <Spinner className="h-4 w-4" /> : <PlayIcon className="h-4 w-4" />}
              Start exercise
            </button>
          </>
        }
      />

      <p className="rounded-lg border border-line/70 bg-surface/40 px-3.5 py-2.5 text-[10.5px] leading-relaxed text-muted">
        {t("common.englishOnly")}
      </p>

      {error && <Notice tone="error">{error}</Notice>}
      {feedback && <Notice tone="success">{feedback}</Notice>}

      {loading ? (
        <Card className="flex items-center justify-center gap-3 py-16 text-sm text-muted">
          <Spinner className="text-brand" />
          Loading readiness workspace
        </Card>
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <Card className="flex items-center gap-4 p-4">
              {latest ? (
                <>
                  <ScoreRing score={latest.score} band={latest.band} size={92} />
                  <div className="min-w-0">
                    <p className="text-[9.5px] font-semibold uppercase tracking-[0.16em] text-muted">
                      Latest readiness
                    </p>
                    <div className="mt-1.5">
                      <BandPill band={latest.band} />
                    </div>
                    <p className="mt-2 truncate text-[11px] text-muted">{latest.title}</p>
                    <p className="text-[10px] text-muted/80">
                      {formatDateTime(latest.assessment_date)}
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <span className="grid h-16 w-16 place-items-center rounded-full border border-line bg-surface-2/60 text-muted">
                    <TargetIcon className="h-6 w-6" />
                  </span>
                  <div>
                    <p className="text-[9.5px] font-semibold uppercase tracking-[0.16em] text-muted">
                      Latest readiness
                    </p>
                    <p className="mt-2 text-sm font-semibold text-text">No score yet</p>
                    <p className="mt-1 text-[10.5px] text-muted">Run a first assessment.</p>
                  </div>
                </>
              )}
            </Card>

            <SummaryTile
              icon={<ClipboardIcon className="h-4 w-4" />}
              label="Assessments"
              value={summary?.total_assessments ?? 0}
              hint={`${summary?.total_findings ?? 0} findings derived from recorded answers`}
            />

            <SummaryTile
              icon={<ShieldCheckIcon className="h-4 w-4" />}
              label="Open findings"
              value={summary?.open_findings ?? 0}
              tone={summary?.open_findings ? "text-warning" : "text-success"}
              hint={
                summary
                  ? `${summary.open_by_severity.critical ?? 0} critical · ${summary.open_by_severity.high ?? 0} high · ${summary.resolved_findings} resolved`
                  : undefined
              }
            />

            <SummaryTile
              icon={<PlayIcon className="h-4 w-4" />}
              label="Exercises"
              value={exercises.length}
              hint={`${completedExercises} completed · synthetic only`}
            />
          </div>

          <div
            role="tablist"
            aria-label="Resilience workspace"
            className="inline-flex flex-wrap items-center gap-1 rounded-xl border border-line/80 bg-surface/50 p-1"
          >
            <WorkspaceTab
              active={tab === "assessments"}
              onClick={() => setTab("assessments")}
              icon={<ClipboardIcon className="h-4 w-4" />}
              label="Readiness assessments"
              count={assessments.length}
            />
            <WorkspaceTab
              active={tab === "exercises"}
              onClick={() => setTab("exercises")}
              icon={<PlayIcon className="h-4 w-4" />}
              label="Synthetic exercises"
              count={exercises.length}
            />
          </div>

          {tab === "assessments" ? (
            <div role="tabpanel" aria-label="Readiness assessments" className="space-y-4">
              {showForm && questionnaire && (
                <AssessmentForm
                  questionnaire={questionnaire}
                  busy={busy}
                  onCancel={() => setShowForm(false)}
                  onSubmit={handleCreateAssessment}
                />
              )}

              <div className="grid gap-4 xl:grid-cols-[minmax(260px,0.8fr)_minmax(0,1.5fr)]">
                <Card className="self-start">
                  <CardHeader
                    title="Assessment history"
                    description="Each assessment keeps the answers that produced its score."
                    action={
                      <button
                        type="button"
                        onClick={() => setShowForm((value) => !value)}
                        className={btnSubtle}
                      >
                        <PlusIcon className="h-3.5 w-3.5" />
                        New
                      </button>
                    }
                  />
                  {assessments.length === 0 ? (
                    <EmptyState
                      title="No assessments yet"
                      body="Run the fixed 12-control questionnaire to produce a reproducible readiness score and a remediation list."
                      action={
                        <button type="button" onClick={() => setShowForm(true)} className={btnPrimary}>
                          <PlusIcon className="h-4 w-4" />
                          Start assessment
                        </button>
                      }
                    />
                  ) : (
                    <ul className="divide-y divide-line/60">
                      {assessments.map((item) => {
                        const active = item.id === selectedAssessment;
                        return (
                          <li key={item.id}>
                            <button
                              type="button"
                              onClick={() => setSelectedAssessment(item.id)}
                              aria-pressed={active}
                              className={cn(
                                "flex w-full items-center gap-3 px-4 py-3 text-left transition",
                                active
                                  ? "bg-brand/[0.07]"
                                  : "hover:bg-surface-2/50",
                              )}
                            >
                              <span
                                className={cn(
                                  "grid h-11 w-11 shrink-0 place-items-center rounded-full border font-mono text-[11px] font-semibold",
                                  active
                                    ? "border-brand/40 bg-brand/10 text-brand"
                                    : "border-line bg-surface-2/60 text-muted",
                                )}
                              >
                                {item.score.toFixed(0)}
                              </span>
                              <span className="min-w-0 flex-1">
                                <span className="block truncate text-xs font-semibold text-text">
                                  {item.title}
                                </span>
                                <span className="mt-0.5 block text-[10px] text-muted">
                                  {formatDateTime(item.assessment_date)}
                                </span>
                                <span className="mt-1 flex items-center gap-1.5 text-[10px] text-muted">
                                  <BandPill band={item.band} />
                                  <span>{item.open_findings} open</span>
                                </span>
                              </span>
                              <ChevronRightIcon
                                className={cn(
                                  "h-4 w-4 shrink-0",
                                  active ? "text-brand" : "text-muted/60",
                                )}
                              />
                            </button>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </Card>

                <div className="min-w-0 space-y-4">
                  {detailLoading && !assessment ? (
                    <Card className="flex items-center justify-center gap-3 py-16 text-sm text-muted">
                      <Spinner className="text-brand" />
                      Loading assessment
                    </Card>
                  ) : assessment ? (
                    <AssessmentDetailCard
                      assessment={assessment}
                      busy={busy}
                      onFindingSave={handleFindingSave}
                    />
                  ) : (
                    <Card>
                      <EmptyState
                        title="Select an assessment"
                        body="Choose an assessment from the history, or start a new one to score the current controls."
                      />
                    </Card>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div role="tabpanel" aria-label="Synthetic exercises" className="space-y-4">
              <div className="grid gap-4 xl:grid-cols-[minmax(260px,0.8fr)_minmax(0,1.5fr)]">
                <Card className="self-start">
                  <CardHeader
                    title="Exercise history"
                    description="Fixed phishing-triage scenario, six tracked tasks."
                    action={
                      <button
                        type="button"
                        onClick={() => void handleStartExercise()}
                        className={btnSubtle}
                        disabled={busy}
                      >
                        <PlusIcon className="h-3.5 w-3.5" />
                        New
                      </button>
                    }
                  />
                  {exercises.length === 0 ? (
                    <EmptyState
                      title="No exercises yet"
                      body="Start the synthetic scenario to rehearse triage, indicator extraction, containment and the decision note."
                      action={
                        <button
                          type="button"
                          onClick={() => void handleStartExercise()}
                          className={btnPrimary}
                          disabled={busy}
                        >
                          <PlayIcon className="h-4 w-4" />
                          Start exercise
                        </button>
                      }
                    />
                  ) : (
                    <ul className="divide-y divide-line/60">
                      {exercises.map((item) => {
                        const active = item.id === selectedExercise;
                        const pct = item.tasks_total
                          ? Math.round((100 * item.tasks_done) / item.tasks_total)
                          : 0;
                        return (
                          <li key={item.id}>
                            <button
                              type="button"
                              onClick={() => setSelectedExercise(item.id)}
                              aria-pressed={active}
                              className={cn(
                                "flex w-full items-start gap-3 px-4 py-3 text-left transition",
                                active ? "bg-brand/[0.07]" : "hover:bg-surface-2/50",
                              )}
                            >
                              <span
                                className={cn(
                                  "mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-lg border",
                                  item.status === "completed"
                                    ? "border-success/30 bg-success/10 text-success"
                                    : "border-brand/30 bg-brand/10 text-brand",
                                )}
                              >
                                {item.status === "completed" ? (
                                  <CheckCircleIcon className="h-4 w-4" />
                                ) : (
                                  <PlayIcon className="h-4 w-4" />
                                )}
                              </span>
                              <span className="min-w-0 flex-1">
                                <span className="block truncate text-xs font-semibold text-text">
                                  {item.title}
                                </span>
                                <span className="mt-0.5 block text-[10px] text-muted">
                                  {formatDateTime(item.started_at)}
                                </span>
                                <span className="mt-1.5 block h-1 overflow-hidden rounded-full bg-surface-2">
                                  <span
                                    className={cn(
                                      "block h-full rounded-full",
                                      item.status === "completed" ? "bg-success" : "bg-brand",
                                    )}
                                    style={{ width: `${pct}%` }}
                                  />
                                </span>
                                <span className="mt-1 flex items-center gap-1.5 text-[10px] text-muted">
                                  <span
                                    className={cn(
                                      "inline-flex items-center rounded-full border px-2 py-0.5 font-semibold",
                                      item.status === "completed"
                                        ? "border-success/30 bg-success/10 text-success"
                                        : "border-brand/25 bg-brand/10 text-brand",
                                    )}
                                  >
                                    {item.status === "completed" ? "Completed" : "Running"}
                                  </span>
                                  <span>
                                    {item.tasks_done}/{item.tasks_total} tasks
                                  </span>
                                </span>
                              </span>
                              <ChevronRightIcon
                                className={cn(
                                  "mt-1 h-4 w-4 shrink-0",
                                  active ? "text-brand" : "text-muted/60",
                                )}
                              />
                            </button>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </Card>

                <div className="min-w-0 space-y-4">
                  {detailLoading && !exercise ? (
                    <Card className="flex items-center justify-center gap-3 py-16 text-sm text-muted">
                      <Spinner className="text-brand" />
                      Loading exercise
                    </Card>
                  ) : exercise ? (
                    <ExerciseDetailCard
                      exercise={exercise}
                      busy={busy}
                      unresolvedTasks={unresolvedTasks}
                      onTaskSave={handleTaskSave}
                      onComplete={handleCompleteExercise}
                    />
                  ) : (
                    <Card>
                      <EmptyState
                        title="Select an exercise"
                        body="Choose a run from the history, or start a fresh synthetic exercise to rehearse the response."
                      />
                    </Card>
                  )}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function WorkspaceTab({
  active,
  onClick,
  icon,
  label,
  count,
}: {
  active: boolean;
  onClick: () => void;
  icon: ReactNode;
  label: string;
  count: number;
}) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-2 rounded-lg border px-3.5 py-2 text-xs font-semibold transition",
        active
          ? "border-brand/30 bg-brand/10 text-brand"
          : "border-transparent text-muted hover:border-line hover:bg-surface-2/60 hover:text-text",
      )}
    >
      {icon}
      {label}
      <span
        className={cn(
          "rounded-full px-1.5 py-0.5 font-mono text-[9.5px]",
          active ? "bg-brand/15 text-brand" : "bg-surface-2 text-muted",
        )}
      >
        {count}
      </span>
    </button>
  );
}

function AssessmentForm({
  questionnaire,
  busy,
  onCancel,
  onSubmit,
}: {
  questionnaire: ResilienceQuestionnaire;
  busy: boolean;
  onCancel: () => void;
  onSubmit: (payload: AssessmentCreatePayload) => void;
}) {
  const today = new Date().toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
  const [title, setTitle] = useState(`Readiness review · ${today}`);
  const [notes, setNotes] = useState("");
  const [answers, setAnswers] = useState<Record<string, number>>(() =>
    Object.fromEntries(questionnaire.controls.map((control) => [control.key, 2])),
  );

  const liveScore = useMemo(() => {
    const values = questionnaire.controls.map((control) => answers[control.key] ?? 0);
    const total = values.reduce((sum, value) => sum + value, 0);
    return Math.round((1000 * total) / (4 * questionnaire.controls.length)) / 10;
  }, [answers, questionnaire.controls]);

  const liveBand: ReadinessBand =
    liveScore >= 70 ? "resilient" : liveScore >= 40 ? "developing" : "fragile";

  return (
    <Card>
      <CardHeader
        title="New readiness assessment"
        description="Answer all 12 controls. Equal weights are applied and the answers are stored with the score."
        action={
          <span className={cn("font-mono text-sm font-semibold", scoreTone(liveScore))}>
            {liveScore.toFixed(1)} / 100
          </span>
        }
      />
      <form
        className="space-y-4 p-5"
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit({
            title: title.trim(),
            notes: notes.trim() || null,
            answers,
          });
        }}
      >
        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <label className={labelClass} htmlFor="assessment-title">
              Assessment title
            </label>
            <input
              id="assessment-title"
              className={inputClass}
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              minLength={3}
              maxLength={160}
              required
            />
          </div>
          <div>
            <label className={labelClass} htmlFor="assessment-notes">
              Notes (optional)
            </label>
            <input
              id="assessment-notes"
              className={inputClass}
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              placeholder="Scope, participants or context for this review"
              maxLength={2000}
            />
          </div>
        </div>

        <div className="grid gap-3 lg:grid-cols-2">
          {CATEGORY_ORDER.map((category) => {
            const controls = questionnaire.controls.filter(
              (control) => control.category === category,
            );
            if (!controls.length) return null;
            return (
              <fieldset
                key={category}
                className="min-w-0 rounded-lg border border-line/70 bg-void/25 p-3.5"
              >
                <legend className="px-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-brand/90">
                  {CATEGORY_LABELS[category] ?? category}
                </legend>
                <div className="mt-1 space-y-3">
                  {controls.map((control) => (
                    <div key={control.key}>
                      <label
                        htmlFor={`control-${control.key}`}
                        className="block text-[11.5px] font-medium text-text/90"
                      >
                        {control.title}
                      </label>
                      <p className="mt-0.5 text-[10px] leading-relaxed text-muted">
                        {control.detail}
                      </p>
                      <select
                        id={`control-${control.key}`}
                        className={cn(selectClass, "mt-1.5 py-1.5 text-xs")}
                        value={answers[control.key] ?? 2}
                        onChange={(event) =>
                          setAnswers((current) => ({
                            ...current,
                            [control.key]: Number(event.target.value),
                          }))
                        }
                      >
                        {[0, 1, 2, 3, 4].map((value) => (
                          <option key={value} value={value}>
                            {value} · {questionnaire.maturity_levels[String(value)]}
                          </option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>
              </fieldset>
            );
          })}
        </div>

        <details className="rounded-lg border border-line/70 bg-surface/40 px-3.5 py-2.5 text-[10.5px] text-muted">
          <summary className="cursor-pointer font-semibold text-text/80">
            How the score is calculated
          </summary>
          <p className="mt-2 leading-relaxed">{questionnaire.scoring_note}</p>
        </details>

        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line/60 pt-4">
          <p className="text-[10.5px] text-muted">
            Projected band: <span className={scoreTone(liveScore)}>{BAND_META[liveBand].label}</span>
          </p>
          <div className="flex items-center gap-2">
            <button type="button" onClick={onCancel} className={btnGhost} disabled={busy}>
              Cancel
            </button>
            <button type="submit" className={btnPrimary} disabled={busy || title.trim().length < 3}>
              {busy ? <Spinner className="h-4 w-4" /> : <TargetIcon className="h-4 w-4" />}
              Score assessment
            </button>
          </div>
        </div>
      </form>
    </Card>
  );
}

function AssessmentDetailCard({
  assessment,
  busy,
  onFindingSave,
}: {
  assessment: AssessmentDetail;
  busy: boolean;
  onFindingSave: (
    finding: ResilienceFinding,
    payload: FindingUpdatePayload,
  ) => void;
}) {
  const controlsByCategory = (category: string): ResilienceControl[] =>
    assessment.controls.filter((control) => control.category === category);

  return (
    <>
      <Card>
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-line/70 px-5 py-4">
          <div className="min-w-0">
            <h2 className="text-base font-semibold text-text">{assessment.title}</h2>
            <p className="mt-1 text-[10.5px] text-muted">
              {formatDateTime(assessment.assessment_date)}
              {assessment.created_by ? ` · ${assessment.created_by.full_name}` : ""}
            </p>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <BandPill band={assessment.band} />
              <span className="rounded-full border border-line bg-surface-2/70 px-2.5 py-1 text-[10.5px] text-muted">
                {assessment.total_findings} findings · {assessment.open_findings} open
              </span>
            </div>
          </div>
          <ScoreRing score={assessment.score} band={assessment.band} />
        </div>
        <div className="space-y-3 px-5 py-4">
          <p className="text-[12px] leading-relaxed text-text/85">{assessment.summary}</p>
          {assessment.notes && (
            <p className="rounded-lg border border-line/60 bg-void/25 px-3 py-2 text-[11px] leading-relaxed text-muted">
              {assessment.notes}
            </p>
          )}
        </div>
      </Card>

      <Card>
        <CardHeader
          title="Remediation findings"
          description="One finding per control answered below implemented. Updates are written to the audit chain."
        />
        {assessment.findings.length === 0 ? (
          <div className="px-5 py-6">
            <p className="flex items-center gap-2 text-xs text-success">
              <CheckCircleIcon className="h-4 w-4" />
              Every control is implemented or verified. No findings were opened.
            </p>
          </div>
        ) : (
          <div className="space-y-2 p-4">
            {assessment.findings.map((finding) => (
              <FindingEditor
                key={`${finding.id}-${finding.updated_at}`}
                finding={finding}
                busy={busy}
                onSave={onFindingSave}
              />
            ))}
          </div>
        )}
      </Card>

      <Card>
        <CardHeader
          title="Recorded answers"
          description="Stored with the assessment so the score can always be reproduced."
        />
        <div className="grid gap-3 p-4 md:grid-cols-2">
          {CATEGORY_ORDER.map((category) => {
            const controls = controlsByCategory(category);
            if (!controls.length) return null;
            return (
              <div
                key={category}
                className="rounded-lg border border-line/60 bg-void/20 p-3.5"
              >
                <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-brand/90">
                  {CATEGORY_LABELS[category] ?? category}
                </p>
                <ul className="mt-2.5 space-y-2.5">
                  {controls.map((control) => {
                    const value = assessment.answers[control.key] ?? 0;
                    return (
                      <li
                        key={control.key}
                        className="flex items-center justify-between gap-3"
                      >
                        <span className="min-w-0 text-[11.5px] leading-snug text-text/85">
                          {control.title}
                        </span>
                        <span className="flex shrink-0 items-center gap-2">
                          <MaturityDots value={value} />
                          <span className="w-6 text-right font-mono text-[10.5px] text-muted">
                            {value}
                          </span>
                        </span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            );
          })}
        </div>
      </Card>
    </>
  );
}

function FindingEditor({
  finding,
  busy,
  onSave,
}: {
  finding: ResilienceFinding;
  busy: boolean;
  onSave: (finding: ResilienceFinding, payload: FindingUpdatePayload) => void;
}) {
  const [status, setStatus] = useState<RemediationStatus>(finding.remediation_status);
  const [owner, setOwner] = useState(finding.owner ?? "");
  const [note, setNote] = useState("");

  const dirty =
    status !== finding.remediation_status ||
    owner !== (finding.owner ?? "") ||
    note.trim().length > 0;

  return (
    <details className="group rounded-lg border border-line/70 bg-void/25">
      <summary className="flex cursor-pointer list-none items-center gap-2.5 px-3.5 py-2.5 [&::-webkit-details-marker]:hidden">
        <ChevronRightIcon className="h-3.5 w-3.5 shrink-0 text-muted transition group-open:rotate-90" />
        <SeverityPill severity={finding.severity} />
        <span className="min-w-0 flex-1 truncate text-[11.5px] font-medium text-text">
          {finding.title}
        </span>
        <span
          className={cn(
            "hidden shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-medium sm:inline-flex",
            REMEDIATION_TONES[finding.remediation_status],
          )}
        >
          {REMEDIATION_LABELS[finding.remediation_status]}
        </span>
      </summary>
      <div className="space-y-3 border-t border-line/60 px-3.5 py-3">
        <p className="text-[11px] leading-relaxed text-muted">{finding.detail}</p>
        <div className="grid gap-2 sm:grid-cols-2">
          <div>
            <label className={labelClass} htmlFor={`finding-status-${finding.id}`}>
              Remediation status
            </label>
            <select
              id={`finding-status-${finding.id}`}
              className={cn(selectClass, "py-2 text-xs")}
              value={status}
              onChange={(event) => setStatus(event.target.value as RemediationStatus)}
            >
              {(Object.keys(REMEDIATION_LABELS) as RemediationStatus[]).map((value) => (
                <option key={value} value={value}>
                  {REMEDIATION_LABELS[value]}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass} htmlFor={`finding-owner-${finding.id}`}>
              Owner
            </label>
            <input
              id={`finding-owner-${finding.id}`}
              className={cn(inputClass, "py-2 text-xs")}
              value={owner}
              onChange={(event) => setOwner(event.target.value)}
              placeholder="Team or person accountable"
              maxLength={160}
            />
          </div>
        </div>
        <div>
          <label className={labelClass} htmlFor={`finding-note-${finding.id}`}>
            Audit note (optional)
          </label>
          <input
            id={`finding-note-${finding.id}`}
            className={cn(inputClass, "py-2 text-xs")}
            value={note}
            onChange={(event) => setNote(event.target.value)}
            placeholder="What changed, and why"
            maxLength={1000}
          />
        </div>
        <div className="flex items-center justify-between gap-2">
          <span className="text-[10px] text-muted">
            {finding.owner ? `Current owner: ${finding.owner}` : "No owner assigned yet"}
          </span>
          <button
            type="button"
            className={btnSubtle}
            disabled={busy || !dirty}
            onClick={() =>
              onSave(finding, {
                remediation_status: status,
                owner: owner.trim() || null,
                note: note.trim() || null,
              })
            }
          >
            {busy ? <Spinner className="h-3 w-3" /> : <FileTextIcon className="h-3.5 w-3.5" />}
            Save remediation
          </button>
        </div>
      </div>
    </details>
  );
}

function ExerciseDetailCard({
  exercise,
  busy,
  unresolvedTasks,
  onTaskSave,
  onComplete,
}: {
  exercise: ExerciseDetail;
  busy: boolean;
  unresolvedTasks: number;
  onTaskSave: (task: ExerciseTask, status: ExerciseTaskStatus, notes: string) => void;
  onComplete: () => void;
}) {
  const grade = GRADE_META[exercise.performance.grade];
  const completed = exercise.status === "completed";

  return (
    <>
      <Card>
        <div className="flex flex-wrap items-start justify-between gap-3 border-b border-line/70 px-5 py-4">
          <div className="min-w-0">
            <h2 className="text-base font-semibold text-text">{exercise.title}</h2>
            <p className="mt-1 text-[10.5px] text-muted">
              Started {formatDateTime(exercise.started_at)}
              {exercise.completed_at ? ` · closed ${formatDateTime(exercise.completed_at)}` : ""}
            </p>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <span
                className={cn(
                  "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10.5px] font-semibold",
                  completed
                    ? "border-success/30 bg-success/10 text-success"
                    : "border-brand/25 bg-brand/10 text-brand",
                )}
              >
                <span
                  className={cn(
                    "h-1.5 w-1.5 rounded-full",
                    completed ? "bg-success" : "bg-brand",
                  )}
                />
                {completed ? "Completed" : "Running"}
              </span>
              <span
                className={cn(
                  "rounded-full border px-2.5 py-1 text-[10.5px] font-semibold",
                  grade.chip,
                )}
              >
                {grade.label}
              </span>
              <span className="rounded-full border border-line bg-surface-2/70 px-2.5 py-1 text-[10.5px] text-muted">
                {exercise.scenario_key}
              </span>
            </div>
          </div>
          <button
            type="button"
            className={btnPrimary}
            disabled={busy || completed || unresolvedTasks > 0}
            onClick={onComplete}
            title={
              completed
                ? "This exercise is already closed."
                : unresolvedTasks
                  ? "Finish or skip every task before closing."
                  : undefined
            }
          >
            {busy ? <Spinner className="h-4 w-4" /> : <CheckCircleIcon className="h-4 w-4" />}
            {completed ? "Closed" : "Complete exercise"}
          </button>
        </div>

        <div className="space-y-3 px-5 py-4">
          <p className="text-[12px] leading-relaxed text-text/85">{exercise.summary}</p>
          <div className="grid gap-2 sm:grid-cols-4">
            <MiniStat
              icon={<ClockIcon className="h-3.5 w-3.5" />}
              label="Elapsed"
              value={formatDuration(exercise.performance.elapsed_seconds)}
            />
            <MiniStat
              icon={<CheckCircleIcon className="h-3.5 w-3.5" />}
              label="Resolved"
              value={`${exercise.performance.tasks_resolved}/${exercise.performance.tasks_total}`}
            />
            <MiniStat
              icon={<TargetIcon className="h-3.5 w-3.5" />}
              label="Completion"
              value={`${exercise.performance.completion_pct.toFixed(1)}%`}
            />
            <MiniStat
              icon={<AlertTriangleIcon className="h-3.5 w-3.5" />}
              label="Skipped"
              value={String(exercise.performance.tasks_skipped)}
            />
          </div>
          <p className="rounded-lg border border-line/60 bg-void/25 px-3 py-2 text-[11px] leading-relaxed text-muted">
            {exercise.performance.note}
          </p>
          {!completed && unresolvedTasks > 0 && (
            <p className="text-[10.5px] text-warning">
              {unresolvedTasks} task{unresolvedTasks === 1 ? "" : "s"} still open. Finish or skip
              them to close the exercise.
            </p>
          )}
        </div>
      </Card>

      <Card>
        <CardHeader
          title="Exercise tasks"
          description="Record the action taken at each step. Every update is audited."
        />
        <div className="space-y-2 p-4">
          {exercise.tasks.map((task) => (
            <TaskEditor
              key={`${task.id}-${task.status}-${task.notes}`}
              task={task}
              busy={busy}
              readOnly={completed}
              onSave={onTaskSave}
            />
          ))}
        </div>
      </Card>
    </>
  );
}

function MiniStat({
  icon,
  label,
  value,
}: {
  icon: ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-line/60 bg-void/25 px-3 py-2.5">
      <p className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.12em] text-muted">
        {icon}
        {label}
      </p>
      <p className="mt-1.5 font-mono text-sm font-semibold text-text">{value}</p>
    </div>
  );
}

function TaskEditor({
  task,
  busy,
  readOnly,
  onSave,
}: {
  task: ExerciseTask;
  busy: boolean;
  readOnly: boolean;
  onSave: (task: ExerciseTask, status: ExerciseTaskStatus, notes: string) => void;
}) {
  const [status, setStatus] = useState<ExerciseTaskStatus>(task.status);
  const [notes, setNotes] = useState(task.notes);
  const dirty = status !== task.status || notes !== task.notes;

  const tone =
    task.status === "done"
      ? "border-success/35 bg-success/10 text-success"
      : task.status === "skipped"
        ? "border-warning/30 bg-warning/10 text-warning"
        : task.status === "in_progress"
          ? "border-brand/30 bg-brand/10 text-brand"
          : "border-line bg-surface-2/70 text-muted";

  return (
    <details className="group rounded-lg border border-line/70 bg-void/25">
      <summary className="flex cursor-pointer list-none items-center gap-2.5 px-3.5 py-2.5 [&::-webkit-details-marker]:hidden">
        <ChevronRightIcon className="h-3.5 w-3.5 shrink-0 text-muted transition group-open:rotate-90" />
        <span
          className={cn(
            "grid h-6 w-6 shrink-0 place-items-center rounded-md border font-mono text-[10px] font-semibold",
            tone,
          )}
        >
          {task.sequence}
        </span>
        <span className="min-w-0 flex-1 truncate text-[11.5px] font-medium text-text">
          {task.title}
        </span>
        <span
          className={cn(
            "hidden shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-medium sm:inline-flex",
            tone,
          )}
        >
          {TASK_STATUS_LABELS[task.status]}
        </span>
      </summary>
      <div className="space-y-3 border-t border-line/60 px-3.5 py-3">
        <p className="text-[11px] leading-relaxed text-muted">{task.description}</p>
        <p className="rounded-lg border border-brand/20 bg-brand/[0.06] px-3 py-2 text-[10.5px] leading-relaxed text-brand/90">
          <span className="font-semibold uppercase tracking-[0.1em]">Expected action · </span>
          {task.expected_action}
        </p>
        {readOnly ? (
          <p className="text-[10.5px] text-muted">
            This exercise is closed. The record is read-only.
            {task.notes ? ` Note: ${task.notes}` : ""}
          </p>
        ) : (
          <>
            <div className="grid gap-2 sm:grid-cols-[180px_minmax(0,1fr)]">
              <div>
                <label className={labelClass} htmlFor={`task-status-${task.id}`}>
                  Status
                </label>
                <select
                  id={`task-status-${task.id}`}
                  className={cn(selectClass, "py-2 text-xs")}
                  value={status}
                  onChange={(event) =>
                    setStatus(event.target.value as ExerciseTaskStatus)
                  }
                >
                  {(Object.keys(TASK_STATUS_LABELS) as ExerciseTaskStatus[]).map((value) => (
                    <option key={value} value={value}>
                      {TASK_STATUS_LABELS[value]}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className={labelClass} htmlFor={`task-notes-${task.id}`}>
                  Decision note
                </label>
                <input
                  id={`task-notes-${task.id}`}
                  className={cn(inputClass, "py-2 text-xs")}
                  value={notes}
                  onChange={(event) => setNotes(event.target.value)}
                  placeholder="What was observed, decided or handed over"
                  maxLength={1000}
                />
              </div>
            </div>
            <div className="flex justify-end">
              <button
                type="button"
                className={btnSubtle}
                disabled={busy || !dirty}
                onClick={() => onSave(task, status, notes)}
              >
                {busy ? <Spinner className="h-3 w-3" /> : <FileTextIcon className="h-3.5 w-3.5" />}
                Record task
              </button>
            </div>
          </>
        )}
      </div>
    </details>
  );
}
