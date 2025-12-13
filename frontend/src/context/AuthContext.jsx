// src/context/AuthContext.jsx
import React, {
  createContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import { axiosInstance, isTokenExpired } from "../utils/axiosHelper";

export const AuthContext = createContext(undefined);

const STORAGE_KEY = "drinkwise_user";

export const AuthContextProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState(null);

  // Load from localStorage on mount
    useEffect(() => {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          
          // Check if token is expired before setting user
          if (parsed?.access_token) {
            const isExpired = isTokenExpired(parsed.access_token);
            if (isExpired) {
              console.log("Token expired on page load, logging out user...");
              localStorage.removeItem(STORAGE_KEY);
              setUser(null);
              return;
            }
          }
          
          setUser(parsed);
          saveUser(parsed)
          console.log("User loaded from localStorage", parsed);
          // Authorization header is now handled by axios interceptor automatically
        } catch {
          localStorage.removeItem(STORAGE_KEY);
        }
      }
    }, []);

  const saveUser = (data) => {
    setUser(data);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    if (data?.access_token) {
      axiosInstance.defaults.headers.common["Authorization"] =
        `Bearer ${data.access_token}`;
    }
  };

  // POST /auth/register
  const registerUser = useCallback(async (payload) => {
    setAuthLoading(true);
    setAuthError(null);
    try {
      const response = await axiosInstance.post("/auth/register", payload);
      const data = response.data;
      saveUser(data);
      return data;
    } catch (err) {
      setAuthError(err?.message || err?.error || "Registration failed");
      throw err;
    } finally {
      setAuthLoading(false);
    }
  }, []);

  // POST /auth/login
  const loginUser = useCallback(async (payload) => {
    setAuthLoading(true);
    setAuthError(null);
    try {
      const response = await axiosInstance.post("/auth/login", payload);
      const data = response.data;
      saveUser(data);
      return data;
    } catch (err) {
      setAuthError(err?.message || err?.error || "Login failed");
      throw err;
    } finally {
      setAuthLoading(false);
    }
  }, []);

  // GET /auth/me
  const fetchMe = useCallback(async () => {
    if (!user?.access_token) return null;
    try {
      const response = await axiosInstance.get("/auth/me");
      const data = response.data;
      saveUser({ ...user, ...data });
      return data;
    } catch (err) {
      console.error(err);
      return null;
    }
  }, [user]);

  // PUT /auth/me
  const updateMe = useCallback(
    async (payload) => {
      if (!user?.access_token) throw new Error("Not authenticated");
      const response = await axiosInstance.put("/auth/me", payload);
      const data = response.data;
      saveUser({ ...user, ...data });
      return data;
    },
    [user]
  );

  // POST /auth/logout
  const logoutUser = useCallback(async () => {
    try {
      await axiosInstance.post("/auth/logout");
    } catch (e) {
      console.error(e);
    }
    localStorage.removeItem(STORAGE_KEY);
    setUser(null);
    delete axiosInstance.defaults.headers.common["Authorization"];
  }, []);

  const value = {
    user,
    authLoading,
    authError,
    loginUser,
    registerUser,
    fetchMe,
    updateMe,
    logoutUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
