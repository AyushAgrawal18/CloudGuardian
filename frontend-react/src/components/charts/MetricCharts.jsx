import { useCallback, useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { RefreshCw } from "lucide-react";

import { getMetrics, getHosts, getHostHealth } from "../../services/metrics";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler,
);

export default function MetricCharts() {
  const [hosts, setHosts] = useState([]);
  const [selectedHostId, setSelectedHostId] = useState("");
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Load available hosts for the selector.
  useEffect(() => {
    async function loadHosts() {
      try {
        const [registeredHosts, monitoredHosts] = await Promise.all([
          getHosts(),
          getHostHealth(),
        ]);

        const registeredMap = new Map(
          registeredHosts.map((host) => [host.host_id, host]),
        );

        const options = monitoredHosts.map((host) => ({
          host_id: host.host_id,
          name: registeredMap.get(host.host_id)?.name || host.host_id,
        }));

        setHosts(options);

        if (options.length > 0) {
          setSelectedHostId(options[0].host_id);
        }
      } catch (err) {
        setError(err.message || "Unable to load hosts.");
        setLoading(false);
      }
    }

    loadHosts();
  }, []);

  const fetchMetrics = useCallback(async () => {
    if (!selectedHostId) return;

    try {
      setError("");

      const data = await getMetrics(50, selectedHostId);

      // Display records in chronological order.
      setMetrics([...data].reverse());
    } catch (err) {
      setError(err.message || "Unable to load metric history.");
    } finally {
      setLoading(false);
    }
  }, [selectedHostId]);

  // Refresh when the selected host changes.
  useEffect(() => {
    if (!selectedHostId) return;

    setLoading(true);
    fetchMetrics();

    const interval = setInterval(fetchMetrics, 15000);

    return () => clearInterval(interval);
  }, [fetchMetrics, selectedHostId]);

  const labels = metrics.map((item) =>
    new Date(item.timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
  );

  const chartData = {
    labels,
    datasets: [
      {
        label: "CPU",
        data: metrics.map((item) => item.cpu_percent),
        borderColor: "#E9B77D",
        backgroundColor: "rgba(233, 183, 125, 0.10)",
        tension: 0.35,
        pointRadius: 2,
        pointHoverRadius: 5,
        fill: true,
      },
      {
        label: "Memory",
        data: metrics.map((item) => item.memory_percent),
        borderColor: "#60A5FA",
        backgroundColor: "rgba(96, 165, 250, 0.08)",
        tension: 0.35,
        pointRadius: 2,
        pointHoverRadius: 5,
        fill: false,
      },
      {
        label: "Disk",
        data: metrics.map((item) => item.disk_percent),
        borderColor: "#F87171",
        backgroundColor: "rgba(248, 113, 113, 0.08)",
        tension: 0.35,
        pointRadius: 2,
        pointHoverRadius: 5,
        fill: false,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: "index",
      intersect: false,
    },
    plugins: {
      legend: {
        position: "top",
        align: "end",
        labels: {
          color: "#9A9A9E",
          usePointStyle: true,
          boxWidth: 7,
          padding: 20,
          font: {
            family: "DM Sans",
            size: 11,
          },
        },
      },
      tooltip: {
        backgroundColor: "#222225",
        titleColor: "#ECECEC",
        bodyColor: "#ECECEC",
        borderColor: "#3A3A3E",
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: (context) => `${context.dataset.label}: ${context.parsed.y}%`,
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: {
          color: "#69696F",
          maxTicksLimit: 8,
          font: { size: 10 },
        },
        border: { color: "#2A2A2D" },
      },
      y: {
        min: 0,
        max: 100,
        ticks: {
          color: "#69696F",
          callback: (value) => `${value}%`,
          font: { size: 10 },
        },
        grid: {
          color: "rgba(255,255,255,0.05)",
        },
        border: { display: false },
      },
    },
  };

  return (
    <section className="metric-charts-panel">
      <div className="metric-charts-header">
        <div>
          <h2>Resource Utilization</h2>
          <p>Historical CPU, memory and disk usage</p>
        </div>

        <div className="chart-actions">
          <select
            className="host-selector"
            value={selectedHostId}
            onChange={(event) => setSelectedHostId(event.target.value)}
            aria-label="Select monitoring host"
          >
            {hosts.map((host) => (
              <option key={host.host_id} value={host.host_id}>
                {host.name}
              </option>
            ))}
          </select>

          <button
            className="refresh-button"
            onClick={fetchMetrics}
            aria-label="Refresh metric history"
            disabled={!selectedHostId}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div className="chart-message">Loading metric history...</div>
      ) : error ? (
        <div className="chart-message chart-error">{error}</div>
      ) : metrics.length === 0 ? (
        <div className="chart-message">
          No metric history available for this host.
        </div>
      ) : (
        <div className="metric-chart-container">
          <Line data={chartData} options={chartOptions} />
        </div>
      )}

      <div className="chart-footer">
        {selectedHostId
          ? `Host: ${selectedHostId} · ${metrics.length} snapshots`
          : "Select a host to view metric history"}
      </div>
    </section>
  );
}
