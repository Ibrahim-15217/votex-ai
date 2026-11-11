import { useRef, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import {
  AlertTriangleIcon,
  CheckCircleIcon,
  LockIcon,
  PlusIcon,
  ShieldCheckIcon,
  UploadIcon,
} from "../components/icons";
import {
  Card,
  CardHeader,
  Notice,
  PageHeader,
  Spinner,
  btnPrimary,
  inputClass,
  labelClass,
  selectClass,
} from "../components/ui";
import { api, type Priority } from "../lib/api";
import { useI18n, type TranslationKey } from "../lib/i18n";

const categories: Array<[string, TranslationKey]> = [
  ["phishing", "report.catPhishing"],
  ["fake_portal", "report.catFakePortal"],
  ["impersonation", "report.catImpersonation"],
  ["payment_fraud", "report.catPaymentFraud"],
  ["malware", "report.catMalware"],
  ["fake_result", "report.catFakeResult"],
  ["other", "report.catOther"],
];

const channels: Array<[string, TranslationKey]> = [
  ["email", "channel.email"],
  ["sms", "channel.sms"],
  ["whatsapp", "channel.whatsapp"],
  ["web_form", "channel.web_form"],
  ["phone", "channel.phone"],
  ["other", "channel.other"],
];

const priorities: Priority[] = ["low", "medium", "high", "critical"];

const states = [
  "Federal Capital Territory",
  "Abia",
  "Adamawa",
  "Akwa Ibom",
  "Anambra",
  "Bauchi",
  "Bayelsa",
  "Benue",
  "Borno",
  "Cross River",
  "Delta",
  "Ebonyi",
  "Edo",
  "Ekiti",
  "Enugu",
  "Gombe",
  "Imo",
  "Jigawa",
  "Kaduna",
  "Kano",
  "Katsina",
  "Kebbi",
  "Kogi",
  "Kwara",
  "Lagos",
  "Nasarawa",
  "Niger",
  "Ogun",
  "Ondo",
  "Osun",
  "Oyo",
  "Plateau",
  "Rivers",
  "Sokoto",
  "Taraba",
  "Yobe",
  "Zamfara",
];

const steps: Array<[TranslationKey, TranslationKey]> = [
  ["report.step1Title", "report.step1Body"],
  ["report.step2Title", "report.step2Body"],
  ["report.step3Title", "report.step3Body"],
  ["report.step4Title", "report.step4Body"],
];

export default function ReportPage() {
  const { user } = useAuth();
  const { t } = useI18n();
  const navigate = useNavigate();
  const isAnalyst = user?.role === "admin" || user?.role === "analyst";
  const errorRef = useRef<HTMLDivElement>(null);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("phishing");
  const [channel, setChannel] = useState("email");
  const [reportedUrl, setReportedUrl] = useState("");
  const [state, setState] = useState("");
  const [priority, setPriority] = useState<Priority>("medium");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const incident = await api.createIncident({
        title: title.trim(),
        description: description.trim(),
        category,
        channel,
        reported_url: reportedUrl.trim() || null,
        state: state || null,
        priority: isAnalyst ? priority : undefined,
      });
      navigate(`/incidents/${incident.id}`, {
        replace: true,
        state: { created: true, reference: incident.reference },
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : t("report.submitError"));
      window.setTimeout(() => errorRef.current?.focus(), 0);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="animate-rise space-y-5">
      <PageHeader
        eyebrow={t("report.eyebrow")}
        title={t("report.title")}
        description={t("report.description")}
      />

      <p className="rounded-lg border border-brand/25 bg-brand/[0.06] px-3.5 py-2.5 text-[11.5px] leading-relaxed text-brand">
        {t("report.languageNote")}
      </p>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.55fr)_minmax(0,1fr)]">
        <Card>
          <CardHeader title={t("report.detailsTitle")} description={t("report.detailsDescription")} />
          <form onSubmit={handleSubmit} className="space-y-4 px-5 py-5">
            {error && (
              <div ref={errorRef} tabIndex={-1} className="focus:outline-none">
                <Notice>{error}</Notice>
              </div>
            )}

            <div>
              <label htmlFor="title" className={labelClass}>
                {t("report.titleLabel")}
              </label>
              <input
                id="title"
                name="title"
                required
                minLength={3}
                maxLength={200}
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder={t("report.titlePlaceholder")}
                className={inputClass}
              />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="category" className={labelClass}>
                  {t("report.categoryLabel")}
                </label>
                <select
                  id="category"
                  value={category}
                  onChange={(event) => setCategory(event.target.value)}
                  className={selectClass}
                >
                  {categories.map(([value, key]) => (
                    <option key={value} value={value}>
                      {t(key)}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="channel" className={labelClass}>
                  {t("report.channelLabel")}
                </label>
                <select
                  id="channel"
                  value={channel}
                  onChange={(event) => setChannel(event.target.value)}
                  className={selectClass}
                >
                  {channels.map(([value, key]) => (
                    <option key={value} value={value}>
                      {t(key)}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="state" className={labelClass}>
                  {t("report.stateLabel")}{" "}
                  <span className="normal-case tracking-normal text-muted">
                    {t("common.optional")}
                  </span>
                </label>
                <select
                  id="state"
                  value={state}
                  onChange={(event) => setState(event.target.value)}
                  className={selectClass}
                >
                  <option value="">{t("common.notSpecified")}</option>
                  {states.map((name) => (
                    <option key={name} value={name}>
                      {name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="priority" className={labelClass}>
                  {t("report.priorityLabel")}
                </label>
                <select
                  id="priority"
                  value={priority}
                  onChange={(event) => setPriority(event.target.value as Priority)}
                  className={selectClass}
                  disabled={!isAnalyst}
                  aria-describedby={!isAnalyst ? "priority-help" : undefined}
                >
                  {priorities.map((value) => (
                    <option key={value} value={value}>
                      {t(`priority.${value}` as TranslationKey)}
                    </option>
                  ))}
                </select>
                {!isAnalyst && (
                  <p id="priority-help" className="mt-1 text-[10.5px] text-muted">
                    {t("report.priorityHint")}
                  </p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="url" className={labelClass}>
                {t("report.urlLabel")}{" "}
                <span className="normal-case tracking-normal text-muted">
                  {t("common.optional")}
                </span>
              </label>
              <input
                id="url"
                name="url"
                type="url"
                value={reportedUrl}
                onChange={(event) => setReportedUrl(event.target.value)}
                placeholder="https://suspicious.example/path"
                aria-describedby="url-help"
                className={inputClass}
              />
              <p id="url-help" className="mt-1 text-[10.5px] text-muted">
                {t("report.urlHint")}
              </p>
            </div>

            <div>
              <label htmlFor="description" className={labelClass}>
                {t("report.descriptionLabel")}
              </label>
              <textarea
                id="description"
                name="description"
                required
                minLength={10}
                maxLength={10000}
                rows={7}
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                placeholder={t("report.descriptionPlaceholder")}
                aria-describedby="description-count"
                className={`${inputClass} resize-y leading-relaxed`}
              />
              <p
                id="description-count"
                className="mt-1 text-right font-mono text-[10px] text-muted"
              >
                {t("report.descriptionCount", { count: description.length })}
              </p>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line/70 pt-4">
              <p className="inline-flex items-center gap-1.5 text-[10.5px] text-muted">
                <LockIcon aria-hidden="true" className="h-3.5 w-3.5 text-brand" />
                {t("report.privacyNote")}
              </p>
              <button type="submit" className={btnPrimary} disabled={submitting} aria-busy={submitting}>
                {submitting ? <Spinner /> : <PlusIcon aria-hidden="true" className="h-4 w-4" />}
                {submitting ? t("report.submitting") : t("report.submit")}
              </button>
            </div>
          </form>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader
              title={t("report.nextTitle")}
              description={t("report.nextDescription")}
            />
            <ol className="space-y-3 px-5 py-4">
              {steps.map(([titleKey, bodyKey], index) => (
                <li key={titleKey} className="flex gap-3">
                  <span className="grid h-6 w-6 shrink-0 place-items-center rounded-md border border-brand/25 bg-brand/10 font-mono text-[10px] font-semibold text-brand">
                    {index + 1}
                  </span>
                  <div>
                    <p className="text-[11.5px] font-semibold text-text">{t(titleKey)}</p>
                    <p className="mt-0.5 text-[10.5px] leading-relaxed text-muted">{t(bodyKey)}</p>
                  </div>
                </li>
              ))}
            </ol>
          </Card>

          <Card>
            <CardHeader title={t("report.beforeTitle")} />
            <ul className="divide-y divide-line/50">
              <li className="flex gap-2.5 px-5 py-3 text-[10.5px] leading-relaxed text-muted">
                <AlertTriangleIcon aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-warning" />
                {t("report.check1")}
              </li>
              <li className="flex gap-2.5 px-5 py-3 text-[10.5px] leading-relaxed text-muted">
                <UploadIcon aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-brand" />
                {t("report.check2")}
              </li>
              <li className="flex gap-2.5 px-5 py-3 text-[10.5px] leading-relaxed text-muted">
                <CheckCircleIcon aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                {t("report.check3")}
              </li>
              <li className="flex gap-2.5 px-5 py-3 text-[10.5px] leading-relaxed text-muted">
                <ShieldCheckIcon aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-violet" />
                {t("report.check4")}
              </li>
            </ul>
          </Card>
        </div>
      </div>
    </div>
  );
}
