import { apiRequest } from "./api";

// Host registration status
export function getHosts() {
  return apiRequest("/api/v1/hosts");
}

// Monitoring health and anomaly counts
export function getHostHealth() {
  return apiRequest("/api/v1/metrics/hosts");
}

// Historical metric snapshots
export function getMetrics(limit = 50, hostId = null) {
  const params = new URLSearchParams({ limit: String(limit) });

  if (hostId) {
    params.set("host_id", hostId);
  }

  return apiRequest(`/api/v1/metrics?${params.toString()}`);
}

// Recent anomalies
export function getAnomalies() {
  return apiRequest("/api/v1/metrics/anomalies");
}
