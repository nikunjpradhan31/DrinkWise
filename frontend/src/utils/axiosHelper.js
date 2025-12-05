import axios from "axios";
export const axiosInstance = axios.create({baseURL: import.meta.env.VITE_BACKEND_URL,headers: {'Content-Type': 'application/json'}});

axiosInstance.interceptors.response.use(
    (response) => response,
    (error) => {
        return Promise.reject(error.response ? error.response.data : error);
    }
);