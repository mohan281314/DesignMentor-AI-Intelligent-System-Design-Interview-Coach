/**
 * auth.js — handles auth state, token storage, and header UI
 * Loaded after app.js on every page.
 */

const Auth = (() => {

  // ── Storage helpers ────────────────────────────────────
  const getToken  = () => localStorage.getItem('access_token');
  const getUser   = () => { try { return JSON.parse(localStorage.getItem('user') || 'null'); } catch { return null; } };
  const isLoggedIn = () => !!getToken();

  function logout() {
    // Call server logout (fire-and-forget)
    const token = getToken();
    if (token) {
      fetch('/api/v1/auth/logout', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      }).catch(() => {});
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/static/login.html';
  }

  // ── Header auth widget ─────────────────────────────────
  function renderHeader() {
    const container = document.getElementById('auth-header');
    if (!container) return;

    const user = getUser();

    if (isLoggedIn() && user) {
      const name  = user.full_name ? user.full_name.split(' ')[0] : user.email.split('@')[0];
      const level = user.profile?.experience_level || 'beginner';
      const levelColors = { beginner:'#6c63ff', intermediate:'#f59e0b', advanced:'#f97316', expert:'#22c55e' };
      const color = levelColors[level] || '#6c63ff';

      container.innerHTML = `
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="font-size:12px;padding:3px 10px;border-radius:20px;background:${color}20;color:${color};border:1px solid ${color}40;text-transform:capitalize;">${level}</span>
          <div style="
            width:32px;height:32px;border-radius:50%;
            background:linear-gradient(135deg,#6c63ff,#a855f7);
            display:flex;align-items:center;justify-content:center;
            font-weight:700;font-size:13px;color:#fff;cursor:default;
            " title="${user.email}">${name[0].toUpperCase()}</div>
          <span style="font-size:13px;color:#a0aec0;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${name}</span>
          <button onclick="Auth.logout()" style="
            padding:6px 12px;background:transparent;
            border:1px solid #2d4a6e;border-radius:6px;
            color:#8892a4;font-size:12px;cursor:pointer;
            transition:all .2s;
          " onmouseover="this.style.borderColor='#6c63ff';this.style.color='#6c63ff'"
             onmouseout="this.style.borderColor='#2d4a6e';this.style.color='#8892a4'">
            Sign out
          </button>
        </div>`;
    } else {
      container.innerHTML = `
        <div style="display:flex;align-items:center;gap:8px;">
          <a href="/static/login.html" style="
            padding:7px 14px;background:transparent;
            border:1px solid #2d4a6e;border-radius:6px;
            color:#a0aec0;font-size:13px;text-decoration:none;
            transition:all .2s;
          " onmouseover="this.style.borderColor='#6c63ff';this.style.color='#6c63ff'"
             onmouseout="this.style.borderColor='#2d4a6e';this.style.color='#a0aec0'">
            Log in
          </a>
          <a href="/static/register.html" style="
            padding:7px 14px;
            background:linear-gradient(135deg,#6c63ff,#a855f7);
            border:1px solid transparent;border-radius:6px;
            color:#fff;font-size:13px;text-decoration:none;font-weight:600;
          ">
            Sign up free
          </a>
        </div>`;
    }
  }

  // ── Auto-refresh token ────────────────────────────────
  async function maybeRefreshToken() {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) return;

    // Check if access token will expire within 5 minutes
    const access = getToken();
    if (!access) return;

    try {
      const parts = access.split('.');
      const payload = JSON.parse(atob(parts[1]));
      const expiresIn = payload.exp - Math.floor(Date.now() / 1000);
      if (expiresIn > 300) return; // still valid

      const res = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
      } else {
        // Token invalid — clear and redirect
        logout();
      }
    } catch (e) {
      // Ignore parse errors
    }
  }

  // ── Patch fetch to include Authorization ──────────────
  // All existing app.js calls to /design, /chat, etc. will
  // now automatically include the token if available.
  const _originalFetch = window.fetch;
  window.fetch = function(url, opts = {}) {
    const token = getToken();
    if (token && typeof url === 'string' && !url.includes('cdn.') && !url.includes('groq.')) {
      opts.headers = opts.headers || {};
      if (!opts.headers['Authorization']) {
        opts.headers['Authorization'] = `Bearer ${token}`;
      }
    }
    return _originalFetch(url, opts);
  };

  // ── Init ──────────────────────────────────────────────
  function init() {
    renderHeader();
    maybeRefreshToken();
    // Refresh token check every 4 minutes
    setInterval(maybeRefreshToken, 4 * 60 * 1000);
  }

  document.addEventListener('DOMContentLoaded', init);

  return { logout, isLoggedIn, getToken, getUser };

})();
