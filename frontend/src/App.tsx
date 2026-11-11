import type { ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";

import { AuthProvider, useAuth } from "./auth/AuthContext";
import { AppShell } from "./components/AppShell";
import { Logo } from "./components/Logo";
import { Spinner } from "./components/ui";
import AuditPage from "./pages/AuditPage";
import DashboardsPage from "./pages/DashboardsPage";
import IncidentDetailPage from "./pages/IncidentDetailPage";
import IncidentsPage from "./pages/IncidentsPage";
import IntelligencePage from "./pages/IntelligencePage";
import LoginPage from "./pages/LoginPage";
import OverviewPage from "./pages/OverviewPage";
import ReportPage from "./pages/ReportPage";

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
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <BootScreen />;
  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return <>{children}</>;
}

function PublicOnly({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <BootScreen />;
  if (user) return <Navigate to="/" replace />;
  return <>{children}</>;
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
