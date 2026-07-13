// uni2-theme.js — Tema inicial, preferencia del sistema y elección persistida.

(function() {
  const STORAGE_KEY = 'uni2-theme';
  const systemPreference = window.matchMedia('(prefers-color-scheme: dark)');

  function readStoredTheme() {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      return stored === 'dark' || stored === 'light' ? stored : null;
    } catch (error) {
      return null;
    }
  }

  function storeTheme(theme) {
    try {
      window.localStorage.setItem(STORAGE_KEY, theme);
    } catch (error) {
      // El tema sigue funcionando durante la sesión aunque el storage esté bloqueado.
    }
  }

  function preferredTheme() {
    return readStoredTheme() || (systemPreference.matches ? 'dark' : 'light');
  }

  function updateToggle(theme) {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;

    const isDark = theme === 'dark';
    themeToggle.setAttribute('aria-pressed', String(isDark));
    themeToggle.setAttribute('title', isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro');
  }

  function applyTheme(theme, persist) {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-bs-theme', theme);
    window.__uni2Theme = theme;
    if (persist) storeTheme(theme);
    updateToggle(theme);
  }

  // Este archivo se carga en <head>: el atributo queda listo antes de pintar la página.
  applyTheme(preferredTheme(), false);

  window.__uni2ToggleTheme = function() {
    const current = window.__uni2Theme || preferredTheme();
    applyTheme(current === 'dark' ? 'light' : 'dark', true);
  };

  function initializeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    updateToggle(window.__uni2Theme || preferredTheme());
    if (themeToggle) themeToggle.addEventListener('click', window.__uni2ToggleTheme);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeToggle, { once: true });
  } else {
    initializeToggle();
  }

  function followSystemPreference(event) {
    if (!readStoredTheme()) applyTheme(event.matches ? 'dark' : 'light', false);
  }

  if (systemPreference.addEventListener) {
    systemPreference.addEventListener('change', followSystemPreference);
  } else {
    systemPreference.addListener(followSystemPreference);
  }
})();
