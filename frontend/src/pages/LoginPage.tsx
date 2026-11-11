import { useState, type FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { LanguageSwitcher } from "../components/LanguageSwitcher";
import { Logo } from "../components/Logo";
import {
  ArrowRightIcon,
  EyeIcon,
  EyeOffIcon,
  LinkIcon,
  LockIcon,
  ScanIcon,
  ShieldCheckIcon,
} from "../components/icons";
import { Spinner } from "../components/ui";
import { useI18n } from "../lib/i18n";

const DEMO_PASSWORD = "VotexDemo!23";

const demoAccounts = [
  { role: "admin", email: "admin@votex.demo" },
  { role: "analyst", email: "analyst@votex.demo" },
  { role: "reporter", email: "reporter@votex.demo" },
  { role: "commission", email: "analyst@inec.demo" },
] as const;

export default function LoginPage() {
  const { login } = useAuth();
  const { lang, setLang, t } = useI18n();
  const navigate = useNavigate();
  const location = useLocation();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("admin@votex.demo");
  const [password, setPassword] = useState(DEMO_PASSWORD);
  const [notice, setNotice] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function changeLanguage(next: typeof lang) {
    setLang(next);
    setNotice(false);
    setError(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setNotice(false);
    setError(null);
    setSubmitting(true);

    try {
      await login(email.trim().toLowerCase(), password);
      const state = location.state as { from?: string } | null;
      navigate(state?.from && state.from !== "/login" ? state.from : "/", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : t("login.invalidCredentials"));
    } finally {
      setSubmitting(false);
    }
  }

  function accountRole(role: (typeof demoAccounts)[number]["role"]): string {
    if (role === "commission") return `${t("role.analyst")} · INEC`;
    return t(`role.${role}`);
  }

  const features = [
    {
      icon: <ScanIcon className="h-5 w-5" />,
      title: t("login.feature1Title"),
      body: t("login.feature1Body"),
    },
    {
      icon: <ShieldCheckIcon className="h-5 w-5" />,
      title: t("login.feature2Title"),
      body: t("login.feature2Body"),
    },
    {
      icon: <LockIcon className="h-5 w-5" />,
      title: t("login.feature3Title"),
      body: t("login.feature3Body"),
    },
  ];

  const fieldClass =
    "w-full rounded-lg border border-line bg-void/60 px-3.5 py-2.5 text-sm text-text placeholder:text-muted/80 transition focus:border-brand/60 focus:bg-void/80 focus:outline-none focus:ring-2 focus:ring-brand/20";

  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden bg-void">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-brand focus:px-3 focus:py-2 focus:text-sm focus:font-semibold focus:text-void"
      >
        {t("common.skipToContent")}
      </a>

      {/* Background layers */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0 bg-grid opacity-50" />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -left-40 -top-56 h-[38rem] w-[38rem] rounded-full bg-brand/10 blur-3xl"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -bottom-64 -right-40 h-[42rem] w-[42rem] rounded-full bg-violet/10 blur-3xl"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-brand/[0.06] to-transparent"
      />
      <div aria-hidden="true" className="absolute inset-x-0 top-0 h-px hairline" />

      <header className="relative z-10 mx-auto flex w-full max-w-7xl flex-wrap items-center justify-between gap-4 px-5 py-5 sm:px-8 lg:px-10 lg:py-7">
        <Logo />
        <div className="flex items-center gap-2.5 sm:gap-3">
          <span className="hidden items-center gap-2 rounded-full border border-success/25 bg-success/[0.08] px-3 py-1.5 text-[11px] font-medium text-success sm:inline-flex">
            <span className="h-1.5 w-1.5 animate-breathe rounded-full bg-success" />
            {t("login.status")}
          </span>
          <LanguageSwitcher
            lang={lang}
            onChange={changeLanguage}
            label={t("a11y.languageGroup")}
          />
        </div>
      </header>

      <main
        id="main"
        tabIndex={-1}
        className="relative z-10 mx-auto grid w-full max-w-7xl flex-1 items-center gap-12 px-5 pb-14 pt-6 focus:outline-none sm:px-8 lg:grid-cols-[minmax(0,1.08fr)_minmax(0,0.92fr)] lg:gap-16 lg:px-10 lg:pb-20 lg:pt-10"
      >
        {/* Narrative column */}
        <section aria-labelledby="hero-title" className="animate-rise">
          <p className="inline-flex items-center gap-2.5 text-[10px] font-semibold uppercase tracking-[0.22em] text-brand/90 sm:text-[11px]">
            <span className="h-px w-7 bg-brand/70" />
            {t("login.track")}
          </p>

          <h1
            id="hero-title"
            className="mt-5 max-w-2xl text-balance text-[2.1rem] font-semibold leading-[1.06] tracking-[-0.02em] text-text sm:text-5xl lg:text-[3.4rem]"
          >
            {t("login.heroTitleA")}{" "}
            <span className="bg-gradient-to-r from-brand via-brand-2 to-violet bg-clip-text text-transparent">
              {t("login.heroTitleB")}
            </span>
          </h1>

          <p className="mt-5 max-w-xl text-sm leading-relaxed text-muted sm:text-base">
            {t("login.heroSubtitle")}
          </p>

          <ul className="mt-8 grid max-w-xl gap-2.5 sm:grid-cols-3">
            {features.map((feature) => (
              <li
                key={feature.title}
                className="rounded-xl border border-line/70 bg-surface/40 p-3.5 transition hover:border-line hover:bg-surface/60"
              >
                <span className="text-brand">{feature.icon}</span>
                <h2 className="mt-2.5 text-[13px] font-semibold text-text">{feature.title}</h2>
                <p className="mt-1 text-[11.5px] leading-relaxed text-muted">{feature.body}</p>
              </li>
            ))}
          </ul>

          <div className="mt-8 max-w-xl overflow-hidden rounded-xl border border-line/80 bg-surface/30">
            <div className="flex items-center justify-between border-b border-line/70 px-4 py-2.5">
              <span className="inline-flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-muted">
                <span className="h-1.5 w-1.5 animate-breathe rounded-full bg-brand" />
                {t("login.signalTitle")}
              </span>
              <span className="font-mono text-[10px] text-muted/80">{t("login.version")}</span>
            </div>
            <dl className="grid grid-cols-3 divide-x divide-line/70">
              <Metric label={t("login.metricReports")} value="128" tone="text-text" />
              <Metric label={t("login.metricLinked")} value="09" tone="text-brand" />
              <Metric label={t("login.metricAudit")} value="100%" tone="text-success" />
            </dl>
            <p className="border-t border-line/70 px-4 py-2 text-[10px] text-muted/80">
              {t("login.syntheticPreview")}
            </p>
          </div>
        </section>

        {/* Authentication column */}
        <section
          aria-labelledby="login-title"
          className="w-full animate-rise lg:justify-self-end"
          style={{ animationDelay: "90ms" }}
        >
          <div className="mx-auto w-full max-w-md rounded-2xl bg-gradient-to-b from-brand/30 via-line/80 to-violet/20 p-px shadow-panel">
            <div className="glass-panel rounded-[15px] px-5 py-6 sm:px-7 sm:py-7">
              <div className="flex items-center justify-between gap-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted">
                <span className="inline-flex items-center gap-1.5">
                  <LockIcon className="h-3.5 w-3.5 text-brand" />
                  {t("login.secureAccess")}
                </span>
                <span className="font-mono tracking-[0.12em] text-success">TLS · DEMO</span>
              </div>

              <div className="mt-6 flex items-start gap-3">
                <span className="mt-0.5 grid h-10 w-10 shrink-0 place-items-center rounded-lg border border-brand/25 bg-brand/10 text-brand">
                  <ShieldCheckIcon className="h-5 w-5" />
                </span>
                <div>
                  <h2 id="login-title" className="text-lg font-semibold tracking-tight text-text">
                    {t("login.signInTitle")}
                  </h2>
                  <p className="mt-1 text-xs leading-relaxed text-muted">
                    {t("login.signInSubtitle")}
                  </p>
                </div>
              </div>

              <form className="mt-6 space-y-4" onSubmit={handleSubmit} noValidate>
                <div>
                  <label
                    htmlFor="email"
                    className="mb-1.5 block text-[10px] font-semibold uppercase tracking-[0.14em] text-muted"
                  >
                    {t("login.emailLabel")}
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="username"
                    required
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder={t("login.emailPlaceholder")}
                    aria-invalid={error ? true : undefined}
                    aria-describedby={error ? "login-error" : undefined}
                    className={fieldClass}
                  />
                </div>

                <div>
                  <label
                    htmlFor="password"
                    className="mb-1.5 block text-[10px] font-semibold uppercase tracking-[0.14em] text-muted"
                  >
                    {t("login.passwordLabel")}
                  </label>
                  <div className="relative">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      autoComplete="current-password"
                      required
                      minLength={8}
                      value={password}
                      onChange={(event) => setPassword(event.target.value)}
                      placeholder={t("login.passwordPlaceholder")}
                      aria-invalid={error ? true : undefined}
                      aria-describedby={error ? "login-error" : undefined}
                      className={`${fieldClass} pr-11`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((visible) => !visible)}
                      aria-label={
                        showPassword ? t("login.hidePassword") : t("login.showPassword")
                      }
                      aria-pressed={showPassword}
                      className="absolute right-1 top-1/2 grid h-9 w-9 -translate-y-1/2 place-items-center rounded-md text-muted transition hover:text-text"
                    >
                      {showPassword ? (
                        <EyeOffIcon className="h-4 w-4" />
                      ) : (
                        <EyeIcon className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between gap-3">
                  <label className="inline-flex cursor-pointer items-center gap-2 text-xs text-muted">
                    <input
                      type="checkbox"
                      className="h-4 w-4 rounded border-line bg-void accent-brand"
                    />
                    {t("login.remember")}
                  </label>
                  <button
                    type="button"
                    onClick={() => setNotice(true)}
                    className="rounded text-xs font-medium text-brand transition hover:text-brand/80"
                  >
                    {t("login.forgot")}
                  </button>
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  aria-busy={submitting}
                  className="group inline-flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-brand to-brand-2 px-4 py-2.5 text-sm font-semibold text-void shadow-glow transition hover:brightness-110 active:translate-y-px disabled:cursor-not-allowed disabled:opacity-70"
                >
                  {submitting ? (
                    <Spinner className="text-void" />
                  ) : (
                    <ArrowRightIcon className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                  )}
                  {submitting ? t("login.signingIn") : t("login.signIn")}
                </button>

                {error && (
                  <p
                    id="login-error"
                    role="alert"
                    className="rounded-lg border border-danger/25 bg-danger/[0.08] px-3 py-2.5 text-[11px] leading-relaxed text-danger"
                  >
                    {error}
                  </p>
                )}

                {notice && (
                  <p
                    role="status"
                    className="rounded-lg border border-warning/25 bg-warning/[0.08] px-3 py-2.5 text-[11px] leading-relaxed text-warning"
                  >
                    {t("login.phaseNotice")}
                  </p>
                )}
              </form>

              <div className="mt-5 rounded-xl border border-line/80 bg-void/40 p-3.5">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-muted">
                    {t("login.demoTitle")}
                  </p>
                  <code className="font-mono text-[10px] text-brand">
                    {t("login.demoPasswordLabel")}: {DEMO_PASSWORD}
                  </code>
                </div>
                <ul className="mt-2.5 space-y-0.5">
                  {demoAccounts.map((account) => (
                    <li key={account.email}>
                      <button
                        type="button"
                        onClick={() => {
                          setEmail(account.email);
                          setPassword(DEMO_PASSWORD);
                          setNotice(false);
                          setError(null);
                        }}
                        className="group flex w-full items-center justify-between gap-3 rounded-md px-2 py-1.5 text-left transition hover:bg-surface-2"
                      >
                        <span className="inline-flex items-center gap-2">
                          <span className="h-1 w-1 rounded-full bg-brand/70" />
                          <span className="text-[11px] text-muted transition group-hover:text-text">
                            {accountRole(account.role)}
                          </span>
                        </span>
                        <span className="truncate font-mono text-[10px] text-muted/80 transition group-hover:text-brand">
                          {account.email}
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
                <p className="mt-2 text-[10px] leading-relaxed text-muted/80">{t("login.demoBody")}</p>
              </div>

              <p className="mt-4 inline-flex items-start gap-1.5 text-[10px] leading-relaxed text-muted/80">
                <LinkIcon className="mt-0.5 h-3 w-3 shrink-0 text-brand/70" />
                {t("login.securityNote")}
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer className="relative z-10 border-t border-line/60 bg-void/40">
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-1.5 px-5 py-4 text-[10px] text-muted/80 sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:px-10">
          <span>{t("login.footerDisclosure")}</span>
          <span>{t("login.notAffiliated")}</span>
        </div>
      </footer>
    </div>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone: string }) {
  return (
    <div className="flex flex-col-reverse px-4 py-3">
      <dt className="mt-0.5 text-[9.5px] uppercase tracking-[0.1em] text-muted/80">{label}</dt>
      <dd className={`font-mono text-lg font-semibold leading-none ${tone}`}>{value}</dd>
    </div>
  );
}
