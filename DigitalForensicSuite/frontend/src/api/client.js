/**
 * Axios API client — pre-configured for the Digital Forensic Suite backend.
 * All three engine endpoints (/image, /video, /signature) and the report
 * endpoint (/report, /history) use this single instance.
 *
 * Usage:
 *   import api from './client';
 *   const res = await api.post('/image/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
 */

import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000, // 120 s — large video uploads / long inference can take time
  headers: {
    'Accept': 'application/json',
  },
});

// ── Request interceptor ──────────────────────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    // Add auth token here when auth is implemented (Phase 10)
    // const token = localStorage.getItem('token');
    // if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor ─────────────────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      error?.message ||
      'An unexpected error occurred.';
    // You can show a global toast here once a toast system is added
    return Promise.reject({ ...error, userMessage: message });
  }
);

export default api;

// ── Convenience helpers ───────────────────────────────────────────────────────

/**
 * Upload a single file for image forgery analysis.
 * @param {File} file
 * @returns {Promise<{prediction, confidence, forgery_type, heatmap_url}>}
 */
export async function analyzeImage(file) {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post('/image/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

/**
 * Upload a video file for deepfake analysis.
 * @param {File} file
 * @returns {Promise<{prediction, confidence, suspicious_frames, timeline}>}
 */
export async function analyzeVideo(file) {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post('/video/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

/**
 * Upload two signature images for forgery verification.
 * @param {File} reference  — known authentic signature
 * @param {File} query      — signature to verify
 * @returns {Promise<{verdict, similarity_score, confidence}>}
 */
export async function analyzeSignature(reference, query) {
  const form = new FormData();
  form.append('reference', reference);
  form.append('query', query);
  const { data } = await api.post('/signature/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

/**
 * Fetch all past analysis records for the History page.
 * @returns {Promise<Array>}
 */
export async function fetchHistory() {
  const { data } = await api.get('/history/');
  return data;
}

/**
 * Download a PDF forensic report by case ID.
 * @param {string} caseId
 * @returns {string} Object URL for download
 */
export async function downloadReport(caseId) {
  const { data } = await api.get(`/report/${caseId}`, {
    responseType: 'blob',
  });
  return URL.createObjectURL(data);
}
