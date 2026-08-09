import axios from 'axios';

// Get backend URL from localStorage or use default
const getBackendUrl = () => {
  return import.meta.env.VITE_API_URL || localStorage.getItem('contextos_backend_url') || 'http://127.0.0.1:8000';
};

export const apiClient = axios.create({
  baseURL: getBackendUrl(),
  timeout: 10000, // 10s timeout to prevent indefinite loading state hanging
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT token if available in localStorage
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token') || localStorage.getItem('access_token') || localStorage.getItem('contextos_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Update the base URL dynamically if settings change
export const updateApiBaseUrl = (newUrl: string) => {
  apiClient.defaults.baseURL = newUrl;
};

// API calls
export const api = {
  getStats: () => apiClient.get('/api/v1/evaluation/stats').then(res => res.data),
  getLatest: () => apiClient.get('/api/v1/evaluation/latest').then(res => res.data),
  getAll: (skip = 0, limit = 100) => apiClient.get(`/api/v1/evaluation/?skip=${skip}&limit=${limit}`).then(res => res.data),
  getById: (id: string | number) => apiClient.get(`/api/v1/evaluation/${id}`).then(res => res.data),
};
