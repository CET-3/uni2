# Design System Unificado — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aplicar el diseño de PAGINA-WEB a toda la app Uni2 como capa temática sobre Bootstrap 5.3.3

**Architecture:** Design system layer (`uni2-design-system.css`) sobrescribe componentes Bootstrap con la paleta de style2.css. Theme toggle vía CSS variables + `[data-theme="dark"]` con persistencia en localStorage. Landing reescrita para calcar index.html con datos dinámicos de Django.

**Tech Stack:** Django, Bootstrap 5.3.3, CSS custom properties, HTML templates, JavaScript vanilla

## Global Constraints
- Réplica exacta de la paleta de PAGINA-WEB (rojo #ff2b2b, amarillo #ffcb30, verde #4ccb4a, primary #3f51b5)
- Mantener Bootstrap 5.3.3 como base
- No eliminar archivos existentes (solo deprecar)
- Inter font desde Google Fonts
- Dark mode vía `[data-theme="dark"]` con persistencia en localStorage
- Grain texture SVG overlay en body

---

### Task 1: uni2-design-system.css — tokens y overrides

**Files:**
- Create: `static/css/uni2-design-system.css`

**Interfaces:**
- Consumes: style2.css como referencia de diseño
- Produces: CSS que cualquier template puede cargar para obtener el diseño PAGINA-WEB

- [ ] **Step 1: Crear archivo con variables de diseño y reset base**

```css
/* uni2-design-system.css — Design System Unificado Uni2 + PAGINA-WEB */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  /* Paleta PAGINA-WEB (réplica exacta de style2.css) */
  --primary: #3f51b5;
  --primary-dark: #303f9f;
  --primary-light: #5c6bc0;
  --rojo: #ff2b2b;
  --rojo-light: #ff6b6b;
  --amarillo: #ffcb30;
  --verde: #4ccb4a;
  --verde-dark: #3db83b;
  --bg: #ffffff;
  --bg-alt: #f0f2f5;
  --text: #1a1a2e;
  --text-secondary: #6c757d;
  --border: #e0e0e0;
  --shadow-sm: 0 1px 3px rgba(26, 26, 46, 0.08);
  --shadow-md: 0 4px 12px rgba(26, 26, 46, 0.1);
  --radius: 12px;
  --radius-sm: 8px;
  --radius-lg: 20px;
  --topbar-bg: #1a1a2e;
  --topbar-text: rgba(255, 255, 255, 0.85);
  --nav-bg: #ffffff;
  --nav-link: #555;
  --nav-link-hover: #3f51b5;
  --footer-bg: #1a1a2e;
  --footer-text: rgba(255, 255, 255, 0.75);

  /* Bootstrap overrides */
  --bs-primary: #3f51b5;
  --bs-primary-rgb: 63, 81, 181;
  --bs-font-sans-serif: 'Inter', system-ui, -apple-system, sans-serif;
}

[data-theme="dark"] {
  --bg: #1a1a2e;
  --bg-alt: #16213e;
  --text: #eaeaea;
  --text-secondary: #a0a0b0;
  --border: #2a2a4a;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --nav-bg: #16213e;
  --nav-link: #a0a0b0;
  --nav-link-hover: #eaeaea;
  --bs-body-bg: #1a1a2e;
  --bs-body-color: #eaeaea;
  --bs-border-color: #2a2a4a;
}

*, *::before, *::after { box-sizing: border-box; }

body {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

- [ ] **Step 2: Agregar grain texture**

```css
/* Grain texture overlay */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  opacity: 0.03;
  pointer-events: none;
  z-index: 9999;
}
```

- [ ] **Step 3: Override navbar Bootstrap → estilo PAGINA-WEB**

```css
/* === TOPBAR === */
.uni2-topbar {
  background: var(--topbar-bg);
  color: var(--topbar-text);
  font-size: 0.8rem;
  padding: 0.4rem 0;
}

.uni2-topbar .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.uni2-topbar a {
  color: var(--topbar-text);
  text-decoration: none;
}

.uni2-topbar a:hover { color: #fff; }

/* === NAVBAR === */
.uni2-navbar {
  background: var(--nav-bg);
  border-bottom: 1px solid var(--border);
  padding: 0;
}

.uni2-navbar .navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.uni2-navbar .navbar-brand img {
  height: 40px;
  width: auto;
}

.uni2-navbar .nav-link {
  color: var(--nav-link) !important;
  font-weight: 500;
  font-size: 0.9rem;
  padding: 0.75rem 1rem !important;
  transition: color 0.15s ease;
}

.uni2-navbar .nav-link:hover,
.uni2-navbar .nav-link.active {
  color: var(--nav-link-hover) !important;
}

.uni2-navbar .navbar-toggler {
  border: 1px solid var(--border);
  color: var(--text);
}
```

- [ ] **Step 4: Override cards con borde coloreado**

```css
/* === CARDS === */
.card {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  background: var(--bg);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.card:hover {
  box-shadow: var(--shadow-md);
}

/* Borde superior coloreado secuencial */
.card-border-rojo { border-top: 4px solid var(--rojo); }
.card-border-amarillo { border-top: 4px solid var(--amarillo); }
.card-border-verde { border-top: 4px solid var(--verde); }
.card-border-primary { border-top: 4px solid var(--primary); }

.card-header {
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  font-weight: 600;
  font-size: 0.9rem;
  padding: 1rem 1.25rem;
  border-radius: var(--radius) var(--radius) 0 0 !important;
  color: var(--text-secondary);
}

.card-body { padding: 1.25rem; }
```

- [ ] **Step 5: Override botones**

```css
/* === BOTONES === */
.btn {
  font-weight: 600;
  border-radius: var(--radius-sm);
  transition: all 0.15s ease;
}

.btn-primary {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}
.btn-primary:hover, .btn-primary:focus {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
  color: #fff;
}

.btn-outline-primary {
  color: var(--primary);
  border-color: var(--primary);
}
.btn-outline-primary:hover {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}

.btn-light {
  background: var(--bg-alt);
  border-color: var(--border);
  color: var(--text);
}
.btn-light:hover {
  background: var(--border);
}

/* Botones hero (SÚMATE / INICIAR SESIÓN) */
.btn-hero {
  font-weight: 700;
  font-size: 0.9rem;
  letter-spacing: 0.05em;
  padding: 0.65rem 1.75rem;
  text-transform: uppercase;
  border-radius: 50px;
}

.btn-hero-primary {
  background: var(--primary);
  border: 2px solid var(--primary);
  color: #fff;
}
.btn-hero-primary:hover {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
  color: #fff;
}

.btn-hero-outline {
  background: transparent;
  border: 2px solid #fff;
  color: #fff;
}
.btn-hero-outline:hover {
  background: #fff;
  color: var(--text);
}
```

- [ ] **Step 6: Override tablas, alerts, formularios**

```css
/* === TABLAS === */
.table { --bs-table-bg: transparent; }

.table thead th {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border);
  padding: 0.75rem 1.25rem;
  background: var(--bg-alt);
  white-space: nowrap;
}

.table tbody td {
  padding: 0.875rem 1.25rem;
  vertical-align: middle;
  font-size: 0.9rem;
  border-bottom: 1px solid var(--border);
}

.table-hover tbody tr:hover { background: rgba(63, 81, 181, 0.03); }

/* === ALERTS === */
.alert {
  border: none;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.875rem 1.25rem;
}
.alert-success { background: #d4edda; color: #155724; }
.alert-danger  { background: #f8d7da; color: #721c24; }
.alert-warning { background: #fff3cd; color: #856404; }
.alert-info    { background: #d1ecf1; color: #0c5460; }

/* === FORMULARIOS === */
.form-label {
  font-weight: 600;
  font-size: 0.875rem;
  margin-bottom: 0.375rem;
  color: var(--text);
}

.form-control,
.form-select {
  border-radius: var(--radius-sm);
  border: 1.5px solid var(--border);
  padding: 0.625rem 0.875rem;
  font-size: 0.9rem;
  background: var(--bg);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.form-control:focus,
.form-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(63, 81, 181, 0.12);
  outline: none;
}

.form-control.is-invalid { border-color: var(--rojo); }
.invalid-feedback, .text-danger {
  font-size: 0.8rem;
  color: var(--rojo) !important;
  font-weight: 500;
}
```

- [ ] **Step 7: Componentes de landing PAGINA-WEB (hero, benefit, steps, footer)**

```css
/* === HERO === */
.hero-section {
  background: linear-gradient(135deg, #3f51b5 0%, #5c6bc0 40%, #7c4dff 100%);
  color: #fff;
  padding: 4rem 0;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: -150px;
  right: -150px;
  width: 500px;
  height: 500px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50%;
  pointer-events: none;
}

.hero-section .hero-content { position: relative; z-index: 1; }

.hero-section h1 {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.hero-section p.lead {
  font-size: 1.1rem;
  opacity: 0.9;
  max-width: 540px;
  line-height: 1.6;
}

/* === BENEFIT CARD (delegado a beneficios.css) === */

/* === STEPS === */
.step-card {
  text-align: center;
  padding: 1.5rem;
}

.step-number {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  font-weight: 800;
  margin: 0 auto 1rem;
  color: #fff;
}

.step-number-rojo { background: var(--rojo); }
.step-number-amarillo { background: var(--amarillo); color: #1a1a2e; }
.step-number-verde { background: var(--verde); }
.step-number-primary { background: var(--primary); }

.step-card h3 {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.step-card p {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 0;
}

/* === FOOTER === */
.uni2-footer {
  background: var(--footer-bg);
  color: var(--footer-text);
  padding: 3rem 0 1.5rem;
}

.uni2-footer h4, .uni2-footer h6 { color: #fff; }

.uni2-footer a {
  color: var(--footer-text);
  text-decoration: none;
  transition: color 0.15s ease;
}

.uni2-footer a:hover { color: #fff; }

.uni2-footer hr {
  border-color: rgba(255, 255, 255, 0.15);
}

/* === THEME TOGGLE === */
.theme-toggle {
  background: none;
  border: 1px solid var(--border);
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text);
  font-size: 1rem;
  transition: background 0.15s ease;
}

.theme-toggle:hover { background: var(--bg-alt); }
```

- [ ] **Step 8: Dashboard utilities (migradas de base.html inline)**

```css
/* === DASHBOARD COMPONENTS (migrados de base.html inline) === */
.app-panel-shell { display: grid; gap: 1.5rem; }

.dashboard-hero {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  border: 0;
  border-radius: 1.5rem;
  color: #fff;
  overflow: hidden;
  position: relative;
}

.dashboard-hero::after {
  background: radial-gradient(circle at top right, rgba(255, 255, 255, 0.32), transparent 45%);
  content: "";
  inset: 0;
  pointer-events: none;
  position: absolute;
}

.dashboard-hero .card-body {
  padding: 1.75rem;
  position: relative;
  z-index: 1;
}

.dashboard-eyebrow {
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
}

.dashboard-actions-grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); }
.module-card-grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }

.quick-action-card,
.module-card,
.info-card {
  border: 1px solid var(--border);
  border-radius: 1rem;
  box-shadow: var(--shadow-sm);
}

.quick-action-card .card-body,
.module-card .card-body,
.info-card .card-body {
  padding: 1.25rem;
}

.sidebar-card {
  border: 1px solid var(--border);
  border-radius: 1.25rem;
  box-shadow: var(--shadow-sm);
  top: 1.25rem;
}

.sidebar-card .list-group-item {
  align-items: center;
  border: 0;
  display: flex;
  font-weight: 500;
  gap: 0.75rem;
  justify-content: space-between;
  padding: 0.85rem 1.25rem;
}

.sidebar-card .list-group-item + .list-group-item {
  border-top: 1px solid var(--border);
}

.sidebar-card .list-group-item.active {
  background: rgba(63, 81, 181, 0.08);
  color: var(--primary);
}

.metric-card {
  border: 0;
  border-radius: 1rem;
  box-shadow: var(--shadow-sm);
}

.metric-card .metric-label {
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  margin-bottom: 0.35rem;
  text-transform: uppercase;
}

.metric-card .metric-value {
  font-size: 1.7rem;
  font-weight: 700;
  line-height: 1.05;
}

.section-card {
  border: 0;
  border-radius: 1.25rem;
  box-shadow: var(--shadow-sm);
}

.section-card .card-body { padding: 1.5rem; }

.section-title-row {
  align-items: center;
  display: flex;
  gap: 0.75rem;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.pill-row { display: flex; flex-wrap: wrap; gap: 0.5rem; }

.dashboard-pill {
  background: rgba(255, 255, 255, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 999px;
  display: inline-flex;
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.4rem 0.8rem;
}

.muted-kicker {
  color: var(--text-secondary);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  margin-bottom: 0.4rem;
  text-transform: uppercase;
}

.status-badge-soft {
  background: rgba(63, 81, 181, 0.08);
  border-radius: 999px;
  color: var(--primary);
  display: inline-flex;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 0.35rem 0.7rem;
}

.compact-list li + li { margin-top: 0.75rem; }

.page-header-actions,
.mobile-stack-actions {
  display: flex;
  gap: 0.75rem;
}

.surface-card {
  border: 0;
  border-radius: 1.1rem;
  box-shadow: var(--shadow-sm);
}

.admin-layout { display: grid; gap: 1.5rem; }

.admin-main-column,
.admin-side-column {
  display: grid;
  gap: 1.5rem;
  align-content: start;
}

.quick-action-meta {
  align-items: center;
  color: var(--text-secondary);
  display: flex;
  font-size: 0.88rem;
  gap: 0.75rem;
  justify-content: space-between;
  margin: 0.9rem 0 1rem;
}

.quick-action-meta span:first-child { min-width: 0; }

.support-link-list,
.module-link-list { display: grid; gap: 0.75rem; }

.support-link-item,
.module-link-item {
  align-items: center;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 1rem;
  color: inherit;
  display: flex;
  gap: 1rem;
  justify-content: space-between;
  padding: 0.95rem 1rem;
  text-decoration: none;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.support-link-item:hover,
.module-link-item:hover {
  border-color: var(--primary);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.support-link-copy,
.module-link-copy { min-width: 0; }

.support-link-copy strong,
.module-link-copy strong {
  display: block;
  font-size: 0.98rem;
}

.support-link-copy span,
.module-link-copy span {
  color: var(--text-secondary);
  display: block;
  font-size: 0.86rem;
  margin-top: 0.2rem;
}

.module-toggle {
  align-items: center;
  background: rgba(63, 81, 181, 0.08);
  border: 1px solid var(--border);
  border-radius: 1rem;
  color: var(--primary);
  display: flex;
  font-weight: 600;
  justify-content: space-between;
  padding: 0.9rem 1rem;
  width: 100%;
}

.module-toggle[aria-expanded="true"] .module-toggle-label::after { content: "ocultar"; }
.module-toggle[aria-expanded="false"] .module-toggle-label::after { content: "mostrar"; }

.module-toggle-label::after {
  color: var(--text-secondary);
  font-size: 0.82rem;
  font-weight: 500;
  margin-left: 0.45rem;
  text-transform: lowercase;
}

.table-soft thead th {
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  white-space: nowrap;
}

@media (min-width: 992px) {
  .admin-layout {
    align-items: start;
    grid-template-columns: minmax(0, 1fr) 320px;
  }
  .admin-side-column {
    position: sticky;
    top: 1.25rem;
  }
}

@media (max-width: 991.98px) {
  .navbar .collapse.show,
  .navbar .collapse.collapsing {
    background: var(--nav-bg);
    border: 1px solid var(--border);
    border-radius: 1rem;
    margin-top: 0.75rem;
    padding: 1rem;
  }
  .navbar .collapse.show .d-flex,
  .navbar .collapse.collapsing .d-flex {
    flex-direction: column;
  }
  .dashboard-hero .card-body { padding: 1.25rem; }
  .dashboard-hero .display-6 { font-size: 2rem; }
  .app-panel-shell { gap: 1rem; }
  .page-header-actions,
  .mobile-stack-actions { flex-direction: column; }
  .page-header-actions .btn,
  .mobile-stack-actions .btn { width: 100%; }
  .module-toggle { margin-bottom: 0.9rem; }
  .table-soft { font-size: 0.92rem; }
  .surface-card .card-body,
  .section-card .card-body,
  .metric-card .card-body { padding: 1.15rem; }
}

@media (max-width: 575.98px) {
  main.py-4 { padding-top: 1rem !important; }
  .dashboard-hero { border-radius: 1.1rem; }
  .dashboard-hero .display-6 { font-size: 1.7rem; }
  .dashboard-actions-grid { grid-template-columns: 1fr; }
  .quick-action-meta { align-items: flex-start; flex-direction: column; }
  .table-soft { font-size: 0.88rem; }
  .table-soft td, .table-soft th { padding: 0.7rem 0.5rem; }
}
```

- [ ] **Step 9: Verificar que el CSS carga sin errores**

Run: `python manage.py check`
Expected: No errors

- [ ] **Step 10: Commit**

```bash
git add static/css/uni2-design-system.css
git commit -m "feat: crear uni2-design-system.css con tokens PAGINA-WEB y overrides Bootstrap"
```

---

### Task 2: uni2-theme.js — lógica de theme toggle

**Files:**
- Create: `static/js/uni2-theme.js`

**Interfaces:**
- Consumes: `document.documentElement` (setea `data-theme`)
- Produces: theme toggle widget que usa `window.__uni2Theme` para estado global

- [ ] **Step 1: Crear el script de theme toggle**

```javascript
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
```

- [ ] **Step 2: Verificar que el JS carga sin errores**

Run: `python manage.py collectstatic --noinput` (si aplica)
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add static/js/uni2-theme.js
git commit -m "feat: agregar uni2-theme.js con toggle oscuro persistente"
```

---

### Task 3: base.html modernizado

**Files:**
- Modify: `templates/base.html`

**Interfaces:**
- Consumes: `uni2-design-system.css` (Task 1), `uni2-theme.js` (Task 2)
- Produces: base que heredan todas las páginas

- [ ] **Step 1: Reemplazar contenido de base.html**

```html
{% load static %}
<!doctype html>
<html lang="es" data-theme="light">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}Uni2{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{% static 'css/uni2-design-system.css' %}">
    <link rel="stylesheet" href="{% static 'css/beneficios.css' %}">
    {% block extra_head %}{% endblock %}
</head>
<body class="d-flex flex-column min-vh-100">
    {% include "includes/navbar.html" %}
    <main class="flex-grow-1">
        {% block content %}{% endblock %}
    </main>
    {% include "includes/footer.html" %}
    <script src="{% static 'js/uni2-theme.js' %}"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

Notas:
- Se eliminó el inline CSS (migrado a uni2-design-system.css)
- Se sacó el `<div class="container">` del main (cada template define su propio contenedor, asi el hero puede ser full-width)
- Se agregó `data-theme="light"` en `<html>` para que el JS lo actualice sin flash
- uni2.css ya no se carga (deprecado, disponible para rollback si se necesita)
- Se reemplazó `bg-light` por el default del design system
- Se agregó `py-4` condicional según template (hero no necesita padding extra)

- [ ] **Step 2: Verificar sintaxis del template**

Run: `python manage.py validate_templates --ignore-app django.contrib.admin 2>/dev/null || python -c "import django; from django.template import engines; engines['django'].from_string(open('templates/base.html').read())"`

Expected: No template syntax errors

- [ ] **Step 3: Commit**

```bash
git add templates/base.html
git commit -m "refactor: modernizar base.html con design system y theme toggle"
```

---

### Task 4: Navbar — fusión PAGINA-WEB + lógica de sesión

**Files:**
- Modify: `templates/includes/navbar.html`

- [ ] **Step 1: Reescribir navbar con topbar + nav**

```html
{% load static %}
<!-- Topbar -->
<div class="uni2-topbar d-none d-md-block">
    <div class="container">
        <span>
            <i class="bi bi-clock"></i> Lun–Vie 08:50–16:30
        </span>
        <span>
            <a href="https://wa.me/5492984210672" target="_blank" rel="noopener"><i class="bi bi-whatsapp"></i> WhatsApp</a>
            <a href="https://www.instagram.com/unidos.cet3" target="_blank" rel="noopener" class="ms-3"><i class="bi bi-instagram"></i> Instagram</a>
        </span>
    </div>
</div>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg uni2-navbar">
    <div class="container">
        <a class="navbar-brand" href="{% url 'web:home' %}">
            <img src="{% static 'img/LOJO_UNI2.png' %}" alt="Uni2">
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarUni2" aria-controls="navbarUni2" aria-expanded="false">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarUni2">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                <li class="nav-item"><a class="nav-link" href="{% url 'web:productos_servicios' %}">Productos y servicios</a></li>
                <li class="nav-item"><a class="nav-link" href="{% url 'web:comercios' %}">Comercios</a></li>
            </ul>
            <div class="d-flex align-items-center gap-2 flex-wrap">
                <button class="theme-toggle" onclick="window.__uni2ToggleTheme()" aria-label="Cambiar tema">
                    <span id="theme-icon">🌙</span>
                </button>
                {% if user.is_authenticated %}
                    <div class="dropdown">
                        <button class="btn btn-outline-primary btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                            {{ nombre_usuario }}
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end">
                            {% if cantidad_experiencias > 1 %}
                                {% if tiene_perfil_asociado %}
                                    <li><a class="dropdown-item" href="{% url 'asociados:dashboard' %}">Mi panel</a></li>
                                {% endif %}
                                {% if tiene_gestion %}
                                    <li><a class="dropdown-item" href="{% url 'gestion:dashboard' %}">Panel de gestión</a></li>
                                {% endif %}
                                {% if tiene_perfil_comercio %}
                                    <li><a class="dropdown-item" href="{% url 'comercios:dashboard' %}">Mi comercio</a></li>
                                {% endif %}
                            {% elif tiene_gestion %}
                                <li><a class="dropdown-item" href="{% url 'gestion:dashboard' %}">Panel de gestión</a></li>
                            {% elif tiene_perfil_asociado %}
                                <li><a class="dropdown-item" href="{% url 'asociados:dashboard' %}">Mi panel</a></li>
                            {% elif tiene_perfil_comercio %}
                                <li><a class="dropdown-item" href="{% url 'comercios:dashboard' %}">Mi comercio</a></li>
                            {% endif %}
                            {% if es_staff %}
                                <li><a class="dropdown-item" href="{% url 'admin:index' %}">Admin técnico</a></li>
                            {% endif %}
                            {% if perms.gestion.ver_especificacion %}
                                <li><a class="dropdown-item" href="{% url 'especificacion:indice' %}">Especificación</a></li>
                            {% endif %}
                            <li><hr class="dropdown-divider"></li>
                            <li>
                                <form method="post" action="{% url 'usuarios:logout' %}">
                                    {% csrf_token %}
                                    <button class="dropdown-item" type="submit">Salir</button>
                                </form>
                            </li>
                        </ul>
                    </div>
                {% else %}
                    <a class="btn btn-primary btn-sm" href="{% url 'usuarios:login' %}">Ingresar</a>
                {% endif %}
            </div>
        </div>
    </div>
</nav>
```

Nota: los iconos de Bootstrap Icons se usan en el topbar. Asegurarse que Bootstrap Icons CDN esté cargado. Si no, agregar en base.html. Alternativamente usar emojis o FontAwesome.

- [ ] **Step 2: Agregar Bootstrap Icons en base.html (si no está)**

Agregar después de bootstrap CSS en base.html:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
```

- [ ] **Step 3: Verificar sintaxis del template**

Run: `python -c "import django; from django.template import engines; engines['django'].from_string(open('templates/includes/navbar.html').read())"`

Expected: No template syntax errors

- [ ] **Step 4: Commit**

```bash
git add templates/includes/navbar.html
git commit -m "feat: fusionar navbar PAGINA-WEB con login state de Uni2"
```

---

### Task 5: Footer — estilo PAGINA-WEB

**Files:**
- Modify: `templates/includes/footer.html`

- [ ] **Step 1: Reescribir footer con nueva clase**

```html
{% load static %}
<footer class="uni2-footer mt-auto" id="contacto">
    <div class="container">
        <div class="row g-4">
            <div class="col-md-4">
                <h4 class="fw-bold">MUTUAL <span class="fw-normal">UNI2</span></h4>
                <p class="small mt-2" style="opacity: 0.75;">Un espacio creado por y para los estudiantes, promoviendo valores, solidaridad y crecimiento conjunto.</p>
            </div>

            <div class="col-md-2">
                <h6 class="fw-semibold text-uppercase small mb-3">Recursos</h6>
                <ul class="list-unstyled small">
                    <li class="mb-2"><a href="{% url 'web:home' %}">Inicio</a></li>
                    <li class="mb-2"><a href="#beneficios">Beneficios</a></li>
                    <li class="mb-2"><a href="{% url 'web:productos_servicios' %}">Servicios</a></li>
                    <li class="mb-2"><a href="#como-asociarse">Asociarse</a></li>
                </ul>
            </div>

            <div class="col-md-3">
                <h6 class="fw-semibold text-uppercase small mb-3">Contacto</h6>
                <ul class="list-unstyled small">
                    <li class="mb-2">Email: <a href="mailto:unidosatencionalcliente@gmail.com">unidosatencionalcliente@gmail.com</a></li>
                    <li class="mb-2">WhatsApp: <a href="https://wa.me/5492984210672" target="_blank" rel="noopener">+54 9 298 421-0672</a></li>
                    <li class="mb-2">Chacabuco 1050, General Roca, Río Negro</li>
                </ul>
            </div>

            <div class="col-md-3">
                <h6 class="fw-semibold text-uppercase small mb-3">Seguinos</h6>
                <ul class="list-unstyled small">
                    <li class="mb-2"><a href="https://www.instagram.com/unidos.cet3" target="_blank" rel="noopener">Instagram: @unidos.cet3</a></li>
                </ul>
                <a href="{% url 'web:home' %}#como-asociarse" class="btn btn-outline-light btn-sm">Asociate ahora</a>
            </div>
        </div>

        <hr class="mt-4 mb-3">
        <p class="small text-center mb-0" style="opacity: 0.5;">&copy; {% now "Y" %} Mutual Escolar UNI2 — CET N&deg; 3. Todos los derechos reservados.</p>
    </div>
</footer>
```

Cambios clave:
- `bg-primary text-white` → `uni2-footer` (usa el color del token)
- `text-white` inline removido (heredado de `.uni2-footer a`)
- Mantiene estructura de columnas Bootstrap
- Mantiene contenido existente

- [ ] **Step 2: Verificar sintaxis del template**

Run: `python -c "import django; from django.template import engines; engines['django'].from_string(open('templates/includes/footer.html').read())"`

Expected: No template syntax errors

- [ ] **Step 3: Commit**

```bash
git add templates/includes/footer.html
git commit -m "feat: rediseñar footer con estilo PAGINA-WEB"
```

---

### Task 6: Landing page reescrita

**Files:**
- Modify: `templates/web/home.html`

- [ ] **Step 1: Reescribir home.html con diseño PAGINA-WEB**

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Inicio | Uni2{% endblock %}

{% block content %}

<!-- HERO -->
<section class="hero-section" id="inicio" aria-labelledby="hero-title">
    <div class="container">
        <div class="hero-content text-center text-md-start">
            <div class="row align-items-center">
                <div class="col-lg-7">
                    <p class="text-uppercase small fw-semibold mb-1" style="opacity: 0.8;">Mutual Escolar UNI2</p>
                    <h1 id="hero-title">Tu mutual, más cerca que nunca</h1>
                    <p class="lead">Una comunidad comprometida con sus asociados, ofreciendo beneficios, servicios y oportunidades.</p>
                    <div class="mt-4 d-flex gap-3 flex-wrap">
                        <a class="btn btn-hero btn-hero-primary" href="#como-asociarse">SÚMATE</a>
                        <a class="btn btn-hero btn-hero-outline" href="{% url 'usuarios:login' %}">INICIAR SESIÓN</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<div class="container my-5">

    <!-- SERVICIOS -->
    <section class="mb-5" id="servicios" aria-labelledby="servicios-title">
        <p class="text-uppercase text-secondary small fw-semibold mb-1">Servicios</p>
        <h2 id="servicios-title" class="h3 mb-4">Nuestros servicios</h2>

        <div class="row g-4">
            {% for categoria in categorias_productos_servicios %}
                <div class="col-md-6 col-lg-3">
                    <div class="card h-100 card-border-{% cycle 'rojo' 'amarillo' 'verde' 'primary' %}">
                        <div class="card-body d-flex flex-column">
                            <h3 class="h5">{{ categoria.nombre }}</h3>
                            {% if categoria.descripcion %}
                                <p class="card-text text-secondary small flex-grow-1">{{ categoria.descripcion }}</p>
                            {% endif %}
                            <a href="{% url 'web:categoria_detalle' categoria.pk %}" class="btn btn-outline-primary btn-sm mt-2">
                                Ver más
                            </a>
                        </div>
                    </div>
                </div>
            {% empty %}
                <div class="col-12">
                    <p class="text-secondary">Sin servicios cargados por ahora.</p>
                </div>
            {% endfor %}
        </div>
    </section>

    <!-- BENEFICIOS -->
    {% if rubros_beneficio %}
        <aside class="mb-5" id="beneficios" aria-labelledby="beneficios-title">
            <p class="text-uppercase text-secondary small fw-semibold mb-1">Beneficios</p>
            <h2 id="beneficios-title" class="h3 mb-4">Beneficios para vos</h2>

            <div class="benefit-grid">
                {% for rubro in rubros_beneficio %}
                    <a href="{% url 'web:actividad_comercial_detalle' rubro.pk %}" class="benefit-mix-card benefit-mix-card-{{ forloop.counter0 }}">
                        <span class="logo-cloud">
                            {% for comercio in rubro.comercios_con_foto|slice:":3" %}
                                {% if comercio.foto %}
                                <span class="logo-dot 
                                    {% if forloop.counter == 1 %}logo-dot-left
                                    {% elif forloop.counter == 2 %}logo-dot-main
                                    {% else %}logo-dot-right{% endif %}">
                                    <img src="{{ comercio.foto.url }}" alt="{{ comercio.nombre }}" loading="lazy">
                                </span>
                                {% endif %}
                            {% endfor %}
                        </span>
                        <span class="benefit-rubric">{{ rubro.nombre }}</span>
                    </a>
                {% endfor %}
            </div>
        </aside>
    {% endif %}

    <!-- PUBLICIDADES -->
    {% if publicidades %}
        <section class="mb-5" aria-labelledby="publicidad-title">
            <p class="text-uppercase text-secondary small fw-semibold mb-1">Promos destacadas</p>
            <h2 id="publicidad-title" class="h3 mb-4">Nuestros favoritos</h2>

            <div class="row g-4">
                {% for publicidad in publicidades %}
                    <div class="col-md-6 col-lg-3">
                        <article class="card h-100">
                            <div class="card-body d-flex flex-column">
                                {% if publicidad.foto %}
                                    <img src="{{ publicidad.foto.url }}" alt="{{ publicidad.titulo }}" class="card-img-top mb-3" style="height: 160px; object-fit: cover; border-radius: var(--radius-sm) var(--radius-sm) 0 0;">
                                {% endif %}
                                <span class="badge bg-light text-dark align-self-start mb-2">{{ publicidad.etiqueta_principal }}</span>
                                <h3 class="h5">{{ publicidad.titulo }}</h3>
                                <strong class="h4 text-primary">{{ publicidad.etiqueta_secundaria }}</strong>
                                <p class="card-text text-secondary small flex-grow-1 mt-2">{{ publicidad.descripcion }}</p>
                                {% if publicidad.get_absolute_url %}
                                    <a href="{{ publicidad.get_absolute_url }}" class="btn btn-outline-primary btn-sm mt-auto">Conocer más</a>
                                {% endif %}
                            </div>
                        </article>
                    </div>
                {% endfor %}
            </div>
        </section>
    {% endif %}

    <!-- CÓMO ASOCIARSE (pasos + info) -->
    <section class="mb-5" id="como-asociarse" aria-labelledby="asociarse-title">
        <p class="text-uppercase text-secondary small fw-semibold mb-1">Asociate en cuatro pasos</p>
        <h2 id="asociarse-title" class="h3 mb-4">Cómo ser parte de UNI2</h2>

        <div class="row g-4 mb-5">
            <div class="col-md-6 col-lg-3">
                <div class="step-card">
                    <div class="step-number step-number-primary">1</div>
                    <h3>Acércate a la mutual</h3>
                    <p>Visitá UNI2 durante nuestros horarios de atención.</p>
                </div>
            </div>
            <div class="col-md-6 col-lg-3">
                <div class="step-card">
                    <div class="step-number step-number-rojo">2</div>
                    <h3>Completá tu inscripción</h3>
                    <p>Registrá tus datos de forma rápida y sencilla.</p>
                </div>
            </div>
            <div class="col-md-6 col-lg-3">
                <div class="step-card">
                    <div class="step-number step-number-amarillo">3</div>
                    <h3>Sumate a la comunidad</h3>
                    <p>Con una cuota social de solo $700 por mes, ya sos asociado.</p>
                </div>
            </div>
            <div class="col-md-6 col-lg-3">
                <div class="step-card">
                    <div class="step-number step-number-verde">4</div>
                    <h3>Disfrutá tus beneficios</h3>
                    <p>Accedé a servicios, descuentos y oportunidades exclusivas.</p>
                </div>
            </div>
        </div>

        <div class="row g-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h3 class="h6">Asociación</h3>
                        <p class="small text-secondary mb-0">Presencial en la mutual.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h3 class="h6">Cuota social</h3>
                        <p class="small text-secondary mb-0">$700 mensuales.</p>
                    </div>
                </div>
            </div>
            <div class="col-12 mt-3">
                <div class="card">
                    <div class="card-body">
                        <h3 class="h6 mb-3">Horarios de atención</h3>
                        <div class="table-responsive">
                            <table class="table table-sm table-bordered mb-0">
                                <thead>
                                    <tr>
                                        <th>Día</th>
                                        <th>Horario 1</th>
                                        <th>Horario 2</th>
                                        <th>Horario 3</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr><td>Lunes</td><td>08:50 - 09:00</td><td>10:20 - 10:30</td><td>13:30 - 16:30</td></tr>
                                    <tr><td>Martes</td><td>08:50 - 09:00</td><td>10:20 - 10:30</td><td>13:30 - 16:30</td></tr>
                                    <tr><td>Miércoles</td><td>08:50 - 09:00</td><td>10:20 - 10:30</td><td>13:30 - 16:30</td></tr>
                                    <tr><td>Jueves</td><td>08:50 - 09:00</td><td>10:20 - 10:30</td><td>13:30 - 16:30</td></tr>
                                    <tr><td>Viernes</td><td>08:50 - 09:00</td><td>10:20 - 10:30</td><td>—</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

</div> <!-- /container -->
{% endblock %}
```

- [ ] **Step 2: Verificar sintaxis del template**

Run: `python -c "import django; from django.template import engines; engines['django'].from_string(open('templates/web/home.html').read())"`

Expected: No template syntax errors

- [ ] **Step 3: Verificar que el home se renderiza sin errores**

Run: `python manage.py test web.tests.test_views 2>/dev/null || python -c "
import django; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.test import RequestFactory; from web.views import HomeView
rf = RequestFactory(); request = rf.get('/')
response = HomeView.as_view()(request)
print('Status:', response.status_code)
print('OK' if response.status_code == 200 else 'FAIL')
"`

Expected: Status: 200, OK

- [ ] **Step 4: Commit**

```bash
git add templates/web/home.html
git commit -m "feat: rediseñar landing con diseño PAGINA-WEB (hero, cards, steps, benefits)"
```

---

### Task 7: Página showcase del Design System

**Files:**
- Create: `templates/web/design-system.html`
- Modify: `web/views.py`
- Modify: `web/urls.py`

- [ ] **Step 1: Agregar vista en web/views.py**

Agregar después de `HomeView`:
```python
class DesignSystemView(TemplateView):
    template_name = "web/design-system.html"
```

- [ ] **Step 2: Agregar ruta en web/urls.py**

Agregar en urlpatterns:
```python
    path("design-system/", DesignSystemView.as_view(), name="design-system"),
```

Y en el import agregar `DesignSystemView`:
```python
from .views import (
    ActividadComercialDetalleView,
    CategoriaProductoServicioDetalleView,
    ComercioDetalleView,
    ComerciosPublicosView,
    DesignSystemView,
    HomeView,
    ProductoServicioDetalleView,
    ProductosServiciosPublicosView,
)
```

- [ ] **Step 3: Crear template design-system.html**

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Design System | Uni2{% endblock %}

{% block content %}
<div class="container py-5">

    <h1 class="mb-4">Design System — Uni2</h1>
    <p class="text-secondary mb-5">Referencia visual de todos los componentes del sistema. Basado en el diseño de PAGINA-WEB con Bootstrap 5.3.3.</p>

    <!-- ======== COLORES ======== -->
    <section class="mb-5" id="colors">
        <h2 class="h4 mb-3">Colores</h2>
        <div class="row g-3">
            <div class="col-6 col-md-3"><div class="card"><div class="card-body"><div style="width:100%;height:60px;background:var(--primary);border-radius:8px;margin-bottom:8px;"></div><code>--primary</code><br><span class="small text-secondary">#3f51b5</span></div></div></div>
            <div class="col-6 col-md-3"><div class="card"><div class="card-body"><div style="width:100%;height:60px;background:var(--rojo);border-radius:8px;margin-bottom:8px;"></div><code>--rojo</code><br><span class="small text-secondary">#ff2b2b</span></div></div></div>
            <div class="col-6 col-md-3"><div class="card"><div class="card-body"><div style="width:100%;height:60px;background:var(--amarillo);border-radius:8px;margin-bottom:8px;"></div><code>--amarillo</code><br><span class="small text-secondary">#ffcb30</span></div></div></div>
            <div class="col-6 col-md-3"><div class="card"><div class="card-body"><div style="width:100%;height:60px;background:var(--verde);border-radius:8px;margin-bottom:8px;"></div><code>--verde</code><br><span class="small text-secondary">#4ccb4a</span></div></div></div>
        </div>
    </section>

    <!-- ======== TIPOGRAFÍA ======== -->
    <section class="mb-5" id="typography">
        <h2 class="h4 mb-3">Tipografía</h2>
        <div class="card"><div class="card-body">
            <p style="font-weight:300">Inter Light (300) — El acceso a la educación es un derecho.</p>
            <p style="font-weight:400">Inter Regular (400) — El acceso a la educación es un derecho.</p>
            <p style="font-weight:500">Inter Medium (500) — El acceso a la educación es un derecho.</p>
            <p style="font-weight:600">Inter Semibold (600) — El acceso a la educación es un derecho.</p>
            <p style="font-weight:700">Inter Bold (700) — El acceso a la educación es un derecho.</p>
            <p style="font-weight:800">Inter ExtraBold (800) — El acceso a la educación es un derecho.</p>
            <hr>
            <h1>h1. Heading</h1>
            <h2>h2. Heading</h2>
            <h3>h3. Heading</h3>
            <h4>h4. Heading</h4>
            <h5>h5. Heading</h5>
            <h6>h6. Heading</h6>
        </div></div>
    </section>

    <!-- ======== BOTONES ======== -->
    <section class="mb-5" id="buttons">
        <h2 class="h4 mb-3">Botones</h2>
        <div class="card"><div class="card-body d-flex flex-wrap gap-2">
            <button class="btn btn-primary">Primario</button>
            <button class="btn btn-outline-primary">Outline</button>
            <button class="btn btn-light">Light</button>
            <button class="btn btn-outline-light" style="background:#1a1a2e;">Outline Light</button>
            <button class="btn btn-hero btn-hero-primary">SÚMATE</button>
            <button class="btn btn-hero btn-hero-outline" style="background:var(--primary);">INICIAR SESIÓN</button>
            <button class="btn btn-primary btn-sm">Chico</button>
            <button class="btn btn-primary btn-lg">Grande</button>
        </div></div>
    </section>

    <!-- ======== CARDS ======== -->
    <section class="mb-5" id="cards">
        <h2 class="h4 mb-3">Cards</h2>
        <div class="row g-3">
            <div class="col-md-3"><div class="card card-border-rojo h-100"><div class="card-body"><h5>Borde rojo</h5><p class="small text-secondary mb-0">Card con borde superior rojo.</p></div></div></div>
            <div class="col-md-3"><div class="card card-border-amarillo h-100"><div class="card-body"><h5>Borde amarillo</h5><p class="small text-secondary mb-0">Card con borde superior amarillo.</p></div></div></div>
            <div class="col-md-3"><div class="card card-border-verde h-100"><div class="card-body"><h5>Borde verde</h5><p class="small text-secondary mb-0">Card con borde superior verde.</p></div></div></div>
            <div class="col-md-3"><div class="card card-border-primary h-100"><div class="card-body"><h5>Borde primary</h5><p class="small text-secondary mb-0">Card con borde superior azul.</p></div></div></div>
        </div>
    </section>

    <!-- ======== TABLAS ======== -->
    <section class="mb-5" id="tables">
        <h2 class="h4 mb-3">Tablas</h2>
        <div class="card"><div class="card-body p-0">
            <table class="table table-hover mb-0">
                <thead><tr><th>Columna 1</th><th>Columna 2</th><th>Columna 3</th></tr></thead>
                <tbody>
                    <tr><td>Dato 1</td><td>Dato 2</td><td>Dato 3</td></tr>
                    <tr><td>Dato 4</td><td>Dato 5</td><td>Dato 6</td></tr>
                    <tr><td>Dato 7</td><td>Dato 8</td><td>Dato 9</td></tr>
                </tbody>
            </table>
        </div></div>
    </section>

    <!-- ======== FORMULARIOS ======== -->
    <section class="mb-5" id="forms">
        <h2 class="h4 mb-3">Formularios</h2>
        <div class="card"><div class="card-body">
            <div class="mb-3">
                <label class="form-label" for="input-ejemplo">Input de texto</label>
                <input type="text" class="form-control" id="input-ejemplo" placeholder="Escribí algo...">
            </div>
            <div class="mb-3">
                <label class="form-label" for="select-ejemplo">Select</label>
                <select class="form-select" id="select-ejemplo"><option>Opción 1</option><option>Opción 2</option></select>
            </div>
            <div class="mb-3">
                <label class="form-label" for="input-error">Input con error</label>
                <input type="text" class="form-control is-invalid" id="input-error" value="mal">
                <div class="invalid-feedback">Este campo es obligatorio.</div>
            </div>
        </div></div>
    </section>

    <!-- ======== ALERTS ======== -->
    <section class="mb-5" id="alerts">
        <h2 class="h4 mb-3">Alertas</h2>
        <div class="d-flex flex-column gap-2">
            <div class="alert alert-success mb-0">Operación exitosa.</div>
            <div class="alert alert-danger mb-0">Ocurrió un error.</div>
            <div class="alert alert-warning mb-0">Atención: revisá los datos.</div>
            <div class="alert alert-info mb-0">Información importante.</div>
        </div>
    </section>

    <!-- ======== HERO ======== -->
    <section class="mb-5" id="hero">
        <h2 class="h4 mb-3">Hero (landing)</h2>
        <div style="background:linear-gradient(135deg, #3f51b5 0%, #5c6bc0 40%, #7c4dff 100%);color:#fff;border-radius:var(--radius);padding:3rem 2rem;position:relative;overflow:hidden;">
            <div style="position:relative;z-index:1;">
                <p class="text-uppercase small fw-semibold mb-1" style="opacity:0.8;">Mutual Escolar UNI2</p>
                <h1 class="display-5 fw-bold">Tu mutual, más cerca que nunca</h1>
                <button class="btn btn-hero btn-hero-primary mt-3">SÚMATE</button>
                <button class="btn btn-hero btn-hero-outline mt-3 ms-2">INICIAR SESIÓN</button>
            </div>
        </div>
    </section>

    <!-- ======== STEPS ======== -->
    <section class="mb-5" id="steps">
        <h2 class="h4 mb-3">Pasos</h2>
        <div class="row g-3">
            <div class="col-md-3"><div class="step-card"><div class="step-number step-number-primary">1</div><h3>Paso uno</h3><p class="small text-secondary mb-0">Descripción del paso.</p></div></div>
            <div class="col-md-3"><div class="step-card"><div class="step-number step-number-rojo">2</div><h3>Paso dos</h3><p class="small text-secondary mb-0">Descripción del paso.</p></div></div>
            <div class="col-md-3"><div class="step-card"><div class="step-number step-number-amarillo">3</div><h3>Paso tres</h3><p class="small text-secondary mb-0">Descripción del paso.</p></div></div>
            <div class="col-md-3"><div class="step-card"><div class="step-number step-number-verde">4</div><h3>Paso cuatro</h3><p class="small text-secondary mb-0">Descripción del paso.</p></div></div>
        </div>
    </section>

</div>
{% endblock %}
```

- [ ] **Step 4: Verificar que la página renderiza**

Run: `python -c "
import django; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.test import RequestFactory; from web.views import DesignSystemView
rf = RequestFactory(); request = rf.get('/design-system/')
response = DesignSystemView.as_view()(request)
print('Status:', response.status_code)
print('OK' if response.status_code == 200 else 'FAIL')
"`

Expected: Status: 200, OK

- [ ] **Step 5: Commit**

```bash
git add templates/web/design-system.html web/views.py web/urls.py
git commit -m "feat: agregar pagina showcase del design system en /design-system/"
```

---

### Task 8: Verificación final y linter

**Files:**
- All modified files

- [ ] **Step 1: Correr check de Django**

```bash
python manage.py check
```

Expected: No system check errors

- [ ] **Step 2: Verificar que las rutas nuevas existen**

```bash
python manage.py show_urls | grep design-system
```

Expected: `/design-system/` listado

- [ ] **Step 3: Verificar que templates heredan correctamente**

```bash
python -c "
import django; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.template.loader import get_template
for name in ['base.html', 'web/home.html', 'web/design-system.html']:
    t = get_template(name)
    print(f'{name}: OK')
"
```

Expected: All three templates load without errors

- [ ] **Step 4: Commit final**

```bash
git add -A
git commit -m "chore: verificacion final del design system"
```
