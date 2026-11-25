import { apiRequest } from "./api";

const TOKEN_KEY = "cloudguardian_token";

export async function registerUser(userData) {
  return apiRequest("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(userData),
  });
}

export async function loginUser(credentials) {
  const data = await apiRequest("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  });

  sessionStorage.setItem(TOKEN_KEY, data.access_token);
  return data;
}

export async function restoreSession() {
  try {
    const data = await apiRequest("/api/v1/auth/refresh", {
      method: "POST",
    });

    if (!data?.access_token) {
      sessionStorage.removeItem(TOKEN_KEY);
      return null;
    }

    sessionStorage.setItem(TOKEN_KEY, data.access_token);
    return data.access_token;
  } catch {
    sessionStorage.removeItem(TOKEN_KEY);
    return null;
  }
}

export async function logoutUser() {
  try {
    await apiRequest("/api/v1/auth/logout", {
      method: "POST",
    });
  } finally {
    sessionStorage.removeItem(TOKEN_KEY);
  }
}

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function isAuthenticated() {
  return Boolean(getToken());
}
