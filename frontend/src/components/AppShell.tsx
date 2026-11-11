import { useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { Logo } from "./Logo";
import {
  ActivityIcon,
  InboxIcon,
  LayersIcon,
  LogOutIcon,
  MenuIcon,
  NetworkIcon,
  PlusIcon,
  ShieldCheckIcon,
  XIcon,
} from "./icons";
import { cn } from "./ui";
import { initials } from "../lib/format";
import { useI18n, type TranslationKey } from "../lib/i18n";

type PageKey = { title: TranslationKey; eyebrow: TranslationKey };

const pageTitles: Record<string, PageKey> = {
  "/": { title: "page.overview.title", eyebrow: "page.overview.eyebrow" },
  "/incidents": { title: "page.incidents.title", eyebrow: "page.incidents.eyebrow" },
  "/intelligence": { title: "page.intelligence.title", eyebrow: "page.intelligence.eyebrow" },
  "/dashboards": { title: "page.dashboards.title", eyebrow: "page.dashboards.eyebrow" },
  "/report": { title: "page.report.title", eyebrow: "page.report.eyebrow" },
  "/audit": { title: "page.audit.title", eyebrow: "page.audit.eyebrow" },
};

const navItems: Array<{
  to: string;
  label: TranslationKey;
  icon: typeof ActivityIcon;
  end: boolean;
  analystOnly?: boolean;
}> = [
  { to: "/", label: "nav.overview", icon: ActivityIcon, end: true },
  { to: "/incidents", label: "nav.incidents", icon: InboxIcon, end: false },
  {
    to: "/intelligence",
    label: "nav.intelligence",
    icon: NetworkIcon,
    end: false,
    analystOnly: true,
  },
  { to: "/dashboards", label: "nav.dashboards", icon: LayersIcon, end: true, analystOnly: true },
  { to: "/report", label: "nav.report", icon: PlusIcon, end: true },
  { to: "/audit", label: "nav.audit", icon: ShieldCheckIcon, end: true, analystOnly: true },
];

const guardrails: TranslationKey[] = [
  "shell.tenantIsolation",
  "shell.reporterScope",
  "shell.evidenceHash",
  "shell.kAnon",
  "shell.offline",
];

export function AppShell() {
  const { user, logout } = useAuth();
  const { lang, setLang, t } = useI18n();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [announcement, setAnnouncement] = useState("");
  const mainRef = useRef<HTMLElement>(null);
  const isFirstRender = useRef(true);

  const detail =
    /^\/incidents\/[^/]+$/.test(location.pathname) && location.pathname !== "/incidents";
  const page = detail
    ? { title: "page.detail.title" as TranslationKey, eyebrow: "page.detail.eyebrow" as TranslationKey }
    : (pageTitles[location.pathname] ?? {
        title: "page.fallback.title" as TranslationKey,
        eyebrow: "page.fallback.eyebrow" as TranslationKey,
      });

  const pageTitle = t(page.title);
  const pageEyebrow = t(page.eyebrow);

  useEffect(() => {
    document.title = `${pageTitle} · Votex AI`;
  }, [pageTitle]);

  useEffect(() => {
    // Skip the very first mount so the browser keeps its initial focus target,
    // then move focus to the main region on every client-side navigation.
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    mainRef.current?.focus();
    setAnnouncement(t("a11y.routeAnnouncement", { page: pageTitle }));
  }, [location.pathname, pageTitle, t]);

  if (!user) return null;

  const visibleNav = navItems.filter((item) => !item.analystOnly || user.role !== "reporter");

  function signOut() {
    logout();
    navigate("/login", { replace: true });
  }

  const nav = (
    <nav className="flex-1 space-y-1 overflow-y-auto px-3" aria-label={t("a11y.primaryNav")}>
      {visibleNav.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) =>
              cn(
                "group flex items-center gap-3 rounded-lg border px-3 py-2.5 text-[13px] font-medium transition",
                isActive
                  ? "border-brand/25 bg-brand/10 text-brand"
                  : "border-transparent text-muted hover:border-line hover:bg-surface-2/60 hover:text-text",
              )
            }
          >
            <Icon className="h-4 w-4" />
            {t(item.label)}
          </NavLink>
        );
      })}

      <div className="!mt-6 space-y-2 rounded-xl border border-line/70 bg-void/40 p-3">
        <p className="text-[9.5px] font-semibold uppercase tracking-[0.16em] text-muted">
          {t("shell.guardrails")}
        </p>
        <ul className="space-y-1.5 text-[10.5px] leading-relaxed text-muted">
          {guardrails.map((key) => (
            <li key={key} className="flex gap-2">
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-success" />
              {t(key)}
            </li>
          ))}
        </ul>
        <span className="inline-flex items-center rounded-full border border-success/25 bg-success/[0.08] px-2 py-0.5 text-[9.5px] font-medium text-success">
          {t("common.syntheticOnly")}
        </span>
      </div>
    </nav>
  );

  return (
    <div className="min-h-screen bg-void">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-brand focus:px-3 focus:py-2 focus:text-sm focus:font-semibold focus:text-void"
      >
        {t("common.skipToContent")}
      </a>

      <p className="sr-only" role="status" aria-live="polite">
        {announcement}
      </p>

      <div aria-hidden="true" className="pointer-events-none fixed inset-0 bg-grid opacity-30" />
      <div
        aria-hidden="true"
        className="pointer-events-none fixed -left-48 top-0 h-[30rem] w-[30rem] rounded-full bg-brand/[0.06] blur-3xl"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none fixed -right-56 bottom-0 h-[34rem] w-[34rem] rounded-full bg-violet/[0.06] blur-3xl"
      />

      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[248px] flex-col border-r border-line/70 bg-surface/40 backdrop-blur-xl lg:flex">
        <div className="border-b border-line/70 px-5 py-5">
          <Logo />
        </div>
        {nav}
        <div className="border-t border-line/70 p-3">
          <UserCard onSignOut={signOut} />
        </div>
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label={t("a11y.closeNav")}
            className="absolute inset-0 bg-void/80 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="relative flex h-full w-[280px] flex-col border-r border-line bg-surface">
            <div className="flex items-center justify-between border-b border-line/70 px-5 py-5">
              <Logo />
              <button
                type="button"
                onClick={() => setMobileOpen(false)}
                className="grid h-10 w-10 place-items-center rounded-md text-muted transition hover:text-text"
                aria-label={t("a11y.closeNav")}
              >
                <XIcon className="h-4 w-4" />
              </button>
            </div>
            {nav}
            <div className="border-t border-line/70 p-3">
              <UserCard onSignOut={signOut} />
            </div>
          </aside>
        </div>
      )}

      <div className="relative lg:pl-[248px]">
        <header className="sticky top-0 z-20 border-b border-line/70 bg-void/75 backdrop-blur-xl">
          <div className="flex items-center gap-2.5 px-4 py-3.5 sm:gap-3 sm:px-6 lg:px-8">
            <button
              type="button"
              onClick={() => setMobileOpen(true)}
              className="grid h-10 w-10 place-items-center rounded-md border border-line text-muted transition hover:text-text lg:hidden"
              aria-label={t("a11y.openNav")}
              aria-expanded={mobileOpen}
            >
              <MenuIcon className="h-4 w-4" />
            </button>

            <div className="min-w-0 flex-1">
              <p className="text-[9.5px] font-semibold uppercase tracking-[0.18em] text-muted">
                {pageEyebrow}
              </p>
              <p className="truncate text-sm font-semibold text-text">{pageTitle}</p>
            </div>

            <LanguageSwitcher
              lang={lang}
              onChange={setLang}
              label={t("a11y.languageGroup")}
            />

            <span className="hidden items-center gap-2 rounded-full border border-success/25 bg-success/[0.08] px-3 py-1.5 text-[10.5px] font-medium text-success xl:inline-flex">
              <span className="h-1.5 w-1.5 animate-breathe rounded-full bg-success" />
              {t("shell.phase")}
            </span>
            <span className="hidden rounded-full border border-line bg-surface/60 px-3 py-1.5 font-mono text-[10px] text-muted lg:inline-flex">
              {user.organisation.slug}
            </span>
          </div>
        </header>

        <main
          id="main"
          ref={mainRef}
          tabIndex={-1}
          className="mx-auto w-full max-w-[1440px] scroll-mt-24 px-4 py-6 focus:outline-none sm:px-6 lg:px-8 lg:py-8"
        >
          <Outlet />
        </main>

        <footer className="mx-auto flex w-full max-w-[1440px] flex-col gap-1 px-4 pb-6 text-[10px] text-muted/80 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <span>{t("shell.footerHackathon")}</span>
          <span>{t("shell.footerDisclaimer")}</span>
        </footer>
      </div>
    </div>
  );
}

function UserCard({ onSignOut }: { onSignOut: () => void }) {
  const { user } = useAuth();
  const { t } = useI18n();
  if (!user) return null;

  const roleLabel = t(`role.${user.role}` as TranslationKey);

  return (
    <div className="rounded-xl border border-line/70 bg-void/50 p-3">
      <div className="flex items-center gap-2.5">
        <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-brand/25 bg-brand/10 text-[11px] font-semibold text-brand">
          {initials(user.full_name)}
        </span>
        <div className="min-w-0 flex-1">
          <p className="truncate text-xs font-semibold text-text">{user.full_name}</p>
          <p className="truncate text-[10px] text-muted">
            {roleLabel} · {user.organisation.name}
          </p>
        </div>
        <button
          type="button"
          onClick={onSignOut}
          title={t("a11y.signOut")}
          aria-label={t("a11y.signOut")}
          className="grid h-8 w-8 place-items-center rounded-md text-muted transition hover:bg-surface-2 hover:text-danger"
        >
          <LogOutIcon className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
