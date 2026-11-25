import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, RefreshCw, ShieldAlert, Activity } from "lucide-react";

import { getAnomalies } from "../../services/metrics";

function SeverityBadge({ severity }) {
  const critical = severity?.toLowerCase() === "critical";

  return (
    <span className={`anomaly-severity ${critical ? "critical" : "warning"}`}>
      <span className="severity-dot" />
      {severity || "Warning"}
    </span>
  );
}

export default function AnomalyFeed() {
  const [visibleCount, setVisibleCount] = useState(10);
  const [anomalies, setAnomalies] = useState([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchAnomalies = useCallback(async () => {
    try {
      setError("");
      const data = await getAnomalies();
      setAnomalies(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Unable to load anomalies.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnomalies();

    const interval = setInterval(fetchAnomalies, 30000);
    return () => clearInterval(interval);
  }, [fetchAnomalies]);

  const filteredAnomalies = anomalies.filter((anomaly) => {
    if (filter === "all") return true;
    return anomaly.severity?.toLowerCase() === filter;
  });

  const visibleAnomalies = filteredAnomalies.slice(0, visibleCount);

  const handleFilterChange = (value) => {
    setFilter(value);
    setVisibleCount(10);
  };

  const criticalCount = anomalies.filter(
    (item) => item.severity?.toLowerCase() === "critical",
  ).length;

  const warningCount = anomalies.filter(
    (item) => item.severity?.toLowerCase() === "warning",
  ).length;

  return (
    <section className="anomaly-feed-panel">
      <div className="anomaly-feed-header">
        <div>
          <h2>Recent Anomalies</h2>
          <p>Detected threshold breaches and unusual metric behavior</p>
        </div>

        <button
          className="refresh-button"
          onClick={fetchAnomalies}
          aria-label="Refresh anomalies"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      <div className="anomaly-summary">
        <div className="anomaly-summary-item">
          <ShieldAlert size={18} />
          <span>Critical</span>
          <strong>{criticalCount}</strong>
        </div>

        <div className="anomaly-summary-item">
          <AlertTriangle size={18} />
          <span>Warning</span>
          <strong>{warningCount}</strong>
        </div>

        <div className="anomaly-summary-item">
          <Activity size={18} />
          <span>Total records</span>
          <strong>{anomalies.length}</strong>
        </div>
      </div>

      <div className="anomaly-filter">
        {["all", "critical", "warning"].map((value) => (
          <button
            key={value}
            className={filter === value ? "active" : ""}
            onClick={() => handleFilterChange(value)}
          >
            {value.charAt(0).toUpperCase() + value.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="chart-message">Loading anomalies...</div>
      ) : error ? (
        <div className="dashboard-error">
          <AlertTriangle size={18} />
          <span>{error}</span>
          <button onClick={fetchAnomalies}>Retry</button>
        </div>
      ) : filteredAnomalies.length === 0 ? (
        <div className="chart-message">No anomalies found for this filter.</div>
      ) : (
        <div className="anomaly-list">
          {visibleAnomalies.map((anomaly) => (
            <article className="anomaly-item" key={anomaly.id}>
              <div className="anomaly-item-icon">
                <AlertTriangle size={18} />
              </div>

              <div className="anomaly-item-content">
                <div className="anomaly-item-top">
                  <strong>
                    {anomaly.metric_name?.replaceAll("_", " ") ||
                      "Metric anomaly"}
                  </strong>

                  <SeverityBadge severity={anomaly.severity} />
                </div>

                <p className="anomaly-explanation">{anomaly.explanation}</p>

                <div className="anomaly-metadata">
                  <span>Host: {anomaly.host_id}</span>
                  <span>Observed: {anomaly.actual_value}</span>
                  <span>Threshold: {anomaly.threshold}</span>
                </div>

                <time>{new Date(anomaly.timestamp).toLocaleString()}</time>
              </div>
            </article>
          ))}
        </div>
      )}

      {!loading && !error && filteredAnomalies.length > 0 && (
        <div className="chart-footer">
          <span>
            Showing {visibleAnomalies.length} of {filteredAnomalies.length}{" "}
            anomaly records
          </span>

          <div className="anomaly-pagination">
            {visibleCount < filteredAnomalies.length && (
              <button
                className="show-more-button"
                onClick={() => setVisibleCount((count) => count + 10)}
              >
                Show More
              </button>
            )}

            {visibleCount > 10 && (
              <button
                className="show-less-button"
                onClick={() => setVisibleCount(10)}
              >
                Show Less
              </button>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
