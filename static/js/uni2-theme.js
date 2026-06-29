// uni2-theme.js — Theme toggle con persistencia

(function() {
  const STORAGE_KEY = 'uni2-theme';
  const themeToggle = document.getElementById('theme-toggle');

  function getPreferredTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    window.__uni2Theme = theme;
    if (themeToggle) {
      const isDark = theme === 'dark';
      const label = isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro';
      themeToggle.setAttribute('aria-label', label);
      themeToggle.setAttribute('title', label);
    }
  }

  // Setear theme antes de render (evita flash)
  setTheme(getPreferredTheme());

  // Exponer toggle global
  window.__uni2ToggleTheme = function() {
    const current = window.__uni2Theme || 'light';
    setTheme(current === 'dark' ? 'light' : 'dark');
  };

  if (themeToggle) {
    themeToggle.addEventListener('click', window.__uni2ToggleTheme);
  }

  // Escuchar cambios en preferencia del sistema
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
    if (!localStorage.getItem(STORAGE_KEY)) {
      setTheme(e.matches ? 'dark' : 'light');
    }
  });
})();
