// src/utils/axiosHelper.js
import axios from "axios";

// Base URL comes from Vite env or falls back to localhost
const baseURL =
  import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export const axiosInstance = axios.create({
  baseURL,
  withCredentials: false,
});

// Optional: basic response error logging
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API error:", error?.response || error);
    throw error?.response?.data || error;
  }
);
