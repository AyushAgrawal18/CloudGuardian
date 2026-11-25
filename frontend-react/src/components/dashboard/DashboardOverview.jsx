import { useCallback, useEffect, useState } from "react";
import HostHealthPanel from "./HostHealthPanel";
import MetricCharts from "../charts/MetricCharts";
import AnomalyFeed from "./AnomalyFeed";
import {
  Activity,
  Server,
  Cpu,
  MemoryStick,
  HardDrive,
  RefreshCw,
  AlertTriangle,
} from "lucide-react";

import { getHosts, getMetrics } from "../../services/metrics";

function MetricCard({ title, value, unit, icon: Icon, status, description }) {
  return (
    <div className="overview-card">
      <div className="overview-card-top">
        <span>{title}</span>
        <div className="overview-card-icon">
          <Icon size={19} />
        </div>
      </div>

      <div className="overview-card-value">
        {value}
        {unit && <span>{unit}</span>}
      </div>

      <div className="overview-card-bottom">
        <span className={`status-dot ${status || "neutral"}`} />
        <span>{description}</span>
      </div>
    </div>
  );
}

export default function DashboardOverview() {
  const [hosts, setHosts] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchDashboardData = useCallback(async () => {
    try {
      setError("");

      const [hostData, metricData] = await Promise.all([
        getHosts(),
        getMetrics(50),
      ]);

      setHosts(hostData);
      setMetrics(metricData);
    } catch (err) {
      setError(err.message || "Unable to load infrastructure data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();

    const interval = setInterval(fetchDashboardData, 15000);

    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  const latestMetric = metrics[0];

  const healthyHosts = hosts.filter((host) => host.status === "active").length;

  const warningHosts = hosts.filter(
    (host) => host.status === "maintenance",
  ).length;

  const inactiveHosts = hosts.filter(
    (host) => host.status === "inactive",
  ).length;

  const cpu = latestMetric?.cpu_percent;
  const memory = latestMetric?.memory_percent;
  const disk = latestMetric?.disk_percent;

  const getMetricStatus = (value, threshold) => {
    if (value == null) return "neutral";
    if (value >= threshold) return "critical";
    if (value >= threshold * 0.9) return "warning";
    return "healthy";
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <RefreshCw size={22} className="loading-icon" />
        <p>Loading infrastructure data...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-overview">
      <div className="overview-welcome">
        <div>
          <h2>Infrastructure Overview</h2>
          <p>Monitor your hosts and resource utilization.</p>
        </div>

        <button className="refresh-button" onClick={fetchDashboardData}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="dashboard-error">
          <AlertTriangle size={18} />
          <span>{error}</span>
          <button onClick={fetchDashboardData}>Retry</button>
        </div>
      )}

      <div className="overview-grid">
        <MetricCard
          title="Registered Hosts"
          value={hosts.length}
          icon={Server}
          description="Registered infrastructure"
          status="neutral"
        />

        <MetricCard
          title="Active Hosts"
          value={healthyHosts}
          icon={Activity}
          description="Currently active"
          status="healthy"
        />

        <MetricCard
          title="CPU Utilization"
          value={cpu == null ? "--" : cpu.toFixed(1)}
          unit={cpu == null ? "" : "%"}
          icon={Cpu}
          description="Latest collected snapshot"
          status={getMetricStatus(cpu, 85)}
        />

        <MetricCard
          title="Memory Utilization"
          value={memory == null ? "--" : memory.toFixed(1)}
          unit={memory == null ? "" : "%"}
          icon={MemoryStick}
          description="Latest collected snapshot"
          status={getMetricStatus(memory, 85)}
        />

        <MetricCard
          title="Disk Utilization"
          value={disk == null ? "--" : disk.toFixed(1)}
          unit={disk == null ? "" : "%"}
          icon={HardDrive}
          description="Latest collected snapshot"
          status={getMetricStatus(disk, 90)}
        />

        <MetricCard
          title="Other Host States"
          value={warningHosts + inactiveHosts}
          icon={AlertTriangle}
          description={`${warningHosts} maintenance · ${inactiveHosts} inactive`}
          status={inactiveHosts > 0 ? "critical" : "neutral"}
        />
      </div>

      <div className="overview-latest">
        <div>
          <span className="latest-label">MONITORING HOST</span>
          <strong>{latestMetric?.host_id || "Waiting for telemetry"}</strong>
        </div>

        <div>
          <span className="latest-label">LATEST SNAPSHOT</span>
          <strong>
            {latestMetric?.timestamp
              ? new Date(latestMetric.timestamp).toLocaleString()
              : "No metrics available"}
          </strong>
        </div>

        <div>
          <span className="latest-label">METRIC RECORDS</span>
          <strong>{metrics.length}</strong>
        </div>
      </div>
      <MetricCharts />
      <AnomalyFeed />
      <HostHealthPanel />
    </div>
  );
}
