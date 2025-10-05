// API origin
const API_BASE = 'http://0.0.0.0:8000';

// token helpers
function setToken(t){ localStorage.setItem('token', t); }
function getToken(){ return localStorage.getItem('token'); }
function clearToken(){ localStorage.removeItem('token'); }

// fetch helper
async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  let data = null;
  try { data = await res.json(); } catch {}
  if (!res.ok || (data && data.status === false)) {
    const msg = (data && (data.message || data.detail)) || `HTTP ${res.status}`;
    const err = new Error(msg);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data ?? {};
}
