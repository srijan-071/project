import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

// ─── Analyze ─────────────────────────────────────────────
export const analyzeText = (text) =>
  api.post('/analyze', { text }).then(r => r.data);

export const whatIfAnalysis = (original_text, modified_text) =>
  api.post('/analyze/what-if', { original_text, modified_text }).then(r => r.data);

export const playgroundAnalysis = (text) =>
  api.post('/analyze/playground', { text }).then(r => r.data);

// ─── Batch ───────────────────────────────────────────────
export const batchAnalyze = (texts) =>
  api.post('/batch-analyze', { texts }).then(r => r.data);

// ─── Compare ─────────────────────────────────────────────
export const compareArticles = (text_a, text_b) =>
  api.post('/compare', { text_a, text_b }).then(r => r.data);

// ─── History ─────────────────────────────────────────────
export const getHistory = (params = {}) =>
  api.get('/history', { params }).then(r => r.data);

export const deleteHistoryItem = (id) =>
  api.delete(`/history/${id}`).then(r => r.data);

// ─── Model ───────────────────────────────────────────────
export const getModelInfo = () =>
  api.get('/model/info').then(r => r.data);

export const getModelMetrics = () =>
  api.get('/model/metrics').then(r => r.data);

export const getModelArchitecture = () =>
  api.get('/model/architecture').then(r => r.data);

export const getModelComparison = () =>
  api.get('/model/comparison').then(r => r.data);

// ─── Analytics ───────────────────────────────────────────
export const getAnalyticsSummary = () =>
  api.get('/analytics/summary').then(r => r.data);

export const getSectorAnalytics = () =>
  api.get('/analytics/sectors').then(r => r.data);

// ─── Health ──────────────────────────────────────────────
export const checkHealth = () =>
  axios.get('http://localhost:8000/health').then(r => r.data);

export default api;
