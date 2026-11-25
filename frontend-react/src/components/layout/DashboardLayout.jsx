import {
  Activity,
  LayoutDashboard,
  Server,
  ChartLine,
  AlertTriangle,
  LogOut,
  ShieldCheck,
  Bell,
  Menu,
} from "lucide-react";

import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

const navigation = [
  { label: "Overview", path: "/dashboard", icon: LayoutDashboard },
  { label: "Hosts", path: "/hosts", icon: Server },
  { label: "Metrics", path: "/metrics", icon: ChartLine },
  { label: "Anomalies", path: "/anomalies", icon: AlertTriangle },
];

export default function DashboardLayout({ children, title = "Overview" }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="dashboard-shell">
      <aside className="dashboard-sidebar">
        <div className="dashboard-brand">
          <div className="dashboard-brand-icon">
            <Activity size={23} />
          </div>
          <span>
            Cloud<span>Guardian</span>
          </span>
        </div>

        <div className="sidebar-section-label">WORKSPACE</div>

        <nav className="sidebar-navigation">
          {navigation.map(({ label, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/dashboard"}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
            >
              <Icon size={19} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-security">
            <ShieldCheck size={19} />
            <div>
              <strong>Infrastructure</strong>
              <span>Monitoring active</span>
            </div>
          </div>

          <button className="sidebar-logout" onClick={handleLogout}>
            <LogOut size={18} />
            <span>Sign out</span>
          </button>
        </div>
      </aside>

      <div className="dashboard-main">
        <header className="dashboard-header">
          <div className="dashboard-header-left">
            <button className="mobile-menu" aria-label="Open navigation">
              <Menu size={21} />
            </button>

            <div>
              <h1>{title}</h1>
              <p>Monitor your infrastructure in real time</p>
            </div>
          </div>

          <div className="dashboard-header-actions">
            <button className="header-icon-button" aria-label="Notifications">
              <Bell size={19} />
            </button>

            <div className="dashboard-avatar">CG</div>
          </div>
        </header>

        <main className="dashboard-content">{children}</main>
      </div>
    </div>
  );
}
