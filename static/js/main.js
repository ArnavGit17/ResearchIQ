/**
 * ResearchIQ – main.js
 * Global UI behaviour: sidebar toggle, theme switcher, auto-dismiss alerts.
 */

/* ── DOM Ready ───────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initSidebar();
  initAlerts();
  initActiveLinks();
});

/* ════════════════════════════════════════════════════════════
   GLOBAL FETCH INTERCEPTOR (CSRF)
   ═══════════════════════════════════════════════════════════ */
const originalFetch = window.fetch;
window.fetch = async function () {
  let [resource, config] = arguments;
  if (!config) config = {};
  
  // Inject CSRF for non-GET/HEAD methods
  if (config.method && !['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(config.method.toUpperCase())) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (csrfToken) {
      if (!config.headers) config.headers = {};
      config.headers['X-CSRFToken'] = csrfToken;
    }
  }
  return originalFetch(resource, config);
};

/* ════════════════════════════════════════════════════════════
   THEME (Dark / Light)
   ═══════════════════════════════════════════════════════════ */
function initTheme() {
  const html      = document.documentElement;
  const btn       = document.getElementById('themeToggle');
  const icon      = document.getElementById('themeIcon');
  const STORAGE_KEY = 'riq-theme';

  // Restore saved preference
  const saved = localStorage.getItem(STORAGE_KEY) || 'dark';
  applyTheme(saved);

  btn?.addEventListener('click', () => {
    const current = html.getAttribute('data-bs-theme') || 'dark';
    const next    = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    localStorage.setItem(STORAGE_KEY, next);
  });

  function applyTheme(theme) {
    html.setAttribute('data-bs-theme', theme);
    if (icon) {
      icon.className = theme === 'dark' ? 'bi bi-moon-fill' : 'bi bi-sun-fill';
    }
  }
}

/* ════════════════════════════════════════════════════════════
   SIDEBAR (mobile toggle + overlay)
   ═══════════════════════════════════════════════════════════ */
function initSidebar() {
  const sidebar  = document.getElementById('sidebar');
  const toggle   = document.getElementById('sidebarToggle');
  const wrapper  = document.getElementById('mainWrapper');

  if (!sidebar || !toggle) return;

  // Create overlay element
  const overlay = document.createElement('div');
  overlay.className = 'sidebar-overlay';
  overlay.id = 'sidebarOverlay';
  document.body.appendChild(overlay);

  toggle.addEventListener('click', openSidebar);
  overlay.addEventListener('click', closeSidebar);

  // Close sidebar on nav link click (mobile)
  sidebar.querySelectorAll('.sidebar-link').forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth < 768) closeSidebar();
    });
  });

  function openSidebar() {
    sidebar.classList.add('sidebar--open');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('sidebar--open');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }
}

/* ════════════════════════════════════════════════════════════
   AUTO-DISMISS FLASH ALERTS
   ═══════════════════════════════════════════════════════════ */
function initAlerts() {
  const alerts = document.querySelectorAll('.riq-alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert?.close();
    }, 5000);
  });
}

/* ════════════════════════════════════════════════════════════
   ACTIVE NAV LINKS (re-checks on navigation)
   ═══════════════════════════════════════════════════════════ */
function initActiveLinks() {
  const path = window.location.pathname;
  document.querySelectorAll('.sidebar-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '#' && path.startsWith(href) && href.length > 1) {
      link.classList.add('active');
    }
  });
}

/* ════════════════════════════════════════════════════════════
   UTILITY – Animated counter
   Used by dashboard and analytics pages.
   ═══════════════════════════════════════════════════════════ */
function animateCounter(el, target, duration = 800) {
  let start = null;
  const step = (timestamp) => {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    el.textContent = Math.floor(progress * target);
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = target;
  };
  requestAnimationFrame(step);
}

// Run animated counters if present
document.querySelectorAll('.stat-value[data-target]').forEach(el => {
  const target = parseInt(el.dataset.target, 10);
  animateCounter(el, target);
});
