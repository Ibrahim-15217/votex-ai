import type { ReactNode } from "react";

import {
  AlertTriangleIcon,
  CheckCircleIcon,
  RefreshIcon,
  ScanIcon,
} from "./icons";
import {
  Card,
  CardHeader,
  Spinner,
  btnSubtle,
  cn,
} from "./ui";
import type {
  AnalysisClassification,
  AnalysisFactor,
  AnalysisReason,
  IncidentAnalysis,
} from "../lib/api";
import { formatDateTime } from "../lib/format";

type BandStyle = {
  label: string;
  text: string;
  stroke: string;
  chip: string;
  soft: string;
};

const bandStyles: Record<AnalysisClassification, BandStyle> = {
  high_risk: {
    label: "High risk",
    text: "text-critical",
    stroke: "#FB7185",
    chip: "border-critical/35 bg-critical/12 text-critical",
    soft: "border-critical/20 bg-critical/[0.05]",
  },
  suspicious: {
    label: "Suspicious",
    text: "text-warning",
    stroke: "#FBBF24",
    chip: "border-warning/35 bg-warning/12 text-warning",
    soft: "border-warning/20 bg-warning/[0.05]",
  },
  benign: {
    label: "Low risk",
    text: "text-success",
    stroke: "#34D399",
    chip: "border-success/35 bg-success/12 text-success",
    soft: "border-success/20 bg-success/[0.05]",
  },
};

const componentStyles: Record<string, { label: string; text: string; bg: string }> = {
  U: { label: "URL", text: "text-brand", bg: "bg-brand" },
  N: { label: "NLP", text: "text-violet", bg: "bg-violet" },
  M: { label: "ML", text: "text-brand-2", bg: "bg-brand-2" },
  I: { label: "Rules", text: "text-warning", bg: "bg-warning" },
};

const severityStyles: Record<string, string> = {
  high: "border-critical/30 bg-critical/10 text-critical",
  medium: "border-warning/30 bg-warning/10 text-warning",
  low: "border-brand/25 bg-brand/10 text-brand",
  info: "border-line bg-surface-2/70 text-muted",
};

export function AIAnalysisPanel({
  analysis,
  aiStatus,
  canAnalyse,
  busy,
  onAnalyse,
}: {
  analysis: IncidentAnalysis | null;
  aiStatus: string;
  canAnalyse: boolean;
  busy: boolean;
  onAnalyse: () => void;
}) {
  if (!analysis) {
    return (
      <Card>
        <CardHeader
          title="Explainable AI analysis"
          description="URL intelligence, language signals, a trained classifier and policy rules."
          action={<ModelChip version="hybrid-v0.2.0" />}
        />
        <div className="flex flex-col items-center gap-3 px-5 py-10 text-center">
          <span className="grid h-12 w-12 place-items-center rounded-2xl border border-brand/25 bg-brand/10 text-brand">
            <ScanIcon className="h-6 w-6" />
          </span>
          <div>
            <p className="text-sm font-semibold text-text">
              {aiStatus === "failed" ? "Analysis failed" : "Analysis pending"}
            </p>
            <p className="mx-auto mt-1 max-w-md text-[11.5px] leading-relaxed text-muted">
              {aiStatus === "failed"
                ? "The report is safe. Re-run the analyser to produce a new explainable result."
                : canAnalyse
                  ? "Run the hybrid analyser to score this report and generate analyst-readable reasons."
                  : "The response team will triage this report. You can keep adding context to the case."}
            </p>
          </div>
          {canAnalyse && (
            <button type="button" onClick={onAnalyse} className={btnSubtle} disabled={busy}>
              {busy ? <Spinner className="h-3.5 w-3.5" /> : <ScanIcon className="h-3.5 w-3.5" />}
              Run AI analysis
            </button>
          )}
        </div>
      </Card>
    );
  }

  const band = bandStyles[analysis.classification] ?? bandStyles.suspicious;
  const topReasons = analysis.reasons.slice(0, 10);
  const indicators = analysis.indicators.slice(0, 14);

  return (
    <Card className={cn("overflow-hidden border", band.soft)}>
      <CardHeader
        title="Explainable AI analysis"
        description="Four independent components combined by a published, auditable formula."
        action={
          <div className="flex flex-wrap items-center gap-2">
            <ModelChip version={analysis.model_version} />
            {canAnalyse && (
              <button type="button" onClick={onAnalyse} className={btnSubtle} disabled={busy}>
                {busy ? <Spinner className="h-3 w-3" /> : <RefreshIcon className="h-3 w-3" />}
                Re-run
              </button>
            )}
          </div>
        }
      />

      <div className="border-b border-line/70 px-5 py-5">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[208px_minmax(0,1fr)]">
          <div className="flex flex-col items-center">
            <RiskGauge score={analysis.risk_score} stroke={band.stroke} />
            <span
              className={cn(
                "mt-3 inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold",
                band.chip,
              )}
            >
              <span className="h-1.5 w-1.5 rounded-full bg-current" />
              {band.label}
            </span>
            <div className="mt-3 w-full rounded-lg border border-line/70 bg-void/35 px-3 py-2">
              <div className="flex items-center justify-between text-[9.5px]">
                <span className="uppercase tracking-[0.13em] text-muted/80">Confidence</span>
                <span className="font-mono text-text/90">{Math.round(analysis.confidence * 100)}%</span>
              </div>
              <div className="mt-1.5 h-1 overflow-hidden rounded-full bg-surface-2">
                <span
                  className="block h-full rounded-full bg-gradient-to-r from-brand to-violet"
                  style={{ width: `${Math.round(analysis.confidence * 100)}%` }}
                />
              </div>
              <p className="mt-1.5 text-[8.5px] leading-snug text-muted/80">
                Reflects component agreement, not certainty that an attack occurred.
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <p className="text-[12.5px] leading-relaxed text-text/90">{analysis.summary}</p>
            <div className="space-y-3">
              {analysis.factors.map((factor) => (
                <FactorBar key={factor.key} factor={factor} />
              ))}
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 border-t border-line/60 pt-3 text-[9.5px] text-muted/80">
              <span className="font-mono text-text/80">R = 0.30U + 0.25N + 0.25M + 0.20I</span>
              <span>Low &lt; 35</span>
              <span>Suspicious 35–64</span>
              <span>High ≥ 65</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-0 lg:grid-cols-2">
        <div className="border-b border-line/70 px-5 py-4 lg:border-b-0 lg:border-r">
          <SectionLabel count={topReasons.length}>Why this score</SectionLabel>
          <ol className="mt-3 space-y-2">
            {topReasons.map((reason, index) => (
              <ReasonRow key={`${reason.component}-${index}`} reason={reason} />
            ))}
          </ol>
        </div>

        <div className="px-5 py-4">
          <SectionLabel count={analysis.indicators.length}>Extracted indicators</SectionLabel>
          {indicators.length === 0 ? (
            <p className="mt-3 text-[11px] text-muted/80">No indicators were extracted from this report.</p>
          ) : (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {indicators.map((indicator) => (
                <span
                  key={indicator.code}
                  title={indicator.detail}
                  className={cn(
                    "inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-[9.5px] font-medium",
                    severityStyles[indicator.severity] ?? severityStyles.info,
                  )}
                >
                  <span className="h-1 w-1 rounded-full bg-current" />
                  {indicator.label}
                </span>
              ))}
              {analysis.indicators.length > indicators.length && (
                <span className="rounded-md border border-line bg-surface-2/60 px-2 py-1 text-[9.5px] text-muted">
                  +{analysis.indicators.length - indicators.length} more
                </span>
              )}
            </div>
          )}

          {analysis.warnings.length > 0 && (
            <div className="mt-4 space-y-1.5">
              {analysis.warnings.map((warning) => (
                <p
                  key={warning}
                  className="flex gap-2 rounded-md border border-warning/20 bg-warning/[0.06] px-2.5 py-2 text-[9.5px] leading-relaxed text-warning/90"
                >
                  <AlertTriangleIcon className="mt-0.5 h-3 w-3 shrink-0" />
                  {warning}
                </p>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid gap-2 border-t border-line/70 px-5 py-3 text-[9px] text-muted/80 sm:grid-cols-2 lg:grid-cols-4">
        <Meta label="Model" value={analysis.model_version} />
        <Meta label="Ruleset" value={analysis.ruleset_version} />
        <Meta label="Analysed" value={formatDateTime(analysis.created_at)} />
        <Meta label="Latency" value={`${analysis.latency_ms} ms`} />
      </div>

      <div className="flex flex-wrap items-center gap-2 border-t border-line/70 bg-void/30 px-5 py-2.5">
        <CheckCircleIcon className="h-3.5 w-3.5 text-success/80" />
        <p className="text-[9.5px] leading-relaxed text-muted/80">
          Advisory output from a synthetic-data model. A human analyst remains accountable for every decision,
          and each run is written to the audit chain.
        </p>
      </div>
    </Card>
  );
}

function RiskGauge({ score, stroke }: { score: number; stroke: string }) {
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const offset = circumference * (1 - clamped / 100);

  return (
    <div className="relative h-44 w-44">
      <svg viewBox="0 0 180 180" className="h-44 w-44 -rotate-90" aria-hidden="true">
        <circle cx="90" cy="90" r={radius} fill="none" stroke="#16243A" strokeWidth="11" />
        <circle
          cx="90"
          cy="90"
          r={radius}
          fill="none"
          stroke={stroke}
          strokeWidth="11"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 650ms cubic-bezier(0.22, 1, 0.36, 1)" }}
        />
        <circle cx="90" cy="20" r="2.4" fill={stroke} opacity="0.75" />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-[9px] font-semibold uppercase tracking-[0.2em] text-muted/80">Risk score</span>
        <span className="mt-1 font-mono text-[2.6rem] font-semibold leading-none tracking-tight text-text">
          {score.toFixed(1)}
        </span>
        <span className="mt-1 text-[9.5px] text-muted/80">out of 100</span>
      </div>
    </div>
  );
}

function FactorBar({ factor }: { factor: AnalysisFactor }) {
  const style = componentStyles[factor.key] ?? componentStyles.U;
  const score = Math.max(0, Math.min(100, factor.score));
  return (
    <div>
      <div className="flex items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2">
          <span className={cn("rounded border border-line/70 bg-void/50 px-1.5 py-0.5 font-mono text-[9px] font-semibold", style.text)}>
            {factor.key}
          </span>
          <span className="truncate text-[11px] font-medium text-text/90">{factor.label}</span>
          <span className="hidden rounded border border-line/60 px-1 py-0.5 font-mono text-[8.5px] text-muted/80 sm:inline">
            {Math.round(factor.weight * 100)}%
          </span>
        </div>
        <span className={cn("font-mono text-[11px] font-semibold", style.text)}>{score.toFixed(1)}</span>
      </div>
      <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-surface-2">
        <span
          className={cn("block h-full rounded-full transition-[width] duration-700", style.bg)}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}

function ReasonRow({ reason }: { reason: AnalysisReason }) {
  const style = componentStyles[reason.component] ?? componentStyles.U;
  const raises = reason.direction === "increases_risk";
  return (
    <li className="flex gap-2.5 rounded-lg border border-line/60 bg-void/30 px-3 py-2.5">
      <span className={cn("mt-0.5 h-fit rounded border border-line/70 bg-surface-2/70 px-1.5 py-0.5 font-mono text-[9px] font-semibold", style.text)}>
        {reason.component}
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-[10.5px] leading-relaxed text-text/85">{reason.message}</p>
        <p className="mt-1 flex items-center gap-1.5 text-[8.5px] uppercase tracking-[0.12em] text-muted/80">
          <span className={raises ? "text-critical/80" : "text-success/80"}>
            {raises ? "▲ Raises risk" : "▼ Lowers risk"}
          </span>
          <span className="text-muted/80">·</span>
          <span className="font-mono normal-case tracking-normal">{reason.weight > 0 ? "+" : ""}{reason.weight.toFixed(1)}</span>
        </p>
      </div>
    </li>
  );
}

function SectionLabel({ children, count }: { children: ReactNode; count: number }) {
  return (
    <div className="flex items-center justify-between gap-2">
      <h3 className="text-[10px] font-semibold uppercase tracking-[0.16em] text-muted/80">{children}</h3>
      <span className="rounded-full border border-line bg-void/40 px-1.5 py-0.5 font-mono text-[9px] text-muted/80">
        {count}
      </span>
    </div>
  );
}

function ModelChip({ version }: { version: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-brand/25 bg-brand/[0.08] px-2 py-0.5 font-mono text-[9.5px] text-brand/90">
      <span className="h-1.5 w-1.5 animate-breathe rounded-full bg-brand" />
      {version}
    </span>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-2 lg:block">
      <span className="uppercase tracking-[0.12em] text-muted/80">{label}</span>
      <span className="font-mono text-muted/80 lg:mt-0.5 lg:block">{value}</span>
    </div>
  );
}
