import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { NetworkIcon, ShieldCheckIcon } from "./icons";
import { Card, CardHeader, IndicatorKindPill, RiskScore, StatusPill, cn } from "./ui";
import { api, type RelatedIncidentList, type RelatedIncidentItem } from "../lib/api";
import { relativeTime } from "../lib/format";

export function RelatedIncidentsPanel({
  incidentId,
  refreshToken,
}: {
  incidentId: string;
  refreshToken?: string;
}) {
  const [data, setData] = useState<RelatedIncidentList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(false);

    api
      .relatedIncidents(incidentId)
      .then((value) => {
        if (active) setData(value);
      })
      .catch(() => {
        if (active) setError(true);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [incidentId, refreshToken]);

  return (
    <Card>
      <CardHeader
        title="Linked incidents"
        description="Cases in your organisation that share a normalised URL, domain, IP address or file hash."
        action={
          <span
            className={cn(
              "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 font-mono text-[10px]",
              data && data.total > 0
                ? "border-warning/25 bg-warning/10 text-warning"
                : "border-line bg-void/40 text-muted",
            )}
          >
            <NetworkIcon className="h-3 w-3" />
            {data?.total ?? 0} linked
          </span>
        }
      />

      {loading ? (
        <div className="space-y-2 px-5 py-4">
          {[0, 1].map((row) => (
            <div key={row} className="h-[74px] animate-pulse rounded-lg bg-surface-2/50" />
          ))}
        </div>
      ) : error ? (
        <p className="px-5 py-6 text-center text-[11px] text-muted/80">
          Correlation could not be loaded for this case.
        </p>
      ) : !data || data.items.length === 0 ? (
        <div className="flex flex-col items-center gap-2.5 px-5 py-8 text-center">
          <span className="grid h-10 w-10 place-items-center rounded-xl border border-line bg-void/50 text-brand/80">
            <NetworkIcon className="h-5 w-5" />
          </span>
          <div>
            <p className="text-xs font-semibold text-text">No linked incidents yet</p>
            <p className="mx-auto mt-1 max-w-md text-[10.5px] leading-relaxed text-muted/80">
              This case has no exact indicator match in your organisation. Correlation refreshes automatically when
              reports, analyses or evidence introduce a shared value.
            </p>
          </div>
        </div>
      ) : (
        <ul className="divide-y divide-line/50">
          {data.items.map((item) => (
            <RelatedRow key={item.id} item={item} />
          ))}
        </ul>
      )}

      <div className="flex flex-wrap items-center gap-2 border-t border-line/70 bg-void/30 px-5 py-2.5">
        <ShieldCheckIcon className="h-3.5 w-3.5 text-success/80" />
        <p className="text-[9.5px] leading-relaxed text-muted/80">
          Matches are exact and deterministic. Cross-organisation records are never returned, and reporters only see
          their own reports.
        </p>
      </div>
    </Card>
  );
}

function RelatedRow({ item }: { item: RelatedIncidentItem }) {
  const visibleIndicators = item.shared_indicators.slice(0, 4);
  const overflow = item.shared_indicators.length - visibleIndicators.length;

  return (
    <li>
      <Link to={`/incidents/${item.id}`} className="block px-5 py-3.5 transition hover:bg-surface-2/40">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span className="font-mono text-[10px] text-brand/90">{item.reference}</span>
          <span className="inline-flex items-center gap-1 rounded-full border border-warning/25 bg-warning/10 px-1.5 py-0.5 text-[9px] font-medium text-warning">
            {item.shared_count} shared indicator{item.shared_count === 1 ? "" : "s"}
          </span>
        </div>
        <p className="mt-1 text-[11.5px] font-medium text-text/90">{item.title}</p>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <StatusPill status={item.status} />
          <RiskScore score={item.risk_score} />
          <span className="text-[9.5px] text-muted/80">
            {item.assignee_name ? `Owner ${item.assignee_name}` : "Unassigned"} · {relativeTime(item.created_at)}
          </span>
        </div>
        {visibleIndicators.length > 0 && (
          <div className="mt-2 flex flex-wrap items-center gap-1.5">
            {visibleIndicators.map((indicator) => (
              <span
                key={indicator.id}
                title={indicator.value}
                className="inline-flex max-w-full items-center gap-1 rounded border border-line/70 bg-void/40 px-1.5 py-0.5"
              >
                <IndicatorKindPill kind={indicator.kind} className="border-0 bg-transparent px-0 py-0" />
                <span className="max-w-[190px] truncate font-mono text-[9px] text-muted/80">
                  {indicator.display_value}
                </span>
              </span>
            ))}
            {overflow > 0 && (
              <span className="rounded border border-line/70 bg-void/40 px-1.5 py-0.5 font-mono text-[9px] text-muted/80">
                +{overflow} more
              </span>
            )}
          </div>
        )}
      </Link>
    </li>
  );
}
