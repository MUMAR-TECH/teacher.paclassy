/**
 * Paclassy — App.js
 * Core JS utilities: auth, API helpers, toast notifications
 */

const TOKEN_KEY = 'access_token';
const REFRESH_KEY = 'refresh_token';
const USER_KEY = 'user';

/* ─── Security helpers ─────────────────────────────────────── */
/**
 * Escape a string for safe insertion into HTML contexts.
 * Use whenever dynamically constructing innerHTML from untrusted data.
 */
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}


/* ─── Auth ─────────────────────────────────────────────────── */
function getToken() { return localStorage.getItem(TOKEN_KEY); }
function getUser() {
  try { return JSON.parse(localStorage.getItem(USER_KEY) || 'null'); } catch { return null; }
}
function setAuth(access, refresh, user) {
  localStorage.setItem(TOKEN_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
}
function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
}

function requireAuth(redirectUrl = '/login/') {
  if (!getToken()) { window.location.href = redirectUrl; }
}

/**
 * Enforce that the logged-in user has one of the allowed roles.
 * If not authenticated → redirect to login.
 * If authenticated but wrong role → redirect to the user's own dashboard.
 * @param {string|string[]} allowedRoles - e.g. 'teacher' or ['teacher','admin']
 */
function requireRole(allowedRoles) {
  const token = getToken();
  if (!token) { window.location.href = '/login/'; return; }

  const user = getUser();
  if (!user) { window.location.href = '/login/'; return; }

  const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
  if (!roles.includes(user.role)) {
    const dashboardMap = {
      teacher: '/dashboard/teacher/',
      student: '/dashboard/student/',
      admin: '/dashboard/admin/',
    };
    window.location.href = dashboardMap[user.role] || '/login/';
  }
}

async function logout() {
  const refresh = localStorage.getItem(REFRESH_KEY);
  if (refresh) {
    try {
      await fetch('/api/v1/auth/logout/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${getToken()}` },
        body: JSON.stringify({ refresh }),
      });
    } catch {}
  }
  clearAuth();
  window.location.href = '/login/';
}

/* ─── API Helpers ───────────────────────────────────────────── */
async function apiRequest(url, method = 'GET', body = null) {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  let res = await fetch(url, opts);

  // Try token refresh on 401
  if (res.status === 401) {
    const refresh = localStorage.getItem(REFRESH_KEY);
    if (refresh) {
      const refreshRes = await fetch('/api/v1/auth/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      });
      if (refreshRes.ok) {
        const data = await refreshRes.json();
        localStorage.setItem(TOKEN_KEY, data.access);
        headers['Authorization'] = `Bearer ${data.access}`;
        res = await fetch(url, { ...opts, headers });
      } else {
        clearAuth();
        window.location.href = '/login/';
        return null;
      }
    } else {
      clearAuth();
      window.location.href = '/login/';
      return null;
    }
  }

  if (!res.ok) {
    let msg = `Error ${res.status}`;
    try { const err = await res.json(); msg = err.detail || err.error || msg; } catch {}
    showToast(msg, 'error');
    return null;
  }

  if (res.status === 204) return {};
  return res.json().catch(() => ({}));
}

function apiGet(url) { return apiRequest(url, 'GET'); }
function apiPost(url, data) { return apiRequest(url, 'POST', data); }
function apiPut(url, data) { return apiRequest(url, 'PUT', data); }
function apiPatch(url, data) { return apiRequest(url, 'PATCH', data); }
function apiDelete(url) { return apiRequest(url, 'DELETE'); }

/* ─── Toast Notifications ───────────────────────────────────── */
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed bottom-6 right-6 z-50 flex flex-col gap-2';
    document.body.appendChild(container);
  }

  const colors = {
    success: 'bg-emerald-500',
    error: 'bg-red-500',
    warning: 'bg-amber-500',
    info: 'bg-blue-500',
  };
  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };

  const toast = document.createElement('div');
  toast.className = `flex items-center gap-3 px-4 py-3 rounded-xl text-white shadow-lg text-sm font-medium 
    transition-all duration-300 translate-y-2 opacity-0 ${colors[type] || colors.info}`;
  toast.innerHTML = `<span>${icons[type] || icons.info}</span><span>${message}</span>`;
  container.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('translate-y-2', 'opacity-0');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/* ─── Populate Header/Sidebar with User Info ────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const user = getUser();
  if (!user) return;

  const name = user.full_name || user.email || 'User';
  const initial = name.charAt(0).toUpperCase();
  const role = (user.role || 'user').charAt(0).toUpperCase() + (user.role || 'user').slice(1);

  const getById = id => document.getElementById(id);
  if (getById('header-username')) getById('header-username').textContent = name;
  if (getById('header-avatar-initial')) getById('header-avatar-initial').textContent = initial;
  if (getById('sidebar-username')) getById('sidebar-username').textContent = name;
  if (getById('sidebar-role')) getById('sidebar-role').textContent = role;
  if (getById('sidebar-avatar-initial')) getById('sidebar-avatar-initial').textContent = initial;
  if (getById('user-avatar-initial')) getById('user-avatar-initial').textContent = initial;
});
