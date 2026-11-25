import { useCallback, useEffect, useState } from "react";
import { RefreshCw, Server, AlertTriangle, Radio } from "lucide-react";

import { getHosts, getHostHealth } from "../../services/metrics";

const ONLINE_THRESHOLD = 30;
const STALE_THRESHOLD = 90;

function getAgentStatus(timestamp) {
  if (!timestamp) return "offline";

  const ageSeconds = (Date.now() - new Date(timestamp).getTime()) / 1000;

  if (!Number.isFinite(ageSeconds) || ageSeconds < 0) {
    return "offline";
  }

  if (ageSeconds <= ONLINE_THRESHOLD) return "online";
  if (ageSeconds <= STALE_THRESHOLD) return "stale";

  return "offline";
}

function getLastSeen(timestamp) {
  if (!timestamp) return "Never seen";

  const ageSeconds = Math.max(
    0,
    Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000),
  );

  if (ageSeconds < 60) return `${ageSeconds}s ago`;
  if (ageSeconds < 3600) return `${Math.floor(ageSeconds / 60)}m ago`;

  return `${Math.floor(ageSeconds / 3600)}h ago`;
}

function AgentBadge({ timestamp }) {
  const status = getAgentStatus(timestamp);

  return (
    <span className={`agent-badge ${status}`}>
      <span className="agent-dot" />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}

export default function HostHealthPanel() {
  const [hosts, setHosts] = useState([]);
  const [health, setHealth] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [, setHeartbeatTick] = useState(0);

  const fetchHostData = useCallback(async () => {
    try {
      setError("");

      const [hostData, healthData] = await Promise.all([
        getHosts(),
        getHostHealth(),
      ]);

      setHosts(hostData);
      setHealth(healthData);
    } catch (err) {
      setError(err.message || "Unable to load host information.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHostData();

    const interval = setInterval(fetchHostData, 15000);
    return () => clearInterval(interval);
  }, [fetchHostData]);

  // Update elapsed heartbeat time every second.
  useEffect(() => {
    const interval = setInterval(() => {
      setHeartbeatTick((tick) => tick + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const registrationMap = new Map(hosts.map((host) => [host.host_id, host]));

  const statusClass = (status) => {
    const value = (status || "unknown").toLowerCase();

    return ["healthy", "warning", "critical"].includes(value)
      ? value
      : "unknown";
  };

  if (loading) {
    return <div className="host-panel-message">Loading host health...</div>;
  }

  return (
    <section className="host-health-panel">
      <div className="host-panel-header">
        <div>
          <h2>Host Health</h2>
          <p>Registration status and monitoring health</p>
        </div>

        <button
          className="refresh-button"
          onClick={fetchHostData}
          aria-label="Refresh host health"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="host-panel-error">
          <AlertTriangle size={17} />
          {error}
        </div>
      )}

      {!error && health.length === 0 && (
        <div className="host-panel-message">
          No monitoring health records available.
        </div>
      )}

      {health.length > 0 && (
        <div className="host-table-wrapper">
          <table className="host-table">
            <thead>
              <tr>
                <th>HOST</th>
                <th>REGISTRATION</th>
                <th>AGENT</th>
                <th>HEALTH</th>
                <th>ANOMALIES</th>
                <th>LAST METRIC</th>
              </tr>
            </thead>

            <tbody>
              {health.map((item) => {
                const registeredHost = registrationMap.get(item.host_id);
                const timestamp = item.latest_metric_timestamp;

                return (
                  <tr key={item.host_id}>
                    <td>
                      <div className="host-name-cell">
                        <div className="host-icon">
                          <Server size={17} />
                        </div>

                        <div>
                          <strong>
                            {registeredHost?.name || item.host_id}
                          </strong>
                          <span>{item.host_id}</span>
                        </div>
                      </div>
                    </td>

                    <td>
                      <span className="registration-status">
                        {registeredHost?.status || "Unknown"}
                      </span>
                    </td>

                    <td>
                      <div className="agent-status-cell">
                        <AgentBadge timestamp={timestamp} />

                        <span className="agent-last-seen">
                          <Radio size={12} />
                          <span>{getLastSeen(timestamp)}</span>
                        </span>
                      </div>
                    </td>

                    <td>
                      <span
                        className={`health-badge ${statusClass(item.status)}`}
                      >
                        <span className="health-dot" />
                        {item.status || "Unknown"}
                      </span>
                    </td>

                    <td className="anomaly-count">{item.anomaly_count ?? 0}</td>

                    <td className="host-timestamp">
                      {timestamp
                        ? new Date(timestamp).toLocaleString()
                        : "No metrics"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
