const configuredApiUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const API_BASE_URL = (configuredApiUrl || 'http://127.0.0.1:8000/api/v1').replace(/\/+$/, '');
const TOKEN_KEY = 'ai-life-admin-access-token';

export function getApiBaseUrl() {
  return API_BASE_URL;
}

export function getAccessToken() {
  return window.sessionStorage.getItem(TOKEN_KEY);
}

export function setAccessToken(token) {
  window.sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearAccessToken() {
  window.sessionStorage.removeItem(TOKEN_KEY);
  window.dispatchEvent(new Event('ai-life-admin:auth-expired'));
}

export async function apiRequest(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getAccessToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`, {
    ...options,
    headers,
  });
  if (response.status === 204) return null;

  const contentType = response.headers.get('content-type') || '';
  const result = contentType.includes('application/json')
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = result?.detail;
    const error = new Error(typeof detail === 'string' ? detail : detail ? JSON.stringify(detail) : `Request failed (${response.status})`);
    error.status = response.status;
    if (response.status === 401 && !path.startsWith('/auth/login') && !path.startsWith('/auth/register')) {
      clearAccessToken();
    }
    throw error;
  }

  return result;
}