import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  loginUser,
  logoutUser,
  registerUser,
  getToken,
  restoreSession,
} from "../services/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(getToken);
  const [isInitializing, setIsInitializing] = useState(!getToken());

  const logout = useCallback(async () => {
    // Update the UI immediately; clear the server cookie asynchronously.
    setToken(null);
    try {
      await logoutUser();
    } catch (error) {
      console.error("Logout request failed:", error);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;

    const handleSessionExpired = () => {
      setToken(null);
    };

    window.addEventListener(
      "cloudguardian:session-expired",
      handleSessionExpired,
    );

    const initializeSession = async () => {
      if (getToken()) {
        if (isMounted) setIsInitializing(false);
        return;
      }

      const restoredToken = await restoreSession();

      if (isMounted) {
        setToken(restoredToken);
        setIsInitializing(false);
      }
    };

    initializeSession();

    return () => {
      isMounted = false;
      window.removeEventListener(
        "cloudguardian:session-expired",
        handleSessionExpired,
      );
    };
  }, []);

  const login = async (credentials) => {
    const data = await loginUser(credentials);
    setToken(data.access_token);
    return data;
  };

  const signup = async (userData) => {
    return registerUser(userData);
  };

  const value = {
    token,
    isAuthenticated: Boolean(token),
    isInitializing,
    login,
    signup,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}
