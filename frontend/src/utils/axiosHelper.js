// src/utils/axiosHelper.js
import axios from "axios";

// Helper function to decode JWT token and check expiration
function decodeJWT(token) {
  try {
    if (!token) return null;
    
    // Split token to get payload (JWT tokens have 3 parts: header.payload.signature)
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    // Decode base64 payload
    const payload = parts[1];
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(decoded);
  } catch (error) {
    console.error("Failed to decode JWT:", error);
    return null;
  }
}

// Check if token is expired
export function isTokenExpired(token) {
  const decoded = decodeJWT(token);
  if (!decoded || !decoded.exp) return true;
  
  // Convert expiration time from seconds to milliseconds and compare with current time
  const expirationTime = decoded.exp * 1000;
  const currentTime = Date.now();
  
  return currentTime >= expirationTime;
  //return False
}

// Base URL comes from Vite env or falls back to localhost
const baseURL =
  import.meta.env.VITE_BACKEND_URL || "http://localhost:8000/api";

export const axiosInstance = axios.create({
  baseURL,
  withCredentials: false,
});

// Request interceptor to add Authorization header and check token expiration
axiosInstance.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const storedUser = localStorage.getItem("drinkwise_user");
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        if (user?.access_token) {
          
          // Check if token is expired
          if (isTokenExpired(user.access_token)) {
            console.log("Token expired, logging out user...");
            
            // Remove user from localStorage
            localStorage.removeItem("drinkwise_user");
            
            // Remove Authorization header
            delete axiosInstance.defaults.headers.common["Authorization"];
            
            // Redirect to login page
            if (typeof window !== "undefined") {
              window.location.href = "/login";
            }
            
            // Reject the request to prevent it from being sent
            return Promise.reject(new Error("Token expired"));
          }
          
          // Add Authorization header if not already present
          if (!config.headers?.Authorization) {
            config.headers.Authorization = `Bearer ${user.access_token}`;
          }
        }
      } catch (error) {
        console.error("Failed to parse user from localStorage:", error);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token expiration and automatic logout
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API error:", error?.response || error);
    
    // Check for 401 Unauthorized errors (token expired or invalid)
    if (error?.response?.status === 401) {
      console.log("Token expired or invalid, logging out user...");
      
      // Remove user from localStorage
      localStorage.removeItem("drinkwise_user");
      
      // Remove Authorization header
      delete axiosInstance.defaults.headers.common["Authorization"];
      
      // Redirect to login page
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
    
    throw error?.response?.data || error;
  }
);
