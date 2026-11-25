
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const TOKEN_KEY = "cloudguardian_token";

// Multiple simultaneous 401 responses share one refresh request.
let refreshPromise = null;

async function refreshAccessToken() {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          {
            method: "POST",
            credentials: "include",
          },
        );

        if (!response.ok) {
          sessionStorage.removeItem(TOKEN_KEY);
          return false;
        }

        const data = await response.json();

        if (!data.access_token) {
          sessionStorage.removeItem(TOKEN_KEY);
          return false;
        }

        sessionStorage.setItem(TOKEN_KEY, data.access_token);
        return true;
      } catch {
        sessionStorage.removeItem(TOKEN_KEY);
        return false;
      }
    })().finally(() => {
      refreshPromise = null;
    });
  }

  return refreshPromise;
}

export async function apiRequest(endpoint, options = {}) {
  const token = sessionStorage.getItem(TOKEN_KEY);

  const makeRequest = (accessToken) => {
    const headers = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (accessToken) {
      headers.Authorization = `Bearer ${accessToken}`;
    }

    return fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
      credentials: "include",
    });
  };

  let response = await makeRequest(token);

  const isAuthEndpoint = [
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/logout",
  ].includes(endpoint);

  if (
    response.status === 401 &&
    token &&
    !isAuthEndpoint
  ) {
    const refreshed = await refreshAccessToken();

    if (refreshed) {
      const newToken = sessionStorage.getItem(TOKEN_KEY);
      response = await makeRequest(newToken);
    } else if (typeof window !== "undefined") {
      window.dispatchEvent(
        new Event("cloudguardian:session-expired"),
      );
    }
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      data?.detail || `Request failed with status ${response.status}`,
    );
  }

  return data;
}

export { API_BASE_URL };
