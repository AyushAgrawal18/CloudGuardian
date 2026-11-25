import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import Signup from "./pages/Signup";

import DashboardLayout from "./components/layout/DashboardLayout";
import DashboardOverview from "./components/dashboard/DashboardOverview";
import HostHealthPanel from "./components/dashboard/HostHealthPanel";
import MetricCharts from "./components/charts/MetricCharts";
import AnomalyFeed from "./components/dashboard/AnomalyFeed";

function ProtectedRoute({ children }) {
  const { isAuthenticated, isInitializing } = useAuth();

  if (isInitializing) {
    return <div className="auth-loading">Restoring your session...</div>;
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function PublicRoute({ children }) {
  const { isAuthenticated, isInitializing } = useAuth();

  if (isInitializing) {
    return <div className="auth-loading">Restoring your session...</div>;
  }

  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
}

function DashboardHome() {
  return (
    <DashboardLayout title="Overview">
      <DashboardOverview />
    </DashboardLayout>
  );
}

function HostsPage() {
  return (
    <DashboardLayout title="Hosts">
      <HostHealthPanel />
    </DashboardLayout>
  );
}

function MetricsPage() {
  return (
    <DashboardLayout title="Metrics">
      <MetricCharts />
    </DashboardLayout>
  );
}

function AnomaliesPage() {
  return (
    <DashboardLayout title="Anomalies">
      <AnomalyFeed />
    </DashboardLayout>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />

        <Route
          path="/signup"
          element={
            <PublicRoute>
              <Signup />
            </PublicRoute>
          }
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardHome />
            </ProtectedRoute>
          }
        />

        <Route
          path="/hosts"
          element={
            <ProtectedRoute>
              <HostsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/metrics"
          element={
            <ProtectedRoute>
              <MetricsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/anomalies"
          element={
            <ProtectedRoute>
              <AnomaliesPage />
            </ProtectedRoute>
          }
        />

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
