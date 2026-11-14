import { Link } from "react-router-dom";

import type { IncidentListItem } from "../lib/api";
import { formatRelative, useI18n, type TranslationKey } from "../lib/i18n";
import { PriorityPill, RiskScore, StatusPill } from "./ui";

export function IncidentTable({
  incidents,
  showReporter = false,
}: {
  incidents: IncidentListItem[];
  showReporter?: boolean;
}) {
  const { lang, t } = useI18n();

  const categoryName = (category: string) => {
    const key = `category.${category}` as TranslationKey;
    return t(key);
  };

  return (
    <>
      <div
        className="hidden overflow-x-auto focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/40 md:block"
        tabIndex={0}
        role="region"
        aria-label={t("queue.title")}
      >
        <table className="w-full min-w-[720px] text-left">
          <thead>
            <tr className="border-b border-line/70 text-[9.5px] uppercase tracking-[0.14em] text-muted">
              <th scope="col" className="px-5 py-2.5 font-semibold">
                {t("queue.tableIncident")}
              </th>
              <th scope="col" className="px-3 py-2.5 font-semibold">
                {t("queue.tableStatus")}
              </th>
              <th scope="col" className="px-3 py-2.5 font-semibold">
                {t("queue.tablePriority")}
              </th>
              <th scope="col" className="px-3 py-2.5 font-semibold">
                {t("queue.tableRisk")}
              </th>
              <th scope="col" className="px-3 py-2.5 font-semibold">
                {showReporter ? t("queue.tableReporter") : t("queue.tableAssignee")}
              </th>
              <th scope="col" className="px-5 py-2.5 text-right font-semibold">
                {t("queue.tableUpdated")}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line/50">
            {incidents.map((incident) => (
              <tr key={incident.id} className="group transition hover:bg-surface-2/40">
                <td className="px-5 py-3.5">
                  <Link to={`/incidents/${incident.id}`} className="block min-w-0">
                    <span className="font-mono text-[10px] text-brand/80">{incident.reference}</span>
                    <span className="mt-0.5 block max-w-md truncate text-[13px] font-medium text-text transition group-hover:text-brand">
                      {incident.title}
                    </span>
                    <span className="mt-0.5 block text-[10.5px] text-muted">
                      {categoryName(incident.category)} ·{" "}
                      {t("queue.evidence", { count: incident.evidence_count })}
                    </span>
                  </Link>
                </td>
                <td className="px-3 py-3.5">
                  <StatusPill status={incident.status} />
                </td>
                <td className="px-3 py-3.5">
                  <PriorityPill priority={incident.priority} />
                </td>
                <td className="px-3 py-3.5">
                  <RiskScore score={incident.risk_score} />
                </td>
                <td className="px-3 py-3.5 text-[11.5px] text-muted">
                  {showReporter
                    ? incident.reporter.full_name
                    : (incident.assignee?.full_name ?? (
                        <span className="text-warning">{t("common.unassigned")}</span>
                      ))}
                </td>
                <td className="px-5 py-3.5 text-right text-[11px] text-muted">
                  {formatRelative(t, incident.updated_at, lang)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ul className="divide-y divide-line/50 md:hidden">
        {incidents.map((incident) => (
          <li key={incident.id}>
            <Link to={`/incidents/${incident.id}`} className="block px-4 py-3.5 transition hover:bg-surface-2/40">
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono text-[10px] text-brand/80">{incident.reference}</span>
                <span className="text-[10px] text-muted">
                  {formatRelative(t, incident.updated_at, lang)}
                </span>
              </div>
              <p className="mt-1 text-[13px] font-medium leading-snug text-text">{incident.title}</p>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <StatusPill status={incident.status} />
                <PriorityPill priority={incident.priority} />
                <RiskScore score={incident.risk_score} />
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </>
  );
}
