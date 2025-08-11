import axios from 'axios';

// Create axios instance with base URL from environment
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, config.data);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      data: error.response?.data,
      message: error.message,
    });
    return Promise.reject(error);
  }
);

// Helper methods
export const apiClient = {
  // Health check
  async getHealth() {
    const response = await api.get('/health');
    return response.data;
  },

  // Discovery
  async postDiscovery(body) {
    const response = await api.post('/discovery', body);
    return response.data;
  },

  // Activation
  async postActivation(body) {
    const response = await api.post('/activation', body);
    return response.data;
  },

  // Status
  async getStatus(id) {
    const response = await api.get(`/status/${id}`);
    return response.data;
  },

  // Pending activations
  async getPendingActivations() {
    const response = await api.get('/status/list/pending');
    return response.data;
  },

  // Simulate status transition
  async simulateStatusTransition(id) {
    const response = await api.post(`/status/${id}/simulate`);
    return response.data;
  },

  // Bulk status simulation
  async simulateBulkTransitions(maxTransitions = 10) {
    const response = await api.post('/status/simulate/bulk', null, {
      params: { max_transitions: maxTransitions }
    });
    return response.data;
  },

  // Force status
  async forceStatus(id, status) {
    const response = await api.post(`/status/${id}/force`, null, {
      params: { status }
    });
    return response.data;
  },
};

export default apiClient;
