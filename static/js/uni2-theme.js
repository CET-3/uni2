// uni2-theme.js — Theme toggle con persistencia

(function() {
  const STORAGE_KEY = 'uni2-theme';

  function getPreferredTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    window.__uni2Theme = theme;
  }

  // Setear theme antes de render (evita flash)
  setTheme(getPreferredTheme());

  // Exponer toggle global
  window.__uni2ToggleTheme = function() {
    const current = window.__uni2Theme || 'light';
    setTheme(current === 'dark' ? 'light' : 'dark');
  };

  // Escuchar cambios en preferencia del sistema
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
    if (!localStorage.getItem(STORAGE_KEY)) {
      setTheme(e.matches ? 'dark' : 'light');
    }
  });
})();
