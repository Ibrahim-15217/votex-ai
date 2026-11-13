import type { ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";

import { AuthProvider, useAuth } from "./auth/AuthContext";
import { AppShell } from "./components/AppShell";
import { Logo } from "./components/Logo";
import { AlertTriangleIcon } from "./components/icons";
import { Spinner } from "./components/ui";
import AuditPage from "./pages/AuditPage";
import DashboardsPage from "./pages/DashboardsPage";
import IncidentDetailPage from "./pages/IncidentDetailPage";
import IncidentsPage from "./pages/IncidentsPage";
import IntelligencePage from "./pages/IntelligencePage";
import LoginPage from "./pages/LoginPage";
import OverviewPage from "./pages/OverviewPage";
import ReportPage from "./pages/ReportPage";
import ResiliencePage from "./pages/ResiliencePage";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route
            path="/login"
            element={
              <PublicOnly>
                <LoginPage />
              </PublicOnly>
            }
          />
          <Route
            element={
              <ProtectedRoute>
                <AppShell />
              </ProtectedRoute>
            }
          >
            <Route index element={<OverviewPage />} />
            <Route path="incidents" element={<IncidentsPage />} />
            <Route path="incidents/:id" element={<IncidentDetailPage />} />
            <Route path="intelligence" element={<IntelligencePage />} />
            <Route path="dashboards" element={<DashboardsPage />} />
            <Route path="resilience" element={<ResiliencePage />} />
            <Route path="report" element={<ReportPage />} />
            <Route path="audit" element={<AuditPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, loading, unavailable } = useAuth();
  const location = useLocation();

  if (loading) return <BootScreen />;
  if (unavailable) return <ServiceUnavailable />;
  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return <>{children}</>;
}

function PublicOnly({ children }: { children: ReactNode }) {
  const { user, loading, unavailable } = useAuth();
  if (loading) return <BootScreen />;
  if (unavailable) return <ServiceUnavailable />;
  if (user) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function ServiceUnavailable() {
  const { retry, logout } = useAuth();

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-5 bg-void px-6">
      <div aria-hidden="true" className="pointer-events-none fixed inset-0 bg-grid opacity-40" />
      <div className="relative">
        <Logo />
      </div>
      <div className="relative w-full max-w-md rounded-xl border border-line bg-surface/60 p-6 text-center shadow-panel">
        <span className="mx-auto grid h-11 w-11 place-items-center rounded-xl border border-danger/25 bg-danger/10 text-danger">
          <AlertTriangleIcon className="h-5 w-5" />
        </span>
        <p className="mt-3 text-sm font-semibold text-text">The service is temporarily unavailable</p>
        <p className="mt-1.5 text-xs leading-relaxed text-muted">
          We could not reach the Votex service. Your session is still saved — try again, or sign out
          to use a different account.
        </p>
        <div className="mt-4 flex flex-wrap justify-center gap-2">
          <button
            type="button"
            onClick={retry}
            className="inline-flex min-h-[38px] items-center rounded-lg bg-gradient-to-r from-brand to-brand-2 px-3.5 py-2 text-xs font-semibold text-void transition hover:brightness-110"
          >
            Try again
          </button>
          <button
            type="button"
            onClick={logout}
            className="inline-flex min-h-[38px] items-center rounded-lg border border-line bg-surface/60 px-3.5 py-2 text-xs font-medium text-muted transition hover:text-text"
          >
            Sign out
          </button>
        </div>
      </div>
    </div>
  );
}

function BootScreen() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-5 bg-void">
      <div aria-hidden="true" className="pointer-events-none fixed inset-0 bg-grid opacity-40" />
      <div className="relative">
        <Logo />
      </div>
      <div className="relative inline-flex items-center gap-2 rounded-full border border-line bg-surface/60 px-3 py-1.5 text-[11px] text-muted">
        <Spinner className="text-brand" />
        Securing the operations console
      </div>
    </div>
  );
}
