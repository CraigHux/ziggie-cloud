import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:54112/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      // Error in request setup
      console.error('Request Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// API methods
export const systemAPI = {
  getStats: () => api.get('/system/stats'),
  getProcesses: () => api.get('/system/processes'),
  getPorts: () => api.get('/system/ports'),
  getInfo: () => api.get('/system/info'),
};

export const servicesAPI = {
  getAll: () => api.get('/services'),
  getStatus: (serviceName) => api.get(`/services/${serviceName}/status`),
  start: (serviceName) => api.post(`/services/${serviceName}/start`),
  stop: (serviceName) => api.post(`/services/${serviceName}/stop`),
  restart: (serviceName) => api.post(`/services/${serviceName}/restart`),
  getLogs: (serviceName, lines = 100) => api.get(`/services/${serviceName}/logs?lines=${lines}`),
};

export const agentsAPI = {
  getSummary: () => api.get('/agents/stats'),
  getAll: () => api.get('/agents'),
  getById: (agentId) => api.get(`/agents/${agentId}`),
};

export const knowledgeAPI = {
  getRecent: (limit = 10) => api.get(`/knowledge/recent?limit=${limit}`),
  search: (query) => api.post('/knowledge/search', { query }),
  getStats: () => api.get('/knowledge/stats'),
  getFiles: (page = 1, limit = 20, type = '', sort = 'name') =>
    api.get(`/knowledge/files?page=${page}&limit=${limit}&type=${type}&sort=${sort}`),
  getCreators: () => api.get('/knowledge/creators'),
  triggerScan: () => api.post('/knowledge/scan'),
  getJobHistory: (limit = 10) => api.get(`/knowledge/jobs/history?limit=${limit}`),
};

export const apiUsageAPI = {
  getStats: () => api.get('/api-usage/stats'),
  getHistory: (provider, days = 7) => api.get(`/api-usage/${provider}/history?days=${days}`),
};

export default api;
