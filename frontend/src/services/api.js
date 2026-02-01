/**
 * API service for communicating with the backend.
 * Handles all HTTP requests using Axios.
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 second timeout for sync operations
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const documentAPI = {
  // List documents with filters
  listDocuments: (params = {}) => {
    return api.get('/api/documents', { params });
  },

  // Get single document by ID
  getDocument: (id) => {
    return api.get(`/api/documents/${id}`);
  },

  // Get chunk status for a document
  getChunkStatus: (id) => {
    return api.get(`/api/documents/${id}/chunks/status`);
  },

  // Sync documents from SEC
  syncDocuments: (data = {}) => {
    return api.post('/api/documents/sync', data);
  },

  // Get filing types
  getFilingTypes: () => {
    return api.get('/api/filing-types');
  },

  // Health check
  healthCheck: () => {
    return api.get('/api/health');
  },
};

export default api;

